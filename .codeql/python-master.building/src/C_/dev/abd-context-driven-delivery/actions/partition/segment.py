"""Partition segment resource - a ``*-segment.md`` chunk and its named entries."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_EXPECTED_BLOCK = re.compile(
    r"<!--\s*expected-entries\s*\n(.*?)-->",
    re.IGNORECASE | re.DOTALL,
)
_EXPECTED_INLINE = re.compile(
    r"<!--\s*expected-entries:\s*(.+?)-->",
    re.IGNORECASE | re.DOTALL,
)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_ALL_CAPS = re.compile(r"^[A-Z][A-Z0-9 /'\-]{1,60}$")


@dataclass(frozen=True)
class SegmentCompletenessConfig:
    """Completeness knobs loaded from the partition root index (not kit defaults)."""

    min_body_chars: int = 120
    non_entry_headers: frozenset[str] = field(default_factory=frozenset)
    short_body_pattern: re.Pattern[str] | None = None


class SegmentEntry:
    """One expected named entry inside a segment chunk."""

    def __init__(
        self,
        name: str,
        body: str | None,
        config: SegmentCompletenessConfig,
    ) -> None:
        self._name = name
        self._body = body
        self._config = config

    @property
    def name(self) -> str:
        return self._name

    @property
    def body(self) -> str | None:
        return self._body

    @property
    def body_chars(self) -> int:
        return 0 if self._body is None else len(self._body)

    @property
    def status(self) -> str:
        if self._body is None:
            return "MISSING_HEADER"
        n = len(self._body)
        pattern = self._config.short_body_pattern
        short_ok = n >= 40 and pattern is not None and bool(pattern.search(self._body))
        if n >= self._config.min_body_chars or short_ok:
            return "OK"
        return "STUB"

    @property
    def is_complete(self) -> bool:
        return self.status == "OK"


class Segment:
    """A partitioned ``*-segment.md`` chunk on disk (or in memory)."""

    def __init__(
        self,
        path: Path,
        text: str,
        config: SegmentCompletenessConfig,
        *,
        expected_names: list[str] | None = None,
    ) -> None:
        self._path = path
        self._text = text
        self._config = config
        self._expected_names = (
            list(expected_names)
            if expected_names is not None
            else self._names_from_marker(text)
        )

    @classmethod
    def from_text(
        cls,
        path: Path,
        text: str,
        config: SegmentCompletenessConfig,
        *,
        expected_names: str = "",
    ) -> Segment:
        """Build a segment from already-loaded text."""
        names = (
            cls._split_names(expected_names) if expected_names.strip() else None
        )
        return cls(path, text, config, expected_names=names)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def text(self) -> str:
        return self._text

    @property
    def config(self) -> SegmentCompletenessConfig:
        return self._config

    @property
    def expected_names(self) -> list[str]:
        return list(self._expected_names)

    @property
    def has_expected_names(self) -> bool:
        return bool(self._expected_names)

    def entries(self) -> list[SegmentEntry]:
        lines = self._content_lines(self._text)
        return [self._entry_for(name, lines) for name in self._expected_names]

    @property
    def is_complete(self) -> bool:
        found = self.entries()
        return bool(found) and all(entry.is_complete for entry in found)

    def completeness_report(self) -> str:
        if not self.has_expected_names:
            return (
                f"segment: {self._path}\n"
                "completeness: FAIL\n"
                "error: no expected_names argument and no "
                "<!-- expected-entries --> marker in segment\n"
            )
        entries = self.entries()
        ok_count = sum(1 for entry in entries if entry.is_complete)
        total = len(entries)
        incomplete = total - ok_count
        overall = "PASS" if incomplete == 0 and total > 0 else "FAIL"
        lines = self._report_header(overall, ok_count, total, incomplete)
        lines.extend(self._report_rows(entries, incomplete, total))
        if overall == "FAIL":
            lines.extend(self._fail_footer())
        return "\n".join(lines) + "\n"

    def _report_header(
        self, overall: str, ok_count: int, total: int, incomplete: int
    ) -> list[str]:
        return [
            f"segment: {self._path}",
            f"min_body_chars: {self._config.min_body_chars}",
            (
                f"completeness: {overall} "
                f"({ok_count}/{total} OK, {incomplete} incomplete)"
            ),
            "note: span length alone is a false PASS - named-entry completeness is required",
            "",
            "| Entry | Status | Body chars |",
            "|-------|--------|------------|",
        ]

    @staticmethod
    def _fail_footer() -> list[str]:
        return [
            "",
            "HARD FAIL: do not lock story inventory from this chunk.",
            "Repair the segment (re-extract / re-OCR) until completeness PASS.",
        ]

    def _entry_for(self, name: str, lines: list[str]) -> SegmentEntry:
        header = name.upper().strip()
        idxs = [i for i, line in enumerate(lines) if line.strip() == header]
        if not idxs:
            return SegmentEntry(name, None, self._config)
        body = self._body_after_header(lines, idxs[0], header)
        return SegmentEntry(name, body, self._config)

    def _body_after_header(
        self, lines: list[str], header_index: int, header: str
    ) -> str:
        start = header_index + 1
        body_end = len(lines)
        for index in range(start, len(lines)):
            candidate = lines[index].strip()
            if candidate and self._is_entry_header(candidate, header):
                body_end = index
                break
        return "\n".join(lines[start:body_end]).strip()

    def _is_entry_header(self, candidate: str, current_header: str) -> bool:
        if not _ALL_CAPS.match(candidate):
            return False
        if (
            candidate in self._config.non_entry_headers
            or candidate == current_header
        ):
            return False
        if re.fullmatch(r"\d{2,3}", candidate):
            return False
        return True

    def _report_rows(
        self, entries: list[SegmentEntry], incomplete: int, total: int
    ) -> list[str]:
        rows = [
            f"| {entry.name} | {entry.status} | {entry.body_chars} |"
            for entry in entries
            if not entry.is_complete
        ]
        if incomplete == 0 and total > 0:
            rows.append(
                f"| - | (all expected entries) | OK | "
                f">={self._config.min_body_chars} |"
            )
        return rows

    @classmethod
    def _names_from_marker(cls, text: str) -> list[str]:
        block = _EXPECTED_BLOCK.search(text)
        if block:
            return cls._split_names(block.group(1))
        inline = _EXPECTED_INLINE.search(text)
        if inline:
            return cls._split_names(inline.group(1))
        return []

    @staticmethod
    def _content_lines(segment_text: str) -> list[str]:
        return _HTML_COMMENT.sub("", segment_text).splitlines()

    @staticmethod
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
