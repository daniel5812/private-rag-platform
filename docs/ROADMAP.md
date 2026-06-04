# Roadmap

## Product Direction

Private RAG Platform is a general-purpose, tenant-aware, workspace-based RAG platform.

It is not limited to a single domain such as finance. Users create workspaces, upload documents, and ask grounded questions over that specific context. Finance, HR, legal, and engineering are future workspace profiles — not separate hardcoded products.

## Target Architecture

```text
Tenant
→ Workspace
→ Documents
→ Chunks + Embeddings
→ Workspace-scoped Retrieval
→ Grounded Answer with Citations
```

## Core Design Principles

- Keep the core RAG engine domain-agnostic
- Use tenants for organization-level data isolation
- Use workspaces for user-facing knowledge contexts
- Use domain profiles to customize behavior without forking the architecture
- Keep retrieved chunks as the source of truth
- Use the LLM only to synthesize retrieved context
- Prefer grounded answers with explicit citations over fluent but unsupported answers
- Keep local-first development compatible with future AWS private deployment

---

## Phase 1 — Local Backend Foundation

**Status: Completed**

- FastAPI backend
- Health endpoints
- Dockerfile and Docker Compose setup
- PostgreSQL service with pgvector extension
- Database connection layer
- Environment-based settings

---

## Phase 2 — Document Ingestion

**Status: Completed**

- `POST /documents/upload`
- File upload handling and local file storage
- Document metadata storage
- Tenant-aware document records
- Text extraction for `.txt` and `.pdf` files via pypdf
- Empty PDF detection with clean error handling
- Failed upload cleanup
- Chunking with configurable overlap
- Chunk storage in PostgreSQL
- Per-chunk embedding generation

**Known limitations:**
- No OCR for scanned PDFs
- No page-level citations
- No background processing

---

## Phase 3 — Embeddings and Vector Storage

**Status: Completed**

- Ollama service in Docker Compose
- `nomic-embed-text` embedding model
- Embedding generation for document chunks
- Embedding storage in PostgreSQL using pgvector
- Query embedding generation

---

## Phase 4 — Semantic Retrieval

**Status: Completed**

- `POST /rag/retrieve`
- Query embedding and pgvector cosine distance search
- Tenant-aware retrieval
- Top-k retrieval with distance scores
- Distance-based filtering (`RETRIEVAL_MAX_DISTANCE = 0.32`)

---

## Phase 5 — RAG Answer Generation

**Status: Completed**

- `POST /rag/ask`
- Prompt builder from retrieved context
- Local LLM generation via Ollama (`llama3.2:1b`)
- Source citations (`[D1]`, `[D2]`, etc.)
- Answer validation (citation check, allowed source check, suspicious phrase detection)
- Grounded fallback answer on validation failure

---

## Phase 6 — Document Management API

**Status: Completed**

- `GET /documents`
- `GET /documents/{document_id}`
- `GET /documents/{document_id}/chunks`

---

## Phase 7 — Document Status Tracking

**Status: Completed**

- Document lifecycle fields: `status`, `error_message`
- Supported statuses: `processing`, `ready`, `failed`
- Upload response includes document status

---

## Phase 8 — Tenant Context Groundwork

**Status: Completed**

- Tenant context extracted from `X-Tenant-ID` request header
- Central `get_tenant_id` dependency
- All RAG and document endpoints use tenant context
- Retrieval filtered by `tenant_id`

**Note:** `X-Tenant-ID` is a development-only mechanism. Production requires authenticated tenant identity from JWT or OAuth claims.

---

## Phase 9 — Workspace Layer

**Status: Completed**

- `workspaces` database table with `tenant_id`, `name`, `description`
- `workspace_id` column on `documents` and `document_chunks`
- Workspace CRUD endpoints (`POST`, `GET`, `PATCH`, `DELETE`)
- `POST /workspaces/{workspace_id}/documents/upload`
- `GET /workspaces/{workspace_id}/documents`
- `POST /workspaces/{workspace_id}/rag/retrieve`
- `POST /workspaces/{workspace_id}/rag/ask`
- `require_workspace` ownership check on every workspace route
- Retrieval filtered by `tenant_id` AND `workspace_id`
- Shared RAG logic refactored into `app/rag/service.py`
- Tests covering workspace retrieval filtering and workspace RAG routes

---

## Phase 10 — Testing Expansion

**Status: Partially Completed**

**Completed:**
- Chunking tests
- Text extraction tests
- PDF error handling tests
- Answer validator tests
- Grounded fallback answer tests
- Retrieval distance filter tests
- Tenant normalization tests
- Workspace-aware retrieval filtering tests
- Workspace RAG route tests
- JWT resolution tests (valid token, expired, wrong secret, missing claim)
- AUTH_DEV_MODE behavior tests

**Planned:**
- Integration tests with real PostgreSQL
- End-to-end pipeline tests
- Tenant isolation tests
- Retrieval threshold evaluation dataset
- Domain inference tests (future)
- Performance benchmarks

---

## Phase 11 — JWT Tenant Resolution + Auth Hardening

**Status: Completed**

- Added `PyJWT` dependency
- Added `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `AUTH_DEV_MODE` config fields
- Docker Compose API service loads backend environment via `env_file`
- `get_tenant_id` now validates `Authorization: Bearer <JWT>` when present
- `tenant_id` extracted from JWT payload; JWT always wins over `X-Tenant-ID`
- Invalid/expired JWT returns 401; missing `tenant_id` claim returns 401
- Bearer token with unconfigured `JWT_SECRET_KEY` returns 401
- `AUTH_DEV_MODE=true` allows `X-Tenant-ID` fallback for local development
- `AUTH_DEV_MODE=false` requires valid JWT — no header fallback
- Workspace/document/RAG filtering unchanged

**Not yet implemented:** OAuth login, users table, internal JWT issuing, tenant membership model.

---

## Next Steps

### Workspace Document Detail Endpoints

- `GET /workspaces/{workspace_id}/documents/{document_id}`
- `GET /workspaces/{workspace_id}/documents/{document_id}/chunks`

These are missing from the workspace-scoped API and needed for a complete document inspection flow.

### Authentication — Remaining Steps

JWT groundwork is in place (Phase 11). Remaining work:

- Local dev helper/script for generating JWT tokens manually
- User model and user-to-tenant membership
- OAuth login flow
- Internal JWT issuing after OAuth login
- Further restrict or remove `X-Tenant-ID` fallback
- RBAC / admin role enforcement (future)

### Async / Background Ingestion

- Accept upload, return `processing` status immediately
- Background worker extracts text, chunks, embeds, updates status to `ready` or `failed`
- Retry logic for transient Ollama failures

### Workspace Profile / Domain Inference

- Infer workspace context (finance, HR, legal, engineering) from uploaded content
- Store `detected_domain` and `user_selected_domain` on workspaces
- Use profile to influence prompt style and answer behavior only — not core retrieval logic
- Allow user to accept or override inferred profile

### Frontend Workspace UI

React + TypeScript frontend:
- Workspace list and creation
- Document upload into workspace
- Chat/query interface inside workspace
- Source citation viewer
- Workspace profile display and override

### Observability / Logging

- Structured request logging
- Retrieval distance and result count logging
- Answer validation outcome logging
- CloudWatch integration for AWS deployment

### AWS Private Deployment

- VPC with public and private subnets
- EC2 or ECS for FastAPI backend
- RDS PostgreSQL with pgvector
- S3 for private document storage
- Secrets Manager for credentials
- CloudWatch for logs and monitoring

---

## Long-Term Vision

A private, secure, workspace-based AI knowledge platform where users can:

- Create a private workspace
- Upload internal documents
- Let the system infer the workspace context
- Override or customize the workspace profile
- Ask grounded questions over that workspace
- See source citations for every answer
- Keep all data tenant-isolated and private
