from fastapi import APIRouter, Depends

from app.core.tenant import get_tenant_id
from app.rag.schemas import AskRequest, AskResponse, RetrieveRequest, RetrieveResponse
from app.rag.service import answer_question, retrieve_context

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(
    request: RetrieveRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    results = await retrieve_context(
        query=request.query,
        tenant_id=tenant_id,
        top_k=request.top_k,
        workspace_id=None,
    )

    return {
        "query": request.query,
        "tenant_id": tenant_id,
        "results": results,
    }


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    return await answer_question(
        query=request.query,
        tenant_id=tenant_id,
        top_k=request.top_k,
        workspace_id=None,
    )