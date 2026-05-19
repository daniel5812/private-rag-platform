from app.rag.answer_builder import build_grounded_fallback_answer


def test_fallback_returns_not_enough_information_without_chunks():
    answer = build_grounded_fallback_answer(
        query="What does the document say?",
        chunks=[],
    )

    assert answer == "I don't have enough information in the provided documents."


def test_fallback_for_access_control_uses_grounded_template():
    chunks = [
        {
            "content": (
                "This is a private RAG test document about internal company policy, "
                "access control, permissions, secure document retrieval, and employee "
                "access management."
            )
        }
    ]

    answer = build_grounded_fallback_answer(
        query="What does the document say about access control?",
        chunks=chunks,
    )

    assert answer == (
        "The document mentions access control in relation to internal company "
        "policy, permissions, secure document retrieval, and employee access "
        "management. [D1]"
    )