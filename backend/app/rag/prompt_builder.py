def build_rag_prompt(query: str, chunks: list[dict]) -> str:
    context_blocks = []
    allowed_sources = []

    for index, chunk in enumerate(chunks, start=1):
        source_id = f"D{index}"
        allowed_sources.append(f"[{source_id}]")
        context_blocks.append(
            f"[{source_id}]\n"
            f"Content:\n{chunk['content']}"
        )

    context = "\n\n".join(context_blocks)
    allowed_sources_text = ", ".join(allowed_sources)

    return f"""
You are a private enterprise RAG assistant.

Answer the user's question using ONLY the provided context.

Allowed source IDs:
{allowed_sources_text}

Strict rules:
- Use ONLY facts that appear explicitly in the context.
- Do not use outside knowledge.
- Do not define terms unless the definition appears in the context.
- Do not infer general meanings.
- Do not mention compliance, security requirements, authorization, viewing, editing, deleting, or modification unless those exact ideas appear in the context.
- Do not invent source IDs. Use only these source IDs: {allowed_sources_text}
- If only one source is provided, cite only [D1].
- Every sentence must include a valid citation.
- Keep the answer to one short sentence when possible.
- If the context is too limited, say what the document mentions, not what the concept generally means.

Good answer style:
"The document mentions access control in relation to internal company policy, permissions, secure document retrieval, and employee access management. [D1]"

Bad answer style:
"Access control refers to controlling who can view, edit, or delete documents."
This is bad unless those details appear explicitly in the context.

Context:
{context}

User question:
{query}

Answer:
""".strip()