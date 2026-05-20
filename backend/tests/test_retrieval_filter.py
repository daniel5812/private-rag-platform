from app.rag.retrieval import filter_chunks_by_distance


def test_filter_chunks_by_distance_keeps_relevant_chunks():
    chunks = [
        {"content": "relevant", "distance": 0.25},
        {"content": "less relevant", "distance": 0.55},
    ]

    result = filter_chunks_by_distance(chunks, max_distance=0.45)

    assert len(result) == 1
    assert result[0]["content"] == "relevant"


def test_filter_chunks_by_distance_returns_empty_when_all_too_far():
    chunks = [
        {"content": "far", "distance": 0.8},
        {"content": "farther", "distance": 0.9},
    ]

    result = filter_chunks_by_distance(chunks, max_distance=0.45)

    assert result == []


def test_filter_chunks_by_distance_ignores_missing_distance():
    chunks = [
        {"content": "bad", "distance": None},
        {"content": "good", "distance": 0.2},
    ]

    result = filter_chunks_by_distance(chunks, max_distance=0.45)

    assert len(result) == 1
    assert result[0]["content"] == "good"