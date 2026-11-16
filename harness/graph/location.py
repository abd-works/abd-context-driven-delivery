"""A place in a file: the file and the first and last of its lines."""

from __future__ import annotations


class Location:
    """Lines line to end_line of one file, named from the folder its reader read it from. A place that names no file
    or no line leaves them out; a place that names one line ends on it."""

    def __init__(self, file: str = "", line: int | None = None, end_line: int | None = None) -> None:
        self._file = file
        self._line = line
        self._end_line = end_line if end_line is not None else line

    @property
    def file(self) -> str:
        return self._file

    @property
    def line(self) -> int | None:
        return self._line

    @property
    def end_line(self) -> int | None:
        return self._end_line

    def moved_to(self, file: str) -> Location:
        """The same lines, of file."""
        return Location(file, self._line, self._end_line)

    def __repr__(self) -> str:
        return f"Location({self._file!r}, {self._line}, {self._end_line})"
