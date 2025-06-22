import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test_key_for_testing"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["QDRANT_API_URL"] = "http://localhost:6333"
os.environ["DEBUG"] = "True"

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture
def mock_rag_chain():
    """Mock the RAG chain for testing."""
    with patch('app.api.chat.rag_chain') as mock:
        mock.process_query.return_value = {
            "response": "This is a test response about synthesizer features.",
            "relevant_chunks": [
                {
                    "id": "test-chunk-1",
                    "score": 0.95,
                    "payload": {
                        "content": "Test chunk content about synthesizer features.",
                        "page_number": 1
                    }
                }
            ]
        }
        yield mock

@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    with patch('app.api.chat.get_db') as mock:
        mock_session = MagicMock()
        mock.return_value = mock_session
        yield mock_session

@pytest.fixture
def mock_embedding_service():
    """Mock embedding service for testing."""
    with patch('app.services.embeddings.embedding_service') as mock:
        mock.get_embedding.return_value = [0.1, 0.2, 0.3]  # Mock embedding
        yield mock

@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    with patch('app.services.vector_store.vector_store') as mock:
        mock.search_similar.return_value = [
            {
                "id": "test-chunk-1",
                "score": 0.95,
                "payload": {
                    "content": "Test chunk content about synthesizer features.",
                    "page_number": 1
                }
            }
        ]
        yield mock 