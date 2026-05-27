from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.tenant import get_tenant_id
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