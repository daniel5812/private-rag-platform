# Roadmap

## Phase 1 — Local Backend Foundation

Status: Completed

Implemented:

- FastAPI backend
- Health endpoint
- Dockerfile
- Docker Compose
- PostgreSQL service
- pgvector extension
- Database connection layer
- Environment-based settings

## Phase 2 — Document Ingestion

Status: Completed for `.txt` files

Implemented:

- `POST /documents/upload`
- File upload handling
- Local file storage
- Document metadata storage
- Basic tenant field
- Text extraction for `.txt`
- Chunking
- Chunk storage in PostgreSQL

Next improvements:

- File size validation
- Supported file type validation
- Better filename sanitization
- Transaction handling for file + DB consistency
- PDF support

## Phase 3 — Embeddings and Vector Storage

Status: Completed

Implemented:

- Ollama service in Docker Compose
- `nomic-embed-text` model
- Embedding generation for chunks
- Embedding storage in pgvector
- Query embedding generation

Next improvements:

- Batch embeddings
- Retry logic for Ollama failures
- Embedding dimension validation
- Background ingestion jobs

## Phase 4 — Semantic Retrieval

Status: Completed

Implemented:

- `POST /rag/retrieve`
- Query embedding
- pgvector similarity search
- Tenant-aware retrieval
- Top-k retrieval
- Distance score return

Next improvements:

- Similarity threshold
- Hybrid keyword + vector retrieval
- Metadata filters
- Better ranking
- Index optimization for pgvector

## Phase 5 — RAG Answer Generation

Status: Completed as basic MVP

Implemented:

- `POST /rag/ask`
- Prompt builder
- Local LLM generation with Ollama
- Source citations
- Source chunks returned in response
- Basic hallucination guardrail
- Grounded fallback answer

Next improvements:

- More robust answer validation
- Sentence-level citation checking
- Better prompt structure
- Streaming responses
- Better model selection
- Confidence / groundedness metadata

## Phase 6 — Document Management API

Status: Next Recommended Step

Planned endpoints:

```http
GET /documents
GET /documents/{document_id}
GET /documents/{document_id}/chunks
```

Purpose:

Inspect uploaded documents
Check chunks
Check embeddings
Debug ingestion
Prepare for frontend integration
Phase 7 — Authentication and Tenant Isolation

Status: Planned

Planned:

User authentication
Tenant identity from auth token
Remove hardcoded demo
Ensure users can only access their own tenant data
Add tests for tenant isolation
Phase 8 — PDF Support

Status: Planned

Planned:

PDF upload support
Text extraction from PDF
Error handling for scanned/image-based PDFs
Metadata extraction
Source page references
Phase 9 — Frontend

Status: Planned

Planned:

React + TypeScript frontend
Document upload screen
Document list screen
Chat/query screen
Source citation display
Basic admin/debug views
Phase 10 — Testing

Status: Planned

Planned tests:

Health check tests
DB connection tests
Document upload tests
Chunking tests
Embedding mock tests
Retrieval tests
Tenant isolation tests
Answer validation tests
Phase 11 — AWS Deployment

Status: Planned

Target AWS architecture:

VPC
Public subnet for load balancer
Private subnet for backend
RDS PostgreSQL with pgvector
S3 for private document storage
Secrets Manager
CloudWatch logs
Optional EC2 GPU / Bedrock / private model endpoint