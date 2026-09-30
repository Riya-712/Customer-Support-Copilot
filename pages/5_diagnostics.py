import streamlit as st, json
from src.config import get_settings
from src.rag.retriever import ChromaRetriever
from src.feedback import load_feedback
st.set_page_config(page_title='Diagnostics',layout='wide')
st.title('Diagnostics')
s=get_settings(); r=ChromaRetriever()
c1,c2,c3=st.columns(3); c1.metric('LLM model',s.groq_model); c2.metric('Embedding model',s.embedding_model); c3.metric('Configured TOP_K',s.top_k)
c1,c2=st.columns(2); c1.metric('KB chunks',r.kb.count()); c2.metric('Indexed support tickets',r.tickets.count())
st.subheader('Live retrieval diagnostics')
q=st.text_input('Test retrieval query','I was charged twice for my order')
if q:
    kb=r.search_knowledge_base(q); sim=r.search_similar_tickets(q)
    st.write(f'Retrieved documents: {len(kb)+len(sim)}')
    for title,rows in [('Knowledge base',kb),('Similar tickets',sim)]:
        st.markdown(f'**{title}**')
        for x in rows:
            st.write(f"`{x['id']}` · distance `{x['distance']:.4f}`")
            with st.expander('Evidence'): st.write(x['document'])
st.subheader('Feedback file')
st.write(f'{len(load_feedback())} feedback records')
