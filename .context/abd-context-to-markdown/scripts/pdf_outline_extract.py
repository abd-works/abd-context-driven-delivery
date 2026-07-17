"""
PDF → markdown by **outline + anchored text** (PyMuPDF).

Uses the PDF bookmark list in **document order** (not sorted by page). For each entry,
text runs from **below that entry’s heading** to **just before the next entry’s heading**,
using ``page.search_for()`` to locate heading banners. That keeps each paragraph in one
section only (no parent bodies containing subsection text, no duplicate copies for nested
headings on the same page).

* ``extract_markdown_from_pdf_outline(pdf_path)`` returns ``None`` unless
  ``PDF_USE_PYMUPDF_OUTLINE=1`` is set (opt-in), or if PyMuPDF is missing,
  the file can’t open, or the PDF has no outline—then ``convert_to_markdown`` uses
  MarkItDown + ``pdf_markdown_post``.

**Default** PDF extraction is **MarkItDown** (linear). Set ``PDF_USE_PYMUPDF_OUTLINE=1``
to use this bookmark-bounded path. ``PDF_USE_MARKITDOWN_PDF`` is ignored here; unset or any
value keeps the default unless the opt-in is set.
"""

from __future__ import annotations

import os
import re
import sys
import traceback
from pathlib import Path


def _pymupdf_outline_wanted() -> bool:
    """True when the user opts into PyMuPDF bookmark outline extraction."""
    v = os.environ.get("PDF_USE_PYMUPDF_OUTLINE", "").strip().lower()
    return v in ("1", "true", "yes")


def _heading_hashes_for_level(level: int) -> str:
    """PyMuPDF outline levels are 1-based; avoid single ``#`` (document title reserved)."""
    n = min(6, max(2, int(level) + 1))
    return "#" * n


def _title_search_strings(title: str) -> list[str]:
    """Fallback phrases if the **exact** TOC title is not found on the page (typography variants).

    Callers should try **exact bookmark text first** via ``_title_exact_queries`` — that string is
    the PDF’s section marker. These variants exist only for banners that omit punctuation or use
    all-caps, not as the primary anchor.
    """
    t = title.strip()
    if not t:
        return []
    seen: set[str] = set()
    out: list[str] = []

    def add(s: str) -> None:
        s = " ".join(s.split())
        if len(s) < 2:
            return
        if s not in seen:
            seen.add(s)
            out.append(s)

    add(t)
    add(t.upper())
    # "Chapter 1: The Basics" → also try subtitle fragment (banner often uses caps)
    if ":" in t:
        tail = t.split(":", 1)[1].strip()
        add(tail)
        add(tail.upper())
    # collapse spaces for banners like "THE CORE MECHANIC"
    collapsed = re.sub(r"\s+", " ", t.upper())
    add(collapsed)
    return out


def _title_exact_queries(title: str) -> list[str]:
    """Exact text from the outline/TOC entry (strip only whitespace). That is the section marker."""
    t = title.strip()
    if len(t) < 2:
        return []
    return [t]


def _queries_for_heading_lookup(title: str) -> list[str]:
    """Ordered queries: exact TOC title first, then typography fallbacks."""
    exact = _title_exact_queries(title)
    fallbacks = _title_search_strings(title)
    seen: set[str] = set()
    out: list[str] = []
    for s in exact + fallbacks:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def _resolve_primary_heading(
    doc,
    title: str,
    page_hint_0: int,
    radius: int = 3,
):
    """Find the printed section banner when the TOC page index is off by one (or more).

    Searches ``page_hint_0 ± radius`` and keeps the **largest-area** ``_primary_heading_rect``
    match so we anchor to the main banner rather than a body mention.
    """
    queries = _queries_for_heading_lookup(title)
    n = doc.page_count
    best_a = -1.0
    best_pi = page_hint_0
    best_rect = None
    for d in range(-radius, radius + 1):
        pi = page_hint_0 + d
        if pi < 0 or pi >= n:
            continue
        pr = _primary_heading_rect(doc[pi], queries)
        if pr is None:
            continue
        a = float(pr.width * pr.height)
        if a > best_a:
            best_a = a
            best_pi = pi
            best_rect = pr
    return best_pi, best_rect


def _boundary_next_toc_same_column(
    doc,
    items: list[dict],
    cur_i: int,
    page_idx: int,
    band_cur: tuple[float, float] | None,
) -> float | None:
    """On 2-column pages, the next *bookmark* may be in the other column (lower or higher Y).

    Scan subsequent TOC entries in order; return the **top Y** of the first whose **primary**
    banner lies in ``band_cur`` on ``page_idx``. Used to end Affliction (right column) before
    Communication (right column) even though Burrowing (left) is the next TOC entry.
    """
    if band_cur is None:
        return None
    pg = doc[page_idx]
    for j in range(cur_i + 1, len(items)):
        nxt = items[j]
        title = nxt["title"]
        hint = int(nxt["page_0"])
        if hint > page_idx + 3:
            break
        if hint < page_idx - 3:
            continue
        pi, pr = _resolve_primary_heading(doc, title, hint)
        if pi != page_idx or pr is None:
            continue
        b = _column_band(pg, pr)
        if b is None:
            continue
        if abs(b[0] - band_cur[0]) < 1.0 and abs(b[1] - band_cur[1]) < 1.0:
            return float(pr.y0)
    return None


def _last_page_span_end_y(
    page,
    band_cur: tuple[float, float] | None,
    next_primary,
    y_body0: float,
) -> float:
    """End Y for the **last** page of a multi-page section (body often starts at 0 on that page)."""
    h = float(page.rect.height)
    if next_primary is None:
        return h
    b_nxt = _column_band(page, next_primary)
    if (
        band_cur is not None
        and b_nxt is not None
        and _bands_different_column(band_cur, b_nxt)
    ):
        return h
    yn = float(next_primary.y0)
    if yn <= y_body0 + 0.5:
        return h
    return yn


def _primary_heading_rect(page, ordered_queries: list[str]):
    """Pick the **main** printed heading vs running headers / small duplicate hits.

    ``ordered_queries`` is tried **in order** (exact TOC title first, then typography fallbacks).
    The first query that yields any in-band match wins — we do not merge matches from a loose
    variant when the exact section-marker text exists on the page.

    Among matches for that query, prefer the **largest-area** rect in the upper ~88% of the page.
    Tie-break: higher on page (smaller y0).
    """
    h = float(page.rect.height)
    hmax = h * 0.88
    for q in ordered_queries:
        candidates: list = []
        try:
            rects = page.search_for(q)
        except Exception:
            rects = []
        for r in rects:
            if r.y0 >= hmax:
                continue
            candidates.append(r)
        if candidates:
            return max(candidates, key=lambda r: (r.width * r.height, -r.y0))
    return None


def _heading_top_bottom(page, queries: list[str]):
    """Return (y0, y1) of the **primary** heading rect (main banner), or (None, None)."""
    best = _primary_heading_rect(page, queries)
    if best is None:
        return None, None
    return best.y0, best.y1


def _body_start_y(page, title: str) -> float:
    """Y coordinate where body text starts (below the heading banner)."""
    y0, y1 = _heading_top_bottom(page, _queries_for_heading_lookup(title))
    if y0 is None or y1 is None:
        return 0.0
    return min(y1 + 1.0, page.rect.height)


def _heading_top_for_item(page, title: str) -> float:
    """Top y of this section’s heading (for filtering the *next* heading on the same page)."""
    y0, _ = _heading_top_bottom(page, _queries_for_heading_lookup(title))
    return 0.0 if y0 is None else y0


def _next_heading_top(page, title: str, y_min: float = 0.0) -> float | None:
    """Deprecated for same-page boundaries — use ``_primary_heading_rect`` for the next title.

    Kept for callers that need a legacy top; **min y** among matches with ``y0 >= y_min`` is wrong
    on two-column pages (the real next banner can sit above ``y_min`` in the other column).
    """
    for q in _queries_for_heading_lookup(title):
        best_y0: float | None = None
        try:
            rects = page.search_for(q)
        except Exception:
            rects = []
        for r in rects:
            if r.y0 < y_min - 0.5:
                continue
            if best_y0 is None or r.y0 < best_y0:
                best_y0 = r.y0
        if best_y0 is not None:
            return best_y0
    return None


def _column_band(page, heading_rect) -> tuple[float, float] | None:
    """Horizontal clip for a **section banner** on a two-column spread.

    Returns ``(x0, x1)`` in page coordinates for **half-page** columns, or ``None`` for
    **full-width** headings (wide banners / chapter titles) — caller clips ``0 .. page.width``.
    """
    if heading_rect is None:
        return None
    w = float(page.rect.width)
    rw = float(heading_rect.width)
    if rw >= 0.40 * w:
        return None
    cx = (float(heading_rect.x0) + float(heading_rect.x1)) / 2.0
    mid = w / 2.0
    if cx < mid:
        return (0.0, mid)
    return (mid, w)


def _bands_different_column(
    band_a: tuple[float, float] | None,
    band_b: tuple[float, float] | None,
) -> bool:
    """True when both bands are **column halves** (non-``None``) and they are **not** the same half."""
    if band_a is None or band_b is None:
        return False
    return abs(band_a[0] - band_b[0]) > 1.0


def _same_page_body_end_y(
    page,
    cur_primary,
    next_primary,
    y_body0: float,
) -> float:
    """Bottom Y (exclusive) for body text on **this** page when ``cur`` and ``next`` are on the same page.

    If the next bookmark’s **primary** banner sits in the **other** column**, the vertical
    boundary for this column is the **page bottom** — the next section’s ``y0`` must not clip
    the current column (two-column layouts often place the next TOC entry above/beside the
    current heading in Y).
    """
    h = float(page.rect.height)
    if next_primary is None:
        return h
    b_cur = _column_band(page, cur_primary)
    b_nxt = _column_band(page, next_primary)
    if _bands_different_column(b_cur, b_nxt):
        return h
    yn = float(next_primary.y0)
    if yn <= y_body0 + 0.5:
        return h
    return yn


def _extract_vertical_span(
    doc,
    p0: int,
    y_start: float,
    p1: int,
    y_end_exclusive: float,
    x0_clip: float | None = None,
    x1_clip: float | None = None,
) -> str:
    """Extract text from (p0, y_start) through optional horizontal band, ending before y_end_exclusive on p1."""
    parts: list[str] = []
    n = doc.page_count
    p0 = max(0, min(p0, n - 1))
    p1 = max(0, min(p1, n - 1))
    if p0 > p1:
        return ""

    for pn in range(p0, p1 + 1):
        pg = doc[pn]
        rect = pg.rect
        w, h = rect.width, rect.height
        xa = 0.0 if x0_clip is None else max(0.0, min(float(x0_clip), w))
        xb = float(w) if x1_clip is None else max(0.0, min(float(x1_clip), w))
        if xa >= xb:
            xa, xb = 0.0, float(w)
        if pn == p0 and pn == p1:
            y1_clip = max(0.0, min(y_end_exclusive, h))
            y0_clip = max(0.0, min(y_start, h))
            if y0_clip >= y1_clip:
                continue
            clip = (xa, y0_clip, xb, y1_clip)
        elif pn == p0:
            y0_clip = max(0.0, min(y_start, h))
            clip = (xa, y0_clip, xb, h)
        elif pn == p1:
            y1_clip = max(0.0, min(y_end_exclusive, h))
            clip = (xa, 0.0, xb, y1_clip)
        else:
            clip = (xa, 0.0, xb, h)
        # PyMuPDF expects fitz.Rect — import inside function to avoid if fitz missing
        import fitz  # type: ignore[import-untyped]

        r = fitz.Rect(clip[0], clip[1], clip[2], clip[3])
        t = pg.get_text("text", clip=r) or ""
        if t.strip():
            parts.append(t)
    return "\n\n".join(parts)


def _parse_toc_entries(doc) -> list[dict] | None:
    """Return [{level, title, page_0}, ...] in **bookmark order** (do not sort by page)."""
    try:
        toc = doc.get_toc(simple=False)
    except Exception:
        toc = None
    if not toc:
        toc = doc.get_toc()
    if not toc:
        return None

    items: list[dict] = []
    for row in toc:
        if len(row) < 3:
            continue
        try:
            lvl = int(row[0])
            title = str(row[1]).strip()
        except (TypeError, ValueError):
            continue
        if not title:
            continue
        dest = row[3] if len(row) > 3 and isinstance(row[3], dict) else None
        if dest is not None and "page" in dest:
            try:
                p0 = int(dest["page"])
            except (TypeError, ValueError):
                continue
        else:
            try:
                p1b = int(row[2])
            except (TypeError, ValueError):
                continue
            if p1b < 1:
                continue
            p0 = p1b - 1
        items.append({"level": lvl, "title": title, "page_0": p0})
    return items if items else None


def extract_markdown_from_pdf_outline(pdf_path: Path) -> str | None:
    """
    Build markdown from PDF bookmarks: each section’s body is the text **between** this
    heading and the next bookmark heading (TOC order), so subsection text is not repeated
    under parents.
    """
    if not _pymupdf_outline_wanted():
        return None
    try:
        import fitz  # type: ignore[import-untyped]  # PyMuPDF
    except ImportError as e:
        print(
            "pdf_outline_extract: PyMuPDF is not installed (pip install pymupdf).",
            file=sys.stderr,
        )
        print(f"  ImportError: {e}", file=sys.stderr)
        return None

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(
            f"pdf_outline_extract: fitz.open({pdf_path!r}) failed; falling back to MarkItDown path.",
            file=sys.stderr,
        )
        print(f"  {type(e).__name__}: {e}", file=sys.stderr)
        traceback.print_exc()
        return None

    try:
        items = _parse_toc_entries(doc)
        if not items:
            print(
                "pdf_outline_extract: PDF has no outline/TOC entries; "
                "use MarkItDown or fix the PDF.",
                file=sys.stderr,
            )
            return None
        print(
            f"[convert] PyMuPDF outline: {doc.page_count} pages, {len(items)} outline entries…",
            file=sys.stderr,
            flush=True,
        )

        parts: list[str] = []
        n_doc = doc.page_count

        for i, cur in enumerate(items):
            lvl = cur["level"]
            title = cur["title"]
            hashes = _heading_hashes_for_level(lvl)

            p_start_raw = max(0, min(cur["page_0"], n_doc - 1))
            p_start, cur_primary = _resolve_primary_heading(doc, title, p_start_raw)
            page_s = doc[p_start]
            if cur_primary is not None:
                y_body0 = min(float(cur_primary.y1) + 1.0, float(page_s.rect.height))
            else:
                y_body0 = _body_start_y(page_s, title)

            band_cur = _column_band(page_s, cur_primary)
            x0_clip = None if band_cur is None else band_cur[0]
            x1_clip = None if band_cur is None else band_cur[1]

            if i + 1 < len(items):
                nxt = items[i + 1]
                p_end_raw = max(0, min(nxt["page_0"], n_doc - 1))
                p_end, next_primary = _resolve_primary_heading(
                    doc, nxt["title"], p_end_raw
                )
                page_e = doc[p_end]

                if p_start == p_end:
                    y_end = _same_page_body_end_y(
                        page_s, cur_primary, next_primary, y_body0
                    )
                else:
                    y_peer = _boundary_next_toc_same_column(
                        doc, items, i, p_end, band_cur
                    )
                    if y_peer is not None:
                        y_end = y_peer
                    else:
                        y_end = _last_page_span_end_y(
                            page_e, band_cur, next_primary, 0.0
                        )

                if p_start == p_end:
                    # Same page: column-aware clip (two-column spreads).
                    if y_body0 >= y_end:
                        body = ""
                    else:
                        import fitz  # type: ignore[import-untyped]

                        r = page_s.rect
                        xa = 0.0 if x0_clip is None else x0_clip
                        xb = float(r.width) if x1_clip is None else x1_clip
                        body = (
                            page_s.get_text(
                                "text",
                                clip=fitz.Rect(xa, y_body0, xb, y_end),
                            )
                            or ""
                        )
                else:
                    body = _extract_vertical_span(
                        doc, p_start, y_body0, p_end, y_end, x0_clip, x1_clip
                    )
            else:
                # Last entry: to EOF from body start
                body_parts: list[str] = []
                for pn in range(p_start, n_doc):
                    pg = doc[pn]
                    r = pg.rect
                    xa = 0.0 if x0_clip is None else max(0.0, min(x0_clip, r.width))
                    xb = float(r.width) if x1_clip is None else max(0.0, min(x1_clip, r.width))
                    if pn == p_start:
                        import fitz  # type: ignore[import-untyped]

                        t = (
                            pg.get_text("text", clip=fitz.Rect(xa, y_body0, xb, r.height))
                            or ""
                        )
                    else:
                        t = (
                            pg.get_text("text", clip=fitz.Rect(xa, 0.0, xb, r.height))
                            or ""
                        )
                    if t.strip():
                        body_parts.append(t)
                body = "\n\n".join(body_parts)

            parts.append(f"{hashes} {title}\n\n{body.strip()}")

        out = "\n\n".join(parts)
        if out and not out.endswith("\n"):
            out += "\n"
        print(
            f"[convert] PyMuPDF outline: finished ({len(out)} chars).",
            file=sys.stderr,
            flush=True,
        )
        return out
    finally:
        doc.close()


def prepend_outline_extract_notice(text: str) -> str:
    """Optional banner so readers know this file was built from outline + page text."""
    return (
        "<!-- PDF: extracted from bookmark outline + anchored text (PyMuPDF). "
        "Sections are bounded by consecutive bookmarks; each paragraph appears once. "
        "Multi-column spreads use half-page clips; headings are resolved within ±3 pages "
        "of each bookmark when the destination is off. "
        "Unset PDF_USE_PYMUPDF_OUTLINE for MarkItDown + postprocess instead. -->\n\n"
    ) + text
