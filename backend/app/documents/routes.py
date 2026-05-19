from fastapi import APIRouter, File, HTTPException, UploadFile

from app.documents.schemas import (
    DocumentChunkResponse,
    DocumentDetail,
    DocumentSummary,
    DocumentUploadResponse,
)
from app.documents.service import (
    get_document,
    get_document_chunks,
    list_documents,
    save_uploaded_document,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    document = await save_uploaded_document(file=file, tenant_id="demo")
    return document


@router.get("", response_model=list[DocumentSummary])
async def documents_list():
    return await list_documents(tenant_id="demo")


@router.get("/{document_id}", response_model=DocumentDetail)
async def document_detail(document_id: str):
    document = await get_document(document_id=document_id, tenant_id="demo")

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
async def document_chunks(document_id: str):
    document = await get_document(document_id=document_id, tenant_id="demo")

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return await get_document_chunks(document_id=document_id, tenant_id="demo")