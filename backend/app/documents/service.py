from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.core.database import database
from app.documents.chunker import chunk_text
from app.documents.text_extractor import extract_text_from_file
from app.embeddings.ollama_client import generate_embedding


def _embedding_to_pgvector_text(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


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
        embedding = await generate_embedding(chunk)
        embedding_as_text = _embedding_to_pgvector_text(embedding)

        await database.execute(
            """
            INSERT INTO document_chunks (
                id,
                document_id,
                tenant_id,
                chunk_index,
                content,
                embedding
            )
            VALUES ($1, $2, $3, $4, $5, $6::vector);
            """,
            uuid4(),
            document_id,
            tenant_id,
            index,
            chunk,
            embedding_as_text,
        )

    document = dict(row)
    document["id"] = str(document["id"])
    return document


async def list_documents(tenant_id: str = "demo") -> list[dict]:
    rows = await database.fetch(
        """
        SELECT
            d.id::text AS id,
            d.tenant_id,
            d.filename,
            d.content_type,
            d.storage_path,
            d.created_at::text AS created_at,
            COUNT(c.id)::int AS chunk_count,
            COUNT(c.embedding)::int AS chunks_with_embedding
        FROM documents d
        LEFT JOIN document_chunks c
            ON c.document_id = d.id
        WHERE d.tenant_id = $1
        GROUP BY
            d.id,
            d.tenant_id,
            d.filename,
            d.content_type,
            d.storage_path,
            d.created_at
        ORDER BY d.created_at DESC;
        """,
        tenant_id,
    )

    return [dict(row) for row in rows]


async def get_document(document_id: str, tenant_id: str = "demo") -> dict | None:
    row = await database.fetchrow(
        """
        SELECT
            id::text AS id,
            tenant_id,
            filename,
            content_type,
            storage_path,
            created_at::text AS created_at
        FROM documents
        WHERE id = $1::uuid
          AND tenant_id = $2;
        """,
        document_id,
        tenant_id,
    )

    if row is None:
        return None

    return dict(row)


async def get_document_chunks(document_id: str, tenant_id: str = "demo") -> list[dict]:
    rows = await database.fetch(
        """
        SELECT
            id::text AS id,
            document_id::text AS document_id,
            tenant_id,
            chunk_index,
            content,
            embedding IS NOT NULL AS has_embedding,
            created_at::text AS created_at
        FROM document_chunks
        WHERE document_id = $1::uuid
          AND tenant_id = $2
        ORDER BY chunk_index ASC;
        """,
        document_id,
        tenant_id,
    )

    return [dict(row) for row in rows]