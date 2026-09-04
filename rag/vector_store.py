import math
from typing import List, Dict, Any, Tuple
from rag.embeddings import embedding_engine, LocalEmbeddingEngine

class LocalVectorStore:
    """
    Sovereign local vector store implementing cosine similarity search over chunk vectors.
    Supports 100% offline document indexing and retrieval.
    """

    def __init__(self, embedder: LocalEmbeddingEngine = embedding_engine):
        self.embedder = embedder
        self.documents: List[Dict[str, Any]] = []
        self.vectors: List[List[float]] = []

    def clear(self):
        """Clears all stored vector documents."""
        self.documents = []
        self.vectors = []

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Indexes document chunks into local vector store."""
        for chunk in chunks:
            vec = self.embedder.embed_text(chunk["text"])
            self.documents.append(chunk)
            self.vectors.append(vec)

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a > 0 and norm_b > 0:
            return dot / (norm_a * norm_b)
        return 0.0

    def search(self, query: str, top_k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """Searches top-K relevant chunks using query vector similarity."""
        if not self.documents:
            return []

        query_vec = self.embedder.embed_text(query)
        scored_results = []
        for doc, vec in zip(self.documents, self.vectors):
            score = self._cosine_similarity(query_vec, vec)
            scored_results.append((doc, score))

        # Sort descending by similarity score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]

vector_store = LocalVectorStore()
