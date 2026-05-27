BEGIN;

CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_workspaces_tenant_name UNIQUE (tenant_id, name)
);

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS workspace_id UUID REFERENCES workspaces(id) ON DELETE RESTRICT;

ALTER TABLE document_chunks
    ADD COLUMN IF NOT EXISTS workspace_id UUID REFERENCES workspaces(id) ON DELETE RESTRICT;

CREATE INDEX IF NOT EXISTS idx_documents_workspace_id
    ON documents (workspace_id);

CREATE INDEX IF NOT EXISTS idx_document_chunks_workspace_id
    ON document_chunks (workspace_id);

CREATE INDEX IF NOT EXISTS idx_chunks_tenant_workspace
    ON document_chunks (tenant_id, workspace_id);

COMMIT;