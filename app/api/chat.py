from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time
from typing import Optional


from app.db.database import get_db
from app.db.models import Chat, ChatCitation, DocumentChunk
from app.schemas.chat import ChatRequest, ChatResponse, Citation, ChatHistoryResponse, ChatHistoryItem
from app.rag.chain import rag_chain

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Process a chat query and return a response with citations."""
    start_time = time.time()
    
    try:
        # Process query through RAG chain
        result = rag_chain.process_query(request.query)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Create chat record
        chat = Chat(
            user_query=request.query,
            ai_response=result["response"],
            response_time=response_time,
            document_id=request.document_id
        )
        
        db.add(chat)
        db.flush()  # Get the chat ID
        
        # Create citation records
        citations = []
        for chunk_data in result["relevant_chunks"]:
            # Find the corresponding chunk in database
            chunk = db.query(DocumentChunk).filter(
                DocumentChunk.embedding_id == chunk_data["id"]
            ).first()
            
            if chunk:
                citation = ChatCitation(
                    chat_id=chat.id,
                    chunk_id=chunk.id,
                    relevance_score=chunk_data["score"]
                )
                db.add(citation)
                
                # Add to response citations
                citations.append(Citation(
                    chunk_id=str(chunk.id),
                    content=str(chunk.content),
                    page_number=int(chunk.page_number),  # type: ignore
                    relevance_score=chunk_data["score"]
                ))
        
        db.commit()
        
        return ChatResponse(
            response=result["response"],
            citations=citations,
            response_time=response_time
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    document_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get chat history with optional filtering by document."""
    try:
        query = db.query(Chat)
        
        if document_id:
            query = query.filter(Chat.document_id == document_id)
        
        total = query.count()
        chats = query.offset(skip).limit(limit).all()
        
        chat_items = []
        for chat in chats:
            chat_items.append(ChatHistoryItem(
                id=str(chat.id),
                user_query=str(chat.user_query),
                ai_response=str(chat.ai_response),
                created_at=chat.created_at,  # type: ignore
                response_time=chat.response_time,  # type: ignore
                document_id=str(chat.document_id)
            ))
        
        return ChatHistoryResponse(
            chats=chat_items,
            total=total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}") 