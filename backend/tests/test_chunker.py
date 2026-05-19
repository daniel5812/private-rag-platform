from app.documents.chunker import chunk_text


def test_chunk_text_returns_empty_list_for_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_returns_single_chunk_for_short_text():
    text = "This is a short document."
    chunks = chunk_text(text, chunk_size=100, overlap=20)

    assert chunks == [text]


def test_chunk_text_splits_long_text_with_overlap():
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = chunk_text(text, chunk_size=10, overlap=2)

    assert chunks[0] == "abcdefghij"
    assert chunks[1] == "ijklmnopqr"
    assert chunks[2] == "qrstuvwxyz"