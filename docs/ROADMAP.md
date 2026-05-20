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

Status: Completed for `.txt` and `.pdf` files

Implemented:

- `POST /documents/upload`
- File upload handling
- Local file storage
- Document metadata storage
- Tenant-aware field
- Text extraction for `.txt` files
- Text extraction for `.pdf` files via `pypdf`
- Empty PDF detection with clean error handling
- Failed ingestion cleanup (orphaned documents not left in DB)
- Chunking with configurable overlap
- Chunk storage in PostgreSQL
- Per-chunk embedding generation

Next improvements:

- File size validation
- Better filename sanitization
- Transaction handling for file + DB consistency
- OCR for scanned PDFs (future phase)
- Page-level PDF citations

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

Status: Completed with distance filtering

Implemented:

- `POST /rag/retrieve`
- Query embedding
- pgvector cosine distance similarity search
- Tenant-aware retrieval
- Top-k retrieval
- Distance score return for each chunk
- Distance-based filtering (max distance: 0.32) to prevent retrieval of irrelevant chunks

Next improvements:

- Make distance threshold configurable
- Evaluate threshold on a real test dataset
- Hybrid keyword + vector retrieval
- Metadata filters
- Better ranking algorithms
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

Status: Completed

Implemented endpoints:

- `GET /documents` — list all documents (tenant-filtered)
- `GET /documents/{document_id}` — get document metadata
- `GET /documents/{document_id}/chunks` — list chunks for a document

Purpose:

- Inspect uploaded documents without manual DB queries
- View chunk details and extraction status
- Verify embeddings are present
- Debug the ingestion pipeline
- Prepare for frontend integration

## Phase 7 — Better Ingestion Reliability

Status: In Progress / Next Recommended Step

Planned improvements:

- Document status tracking: `processing` → `ready` / `failed`
- Atomic ingestion: metadata only inserted after extraction succeeds
- Better error handling and user feedback for unsupported files
- Ingestion audit trail / logs
- Background job queue for long-running uploads
- File size validation and pre-flight checks
- Retry logic for transient Ollama failures

## Phase 8 — Authentication and Tenant Isolation

Status: Planned

Planned:

- User authentication (OAuth / JWT)
- Derive tenant identity from auth token
- Remove hardcoded `demo` tenant
- Ensure users can only access their own tenant data
- Add tests for tenant isolation
- Audit logging for data access

## Phase 9 — Advanced PDF Support

Status: Planned

Planned:

- Page-level citations in retrieval results
- Scanned PDF detection and user warning
- OCR support (future, not MVP)
- Metadata extraction (author, title, creation date)
- PDF form field handling

## Phase 10 — Frontend

Status: Planned

Planned:

- React + TypeScript frontend
- Document upload screen
- Document list screen
- Chat/query screen with source citations
- Admin/debug views for chunk inspection
- Real-time upload progress

## Phase 11 — Testing & Quality

Status: Partially completed

Completed:

- Unit tests for chunking, PDF extraction, answer validation (15 tests passing)

Planned:

- Integration tests with real PostgreSQL
- Retrieval threshold evaluation on test dataset
- End-to-end tests for full RAG pipeline
- Performance benchmarks
- Load testing

## Phase 12 — AWS Deployment

Status: Planned

Target AWS architecture:

- VPC with public and private subnets
- EC2 or ECS for FastAPI backend
- RDS PostgreSQL with pgvector extension
- S3 for private document storage
- Secrets Manager for credentials
- CloudWatch for logs and monitoring
- Optional: Bedrock or self-hosted model endpoints for GPU-accelerated embeddings/generation
- Private API endpoints (no public access)