import pytest
from unittest.mock import MagicMock, patch, Mock
from qdrant_client.models import PointStruct, ScoredPoint
from app.services.vector_store import VectorStore


class TestVectorStore:
    """Test cases for VectorStore class."""
    
    @pytest.fixture
    def mock_qdrant_client(self):
        """Mock QdrantClient for testing."""
        with patch('app.services.vector_store.QdrantClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def vector_store(self, mock_qdrant_client):
        """Create VectorStore instance with mocked client."""
        return VectorStore()
    
    def test_initialize_collection_new(self, vector_store, mock_qdrant_client):
        """Test initializing a new collection."""
        # Mock collections response - collection doesn't exist
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_qdrant_client.get_collections.return_value = mock_collections
        
        vector_store.initialize_collection()
        
        # Assert create_collection was called with correct parameters
        mock_qdrant_client.create_collection.assert_called_once()
        call_args = mock_qdrant_client.create_collection.call_args
        assert call_args[1]['collection_name'] == "synthesizer_manuals"
        assert call_args[1]['vectors_config'].size == 1536
    
    def test_initialize_collection_exists(self, vector_store, mock_qdrant_client):
        """Test initializing when collection already exists."""
        # Mock collections response - collection exists
        mock_collection = MagicMock()
        mock_collection.name = "synthesizer_manuals"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_qdrant_client.get_collections.return_value = mock_collections
        
        vector_store.initialize_collection()
        
        # Assert create_collection was NOT called
        mock_qdrant_client.create_collection.assert_not_called()
    
    def test_add_embeddings(self, vector_store, mock_qdrant_client):
        """Test adding embeddings to vector store."""
        # Test data
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        metadata = [
            {"filename": "test1.pdf", "page_number": 1, "content": "Test content 1"},
            {"filename": "test2.pdf", "page_number": 2, "content": "Test content 2"}
        ]
        
        embedding_ids = vector_store.add_embeddings(embeddings, metadata)
        
        # Assert upsert was called once
        mock_qdrant_client.upsert.assert_called_once()
        call_args = mock_qdrant_client.upsert.call_args
        
        # Check collection name
        assert call_args[1]['collection_name'] == "synthesizer_manuals"
        
        # Check points structure
        points = call_args[1]['points']
        assert len(points) == 2
        assert all(isinstance(point, PointStruct) for point in points)
        
        # Check first point details
        first_point = points[0]
        assert first_point.vector == [0.1, 0.2, 0.3]
        assert first_point.payload == {"filename": "test1.pdf", "page_number": 1, "content": "Test content 1"}
        
        # Check second point details
        second_point = points[1]
        assert second_point.vector == [0.4, 0.5, 0.6]
        assert second_point.payload == {"filename": "test2.pdf", "page_number": 2, "content": "Test content 2"}
        
        # Check returned IDs
        assert len(embedding_ids) == 2
        assert all(isinstance(id, str) for id in embedding_ids)
    
    def test_search_similar(self, vector_store, mock_qdrant_client):
        """Test searching for similar embeddings."""
        # Mock search results
        mock_scored_point1 = MagicMock()
        mock_scored_point1.id = "test-id-1"
        mock_scored_point1.score = 0.95
        mock_scored_point1.payload = {
            "filename": "test1.pdf",
            "page_number": 1,
            "content": "Test content 1"
        }
        
        mock_scored_point2 = MagicMock()
        mock_scored_point2.id = "test-id-2"
        mock_scored_point2.score = 0.87
        mock_scored_point2.payload = {
            "filename": "test2.pdf",
            "page_number": 2,
            "content": "Test content 2"
        }
        
        mock_qdrant_client.search.return_value = [mock_scored_point1, mock_scored_point2]
        
        # Test search
        query_embedding = [0.1, 0.2, 0.3]
        results = vector_store.search_similar(query_embedding, limit=5)
        
        # Assert search was called correctly
        mock_qdrant_client.search.assert_called_once_with(
            collection_name="synthesizer_manuals",
            query_vector=[0.1, 0.2, 0.3],
            limit=5,
            with_payload=True
        )
        
        # Check results structure
        assert len(results) == 2
        
        # Check first result
        first_result = results[0]
        assert first_result["id"] == "test-id-1"
        assert first_result["score"] == 0.95
        assert first_result["payload"] == {
            "filename": "test1.pdf",
            "page_number": 1,
            "content": "Test content 1"
        }
        
        # Check second result
        second_result = results[1]
        assert second_result["id"] == "test-id-2"
        assert second_result["score"] == 0.87
        assert second_result["payload"] == {
            "filename": "test2.pdf",
            "page_number": 2,
            "content": "Test content 2"
        }
    
    def test_search_similar_default_limit(self, vector_store, mock_qdrant_client):
        """Test search with default limit."""
        mock_qdrant_client.search.return_value = []
        
        query_embedding = [0.1, 0.2, 0.3]
        vector_store.search_similar(query_embedding)
        
        # Assert default limit of 5 was used
        mock_qdrant_client.search.assert_called_once_with(
            collection_name="synthesizer_manuals",
            query_vector=[0.1, 0.2, 0.3],
            limit=5,
            with_payload=True
        )
    
    def test_delete_embeddings(self, vector_store, mock_qdrant_client):
        """Test deleting embeddings by IDs."""
        embedding_ids = ["id-1", "id-2", "id-3"]
        
        vector_store.delete_embeddings(embedding_ids)
        
        # Assert delete was called correctly
        mock_qdrant_client.delete.assert_called_once_with(
            collection_name="synthesizer_manuals",
            points_selector=["id-1", "id-2", "id-3"]
        )
    
    def test_get_collection_info(self, vector_store, mock_qdrant_client):
        """Test getting collection information."""
        # Mock collection info
        mock_collection_info = MagicMock()
        mock_collection_info.name = "synthesizer_manuals"
        mock_collection_info.vectors_count = 100
        mock_collection_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_collection_info
        
        info = vector_store.get_collection_info()
        
        # Assert get_collection was called
        mock_qdrant_client.get_collection.assert_called_once_with("synthesizer_manuals")
        
        # Check returned info
        assert info["name"] == "synthesizer_manuals"
        assert info["vectors_count"] == 100
        assert info["points_count"] == 100
    
    def test_initialize_collection_exception(self, vector_store, mock_qdrant_client):
        """Test handling exceptions during collection initialization."""
        mock_qdrant_client.get_collections.side_effect = Exception("Connection error")
        
        with pytest.raises(Exception, match="Connection error"):
            vector_store.initialize_collection()
    
    def test_add_embeddings_empty_lists(self, vector_store, mock_qdrant_client):
        """Test adding empty embeddings lists."""
        embedding_ids = vector_store.add_embeddings([], [])
        
        # Should return empty list
        assert embedding_ids == []
        
        # Should call upsert with empty points list
        mock_qdrant_client.upsert.assert_called_once_with(
            collection_name="synthesizer_manuals",
            points=[]
        )
    
    def test_search_similar_empty_results(self, vector_store, mock_qdrant_client):
        """Test search with empty results."""
        mock_qdrant_client.search.return_value = []
        
        results = vector_store.search_similar([0.1, 0.2, 0.3])
        
        assert results == [] 