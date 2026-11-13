"""The session's file manager: lists and reads the files under a session's roots, so every application shows files the
same way instead of each object growing a read operation of its own.

A session's roots are its workpath: the folder each of its practices works in, as its `session.json` records it, or the
practice's default folder when it records none. The session's own folder under `.sessions/` is not one of them."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Annotated

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.installation.data_class import SourceFile, data_field, language_adapter
from harness.mcp.mcp_server import mcp


# Installed packages and caches hold no one's work. Hidden folders hold tools and caches too, but a module's .context
# folder holds its models and maps, so a search looks inside it and a person can choose it as a practice root.
UNWORKED_FOLDERS = frozenset({"node_modules", "__pycache__"})
WORKED_HIDDEN_FOLDERS = frozenset({".context"})


def holds_work(folder_name: str) -> bool:
    """Whether a folder of this name can hold someone's work: not installed packages or a cache, and not hidden unless
    it is one of the hidden folders that do, such as .context."""
    return folder_name not in UNWORKED_FOLDERS and (not folder_name.startswith(".") or folder_name in WORKED_HIDDEN_FOLDERS)


class PathOutsideRootsError(ValueError):
    """A path outside every root of the session, which a page may name but never reach."""

    def __init__(self, path: str) -> None:
        super().__init__(f"{path} is outside the session's roots")


class FolderEntry:
    """One entry of a listed folder: a folder or a file, with its path from the workpath and, for a file, its size."""

    def __init__(self, name: str, path: str, is_folder: bool, size: int) -> None:
        self._name = name
        self._path = path
        self._is_folder = is_folder
        self._size = size

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def path(self) -> str:
        return self._path

    @property
    @data_field
    def is_folder(self) -> bool:
        return self._is_folder

    @property
    @data_field
    def size(self) -> int:
        return self._size


class Folder:
    """A listed folder, as a path from the workpath, with its entries."""

    def __init__(self, folder: str, entries: list[FolderEntry]) -> None:
        self._folder = folder
        self._entries = list(entries)

    @property
    @data_field
    def folder(self) -> str:
        return self._folder

    @property
    @data_field
    def entries(self) -> list[FolderEntry]:
        return list(self._entries)

    @property
    def folders(self) -> list[FolderEntry]:
        """Its folders that can hold someone's work, for a person choosing a workpath or a practice root: installed
        packages, caches, and hidden folders other than .context are left out."""
        return [entry for entry in self._entries if entry.is_folder and holds_work(entry.name)]


class FileEntry:
    """One file something declares, such as a fidelity's output, as a path from the project, whether it is there yet,
    and whether the session's branch changed it, which a page filters on."""

    def __init__(self, path: str, exists: bool, is_changed: bool = False) -> None:
        self._path = path
        self._exists = exists
        self._is_changed = is_changed

    @property
    @data_field
    def path(self) -> str:
        return self._path

    @property
    @data_field
    def exists(self) -> bool:
        return self._exists

    @property
    @data_field
    def is_changed(self) -> bool:
        return self._is_changed


# The language a viewer shows a file in, by its suffix; a file of any other suffix is plain text.
LANGUAGES = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".json": "json",
    ".md": "markdown",
    ".drawio": "xml",
    ".html": "html",
    ".css": "css",
    ".yaml": "yaml",
    ".yml": "yaml",
}
PLAIN_TEXT = "plaintext"


class FileText:
    """The text of one file, with its path from the workpath; no text for a file that is not there."""

    def __init__(self, path: str, text: str) -> None:
        self._path = path
        self._text = text

    @property
    @data_field
    def path(self) -> Annotated[str, SourceFile]:
        return self._path

    @property
    @data_field
    def text(self) -> str:
        return self._text

    @property
    @data_field
    def language(self) -> str:
        """The language a viewer shows the text in, from the file's suffix, such as python or markdown."""
        return LANGUAGES.get(Path(self._path).suffix.lower(), PLAIN_TEXT)


@language_adapter(language="typescript", shares_file_views=True)
@agent_toolset
class FileManager:
    """List, read, and save the files under a session's roots, the folders its practices work in."""

    # The session owns its file manager in memory; it keeps nothing but the roots it reads.

    def __init__(self, workpath: Path | str, roots: tuple[Path, ...]) -> None:
        self._workpath = Path(workpath).resolve()
        self._roots = tuple(Path(root).resolve() for root in roots)

    @classmethod
    @tool_subject
    def load(cls, *, call: ToolCall) -> FileManager:
        """The file manager of the session open in the project the call works on. The session owns its file manager, so
        it is read from that session."""
        return call.session.session_files.file_manager

    @property
    @data_field
    def workpath(self) -> Path:
        return self._workpath

    @property
    @data_field
    def roots(self) -> tuple[Path, ...]:
        return self._roots

    @mcp
    @agent_tool
    @noSessionLog
    def list(self, folder: str = "") -> Folder:
        """List the entries of folder, a path from the session's workpath (the workpath when empty) inside one of its roots: folders first, then files, each with its path and size; no entries when the folder is not there, such as one deleted since a page listed it."""
        target = self._inside(folder)
        if not target.is_dir():
            return Folder(self._relative(target), [])
        entries = sorted(target.iterdir(), key=lambda entry: (not entry.is_dir(), entry.name.lower()))
        return Folder(self._relative(target), [self._entry(entry) for entry in entries])

    @mcp
    @agent_tool
    @noSessionLog
    def read(self, path: str) -> FileText:
        """Return the text of path, a file inside one of the session's roots, named from its workpath; no text when the file is not there, such as one deleted since a page listed it."""
        target = self._inside(path)
        text = target.read_text(encoding="utf-8", errors="replace") if target.is_file() else ""
        return FileText(self._relative(target), text)

    @mcp
    @agent_tool
    @noSessionLog
    def write(self, path: str, text: str) -> FileText:
        """Save text as the whole of path, a file inside one of the session's roots, named from its workpath, making its folder when it has none; the file as saved."""
        target = self._inside(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="")
        return FileText(self._relative(target), text)

    def find(self, pattern: str) -> list[Path]:
        """The files pattern names, written from the workpath, in the glob form Path.glob reads: `**/` is any number of
        folders. A pattern that stayed absolute, for a session working outside the repository, searches from its drive."""
        anchor = Path(pattern).anchor
        return self._files_matching(Path(anchor or self._workpath), pattern[len(anchor):])

    def _files_matching(self, start: Path, pattern: str) -> list[Path]:
        """The files under start that pattern names. Installed packages and hidden folders hold no one's work, and
        searching node_modules alone made a pattern take over a second."""
        parts = pattern.split("/")
        fixed = next((index for index, part in enumerate(parts) if set(part) & set("*?")), len(parts))
        # The search starts at the deepest folder the pattern names outright, so a pattern under one folder never walks the drive.
        base = start.joinpath(*parts[:fixed])
        searched = parts[fixed:]
        matching = self._glob_expression("/".join(searched))
        # A pattern without ** names files a fixed number of folders down, so the walk stops there: `*.md` on a large
        # checkout reads its top folder alone instead of every folder in it.
        deepest = None if "**" in searched else len(searched) - 1
        base_text = str(base)
        found = []
        for folder, folders, files in os.walk(base_text):
            # Plain strings here: building a Path for every file in the repository made the search take a second.
            inside = folder[len(base_text):].strip("\\/").replace("\\", "/")
            depth = inside.count("/") + 1 if inside else 0
            folders[:] = [] if deepest is not None and depth >= deepest else [name for name in folders if holds_work(name)]
            found += [Path(folder, name) for name in files if matching.fullmatch(f"{inside}/{name}" if inside else name)]
        return sorted(found)

    def _inside(self, path: str) -> Path:
        """The path resolved from the workpath; a page names paths, so one outside every root is refused."""
        target = (self._workpath / path).resolve()
        if not any(target == root or root in target.parents for root in self._roots):
            raise PathOutsideRootsError(path)
        return target

    def _relative(self, target: Path) -> str:
        """The path from the workpath, so a chosen root outside it reads back as `../reports/...`."""
        return "" if target == self._workpath else Path(os.path.relpath(target, self._workpath)).as_posix()

    def _entry(self, entry: Path) -> FolderEntry:
        is_folder = entry.is_dir()
        return FolderEntry(entry.name, self._relative(entry), is_folder, 0 if is_folder else entry.stat().st_size)

    def _glob_expression(self, pattern: str) -> re.Pattern[str]:
        """A glob pattern as a regular expression over a path written with `/`: `**/` is any number of folders, `*` and
        `?` stay inside one folder, the way Path.glob reads them."""
        parts = re.split(r"(\*\*/|\*\*|\*|\?)", pattern)
        wildcards = {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*", "?": "[^/]"}
        return re.compile("".join(wildcards.get(part, re.escape(part)) for part in parts))
