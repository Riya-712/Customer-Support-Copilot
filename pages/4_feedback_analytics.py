import streamlit as st
from src.feedback import load_feedback
st.set_page_config(page_title='Feedback Analytics',layout='wide')
st.title('Feedback Analytics')
rows=load_feedback(); st.metric('Feedback records',len(rows))
if rows:
    helpful=sum(1 for x in rows if x.get('helpful')); st.metric('Helpful rate',f'{helpful/len(rows):.1%}')
    reasons={}
    for x in rows:
        if x.get('reason'): reasons[x['reason']]=reasons.get(x['reason'],0)+1
    if reasons: st.bar_chart(reasons)
    st.dataframe(rows,use_container_width=True)
else: st.info('No agent feedback recorded yet.')
