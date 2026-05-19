from fastapi import APIRouter, File, UploadFile

from app.documents.schemas import DocumentUploadResponse
from app.documents.service import save_uploaded_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    document = await save_uploaded_document(file=file, tenant_id="demo")
    return document