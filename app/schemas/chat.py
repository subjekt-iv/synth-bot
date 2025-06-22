from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str
    document_id: Optional[str] = None


class Citation(BaseModel):
    """Model for a citation from a document chunk."""
    chunk_id: str
    content: str
    page_number: int
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    citations: List[Citation]
    response_time: float


class ChatHistoryItem(BaseModel):
    """Model for chat history items."""
    id: str
    user_query: str
    ai_response: str
    created_at: datetime
    response_time: Optional[float] = None
    document_id: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    chats: List[ChatHistoryItem]
    total: int 