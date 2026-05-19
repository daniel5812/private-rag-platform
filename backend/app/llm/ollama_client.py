import httpx

from app.core.config import settings


async def generate_answer(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.generation_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                },
            },
        )

    response.raise_for_status()
    data = response.json()

    answer = data.get("response")
    if not answer:
        raise RuntimeError("Ollama did not return a response")

    return answer.strip()