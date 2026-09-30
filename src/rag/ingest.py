import json
from pathlib import Path
from src.config import project_path, get_settings
from src.embeddings.embedding_service import EmbeddingService
from src.rag.chunker import chunk_markdown
import chromadb

EVAL_PATH = project_path("data/evaluation_tickets.json")

def parse_frontmatter(text: str):
    if not text.startswith("---"): return {}, text
    _, front, body = text.split("---", 2)
    meta={}
    for line in front.strip().splitlines():
        if ":" in line:
            k,v=line.split(":",1); meta[k.strip()]=v.strip()
    body = body.strip()
    if "title" not in meta:
        for line in body.splitlines():
            if line.startswith("# "):
                meta["title"] = line[2:].strip()
                break
    return meta, body

def ingest_knowledge():
    settings=get_settings(); client=chromadb.PersistentClient(path=str(settings.chroma_dir)); ef=EmbeddingService(settings.embedding_model)
    col=client.get_or_create_collection("knowledge_base", embedding_function=ef)
    ids=[]; docs=[]; metas=[]
    for path in sorted(project_path("data/knowledge_base").glob("*.md")):
        meta, body=parse_frontmatter(path.read_text(encoding="utf-8"))
        for c in chunk_markdown(body, meta): ids.append(c.chunk_id); docs.append(c.text); metas.append(c.metadata)
    if ids: col.upsert(ids=ids, documents=docs, metadatas=metas)
    return len(ids)

def ingest_tickets():
    settings=get_settings(); client=chromadb.PersistentClient(path=str(settings.chroma_dir)); ef=EmbeddingService(settings.embedding_model)
    col=client.get_or_create_collection("support_tickets", embedding_function=ef)
    eval_ids={x["ticket_id"] for x in json.loads(EVAL_PATH.read_text())} if EVAL_PATH.exists() else set()
    tickets=json.loads(project_path("data/tickets.json").read_text())
    ids=[]; docs=[]; metas=[]
    for t in tickets:
        if t["ticket_id"] in eval_ids: continue
        text=f"Subject: {t['subject']}\nMessage: {t['message']}\nHistorical summary: {t.get('historical_summary','')}\nHistorical resolution: {t.get('historical_resolution','')}"
        ids.append(t["ticket_id"]); docs.append(text); metas.append({"ticket_id":t["ticket_id"],"customer_id":t["customer_id"],"category":t["category"],"created_at":t["created_at"],"summary":t.get("historical_summary",""),"resolution":t.get("historical_resolution","")})
    if ids: col.upsert(ids=ids, documents=docs, metadatas=metas)
    return len(ids)

if __name__ == "__main__":
    print("Knowledge chunks:", ingest_knowledge())
    print("Training tickets indexed:", ingest_tickets())
