# Current State

## Project Status

The project has a working local MVP of a private, multi-tenant, workspace-scoped RAG pipeline.

The implemented architecture is:

```text
Tenant
→ Workspace
→ Documents
→ Chunks + Embeddings
→ Workspace-scoped Retrieval
→ Grounded Answer with Citations
```

## Completed Work

- Dockerized FastAPI backend (API, PostgreSQL, Ollama services)
- PostgreSQL + pgvector for vector storage and similarity search
- Document upload: text extraction, chunking, embedding, storage
- Tenant context via `X-Tenant-ID` header and `get_tenant_id` dependency
- Workspace CRUD endpoints
- Workspace-scoped document upload and document listing
- Workspace-scoped retrieval and answer generation
- Shared RAG logic refactored into `app/rag/service.py`
- Legacy tenant-level RAG endpoints preserved for development/debug
- Tests covering: tenant handling, retrieval distance filtering, workspace-aware retrieval, workspace RAG routes, answer builder/validator, text extraction, chunking

## Current API Endpoints

Tenant context is required on every request via `X-Tenant-ID: <tenant>`.

### Health

```
GET  /health
GET  /health/db
```

### Workspaces

```
POST   /workspaces
GET    /workspaces
GET    /workspaces/{workspace_id}
PATCH  /workspaces/{workspace_id}
DELETE /workspaces/{workspace_id}
```

### Workspace Documents

```
POST  /workspaces/{workspace_id}/documents/upload
GET   /workspaces/{workspace_id}/documents
```

Example upload:

```bash
curl -X POST "http://localhost:8000/workspaces/{workspace_id}/documents/upload" \
  -H "X-Tenant-ID: demo" \
  -F "file=@report.pdf"
```

### Workspace RAG

```
POST  /workspaces/{workspace_id}/rag/retrieve
POST  /workspaces/{workspace_id}/rag/ask
```

Example:

```bash
curl -X POST "http://localhost:8000/workspaces/{workspace_id}/rag/ask" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{"query": "What is the access control policy?", "top_k": 3}'
```

### Legacy Tenant-Level Endpoints

```
POST /documents/upload
GET  /documents
GET  /documents/{document_id}
GET  /documents/{document_id}/chunks
POST /rag/retrieve
POST /rag/ask
```

These remain active for debugging and backward compatibility. Workspace-scoped endpoints are the primary product API.

## Document Upload Flow

```text
User uploads file into a workspace
→ API reads tenant_id from X-Tenant-ID
→ API validates workspace ownership (require_workspace)
→ Text is extracted from .txt or .pdf
→ Text is split into overlapping chunks
→ Each chunk is embedded via Ollama (nomic-embed-text)
→ Chunks stored in document_chunks with tenant_id + workspace_id
→ Document metadata inserted into documents table
→ Document status returned
```

## Question Answering Flow

```text
User asks a question in a workspace
→ API reads tenant_id from X-Tenant-ID
→ API validates workspace ownership (require_workspace)
→ Query is embedded via Ollama
→ pgvector retrieves similar chunks filtered by tenant_id + workspace_id
→ Chunks filtered by distance threshold (RETRIEVAL_MAX_DISTANCE = 0.32)
→ Prompt is built from retrieved context
→ Ollama LLM generates answer (llama3.2:1b)
→ Answer validator checks citations and suspicious phrases
→ Unsafe answers replaced with grounded fallback
→ API returns grounded answer and source citations
```

## Database Tables

### documents

| Field | Notes |
|---|---|
| id | UUID |
| tenant_id | organization isolation |
| workspace_id | workspace isolation |
| filename | original upload filename |
| content_type | txt or pdf |
| storage_path | local file path |
| status | processing / ready / failed |
| error_message | set on failure |
| created_at | |

### document_chunks

| Field | Notes |
|---|---|
| id | UUID |
| document_id | FK to documents |
| tenant_id | denormalized for query performance |
| workspace_id | denormalized for query performance |
| chunk_index | position in document |
| content | raw chunk text |
| embedding | pgvector column |
| created_at | |

### workspaces

| Field | Notes |
|---|---|
| id | UUID |
| tenant_id | owner organization |
| name | user-defined workspace name |
| description | optional |
| created_at | |
| updated_at | |

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Pydantic, asyncpg, httpx, pypdf |
| Database | PostgreSQL 15+, pgvector |
| Embeddings / LLM | Ollama, nomic-embed-text, llama3.2:1b |
| Infrastructure | Docker Compose, Ubuntu VM |

## Retrieval Distance Threshold

Chunks above the distance threshold are filtered before reaching the answer generation stage.

```
RETRIEVAL_MAX_DISTANCE = 0.32
```

This prevents the system from returning the "closest bad chunk" when no relevant context exists. The threshold is a heuristic and should be evaluated against a labeled retrieval dataset.

## Answer Validation

After LLM generation, the system validates the answer:

- Answer includes citations
- Answer cites only source IDs that were in the retrieved context
- Answer avoids known suspicious hallucination phrases
- Unsafe answers are replaced with a grounded fallback

The citation check (`answer_uses_only_allowed_sources`) is a hallucination guardrail — it is not the tenant or workspace security boundary. Access control happens at the SQL layer before retrieval.

## Current Tests

Test coverage includes:

- Tenant handling and normalization
- Retrieval distance filtering
- Workspace-aware retrieval filtering
- Workspace RAG route behavior
- Answer builder and validator logic
- Text extraction (.txt and .pdf)
- PDF error handling
- Chunking

Run tests:

```bash
docker compose -f infra/docker-compose.yml run --rm api pytest tests -v
```

## Current Limitations

- No real authentication or JWT yet — `X-Tenant-ID` is a development-only header
- No user model or user-to-tenant membership
- Ingestion is synchronous — large uploads block the request
- No workspace profile or domain inference yet
- No frontend yet
- No workspace document detail or chunk inspection endpoints yet
- No background job system yet
- No page-level PDF citations
- No OCR for scanned PDFs
- Answer validation is rule-based (heuristic)
- No production AWS deployment yet
- Database schema managed via `init.sql` — no migration framework yet
