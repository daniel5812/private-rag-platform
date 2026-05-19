from app.core.database import database
from app.embeddings.ollama_client import generate_embedding


def _embedding_to_pgvector_text(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


async def retrieve_relevant_chunks(
    query: str,
    tenant_id: str = "demo",
    top_k: int = 5,
) -> list[dict]:
    query_embedding = await generate_embedding(query)
    query_vector = _embedding_to_pgvector_text(query_embedding)

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

    return [dict(row) for row in rows]