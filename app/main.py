from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
print(f"[DEBUG] DISABLE_EMBEDDINGS = {settings.disable_embeddings}")


from app.core.config import settings
from app.db.database import create_tables
from app.services.vector_store import vector_store
from app.api import chat, documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting up Synthesizer Chatbot API...")
    
    # Initialize database tables
    create_tables()
    print("Database tables created/verified")
    
    # Initialize vector store
    try:
        vector_store.initialize_collection()
        print("Vector store initialized")
    except Exception as e:
        print(f"Warning: Could not initialize vector store: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down Synthesizer Chatbot API...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI chatbot for synthesizer manuals using RAG (Retrieval-Augmented Generation)",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(documents.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Synthesizer Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "chat": "/chat",
            "documents": "/documents",
            "upload": "/documents/upload"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
