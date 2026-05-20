from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: str
    tenant_id: str
    filename: str
    content_type: str | None
    storage_path: str
    status: str
    error_message: str | None = None


class DocumentSummary(BaseModel):
    id: str
    tenant_id: str
    filename: str
    content_type: str | None
    storage_path: str
    status: str
    error_message: str | None = None
    created_at: str
    chunk_count: int
    chunks_with_embedding: int


class DocumentDetail(BaseModel):
    id: str
    tenant_id: str
    filename: str
    content_type: str | None
    storage_path: str
    status: str
    error_message: str | None = None
    created_at: str


class DocumentChunkResponse(BaseModel):
    id: str
    document_id: str
    tenant_id: str
    chunk_index: int
    content: str
    has_embedding: bool
    created_at: str