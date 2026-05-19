from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.core.database import database


async def save_uploaded_document(
    file: UploadFile,
    tenant_id: str = "demo",
) -> dict:
    document_id = uuid4()

    original_filename = file.filename or "uploaded_file"
    safe_filename = original_filename.replace("/", "_").replace("\\", "_")

    tenant_storage_dir = Path(settings.storage_dir) / tenant_id
    tenant_storage_dir.mkdir(parents=True, exist_ok=True)

    storage_path = tenant_storage_dir / f"{document_id}_{safe_filename}"

    content = await file.read()
    storage_path.write_bytes(content)

    row = await database.fetchrow(
        """
        INSERT INTO documents (
            id,
            tenant_id,
            filename,
            content_type,
            storage_path
        )
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, tenant_id, filename, content_type, storage_path;
        """,
        document_id,
        tenant_id,
        original_filename,
        file.content_type,
        str(storage_path),
    )

    document = dict(row)
    document["id"] = str(document["id"])
    return document