import fitz  # PyMuPDF
import os
from typing import List, Tuple
from app.core.config import settings


class PDFProcessor:
    """Service for processing PDF documents."""
    
    def __init__(self):
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200  # characters overlap between chunks
    
    def extract_text_from_pdf(self, file_path: str) -> Tuple[List[str], int]:
        """Extract text from PDF and return chunks with page numbers."""
        try:
            doc = fitz.open(file_path)
            chunks = []
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():
                    # Split text into chunks
                    page_chunks = self._split_text_into_chunks(text, page_num + 1)
                    chunks.extend(page_chunks)
            
            doc.close()
            return chunks, total_pages
            
        except Exception as e:
            print(f"Error processing PDF {file_path}: {e}")
            raise
    
    def _split_text_into_chunks(self, text: str, page_number: int) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + self.chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def get_pdf_info(self, file_path: str) -> dict:
        """Get basic information about a PDF file."""
        try:
            doc = fitz.open(file_path)
            info = {
                "num_pages": len(doc),
                "file_size": os.path.getsize(file_path),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", "")
            }
            doc.close()
            return info
            
        except Exception as e:
            print(f"Error getting PDF info for {file_path}: {e}")
            raise


# Global PDF processor instance
pdf_processor = PDFProcessor() 