from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.rag.chunker import chunk_markdown
from src.rag.retriever import ChromaRetriever

def test_chunker_creates_overlap_chunks():
    text='A'*2500
    chunks=chunk_markdown(text,{'document_id':'KB-X'})
    assert len(chunks)>1
    assert chunks[0].chunk_id=='KB-X-0'

def test_retriever_query_mapping():
    class FakeCollection:
        def count(self): return 1
        def query(self,**kwargs): return {'ids':[['X']], 'documents':[['doc']], 'metadatas':[[{'title':'T'}]], 'distances':[[.12]]}
    rows=ChromaRetriever._query(FakeCollection(),'q',5)
    assert rows[0]['id']=='X' and rows[0]['distance']==.12
