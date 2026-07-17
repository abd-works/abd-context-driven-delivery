"""
Generic cleanup for PDF-extracted markdown (MarkItDown / pdfminer, etc.).

**This module rewrites markdown during convert**—the right place for structural composition
(findable headings, less noise) before chunking. The chunker and ``draft_chunking_spec`` only
read what is already on disk.

**Belongs here (convert pipeline):** patterns caused by the PDF format itself—running
headers/footers repeated on every page, duplicate banner lines, obvious extraction noise;
**conservative** regex-based heading promotion (``CHAPTER n``, ``APPENDIX``, ``PART …``);
**dotted-leader lines** (``Title ........ page``) → ``### Title {page}`` before chapter promotion;
optional **PDF outline → headings** via ``pdf_outline_headings`` when PyMuPDF is installed.

**Does not belong here:** book-specific tuning, corpus-only rules, archetype templates—use
a topic ``scripts/prepare_*.py`` or YAML-driven rules. (Exception: ``promote_mnm_reference_tables``
targets stable M&M PDF extract shapes; disable with ``PDF_SKIP_REFERENCE_TABLE_PROMOTE=1``.)

**Pipeline order:** After stripping the leading PDF table-of-contents block, **PDF outline → headings**
(``inject_pdf_outline_headings``) runs **before** ``promote_stacked_h2_column_tables`` and other
heavy layout passes. That way TOC titles still appear as plain lines for outline matching and are not
merged into pipe tables first.

**Canonical copy:** this skill’s ``scripts/`` folder only—implement PDF post-process changes here,
not in other repos. ``convert_to_markdown.convert_one`` applies this to ``.pdf`` sources after extraction
and before ``<!-- Source: -->`` injection and writing ``markdown/*.md``.

**Leading table of contents:** If the extract contains a ``TABLE OF CONTENTS`` block before
real body text, that region is **replaced** (not duplicated) with a short ``## Table of contents``
stub so dot-leader / regex passes do not turn the TOC into hundreds of fake ``###`` lines at
the front. End of the removed region is detected by the first ``WELCOME TO`` line (common RPG
intro) or, if missing, the first long mixed-case prose line. Set ``PDF_KEEP_LEADING_TOC=1`` to
disable.

**Env:** ``PDF_SKIP_REGEX_HEADINGS=1`` — skip regex promotion.
``PDF_SKIP_DOTTED_LEADER_HEADINGS=1`` — skip ``Title .... page`` → ``###`` promotion.
``PDF_SKIP_OUTLINE_HEADINGS=1`` — skip outline pass (see ``pdf_outline_headings.py``).
``PDF_KEEP_LEADING_TOC=1`` — do not replace the leading PDF table-of-contents block.
``PDF_SKIP_DEDUPE_CHAPTER_H2=1`` — skip dropping repeated identical ``## CHAPTER …`` / ``## APPENDIX …``
lines (PDF running headers).
``PDF_SKIP_ALL_CAPS_HEADINGS=1`` — skip promoting standalone ALL CAPS lines (e.g. ``ADVANTAGES``)
to ``### Title Case`` section headings.
``PDF_SKIP_DEMOTE_NON_CHAPTER_H2=1`` — skip demoting ``##`` to ``###`` after the first
``## CHAPTER n`` / ``## APPENDIX`` (keeps MarkItDown ``##`` as top-level everywhere).
``PDF_SKIP_STACKED_H2_TABLES=1`` — skip merging stacked column blocks into markdown pipe tables.
Optional: ``PDF_STACKED_TABLE_MIN_ROWS`` (default ``2``), ``PDF_STACKED_TABLE_MIN_COLS`` (default ``2``).
``PDF_STACKED_ROW_MAJOR_DROP_PARTIAL=0`` — disable dropping an incomplete last row in row-major tables.
``PDF_SKIP_REMOVE_STANDALONE_PAGE=1`` — keep lines that are only ``Page`` (PDF column spacers).
``PDF_SKIP_JOIN_SOFT_WRAPS=1`` — skip joining PDF hard line breaks inside paragraphs (see
``join_soft_wrapped_paragraph_lines``).
``PDF_SKIP_REFERENCE_TABLE_PROMOTE=1`` — skip M&M-style reference table → pipe tables (runs **last**,
after soft-wrap join; safe for bookmark-outline extracts).
Large PDFs: ``PDF_SKIP_OUTLINE_HEADINGS=1`` skips PyMuPDF outline injection (faster convert).
"""

from __future__ import annotations

import os
import re
from pathlib import Path


def _is_probable_running_header_or_footer_line(stripped: str) -> bool:
    """
    Heuristic: short standalone line that looks like a repeated title strip (no body text).

    Not book-specific—many PDFs emit ALL CAPS book title + chapter name in margins.
    """
    if not stripped or len(stripped) > 140:
        return False
    if stripped.startswith(("#", "|", "-", "•", "*")):
        return False
    letters = [c for c in stripped if c.isalpha()]
    if len(letters) < 4:
        return False
    if not all(c.isupper() for c in letters):
        return False
    # Avoid dropping duplicate sentences (rarely identical consecutive in prose)
    if ". " in stripped and len(stripped) > 50:
        return False
    return True


def collapse_consecutive_duplicate_banner_lines(text: str) -> str:
    """
    Drop the second of two consecutive identical lines when both look like PDF margin
    banners (ALL CAPS strips). Typical pattern::

        MUTANTS & MASTERMINDS
        MUTANTS & MASTERMINDS

        DELUXE HERO'S HANDBOOK
        DELUXE HERO'S HANDBOOK

    becomes one copy of each block with no handbook-specific strings hardcoded.
    """
    lines = text.splitlines()
    out: list[str] = []
    prev: str | None = None
    for line in lines:
        stripped = line.strip()
        if (
            prev is not None
            and stripped
            and stripped == prev
            and _is_probable_running_header_or_footer_line(stripped)
        ):
            continue
        out.append(line)
        if stripped:
            prev = stripped
        elif not stripped:
            pass
    joined = "\n".join(out)
    if text.endswith("\n") and not joined.endswith("\n"):
        joined += "\n"
    return joined


def _regex_promotion_disabled() -> bool:
    v = os.environ.get("PDF_SKIP_REGEX_HEADINGS", "").strip().lower()
    return v in ("1", "true", "yes")


def _dotted_leader_promotion_disabled() -> bool:
    v = os.environ.get("PDF_SKIP_DOTTED_LEADER_HEADINGS", "").strip().lower()
    return v in ("1", "true", "yes")


def _leading_toc_replacement_disabled() -> bool:
    v = os.environ.get("PDF_KEEP_LEADING_TOC", "").strip().lower()
    return v in ("1", "true", "yes")


def _dedupe_chapter_h2_disabled() -> bool:
    v = os.environ.get("PDF_SKIP_DEDUPE_CHAPTER_H2", "").strip().lower()
    return v in ("1", "true", "yes")


def _all_caps_headings_disabled() -> bool:
    v = os.environ.get("PDF_SKIP_ALL_CAPS_HEADINGS", "").strip().lower()
    return v in ("1", "true", "yes")


def _stacked_h2_tables_disabled() -> bool:
    v = os.environ.get("PDF_SKIP_STACKED_H2_TABLES", "").strip().lower()
    return v in ("1", "true", "yes")


def _remove_standalone_page_disabled() -> bool:
    v = os.environ.get("PDF_SKIP_REMOVE_STANDALONE_PAGE", "").strip().lower()
    return v in ("1", "true", "yes")


def _demote_non_chapter_h2_disabled() -> bool:
    v = os.environ.get("PDF_SKIP_DEMOTE_NON_CHAPTER_H2", "").strip().lower()
    return v in ("1", "true", "yes")


def _join_soft_wraps_disabled() -> bool:
    v = os.environ.get("PDF_SKIP_JOIN_SOFT_WRAPS", "").strip().lower()
    return v in ("1", "true", "yes")


def _reference_table_promote_disabled() -> bool:
    v = os.environ.get("PDF_SKIP_REFERENCE_TABLE_PROMOTE", "").strip().lower()
    return v in ("1", "true", "yes")


# --- M&M / similar RPG reference blocks → markdown pipe tables (final pass, after soft-wrap join) ---

_CFT_VOLUME_END = re.compile(
    r"(?:\(cft\.\)|(?<!\w)cft\.?|million\s+cft|billion\s+cft)\s*$",
    re.I,
)

# If the volume cell "starts" with these, we are splitting too early (distance leaked into volume).
_BAD_VOLUME_FIRST_TOKEN = frozenset(
    """
    feet foot inches inch mile miles yards yard meters metres meter
    kilometres kilometers km cm mm micron microns nautical
    """.split()
)


def _looks_like_plain_all_caps_heading(s: str) -> bool:
    """True for lines like ``VOLUME`` / ``TABLE`` — letters all upper, no digits, no lowercase."""
    t = s.strip()
    if len(t) < 2:
        return False
    if any(ch.islower() for ch in t) or any(ch.isdigit() for ch in t):
        return False
    letters = [ch for ch in t if ch.isalpha()]
    if len(letters) < 2:
        return False
    return all(ch.isupper() for ch in letters)


def _volume_cell_ok(vol: str) -> bool:
    """
    Volume column text can mix digits, symbols, punctuation, and mixed-case words.
    Reject only: empty, all-caps heading-like labels, or splits where volume starts with a
    distance-only unit word (wrong boundary).
    Rows still end like ``… cft.`` / ``… million cft`` (Measurements Table domain).
    """
    svol = vol.strip()
    if not svol:
        return False
    if _looks_like_plain_all_caps_heading(svol):
        return False
    if not _CFT_VOLUME_END.search(svol):
        return False
    first = svol.split()[0]
    w0 = re.sub(r"^[^\w]+|[^\w]+$", "", first).casefold()
    if w0 in _BAD_VOLUME_FIRST_TOKEN:
        return False
    return True


def _split_distance_volume_row(line: str) -> tuple[str, str] | None:
    """Split imperial distance / volume for Measurements Table rows (``… cft.``)."""
    s = line.strip()
    if not s:
        return None
    low = s.casefold()
    if "cft" not in low and "million" not in low:
        return None
    parts = s.split()
    if len(parts) < 2:
        return None
    for k in range(1, len(parts)):
        vol = " ".join(parts[k:])
        if _volume_cell_ok(vol):
            dist = " ".join(parts[:k])
            if len(dist) >= 2:
                return dist, vol
    return None


def _try_promote_measurements_table(lines: list[str], i: int) -> tuple[int, list[str]] | None:
    """
    ``(MEASUREMENTS|MENTS) TABLE`` + DISTANCE + VOLUME + rows until a non-measurement line.
    Idempotent: skips if already ``#### Measurements Table``.
    """
    if i + 2 >= len(lines):
        return None
    t0 = lines[i].strip()
    if t0.startswith("####") and "measurements" in t0.casefold():
        return None
    if not re.match(r"^(?:MEASUREMENTS|MENTS) TABLE\s*$", t0, re.I):
        return None
    if lines[i + 1].strip() != "DISTANCE" or lines[i + 2].strip() != "VOLUME":
        return None
    j = i + 3
    body: list[str] = []
    while j < len(lines):
        raw = lines[j]
        if not raw.strip():
            # PDF soft-wrap can insert a blank line mid-table; continue if next line parses
            if j + 1 < len(lines) and _split_distance_volume_row(lines[j + 1]) is not None:
                j += 1
                continue
            break
        pair = _split_distance_volume_row(raw)
        if pair is None:
            break
        body.append(pair)
        j += 1
    if len(body) < 5:
        return None
    out_lines = [
        "#### Measurements Table (distance and volume)",
        "",
        "| Distance | Volume |",
        "|----------|--------|",
    ]
    for dist, vol in body:
        out_lines.append(f"| {_md_escape_table_cell(dist)} | {_md_escape_table_cell(vol)} |")
    out_lines.append("")
    return j, out_lines


def _try_promote_opposed_check_examples(lines: list[str], i: int) -> tuple[int, list[str]] | None:
    """OPPOSED CHECK EXAMPLES + TASK/SKILL/OPPOSED BY + triplets until DEGREES OF SUCCESS."""
    if lines[i].strip() != "OPPOSED CHECK EXAMPLES":
        return None
    if i + 3 >= len(lines):
        return None
    if (
        lines[i + 1].strip() != "TASK"
        or lines[i + 2].strip() != "SKILL"
        or lines[i + 3].strip() != "OPPOSED BY"
    ):
        return None
    j = i + 4
    rows: list[tuple[str, str, str]] = []
    while j + 2 < len(lines):
        a, b, c = lines[j].strip(), lines[j + 1].strip(), lines[j + 2].strip()
        if a.startswith("DEGREES OF SUCCESS") or (not a and not b):
            break
        if not a:
            break
        rows.append((a, b, c))
        j += 3
    if len(rows) < 3:
        return None
    out_lines = [
        "#### Opposed check examples",
        "",
        "| Task | Skill | Opposed by |",
        "|------|-------|------------|",
    ]
    for a, b, c in rows:
        out_lines.append(
            f"| {_md_escape_table_cell(a)} | {_md_escape_table_cell(b)} | {_md_escape_table_cell(c)} |"
        )
    out_lines.append("")
    return j, out_lines


def _norm_dc_token(s: str) -> str:
    return (
        s.replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
        .strip()
    )


_EXPECTED_DEGREE_DC = ("DC+15", "DC+10", "DC+5", "DC", "DC-5", "DC-10", "DC-15", "DC-20")


def _try_promote_degrees_success_failure(lines: list[str], i: int) -> tuple[int, list[str]] | None:
    """DEGREES OF SUCCESS AND FAILURE … DC+15 … eight (DC, degree, number) triplets."""
    if lines[i].strip() != "DEGREES OF SUCCESS AND FAILURE":
        return None
    j = i + 1
    # Skip broken multi-line headers until first DC+15
    while j < len(lines) and j < i + 25:
        if lines[j].strip() == "DC+15":
            break
        j += 1
    else:
        return None
    triplets: list[tuple[str, str, str]] = []
    k = j
    for expect_dc in _EXPECTED_DEGREE_DC:
        if k + 2 >= len(lines):
            return None
        d0 = _norm_dc_token(lines[k])
        d1 = lines[k + 1].strip()
        d2 = lines[k + 2].strip()
        if _norm_dc_token(d0) != expect_dc:
            return None
        triplets.append((d0, d1, d2))
        k += 3
    out_lines = [
        "#### Degrees of success and failure",
        "",
        "*Example thresholds when DC is 20.*",
        "",
        "| vs DC | Degree | ≥ |",
        "|-------|--------|---|",
    ]
    for dc, deg, num in triplets:
        out_lines.append(
            f"| {_md_escape_table_cell(dc)} | {_md_escape_table_cell(deg)} | {_md_escape_table_cell(num)} |"
        )
    out_lines.append("")
    return k, out_lines


def promote_mnm_reference_tables(text: str) -> str:
    """
    Final pass: promote common *MUTANTS & MASTERMINDS* reference blocks to GFM pipe tables.

    Runs after ``join_soft_wrapped_paragraph_lines`` so distance/volume rows are one line each.
    Safe on bookmark-outline extracts. Disable with ``PDF_SKIP_REFERENCE_TABLE_PROMOTE=1``.
    """
    if _reference_table_promote_disabled():
        return text
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        hit = _try_promote_measurements_table(lines, i)
        if hit is not None:
            end_i, block = hit
            out.extend(block)
            i = end_i
            continue
        hit = _try_promote_opposed_check_examples(lines, i)
        if hit is not None:
            end_i, block = hit
            out.extend(block)
            i = end_i
            continue
        hit = _try_promote_degrees_success_failure(lines, i)
        if hit is not None:
            end_i, block = hit
            out.extend(block)
            i = end_i
            continue
        out.append(lines[i])
        i += 1
    joined = "\n".join(out)
    if text.endswith("\n") and not joined.endswith("\n"):
        joined += "\n"
    return joined


# Many RPG core books open the body with this line after copyright + TOC (search only *after* TOC).
_WELCOME_BODY_START = re.compile(r"(?im)^WELCOME TO\b")


def _fallback_first_long_prose_line_start(text: str, search_from: int) -> int | None:
    """
    First line at least ~120 chars, not a markdown heading, not mostly ALL CAPS — typical of
    real intro paragraph when ``WELCOME TO`` is absent.
    """
    tail = text[search_from:]
    offset = 0
    for line in tail.splitlines(keepends=True):
        s = line.strip()
        if not s:
            offset += len(line)
            continue
        if len(s) < 120:
            offset += len(line)
            continue
        if s.startswith("#"):
            offset += len(line)
            continue
        letters = [c for c in s if c.isalpha()]
        if len(letters) < 40:
            offset += len(line)
            continue
        upper = sum(1 for c in letters if c.isupper())
        if upper / len(letters) > 0.75:
            offset += len(line)
            continue
        return search_from + offset
    return None


def replace_leading_table_of_contents_block(text: str) -> str:
    """
    Replace the PDF's front ``TABLE OF CONTENTS`` region with a short stub.

    Runs **before** dotted-leader → ``###`` promotion so TOC rows are not turned into fake
    headings. Removes from the ``TABLE OF CONTENTS`` line through the line before real body
    text (``WELCOME TO`` or first long prose line).
    """
    if _leading_toc_replacement_disabled():
        return text
    m = re.search(r"(?im)^TABLE OF CONTENTS\s*$", text)
    if not m:
        return text
    after_toc = text[m.end() :]
    welcome = _WELCOME_BODY_START.search(after_toc)
    if welcome is not None:
        start_body = m.end() + welcome.start()
    else:
        start_body = _fallback_first_long_prose_line_start(text, m.end())
    if start_body is None:
        return text
    stub = (
        "## Table of contents\n\n"
        "*The PDF table of contents (section titles and page numbers) is omitted; "
        "use the headings in the body below for navigation.*\n\n"
    )
    return text[: m.start()] + stub + text[start_body:]


# ``Title ........ 113`` → title + page (used for chapter/appendix cleanup too)
_DOT_LEADER_PAGE = re.compile(r"^(.+?)\s*\.{2,}\s*(\d+)\s*$")


def strip_dot_leader_page_label(s: str) -> str:
    """
    Turn ``CHAPTER 4: SKILLS ........... 113`` into ``CHAPTER 4: SKILLS 113``.

    Keeps page reference as a trailing number (not dot leaders). No-op if no match.
    """
    m = _DOT_LEADER_PAGE.match(s.strip())
    if not m:
        return s
    return f"{m.group(1).strip()} {m.group(2)}"


def promote_dotted_leader_section_lines(text: str) -> str:
    """
    Promote ``Section title ........ page`` stubs to ``###`` headings **with page number**.

    Typical of PDF TOC and rulebook bodies where subsections use dot leaders to page
    numbers. Emits ``### Title 42`` so structure stays in headings—not a pipe table.
    Lines that look like ``CHAPTER n…``, ``APPENDIX …``, or ``PART …`` are
    left unchanged so ``promote_regex_section_headings`` can emit ``##`` / ``###``.
    """
    rx = re.compile(r"^([ \t]*)(.+?)\s*\.{2,}\s*(\d+)\s*$")
    part_start = re.compile(
        r"^PART\s+(?:ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|[IVXLC]+|\d+)\b",
        re.IGNORECASE,
    )
    out: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            out.append(line)
            continue
        m = rx.match(line.rstrip())
        if not m:
            out.append(line)
            continue
        indent, title = m.group(1), m.group(2).strip()
        if len(title) < 4 or len(title) > 200:
            out.append(line)
            continue
        if re.match(r"^CHAPTER\s+\d+", title, re.I):
            out.append(line)
            continue
        if re.match(r"^APPENDIX\s+\S", title, re.I):
            out.append(line)
            continue
        if part_start.match(title):
            out.append(line)
            continue
        page = m.group(3)
        out.append(f"{indent}### {title} {page}")
    joined = "\n".join(out)
    if text.endswith("\n") and not joined.endswith("\n"):
        joined += "\n"
    return joined


def _expand_pdf_duplicate_chapter_banners(stripped: str) -> list[str]:
    """
    Many PDFs glue the chapter title, a duplicate running-header echo, and body on one line::

        CHAPTER 3: ABILITIES CHAPTER 3: ABILITIES Everyone has.

    Only the **first** ``CHAPTER N: <title>`` is the chapter heading (e.g. ``CHAPTER 3: ABILITIES``).
    The second ``CHAPTER 3: ABILITIES`` is not a separate section—it is dropped and the text
    after it (``Everyone has.``) becomes normal prose on the next line.

    Split on repeated ``CHAPTER n:`` markers; when a segment repeats the same banner plus body,
    strip the repeated banner prefix. The first segment alone is promoted to ``##`` by the caller.
    """
    s = stripped.strip()
    if not re.match(r"^CHAPTER\s+\d+\s*:", s, re.I):
        return [stripped]
    parts = re.split(r"\s+(?=CHAPTER\s+\d+\s*:)", s)
    first = parts[0].strip()
    out: list[str] = [first]
    for seg in parts[1:]:
        seg = seg.strip()
        if seg.startswith(first + " "):
            out.append(seg[len(first) :].strip())
        else:
            out.append(seg)
    return [x for x in out if x]


def promote_regex_section_headings(text: str) -> str:
    """
    Promote plain lines that look like section labels (not already markdown headings).

    Conservative: ``CHAPTER n…``, ``APPENDIX …``, ``PART ONE|TWO|…|roman|digit`` on a
    single line, max length 160 (not applied to lines that start with ``CHAPTER`` /
    ``APPENDIX`` so PDF glue lines are not skipped). Skips lines that already start
    with ``#``.
    """
    out: list[str] = []
    part_re = re.compile(
        r"^PART\s+(?:ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN"
        r"|[IVXLC]+|\d+)\b",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            out.append(line)
            continue
        indent = line[: len(line) - len(line.lstrip())]

        if re.match(r"^CHAPTER\s+\d+", s, re.I):
            for piece in _expand_pdf_duplicate_chapter_banners(s):
                ps = piece.strip()
                if re.match(r"^CHAPTER\s+\d+", ps, re.I):
                    out.append(f"{indent}## {strip_dot_leader_page_label(ps)}")
                else:
                    out.append(f"{indent}{piece}")
            continue

        if len(s) > 160:
            out.append(line)
            continue
        if re.match(r"^APPENDIX\s+\S", s, re.IGNORECASE):
            out.append(f"{indent}## {strip_dot_leader_page_label(s)}")
            continue
        if part_re.match(s):
            out.append(f"{indent}### {strip_dot_leader_page_label(s)}")
            continue
        out.append(line)
    joined = "\n".join(out)
    if text.endswith("\n") and not joined.endswith("\n"):
        joined += "\n"
    return joined


_H2_CHAPTER_APPENDIX = re.compile(
    r"^(\s*)##\s+((?:CHAPTER|APPENDIX)\s+.+)$",
    re.IGNORECASE,
)


def _normalize_structure_h2_key(title: str) -> str:
    """Normalize for comparing duplicate running-header ``## CHAPTER …`` / ``## APPENDIX …``."""
    return re.sub(r"\s+", " ", title.strip()).upper()


def collapse_duplicate_structure_h2_lines(text: str) -> str:
    """
    Drop repeated identical ``## CHAPTER …`` / ``## APPENDIX …`` lines (PDF running headers).

    Skips a line when its normalized title equals the last *kept* ``## CHAPTER …`` or
    ``## APPENDIX …`` (running header repeat). When the title changes (e.g. Chapter 2), the
    new heading is emitted.
    """
    lines = text.splitlines()
    out: list[str] = []
    last_key: str | None = None
    for line in lines:
        m = _H2_CHAPTER_APPENDIX.match(line.rstrip())
        if m:
            key = _normalize_structure_h2_key(m.group(2))
            if last_key is not None and key == last_key:
                continue
            last_key = key
        out.append(line)
    joined = "\n".join(out)
    if text.endswith("\n") and not joined.endswith("\n"):
        joined += "\n"
    return joined


# Standalone margin / section labels (ALL CAPS) — exclude known book-title and credit strips.
_ALL_CAPS_HEADING_DENY = frozenset(
    {
        "mutants & masterminds",
        "deluxe hero's handbook",
        "deluxe heros handbook",
        "third edition",
        "green ronin publishing",
        "printed in the usa",
        "interior art",
        "cover art",
        "writing and design",
        "editing and development",
        "adventure design",
        "publisher",
        "playtesters",
        "special thanks",
        "email",
        "web site",
        "web sites",
        "introduction",
        "table of contents",
    }
)


def _normalize_for_deny_compare(stripped: str) -> str:
    """Lowercase and normalize Unicode apostrophes so ``HERO'S`` matches deny ``hero's``."""
    t = stripped.lower().strip()
    for u, a in ("\u2019", "'"), ("\u2018", "'"), ("\u2032", "'"):
        t = t.replace(u, a)
    return t


def _line_is_all_caps_label(stripped: str) -> bool:
    if len(stripped) < 4 or len(stripped) > 120:
        return False
    if stripped.startswith(("#", "-", "•", "*", "|", ">")):
        return False
    letters = [c for c in stripped if c.isalpha()]
    if len(letters) < 3:
        return False
    if not all(c.isupper() for c in letters):
        return False
    if len(stripped.split()) > 12:
        return False
    low = _normalize_for_deny_compare(stripped)
    if low in _ALL_CAPS_HEADING_DENY:
        return False
    # Chapter / appendix / part already handled by regex promotion
    if re.match(r"^(CHAPTER|APPENDIX|PART)\b", stripped, re.I):
        return False
    if "HTTP://" in stripped.upper() or "WWW." in stripped.upper():
        return False
    return True


def _all_caps_to_title_case(s: str) -> str:
    """``ADVANTAGES`` → ``Advantages``; ``THINGS TO KNOW ABOUT MEASUREMENTS`` → title case."""
    return " ".join(w[:1].upper() + w[1:].lower() if w else w for w in s.split())


def promote_all_caps_section_headings(text: str) -> str:
    """
    Promote short standalone ALL CAPS lines to ``###`` headings (title case).

    Typical of rulebook chapter intros: ``ABILITIES``, ``SKILLS``, ``ADVANTAGES`` as plain lines
    before body paragraphs. Use ``###`` so chapters stay ``## CHAPTER n`` / ``## APPENDIX`` and
    in-chapter sections nest under them. Conservative denylist skips book titles, credits, and
    lines that already match ``CHAPTER`` / ``APPENDIX`` / ``PART`` (handled elsewhere).
    """
    out: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            out.append(line)
            continue
        if s.startswith("#"):
            out.append(line)
            continue
        if not _line_is_all_caps_label(s):
            out.append(line)
            continue
        indent = line[: len(line) - len(line.lstrip())]
        title = _all_caps_to_title_case(s)
        out.append(f"{indent}### {title}")
    joined = "\n".join(out)
    if text.endswith("\n") and not joined.endswith("\n"):
        joined += "\n"
    return joined


# After the first ``## CHAPTER n`` / ``## APPENDIX``, MarkItDown ``##`` subsection titles become ``###``.
_H2_CHAPTER_OR_APPENDIX = re.compile(
    r"^(\s*)##\s+(CHAPTER\s+\d+|APPENDIX)\b",
    re.IGNORECASE,
)
_H2_LINE = re.compile(r"^(\s*)##\s+(.+)$")


def demote_non_chapter_h2_to_h3(text: str) -> str:
    """
    After the first ``## CHAPTER`` / ``## APPENDIX`` line, rewrite other ``##`` lines to ``###``.

    Keeps book structure: chapters and appendices at ``##``, in-chapter sections at ``###``.
    Front matter before the first chapter anchor is left unchanged (multiple ``##`` allowed).
    """
    if _demote_non_chapter_h2_disabled():
        return text
    lines = text.splitlines()
    out: list[str] = []
    seen_chapter_anchor = False
    for line in lines:
        if _H2_CHAPTER_OR_APPENDIX.match(line.strip()):
            seen_chapter_anchor = True
            out.append(line)
            continue
        if not seen_chapter_anchor:
            out.append(line)
            continue
        m = _H2_LINE.match(line)
        if m:
            indent, rest = m.group(1), m.group(2).strip()
            out.append(f"{indent}### {rest}")
        else:
            out.append(line)
    joined = "\n".join(out)
    if text.endswith("\n") and not joined.endswith("\n"):
        joined += "\n"
    return joined


def _is_structural_or_special_line(line: str) -> bool:
    """Lines that must not be merged with neighbors (markdown or layout)."""
    s = line.strip()
    if not s:
        return True
    if s.startswith("•"):
        return True
    if s.startswith("#"):
        return True
    if s.startswith("|"):
        return True
    if s.startswith("```"):
        return True
    if re.match(r"^>\s", s):
        return True
    if re.match(r"^[-*+]\s+", s):
        return True
    if re.match(r"^\d{1,4}[.)]\s+", s):
        return True
    if re.match(r"^Page\s+\d+\s*$", s, re.I):
        return True
    if re.match(r"^[-*]{3,}\s*$", s):
        return True
    return False


def _first_alpha_index(s: str) -> int | None:
    for i, c in enumerate(s):
        if c.isalpha():
            return i
    return None


def _looks_like_pdf_metadata_field_line(s: str) -> bool:
    """RPG/stat block lines (Action: … • Range: …) — do not glue to adjacent lines."""
    t = s.strip()
    if not t:
        return False
    if "•" in t and ":" in t:
        return True
    return bool(
        re.match(
            r"(?i)^(action|range|duration|cost|defense|save|dc|speed|initiative|attack|skills)\s*:",
            t,
        )
    )


def _looks_like_standalone_page_number_line(s: str) -> bool:
    """A line that is only a page number (common PDF footer extract)."""
    return bool(re.match(r"^\d{1,4}\s*$", s.strip()))


def _volume_measurement_cell_completed(pl: str) -> bool:
    """True when this line ends a distance/volume cell (volume often ``… cft.`` or ``(cft.)``)."""
    ps = pl.rstrip()
    if ps.endswith(")"):
        return True
    return bool(re.search(r"(?i)cft\.?\s*$", ps))


def _looks_like_following_distance_row_start(nl: str) -> bool:
    """Next line starts a new distance column (another row), not a wrapped fragment."""
    t = nl.strip()
    if not t:
        return False
    return bool(
        re.match(
            r"(?i)^(\d+,?\d*|\d+/\d+|1/2)\s*(feet|foot|inch|inches|mile|miles)\b",
            t,
        )
    ) or bool(re.match(r"(?i)^\d+/\d+\s*mile", t))


def _should_join_soft_wrap(prev: str, nxt: str) -> bool:
    """
    True when ``nxt`` is likely a PDF line-wrap continuation of ``prev`` (same paragraph).

    **Conservative:** merge when the next line starts with a lowercase letter (usual wrapped
    sentence), when the previous line ends with ``,``, ``;``, or ``:`` (mid-clause), or when
    the previous line ends with a hyphen (syllable hyphenation) and the next part continues
    the word. We **do not** merge every non-sentence-ending line with a capitalized next
    line — that glues measurement tables, cells ending in ``(cft.)``, banners, and columns.

    Skips markdown structure, ALL CAPS margin strips, adjacent full measurement rows (volume
    cell complete, next line starts a new distance), and metadata stat lines.
    """
    if _is_structural_or_special_line(prev) or _is_structural_or_special_line(nxt):
        return False
    pl = prev.rstrip()
    nl = nxt.strip()
    if not pl or not nl:
        return False
    if _is_probable_running_header_or_footer_line(nl) or _is_probable_running_header_or_footer_line(pl):
        return False
    if len(pl) > 1200 or len(nl) > 1200:
        return False
    if _looks_like_pdf_metadata_field_line(pl) or _looks_like_pdf_metadata_field_line(nl):
        return False
    if _looks_like_standalone_page_number_line(pl) or _looks_like_standalone_page_number_line(nl):
        return False
    # Two full table rows: "30 feet … (cft.)" then "60 feet …" — do not glue.
    if _volume_measurement_cell_completed(pl) and _looks_like_following_distance_row_start(nl):
        return False
    if pl[-1] in ",;:":
        return True
    # Table cells and many labels end with ")"; "(cft.)" was incorrectly continued before.
    if pl.endswith(")"):
        return False
    if re.search(r"[.!?]['\"]?\s*$", pl):
        return False
    i = _first_alpha_index(nl)
    if i is None:
        return False
    # Wrapped line continues with lowercase (includes "tenta-" + "cles" / "ef-" + "fect").
    return nl[i].islower()


def _join_soft_wrap_pair(prev: str, nxt: str) -> str:
    pl = prev.rstrip()
    nl = nxt.lstrip()
    # Line-break hyphenation: "ef-" + "fect" → "effect" (not "ef- fect")
    if pl.endswith("-") and not pl.endswith("--"):
        return pl[:-1].rstrip() + nl
    return pl + " " + nl


def join_soft_wrapped_paragraph_lines(text: str) -> str:
    """
    Join consecutive non-empty lines that are plain prose when the PDF used a hard line break
    inside one paragraph (no blank line between).

    Adobe / pdfminer often emit one physical line per layout line. Continuations are merged when
    the next line starts with a lowercase letter, when the previous line ends with ``,``, ``;``,
    or ``:``, when the previous line ends with a hyphen (hyphenation), or after ``)`` / sentence
    ends we stop so full table rows and ``(cft.)`` cells are not glued across rows. Blank lines separate
    paragraphs. Headings, lists, ``•`` bullets, code fences, ALL CAPS
    strips, stat lines, and standalone page numbers are not merged with neighbors.

    Disable with ``PDF_SKIP_JOIN_SOFT_WRAPS=1``.
    """
    if _join_soft_wraps_disabled():
        return text
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            out.append(line)
            i += 1
            continue
        cur = line
        i += 1
        while i < n:
            nxt = lines[i]
            if not nxt.strip():
                break
            if _should_join_soft_wrap(cur, nxt):
                cur = _join_soft_wrap_pair(cur, nxt)
                i += 1
            else:
                break
        out.append(cur)
    joined = "\n".join(out)
    if text.endswith("\n") and not joined.endswith("\n"):
        joined += "\n"
    return joined


def _md_escape_table_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()


# Book chapter/appendix titles must stay as ``##`` headings — never as pipe-table column headers.
_CHAPTER_OR_APPENDIX_HEADING_TITLE = re.compile(r"(?i)^(CHAPTER\s+\d+|APPENDIX)\b")


def _looks_like_chapter_or_appendix_heading_title(title: str) -> bool:
    """True if ``title`` is a real chapter/appendix line (must not merge into stacked tables)."""
    t = title.strip()
    if not t:
        return False
    return bool(_CHAPTER_OR_APPENDIX_HEADING_TITLE.match(t))


def _is_section_break_h2(line: str) -> bool:
    """Long ``##`` titles end a stacked table (body sections, not column labels).

    Short titles are up to **three** words / ~44 chars so PDF table column headers like
    ``## Degrees Of Success`` still count as labels, not body sections.
    """
    s = line.strip()
    if not s.startswith("## ") or s.startswith("###"):
        return False
    title = s[3:].strip()
    if not title:
        return False
    ws = title.split()
    return len(ws) > 3 or len(title) > 44


def _plain_stacked_column_title(line: str) -> str | None:
    """Single-line column labels often extracted without ``##`` (e.g. ``d20``, ``Archetype``)."""
    s = line.strip()
    if re.match(r"^d20\s*$", s, re.I):
        return "d20"
    if s.casefold() == "archetype":
        return "Archetype"
    return None


def _short_h2_stacked_column_title(line: str) -> str | None:
    """``## Foo`` / ``## Foo Bar Baz`` as column headers; longer ``##`` lines are section breaks."""
    s = line.strip()
    if not s.startswith("## ") or s.startswith("###"):
        return None
    title = s[3:].strip()
    if not title:
        return None
    ws = title.split()
    if len(ws) > 3 or len(title) > 44:
        return None
    if _looks_like_chapter_or_appendix_heading_title(title):
        return None
    return title


def _stacked_column_header_title(line: str) -> str | None:
    p = _plain_stacked_column_title(line)
    if p is not None:
        return p
    return _short_h2_stacked_column_title(line)


def remove_standalone_page_lines(text: str) -> str:
    """
    Remove lines that are only ``Page`` (case-insensitive).

    PDF table columns often insert a ``Page`` spacer line between roll/name and page numbers.
    """
    out: list[str] = []
    for line in text.splitlines():
        if line.strip().casefold() == "page":
            continue
        out.append(line)
    joined = "\n".join(out)
    if text.endswith("\n") and not joined.endswith("\n"):
        joined += "\n"
    return joined


def _try_parse_stacked_column_table(
    lines: list[str],
    start: int,
    *,
    min_rows: int,
    min_cols: int,
    max_header_len: int = 80,
) -> tuple[int, str] | None:
    """
    Vertical column stacks → pipe table: ``## Mass`` / plain ``d20`` / ``Archetype`` / short ``##``.

    Stops at long ``## Section Title`` (not a column label). Later columns cap at the first
    column's row count and skip prose until the next column or section heading.
    """
    if start >= len(lines):
        return None
    t0 = _stacked_column_header_title(lines[start])
    if not t0 or len(t0) > max_header_len:
        return None
    if _looks_like_chapter_or_appendix_heading_title(t0):
        return None
    pos = start + 1
    vals0: list[str] = []
    while pos < len(lines):
        line = lines[pos]
        if _is_section_break_h2(line):
            return None
        if _stacked_column_header_title(line) is not None:
            break
        s = line.strip()
        if s:
            vals0.append(s)
        pos += 1
    n0 = len(vals0)
    if n0 < min_rows:
        return None
    columns: list[tuple[str, list[str]]] = [(t0, vals0)]
    while pos < len(lines):
        if _is_section_break_h2(lines[pos]):
            break
        t = _stacked_column_header_title(lines[pos])
        if t is None:
            break
        if _looks_like_chapter_or_appendix_heading_title(t):
            return None
        if len(t) > max_header_len:
            break
        header_line_idx = pos
        pos += 1
        vals: list[str] = []
        while (
            pos < len(lines)
            and len(vals) < n0
            and not _is_section_break_h2(lines[pos])
            and _stacked_column_header_title(lines[pos]) is None
        ):
            s = lines[pos].strip()
            if s:
                vals.append(s)
            pos += 1
        while pos < len(lines) and not _is_section_break_h2(lines[pos]):
            if _stacked_column_header_title(lines[pos]) is not None:
                break
            pos += 1
        if len(vals) != n0:
            pos = header_line_idx
            break
        columns.append((t, vals))
    if len(columns) < min_cols:
        return None
    headers = [c[0] for c in columns]
    rows = list(zip(*(c[1] for c in columns)))
    out_lines: list[str] = []
    out_lines.append("| " + " | ".join(_md_escape_table_cell(h) for h in headers) + " |")
    out_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        out_lines.append("| " + " | ".join(_md_escape_table_cell(x) for x in row) + " |")
    return pos, "\n".join(out_lines)


def _try_parse_h2_header_block_row_major_table(
    lines: list[str],
    start: int,
    *,
    min_rows: int,
    min_cols: int,
    max_header_len: int = 80,
) -> tuple[int, str] | None:
    """
    All short column ``##`` titles stacked first, then cell text in **row-major** order.

    Some PDFs emit ``## Action``, ``## Range``, … with only blank lines between, then
    each row's cells left-to-right (``Instant``, ``Varies``, … for row 1, then the next row).

    If the first title is multi-word (e.g. ``## Power Effects``) and the following titles
    are single-word column names, the first title is kept as a ``##`` caption above the table.
    """
    pos = start
    while pos < len(lines) and not lines[pos].strip():
        pos += 1
    if pos >= len(lines) or _stacked_column_header_title(lines[pos]) is None:
        return None
    headers: list[str] = []
    while pos < len(lines):
        t = _stacked_column_header_title(lines[pos])
        if t is None:
            break
        if len(t) > max_header_len:
            return None
        if _looks_like_chapter_or_appendix_heading_title(t):
            return None
        headers.append(t)
        pos += 1
        while pos < len(lines) and not lines[pos].strip():
            pos += 1
    if len(headers) < min_cols:
        return None
    caption: str | None = None
    if (
        len(headers) >= min_cols + 1
        and len(headers[0].split()) > 1
        and all(len(h.split()) == 1 for h in headers[1:])
    ):
        caption = headers[0]
        headers = headers[1:]
    if len(headers) < min_cols:
        return None
    k = len(headers)
    vals: list[str] = []
    while pos < len(lines):
        line = lines[pos]
        if _is_section_break_h2(line):
            break
        st = line.strip()
        if not st:
            pos += 1
            continue
        if _stacked_column_header_title(line) is not None:
            break
        vals.append(st)
        pos += 1
    if not vals:
        return None
    rem = len(vals) % k
    if rem != 0:
        drop_partial = os.environ.get("PDF_STACKED_ROW_MAJOR_DROP_PARTIAL", "1").strip().lower() not in (
            "0",
            "false",
            "no",
        )
        if drop_partial:
            trimmed = vals[:-rem]
            if len(trimmed) >= k * min_rows:
                vals = trimmed
        if len(vals) % k != 0:
            return None
    n = len(vals) // k
    if n < min_rows:
        return None
    out_parts: list[str] = []
    if caption:
        out_parts.append(f"## {caption}")
        out_parts.append("")
    out_lines: list[str] = []
    out_lines.append("| " + " | ".join(_md_escape_table_cell(h) for h in headers) + " |")
    out_lines.append("| " + " | ".join(["---"] * k) + " |")
    for i in range(n):
        row = [vals[i * k + j] for j in range(k)]
        out_lines.append("| " + " | ".join(_md_escape_table_cell(x) for x in row) + " |")
    out_parts.append("\n".join(out_lines))
    return pos, "\n".join(out_parts)


def promote_stacked_h2_column_tables(text: str) -> str:
    """
    Merge stacked column blocks (``##`` and/or plain ``d20`` / ``Archetype``) into pipe tables.

    PDF tables often extract as vertical columns with blank lines; standalone ``Page`` lines
    should be removed via ``remove_standalone_page_lines`` first.

    Tries **per-column then values** (vertical strips) first, then **all headers then
    row-major values** (``## Action`` … ``## Cost`` then each row left-to-right).
    """
    try:
        min_rows = max(2, int(os.environ.get("PDF_STACKED_TABLE_MIN_ROWS", "2")))
    except ValueError:
        min_rows = 2
    try:
        min_cols = max(2, int(os.environ.get("PDF_STACKED_TABLE_MIN_COLS", "2")))
    except ValueError:
        min_cols = 2
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        parsed = _try_parse_stacked_column_table(
            lines, i, min_rows=min_rows, min_cols=min_cols
        )
        if parsed is not None:
            end_i, table_md = parsed
            if out and out[-1].strip():
                out.append("")
            out.append(table_md)
            i = end_i
            continue
        parsed2 = _try_parse_h2_header_block_row_major_table(
            lines, i, min_rows=min_rows, min_cols=min_cols
        )
        if parsed2 is not None:
            end_i, table_md = parsed2
            if out and out[-1].strip():
                out.append("")
            out.append(table_md)
            i = end_i
            continue
        out.append(lines[i])
        i += 1
    joined = "\n".join(out)
    if text.endswith("\n") and not joined.endswith("\n"):
        joined += "\n"
    return joined


_OUTLINE_BOOKMARK_EXTRACT_PREFIX = "<!-- PDF: extracted from bookmark outline"


def _is_outline_bookmark_extract(text: str) -> bool:
    """True when markdown came from ``pdf_outline_extract`` (bookmark-structured body)."""
    return text.lstrip().startswith(_OUTLINE_BOOKMARK_EXTRACT_PREFIX)


def postprocess_pdf_markdown(text: str, pdf_path: Path | None = None) -> str:
    """
    Apply generic PDF markdown normalizations.

    When ``pdf_path`` is set (the source ``.pdf``), runs optional outline alignment
    if PyMuPDF is installed (see ``pdf_outline_headings``). Outline injection runs early
    (after leading TOC replacement), before stacked-column table promotion, so chapter
    lines are not absorbed into pipe tables first.

    **Bookmark-outline extracts** (see ``pdf_outline_extract``) already embed structure;
    running TOC replacement, re-injecting outline headings, or stacked-``##`` table promotion
    on that text corrupts it. Those sources get banner dedupe, soft-wrap join, then
    ``promote_mnm_reference_tables`` (pipe tables for known M&M reference blocks).
    """
    if _is_outline_bookmark_extract(text):
        t = collapse_consecutive_duplicate_banner_lines(text)
        t = join_soft_wrapped_paragraph_lines(t)
        if not _reference_table_promote_disabled():
            t = promote_mnm_reference_tables(t)
        return t
    t = collapse_consecutive_duplicate_banner_lines(text)
    if not _leading_toc_replacement_disabled():
        t = replace_leading_table_of_contents_block(t)
    # Phase 1: map PDF bookmarks to ## lines while chapter titles are still plain lines.
    if pdf_path is not None:
        from pdf_outline_headings import inject_pdf_outline_headings

        t = inject_pdf_outline_headings(pdf_path, t)
    # Phase 2: dotted leaders, regex headings, dedupe, caps, page noise — then tables.
    if not _dotted_leader_promotion_disabled():
        t = promote_dotted_leader_section_lines(t)
    if not _regex_promotion_disabled():
        t = promote_regex_section_headings(t)
    if not _dedupe_chapter_h2_disabled():
        t = collapse_duplicate_structure_h2_lines(t)
    if not _all_caps_headings_disabled():
        t = promote_all_caps_section_headings(t)
    if not _remove_standalone_page_disabled():
        t = remove_standalone_page_lines(t)
    if not _stacked_h2_tables_disabled():
        t = promote_stacked_h2_column_tables(t)
    if not _demote_non_chapter_h2_disabled():
        t = demote_non_chapter_h2_to_h3(t)
    t = join_soft_wrapped_paragraph_lines(t)
    if not _reference_table_promote_disabled():
        t = promote_mnm_reference_tables(t)
    return t
