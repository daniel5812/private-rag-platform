# Private RAG Platform

Private RAG Platform is an enterprise-style Retrieval-Augmented Generation system for securely asking questions over internal documents.

The goal of this project is to build a private document question-answering platform that can run locally during development and later be deployed inside an AWS environment. It is designed for organizations that want to use RAG over sensitive internal data without exposing documents to external AI providers.

## Project Goals

- Secure document ingestion
- Tenant-aware document storage and retrieval
- Local/private embeddings
- Local/private LLM inference
- Source-grounded answers with citations
- Clear separation between retrieval, context building, and generation
- Future AWS deployment inside a private cloud environment

## Initial MVP

The first version focuses on a local development setup:

- FastAPI backend
- PostgreSQL with pgvector
- Local document storage
- Ollama for local embeddings and LLM inference
- Basic RAG flow:
  - Upload document
  - Extract text
  - Split into chunks
  - Generate embeddings
  - Store chunks and vectors
  - Ask a question
  - Retrieve relevant chunks
  - Generate an answer with citations

## Future AWS Target

The target architecture will run inside AWS:

- VPC with public and private subnets
- FastAPI service in a private subnet
- RDS PostgreSQL with pgvector
- S3 private bucket for uploaded documents
- Ollama or vLLM on EC2 GPU, or Amazon Bedrock through a private endpoint
- AWS Secrets Manager for credentials
- CloudWatch for logs and metrics
- Security groups and IAM roles for controlled access

## Current Status

The project currently contains a minimal FastAPI backend with a health check endpoint.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cat > README.md <<'EOF'
```

# Private RAG Platform

Private RAG Platform is an enterprise-style Retrieval-Augmented Generation system for securely asking questions over internal documents.

The goal of this project is to build a private document question-answering platform that can run locally during development and later be deployed inside an AWS environment. It is designed for organizations that want to use RAG over sensitive internal data without exposing documents to external AI providers.

## Project Goals

- Secure document ingestion
- Tenant-aware document storage and retrieval
- Local/private embeddings
- Local/private LLM inference
- Source-grounded answers with citations
- Clear separation between retrieval, context building, and generation
- Future AWS deployment inside a private cloud environment

## Initial MVP

The first version focuses on a local development setup:

- FastAPI backend
- PostgreSQL with pgvector
- Local document storage
- Ollama for local embeddings and LLM inference
- Basic RAG flow:
  - Upload document
  - Extract text
  - Split into chunks
  - Generate embeddings
  - Store chunks and vectors
  - Ask a question
  - Retrieve relevant chunks
  - Generate an answer with citations

## Future AWS Target

The target architecture will run inside AWS:

- VPC with public and private subnets
- FastAPI service in a private subnet
- RDS PostgreSQL with pgvector
- S3 private bucket for uploaded documents
- Ollama or vLLM on EC2 GPU, or Amazon Bedrock through a private endpoint
- AWS Secrets Manager for credentials
- CloudWatch for logs and metrics
- Security groups and IAM roles for controlled access

## Current Status

The project currently contains a minimal FastAPI backend with a health check endpoint.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Health check:

GET /health

Expected response:

{
  "status": "ok",
  "service": "private-rag-platform",
  "version": "0.1.0"
}
```

Planned Development Phases
Phase 1 — Local Backend Foundation
FastAPI project structure
PostgreSQL + pgvector using Docker Compose
Basic database schema
Health check and configuration layer

Phase 2 — Document Ingestion
Upload documents
Store original files
Extract text from documents
Split text into chunks
Store document and chunk metadata

Phase 3 — Embeddings and Retrieval
Generate embeddings locally
Store vectors in PostgreSQL with pgvector
Retrieve top-k relevant chunks
Enforce tenant-aware retrieval

Phase 4 — RAG Answer Generation
Build cited context
Generate answers using a local/private LLM
Return answers with source citations
Handle missing context safely

Phase 5 — AWS Deployment
Deploy backend on AWS
Move document storage to S3
Move database to RDS PostgreSQL
Add Secrets Manager, CloudWatch, and private networking
Design Principles
Data first, LLM second
Retrieved content is treated as data, not instructions
Every answer should be grounded in retrieved context
No cross-tenant document access
Missing context should produce an explicit "not enough information" answer
The LLM should not decide what data source to use

docker compose -f infra/docker-compose.yml up --build
docker compose -f infra/docker-compose.yml down