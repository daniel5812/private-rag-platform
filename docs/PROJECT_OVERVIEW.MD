# Private RAG Platform — Project Overview

## Project Description

Private RAG Platform is a secure, enterprise-style Retrieval-Augmented Generation system for asking questions over private internal documents.

The goal of the project is to build a local-first RAG platform that can later be deployed inside an AWS private cloud environment. The system is designed for organizations that want to use AI over sensitive internal data while keeping documents, embeddings, retrieval, and generation under their own control.

This project is built as a learning and portfolio project, with emphasis on backend architecture, data flow, infrastructure, security thinking, and production-oriented design.

## Core Idea

The system follows a standard RAG pipeline:

```text
Upload document
→ Store document metadata
→ Extract text
→ Split text into chunks
→ Generate embeddings
→ Store vectors in PostgreSQL with pgvector
→ Retrieve relevant chunks for a user query
→ Generate a grounded answer using a local LLM
→ Return answer with source citations

The LLM is not treated as the source of truth.
The database and retrieved document chunks are the source of truth.

Main Goals
Allow users to upload private documents.
Store document metadata in PostgreSQL.
Store document chunks and embeddings using pgvector.
Use local/private embeddings through Ollama.
Use a local/private LLM through Ollama.
Generate answers grounded in retrieved document context.
Return citations for every answer.
Prevent cross-tenant data leakage.
Build toward a future AWS private deployment.
Current Technology Stack
Backend
Python
FastAPI
Pydantic
asyncpg
httpx
Database
PostgreSQL
pgvector extension
AI / ML Runtime
Ollama
nomic-embed-text for embeddings
llama3.2:1b for local answer generation
Infrastructure
Docker
Docker Compose
Ubuntu VM
VMware local development environment
Future Cloud Target
AWS VPC
Private subnets
FastAPI service on EC2 / ECS
RDS PostgreSQL with pgvector
S3 for private document storage
Secrets Manager
CloudWatch
Optional Bedrock / private model serving
Design Principles
1. Data First, LLM Second

The system should retrieve relevant data before asking the LLM to answer.

The LLM should only reason over retrieved context and should not invent facts.

2. Local-First Development

The MVP is built locally first using Docker Compose. This makes development easier and prepares the architecture for future AWS deployment.

3. Private by Design

Documents, embeddings, and generated answers should remain inside the controlled environment.

4. Tenant-Aware Architecture

Every document and chunk is stored with a tenant_id.

Current MVP uses a hardcoded tenant:

demo

Future versions should derive tenant identity from authentication.

5. Grounded Answers

Every generated answer should be based on retrieved chunks and include source citations like:

[D1], [D2]
6. Guardrails Beyond Prompting

Prompting alone is not enough to prevent hallucinations. The system includes basic validation logic to detect unsupported or suspicious generated answers and replace them with safer grounded fallback responses.