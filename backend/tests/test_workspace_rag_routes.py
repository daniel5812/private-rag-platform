from fastapi.testclient import TestClient

from app.core.tenant import get_tenant_id
from app.main import app
from app.workspaces import routes as workspace_routes


client = TestClient(app)


def override_tenant_demo():
    return "demo"


def override_tenant_other():
    return "other-tenant"


def test_workspace_retrieve_route_passes_workspace_id(monkeypatch):
    captured = {}

    async def fake_require_workspace(*, workspace_id: str, tenant_id: str):
        captured["require_workspace"] = {
            "workspace_id": workspace_id,
            "tenant_id": tenant_id,
        }
        return {
            "id": workspace_id,
            "tenant_id": tenant_id,
            "name": "Test Workspace",
            "description": None,
            "created_at": "now",
            "updated_at": "now",
        }

    async def fake_retrieve_context(
        *,
        query: str,
        tenant_id: str,
        top_k: int,
        workspace_id: str | None = None,
    ):
        captured["retrieve_context"] = {
            "query": query,
            "tenant_id": tenant_id,
            "top_k": top_k,
            "workspace_id": workspace_id,
        }

        return [
            {
                "document_id": "doc-1",
                "chunk_id": "chunk-1",
                "chunk_index": 0,
                "content": "Workspace content",
                "distance": 0.11,
            }
        ]

    monkeypatch.setattr(workspace_routes, "require_workspace", fake_require_workspace)
    monkeypatch.setattr(workspace_routes, "retrieve_context", fake_retrieve_context)

    app.dependency_overrides[get_tenant_id] = override_tenant_demo

    try:
        response = client.post(
            "/workspaces/11111111-1111-1111-1111-111111111111/rag/retrieve",
            json={
                "query": "What does this workspace say?",
                "top_k": 3,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "query": "What does this workspace say?",
        "tenant_id": "demo",
        "results": [
            {
                "document_id": "doc-1",
                "chunk_id": "chunk-1",
                "chunk_index": 0,
                "content": "Workspace content",
                "distance": 0.11,
            }
        ],
    }

    assert captured["require_workspace"] == {
        "workspace_id": "11111111-1111-1111-1111-111111111111",
        "tenant_id": "demo",
    }

    assert captured["retrieve_context"] == {
        "query": "What does this workspace say?",
        "tenant_id": "demo",
        "top_k": 3,
        "workspace_id": "11111111-1111-1111-1111-111111111111",
    }


def test_workspace_ask_route_passes_workspace_id(monkeypatch):
    captured = {}

    async def fake_require_workspace(*, workspace_id: str, tenant_id: str):
        captured["require_workspace"] = {
            "workspace_id": workspace_id,
            "tenant_id": tenant_id,
        }
        return {
            "id": workspace_id,
            "tenant_id": tenant_id,
            "name": "Test Workspace",
            "description": None,
            "created_at": "now",
            "updated_at": "now",
        }

    async def fake_answer_question(
        *,
        query: str,
        tenant_id: str,
        top_k: int,
        workspace_id: str | None = None,
    ):
        captured["answer_question"] = {
            "query": query,
            "tenant_id": tenant_id,
            "top_k": top_k,
            "workspace_id": workspace_id,
        }

        return {
            "query": query,
            "tenant_id": tenant_id,
            "answer": "This answer is grounded in the workspace. [D1]",
            "sources": [
                {
                    "id": "D1",
                    "document_id": "doc-1",
                    "chunk_id": "chunk-1",
                    "chunk_index": 0,
                    "content": "Workspace content",
                    "distance": 0.11,
                }
            ],
        }

    monkeypatch.setattr(workspace_routes, "require_workspace", fake_require_workspace)
    monkeypatch.setattr(workspace_routes, "answer_question", fake_answer_question)

    app.dependency_overrides[get_tenant_id] = override_tenant_demo

    try:
        response = client.post(
            "/workspaces/22222222-2222-2222-2222-222222222222/rag/ask",
            json={
                "query": "Summarize this workspace",
                "top_k": 2,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "query": "Summarize this workspace",
        "tenant_id": "demo",
        "answer": "This answer is grounded in the workspace. [D1]",
        "sources": [
            {
                "id": "D1",
                "document_id": "doc-1",
                "chunk_id": "chunk-1",
                "chunk_index": 0,
                "content": "Workspace content",
                "distance": 0.11,
            }
        ],
    }

    assert captured["require_workspace"] == {
        "workspace_id": "22222222-2222-2222-2222-222222222222",
        "tenant_id": "demo",
    }

    assert captured["answer_question"] == {
        "query": "Summarize this workspace",
        "tenant_id": "demo",
        "top_k": 2,
        "workspace_id": "22222222-2222-2222-2222-222222222222",
    }


def test_workspace_rag_route_returns_404_when_workspace_not_found(monkeypatch):
    async def fake_require_workspace(*, workspace_id: str, tenant_id: str):
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Workspace not found")

    async def fake_answer_question(
        *,
        query: str,
        tenant_id: str,
        top_k: int,
        workspace_id: str | None = None,
    ):
        raise AssertionError("answer_question should not be called")

    monkeypatch.setattr(workspace_routes, "require_workspace", fake_require_workspace)
    monkeypatch.setattr(workspace_routes, "answer_question", fake_answer_question)

    app.dependency_overrides[get_tenant_id] = override_tenant_other

    try:
        response = client.post(
            "/workspaces/33333333-3333-3333-3333-333333333333/rag/ask",
            json={
                "query": "Should not access this workspace",
                "top_k": 3,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workspace not found",
    }