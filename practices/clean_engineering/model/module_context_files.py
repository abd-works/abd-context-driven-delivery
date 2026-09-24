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


class ModuleContext:
    def __init__(self, py_file: Path) -> None:
        self.py_file = py_file
        self.folder = py_file.parent
        self.path = self.folder / ".context" / "module-context.md"

    def exists(self) -> bool:
        return self.path.is_file()

    def as_record(self) -> dict:
        return {
            "path": str(self.path),
            "folder": self.folder.name,
            "exists": self.exists(),
        }

    def update_self(self, source: "ModuleContext") -> None:
        self.py_file = source.py_file
        self.folder = source.folder
        self.path = source.path

    def read(self) -> str:
        try:
            return self.path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def missing_hit(self, row: dict) -> dict | None:
        if self.py_file.suffix.lower() != ".py" or self.exists():
            return None
        return _hit(
            row,
            f"Module folder '{self.folder.name}' defines classes but has no "
            f".context/module-context.md. "
            f"Add one with at minimum: Purpose, Seam, Dependencies.",
        )

    def modules_heading_hit(self, row: dict) -> dict | None:
        if not self.exists() or not _MODULES_HEADING.search(self.read()):
            return None
        return _hit(
            row,
            f"Module '{self.path.parent.parent.name}' module-context has a "
            f"'Modules' heading. Language and modules are one ## Language "
            f"section — drop ## Modules.",
        )

    def public_seam_hits(self, row: dict) -> List[dict]:
        if not self.exists():
            return []
        hits: List[dict] = []
        content = self.read()
        folder = self.path.parent.parent.name
        for line in content.splitlines():
            match = _HEADING.match(line)
            if not match:
                continue
            heading = match.group(1).strip()
            key_heading = heading.lower()
            if key_heading in _FORBIDDEN_HEADINGS or "internal" in key_heading:
                hits.append(
                    _hit(
                        row,
                        f"Module '{folder}' module-context heading '{heading}' is "
                        f"not part of the public seam.",
                    )
                )
        for match in _PRIVATE_NAME.finditer(content):
            hits.append(
                _hit(
                    row,
                    f"Module '{folder}' module-context names private '{match.group(1)}'.",
                )
            )
        return hits

    def model_block_hits(self, row: dict) -> List[dict]:
        if not self.exists():
            return []
        hits: List[dict] = []
        content = self.read()
        folder = self.path.parent.parent.name
        for pattern, detail in (
            (_SIX_DASHES, "typed `------` member dump"),
            (_SOURCES, "**Sources / context** that lists this folder's own files"),
            (_LIVE_INSTANCE, "'Live instance:' name inventory"),
        ):
            if pattern.search(content):
                hits.append(_hit(row, f"Module '{folder}' module-context has {detail}"))
        return hits


class ModuleContextFiles:
    def rows_for_missing_module_context(self, rows: Iterable[dict]) -> List[dict]:
        refined: List[dict] = []
        seen: set[str] = set()
        for row in rows:
            context = ModuleContext(_py_file(row))
            key = str(context.folder)
            if key in seen:
                continue
            hit = context.missing_hit(row)
            if hit is None:
                continue
            seen.add(key)
            refined.append(hit)
        return refined

    def rows_for_language_modules_one_section(self, rows: Iterable[dict]) -> List[dict]:
        refined: List[dict] = []
        seen: set[str] = set()
        for row in rows:
            context = ModuleContext(_py_file(row))
            key = str(context.path)
            if key in seen:
                continue
            hit = context.modules_heading_hit(row)
            if hit is None:
                continue
            seen.add(key)
            refined.append(hit)
        return refined

    def rows_for_public_seam_only(self, rows: Iterable[dict]) -> List[dict]:
        refined: List[dict] = []
        seen: set[str] = set()
        for row in rows:
            context = ModuleContext(_py_file(row))
            key = str(context.path)
            if key in seen:
                continue
            seen.add(key)
            refined.extend(context.public_seam_hits(row))
        return refined

    def rows_for_modules_not_model_blocks(self, rows: Iterable[dict]) -> List[dict]:
        refined: List[dict] = []
        seen: set[str] = set()
        for row in rows:
            context = ModuleContext(_py_file(row))
            key = str(context.path)
            if key in seen:
                continue
            seen.add(key)
            refined.extend(context.model_block_hits(row))
        return refined


def _py_file(row: dict) -> Path:
    return Path(str(row.get("message") or ""))


def _hit(row: dict, message: str) -> dict:
    return {
        "name": row.get("name") or "",
        "message": message,
        "contributor": row.get("contributor") or "",
    }
