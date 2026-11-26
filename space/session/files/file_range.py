"""Lines of one file and the text they hold: what a file comment, a fold, and a violation each sit on."""

from __future__ import annotations

from typing import Annotated

from harness.installation.data_class import SourceFile, data_field


class LineSpan:
    """Lines start_line to end_line of a file, counted from 1, both included."""

    def __init__(self, start_line: int, end_line: int) -> None:
        self.start_line = start_line
        self.end_line = end_line


class Range:
    """Lines start_line to end_line of one file, named from the project, and the text those lines held when the range
    was taken."""

    def __init__(self, path: str, span: LineSpan, content: str) -> None:
        self._path = path
        self._span = span
        self._content = content

    @classmethod
    def of_text(cls, path: str, text: str, span: LineSpan) -> Range:
        """The lines span names of text, the whole of path; lines past its end hold nothing."""
        lines = text.splitlines()
        return cls(path, span, "\n".join(lines[span.start_line - 1 : span.end_line]))

    @property
    @data_field
    def path(self) -> Annotated[str, SourceFile]:
        return self._path

    @property
    @data_field
    def start_line(self) -> int:
        return self._span.start_line

    @property
    @data_field
    def end_line(self) -> int:
        return self._span.end_line

    @property
    @data_field
    def content(self) -> str:
        return self._content

    @property
    @data_field
    def anchor(self) -> str:
        """Where the range is, such as src/checkout/order.py:L12-L14."""
        return f"{self._path}:L{self.start_line}-L{self.end_line}"

    @property
    def quoted(self) -> list[str]:
        """Each line of the range marked > with its number, as a chat reads lines it is shown: `> 12 |     def place`."""
        return [f"> {self.start_line + offset} | {line}" for offset, line in enumerate(self._content.splitlines())]

    @property
    def context(self) -> str:
        """The range as a chat's context: the file and its lines, then each line quoted."""
        return "\n".join([f"{self._path}:{self.start_line}-{self.end_line}", *self.quoted])
