from fastapi import APIRouter

from app.rag.retrieval import retrieve_relevant_chunks
from app.rag.schemas import RetrieveRequest, RetrieveResponse

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