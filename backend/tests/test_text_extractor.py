from pathlib import Path

import pytest

from app.documents.text_extractor import (
    EmptyExtractedTextError,
    UnsupportedFileTypeError,
    extract_text_from_file,
)


def test_extract_text_from_txt(tmp_path: Path):
    file_path = tmp_path / "document.txt"
    file_path.write_text("Hello private RAG", encoding="utf-8")

    text = extract_text_from_file(str(file_path), content_type="text/plain")

    assert text == "Hello private RAG"


def test_extract_text_rejects_unsupported_file_type(tmp_path: Path):
    file_path = tmp_path / "document.csv"
    file_path.write_text("a,b,c", encoding="utf-8")

    with pytest.raises(UnsupportedFileTypeError):
        extract_text_from_file(str(file_path), content_type="text/csv")


def test_extract_text_rejects_empty_txt(tmp_path: Path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("   ", encoding="utf-8")

    with pytest.raises(EmptyExtractedTextError):
        extract_text_from_file(str(file_path), content_type="text/plain")

def test_extract_text_rejects_empty_pdf(tmp_path: Path):
    file_path = tmp_path / "empty.pdf"
    file_path.write_bytes(b"")

    with pytest.raises(EmptyExtractedTextError):
        extract_text_from_file(str(file_path), content_type="application/pdf")