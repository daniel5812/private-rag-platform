# Private RAG Platform

A secure, enterprise-grade Retrieval-Augmented Generation (RAG) system for asking questions over private internal documents. Built as a local-first platform designed for future AWS private cloud deployment.

**Key Features:**
- Semantic search over document text and PDFs
- Local LLM and embeddings (no external APIs)
- Grounded answers with source citations
- Multi-tenant support with data isolation
- Hallucination guardrails beyond prompting

## Quick Start

### Prerequisites

- Docker & Docker Compose
- 50GB+ disk space
- 8GB+ RAM (minimum for Ollama + PostgreSQL)

### Start the System

```bash
docker compose -f infra/docker-compose.yml up --build
```

This starts:
- **API** — FastAPI backend on `http://localhost:8000`
- **PostgreSQL** — Vector database with pgvector
- **Ollama** — Local embeddings and LLM runtime

### Test the API

Upload a document:

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@sample.txt" \
  -F "tenant_id=demo"
```

Ask a question:

```bash
curl -X POST "http://localhost:8000/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is access control?","tenant_id":"demo","top_k":3}'
```

### Run Tests

```bash
docker compose -f infra/docker-compose.yml run --rm api pytest tests -v
```

### Useful Commands

```bash
# Stop the system
docker compose -f infra/docker-compose.yml down

# View API logs
docker compose -f infra/docker-compose.yml logs api --tail=80

# Query PostgreSQL directly
docker exec -it private-rag-db psql -U rag_user -d private_rag
```

## Documentation

- **[Project Overview](docs/PROJECT_OVERVIEW.md)** — Architecture, design principles, tech stack
- **[Current State](docs/CURRENT_STATE.md)** — Implemented features and current API endpoints
- **[Issues Solved](docs/ISSUES_SOLVED.md)** — Technical problems solved during development
- **[Roadmap](docs/ROADMAP.md)** — Completed and planned phases

## Current Capabilities

✅ Upload text and PDF documents  
✅ Semantic search with vector similarity  
✅ Grounded answer generation with citations  
✅ Distance-based relevance filtering  
✅ Answer validation to reduce hallucinations  
✅ Document management endpoints  
✅ Unit tests (15 passing)

## Planned

- Authentication and user-based tenant isolation
- Frontend (React + TypeScript)
- Better PDF support (page-level citations, OCR)
- AWS deployment (VPC, RDS, S3)
- Background job system for large uploads

## Technology Stack

**Backend:** Python, FastAPI, Pydantic  
**Database:** PostgreSQL + pgvector  
**AI/ML:** Ollama (nomic-embed-text, llama3.2:1b)  
**Infrastructure:** Docker Compose, Ubuntu VM