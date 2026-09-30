import streamlit as st
from src.rag.retriever import ChromaRetriever
st.set_page_config(page_title='Knowledge Base',layout='wide')
st.title('Knowledge Base')
st.caption('Browse and search the indexed authoritative NovaMart policy corpus.')
r=ChromaRetriever()
query=st.text_input('Search knowledge base')
if query:
    rows=r.search_knowledge_base(query)
else:
    data=r.knowledge_documents(); rows=[]
    for i,doc in enumerate(data.get('ids',[])):
        rows.append({'id':doc,'document':data['documents'][i],'metadata':data['metadatas'][i],'distance':None})
for x in rows:
    m=x['metadata']
    with st.expander(f"{m.get('document_id',x['id'])} · {m.get('title','Knowledge document')}"):
        st.write(x['document']); st.caption(f"Source: {m.get('source','NovaMart Internal Support Policy')} · Category: {m.get('category')} · Product category: {m.get('product_category')} · Version: {m.get('version')} · Effective date: {m.get('effective_date')}")
