from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.tenant import get_tenant_id
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
from app.documents.text_extractor import (
    EmptyExtractedTextError,
    InvalidDocumentError,
    UnsupportedFileTypeError,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        return await save_uploaded_document(
            file=file,
            tenant_id=tenant_id,
            workspace_id=None,
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except EmptyExtractedTextError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=list[DocumentSummary])
async def documents_list(
    tenant_id: str = Depends(get_tenant_id),
):
    return await list_documents(
        tenant_id=tenant_id,
        workspace_id=None,
    )


@router.get("/{document_id}", response_model=DocumentDetail)
async def document_detail(
    document_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    document = await get_document(
        document_id=document_id,
        tenant_id=tenant_id,
        workspace_id=None,
    )

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
async def document_chunks(
    document_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    document = await get_document(
        document_id=document_id,
        tenant_id=tenant_id,
        workspace_id=None,
    )

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return await get_document_chunks(
        document_id=document_id,
        tenant_id=tenant_id,
        workspace_id=None,
    )