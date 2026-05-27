# Roadmap

## Product Direction

Private RAG Platform is a general-purpose, tenant-aware, workspace-based RAG platform.

The project is not limited to a single domain such as finance. Instead, it is designed as a private AI knowledge system where users can create workspaces/notebooks, upload documents, and ask grounded questions over that specific context.

Finance, HR, legal, engineering, academic research, and internal company policies should be treated as optional workspace profiles, not separate hardcoded products.

## Target Architecture

```text
Tenant
→ Workspace / Notebook
→ Documents
→ Chunks
→ Embeddings
→ Retrieval
→ Workspace-aware prompt
→ Grounded answer with citations
Core Design Principles
Keep the core RAG engine domain-agnostic.
Use tenants for organization-level data isolation.
Use workspaces/notebooks for user-facing knowledge contexts.
Use domain profiles to customize behavior without forking the architecture.
Keep retrieved chunks as the source of truth.
Use the LLM only to synthesize retrieved context.
Prefer explicit citations and grounded answers over fluent but unsupported answers.
Keep local-first development compatible with future AWS private deployment.
Phase 1 — Local Backend Foundation

Status: Completed

Implemented
FastAPI backend
Health endpoint
Dockerfile
Docker Compose setup
PostgreSQL service
pgvector extension
Database connection layer
Environment-based settings
Purpose

This phase established the basic local backend environment and made the system runnable through Docker Compose.

Phase 2 — Document Ingestion

Status: Completed for .txt and .pdf MVP

Implemented
POST /documents/upload
File upload handling
Local file storage
Document metadata storage
Tenant-aware document records
Text extraction for .txt files
Text extraction for .pdf files via pypdf
Empty PDF detection with clean error handling
Failed upload cleanup
Chunking with configurable overlap
Chunk storage in PostgreSQL
Per-chunk embedding generation
Current Limitations
No OCR for scanned PDFs.
No page-level citations yet.
No file size validation yet.
No background processing yet.
Future Improvements
File size validation
Better filename sanitization
Transaction handling for file + DB consistency
OCR support for scanned PDFs
Page-level PDF citations
Background ingestion jobs

Phase 3 — Embeddings and Vector Storage

Status: Completed

Implemented
Ollama service in Docker Compose
nomic-embed-text embedding model
Embedding generation for document chunks
Embedding storage in PostgreSQL using pgvector
Query embedding generation
Purpose

This phase enabled semantic search by converting both documents and user queries into vectors.

Future Improvements
Batch embedding generation
Retry logic for Ollama failures
Embedding dimension validation
Embedding metadata
Background embedding jobs

Phase 4 — Semantic Retrieval

Status: Completed with distance filtering

Implemented
POST /rag/retrieve
Query embedding
pgvector cosine distance similarity search
Tenant-aware retrieval
Top-k retrieval
Distance score returned for each chunk
Distance-based filtering with RETRIEVAL_MAX_DISTANCE
Current Behavior

Chunks with distance above the configured threshold are filtered out before reaching the answer generation stage.

Current tuned threshold:

RETRIEVAL_MAX_DISTANCE = 0.32
Purpose

The distance threshold prevents the system from returning the “closest bad chunk” when the uploaded documents do not actually contain relevant context.

Future Improvements
Evaluate threshold on a labeled retrieval dataset.
Add hybrid keyword + vector retrieval.
Add metadata filters.
Add workspace-level retrieval filtering.
Add pgvector index optimization.
Add retrieval evaluation metrics.

Phase 5 — RAG Answer Generation

Status: Completed as basic MVP

Implemented
POST /rag/ask
Prompt builder
Local LLM generation through Ollama
Source citations such as [D1]
Returned source chunks in API response
Basic hallucination guardrail
Grounded fallback answer generation
Purpose

This phase connected retrieval to answer generation and made the system capable of answering questions over private uploaded documents.

Future Improvements
Sentence-level citation validation
More robust groundedness checks
Better prompt profiles
Streaming responses
Better model selection
Confidence / groundedness metadata

Phase 6 — Document Management API

Status: Completed

Implemented Endpoints
GET /documents
GET /documents/{document_id}
GET /documents/{document_id}/chunks
Purpose

The document management endpoints make it possible to inspect uploaded documents, chunks, and embedding status without manually querying PostgreSQL.

Future Improvements
Filter documents by workspace.
Filter documents by status.
Add delete document endpoint.
Add reprocess document endpoint.
Add document metadata editing.
Phase 7 — Document Status Tracking

Status: Completed / Current

Implemented
Document lifecycle fields:
status
error_message
Supported statuses:
processing
ready
failed
Upload response includes document status.
Document listing includes document status.
Failed uploads return clear errors.
Invalid uploads do not leave misleading ready documents.
Purpose

Document status tracking prepares the ingestion pipeline for future background jobs and makes ingestion state visible through the API.

Future Improvements
Persist failed document records intentionally with status = failed.
Add retry support.
Add ingestion audit trail.
Add background worker.
Add progress reporting.

Phase 8 — Tenant Context Groundwork

Status: Completed / Current

Implemented
Tenant context extracted from request headers.
Transitional header:
X-Tenant-ID: demo
Central tenant dependency.
RAG and document endpoints use tenant context.
Retrieval is filtered by tenant.
Basic tenant isolation behavior verified manually.
Purpose

Before this phase, tenant_id existed in the database but the API mostly used a hardcoded demo tenant. This phase moves tenant selection into the request flow.

Important Note

X-Tenant-ID is a development-time mechanism. It is not production authentication.

In production, tenant identity should come from authentication claims, such as JWT or OAuth tokens.

Future Improvements
Replace free-form tenant header with authenticated tenant identity.
Add tenant isolation integration tests.
Add user-to-tenant membership.
Add audit logging.

Phase 9 — Workspace / Notebook Layer

Status: Next Major Architecture Step

Goal

Introduce a workspace/notebook abstraction between tenants and documents.

New structure:

Tenant
→ Workspace / Notebook
→ Documents
→ Chunks
Why This Matters

Currently, retrieval happens across all documents for a tenant. That works for the MVP, but it can mix unrelated documents.

Workspaces solve this by grouping documents into a specific user context.

Examples:

“Q1 Finance Reports”
“HR Policies”
“Legal Contracts”
“Engineering Docs”
“Research Papers”
Planned Database Changes

Add a new table:

workspaces

Possible fields:

id
tenant_id
name
description
detected_domain
user_selected_domain
answer_style
strictness_level
profile_confidence
created_at
updated_at

Update documents:

Add workspace_id
Ensure documents belong to a workspace.
Retrieval should filter by both tenant_id and workspace_id.
Planned API Endpoints
POST /workspaces
GET /workspaces
GET /workspaces/{workspace_id}
PATCH /workspaces/{workspace_id}
DELETE /workspaces/{workspace_id}
POST /workspaces/{workspace_id}/documents/upload
GET /workspaces/{workspace_id}/documents
POST /workspaces/{workspace_id}/rag/ask
POST /workspaces/{workspace_id}/rag/retrieve
Compatibility Decision

Existing document endpoints can remain temporarily as MVP/debug endpoints, but the long-term product API should become workspace-based.

Future Benefits
Better document organization
Better retrieval precision
Cleaner frontend UX
Workspace-specific prompts
Workspace-specific permissions
Domain-aware behavior
Notebook-like user experience

Phase 10 — Workspace Profile / Domain Inference

Status: Planned

Goal

Allow the system to infer the workspace context from uploaded documents and user intent, while allowing the user to override the result.

Hybrid Profile Model
Auto-detected profile + user override
Inputs for Inference
Workspace name
Workspace description
Uploaded filenames
Extracted document text
User questions
User-provided instructions
Example Domains
finance
hr
legal
engineering
academic
general
Example Flow
User creates workspace: "Q1 Reports"
→ Uploads financial PDFs
→ System detects finance/reporting context
→ Suggested profile: finance analyst style
→ User can accept, edit, or override
Planned Profile Fields
detected_domain
user_selected_domain
answer_style
strictness_level
profile_confidence
profile_source
Design Rule

The domain should influence prompt/profile behavior only.

It should not hardcode finance-specific, legal-specific, or HR-specific logic into the core retrieval architecture.

Phase 11 — Better Ingestion Reliability

Status: Planned

Planned Improvements
Background job queue for long-running uploads
Async ingestion flow
Retry logic for transient Ollama failures
File size validation
Pre-flight file validation
Ingestion audit trail
Better cleanup strategy
Reprocess failed document endpoint
Future Flow
POST upload
→ create document with status = processing
→ background worker extracts text
→ chunks and embeddings are created
→ status becomes ready or failed

Phase 12 — Authentication and Real Tenant Isolation

Status: Planned

Planned Improvements
User authentication
OAuth or JWT support
Tenant derived from token claims
Remove free-form X-Tenant-ID in production
User-to-tenant membership model
Workspace-level permissions
Tenant isolation tests
Audit logging for data access
Target Behavior

Users should not be able to choose arbitrary tenant IDs.

The system should identify the tenant from trusted authentication data.

Phase 13 — Advanced PDF Support

Status: Planned

Planned Improvements
Page-level citations
Scanned PDF detection
OCR support for scanned documents
PDF metadata extraction
PDF form field extraction
Better parsing for tables and structured documents
Citation Goal

Future citations should support references such as:

[D1, page 4]

Phase 14 — Frontend

Status: Planned

Planned Stack
React
TypeScript
Planned Screens
Login screen
Workspace list
Create workspace
Workspace settings
Document upload into workspace
Document list by workspace
Chat/query screen inside workspace
Source citation viewer
Inferred workspace profile display
User override controls for workspace profile
Admin/debug views for chunks and retrieval
Product Direction

The frontend should feel like a private AI notebook system:

Create notebook
→ Upload documents
→ Ask questions inside that notebook
→ View grounded answers and sources

Phase 15 — Testing and Quality

Status: Partially Completed / Planned

Completed
Unit tests for chunking
Unit tests for text extraction
Unit tests for PDF error handling
Unit tests for answer validation
Unit tests for grounded fallback answer generation
Unit tests for retrieval distance filtering
Unit tests for tenant normalization
Planned
Integration tests with PostgreSQL
End-to-end tests for the full RAG pipeline
Tenant isolation tests
Workspace isolation tests
Retrieval threshold evaluation dataset
Domain inference tests
API route tests
Performance benchmarks
Load testing

Phase 16 — AWS Deployment

Status: Planned

Target AWS Architecture
VPC with public and private subnets
Private backend service on EC2 or ECS
RDS PostgreSQL with pgvector
S3 for private document storage
Secrets Manager for credentials
CloudWatch logs and monitoring
Optional Bedrock integration
Optional self-hosted model serving
Private API endpoints where possible
AWS Design Goal

The system should be deployable as a private enterprise knowledge platform where documents, embeddings, and generated answers remain inside the organization’s controlled cloud environment.

Long-Term Vision

The long-term goal is to build a private, secure, workspace-based AI knowledge platform.

Users should be able to:

Create a private workspace/notebook.
Upload internal documents.
Let the system infer the workspace context.
Override or customize the workspace profile.
Ask grounded questions over that workspace.
See source citations for every answer.
Keep all data tenant-isolated and private.