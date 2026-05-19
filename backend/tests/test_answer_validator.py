from app.rag.answer_validator import (
    answer_has_required_citation,
    answer_uses_only_allowed_sources,
    extract_citations,
)


def test_extract_citations():
    answer = "This is supported by [D1] and [D2]."
    assert extract_citations(answer) == {"[D1]", "[D2]"}


def test_answer_has_required_citation():
    assert answer_has_required_citation("The document says this. [D1]") is True
    assert answer_has_required_citation("The document says this.") is False


def test_answer_uses_only_allowed_sources():
    allowed_sources = {"[D1]"}

    assert answer_uses_only_allowed_sources(
        "The document says this. [D1]",
        allowed_sources,
    ) is True

    assert answer_uses_only_allowed_sources(
        "The document says this. [D2]",
        allowed_sources,
    ) is False