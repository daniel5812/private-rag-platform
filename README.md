Private RAG platform is a private document question-answering platform
designed for organizations that need to query internal documents without
exposing sensitive data to external AI providers.

Backend: FastAPI
Frontend: React + TypeScript + Vite
Database: PostgreSQL
Vector Search: PostgreSQL + pgvector
LLM local: Ollama
Embeddings local: Ollama / nomic-embed-text
Documents: local filesystem בהתחלה, S3 בהמשך
Deployment local: Docker Compose
Deployment cloud: AWS EC2 בהתחלה

Architecture:
User -> React Frontend -> FastAPI Backend -> Auth / tenant_id -> Document Upload Service -> Text Extractor
-> Chunker -> Embedding Service -> PostgreSQL + pgvector -> Retriever -> Prompt Builder -> Ollama LLM
-> Answer with citations

secure-enterprise-rag/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   │
│   │   ├── documents/
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   ├── extractor.py
│   │   │   └── chunker.py
│   │   │
│   │   ├── embeddings/
│   │   │   ├── provider.py
│   │   │   └── ollama.py
│   │   │
│   │   ├── rag/
│   │   │   ├── routes.py
│   │   │   ├── retriever.py
│   │   │   ├── prompt_builder.py
│   │   │   └── service.py
│   │   │
│   │   ├── llm/
│   │   │   ├── provider.py
│   │   │   └── ollama.py
│   │   │
│   │   └── schemas/
│   │       ├── documents.py
│   │       └── rag.py
│   │
│   ├── migrations/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   └── later
│
├── infra/
│   ├── docker-compose.yml
│   └── aws/
│       └── later
│
├── docs/
│   ├── architecture.md
│   ├── aws-target-architecture.md
│   └── threat-model.md
│
├── .env.example
└── README.md


AWS VPC
├── Public Subnet
│   └── ALB / NGINX
│
├── Private Subnet
│   ├── FastAPI
│   ├── Ollama / vLLM
│   ├── RDS PostgreSQL + pgvector
│   └── Redis / optional
│
├── S3 private bucket
├── Secrets Manager
├── CloudWatch
└── NAT Gateway / VPC Endpoints
