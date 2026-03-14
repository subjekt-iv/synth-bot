from openai import OpenAI
from typing import List
from app.core.config import settings


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-3-small"


    def estimate_embedding_cost(self, texts: List[str]) -> float:
        """Rough cost estimation for embeddings based on token count."""
        token_count = sum(len(text.split()) for text in texts)  # Simple approximation
        cost = token_count / 1000 * 0.0001
        print(f"[INFO] Estimated embedding cost: ${cost:.6f}")
        return cost

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        print(f"[DEBUG] get_embeddings called. DISABLE_EMBEDDINGS = {settings.disable_embeddings}")
        if settings.disable_embeddings:
            print("[WARN] Embeddings are disabled. Returning empty vectors.")
            return [[0.0] * 1536 for _ in texts]  

        self.estimate_embedding_cost(texts)

        try:
            print("[DEBUG] Calling OpenAI API for embeddings...")
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            embeddings = [embedding.embedding for embedding in response.data]
            return embeddings
        except Exception as e:
            print(f"[ERROR] Error generating embeddings: {e}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        print(f"[DEBUG] get_embedding called. DISABLE_EMBEDDINGS = {settings.disable_embeddings}")
        embeddings = self.get_embeddings([text])
        return embeddings[0]


# Global embedding service instance
embedding_service = EmbeddingService()
