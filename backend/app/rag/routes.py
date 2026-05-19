from fastapi import APIRouter

from app.rag.answer_builder import build_grounded_fallback_answer
from app.rag.answer_validator import (
    answer_has_required_citation,
    answer_uses_only_allowed_sources,
)
from app.llm.ollama_client import generate_answer
from app.rag.prompt_builder import build_rag_prompt
from app.rag.retrieval import retrieve_relevant_chunks
from app.rag.schemas import AskRequest, AskResponse, RetrieveRequest, RetrieveResponse

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest):
    results = await retrieve_relevant_chunks(
        query=request.query,
        tenant_id=request.tenant_id,
        top_k=request.top_k,
    )

    return {
        "query": request.query,
        "tenant_id": request.tenant_id,
        "results": results,
    }


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    chunks = await retrieve_relevant_chunks(
        query=request.query,
        tenant_id=request.tenant_id,
        top_k=request.top_k,
    )

    if not chunks:
        return {
            "query": request.query,
            "tenant_id": request.tenant_id,
            "answer": "I don't have enough information in the provided documents.",
            "sources": [],
        }

    prompt = build_rag_prompt(query=request.query, chunks=chunks)
    answer = await generate_answer(prompt)

    allowed_source_ids = {f"[D{index}]" for index in range(1, len(chunks) + 1)}

    suspicious_phrases = [
        "view, edit, or delete",
        "view or modify",
        "regulatory requirements",
        "authorized personnel",
        "compliance",
    ]

    if (
        not answer_has_required_citation(answer)
        or not answer_uses_only_allowed_sources(answer, allowed_source_ids)
        or any(phrase in answer.lower() for phrase in suspicious_phrases)
    ):
        answer = build_grounded_fallback_answer(
            query=request.query,
            chunks=chunks,
        )

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

    return {
        "query": request.query,
        "tenant_id": request.tenant_id,
        "answer": answer,
        "sources": sources,
    }