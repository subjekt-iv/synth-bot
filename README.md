# Synth Bot

A RAG-powered chatbot for synthesizer manuals. Upload your synth manuals (PDF), ask questions about your gear, and get answers with page-level citations sourced from the actual documentation.

## Structure

```
synth-bot/
  backend/            FastAPI REST API, RAG pipeline, vector search
  ui/                 React frontend with AI chat interface
  docker-compose.yml  Orchestrates backend, PostgreSQL, and Qdrant
```

## Backend

FastAPI application with a RAG (Retrieval-Augmented Generation) pipeline:

- PDF ingestion with text extraction and chunking
- Embeddings via OpenAI (text-embedding-3-small)
- Vector search via Qdrant
- Chat with conversation support and page-level citations
- PostgreSQL for metadata, Qdrant for vector storage

Tech: Python 3.11, FastAPI, LangChain, OpenAI API, Qdrant, PostgreSQL, SQLAlchemy, Alembic

See `backend/` for full backend documentation.

## Frontend

React application with a purpose-built AI chat interface:

- Conversation-based chat with sidebar history
- Markdown rendering with syntax-highlighted code blocks
- Expandable citations showing source text, page numbers, and relevance scores
- Manual (PDF) upload and management
- Dark/light theme

Tech: React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui, Prompt Kit

See `ui/README.md` for full frontend documentation.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+
- OpenAI API key

### Run the backend

```bash
export OPENAI_API_KEY=your-key-here

# From repo root:
docker compose up -d
```

This starts PostgreSQL, Qdrant, and the FastAPI app on http://localhost:8000.

### Run the frontend

```bash
cd ui
npm install
npm run dev
```

Opens on http://localhost:3000, proxies API requests to the backend.

### Usage

1. Go to Manuals and upload a synthesizer manual (PDF)
2. Start a new chat and ask questions about your synth
3. Responses include citations with page numbers from your manuals
