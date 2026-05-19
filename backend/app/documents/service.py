from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.core.database import database
from app.documents.chunker import chunk_text
from app.documents.text_extractor import extract_text_from_file


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

    text = extract_text_from_file(
        storage_path=str(storage_path),
        content_type=file.content_type,
    )

    chunks = chunk_text(text)

    for index, chunk in enumerate(chunks):
        await database.execute(
            """
            INSERT INTO document_chunks (
                id,
                document_id,
                tenant_id,
                chunk_index,
                content
            )
            VALUES ($1, $2, $3, $4, $5);
            """,
            uuid4(),
            document_id,
            tenant_id,
            index,
            chunk,
        )

    document = dict(row)
    document["id"] = str(document["id"])
    return document