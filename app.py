from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

import pandas as pd
import streamlit as st

from src.config import get_settings
from src.data.ticket_repository import TicketRepository


st.set_page_config(
    page_title="NovaMart Support Copilot",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Existing navigation / configuration — intentionally kept unchanged.
# -----------------------------------------------------------------------------
settings = get_settings()

st.sidebar.header("Navigation")
st.sidebar.info(
    "Use the pages to work the support queue, inspect evidence, search the "
    "knowledge base, review feedback, and diagnose the RAG pipeline."
)


# -----------------------------------------------------------------------------
# Dashboard helpers
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_tickets() -> list[dict[str, Any]]:
    """Load the existing ticket dataset through the application's repository."""
    return TicketRepository().all_tickets()


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def period_rows(rows: list[dict[str, Any]], days: int) -> tuple[list[dict[str, Any]], date, date]:
    """Return the latest N-day activity window based on the dataset's max timestamp."""
    dates = [parse_date(str(row["created_at"])) for row in rows if row.get("created_at")]
    end_date = max(dates)
    start_date = end_date - timedelta(days=days - 1)
    filtered = [
        row
        for row in rows
        if row.get("created_at")
        and start_date <= parse_date(str(row["created_at"])) <= end_date
    ]
    return filtered, start_date, end_date


def previous_period_rows(
    rows: list[dict[str, Any]], start_date: date, days: int
) -> list[dict[str, Any]]:
    """Return the immediately preceding period of equal length."""
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - timedelta(days=days - 1)
    return [
        row
        for row in rows
        if row.get("created_at")
        and previous_start <= parse_date(str(row["created_at"])) <= previous_end
    ]


INTENT_LABELS: dict[str, str] = {
    "order_tracking": "Order tracking",
    "delivery_delay": "Delivery delay",
    "missing_delivery": "Missing delivery",
    "wrong_item": "Wrong item",
    "damaged_item": "Damaged item",
    "return_request": "Return request",
    "refund_request": "Refund request",
    "exchange_request": "Exchange request",
    "order_cancellation": "Order cancellation",
    "payment_failure": "Payment failure",
    "duplicate_charge": "Duplicate charge",
    "coupon_issue": "Coupon issue",
    "warranty": "Warranty",
    "product_question": "Product question",
    "account_issue": "Account issue",
    "shipping_question": "Shipping question",
    "other": "Other",
}


HIGH_LEVEL_CATEGORY_MAP: dict[str, str] = {
    "product_question": "Product & Quality",
    "damaged_item": "Product & Quality",
    "wrong_item": "Product & Quality",
    "warranty": "Product & Quality",
    "payment_failure": "Billing & Payments",
    "duplicate_charge": "Billing & Payments",
    "refund_request": "Billing & Payments",
    "coupon_issue": "Billing & Payments",
    "order_tracking": "Delivery & Logistics",
    "delivery_delay": "Delivery & Logistics",
    "missing_delivery": "Delivery & Logistics",
    "shipping_question": "Delivery & Logistics",
    "return_request": "Returns & Changes",
    "exchange_request": "Returns & Changes",
    "order_cancellation": "Returns & Changes",
    "account_issue": "Account & Access",
    "other": "Other",
}


ERROR_CLUSTERS: dict[str, tuple[str, ...]] = {
    "Payment processing issues": (
        "payment failed",
        "payment failure",
        "payment declined",
        "payment error",
        "could not pay",
        "couldn't pay",
        "charged twice",
        "duplicate charge",
        "charged twice",
    ),
    "Delivery exceptions": (
        "delivered but missing",
        "did not receive",
        "didn't receive",
        "not receive",
        "delivery delayed",
        "delivery delay",
        "arrived late",
        "late delivery",
    ),
    "Product condition issues": (
        "damaged",
        "broken",
        "defective",
        "cracked",
        "not working",
        "does not work",
        "doesn't work",
    ),
    "Account access issues": (
        "cannot login",
        "can't login",
        "cannot log in",
        "can't log in",
        "sign in",
        "login",
        "account access",
    ),
}


def high_level_distribution(rows: list[dict[str, Any]]) -> pd.DataFrame:
    counts = Counter(
        HIGH_LEVEL_CATEGORY_MAP.get(str(row.get("queue_intent", "other")), "Other")
        for row in rows
    )
    total = sum(counts.values())
    data = [
        {"Category": category, "Tickets": count, "Share": (count / total * 100) if total else 0.0}
        for category, count in counts.most_common()
    ]
    return pd.DataFrame(data)


def top_request_themes(rows: list[dict[str, Any]], limit: int = 5) -> pd.DataFrame:
    """Use recurring ticket subjects because the dataset has no dedicated feature-request field."""
    counts = Counter(str(row.get("subject", "Other")).strip() or "Other" for row in rows)
    total = sum(counts.values())
    data = [
        {
            "Request / theme": theme,
            "Tickets": count,
            "Share of tickets": (count / total * 100) if total else 0.0,
        }
        for theme, count in counts.most_common(limit)
    ]
    return pd.DataFrame(data)


def top_support_issues(rows: list[dict[str, Any]], limit: int = 5) -> pd.DataFrame:
    counts = Counter(str(row.get("queue_intent", "other")) for row in rows)
    data = [
        {
            "Issue": INTENT_LABELS.get(intent, intent.replace("_", " ").title()),
            "Tickets": count,
        }
        for intent, count in counts.most_common(limit)
    ]
    return pd.DataFrame(data)


def find_emerging_issue(
    recent_rows: list[dict[str, Any]], previous_rows: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Detect a recent error/exception cluster that has materially increased vs the prior period."""
    if len(recent_rows) < 5:
        return None

    recent_total = len(recent_rows)
    previous_total = len(previous_rows)
    candidates: list[dict[str, Any]] = []

    recent_texts = [
        f"{row.get('subject', '')} {row.get('message', '')}".lower()
        for row in recent_rows
    ]
    previous_texts = [
        f"{row.get('subject', '')} {row.get('message', '')}".lower()
        for row in previous_rows
    ]

    for cluster_name, keywords in ERROR_CLUSTERS.items():
        recent_count = sum(any(keyword in text for keyword in keywords) for text in recent_texts)
        previous_count = sum(any(keyword in text for keyword in keywords) for text in previous_texts)
        recent_share = recent_count / recent_total if recent_total else 0.0
        previous_share = previous_count / previous_total if previous_total else 0.0
        delta = recent_share - previous_share

        # Require a meaningful cluster and increase to avoid flagging ordinary volume.
        materially_increased = delta >= 0.05 or (
            previous_count > 0 and recent_count >= previous_count * 1.5
        )
        if recent_count >= 5 and recent_share >= 0.10 and materially_increased:
            candidates.append(
                {
                    "issue": cluster_name,
                    "count": recent_count,
                    "recent_share": recent_share,
                    "previous_share": previous_share,
                    "delta": delta,
                }
            )

    if not candidates:
        return None

    return max(candidates, key=lambda x: (x["delta"], x["count"]))


def format_period(start_date: date, end_date: date) -> str:
    return f"{start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')}"


# -----------------------------------------------------------------------------
# Landing page / Support Operations Dashboard
# -----------------------------------------------------------------------------
tickets = load_tickets()
recent_tickets, recent_start, recent_end = period_rows(tickets, days=30)
previous_tickets = previous_period_rows(tickets, recent_start, days=30)

received = len(recent_tickets)
resolved = sum(str(row.get("status", "")).lower() == "resolved" for row in recent_tickets)
backlog_change = received - resolved
resolution_rate = (resolved / received * 100) if received else 0.0

st.title("NovaMart Support Copilot")
st.caption("AI-assisted retail support workspace")
st.markdown("## Support Operations Overview")

st.markdown("### Today's Support Snapshot")

metric_cols = st.columns(4)
with metric_cols[0]:
    st.metric("Tickets Received", f"{received:,}")
with metric_cols[1]:
    st.metric("Resolved", f"{resolved:,}")
with metric_cols[2]:
    st.metric("Backlog Change", f"{backlog_change:+,}")
with metric_cols[3]:
    st.metric("Resolution Rate", f"{resolution_rate:.1f}%")

st.caption("Backlog Change = tickets received minus tickets marked resolved in the recent activity window.")

st.divider()

# Customer feedback / issue distribution
st.markdown("## Customer Feedback & Issue Distribution")
st.caption(
    "The current dataset does not contain a dedicated product-feedback taxonomy, so support intents are "
    "mapped into high-level operational categories."
)

category_df = high_level_distribution(tickets)
chart_col, table_col = st.columns([1.65, 1])
with chart_col:
    if not category_df.empty:
        st.bar_chart(
            category_df.set_index("Category")["Share"],
            height=320,
            y_label="Share of support conversations (%)",
        )
with table_col:
    if not category_df.empty:
        display_df = category_df.copy()
        display_df["Share"] = display_df["Share"].map(lambda x: f"{x:.1f}%")
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": st.column_config.TextColumn("Category"),
                "Tickets": st.column_config.NumberColumn("Tickets"),
                "Share": st.column_config.TextColumn("Share"),
            },
        )

st.divider()

# Top recurring requests
left, right = st.columns(2)
with left:
    st.markdown("## Top Recurring Customer Requests")
    st.caption(
        "No explicit feature-request records were found, so the dashboard shows the most frequent customer-request themes."
    )
    requests_df = top_request_themes(tickets, limit=5)
    if not requests_df.empty:
        for rank, (_, row) in enumerate(requests_df.iterrows(), start=1):
            st.markdown(
                f"**{rank}. {row['Request / theme']}**  \n"
                f"{int(row['Tickets']):,} tickets · {row['Share of tickets']:.1f}% of all tickets"
            )
            if rank < len(requests_df):
                st.markdown("---")

with right:
    st.markdown("## Top Issues")
    st.caption("Most common support intents in the full ticket dataset.")
    issues_df = top_support_issues(tickets, limit=5)
    if not issues_df.empty:
        st.dataframe(
            issues_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Issue": st.column_config.TextColumn("Issue"),
                "Tickets": st.column_config.NumberColumn("Tickets", format="%d"),
            },
        )

st.divider()

# Emerging issue detection
st.markdown("## ⚠ Potential Emerging Issue")
emerging = find_emerging_issue(recent_tickets, previous_tickets)
if emerging is None:
    st.success("No significant emerging issue detected in the recent activity window.")
else:
    st.warning(
        f"**{emerging['issue']}**\n\n"
        f"{emerging['count']:,} tickets mention a similar error or exception pattern.\n\n"
        f"This represents **{emerging['recent_share'] * 100:.1f}%** of recent support tickets, "
        f"up from **{emerging['previous_share'] * 100:.1f}%** in the preceding 30-day period. "
        f"The share increased by **{emerging['delta'] * 100:.1f} percentage points**."
    )

