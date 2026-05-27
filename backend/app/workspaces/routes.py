from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status

from app.core.tenant import get_tenant_id
from app.documents.schemas import DocumentSummary, DocumentUploadResponse
from app.documents.service import list_documents, save_uploaded_document
from app.documents.text_extractor import (
    EmptyExtractedTextError,
    InvalidDocumentError,
    UnsupportedFileTypeError,
)
from app.rag.schemas import AskRequest, AskResponse, RetrieveRequest, RetrieveResponse
from app.rag.service import answer_question, retrieve_context
from app.workspaces.schemas import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.workspaces.service import (
    create_workspace,
    delete_workspace,
    get_workspace,
    list_workspaces,
    require_workspace,
    update_workspace,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace_route(
    request: WorkspaceCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    return await create_workspace(
        tenant_id=tenant_id,
        name=request.name,
        description=request.description,
    )


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces_route(
    tenant_id: str = Depends(get_tenant_id),
):
    return await list_workspaces(tenant_id=tenant_id)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace_route(
    workspace_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    workspace = await get_workspace(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
    )

    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace_route(
    workspace_id: str,
    request: WorkspaceUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    workspace = await update_workspace(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
        name=request.name,
        description=request.description,
    )

    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace_route(
    workspace_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    deleted = await delete_workspace(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{workspace_id}/documents/upload",
    response_model=DocumentUploadResponse,
)
async def upload_document_to_workspace_route(
    workspace_id: str,
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_tenant_id),
):
    await require_workspace(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
    )

    try:
        return await save_uploaded_document(
            file=file,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except EmptyExtractedTextError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get(
    "/{workspace_id}/documents",
    response_model=list[DocumentSummary],
)
async def list_workspace_documents_route(
    workspace_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    await require_workspace(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
    )

    return await list_documents(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
    )


@router.post(
    "/{workspace_id}/rag/retrieve",
    response_model=RetrieveResponse,
)
async def retrieve_from_workspace_route(
    workspace_id: str,
    request: RetrieveRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    await require_workspace(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
    )

    results = await retrieve_context(
        query=request.query,
        tenant_id=tenant_id,
        top_k=request.top_k,
        workspace_id=workspace_id,
    )

    return {
        "query": request.query,
        "tenant_id": tenant_id,
        "results": results,
    }


@router.post(
    "/{workspace_id}/rag/ask",
    response_model=AskResponse,
)
async def ask_workspace_route(
    workspace_id: str,
    request: AskRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    await require_workspace(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
    )

    return await answer_question(
        query=request.query,
        tenant_id=tenant_id,
        top_k=request.top_k,
        workspace_id=workspace_id,
    )