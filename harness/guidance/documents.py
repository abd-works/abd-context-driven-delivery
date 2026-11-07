"""The document a call names: text it sends, or the files at paths it names, read here so the call carries no body."""
from __future__ import annotations

from pathlib import Path

# Folders a document read from a folder never includes: version control, environments, and caches.
_SKIP_PARTS = {".git", ".venv", "node_modules", "__pycache__"}
# A null byte never appears in text, so a file holding one is an image or another binary file.
_BINARY_MARK = b"\x00"


def load_document(content: str = "", paths: list[str] | str | None = None) -> str:
    """The in-process text, or the files at paths. Paths win."""
    if paths in ("", None, []):
        return content or ""
    entries = [paths] if isinstance(paths, str) else list(paths)
    return "\n\n".join(_read_entry(Path(entry)) for entry in entries)


def _read_entry(path: Path) -> str:
    if path.is_dir():
        files = [
            item
            for item in sorted(path.rglob("*"))
            if item.is_file() and not any(part in _SKIP_PARTS for part in item.parts)
        ]
        return "\n\n".join(text for text in map(_text_of, files) if text is not None)
    return path.read_text(encoding="utf-8", errors="replace")


def _text_of(file: Path) -> str | None:
    """The text of a file in a folder a call names; none for an image or another binary file, which a folder of
    documents can hold beside them but no reader can take as text."""
    data = file.read_bytes()
    return None if _BINARY_MARK in data else data.decode("utf-8", errors="replace")
