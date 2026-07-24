"""Named-entry completeness for partitioned ``*-segment.md`` chunks.

Used by tool ``verify_segment_completeness``. Span length alone is a false PASS.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_EXPECTED_BLOCK = re.compile(
    r"<!--\s*expected-entries\s*\n(.*?)-->",
    re.IGNORECASE | re.DOTALL,
)
_EXPECTED_INLINE = re.compile(
    r"<!--\s*expected-entries:\s*(.+?)-->",
    re.IGNORECASE | re.DOTALL,
)
_ALL_CAPS = re.compile(r"^[A-Z][A-Z0-9 /'\-]{1,60}$")
_SKIP_CAPS = frozenset(
    {
        "MUTANTS & MASTERMINDS",
        "CHAPTER 6: POWERS",
        "DELUXE HERO’S HANDBOOK",
        "DELUXE HERO'S HANDBOOK",
        "NAME",
        "COST",
        "DESCRIPTION",
        "EXTRAS",
        "FLAWS",
        "SHAPE",
        "SINGLE TARGET",
        "MULTIPLE TARGETS",
        "COVERING ATTACK",
        "DYNAMIC ALTERNATE EFFECT",
        "PARTIALLY LIMITED",
        "REMOVABLE POINT VALUE",
        "REMOVABLE AND DAMAGE",
    }
)


@dataclass(frozen=True)
class EntryResult:
    name: str
    status: str  # OK | MISSING_HEADER | STUB
    body_chars: int


def has_expected_entries_marker(text: str) -> bool:
    return bool(_EXPECTED_BLOCK.search(text) or _EXPECTED_INLINE.search(text))


def parse_expected_names(text: str) -> list[str]:
    block = _EXPECTED_BLOCK.search(text)
    if block:
        return _split_names(block.group(1))
    inline = _EXPECTED_INLINE.search(text)
    if inline:
        return _split_names(inline.group(1))
    return _split_names(text)


def _split_names(raw: str) -> list[str]:
    names: list[str] = []
    for part in re.split(r"[\n|,;]+", raw):
        name = part.strip().strip("-").strip()
        if not name or name.startswith("#"):
            continue
        names.append(name)
    seen: set[str] = set()
    out: list[str] = []
    for name in names:
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(name)
    return out


def check_named_entries(
    segment_text: str,
    expected_names: list[str],
    *,
    min_body_chars: int = 120,
) -> list[EntryResult]:
    lines = segment_text.splitlines()
    results: list[EntryResult] = []
    for name in expected_names:
        header = name.upper().strip()
        idxs = [i for i, line in enumerate(lines) if line.strip() == header]
        if not idxs:
            results.append(EntryResult(name, "MISSING_HEADER", 0))
            continue
        start = idxs[0] + 1
        body_end = len(lines)
        for j in range(start, len(lines)):
            cand = lines[j].strip()
            if not cand:
                continue
            if (
                _ALL_CAPS.match(cand)
                and cand not in _SKIP_CAPS
                and not re.fullmatch(r"\d{2,3}", cand)
                and cand != header
            ):
                body_end = j
                break
        body = "\n".join(lines[start:body_end]).strip()
        n = len(body)
        results.append(
            EntryResult(name, "OK" if n >= min_body_chars else "STUB", n)
        )
    return results


def format_report(
    segment_path: str,
    results: list[EntryResult],
    *,
    min_body_chars: int = 120,
) -> str:
    ok = sum(1 for r in results if r.status == "OK")
    total = len(results)
    incomplete = total - ok
    overall = "PASS" if incomplete == 0 and total > 0 else "FAIL"
    lines = [
        f"segment: {segment_path}",
        f"min_body_chars: {min_body_chars}",
        f"completeness: {overall} ({ok}/{total} OK, {incomplete} incomplete)",
        "note: span length alone is a false PASS — named-entry completeness is required",
        "",
        "| Entry | Status | Body chars |",
        "|-------|--------|------------|",
    ]
    for r in results:
        if r.status != "OK":
            lines.append(f"| {r.name} | {r.status} | {r.body_chars} |")
    if incomplete == 0 and total > 0:
        lines.append(f"| — | (all expected entries) | OK | ≥{min_body_chars} |")
    if overall == "FAIL":
        lines += [
            "",
            "HARD FAIL: do not lock story inventory from this chunk.",
            "Repair the segment (re-extract / re-OCR) until completeness PASS.",
        ]
    return "\n".join(lines) + "\n"
