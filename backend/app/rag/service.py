from app.llm.ollama_client import generate_answer
from app.rag.answer_builder import build_grounded_fallback_answer
from app.rag.answer_validator import (
    answer_has_required_citation,
    answer_uses_only_allowed_sources,
)
from app.rag.prompt_builder import build_rag_prompt
from app.rag.retrieval import retrieve_relevant_chunks


INSUFFICIENT_INFO_ANSWER = "I don't have enough information in the provided documents."


def build_sources(chunks: list[dict]) -> list[dict]:
    sources = []

    for index, chunk in enumerate(chunks, start=1):
        sources.append(
            {
                "id": f"D{index}",
                "document_id": chunk["document_id"],
                "chunk_id": chunk["chunk_id"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"],
                "distance": chunk["distance"],
            }
        )

    return sources


def answer_needs_fallback(answer: str, source_count: int) -> bool:
    allowed_source_ids = {f"[D{index}]" for index in range(1, source_count + 1)}

    suspicious_phrases = [
        "view, edit, or delete",
        "view or modify",
        "regulatory requirements",
        "authorized personnel",
        "compliance",
    ]

    return (
        not answer_has_required_citation(answer)
        or not answer_uses_only_allowed_sources(answer, allowed_source_ids)
        or any(phrase in answer.lower() for phrase in suspicious_phrases)
    )


async def retrieve_context(
    *,
    query: str,
    tenant_id: str,
    top_k: int,
    workspace_id: str | None = None,
) -> list[dict]:
    return await retrieve_relevant_chunks(
        query=query,
        tenant_id=tenant_id,
        top_k=top_k,
        workspace_id=workspace_id,
    )


async def answer_question(
    *,
    query: str,
    tenant_id: str,
    top_k: int,
    workspace_id: str | None = None,
) -> dict:
    chunks = await retrieve_context(
        query=query,
        tenant_id=tenant_id,
        top_k=top_k,
        workspace_id=workspace_id,
    )

    if not chunks:
        return {
            "query": query,
            "tenant_id": tenant_id,
            "answer": INSUFFICIENT_INFO_ANSWER,
            "sources": [],
        }

    prompt = build_rag_prompt(query=query, chunks=chunks)
    answer = await generate_answer(prompt)

    if answer_needs_fallback(answer=answer, source_count=len(chunks)):
        answer = build_grounded_fallback_answer(
            query=query,
            chunks=chunks,
        )

    return {
        "query": query,
        "tenant_id": tenant_id,
        "answer": answer,
        "sources": build_sources(chunks),
    }