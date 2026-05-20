# Current State

## Project Status

The project currently has a working local MVP of a private RAG pipeline.

The system can:

1. Run a FastAPI backend inside Docker.
2. Run PostgreSQL with pgvector inside Docker.
3. Run Ollama inside Docker.
4. Upload text and PDF documents.
5. Store document metadata in PostgreSQL.
6. Store uploaded files in local Docker storage.
7. Extract text from `.txt` and `.pdf` files.
8. Handle empty or invalid PDFs with clean error responses and cleanup.
9. Split text into chunks with configurable overlap.
10. Generate embeddings using Ollama and `nomic-embed-text`.
11. Store chunk embeddings in PostgreSQL using pgvector.
12. Retrieve semantically relevant chunks with distance-based filtering.
13. Generate grounded answers using a local LLM.
14. Return citations and source chunks.
15. Apply answer validation to reduce hallucinations.
16. List documents, view document details, and inspect chunks without manual DB queries.

## Current API Endpoints

### GET /health

Returns basic service status.

### GET /health/db

Checks that the FastAPI backend can connect to PostgreSQL.

### POST /documents/upload

Uploads a document and stores:

- document metadata
- original file
- extracted text chunks
- embeddings for each chunk

**Supported file types:**

- `.txt`
- `.pdf`

**Error handling:**

- Empty PDF returns HTTP 422 with `{"detail":"The uploaded PDF file is empty"}`
- Invalid PDFs return HTTP 422 with descriptive error messages
- Failed uploads are cleaned up to prevent orphaned metadata

### GET /documents

Returns metadata for all documents (tenant-filtered).

### GET /documents/{document_id}

Returns metadata for a specific document including:

- document id, filename, upload timestamp
- file size
- number of chunks
- embedding status

### GET /documents/{document_id}/chunks

Returns extracted chunks for a document including:

- chunk content
- chunk index
- embedding distance (null if not yet retrieved)

### POST /rag/retrieve

Retrieves the most relevant document chunks based on vector similarity (cosine distance).

**Request example:**

```json
{
  "query": "What does the document say about access control?",
  "tenant_id": "demo",
  "top_k": 3
}
```

**Distance Threshold:** Chunks with distance > 0.32 are filtered out. This prevents the system from returning the "closest bad chunk" when no relevant context exists for a query. This is a tuned heuristic for the current dataset and should be made configurable with evaluation on a test set in future iterations.

### POST /rag/ask

Generates a grounded answer based on retrieved context.

**Request example:**

```json
{
  "query": "What does the document say about access control?",
  "tenant_id": "demo",
  "top_k": 3
}
```

**Returns:**

- grounded answer
- source citations
- retrieved source chunks

**Example answer:**

```
The document mentions access control in relation to internal company policy, 
permissions, secure document retrieval, and employee access management. [D1]
```
## Current Docker Services

The system uses Docker Compose with these services:

**api** — FastAPI backend on port 8000

**db** — PostgreSQL 15 with pgvector extension

**ollama** — Local Ollama runtime for embeddings and generation

## Current Models

**Embedding Model:** `nomic-embed-text`

Used to convert document chunks and user queries into vectors.

**Generation Model:** `llama3.2:1b`

Used to generate local answers from retrieved context.

## Current Database Tables

**documents**

Stores uploaded document metadata.

Important fields:

- `id` — document UUID
- `tenant_id` — tenant identifier
- `filename` — original filename
- `content_type` — MIME type
- `storage_path` — local file path
- `created_at` — upload timestamp

**document_chunks**

Stores extracted chunks and embeddings.

Important fields:

- `id` — chunk UUID
- `document_id` — reference to parent document
- `tenant_id` — tenant identifier
- `chunk_index` — position in document
- `content` — text content
- `embedding` — pgvector embedding
- `created_at` — insertion timestamp

## Current Working Flow

```text
User uploads document
→ FastAPI saves file
→ Text is extracted (txt or pdf)
→ Text is split into chunks
→ Each chunk is embedded using Ollama
→ Chunk + vector are stored in document_chunks
→ Metadata is inserted into documents table

User asks a question
→ Query is embedded using Ollama
→ PostgreSQL pgvector retrieves similar chunks
→ Chunks filtered by distance threshold (max 0.32)
→ Prompt is built with retrieved context
→ Ollama LLM generates answer
→ Answer validator checks citations and detects hallucinations
→ API returns grounded answer and sources
```
Current Limitations

- Tenant ID is hardcoded as `demo`; no user authentication.
- Answer validation is rule-based (not ML-based).
- Retrieval threshold (0.32) is a heuristic, not learned from evaluation data.
- No frontend yet.
- No migration system; database schema is initialized via `init.sql`.
- No background job system for long-running ingestions.
- No document status tracking (processing / ready / failed).
- Page-level PDF citations not yet supported (chapter-level only).

## Test Status

Current tests pass successfully:
- **15 tests passing**
- Unit tests for chunking
- Unit tests for PDF and text extraction
- Unit tests for answer validation
- Unit tests for grounded fallback answer generation
- Unit tests for retrieval distance filtering

To run tests locally:

```bash
docker compose -f infra/docker-compose.yml run --rm api pytest tests -v
```

## Immediate Next Step

The recommended next step is to improve ingestion reliability and status tracking:

- Add document status tracking (processing, ready, failed)
- Better error recovery and cleanup
- Background job queue for long-running uploads
- Document ingestion audit trail