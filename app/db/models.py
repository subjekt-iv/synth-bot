from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Document(Base):
    """Model for storing document metadata."""
    
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    num_pages = Column(Integer, nullable=False)
    num_chunks = Column(Integer, nullable=False, default=0)
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="document")


class DocumentChunk(Base):
    """Model for storing document chunks with their embeddings."""
    
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=False)
    embedding_id = Column(String, nullable=False)  # Qdrant vector ID
    
    # Relationships
    document = relationship("Document", back_populates="chunks")


class Chat(Base):
    """Model for storing chat history."""
    
    __tablename__ = "chats"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    user_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Float, nullable=True)  # Response time in seconds
    
    # Relationships
    document = relationship("Document", back_populates="chats")
    citations = relationship("ChatCitation", back_populates="chat", cascade="all, delete-orphan")


class ChatCitation(Base):
    """Model for storing citations used in chat responses."""
    
    __tablename__ = "chat_citations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String, ForeignKey("chats.id"), nullable=False)
    chunk_id = Column(String, ForeignKey("document_chunks.id"), nullable=False)
    relevance_score = Column(Float, nullable=True)
    
    # Relationships
    chat = relationship("Chat", back_populates="citations")
    chunk = relationship("DocumentChunk") 