from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import EmptyFileError, PdfReadError


class UnsupportedFileTypeError(ValueError):
    pass


class EmptyExtractedTextError(ValueError):
    pass


class InvalidDocumentError(ValueError):
    pass


def extract_text_from_txt(storage_path: str) -> str:
    return Path(storage_path).read_text(encoding="utf-8")


def extract_text_from_pdf(storage_path: str) -> str:
    try:
        reader = PdfReader(storage_path)
    except EmptyFileError as exc:
        raise EmptyExtractedTextError("The uploaded PDF file is empty") from exc
    except PdfReadError as exc:
        raise InvalidDocumentError("The uploaded PDF file could not be read") from exc

    page_texts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.strip()

        if text:
            page_texts.append(text)

    return "\n\n".join(page_texts)


def extract_text_from_file(storage_path: str, content_type: str | None = None) -> str:
    file_suffix = Path(storage_path).suffix.lower()

    if content_type == "text/plain" or file_suffix == ".txt":
        text = extract_text_from_txt(storage_path)
    elif content_type == "application/pdf" or file_suffix == ".pdf":
        text = extract_text_from_pdf(storage_path)
    else:
        raise UnsupportedFileTypeError(
            f"Unsupported file type: content_type={content_type}, suffix={file_suffix}"
        )

    text = text.strip()

    if not text:
        raise EmptyExtractedTextError("No text could be extracted from the uploaded file")

    return text