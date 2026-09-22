"""Read `.context/module-context.md` next to a CodeQL class row.

The Python extractor does not put markdown in the database. CodeQL emits the
class and the absolute path of its `.py` file; these helpers open the sibling
module-context file and apply the same text checks the scanners use.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List

_FORBIDDEN_HEADINGS = frozenset(
    {
        "internal design",
        "internal",
        "internals",
        "participants",
        "domain separation",
        "pickup",
        "layout",
        "known scan notes",
        "implementation",
        "implementation notes",
        "scan violations",
        "tests",
        "scanners",
        "modules fidelity",
    }
)
_HEADING = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$")
_MODULES_HEADING = re.compile(r"^\s*#{1,6}\s+Modules\b", re.MULTILINE | re.IGNORECASE)
_PRIVATE_NAME = re.compile(r"(?<![A-Za-z0-9*])(_(?!is_)[A-Za-z][A-Za-z0-9_]*)\b")
_SIX_DASHES = re.compile(r"^------\s*$", re.MULTILINE)
_SOURCES = re.compile(r"^\s*\*\*Sources\s*/\s*context:\*\*", re.MULTILINE | re.IGNORECASE)
_LIVE_INSTANCE = re.compile(r"Live instance:", re.IGNORECASE)


def _py_file(row: dict) -> Path:
    return Path(str(row.get("message") or ""))


def _module_folder(py_file: Path) -> Path:
    return py_file.parent


def _context_file(py_file: Path) -> Path:
    return _module_folder(py_file) / ".context" / "module-context.md"


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _hit(row: dict, message: str) -> dict:
    return {
        "name": row.get("name") or "",
        "message": message,
        "contributor": row.get("contributor") or "",
    }


def rows_for_missing_module_context(rows: Iterable[dict]) -> List[dict]:
    refined: List[dict] = []
    seen: set[str] = set()
    for row in rows:
        py_file = _py_file(row)
        if not py_file.suffix.lower() == ".py":
            continue
        folder = _module_folder(py_file)
        key = str(folder)
        if key in seen:
            continue
        if _context_file(py_file).is_file():
            continue
        seen.add(key)
        refined.append(
            _hit(
                row,
                f"Module folder '{folder.name}' defines classes but has no "
                f".context/module-context.md. "
                f"Add one with at minimum: Purpose, Seam, Dependencies.",
            )
        )
    return refined


def rows_for_language_modules_one_section(rows: Iterable[dict]) -> List[dict]:
    refined: List[dict] = []
    seen: set[str] = set()
    for row in rows:
        context = _context_file(_py_file(row))
        key = str(context)
        if key in seen or not context.is_file():
            continue
        seen.add(key)
        if _MODULES_HEADING.search(_read(context)):
            refined.append(
                _hit(
                    row,
                    f"Module '{context.parent.parent.name}' module-context has a "
                    f"'Modules' heading. Language and modules are one ## Language "
                    f"section — drop ## Modules.",
                )
            )
    return refined


def rows_for_public_seam_only(rows: Iterable[dict]) -> List[dict]:
    refined: List[dict] = []
    seen: set[str] = set()
    for row in rows:
        context = _context_file(_py_file(row))
        key = str(context)
        if key in seen or not context.is_file():
            continue
        seen.add(key)
        content = _read(context)
        folder = context.parent.parent.name
        for line in content.splitlines():
            match = _HEADING.match(line)
            if not match:
                continue
            heading = match.group(1).strip()
            key_heading = heading.lower()
            if key_heading in _FORBIDDEN_HEADINGS or "internal" in key_heading:
                refined.append(
                    _hit(
                        row,
                        f"Module '{folder}' module-context heading '{heading}' is "
                        f"not part of the public seam.",
                    )
                )
        for match in _PRIVATE_NAME.finditer(content):
            refined.append(
                _hit(
                    row,
                    f"Module '{folder}' module-context names private '{match.group(1)}'.",
                )
            )
    return refined


def rows_for_modules_not_model_blocks(rows: Iterable[dict]) -> List[dict]:
    refined: List[dict] = []
    seen: set[str] = set()
    for row in rows:
        context = _context_file(_py_file(row))
        key = str(context)
        if key in seen or not context.is_file():
            continue
        seen.add(key)
        content = _read(context)
        folder = context.parent.parent.name
        for pattern, detail in (
            (_SIX_DASHES, "typed `------` member dump"),
            (_SOURCES, "**Sources / context** that lists this folder's own files"),
            (_LIVE_INSTANCE, "'Live instance:' name inventory"),
        ):
            if pattern.search(content):
                refined.append(
                    _hit(
                        row,
                        f"Module '{folder}' module-context has {detail}",
                    )
                )
    return refined
