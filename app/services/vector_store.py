from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
import uuid
from app.core.config import settings


class VectorStore:
    """Service for managing vector storage with Qdrant."""
    
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_api_url,
            api_key=settings.qdrant_api_key
        )
        self.collection_name = "synthesizer_manuals"
        self.vector_size = 1536  # OpenAI text-embedding-ada-002 dimension
        
    def initialize_collection(self):
        """Initialize the vector collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {self.collection_name}")
            else:
                print(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            print(f"Error initializing collection: {e}")
            raise
    
    def add_embeddings(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]) -> List[str]:
        """Add embeddings to the vector store."""
        points = []
        embedding_ids = []
        
        for i, (embedding, meta) in enumerate(zip(embeddings, metadata)):
            embedding_id = str(uuid.uuid4())
            embedding_ids.append(embedding_id)
            
            point = PointStruct(
                id=embedding_id,
                vector=embedding,
                payload=meta
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return embedding_ids
    
    def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar embeddings."""
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )
        
        results = []
        for result in search_result:
            results.append({
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            })
        
        return results
    
    def delete_embeddings(self, embedding_ids: List[str]):
        """Delete embeddings by their IDs."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=embedding_ids  # type: ignore
        )
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": info.name,  # type: ignore
            "vectors_count": info.vectors_count,
            "points_count": info.points_count
        }


# Global vector store instance
vector_store = VectorStore() 