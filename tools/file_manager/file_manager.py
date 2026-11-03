"""The session's file manager: lists and reads the files under a session's roots, so every application shows files the
same way instead of each object growing a read operation of its own.

A session's roots are its workpath: the folder each of its practices works in, as its `session.json` records it, or the
practice's default folder when it records none. The session's own folder under `.sessions/` is not one of them."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, TypedDict

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.destination import SourceFile, language_adapter
from harness.mcp.mcp_server import mcp


class PathOutsideRootsError(ValueError):
    """A path outside every root of the session, which a page may name but never reach."""

    def __init__(self, path: str) -> None:
        super().__init__(f"{path} is outside the session's roots")


class SessionFileNotFoundError(FileNotFoundError):
    """A path inside the session's roots that names no file or folder."""

    def __init__(self, path: str) -> None:
        super().__init__(f"no file or folder {path} in the session's roots")


class FileManagerData(TypedDict):
    workpath: str
    roots: list[str]


class FolderEntryData(TypedDict):
    name: str
    path: str
    is_folder: bool
    size: int


class FolderData(TypedDict):
    folder: str
    entries: list[FolderEntryData]


class FileTextData(TypedDict):
    path: Annotated[str, SourceFile]
    text: str


@language_adapter(language="typescript")
@agent_toolset
class FileManager:
    """List and read the files under the current session's roots, the folders its practices work in."""

    # The session owns its file manager in memory; it keeps nothing but the roots it reads.

    def __init__(self, workpath: Path | str, roots: tuple[Path, ...]) -> None:
        self._workpath = Path(workpath).resolve()
        self._roots = tuple(Path(root).resolve() for root in roots)

    @classmethod
    @tool_subject
    def current(cls) -> FileManager:
        """The file manager of the session being worked on."""
        from space.session import Session

        return Session.current().file_manager

    @property
    def workpath(self) -> Path:
        return self._workpath

    @property
    def roots(self) -> tuple[Path, ...]:
        return self._roots

    @mcp
    @agent_tool
    @noSessionLog
    def list(self, folder: str = "") -> FolderData:
        """List the entries of folder, a path from the session's workpath (the workpath when empty) inside one of its roots: folders first, then files, each with its path and size."""
        target = self._inside(folder)
        if not target.is_dir():
            raise SessionFileNotFoundError(folder)
        entries = sorted(target.iterdir(), key=lambda entry: (not entry.is_dir(), entry.name.lower()))
        return {"folder": self._relative(target), "entries": [self._entry(entry) for entry in entries]}

    @mcp
    @agent_tool
    @noSessionLog
    def read(self, path: str) -> FileTextData:
        """Return the text of path, a file inside one of the session's roots, named from its workpath."""
        target = self._inside(path)
        if not target.is_file():
            raise SessionFileNotFoundError(path)
        return {"path": self._relative(target), "text": target.read_text(encoding="utf-8", errors="replace")}

    def to_json(self) -> FileManagerData:
        return {"workpath": str(self._workpath), "roots": [str(root) for root in self._roots]}

    def _inside(self, path: str) -> Path:
        """The path resolved from the workpath; a page names paths, so one outside every root is refused."""
        target = (self._workpath / path).resolve()
        if not any(target == root or root in target.parents for root in self._roots):
            raise PathOutsideRootsError(path)
        return target

    def _relative(self, target: Path) -> str:
        """The path from the workpath, so a chosen root outside it reads back as `../reports/...`."""
        return "" if target == self._workpath else Path(os.path.relpath(target, self._workpath)).as_posix()

    def _entry(self, entry: Path) -> FolderEntryData:
        is_folder = entry.is_dir()
        return {"name": entry.name, "path": self._relative(entry), "is_folder": is_folder, "size": 0 if is_folder else entry.stat().st_size}
