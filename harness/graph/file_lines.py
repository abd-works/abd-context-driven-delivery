"""FileLines. The lines of each source file a graph build reads, read from disk once per build."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from enum import Enum
from pathlib import Path


class PathKind(Enum):
    FILE = "file"
    FOLDER = "folder"
    MISSING = "missing"


_READ: ContextVar[dict[str, tuple[PathKind, list[str]]] | None] = ContextVar("harness_graph_file_lines", default=None)


class FileLines:
    """The lines at a path as a graph build reads them: a file's lines, or a folder's code files' lines, each file's
    after a ``// path`` line naming it from the folder; none when nothing is there. Inside ``during_build`` each path is
    looked at and read from disk once, and every node's *Source* there answers from those lines; when the build ends
    they are dropped, so the next build, such as a refresh after the file changed, reads it as it is then. Outside a
    build every call reads the disk again. The lines answered are shared: a reader slices or copies them and never
    changes them."""

    FOLDER_SUFFIXES = frozenset({".ts", ".tsx", ".js", ".py"})

    @staticmethod
    @contextmanager
    def during_build() -> Iterator[None]:
        """Keep each path's lines while the block runs; a build nested inside another shares its lines."""
        if _READ.get() is not None:
            yield
            return
        token = _READ.set({})
        try:
            yield
        finally:
            _READ.reset(token)

    @staticmethod
    def of(path: Path) -> list[str]:
        """The lines at path."""
        return FileLines._at(path)[1]

    @staticmethod
    def kind(path: Path) -> PathKind:
        """Whether path is a file, a folder, or not there."""
        return FileLines._at(path)[0]

    @staticmethod
    def _at(path: Path) -> tuple[PathKind, list[str]]:
        kept = _READ.get()
        if kept is None:
            return FileLines._read(path)
        key = str(path)
        if key not in kept:
            kept[key] = FileLines._read(path)
        return kept[key]

    @staticmethod
    def _read(path: Path) -> tuple[PathKind, list[str]]:
        if path.is_file():
            return PathKind.FILE, path.read_text(encoding="utf-8").splitlines()
        if not path.is_dir():
            return PathKind.MISSING, []
        lines: list[str] = []
        for inside in sorted(path.rglob("*")):
            if inside.suffix.lower() in FileLines.FOLDER_SUFFIXES and FileLines.kind(inside) is PathKind.FILE:
                lines.append(f"// {inside.relative_to(path).as_posix()}")
                lines.extend(FileLines.of(inside))
        return PathKind.FOLDER, lines
