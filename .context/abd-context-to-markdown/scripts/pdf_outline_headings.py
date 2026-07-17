"""
Optional: map PDF bookmark/outline (TOC) entries to markdown ``##`` lines.

Uses **PyMuPDF** (``import fitz``) when installed. If PyMuPDF is missing, the PDF
has no outline, or alignment fails, the markdown is returned unchanged.

Alignment strategies (in order):

1. **Page-aligned:** If the extract contains form-feed page breaks (``\\f``) and the
   segment count roughly matches the PDF page count, match each TOC entry to a line
   on that page's segment.
2. **Global search:** Walk the TOC in order; for each title, promote the first
   unmatched line that matches (normalized equality or substring for longer titles).

Disable entirely: ``PDF_SKIP_OUTLINE_HEADINGS=1``
"""

from __future__ import annotations

import os
from pathlib import Path


def _outline_disabled() -> bool:
    v = os.environ.get("PDF_SKIP_OUTLINE_HEADINGS", "").strip().lower()
    return v in ("1", "true", "yes")


def _heading_from_toc_level(level: int) -> str:
    """PyMuPDF outline levels are 1-based; avoid single ``#`` (reserved for doc title)."""
    n = min(6, max(2, int(level) + 1))
    return "#" * n


def _norm(s: str) -> str:
    return " ".join(s.split())


def _line_matches_title(line: str, title: str) -> bool:
    st = line.strip()
    if not st or st.startswith("#"):
        return False
    a, b = _norm(st), _norm(title)
    if not b:
        return False
    if a == b:
        return True
    if len(b) < 8:
        return False
    if b in a:
        return True
    if len(a) >= 8 and a in b:
        return True
    return False


def _inject_title_in_lines(
    lines: list[str],
    title: str,
    hashes: str,
    used: set[int],
    start: int = 0,
) -> bool:
    for i in range(start, len(lines)):
        if i in used:
            continue
        if not _line_matches_title(lines[i], title):
            continue
        raw = lines[i]
        st = raw.strip()
        indent = raw[: len(raw) - len(raw.lstrip())]
        lines[i] = f"{indent}{hashes} {st}"
        used.add(i)
        return True
    return False


def _inject_page_aligned(
    pages: list[str],
    items: list[tuple[int, str, int]],
) -> str:
    out_pages = [p for p in pages]
    for idx in range(len(out_pages)):
        page_items = [(lvl, t, p) for (lvl, t, p) in items if p - 1 == idx]
        if not page_items:
            continue
        lines = out_pages[idx].splitlines()
        used: set[int] = set()
        for lvl, title, _ in page_items:
            hashes = _heading_from_toc_level(lvl)
            _inject_title_in_lines(lines, title, hashes, used, 0)
        out_pages[idx] = "\n".join(lines)
    return "\f".join(out_pages)


def _inject_global_search(text: str, items: list[tuple[int, str, int]]) -> str:
    lines = text.splitlines()
    used: set[int] = set()
    for lvl, title, _ in items:
        hashes = _heading_from_toc_level(lvl)
        _inject_title_in_lines(lines, title, hashes, used, 0)
    out = "\n".join(lines)
    if text.endswith("\n"):
        out += "\n"
    return out


def inject_pdf_outline_headings(pdf_path: Path, text: str) -> str:
    """If PyMuPDF and a TOC are available, prefix matching lines with markdown headings."""
    if _outline_disabled():
        return text
    try:
        import fitz  # type: ignore[import-untyped]  # PyMuPDF
    except ImportError:
        return text

    try:
        doc = fitz.open(str(pdf_path))
        toc = doc.get_toc()
        n_pdf = doc.page_count
        doc.close()
    except Exception:
        return text

    if not toc:
        return text

    items: list[tuple[int, str, int]] = []
    for row in toc:
        if len(row) < 3:
            continue
        try:
            lvl = int(row[0])
            title = str(row[1]).strip()
            page = int(row[2])
        except (TypeError, ValueError):
            continue
        if not title or page < 1:
            continue
        items.append((lvl, title, page))

    if not items:
        return text

    pages = text.split("\f")
    if len(pages) >= 2 and len(pages) <= n_pdf + 3:
        return _inject_page_aligned(pages, items)
    return _inject_global_search(text, items)
