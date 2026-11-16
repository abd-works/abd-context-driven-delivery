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
# An entry body shorter than this reads as a stub unless the index names a short-body pattern it matches.
MIN_ENTRY_BODY_CHARS = 120
# A shorter body still passes when it is at least this long and matches the index's short-body pattern.
MIN_SHORT_BODY_CHARS = 40
# Where a partition writes each segment under its folder: one folder for each top-level artifact its practice's Scaffold
# names, such as `checks/.context/checks-segment.md`, or `powers/attack/.context/attack-segment.md` for a nested one.
SEGMENT_FILE = "{artifact}/.context/{artifact}-segment.md"
# The glob that finds every segment file a partition wrote under its folder, wherever SEGMENT_FILE placed it.
SEGMENT_FILES = "**/.context/*-segment.md"


@dataclass(frozen=True)
class SegmentCompletenessConfig:
    """Completeness settings loaded from the partition root index; the defaults apply when the index names none."""

    min_body_chars: int = MIN_ENTRY_BODY_CHARS
    non_entry_headers: frozenset[str] = field(default_factory=frozenset)
    short_body_pattern: re.Pattern[str] | None = None




class SegmentEntry:
    """One expected named entry inside a segment chunk."""

    def __init__(
        self,
        name: str,
        body: str | None,
        completeness: SegmentCompletenessConfig,
    ) -> None:
        self._name = name
        self._body = body
        self._completeness = completeness

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
        pattern = self._completeness.short_body_pattern
        short_ok = n >= MIN_SHORT_BODY_CHARS and pattern is not None and bool(pattern.search(self._body))
        if n >= self._completeness.min_body_chars or short_ok:
            return "OK"
        return "STUB"

    @property
    def is_complete(self) -> bool:
        return self.status == "OK"


class Segment:
    """A partitioned ``*-segment.md`` chunk on disk (or in memory). Its expected entries are the ones its
    ``<!-- expected-entries -->`` marker names, unless the caller names them instead."""

    _FAIL_FOOTER = (
        "",
        "HARD FAIL: do not lock story inventory from this chunk.",
        "Repair the segment (re-extract / re-OCR) until completeness PASS.",
    )

    def __init__(self, path: Path, text: str, completeness: SegmentCompletenessConfig) -> None:
        self._path = path
        self._text = text
        self._completeness = completeness
        self._expected_names = self._names_from_marker()

    @classmethod
    def at(cls, path: Path, completeness: SegmentCompletenessConfig, expected_names: str = "") -> Segment:
        """The segment kept in the file at path, read from it and checked with completeness."""
        resolved = path.resolve()
        text = resolved.read_text(encoding="utf-8", errors="replace")
        return cls.from_text(resolved, text, completeness, expected_names=expected_names)

    @classmethod
    def from_text(
        cls,
        path: Path,
        text: str,
        completeness: SegmentCompletenessConfig,
        *,
        expected_names: str = "",
    ) -> Segment:
        """Build a segment from already-loaded text; expected_names, when given, replace the names its marker lists."""
        segment = cls(path, text, completeness)
        if expected_names.strip():
            segment._expected_names = segment._split_names(expected_names)
        return segment

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
    def expected_names(self) -> list[str]:
        return list(self._expected_names)

    @property
    def has_expected_names(self) -> bool:
        return bool(self._expected_names)

    def entries(self) -> list[SegmentEntry]:
        lines = self._content_lines
        return [self._entry_for(name, lines) for name in self._expected_names]

    @property
    def is_complete(self) -> bool:
        return self._passes(self.entries())

    def completeness_report(self) -> str:
        if not self.has_expected_names:
            return (
                f"segment: {self._path}\n"
                "completeness: FAIL\n"
                "error: no expected_names argument and no "
                "<!-- expected-entries --> marker in segment\n"
            )
        entries = self.entries()
        lines = self._report_header(entries)
        lines.extend(self._report_table_lines(entries))
        if not self._passes(entries):
            lines.extend(self._FAIL_FOOTER)
        return "\n".join(lines) + "\n"

    def _passes(self, entries: list[SegmentEntry]) -> bool:
        """A segment passes when it has entries and every one is complete."""
        return bool(entries) and all(entry.is_complete for entry in entries)

    def _report_header(self, entries: list[SegmentEntry]) -> list[str]:
        complete = sum(1 for entry in entries if entry.is_complete)
        overall = "PASS" if self._passes(entries) else "FAIL"
        return [
            f"segment: {self._path}",
            f"min_body_chars: {self._completeness.min_body_chars}",
            f"completeness: {overall} ({complete}/{len(entries)} OK, {len(entries) - complete} incomplete)",
            "note: span length alone is a false PASS - named-entry completeness is required",
            "",
            "| Entry | Status | Body chars |",
            "|-------|--------|------------|",
        ]

    def _entry_for(self, name: str, lines: list[str]) -> SegmentEntry:
        header = name.upper().strip()
        idxs = [i for i, line in enumerate(lines) if line.strip() == header]
        if not idxs:
            return SegmentEntry(name, None, self._completeness)
        body = self._body_after_header(lines, idxs[0], header)
        return SegmentEntry(name, body, self._completeness)

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
            candidate in self._completeness.non_entry_headers
            or candidate == current_header
        ):
            return False
        if re.fullmatch(r"\d{2,3}", candidate):
            return False
        return True

    def _report_table_lines(self, entries: list[SegmentEntry]) -> list[str]:
        table_lines = [
            f"| {entry.name} | {entry.status} | {entry.body_chars} |"
            for entry in entries
            if not entry.is_complete
        ]
        if self._passes(entries):
            table_lines.append(
                f"| - | (all expected entries) | OK | "
                f">={self._completeness.min_body_chars} |"
            )
        return table_lines

    def _names_from_marker(self) -> list[str]:
        block = _EXPECTED_BLOCK.search(self._text)
        if block:
            return self._split_names(block.group(1))
        inline = _EXPECTED_INLINE.search(self._text)
        if inline:
            return self._split_names(inline.group(1))
        return []

    @property
    def _content_lines(self) -> list[str]:
        """The segment's lines with its HTML comments, such as the expected-entries marker, taken out."""
        return _HTML_COMMENT.sub("", self._text).splitlines()

    def _split_names(self, listed: str) -> list[str]:
        """The distinct names a marker or argument lists, split on newlines, bars, commas and semicolons; a repeat
        that differs only in case is dropped."""
        names: list[str] = []
        for part in re.split(r"[\n|,;]+", listed):
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
