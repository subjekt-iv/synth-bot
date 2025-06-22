import pytest
from unittest.mock import MagicMock, patch

# Import fixtures from conftest.py
pytest_plugins = ["tests.conftest"]


@patch('app.api.chat.rag_chain')
@patch('app.api.chat.get_db')
def test_chat_endpoint_success(mock_get_db, mock_rag_chain, client):
    """Test successful chat query processing."""
    # Mock RAG chain response
    mock_rag_chain.process_query.return_value = {
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
    
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    # Mock chunk query
    mock_chunk = MagicMock()
    mock_chunk.id = "test-chunk-1"
    mock_chunk.content = "Test chunk content about synthesizer features."
    mock_chunk.page_number = 1
    mock_session.query.return_value.filter.return_value.first.return_value = mock_chunk
    
    response = client.post("/chat/", json={
        "query": "What are the main features of this synthesizer?",
        "document_id": None
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "citations" in data
    assert "response_time" in data
    assert data["response"] == "This is a test response about synthesizer features."


def test_chat_endpoint_missing_query(client):
    """Test chat endpoint with missing query."""
    response = client.post("/chat/", json={})
    assert response.status_code == 422  # Validation error


@patch('app.api.chat.rag_chain')
@patch('app.api.chat.get_db')
def test_chat_endpoint_empty_query(mock_get_db, mock_rag_chain, client):
    """Test chat endpoint with empty query."""
    # Mock RAG chain to handle empty query gracefully
    mock_rag_chain.process_query.return_value = {
        "response": "Please provide a valid query.",
        "relevant_chunks": []
    }
    
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    response = client.post("/chat/", json={"query": ""})
    # Should return 200 since the RAG chain handles empty queries
    assert response.status_code == 200


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data


@patch('app.api.chat.get_db')
def test_chat_history_endpoint(mock_get_db, client):
    """Test chat history endpoint."""
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    # Mock chat object
    mock_chat = MagicMock()
    mock_chat.id = "test-chat-1"
    mock_chat.user_query = "Test query"
    mock_chat.ai_response = "Test response"
    mock_chat.created_at = "2024-01-01T12:00:00Z"
    mock_chat.response_time = 1.23
    mock_chat.document_id = "test-doc-1"
    
    # Mock query chain
    mock_query = MagicMock()
    mock_query.count.return_value = 1
    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [mock_chat]
    
    mock_session.query.return_value = mock_query
    
    response = client.get("/chat/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "chats" in data
    assert "total" in data 