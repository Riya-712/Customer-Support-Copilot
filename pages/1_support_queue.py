import json
import streamlit as st
from src.config import project_path

st.set_page_config(page_title="Support Queue", layout="wide")
st.title("Support Queue")
st.caption("Filter and open NovaMart support tickets for agent-assisted resolution.")
tickets=json.loads(project_path('data/tickets.json').read_text())
statuses=sorted({x.get('status','open') for x in tickets}); priorities=sorted({x.get('priority','medium') for x in tickets}); intents=sorted({x.get('queue_intent','other') for x in tickets}); tiers=['All']+sorted({x for x in ["Bronze","Silver","Gold","Platinum"]})
customers={x['customer_id']:x for x in json.loads(project_path('data/customers.json').read_text())}
products={x['product_id']:x for x in json.loads(project_path('data/products.json').read_text())}
orders={x['order_id']:x for x in json.loads(project_path('data/orders.json').read_text())}
for t in tickets:
    c=customers.get(t['customer_id'],{}); o=orders.get(t.get('order_id'),{}); item=(o.get('items') or [{}])[0]
    t['_tier']=c.get('loyalty_tier','Unknown'); t['_category']=products.get(item.get('product_id'),{}).get('category',t.get('product_category','All'))
with st.sidebar:
    status=st.multiselect('Status',statuses,default=statuses)
    priority=st.multiselect('Priority',priorities,default=priorities)
    intent=st.multiselect('Intent',intents,default=intents)
    tier=st.selectbox('Customer tier',tiers)
    cats=['All']+sorted({t['_category'] for t in tickets})
    cat=st.selectbox('Product category',cats)
    search=st.text_input('Search ticket')
filtered=[t for t in tickets if t.get('status') in status and t.get('priority') in priority and t.get('queue_intent','other') in intent and (tier=='All' or t['_tier']==tier) and (cat=='All' or t['_category']==cat) and (not search or search.lower() in (t['subject']+' '+t['message']+' '+t['ticket_id']).lower())]
st.metric('Tickets',len(filtered))
for t in filtered[:100]:
    with st.container(border=True):
        c1,c2,c3,c4=st.columns([1.3,1.4,1.2,1.2])
        c1.markdown(f"**{t['ticket_id']}**<br>{t['subject']}", unsafe_allow_html=True)
        c2.write(f"{t['_tier']} · {t['_category']}")
        c3.write(f"Status: **{t['status']}**")
        c4.write(f"Priority: **{t['priority']}**")
        st.caption(t['message'][:240] + ('…' if len(t['message'])>240 else ''))
        if st.button('Open ticket',key=f"open-{t['ticket_id']}"):
            st.session_state['selected_ticket_id']=t['ticket_id']; st.switch_page('pages/2_ticket_workspace.py')
