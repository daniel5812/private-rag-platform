from uuid import UUID, uuid4

import asyncpg
from fastapi import HTTPException

from app.core.database import database


def _validate_uuid(value: str, field_name: str = "id") -> str:
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name}",
        ) from exc


async def create_workspace(
    *,
    tenant_id: str,
    name: str,
    description: str | None = None,
) -> dict:
    workspace_id = uuid4()

    try:
        row = await database.fetchrow(
            """
            INSERT INTO workspaces (
                id,
                tenant_id,
                name,
                description
            )
            VALUES ($1, $2, $3, $4)
            RETURNING
                id::text AS id,
                tenant_id,
                name,
                description,
                created_at::text AS created_at,
                updated_at::text AS updated_at;
            """,
            workspace_id,
            tenant_id,
            name,
            description,
        )
    except asyncpg.UniqueViolationError as exc:
        raise HTTPException(
            status_code=409,
            detail="A workspace with this name already exists for this tenant",
        ) from exc

    return dict(row)


async def list_workspaces(*, tenant_id: str) -> list[dict]:
    rows = await database.fetch(
        """
        SELECT
            id::text AS id,
            tenant_id,
            name,
            description,
            created_at::text AS created_at,
            updated_at::text AS updated_at
        FROM workspaces
        WHERE tenant_id = $1
        ORDER BY created_at DESC;
        """,
        tenant_id,
    )

    return [dict(row) for row in rows]


async def get_workspace(
    *,
    workspace_id: str,
    tenant_id: str,
) -> dict | None:
    validated_workspace_id = _validate_uuid(workspace_id, "workspace_id")

    row = await database.fetchrow(
        """
        SELECT
            id::text AS id,
            tenant_id,
            name,
            description,
            created_at::text AS created_at,
            updated_at::text AS updated_at
        FROM workspaces
        WHERE id = $1::uuid
          AND tenant_id = $2;
        """,
        validated_workspace_id,
        tenant_id,
    )

    if row is None:
        return None

    return dict(row)


async def require_workspace(
    *,
    workspace_id: str,
    tenant_id: str,
) -> dict:
    workspace = await get_workspace(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
    )

    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


async def update_workspace(
    *,
    workspace_id: str,
    tenant_id: str,
    name: str | None = None,
    description: str | None = None,
) -> dict | None:
    validated_workspace_id = _validate_uuid(workspace_id, "workspace_id")

    try:
        row = await database.fetchrow(
            """
            UPDATE workspaces
            SET
                name = COALESCE($3, name),
                description = COALESCE($4, description),
                updated_at = NOW()
            WHERE id = $1::uuid
              AND tenant_id = $2
            RETURNING
                id::text AS id,
                tenant_id,
                name,
                description,
                created_at::text AS created_at,
                updated_at::text AS updated_at;
            """,
            validated_workspace_id,
            tenant_id,
            name,
            description,
        )
    except asyncpg.UniqueViolationError as exc:
        raise HTTPException(
            status_code=409,
            detail="A workspace with this name already exists for this tenant",
        ) from exc

    if row is None:
        return None

    return dict(row)


async def delete_workspace(
    *,
    workspace_id: str,
    tenant_id: str,
) -> bool:
    validated_workspace_id = _validate_uuid(workspace_id, "workspace_id")

    workspace = await get_workspace(
        workspace_id=validated_workspace_id,
        tenant_id=tenant_id,
    )

    if workspace is None:
        return False

    document_count = await database.fetchval(
        """
        SELECT COUNT(*)::int
        FROM documents
        WHERE workspace_id = $1::uuid
          AND tenant_id = $2;
        """,
        validated_workspace_id,
        tenant_id,
    )

    if document_count > 0:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete workspace because it contains documents",
        )

    await database.execute(
        """
        DELETE FROM workspaces
        WHERE id = $1::uuid
          AND tenant_id = $2;
        """,
        validated_workspace_id,
        tenant_id,
    )

    return True