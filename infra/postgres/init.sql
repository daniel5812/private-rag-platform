CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    content_type TEXT,
    storage_path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'processing',
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(768),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_tenant_id
ON documents (tenant_id);

CREATE INDEX IF NOT EXISTS idx_document_chunks_tenant_id
ON document_chunks (tenant_id);

CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id
ON document_chunks (document_id);