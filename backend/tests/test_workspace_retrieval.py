import pytest

from app.rag import retrieval


@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_filters_by_workspace(monkeypatch):
    captured = {}

    async def fake_generate_embedding(query: str):
        captured["query"] = query
        return [0.1, 0.2, 0.3]

    async def fake_fetch(sql: str, *args):
        captured["sql"] = sql
        captured["args"] = args

        return [
            {
                "document_id": "doc-1",
                "chunk_id": "chunk-1",
                "chunk_index": 0,
                "content": "Workspace-specific content",
                "distance": 0.12,
            }
        ]

    monkeypatch.setattr(retrieval, "generate_embedding", fake_generate_embedding)
    monkeypatch.setattr(retrieval.database, "fetch", fake_fetch)
    monkeypatch.setattr(retrieval.settings, "retrieval_max_distance", 0.32)

    results = await retrieval.retrieve_relevant_chunks(
        query="What does this workspace say?",
        tenant_id="tenant-a",
        workspace_id="11111111-1111-1111-1111-111111111111",
        top_k=3,
    )

    assert captured["query"] == "What does this workspace say?"
    assert "workspace_id = $3::uuid" in captured["sql"]
    assert captured["args"] == (
        "[0.1,0.2,0.3]",
        "tenant-a",
        "11111111-1111-1111-1111-111111111111",
        3,
    )

    assert results == [
        {
            "document_id": "doc-1",
            "chunk_id": "chunk-1",
            "chunk_index": 0,
            "content": "Workspace-specific content",
            "distance": 0.12,
        }
    ]


@pytest.mark.asyncio
async def test_retrieve_relevant_chunks_without_workspace_keeps_legacy_behavior(monkeypatch):
    captured = {}

    async def fake_generate_embedding(query: str):
        captured["query"] = query
        return [0.1, 0.2, 0.3]

    async def fake_fetch(sql: str, *args):
        captured["sql"] = sql
        captured["args"] = args
        return []

    monkeypatch.setattr(retrieval, "generate_embedding", fake_generate_embedding)
    monkeypatch.setattr(retrieval.database, "fetch", fake_fetch)
    monkeypatch.setattr(retrieval.settings, "retrieval_max_distance", 0.32)

    results = await retrieval.retrieve_relevant_chunks(
        query="What does the tenant know?",
        tenant_id="tenant-a",
        top_k=5,
    )

    assert captured["query"] == "What does the tenant know?"
    assert "workspace_id = $3::uuid" not in captured["sql"]
    assert captured["args"] == (
        "[0.1,0.2,0.3]",
        "tenant-a",
        5,
    )
    assert results == []