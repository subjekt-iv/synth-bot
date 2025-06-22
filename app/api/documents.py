from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from typing import List

from app.db.database import get_db
from app.db.models import Document, DocumentChunk
from app.schemas.document import (
    DocumentUploadResponse, DocumentInfo, DocumentListResponse,
    DocumentChunkInfo, DocumentChunksResponse
)
from app.ingest.document_processor import document_processor
from app.core.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a PDF document."""
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate file size
    if not file.size or file.size > settings.max_file_size:
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
        )
    
    try:
        # Save file temporarily
        file_path = os.path.join(settings.upload_dir, f"{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document
        document: Document = document_processor.process_document(file_path, file.filename, db)
        
        # Clean up temporary file
        os.remove(file_path)
        
        return DocumentUploadResponse(
            document_id=str(document.id),
            filename=str(document.filename),
            original_filename=str(document.original_filename),
            file_size=int(document.file_size),  # type: ignore
            num_pages=int(document.num_pages),  # type: ignore
            num_chunks=int(document.num_chunks),  # type: ignore
            upload_date=document.upload_date,  # type: ignore
            message="Document uploaded and processed successfully"
        )
        
    except Exception as e:
        # Clean up file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get list of uploaded documents."""
    try:
        total = db.query(Document).count()
        documents: List[Document] = db.query(Document).offset(skip).limit(limit).all()
        
        document_list = []
        for doc in documents:
            document_list.append(DocumentInfo(
                id=str(doc.id),
                filename=str(doc.filename),
                original_filename=str(doc.original_filename),
                file_size=int(doc.file_size),  # type: ignore
                num_pages=int(doc.num_pages),  # type: ignore
                num_chunks=int(doc.num_chunks),  # type: ignore
                upload_date=doc.upload_date  # type: ignore
            ))
        
        return DocumentListResponse(
            documents=document_list,
            total=total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get a specific document by ID."""
    try:
        document: Document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentInfo(
            id=str(document.id),
            filename=str(document.filename),
            original_filename=str(document.original_filename),
            file_size=int(document.file_size),  # type: ignore
            num_pages=int(document.num_pages),  # type: ignore
            num_chunks=int(document.num_chunks),  # type: ignore
            upload_date=document.upload_date  # type: ignore
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")


@router.get("/{document_id}/chunks", response_model=DocumentChunksResponse)
async def get_document_chunks(
    document_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chunks for a specific document."""
    try:
        # Verify document exists
        document: Document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        total = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).count()
        chunks: List[DocumentChunk] = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).offset(skip).limit(limit).all()
        
        chunk_list = []
        for chunk in chunks:
            chunk_list.append(DocumentChunkInfo(
                id=str(chunk.id),
                chunk_index=int(chunk.chunk_index),  # type: ignore
                content=str(chunk.content),
                page_number=int(chunk.page_number),  # type: ignore
                embedding_id=str(chunk.embedding_id)
            ))
        
        return DocumentChunksResponse(
            document_id=document_id,
            chunks=chunk_list,
            total=total
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document chunks: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document and its associated data."""
    try:
        success = document_processor.delete_document(document_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}") 