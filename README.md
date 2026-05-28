# Private RAG Platform

A secure, local-first Retrieval-Augmented Generation (RAG) platform for asking questions over private internal documents. Built with FastAPI, PostgreSQL + pgvector, and Ollama — no external APIs required.

**Key Features:**
- Multi-tenant data isolation with workspace-scoped retrieval
- Semantic search over text and PDF documents
- Grounded answers with source citations
- Hallucination guardrails beyond prompting
- Fully local stack: embeddings and LLM run inside Docker via Ollama

## Architecture

```text
Tenant
→ Workspace
→ Documents
→ Chunks + Embeddings (pgvector)
→ Workspace-scoped Retrieval
→ Grounded Answer with Citations
```

**Security boundaries:**
- `tenant_id` — isolates all data between organizations
- `workspace_id` — isolates retrieval within a tenant
- `require_workspace` — validates ownership before any workspace operation

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Pydantic |
| Database | PostgreSQL 15 + pgvector |
| Embeddings / LLM | Ollama (`nomic-embed-text`, `llama3.2:1b`) |
| Infrastructure | Docker Compose |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- 8GB+ RAM
- 50GB+ disk space

### Start the System

```bash
docker compose -f infra/docker-compose.yml up --build
```

This starts:
- **API** — FastAPI on `http://localhost:8000`
- **PostgreSQL** — vector database with pgvector
- **Ollama** — local embeddings and LLM runtime

### Run Tests

```bash
docker compose -f infra/docker-compose.yml run --rm api pytest tests -v
```

## API Overview

Tenant context is passed via the `X-Tenant-ID` header on every request. This is a development-only mechanism — production should use JWT/OAuth.

### Health

```
GET  /health
GET  /health/db
```

### Workspace Endpoints

```
POST   /workspaces
GET    /workspaces
GET    /workspaces/{workspace_id}
PATCH  /workspaces/{workspace_id}
DELETE /workspaces/{workspace_id}
```

### Workspace Document Upload

```bash
# Upload a document into a workspace
curl -X POST "http://localhost:8000/workspaces/{workspace_id}/documents/upload" \
  -H "X-Tenant-ID: demo" \
  -F "file=@report.pdf"

# List documents in a workspace
curl "http://localhost:8000/workspaces/{workspace_id}/documents" \
  -H "X-Tenant-ID: demo"
```

### Workspace RAG

```bash
# Retrieve relevant chunks (workspace-scoped)
curl -X POST "http://localhost:8000/workspaces/{workspace_id}/rag/retrieve" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{"query": "What is the access control policy?", "top_k": 3}'

# Ask a question (workspace-scoped)
curl -X POST "http://localhost:8000/workspaces/{workspace_id}/rag/ask" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{"query": "What is the access control policy?", "top_k": 3}'
```

### Legacy Tenant-Level RAG

```
POST /rag/retrieve
POST /rag/ask
POST /documents/upload
GET  /documents
GET  /documents/{document_id}
GET  /documents/{document_id}/chunks
```

Legacy endpoints remain for development and debugging. The workspace-scoped endpoints are the primary product API.

## Documentation

- [Project Overview](docs/PROJECT_OVERVIEW.md) — vision, RAG flow, security model
- [Current State](docs/CURRENT_STATE.md) — implemented features, endpoints, limitations
- [Roadmap](docs/ROADMAP.md) — completed phases and next steps
- [Issues Solved](docs/ISSUES_SOLVED.md) — technical problems and solutions

## Planned

- JWT/OAuth authentication replacing `X-Tenant-ID`
- Async background ingestion
- Workspace profile / domain inference
- Frontend (React + TypeScript)
- AWS private deployment (VPC, RDS, S3)
