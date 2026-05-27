from app.core.config import settings
from app.core.database import database
from app.embeddings.ollama_client import generate_embedding


def _embedding_to_pgvector_text(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


def filter_chunks_by_distance(
    chunks: list[dict],
    max_distance: float,
) -> list[dict]:
    return [
        chunk
        for chunk in chunks
        if chunk["distance"] is not None and chunk["distance"] <= max_distance
    ]


async def retrieve_relevant_chunks(
    query: str,
    tenant_id: str = "demo",
    top_k: int = 5,
    workspace_id: str | None = None,
) -> list[dict]:
    query_embedding = await generate_embedding(query)
    query_vector = _embedding_to_pgvector_text(query_embedding)
    if workspace_id is not None:
        rows = await database.fetch(
            """
            SELECT
                document_id::text AS document_id,
                id::text AS chunk_id,
                chunk_index,
                content,
                embedding <=> $1::vector AS distance
            FROM document_chunks
            WHERE tenant_id = $2
                AND workspace_id = $3::uuid
                AND embedding IS NOT NULL
            ORDER BY embedding <=> $1::vector
            LIMIT $4;
            """,
            query_vector,
            tenant_id,
            workspace_id,
            top_k,
        )
    else:
        rows = await database.fetch(
            """
            SELECT
                document_id::text AS document_id,
                id::text AS chunk_id,
                chunk_index,
                content,
                embedding <=> $1::vector AS distance
            FROM document_chunks
            WHERE tenant_id = $2
              AND embedding IS NOT NULL
            ORDER BY embedding <=> $1::vector
            LIMIT $3;
            """,
            query_vector,
            tenant_id,
            top_k,
        )

    chunks = [dict(row) for row in rows]

    return filter_chunks_by_distance(
        chunks=chunks,
        max_distance=settings.retrieval_max_distance,
    )