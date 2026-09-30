from pathlib import Path
from src.config import get_settings
from src.embeddings.embedding_service import EmbeddingService

class ChromaRetriever:
    def __init__(self):
        settings = get_settings()
        import chromadb
        self.client = chromadb.PersistentClient(path=str(settings.chroma_dir))
        self.embedding = EmbeddingService(settings.embedding_model)
        self.kb = self.client.get_or_create_collection("knowledge_base", embedding_function=self.embedding)
        self.tickets = self.client.get_or_create_collection("support_tickets", embedding_function=self.embedding)
        self.top_k = settings.top_k

    def search_knowledge_base(self, query: str, top_k: int | None = None) -> list[dict]:
        return self._query(self.kb, query, top_k or self.top_k)

    def search_similar_tickets(self, query: str, top_k: int | None = None) -> list[dict]:
        return self._query(self.tickets, query, top_k or self.top_k)

    @staticmethod
    def _query(collection, query: str, n: int):
        if collection.count() == 0:
            return []
        result = collection.query(query_texts=[query], n_results=min(n, collection.count()), include=["documents","metadatas","distances"])
        rows=[]
        for i, item_id in enumerate(result["ids"][0]):
            meta=result["metadatas"][0][i]
            rows.append({"id": item_id, "document": result["documents"][0][i], "metadata": meta, "distance": result["distances"][0][i], "ticket_id": meta.get("ticket_id"), "summary": meta.get("summary"), "resolution": meta.get("resolution")})
        return rows

    def knowledge_documents(self):
        if self.kb.count() == 0: return []
        return self.kb.get(include=["documents","metadatas"])
