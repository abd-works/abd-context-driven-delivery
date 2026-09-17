"""Minimal markdown section helpers for instruction docstring expansion."""
from __future__ import annotations

import re
from pathlib import Path


def _read_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def _markdown_headings(content: str) -> list[tuple[int, int, int, str]]:
    headings: list[tuple[int, int, int, str]] = []
    offset = 0
    fence: str | None = None
    for line in content.splitlines(keepends=True):
        bare = line.rstrip("\r\n")
        fence_match = re.match(r"^\s*(```|~~~)", bare)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
        elif fence is None:
            heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", bare)
            if heading:
                headings.append(
                    (offset, offset + len(bare), len(heading.group(1)), heading.group(2))
                )
        offset += len(line)
    return headings


def _section_exists(file_path: Path, section_heading: str) -> bool:
    if not section_heading:
        return True
    content = _read_file(file_path)
    return any(
        heading.casefold() == section_heading.casefold()
        for _start, _end, _level, heading in _markdown_headings(content)
    )


def _read_section(file_path: Path, section_heading: str) -> str:
    content = _read_file(file_path)
    if not section_heading:
        return content
    headings = _markdown_headings(content)
    found = next(
        (
            (index, item)
            for index, item in enumerate(headings)
            if item[3].casefold() == section_heading.casefold()
        ),
        None,
    )
    if found is None:
        return content
    index, (start, _heading_end, level, _heading) = found
    end = next(
        (position for position, _e, next_level, _h in headings[index + 1 :] if next_level <= level),
        len(content),
    )
    return content[start:end].strip()
