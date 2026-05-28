# Private RAG Platform — Project Overview

## Product Vision

Private RAG Platform is a secure, local-first Retrieval-Augmented Generation system for asking questions over private internal documents.

The goal is to give organizations an AI knowledge system where documents, embeddings, retrieval, and generation stay entirely under their own control — no external APIs, no data leaving the environment. The platform is built locally first with Docker Compose and is designed to move into an AWS private cloud deployment later.

This project is built as a learning and portfolio project, with emphasis on backend architecture, data isolation, RAG pipeline design, and production-oriented thinking.

## Core Abstraction: Workspaces

The central user-facing concept is the **workspace** (also called a notebook).

```text
Tenant
→ Workspace
→ Documents
→ Chunks + Embeddings
→ Workspace-scoped Retrieval
→ Grounded Answer with Citations
```

A tenant represents an organization. A workspace is a scoped knowledge context within that tenant — for example "Q1 Reports", "HR Policies", or "Engineering Docs". Documents are uploaded into a workspace, and retrieval is always filtered to that workspace.

**Domain-specific behavior (finance, legal, HR, engineering) is a future workspace profile feature — it is not hardcoded into the core architecture.** The RAG engine stays generic; workspace profiles will influence prompt style and answer behavior only.

## RAG Pipeline

```text
Upload document (.txt or .pdf)
→ Extract and validate text
→ Split text into chunks
→ Generate embeddings via Ollama (nomic-embed-text)
→ Store chunks and vectors in PostgreSQL with pgvector
→ User asks a question in a workspace
→ Embed query
→ Retrieve similar chunks filtered by tenant_id + workspace_id
→ Filter chunks by relevance distance (RETRIEVAL_MAX_DISTANCE)
→ Build prompt with retrieved context
→ Generate answer using local LLM (llama3.2:1b via Ollama)
→ Validate answer (citations, suspicious phrases, fallback)
→ Return grounded answer with source citations
```

**Core principle:** The retrieved chunks are the source of truth. The LLM synthesizes context; it does not invent facts.

## Security Boundaries

| Boundary | Mechanism |
|---|---|
| Tenant isolation | `tenant_id` column on all tables; all queries filter by tenant |
| Workspace isolation | `workspace_id` column on documents and chunks; workspace routes filter by workspace |
| Ownership validation | `require_workspace(workspace_id, tenant_id)` called before every workspace operation |
| Retrieval SQL | `document_chunks` filtered by `tenant_id` AND `workspace_id` in every workspace-scoped query |
| Citation validation | `answer_uses_only_allowed_sources` checks that the LLM cites only source IDs from retrieved context — this is a hallucination guardrail, not a security boundary |

**Important:** `X-Tenant-ID` is a development-only tenant mechanism. It is not production authentication. In production, tenant identity must come from a trusted authentication token (JWT or OAuth claims).

## Design Principles

**Data First, LLM Second**
Retrieval happens before generation. The LLM reasons over retrieved context only and should not draw on general knowledge.

**Local-First Development**
The entire stack runs in Docker Compose with no external services or API keys. This enables rapid iteration and keeps the architecture portable to AWS later.

**Private by Design**
No data leaves the controlled environment. Documents, embeddings, and generated answers all stay inside the deployment boundary.

**Grounded Answers with Citations**
Every answer includes source citations (e.g. `[D1]`, `[D2]`). Users and auditors can verify every claim against the source document.

**Guardrails Beyond Prompting**
The system validates answers after generation:
- Citation presence check
- Allowed source ID check (cites only retrieved sources)
- Suspicious phrase detection
- Grounded fallback answer when validation fails
- Distance-based retrieval filtering to avoid returning irrelevant chunks

**Tenant and Workspace Isolation**
Every document and chunk carries both `tenant_id` and `workspace_id`. Retrieval is always filtered by both. Workspace ownership is validated at the route level before any data access.

## Technology Stack

**Backend:** Python 3.10+, FastAPI, Pydantic, asyncpg, httpx, pypdf

**Database:** PostgreSQL 15+ with pgvector extension

**AI / ML:** Ollama (`nomic-embed-text` for embeddings, `llama3.2:1b` for generation)

**Infrastructure:** Docker Compose, Ubuntu VM

## Future AWS Target

- VPC with public and private subnets
- EC2 or ECS for FastAPI backend
- RDS PostgreSQL with pgvector
- S3 for private document storage
- Secrets Manager for credentials
- CloudWatch for logging and monitoring
