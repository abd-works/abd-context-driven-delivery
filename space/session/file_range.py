"""Lines of one file and the text they hold: what a file comment, a fold, and a violation each sit on."""

from __future__ import annotations

from typing import Annotated

from harness.installation.data_class import SourceFile, data_field


class Range:
    """Lines start_line to end_line of one file, named from the project, and the text those lines held when the range
    was taken."""

    def __init__(self, path: str, start_line: int, end_line: int, content: str) -> None:
        self._path = path
        self._start_line = start_line
        self._end_line = end_line
        self._content = content

    @classmethod
    def of_text(cls, path: str, text: str, start_line: int, end_line: int) -> Range:
        """Lines start_line to end_line of text, the whole of path; lines past its end hold nothing."""
        lines = text.splitlines()
        return cls(path, start_line, end_line, "\n".join(lines[start_line - 1 : end_line]))

    @property
    @data_field
    def path(self) -> Annotated[str, SourceFile]:
        return self._path

    @property
    @data_field
    def start_line(self) -> int:
        return self._start_line

    @property
    @data_field
    def end_line(self) -> int:
        return self._end_line

    @property
    @data_field
    def content(self) -> str:
        return self._content

    @property
    @data_field
    def anchor(self) -> str:
        """Where the range is, such as src/checkout/order.py:L12-L14."""
        return f"{self._path}:L{self._start_line}-L{self._end_line}"

    def contains(self, line: int) -> bool:
        return self._start_line <= line <= self._end_line
