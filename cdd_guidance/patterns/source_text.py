"""One source file's text as a pattern's graph facts read it."""

from __future__ import annotations

import re


class SourceText:
    """The text of one file a pattern overlay reads, and where each match sits in it: rules report a finding by its line,
    so every fact a pattern records names the line its match starts on."""

    def __init__(self, text: str) -> None:
        self.text = text

    def line_of(self, index: int) -> int:
        """The line, counted from 1, holding the character at index."""
        return self.text.count("\n", 0, index) + 1

    def hits(self, pattern: re.Pattern[str]) -> list[list]:
        """[line, matched code] for each match of pattern."""
        return [[self.line_of(match.start()), match.group(0).strip()] for match in pattern.finditer(self.text)]
