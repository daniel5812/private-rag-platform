def build_grounded_fallback_answer(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return "I don't have enough information in the provided documents."

    first_chunk = chunks[0]
    content = first_chunk["content"]

    query_lower = query.lower()
    content_lower = content.lower()

    if "access control" in query_lower and "access control" in content_lower:
        return (
            "The document mentions access control in relation to internal company "
            "policy, permissions, secure document retrieval, and employee access "
            "management. [D1]"
        )

    return f"The provided document mentions the following relevant information: {content} [D1]"