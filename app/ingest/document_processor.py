import os
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import Document, DocumentChunk
from app.services.pdf_processor import pdf_processor
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store
from app.core.config import settings


class DocumentProcessor:
    """Service for processing and ingesting PDF documents."""
    
    def process_document(self, file_path: str, original_filename: str, db: Session) -> Document:
        """Process a PDF document and store it in the database and vector store."""
        try:
            # Get PDF info
            pdf_info = pdf_processor.get_pdf_info(file_path)
            
            # Extract text chunks
            text_chunks, num_pages = pdf_processor.extract_text_from_pdf(file_path)
            
            # Generate embeddings for chunks
            embeddings = embedding_service.get_embeddings(text_chunks)
            
            # Prepare metadata for vector store
            metadata_list = []
            for i, chunk in enumerate(text_chunks):
                metadata = {
                    "content": chunk,
                    "chunk_index": i,
                    "page_number": self._estimate_page_number(i, len(text_chunks), num_pages),
                    "filename": original_filename
                }
                metadata_list.append(metadata)
            
            # Store embeddings in vector store
            embedding_ids = vector_store.add_embeddings(embeddings, metadata_list)
            
            # Create document record
            document = Document(
                filename=os.path.basename(file_path),
                original_filename=original_filename,
                file_size=pdf_info["num_pages"],
                num_pages=num_pages,
                num_chunks=len(text_chunks)
            )
            
            db.add(document)
            db.flush()  # Get the document ID
            
            # Create chunk records
            for i, (chunk, embedding_id) in enumerate(zip(text_chunks, embedding_ids)):
                document_chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=i,
                    content=chunk,
                    page_number=self._estimate_page_number(i, len(text_chunks), num_pages),
                    embedding_id=embedding_id
                )
                db.add(document_chunk)
            
            # Update document with chunk count
            document.num_chunks = len(text_chunks)
            
            db.commit()
            
            return document
            
        except Exception as e:
            db.rollback()
            print(f"Error processing document {file_path}: {e}")
            raise
    
    def _estimate_page_number(self, chunk_index: int, total_chunks: int, total_pages: int) -> int:
        """Estimate the page number for a chunk based on its position."""
        # Simple linear estimation
        estimated_page = int((chunk_index / total_chunks) * total_pages) + 1
        return min(estimated_page, total_pages)
    
    def delete_document(self, document_id: str, db: Session) -> bool:
        """Delete a document and its associated data."""
        try:
            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return False
            
            # Get chunk embedding IDs
            chunk_embedding_ids = [
                chunk.embedding_id for chunk in document.chunks
            ]
            
            # Delete from vector store
            if chunk_embedding_ids:
                vector_store.delete_embeddings(chunk_embedding_ids)
            
            # Delete from database (cascade will handle chunks)
            db.delete(document)
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error deleting document {document_id}: {e}")
            raise


# Global document processor instance
document_processor = DocumentProcessor() 