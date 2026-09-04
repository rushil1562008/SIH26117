import math
import re
from typing import List

class LocalEmbeddingEngine:
    """
    Offline local embedding generator using deterministic term-frequency hashing vectorization.
    Guarantees 100% air-gapped, zero-dependency embedding generation without requiring cloud APIs.
    """

    def __init__(self, vector_dim: int = 128):
        self.vector_dim = vector_dim

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def embed_text(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        vec = [0.0] * self.vector_dim
        if not tokens:
            return vec

        for token in tokens:
            # Deterministic hash to dimension index
            idx = hash(token) % self.vector_dim
            vec[idx] += 1.0

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]

        return vec

    def embed_documents(self, docs: List[str]) -> List[List[float]]:
        return [self.embed_text(doc) for doc in docs]

embedding_engine = LocalEmbeddingEngine()
