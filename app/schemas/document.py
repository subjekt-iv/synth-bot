from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: str
    filename: str
    original_filename: str
    file_size: int
    num_pages: int
    num_chunks: int
    upload_date: datetime
    message: str


class DocumentInfo(BaseModel):
    """Model for document information."""
    id: str
    filename: str
    original_filename: str
    file_size: int
    num_pages: int
    num_chunks: int
    upload_date: datetime


class DocumentListResponse(BaseModel):
    """Response model for document list."""
    documents: List[DocumentInfo]
    total: int


class DocumentChunkInfo(BaseModel):
    """Model for document chunk information."""
    id: str
    chunk_index: int
    content: str
    page_number: int
    embedding_id: str


class DocumentChunksResponse(BaseModel):
    """Response model for document chunks."""
    document_id: str
    chunks: List[DocumentChunkInfo]
    total: int 