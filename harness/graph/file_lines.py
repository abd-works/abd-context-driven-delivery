"""FileLines. The lines of each source file a graph build reads, read from disk once per build."""

from __future__ import annotations

from contextvars import ContextVar, Token
from enum import Enum
from pathlib import Path
from types import TracebackType


class PathKind(Enum):
    FILE = "file"
    FOLDER = "folder"
    MISSING = "missing"


_READ: ContextVar[dict[str, tuple[PathKind, list[str]]] | None] = ContextVar("harness_graph_file_lines", default=None)


class BuildReads:
    """While a graph build runs (``with BuildReads():``) each path is looked at and read from disk once, and every
    node's *Source* there answers from those lines; when the build ends they are dropped, so the next build, such as a
    refresh after the file changed, reads it as it is then. A build nested inside another shares its lines."""

    def __init__(self) -> None:
        self._token: Token | None = None

    def __enter__(self) -> BuildReads:
        if _READ.get() is None:
            self._token = _READ.set({})
        return self

    def __exit__(self, kind: type[BaseException] | None, error: BaseException | None, trace: TracebackType | None) -> None:
        if self._token is not None:
            _READ.reset(self._token)
            self._token = None


class FileLines:
    """The lines at a path as a graph build reads them: a file's lines, or a folder's code files' lines, each file's
    after a ``// path`` line naming it from the folder; none when nothing is there. Inside a build (*BuildReads*) each
    path is read from disk once; outside one every read goes to the disk again. The lines answered are shared: a reader
    slices or copies them and never changes them."""

    FOLDER_SUFFIXES = frozenset({".ts", ".tsx", ".js", ".py"})

    def __init__(self, path: Path) -> None:
        self.path = path

    @property
    def lines(self) -> list[str]:
        """The lines at the path."""
        return self._at()[1]

    @property
    def kind(self) -> PathKind:
        """Whether the path is a file, a folder, or not there."""
        return self._at()[0]

    def _at(self) -> tuple[PathKind, list[str]]:
        kept = _READ.get()
        if kept is None:
            return self._read()
        key = str(self.path)
        if key not in kept:
            kept[key] = self._read()
        return kept[key]

    def _read(self) -> tuple[PathKind, list[str]]:
        path = self.path
        if path.is_file():
            return PathKind.FILE, path.read_text(encoding="utf-8").splitlines()
        if not path.is_dir():
            return PathKind.MISSING, []
        lines: list[str] = []
        for inside in sorted(path.rglob("*")):
            read = FileLines(inside)
            if inside.suffix.lower() in self.FOLDER_SUFFIXES and read.kind is PathKind.FILE:
                lines.append(f"// {inside.relative_to(path).as_posix()}")
                lines.extend(read.lines)
        return PathKind.FOLDER, lines
