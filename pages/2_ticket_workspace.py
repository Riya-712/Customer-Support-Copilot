import json, time
import streamlit as st
from src.config import project_path
from src.support.ticket_analyzer import TicketAnalyzer
from src.feedback import Feedback, save_feedback

st.set_page_config(page_title="Ticket Workspace", layout="wide")
st.title("Ticket Workspace")
tickets=json.loads(project_path('data/tickets.json').read_text()); customers=json.loads(project_path('data/customers.json').read_text()); orders=json.loads(project_path('data/orders.json').read_text())
byid={t['ticket_id']:t for t in tickets}; customer_by={c['customer_id']:c for c in customers}; order_by={o['order_id']:o for o in orders}
selected=st.session_state.get('selected_ticket_id')
if not selected: st.warning('Select a ticket from Support Queue.'); st.stop()
ticket=byid.get(selected)
if not ticket: st.error('Ticket not found.'); st.stop()

if 'analysis_cache' not in st.session_state: st.session_state.analysis_cache={}

c1,c2=st.columns([1.2,2])
with c1:
    c=customer_by.get(ticket['customer_id']); o=order_by.get(ticket.get('order_id'))
    st.subheader('Customer')
    if c:
        st.markdown(f"**{c['name']}**")
        st.write(f"Tier: {c['loyalty_tier']}")
        st.write(f"Customer since: {c['signup_date']}")
        st.write(f"Order count: {len([x for x in orders if x['customer_id']==c['customer_id']])}")
        st.write(f"Customer ID: `{c['customer_id']}`")
    if o:
        st.markdown('**Relevant order**')
        st.write(f"`{o['order_id']}` · {o['status']} · ₹{o['total_amount']:.2f}")
        st.caption(f"Promised delivery: {o['promised_delivery_date']}")
with c2:
    st.subheader('Conversation')
    for msg in ticket.get('conversation',[{'speaker':'customer','message':ticket['message']}]):
        st.chat_message('user' if msg['speaker']=='customer' else 'assistant').write(msg['message'])

run=st.button('Run AI Copilot',type='primary')
if run or selected in st.session_state.analysis_cache:
    if run:
        with st.spinner('Retrieving context, classifying intent, and generating grounded assistance…'):
            try: st.session_state.analysis_cache[selected]=TicketAnalyzer().analyze(ticket)
            except Exception as e: st.error(f'Copilot error: {e}'); st.stop()
    r=st.session_state.analysis_cache[selected]
    if r.errors: st.warning('Some AI steps failed; the response may require manual review.')
    a,b,c,d=st.columns(4)
    a.metric('Intent',r.intent.intent if r.intent else 'other')
    b.metric('Confidence',f"{(r.intent.confidence if r.intent else 0):.0%}")
    c.metric('Retrieved KB',len(r.knowledge))
    d.metric('Latency',f"{r.latency_ms:.0f} ms")
    st.subheader('AI Copilot')
    st.markdown('### Summary'); st.write(r.ticket_analysis.summary if r.ticket_analysis else r.response.summary)
    st.markdown('### Customer issue'); st.write(r.ticket_analysis.customer_issue if r.ticket_analysis else '—')
    st.markdown('### Requested outcome'); st.write(r.ticket_analysis.requested_outcome if r.ticket_analysis else '—')
    st.markdown('### Important details'); st.write(r.ticket_analysis.important_details if r.ticket_analysis else [])
    st.markdown('### Recommended action')
    st.info(f"**{r.recommendation.action}** — {r.recommendation.reason}")
    if r.recommendation.required_verification: st.write('Required verification:',r.recommendation.required_verification)
    st.markdown('### Similar tickets')
    for x in r.similar_tickets:
        with st.expander(f"{x['id']} · similarity distance {x['distance']:.3f}"):
            st.write(f"**Summary:** {x.get('summary') or x['document'][:240]}")
            st.write(f"**Resolution:** {x.get('resolution') or 'Historical resolution not available.'}")
            st.caption('Historical example only — not authoritative policy.')
    st.markdown('### Retrieved knowledge')
    for x in r.knowledge:
        meta=x['metadata']; title=meta.get('title',meta.get('document_id',x['id']))
        with st.expander(f"Authoritative policy · {title}"):
            st.write(x['document']); st.caption(f"Source: {meta.get('document_id',x['id'])} · Category: {meta.get('category')} · Version: {meta.get('version')} · Effective: {meta.get('effective_date')}")
    st.markdown('### Suggested response')
    response_text=r.response.suggested_response
    st.text_area('Customer-facing draft',response_text,height=180,key=f'response-{selected}')
    ac1,ac2,ac3=st.columns(3)
    with ac1:
        if st.button('Accept',key=f'accept-{selected}'): st.session_state[f'accepted-{selected}']=True; st.success('Draft accepted for agent use.')
    with ac2:
        if st.button('Regenerate',key=f'regen-{selected}'): st.session_state.analysis_cache.pop(selected,None); st.rerun()
    with ac3: st.caption('Edit directly in the draft box before sending through your operational workflow.')
    st.markdown('### Citations')
    for cit in r.response.citations:
        with st.expander(cit.title): st.write(f"**Source:** `{cit.source_id}`"); st.write(cit.excerpt)
    st.markdown('### Agent feedback')
    f1,f2=st.columns(2)
    with f1:
        if st.button('👍 Helpful',key=f'help-{selected}'):
            save_feedback(Feedback(ticket_id=selected,helpful=True,response_accepted=st.session_state.get(f'accepted-{selected}'))); st.success('Feedback saved.')
    with f2:
        if st.button('👎 Not helpful',key=f'bad-{selected}'):
            st.session_state[f'negative-{selected}']=True
    if st.session_state.get(f'negative-{selected}'):
        reason=st.selectbox('Why?', ['incorrect_information','missing_context','bad_response','wrong_recommendation','poor_retrieval','other'],key=f'reason-{selected}')
        comment=st.text_input('Optional comment',key=f'comment-{selected}')
        if st.button('Submit negative feedback',key=f'submit-{selected}'):
            save_feedback(Feedback(ticket_id=selected,helpful=False,reason=reason,comment=comment)); st.success('Feedback saved.')
