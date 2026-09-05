"""Shared workspace discovery helpers for abd-architecture-specification scanners.

Context helpers:
  find_central_spec(workspace)       -> Path | None
  find_all_context_files(workspace)  -> list[Path]
  build_arch_spec_context(workspace) -> ScanFilesContext

Text helpers:
  is_mechanism_context(text)  -> bool
  is_test_context(file)       -> bool
  extract_section(text, heading) -> str | None
  iter_code_blocks(text)      -> Iterator[str]
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List, Optional

from scanner_bases.resources.scan_context import FileCollection, ScanFilesContext

# ── filenames ────────────────────────────────────────────────────────────────

CENTRAL_SPEC_NAME = "architecture-specification.md"
CONTEXT_FILE_NAME = "architecture-context.md"

# ── discovery ────────────────────────────────────────────────────────────────

def find_central_spec(workspace: Path) -> Optional[Path]:
    """Return the central architecture-specification.md, or None."""
    for candidate in (
        workspace / "docs" / "architecture" / "specification" / CENTRAL_SPEC_NAME,
        workspace / "docs" / "architecture" / CENTRAL_SPEC_NAME,
        workspace / "architecture" / CENTRAL_SPEC_NAME,
        workspace / CENTRAL_SPEC_NAME,
    ):
        if candidate.is_file():
            return candidate
    matches = sorted(workspace.rglob(CENTRAL_SPEC_NAME))
    return matches[0] if matches else None


def find_all_context_files(workspace: Path) -> List[Path]:
    """Return all architecture-context.md files under workspace, sorted."""
    return sorted(workspace.rglob(CONTEXT_FILE_NAME))


def resolve_spec_link(raw: str, spec_path: Path, workspace: Path) -> Path:
    """Resolve a markdown link target from the central spec.

    Paths starting with ``/`` are repo-root-relative (e.g. ``/src/foo/architecture-context.md``).
    All other paths are relative to the spec file's directory.
    """
    raw_no_anchor = raw.split("#")[0].strip()
    if raw_no_anchor.startswith("/"):
        return (workspace / raw_no_anchor.lstrip("/")).resolve()
    return (spec_path.parent / raw_no_anchor).resolve()


def build_arch_spec_context(
    workspace: Path,
    story_graph: Optional[Path] = None,
) -> ScanFilesContext:
    """ScanFilesContext with the central spec + every context file."""
    del story_graph  # reserved for future graph-aware scans
    files: List[Path] = []
    central = find_central_spec(workspace)
    if central:
        files.append(central)
    for ctx in find_all_context_files(workspace):
        if ctx not in files:
            files.append(ctx)
    ctx = ScanFilesContext(files=FileCollection(code_files=files))
    ctx._workspace = workspace.resolve()  # noqa: SLF001 — scanners read repo root for link resolution
    return ctx


# ── file classification ───────────────────────────────────────────────────────

_PARTICIPANTS_RE = re.compile(r"^##\s+Participants\s*$", re.MULTILINE | re.IGNORECASE)


def is_mechanism_context(text: str) -> bool:
    """True if the file uses the mechanism context template (has a Participants section)."""
    return bool(_PARTICIPANTS_RE.search(text))


def is_test_context(file: Path) -> bool:
    """True if the file lives inside a test-related directory."""
    parts = {p.lower() for p in file.parts}
    return bool(parts & {"test", "tests", "testing", "test-helpers", "test_helpers"})


# ── markdown helpers ──────────────────────────────────────────────────────────

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
_CODE_FENCE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)


def extract_section(text: str, heading: str) -> Optional[str]:
    """Return the body under the first heading whose text matches (case-insensitive).

    Stops at the next heading of equal or higher level. Returns None if not found.
    """
    pattern = re.compile(
        r"^(#{1,6})\s+" + re.escape(heading.strip()) + r"\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    m = pattern.search(text)
    if not m:
        return None
    level = len(m.group(1))
    start = m.end()
    stop_pat = re.compile(r"^#{1," + str(level) + r"}\s", re.MULTILINE)
    stop = stop_pat.search(text, start)
    return text[start: stop.start() if stop else len(text)].strip()


def iter_code_blocks(text: str) -> Iterator[str]:
    """Yield the body of each fenced code block in *text*."""
    for m in _CODE_FENCE_RE.finditer(text):
        yield m.group(1)
