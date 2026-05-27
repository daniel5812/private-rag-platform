from pydantic import BaseModel, Field


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    content: str
    distance: float


class RetrieveResponse(BaseModel):
    query: str
    tenant_id: str
    results: list[RetrievedChunk]


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class Source(BaseModel):
    id: str
    document_id: str
    chunk_id: str
    chunk_index: int
    content: str
    distance: float


class AskResponse(BaseModel):
    query: str
    tenant_id: str
    answer: str
    sources: list[Source]