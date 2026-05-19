from pathlib import Path


def extract_text_from_file(storage_path: str, content_type: str | None = None) -> str:
    path = Path(storage_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {storage_path}")

    if path.suffix.lower() == ".txt" or content_type == "text/plain":
        return path.read_text(encoding="utf-8")

    raise ValueError(f"Unsupported file type: {content_type or path.suffix}")