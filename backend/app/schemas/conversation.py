from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.schemas.chat import ChatHistoryItem


class ConversationCreate(BaseModel):
    """Request model for creating a conversation."""
    title: Optional[str] = None


class ConversationSummary(BaseModel):
    """Summary model for conversation list items."""
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int


class ConversationListResponse(BaseModel):
    """Response model for listing conversations."""
    conversations: List[ConversationSummary]
    total: int


class ConversationDetail(BaseModel):
    """Detailed model for a single conversation with its chats."""
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    chats: List[ChatHistoryItem]
