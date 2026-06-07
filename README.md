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

## Environment Variables

Key variables — set in `.env` or Docker Compose `env_file`:

```env
JWT_SECRET_KEY=change-me-local-dev-secret
JWT_ALGORITHM=HS256
AUTH_DEV_MODE=true
```

- `JWT_SECRET_KEY` must never be hardcoded. Load from environment or secrets manager.
- `AUTH_DEV_MODE=true` enables the `X-Tenant-ID` header fallback for local development.
- `AUTH_DEV_MODE=false` requires a valid JWT on every request (no header fallback).

## API Overview

### Authentication

JWT is the preferred tenant resolution method:

```http
Authorization: Bearer <JWT>
```

The JWT payload must include a `tenant_id` claim:

```json
{ "tenant_id": "demo" }
```

When `AUTH_DEV_MODE=true`, the `X-Tenant-ID` header is accepted as a fallback if no `Authorization` header is present. JWT always wins if both are provided.

> No login or OAuth endpoint exists yet. In local dev, tokens must be generated manually with the configured `JWT_SECRET_KEY`.

### Creating a development JWT

When `JWT_SECRET_KEY` is configured, local API requests can use a JWT:

```bash
export JWT_SECRET_KEY="dev-secret"
export JWT_ALGORITHM="HS256"

TOKEN=$(./scripts/create-dev-token.py --tenant demo)

curl -s http://localhost:8000/workspaces \
  -H "Authorization: Bearer $TOKEN"

This is a local development helper only. It is not a login or OAuth flow.


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
# Upload a document into a workspace (JWT)
curl -X POST "http://localhost:8000/workspaces/{workspace_id}/documents/upload" \
  -H "Authorization: Bearer <JWT>" \
  -F "file=@report.pdf"

# List documents in a workspace (JWT)
curl "http://localhost:8000/workspaces/{workspace_id}/documents" \
  -H "Authorization: Bearer <JWT>"
```

With `AUTH_DEV_MODE=true`, `X-Tenant-ID: demo` works as a fallback instead.

### Workspace RAG

```bash
# Ask a question (workspace-scoped, JWT)
curl -X POST "http://localhost:8000/workspaces/{workspace_id}/rag/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
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

- OAuth login flow + internal JWT issuing (groundwork done; login not yet implemented)
- User model and tenant membership
- Async background ingestion
- Workspace profile / domain inference
- Frontend (React + TypeScript)
- AWS private deployment (VPC, RDS, S3)
