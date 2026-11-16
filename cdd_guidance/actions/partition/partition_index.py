"""Partition root index resource - `{subject}-index.md` plus its config."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from cdd_guidance.actions.partition.segment import MIN_ENTRY_BODY_CHARS, SegmentCompletenessConfig

_PARTITION_CONFIG = re.compile(
    r"<!--\s*partition-config\s*\n(.*?)-->",
    re.IGNORECASE | re.DOTALL,
)
# The partition-config block's YAML settings, by their hyphenated names (``min-body-chars``, ``non-entry-headers``,
# ``short-body-pattern``).
type PartitionSettings = dict[str, object]


class PartitionIndex:
    """The shared partition index at ``{root}/.context/{subject}-index.md``, where root is the partition's out_root, else
    the session's root. Its ``<!-- partition-config -->`` block, when it has one, sets how its segments are checked."""

    def __init__(self, path: Path, text: str) -> None:
        self._path = path
        self._text = text
        self._settings = self._config_settings()
        self._completeness = SegmentCompletenessConfig(
            min_body_chars=self._min_body_chars(),
            non_entry_headers=self._non_entry_headers(),
            short_body_pattern=self._short_body_pattern(),
        )

    @classmethod
    def at(cls, path: Path) -> PartitionIndex | None:
        """The index kept in the file at path, read from it; none when there is no file there."""
        if not path.is_file():
            return None
        resolved = path.resolve()
        return cls(resolved, resolved.read_text(encoding="utf-8", errors="replace"))

    @classmethod
    def near(cls, segment_path: Path) -> PartitionIndex | None:
        """The index a segment file belongs to: the first ``.context/*-index.md`` found walking up from the segment;
        none when no folder above it holds one."""
        start = segment_path.parent
        if start.name == ".context":
            start = start.parent
        for folder in [start, *start.parents]:
            context_dir = folder / ".context"
            if not context_dir.is_dir():
                continue
            indexes = sorted(context_dir.glob("*-index.md"))
            if indexes:
                return cls.at(indexes[0])
        return None

    @property
    def path(self) -> Path:
        return self._path

    @property
    def text(self) -> str:
        return self._text

    @property
    def completeness(self) -> SegmentCompletenessConfig:
        return self._completeness

    def _config_settings(self) -> PartitionSettings:
        """The settings the index's partition-config block names, as YAML; none when it has no block."""
        match = _PARTITION_CONFIG.search(self._text)
        if not match:
            return {}
        loaded = yaml.safe_load(match.group(1))
        return loaded if isinstance(loaded, dict) else {}

    def _non_entry_headers(self) -> frozenset[str]:
        listed = self._settings.get("non-entry-headers", [])
        if isinstance(listed, str):
            parts = re.split(r"[\n|,;]+", listed)
        else:
            parts = list(listed or [])
        return frozenset(
            str(part).upper().strip() for part in parts if str(part).strip()
        )

    def _short_body_pattern(self) -> re.Pattern[str] | None:
        pattern = self._settings.get("short-body-pattern")
        if not pattern:
            return None
        return re.compile(str(pattern), re.I)

    def _min_body_chars(self) -> int:
        chars = self._settings.get("min-body-chars", MIN_ENTRY_BODY_CHARS)
        try:
            return int(chars)
        except (TypeError, ValueError):
            return MIN_ENTRY_BODY_CHARS
