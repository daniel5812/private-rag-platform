# Private RAG Platform — Project Overview

## Project Description

Private RAG Platform is a secure, enterprise-style Retrieval-Augmented Generation system for asking questions over private internal documents.

The goal of the project is to build a local-first RAG platform that can later be deployed inside an AWS private cloud environment. The system is designed for organizations that want to use AI over sensitive internal data while keeping documents, embeddings, retrieval, and generation under their own control.

This project is built as a learning and portfolio project, with emphasis on backend architecture, data flow, infrastructure, security thinking, and production-oriented design.

## Core Idea

The system follows a standard RAG pipeline:

```text
Upload document (.txt or .pdf)
→ Extract and validate text
→ Split text into chunks
→ Generate embeddings via Ollama
→ Store chunks and vectors in PostgreSQL with pgvector
→ User asks a question
→ Embed query and retrieve similar chunks
→ Filter chunks by relevance distance (max distance threshold)
→ Generate grounded answer using local LLM
→ Validate answer against retrieved context
→ Return answer with source citations
```

**Core principle**: The database and retrieved chunks are the source of truth. The LLM is used only to synthesize retrieved context, not to generate facts.

## Main Goals

- Allow users to upload private documents (text and PDF).
- Store document metadata in PostgreSQL.
- Extract, chunk, and embed documents locally.
- Store document chunks and embeddings using pgvector.
- Use local/private embeddings and LLM through Ollama.
- Retrieve relevant chunks based on semantic similarity.
- Generate answers grounded in retrieved document context.
- Include citations for every answer source.
- Filter out low-relevance retrievals to prevent hallucination.
- Prevent cross-tenant data leakage.
- Build toward a future AWS private cloud deployment.

## Current Technology Stack

**Backend**
- Python 3.10+
- FastAPI (async web framework)
- Pydantic (data validation)
- asyncpg (async PostgreSQL driver)
- httpx (async HTTP client for Ollama)
- pypdf (PDF text extraction)

**Database**
- PostgreSQL 15+
- pgvector extension (vector similarity search)

**AI / ML Runtime**
- Ollama (local model serving)
- `nomic-embed-text` (text embeddings)
- `llama3.2:1b` (local answer generation)

**Infrastructure**
- Docker & Docker Compose (local containerization)
- Ubuntu 22.04 VM (local development)
- VMware (hypervisor for local VM)

## Future Cloud Target

**AWS Architecture**
- VPC with public and private subnets
- EC2 or ECS for FastAPI backend
- RDS PostgreSQL with pgvector extension
- S3 for private document storage
- Secrets Manager for credentials
- CloudWatch for logging
- Optional: Bedrock or self-hosted GPU instances for embeddings

## Design Principles

**1. Data First, LLM Second**

The system retrieves relevant data before asking the LLM to answer. The LLM only reasons over retrieved context and should not invent facts. Retrieved context is always the source of truth, not the model's general knowledge.

**2. Local-First Development**

The MVP is built locally first using Docker Compose. This makes development easier, enables rapid iteration, and prepares the architecture for future AWS deployment. Developers should not require external services or API keys to build and test locally.

**3. Private by Design**

Documents, embeddings, and generated answers remain inside the controlled environment. No data is sent to external APIs or third-party services. The system is designed to be deployed behind a VPC in AWS with no public access.

**4. Tenant-Aware Architecture**

Every document and chunk is stored with a `tenant_id`. This enables multi-tenant deployment and prevents cross-tenant data leakage. The current MVP uses a hardcoded tenant (`demo`), but future versions should derive tenant identity from authentication tokens.

**5. Grounded Answers with Source Citations**

Every generated answer is based on retrieved chunks and includes source citations (e.g., `[D1]`, `[D2]`). Users and auditors should be able to verify every claim by reading the source document.

**6. Guardrails Beyond Prompting**

Prompting alone is not enough to prevent hallucinations. The system includes validation logic to:
- Check that answers cite their sources
- Detect unsupported or suspicious phrases not in context
- Replace unsafe answers with grounded fallback responses
- Filter retrievals by relevance distance to avoid "best of bad options"

**7. Reliability & Robustness**

The system handles errors gracefully:
- Empty or malformed PDFs return clear error messages
- Failed uploads are cleaned up (no orphaned metadata)
- Ingestion is atomic (metadata inserted only after chunks succeed)
- Retrieval threshold prevents hallucination from lack of context