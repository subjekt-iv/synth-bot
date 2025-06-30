# Synthesizer Chatbot API

A FastAPI-based RAG (Retrieval-Augmented Generation) chatbot system that can process PDF documents, create embeddings, and provide intelligent responses with citations. The application is specifically designed to work with synthesizer manuals and technical documentation.

## project overview

This API provides a complete solution for:

- **Document Processing**: Upload and process PDF synthesizer manuals
- **Intelligent Chat**: Ask questions about uploaded documents with AI-powered responses
- **Citation System**: Get precise citations from source documents
- **Vector Search**: Advanced similarity search using embeddings
- **Multi-Document Support**: Handle multiple manuals simultaneously

## tech stack

- **Python 3.11+** - Core programming language
- **FastAPI** - Modern, fast web framework for building APIs
- **LangChain** - RAG orchestration and LLM integration
- **OpenAI API** - Embeddings (text-embedding-3-small) and completions (gpt-3.5-turbo)
- **Qdrant** - Vector database for similarity search and storage
- **PostgreSQL** - Metadata storage for documents, chunks, and chat history
- **PyMuPDF** - High-performance PDF parsing and text extraction
- **SQLAlchemy + Alembic** - ORM and database migrations
- **Docker + Docker Compose** - Containerization and orchestration
- **Pydantic** - Data validation and settings management

## project structure

```
backend/
├── app/
│   ├── api/                    # FastAPI route definitions
│   │   ├── __init__.py
│   │   ├── chat.py            # Chat endpoints (/chat/, /chat/history)
│   │   └── documents.py       # Document management endpoints
│   ├── core/                   # Configuration and settings
│   │   ├── __init__.py
│   │   └── config.py          # Environment configuration
│   ├── db/                     # Database models and connection
│   │   ├── __init__.py
│   │   ├── models.py          # SQLAlchemy models (Document, DocumentChunk, Chat, ChatCitation)
│   │   └── database.py        # Database connection and session management
│   ├── ingest/                 # Document ingestion pipeline
│   │   ├── __init__.py
│   │   └── document_processor.py
│   ├── rag/                    # RAG chain implementation
│   │   ├── __init__.py
│   │   └── chain.py           # LangChain RAG pipeline
│   ├── schemas/                # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── chat.py            # Chat request/response schemas
│   │   └── document.py        # Document schemas
│   ├── services/               # Core services
│   │   ├── __init__.py
│   │   ├── embeddings.py      # OpenAI embeddings service
│   │   ├── pdf_processor.py   # PDF processing service
│   │   └── vector_store.py    # Qdrant vector store service
│   └── main.py                 # FastAPI application entrypoint
├── alembic/                    # Database migrations
│   ├── env.py                 # Alembic environment configuration
│   └── script.py.mako         # Migration template
├── tests/                      # Unit and integration tests
│   └── test_chat.py           # Chat functionality tests
├── uploads/                    # Uploaded PDF files storage
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Multi-service orchestration
├── alembic.ini                # Alembic configuration
├── PROJECT_STATUS.md          # Detailed project status and roadmap
└── README.md                  # This file
```

## quick start

### prerequisites

- **Python 3.11+**
- **Docker and Docker Compose**
- **OpenAI API key** (required for embeddings and completions)

### 1. clone and setup

```bash
git clone <repository-url>
cd backend
```

### 2. environment configuration

Create a `.env` file in the root directory:

```bash
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant Vector Database
QDRANT_API_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_here  # Optional

# PostgreSQL Database (Project B - Synth Bot Configuration)
DATABASE_URL=postgresql://user:password@localhost:5433/synthesizer_chatbot

# Application Settings
APP_NAME=Synthesizer Chatbot API
DEBUG=True
LOG_LEVEL=INFO

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR=./uploads
```

### 3. using docker compose (recommended)

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild and restart
docker compose up -d --build
```

### 4. manual setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Qdrant (using Docker)
docker compose up -d postgres qdrant

# Run database migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## service configuration

### port configuration (project b - synth bot)

**Updated to avoid conflicts with Project A (Ledger):**

- **PostgreSQL**: Port 5433 (changed from 5432 to avoid conflict)
- **FastAPI**: Port 8000 (different from Project A's 8080)
- **Qdrant**: Port 6333 (no conflict)
- **Qdrant gRPC**: Port 6334 (no conflict)

**Project A (Ledger) uses:**

- PostgreSQL: 5432
- Redis: 6379
- React Frontend: 3000
- Backend API: 8080

### service urls

- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **FastAPI Application**: http://localhost:8000

## api endpoints

### chat endpoints

#### `POST /chat/`

Process a chat query and return a response with citations.

**Request Body:**

```json
{
  "query": "What are the main features of this synthesizer?",
  "document_id": "optional-document-id"
}
```

**Response:**

```json
{
  "response": "Based on the manual, this synthesizer features...",
  "citations": [
    {
      "chunk_id": "chunk-uuid",
      "content": "The synthesizer includes...",
      "page_number": 5,
      "relevance_score": 0.95
    }
  ],
  "response_time": 1.23
}
```

#### `GET /chat/history`

Get chat history with optional filtering.

**Query Parameters:**

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 50)
- `document_id`: Filter by specific document (optional)

### document endpoints

#### `POST /documents/upload`

Upload and process a PDF document.

**Request:** Multipart form with PDF file

**Response:**

```json
{
  "document_id": "doc-uuid",
  "filename": "processed-filename.pdf",
  "original_filename": "original-name.pdf",
  "file_size": 1024000,
  "num_pages": 25,
  "num_chunks": 150,
  "upload_date": "2024-01-01T12:00:00Z",
  "message": "Document uploaded and processed successfully"
}
```

#### `GET /documents/`

List all uploaded documents.

#### `GET /documents/{document_id}`

Get specific document information.

#### `GET /documents/{document_id}/chunks`

Get chunks for a specific document.

#### `DELETE /documents/{document_id}`

Delete a document and its associated data.

### utility endpoints

#### `GET /`

API information and available endpoints.

#### `GET /health`

Health check endpoint.

## testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_chat.py -v
```

## development

### database migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### code quality

```bash
# Format code (if using black)
black app/ tests/

# Lint code (if using ruff)
ruff check app/ tests/

# Type checking (if using mypy)
mypy app/
```

### development commands

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run FastAPI in development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Connect to PostgreSQL (Project B)
psql -h localhost -p 5433 -U user -d synthesizer_chatbot
```

## docker

### build and run

```bash
# Build the image
docker build -t synthesizer-chatbot .

# Run with environment variables
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e DATABASE_URL=postgresql://user:password@host:5433/synthesizer_chatbot \
  -e QDRANT_API_URL=http://host:6333 \
  synthesizer-chatbot
```

### docker compose services

- **app**: FastAPI application (port 8000)
- **postgres**: PostgreSQL database (port 5433)
- **qdrant**: Qdrant vector database (ports 6333, 6334)

### health checks

All services include health checks:

- **PostgreSQL**: Uses `pg_isready` to verify database connectivity
- **Qdrant**: Uses TCP connection test to verify service availability
- **FastAPI**: Built-in health check endpoint

## usage examples

### 1. upload a manual

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@synthesizer_manual.pdf"
```

### 2. ask a question

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I connect this synthesizer to my computer?",
    "document_id": "optional-document-id"
  }'
```

### 3. get chat history

```bash
curl -X GET "http://localhost:8000/chat/history?limit=10"
```

### 4. list documents

```bash
curl -X GET "http://localhost:8000/documents/"
```

## security considerations

- Set appropriate CORS origins for production
- Use environment variables for sensitive configuration
- Implement authentication/authorization as needed
- Validate file uploads and implement size limits
- Use HTTPS in production
- Secure API keys and database credentials
- Implement rate limiting for API endpoints

## production deployment

1. Set `DEBUG=False` in environment variables
2. Configure proper database credentials
3. Set up reverse proxy (nginx/traefik)
4. Implement proper logging
5. Set up monitoring and health checks
6. Configure backup strategies for database and vector store
7. Use production-grade PostgreSQL and Qdrant instances
8. Implement proper error handling and monitoring

## useful links

- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Project Status**: See `PROJECT_STATUS.md` for detailed status and roadmap

## license

This project is licensed under the MIT License - see the LICENSE file for details.

---
