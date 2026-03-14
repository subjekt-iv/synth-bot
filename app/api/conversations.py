from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

from app.db.database import get_db
from app.db.models import Conversation, Chat, ChatCitation
from app.schemas.chat import Citation
from app.schemas.conversation import (
    ConversationCreate, ConversationSummary, ConversationListResponse, ConversationDetail
)
from app.schemas.chat import ChatHistoryItem

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationSummary)
async def create_conversation(request: ConversationCreate, db: Session = Depends(get_db)):
    """Create a new conversation."""
    try:
        conversation = Conversation(title=request.title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return ConversationSummary(
            id=str(conversation.id),
            title=conversation.title,
            created_at=conversation.created_at,  # type: ignore
            updated_at=conversation.updated_at,  # type: ignore
            message_count=0
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")


@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List conversations ordered by most recently updated."""
    try:
        total = db.query(Conversation).count()

        results = (
            db.query(Conversation, func.count(Chat.id).label("message_count"))
            .outerjoin(Chat, Conversation.id == Chat.conversation_id)
            .group_by(Conversation.id)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        conversations = []
        for conv, message_count in results:
            conversations.append(ConversationSummary(
                id=str(conv.id),
                title=conv.title,
                created_at=conv.created_at,  # type: ignore
                updated_at=conv.updated_at,  # type: ignore
                message_count=message_count
            ))

        return ConversationListResponse(
            conversations=conversations,
            total=total
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing conversations: {str(e)}")


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get a conversation with all its chats and citations."""
    try:
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        chats = (
            db.query(Chat)
            .filter(Chat.conversation_id == conversation_id)
            .options(joinedload(Chat.citations).joinedload(ChatCitation.chunk))
            .order_by(Chat.created_at.asc())
            .all()
        )

        chat_items = []
        for chat in chats:
            citations = []
            for c in chat.citations:
                if c.chunk:
                    citations.append(Citation(
                        chunk_id=str(c.chunk_id),
                        content=str(c.chunk.content),
                        page_number=int(c.chunk.page_number),
                        relevance_score=c.relevance_score
                    ))
            chat_items.append(ChatHistoryItem(
                id=str(chat.id),
                user_query=str(chat.user_query),
                ai_response=str(chat.ai_response),
                created_at=chat.created_at,  # type: ignore
                response_time=chat.response_time,  # type: ignore
                document_id=str(chat.document_id) if chat.document_id else None,
                conversation_id=str(chat.conversation_id) if chat.conversation_id else None,
                citations=citations
            ))

        return ConversationDetail(
            id=str(conversation.id),
            title=conversation.title,
            created_at=conversation.created_at,  # type: ignore
            updated_at=conversation.updated_at,  # type: ignore
            chats=chat_items
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a conversation and all its chats."""
    try:
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        db.delete(conversation)
        db.commit()

        return {"message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")
