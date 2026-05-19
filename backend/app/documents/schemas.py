from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: str
    tenant_id: str
    filename: str
    content_type: str | None
    storage_path: str