# Current State

## Project Status

The project currently has a working local MVP of a private RAG pipeline.

The system can:

1. Run a FastAPI backend inside Docker.
2. Run PostgreSQL with pgvector inside Docker.
3. Run Ollama inside Docker.
4. Upload a text document.
5. Store document metadata in PostgreSQL.
6. Store uploaded files in local Docker storage.
7. Extract text from `.txt` files.
8. Split text into chunks.
9. Generate embeddings using Ollama and `nomic-embed-text`.
10. Store chunk embeddings in PostgreSQL using pgvector.
11. Retrieve semantically relevant chunks for a query.
12. Generate an answer using a local LLM.
13. Return citations and source chunks.
14. Apply basic answer validation to reduce hallucinations.

## Current API Endpoints

### Health Check

```http
GET /health

Returns basic service status.

Database Health Check
GET /health/db

Checks that the FastAPI backend can connect to PostgreSQL.

Upload Document
POST /documents/upload

Uploads a document and stores:

document metadata
original file
extracted text chunks
embeddings for each chunk

Current supported file type:

.txt
Semantic Retrieval
POST /rag/retrieve

Request example:

{
  "query": "What does the document say about access control?",
  "tenant_id": "demo",
  "top_k": 3
}

Returns the most relevant document chunks based on vector similarity.

RAG Answer Generation
POST /rag/ask

Request example:

{
  "query": "What does the document say about access control?",
  "tenant_id": "demo",
  "top_k": 3
}
```

Returns:

grounded answer
source citations
retrieved source chunks

Example answer:

The document mentions access control in relation to internal company policy, permissions, secure document retrieval, and employee access management. [D1]
Current Docker Services

The system currently uses Docker Compose with these services:

api

FastAPI backend.

db

PostgreSQL with pgvector.

ollama

Local Ollama runtime for embeddings and generation.

Current Models
Embedding Model
nomic-embed-text

Used to convert document chunks and user queries into vectors.

Generation Model
llama3.2:1b

Used to generate local answers from retrieved context.

Current Database Tables
documents

Stores uploaded document metadata.

Important fields:

id
tenant_id
filename
content_type
storage_path
created_at
document_chunks

Stores extracted chunks and embeddings.

Important fields:

id
document_id
tenant_id
chunk_index
content
embedding
created_at
Current Working Flow
User uploads document
→ FastAPI saves file
→ Metadata is inserted into documents table
→ Text is extracted
→ Text is split into chunks
→ Each chunk is embedded using Ollama
→ Chunk + vector are stored in document_chunks
→ User asks a question
→ Query is embedded using Ollama
→ PostgreSQL pgvector retrieves similar chunks
→ Prompt is built with retrieved context
→ Ollama LLM generates answer
→ Answer validator checks citations and suspicious hallucinations
→ API returns grounded answer and sources
Current Limitations
Only .txt documents are supported.
Tenant ID is hardcoded as demo.
No authentication yet.
No frontend yet.
No PDF parsing yet.
No AWS deployment yet.
Answer validation is basic and rule-based.
No automated tests yet for ingestion, retrieval, or answer validation.
No document listing endpoints yet.
No migration system yet; database schema is initialized through init.sql.
Immediate Next Step

The recommended next step is to add document management endpoints:

GET /documents
GET /documents/{document_id}
GET /documents/{document_id}/chunks

This will make it easier to inspect uploaded documents, chunks, embeddings, and tenant data through the API instead of manually querying PostgreSQL.