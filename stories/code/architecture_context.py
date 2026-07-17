"""Read testing tiers from a project's `architecture-context.md`.

The reference testing architecture declares a project's tiers (e.g. `server`,
`client`, `e2e`, `domain`) in prose form inside its own architecture-context
doc. This module extracts them so the code-emission pipeline knows which
`<slug>-<tier>.<ext>` file pairs to scaffold.

Detection order:

1. Prose scan — look for lines like "Tiers: server, client, e2e, domain" or
   a bullet block naming tier participants under an "Tiers" heading.
2. Filesystem fallback — if no prose declaration is found, walk `tests-root`
   and infer tiers from existing `<slug>-<tier>.<ext>` filenames. This keeps
   the pipeline useful before a project has authored its arch context.

Returns an ordered tuple of tier slugs. Duplicate declarations collapse
first-mentioned-wins.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple


_KNOWN_TIER_HINTS = (
    "server", "client", "e2e", "domain", "api", "web", "unit", "integration",
    "ui", "browser", "cli", "mobile", "playwright",
)

_TIER_LINE = re.compile(
    r"^\s*[-*]?\s*(?:tiers?|testing\s+tiers?)\s*[:=]\s*(.+)$",
    re.IGNORECASE,
)
_TIER_BULLET = re.compile(r"^\s*[-*]\s+`?(?P<tier>[a-z][a-z0-9-]{1,20})`?\b")

_SPEC_FILE_TIER_RE = re.compile(r"^[a-z0-9-]+-(?P<tier>[a-z][a-z0-9]{0,20})\.(?:ts|tsx|js|py|java)$")
_TEST_FILE_TIER_RE = re.compile(r"^[a-z0-9-]+-(?P<tier>[a-z][a-z0-9]{0,20})\.test\.(?:ts|tsx|js|py|java)$")


def read_tiers(
    architecture_context_path: Optional[Path],
    *,
    tests_root: Optional[Path] = None,
) -> Tuple[str, ...]:
    """Return the ordered tuple of tier slugs for a project.

    - `architecture_context_path` is the project's `architecture-context.md`
      (typically at `docs/architecture/<n>-<phase>/architecture-context.md`
      or similar). If provided and exists, it is scanned first.
    - `tests_root` is the folder that would hold `<slug>-<tier>.<ext>` files
      when no prose declaration is present.
    """
    if architecture_context_path is not None and architecture_context_path.exists():
        tiers = _read_from_prose(architecture_context_path.read_text(encoding="utf-8"))
        if tiers:
            return tiers

    if tests_root is not None and tests_root.exists():
        return _infer_from_filesystem(tests_root)

    return ()


def _read_from_prose(text: str) -> Tuple[str, ...]:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = _TIER_LINE.match(line)
        if not m:
            continue
        return _split_tier_list(m.group(1))

    # No "Tiers: ..." line — try a bulleted block under a "Testing tiers" heading.
    heading_re = re.compile(r"^#+\s+.*tiers?\b", re.IGNORECASE)
    for i, line in enumerate(lines):
        if not heading_re.match(line):
            continue
        collected: list[str] = []
        for j in range(i + 1, len(lines)):
            raw = lines[j]
            if raw.startswith("#"):
                break
            m = _TIER_BULLET.match(raw)
            if not m:
                if raw.strip() == "" or raw.startswith(" ") or raw.startswith("\t"):
                    continue
                if raw.strip() and not raw.startswith("-") and not raw.startswith("*"):
                    break
                continue
            tier = m.group("tier").lower()
            if tier in _KNOWN_TIER_HINTS or _looks_like_tier(tier):
                collected.append(tier)
        if collected:
            return _dedupe_ordered(collected)
    return ()


def _split_tier_list(raw: str) -> Tuple[str, ...]:
    parts = re.split(r"[,/|]+|\s+and\s+|\s{2,}", raw)
    cleaned = []
    for p in parts:
        slug = p.strip().strip("`*_").lower()
        if not slug:
            continue
        slug = slug.split()[0]  # drop trailing prose
        if _looks_like_tier(slug):
            cleaned.append(slug)
    return _dedupe_ordered(cleaned)


def _looks_like_tier(candidate: str) -> bool:
    return bool(re.fullmatch(r"[a-z][a-z0-9-]{1,20}", candidate))


def _dedupe_ordered(items: Iterable[str]) -> Tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return tuple(ordered)


def _infer_from_filesystem(tests_root: Path) -> Tuple[str, ...]:
    tiers: list[str] = []
    for candidate in tests_root.rglob("*"):
        if not candidate.is_file():
            continue
        m = _TEST_FILE_TIER_RE.match(candidate.name)
        if m is None:
            m = _SPEC_FILE_TIER_RE.match(candidate.name)
            if m is None:
                continue
            if m.group("tier") == "stories":
                continue
        tier = m.group("tier").lower()
        if tier == "stories":
            continue
        tiers.append(tier)
    return _dedupe_ordered(tiers)
