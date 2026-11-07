"""Partition root index resource - `{subject}-index.md` plus its config."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from cdd_guidance.actions.partition.segment import MIN_ENTRY_BODY_CHARS, SegmentCompletenessConfig

_PARTITION_CONFIG = re.compile(
    r"<!--\s*partition-config\s*\n(.*?)-->",
    re.IGNORECASE | re.DOTALL,
)


class PartitionIndex:
    """The shared partition index at ``{session.path}/.context/{subject}-index.md``."""

    def __init__(
        self,
        path: Path,
        text: str,
        completeness: SegmentCompletenessConfig,
    ) -> None:
        self._path = path
        self._text = text
        self._completeness = completeness

    @classmethod
    def from_text(cls, path: Path, text: str) -> PartitionIndex:
        return cls(path, text, cls._completeness_from_text(text))

    @classmethod
    def at(cls, path: Path) -> PartitionIndex | None:
        """The index kept in the file at path, read from it; none when there is no file there."""
        if not path.is_file():
            return None
        resolved = path.resolve()
        return cls.from_text(resolved, resolved.read_text(encoding="utf-8", errors="replace"))

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

    @classmethod
    def _completeness_from_text(cls, text: str) -> SegmentCompletenessConfig:
        raw = cls._parse_config(text)
        return SegmentCompletenessConfig(
            min_body_chars=cls._min_body_chars(raw),
            non_entry_headers=cls._non_entry_headers(raw),
            short_body_pattern=cls._short_body_pattern(raw),
        )

    @staticmethod
    def _parse_config(text: str) -> dict[str, Any]:
        match = _PARTITION_CONFIG.search(text)
        if not match:
            return {}
        loaded = yaml.safe_load(match.group(1))
        return loaded if isinstance(loaded, dict) else {}

    @staticmethod
    def _non_entry_headers(raw: dict[str, Any]) -> frozenset[str]:
        headers_raw = raw.get("non-entry-headers", [])
        if isinstance(headers_raw, str):
            parts = re.split(r"[\n|,;]+", headers_raw)
        else:
            parts = list(headers_raw or [])
        return frozenset(
            str(part).upper().strip() for part in parts if str(part).strip()
        )

    @staticmethod
    def _short_body_pattern(raw: dict[str, Any]) -> re.Pattern[str] | None:
        pattern_raw = raw.get("short-body-pattern")
        if not pattern_raw:
            return None
        return re.compile(str(pattern_raw), re.I)

    @staticmethod
    def _min_body_chars(raw: dict[str, Any]) -> int:
        chars_raw = raw.get("min-body-chars", MIN_ENTRY_BODY_CHARS)
        try:
            return int(chars_raw)
        except (TypeError, ValueError):
            return MIN_ENTRY_BODY_CHARS
