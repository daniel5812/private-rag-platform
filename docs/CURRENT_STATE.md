---

# `docs/CURRENT_STATE.md`

```md
# Current State

## Project Status

The project currently has a working local MVP of a private, tenant-aware RAG pipeline.

The system can upload text and PDF documents, extract and chunk text, generate embeddings locally, store vectors in PostgreSQL with pgvector, retrieve relevant chunks, and generate grounded answers with source citations.

The project direction has evolved from a simple private document RAG system into a more general Private RAG Platform.

The next major architecture step is to introduce a workspace/notebook layer.

Current structure:

```text
Tenant
→ Documents
→ Chunks
→ Embeddings
→ Retrieval
→ Grounded Answer

Target structure:

Tenant
→ Workspace / Notebook
→ Documents
→ Chunks
→ Embeddings
→ Retrieval
→ Workspace-aware Grounded Answer
Strategic Direction

The project should remain domain-agnostic.

It should not be hardcoded as a finance system, legal system, HR system, or engineering system.

Instead, the platform should support multiple use cases through workspace profiles.

Examples:

Finance reports
HR policies
Legal contracts
Engineering documentation
Academic papers
Internal company policies

The future workspace model should support a hybrid approach:

Automatic domain/context inference + user override

For example:

User creates a notebook called "Q1 Reports"
→ Uploads financial reports
→ System detects finance/reporting context
→ User can accept or override the workspace profile

This allows the core RAG architecture to stay generic while still providing domain-aware behavior.

Current Capabilities

The system can:

Run a FastAPI backend inside Docker.
Run PostgreSQL with pgvector inside Docker.
Run Ollama inside Docker.
Upload .txt and .pdf documents.
Store document metadata in PostgreSQL.
Store uploaded files in local Docker storage.
Extract text from .txt and .pdf files.
Handle empty or invalid PDFs with clean error responses.
Clean up failed uploads.
Split extracted text into chunks with overlap.
Generate embeddings using Ollama and nomic-embed-text.
Store chunk embeddings in PostgreSQL using pgvector.
Retrieve semantically relevant chunks with distance-based filtering.
Generate grounded answers using a local LLM.
Return citations and retrieved source chunks.
Apply answer validation to reduce hallucinations.
List documents, view document details, and inspect chunks through API endpoints.
Track document status.
Use request-level tenant context through X-Tenant-ID.
Current Technology Stack
Backend
Python
FastAPI
Pydantic
asyncpg
httpx
pypdf
Database
PostgreSQL
pgvector
AI / ML Runtime
Ollama
nomic-embed-text
llama3.2:1b
Infrastructure
Docker
Docker Compose
Ubuntu VM
VMware local development environment
Current Docker Services

The system uses Docker Compose with the following services:

api

FastAPI backend.

Default local URL:

http://localhost:8000
db

PostgreSQL database with pgvector extension.

ollama

Local Ollama runtime used for embeddings and answer generation.

Current Models
Embedding Model
nomic-embed-text

Used to convert document chunks and user queries into vectors.

Generation Model
llama3.2:1b

Used to generate local answers from retrieved context.

Current API Endpoints
GET /health

Returns basic service status.

GET /health/db

Checks that the FastAPI backend can connect to PostgreSQL.

Document Endpoints
POST /documents/upload

Uploads a document and stores:

document metadata
original file
extracted text chunks
embeddings for each chunk

Supported file types:

.txt
.pdf

Example:

curl -i -X POST "http://localhost:8000/documents/upload" \
  -H "X-Tenant-ID: demo" \
  -F "file=@sample.txt"
GET /documents

Returns metadata for all tenant-filtered documents.

GET /documents/{document_id}

Returns metadata for a specific document.

GET /documents/{document_id}/chunks

Returns extracted chunks for a document.

RAG Endpoints
POST /rag/retrieve

Retrieves the most relevant document chunks based on vector similarity.

Example:

curl -i -X POST "http://localhost:8000/rag/retrieve" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{"query":"What does the document say about access control?","top_k":3}'
POST /rag/ask

Generates a grounded answer based on retrieved context.

Example:

curl -i -X POST "http://localhost:8000/rag/ask" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{"query":"What does the document say about access control?","top_k":3}'

Example answer:

The document mentions access control in relation to internal company policy, permissions, secure document retrieval, and employee access management. [D1]
Tenant Context

The MVP now uses request-level tenant context.

Current transitional mechanism:

X-Tenant-ID: demo

This allows the API to filter documents and retrieval by tenant.

Current behavior:

Request with X-Tenant-ID: demo
→ searches only demo documents

Request with X-Tenant-ID: other-tenant
→ does not see demo documents

Important:

X-Tenant-ID is not production authentication.

In production, tenant identity should come from a trusted authentication mechanism such as JWT or OAuth claims.

Current Database Tables
documents

Stores uploaded document metadata.

Important fields:

id
tenant_id
filename
content_type
storage_path
status
error_message
created_at
document_chunks

Stores extracted document chunks and embeddings.

Important fields:

id
document_id
tenant_id
chunk_index
content
embedding
created_at
Current Working Flow
Document Upload Flow
User uploads document
→ API reads tenant context
→ FastAPI saves file
→ Text is extracted from txt/pdf
→ Text is split into chunks
→ Each chunk is embedded using Ollama
→ Chunk + vector are stored in document_chunks
→ Document metadata is inserted into documents table
→ Document status is returned
Question Answering Flow
User asks a question
→ API reads tenant context
→ Query is embedded using Ollama
→ PostgreSQL pgvector retrieves similar chunks for that tenant
→ Chunks are filtered by distance threshold
→ Prompt is built with retrieved context
→ Ollama LLM generates answer
→ Answer validator checks citations and suspicious hallucinations
→ Unsafe answers are replaced with grounded fallback answer
→ API returns grounded answer and sources
Retrieval Distance Threshold

The system uses a distance threshold to avoid returning irrelevant chunks.

Current value:

RETRIEVAL_MAX_DISTANCE = 0.32

Purpose:

Prevent the system from returning the closest irrelevant chunk when no useful context exists.

Example:

Relevant query:
access control
→ distance around 0.26
→ accepted

Irrelevant query:
vacation policy
→ distance around 0.37
→ filtered out

This threshold is currently a heuristic and should be evaluated with a real labeled retrieval dataset later.

Answer Grounding and Validation

The system includes basic guardrails to reduce hallucinations.

Current validation checks:

Answer includes citations.
Answer uses only allowed source IDs.
Answer avoids known suspicious unsupported phrases.
Unsafe answers are replaced with grounded fallback responses.

Example grounded fallback:

The document mentions access control in relation to internal company policy, permissions, secure document retrieval, and employee access management. [D1]

This is intentionally conservative.

The retrieved chunks remain the source of truth.

Document Status

Documents include status fields.

Supported statuses:

processing
ready
failed

Current synchronous upload flow normally returns:

ready

Future background ingestion will use:

processing → ready
processing → failed
Current Tests

Current test coverage includes:

Chunking tests
Text extraction tests
PDF error handling tests
Answer validator tests
Grounded fallback answer tests
Retrieval distance filter tests
Tenant normalization tests

Run tests:

docker compose -f infra/docker-compose.yml run --rm api pytest tests -v

Latest expected result:

18+ tests passing

The exact number may change as new tests are added.

Current Limitations
No workspace/notebook layer yet.
Retrieval is tenant-filtered but not workspace-filtered.
No real authentication yet.
X-Tenant-ID is a development-time tenant mechanism.
No user model yet.
No workspace-level permissions yet.
No frontend yet.
No migration framework yet.
Database schema is still initialized mainly through init.sql.
No background job system yet.
No page-level PDF citations yet.
No OCR support for scanned PDFs.
Answer validation is still rule-based.
Retrieval threshold is heuristic.
Immediate Next Step

The recommended next major implementation step is the Workspace / Notebook Layer.

Goal:

Tenant
→ Workspace / Notebook
→ Documents
→ Chunks

This step should add:

workspaces table
workspace_id on documents
Workspace CRUD endpoints
Workspace-scoped document upload
Workspace-scoped retrieval
Workspace-scoped answer generation

After that, the system can support domain inference and user-overridable workspace profiles.