from typing import List

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Sentence-Transformers embedding adapter for ChromaDB."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def name(self) -> str:
        """Return a stable name required by ChromaDB."""
        return "novamart_bge_small_en_v1"

    def embed_documents(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        embeddings = self.model.encode(
            input,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def embed_query(self, input: str) -> List[float]:
        """Generate an embedding for a single query."""
        embedding = self.model.encode(
            input,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embedding.tolist()

    def __call__(self, input: List[str]) -> List[List[float]]:
        """Compatibility adapter for ChromaDB."""
        return self.embed_documents(input)