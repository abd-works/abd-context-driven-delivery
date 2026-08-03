"""Partition root index resource - `{subject}-index.md` plus its config."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from partition.segment import SegmentCompletenessConfig

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
    def resolve_near(cls, segment_path: str | Path) -> Path | None:
        """Walk up from a segment file to session ``.context/*-index.md``."""
        path = Path(segment_path)
        start = path.parent
        if start.name == ".context":
            start = start.parent
        for folder in [start, *start.parents]:
            context_dir = folder / ".context"
            if not context_dir.is_dir():
                continue
            indexes = sorted(context_dir.glob("*-index.md"))
            if indexes:
                return indexes[0].resolve()
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

    @property
    def non_entry_headers(self) -> frozenset[str]:
        return self._completeness.non_entry_headers

    @property
    def short_body_pattern(self) -> re.Pattern[str] | None:
        return self._completeness.short_body_pattern

    @property
    def min_body_chars(self) -> int:
        return self._completeness.min_body_chars

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
        chars_raw = raw.get("min-body-chars", 120)
        try:
            return int(chars_raw)
        except (TypeError, ValueError):
            return 120
