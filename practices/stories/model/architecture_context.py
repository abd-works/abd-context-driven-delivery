"""Read testing tiers from a project's `architecture-context.md`.

The reference testing architecture declares a project's tiers (e.g. `server`,
`client`, `e2e`, `domain`) in prose form inside its own architecture-context
doc. This module extracts them so the code-emission pipeline knows which
`<slug>-<tier>.<ext>` file pairs to scaffold.

Detection order:

1. Prose scan - look for lines like "Tiers: server, client, e2e, domain" or
   a bullet block naming tier participants under an "Tiers" heading.
2. Filesystem fallback - if no prose declaration is found, walk `tests-root`
   and infer tiers from existing `<slug>-<tier>.<ext>` filenames. This keeps
   the pipeline useful before a project has authored its arch context.

Returns an ordered tuple of tier slugs. Duplicate declarations collapse
first-mentioned-wins.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple


class ArchitectureContext:
    _KNOWN_TIER_HINTS = (
        "server", "client", "e2e", "domain", "api", "web", "unit", "integration",
        "ui", "browser", "cli", "mobile", "playwright",
    )

    _TIER_LINE = re.compile(
        r"^\s*[-*]?\s*(?:tiers?|testing\s+tiers?)\s*[:=]\s*(.+)$",
        re.IGNORECASE,
    )
    _TIER_BULLET = re.compile(r"^\s*[-*]\s+`?(?P<tier>[a-z][a-z0-9-]{1,20})`?\b")
    _SPEC_FILE_TIER_RE = re.compile(
        r"^[a-z0-9-]+-(?P<tier>[a-z][a-z0-9]{0,20})\.(?:ts|tsx|js|py|java)$"
    )
    _TEST_FILE_TIER_RE = re.compile(
        r"^[a-z0-9-]+-(?P<tier>[a-z][a-z0-9]{0,20})\.test\.(?:ts|tsx|js|py|java)$"
    )

    def read_tiers(
        self,
        architecture_context_path: Optional[Path],
        tests_root: Optional[Path] = None,
    ) -> Tuple[str, ...]:
        if architecture_context_path is not None and architecture_context_path.exists():
            tiers = self._read_from_prose(architecture_context_path.read_text(encoding="utf-8"))
            if tiers:
                return tiers
        if tests_root is not None and tests_root.exists():
            return self._infer_from_filesystem(tests_root)
        return ()

    def _read_from_prose(self, text: str) -> Tuple[str, ...]:
        lines = text.splitlines()
        for line in lines:
            m = self._TIER_LINE.match(line)
            if m:
                return self._split_tier_list(m.group(1))
        return self._tiers_from_heading(lines)

    def _tiers_from_heading(self, lines: Sequence[str]) -> Tuple[str, ...]:
        heading_re = re.compile(r"^#+\s+.*tiers?\b", re.IGNORECASE)
        for i, line in enumerate(lines):
            if heading_re.match(line):
                collected = self._collect_tier_bullets(lines, i)
                if collected:
                    return self._dedupe_ordered(collected)
        return ()

    def _collect_tier_bullets(self, lines: Sequence[str], heading_index: int) -> list[str]:
        collected: list[str] = []
        for j in range(heading_index + 1, len(lines)):
            raw = lines[j]
            if raw.startswith("#"):
                break
            m = self._TIER_BULLET.match(raw)
            if not m:
                if raw.strip() == "" or raw.startswith(" ") or raw.startswith("\t"):
                    continue
                if raw.strip() and not raw.startswith("-") and not raw.startswith("*"):
                    break
                continue
            tier = m.group("tier").lower()
            if tier in self._KNOWN_TIER_HINTS or self._looks_like_tier(tier):
                collected.append(tier)
        return collected

    def _split_tier_list(self, raw: str) -> Tuple[str, ...]:
        parts = re.split(r"[,/|]+|\s+and\s+|\s{2,}", raw)
        cleaned = []
        for p in parts:
            slug = p.strip().strip("`*_").lower()
            if not slug:
                continue
            slug = slug.split()[0]
            if self._looks_like_tier(slug):
                cleaned.append(slug)
        return self._dedupe_ordered(cleaned)

    def _looks_like_tier(self, candidate: str) -> bool:
        return bool(re.fullmatch(r"[a-z][a-z0-9-]{1,20}", candidate))

    def _dedupe_ordered(self, items: Iterable[str]) -> Tuple[str, ...]:
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            ordered.append(item)
        return tuple(ordered)

    def _infer_from_filesystem(self, tests_root: Path) -> Tuple[str, ...]:
        tiers: list[str] = []
        for candidate in tests_root.rglob("*"):
            if not candidate.is_file():
                continue
            m = self._TEST_FILE_TIER_RE.match(candidate.name)
            if m is None:
                m = self._SPEC_FILE_TIER_RE.match(candidate.name)
                if m is None:
                    continue
                if m.group("tier") == "stories":
                    continue
            tier = m.group("tier").lower()
            if tier == "stories":
                continue
            tiers.append(tier)
        return self._dedupe_ordered(tiers)
