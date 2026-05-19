import httpx

from app.core.config import settings


async def generate_embedding(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/embed",
            json={
                "model": settings.embedding_model,
                "input": text,
            },
        )

    response.raise_for_status()
    data = response.json()

    embeddings = data.get("embeddings")

    if not embeddings or not isinstance(embeddings, list):
        raise RuntimeError("Ollama did not return embeddings")

    return embeddings[0]