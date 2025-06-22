from openai import OpenAI
from typing import List
from app.core.config import settings


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "text-embedding-ada-002"
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            embeddings = [embedding.embedding for embedding in response.data]
            return embeddings
            
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = self.get_embeddings([text])
        return embeddings[0]


# Global embedding service instance
embedding_service = EmbeddingService() 