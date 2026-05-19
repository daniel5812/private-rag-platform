import re


def extract_citations(answer: str) -> set[str]:
    return set(re.findall(r"\[D\d+\]", answer))


def answer_uses_only_allowed_sources(answer: str, allowed_source_ids: set[str]) -> bool:
    used_sources = extract_citations(answer)
    return used_sources.issubset(allowed_source_ids)


def answer_has_required_citation(answer: str) -> bool:
    return bool(extract_citations(answer))