"""The session's file manager: lists and reads the files under a session's roots, so every application shows files the
same way instead of each object growing a read operation of its own.

A session's roots are its workpath: the folder each of its practices works in, as its `session.json` records it, or the
practice's default folder when it records none. The session's own folder under `.sessions/` is not one of them."""

from __future__ import annotations

import os
import time
import re
from pathlib import Path
from typing import Annotated, NamedTuple, Protocol

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.installation.data_class import SourceFile, data_field, language_adapter
from harness.markdown.format import Format
from harness.mcp.mcp_annotations import mcp


# Installed packages and caches hold no one's work. Hidden folders hold tools and caches too, but a module's .context
# folder holds its models and maps, so a search looks inside it and a person can choose it as a practice root.
UNWORKED_FOLDERS = frozenset({"node_modules", "__pycache__"})
WORKED_HIDDEN_FOLDERS = frozenset({".context"})


def holds_work(folder_name: str) -> bool:
    """Whether a folder of this name can hold someone's work: not installed packages or a cache, and not hidden unless
    it is one of the hidden folders that do, such as .context."""
    return folder_name not in UNWORKED_FOLDERS and (not folder_name.startswith(".") or folder_name in WORKED_HIDDEN_FOLDERS)


class SessionRecordWriteRefused(PermissionError):
    """A write was aimed at a session's own session.json, which only the session's record writes: each of its changes
    holds the file from its read to its write, and a whole-file write would drop a change another chat made."""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"{path} is the session's record, session.json, which is not written as a file: change it with the "
            "session's tools, such as session.choose_workpath, session.record_test_tier and the practice and fidelity "
            "tools, which each hold it for their change; read_file still reads it"
        )
        self.path = path


class OwnRecord(Protocol):
    """The record of the session a file manager reads for, which says whether a path is the record's own file, and
    whether it is a file a change to a session.json leaves beside it."""

    def is_its_file(self, path: Path) -> bool:
        """Whether path is the record's session.json, however the path is spelt."""

    def is_left_beside(self, path: Path) -> bool:
        """Whether path is the lock file or the staged text a change to a session.json leaves beside it."""


class PathOutsideRootsError(ValueError):
    """A path outside every root of the session, which a page may name but never reach."""

    def __init__(self, path: str) -> None:
        super().__init__(f"{path} is outside the session's roots")


class FolderEntry:
    """One entry of a listed folder: a folder or a file, with its path from the workpath and, for a file, its size."""

    def __init__(self, path: str, is_folder: bool, size: int) -> None:
        self._path = path
        self._is_folder = is_folder
        self._size = size

    @property
    @data_field
    def name(self) -> str:
        return Path(self._path).name

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

    @property
    def folder_paths(self) -> list[str]:
        """Those folders as paths from the project, sorted, as a folder picker lists them."""
        return sorted(entry.path for entry in self.folders)


class Publication(NamedTuple):
    """Where a file is published in Claude, which a page opens instead of the file: the link, and what is published
    there, a ``whiteboard`` board or a ``design canvas``; no link and no kind for a file not published."""

    link: str = ""
    kind: str = ""


# What a file published in Claude is published as.
WHITEBOARD_KIND = "whiteboard"
DESIGN_CANVAS_KIND = "design canvas"


class FileEntry:
    """One file something declares, such as a fidelity's output, as a path from the project, whether it is there yet,
    whether the session's branch changed it, the format its extension names, and the fidelities it belongs to, which a
    page filters on, and where it is published, such as a design canvas's link and kind, which a page opens instead of
    the file."""

    def __init__(self, path: str, exists: bool, is_changed: bool = False) -> None:
        self._path = path
        self._exists = exists
        self._is_changed = is_changed
        self._published = Publication()
        self._fidelities: tuple[str, ...] = ()
        # Whether a page lists it, and whether it is the session's own work, for the guidance selection a listing
        # applied (*FileListing*); a file no listing looked at is listed and is no one's work.
        self._is_listed = True
        self._is_session_work = False

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

    @property
    @data_field
    def link(self) -> str:
        """The link it is published at in Claude; none while it is not published."""
        return self._published.link

    @property
    @data_field
    def published_kind(self) -> str:
        """What it is published as in Claude, a ``whiteboard`` or a ``design canvas``, so a page names it so without
        working it out from the path; none for a file that is not published."""
        return self._published.kind

    @property
    @data_field
    def format(self) -> str:
        """The format its extension names, such as python for a .py file."""
        return Format.from_extension(Path(self._path).suffix).name

    @property
    @data_field
    def fidelities(self) -> list[str]:
        """The fidelities whose files it is, such as stories-story-map; none for a file no fidelity declares."""
        return list(self._fidelities)

    @property
    @data_field
    def is_listed(self) -> bool:
        """Whether a page lists it for the stages, practices and formats the session selected and the fidelities the
        page's link names, as the listing that answered it decided (*FileListing*)."""
        return self._is_listed

    @property
    @data_field
    def is_session_work(self) -> bool:
        """Whether it is the session's own work, which This session lists: in a git repository, a file its branch
        changed; in a plain folder no branch changes any file, so a file a fidelity declares or holds that is there."""
        return self._is_session_work

    def listed_as(self, is_listed: bool, is_session_work: bool) -> FileEntry:
        """This file, listed or not and the session's own work or not, as a listing decided."""
        copy = self._copied(self._published, self._fidelities)
        copy._is_listed = is_listed
        copy._is_session_work = is_session_work
        return copy

    def belonging_to(self, fidelities: list[str]) -> FileEntry:
        """This file, saying it is a file of fidelities."""
        return self._copied(self._published, tuple(fidelities))

    def linked(self, published: Publication) -> FileEntry:
        """This file, published as published says, such as a design canvas's, which a page opens instead of the
        file."""
        return self._copied(published, self._fidelities)

    def _copied(self, published: Publication, fidelities: tuple[str, ...]) -> FileEntry:
        copy = FileEntry(self._path, self._exists, self._is_changed)
        copy._published = published
        copy._fidelities = fidelities
        copy._is_listed = self._is_listed
        copy._is_session_work = self._is_session_work
        return copy


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
    """The text of one file, with its path from the workpath; no text for a file that is not there, which ``exists``
    tells from a file that is there and empty."""

    def __init__(self, path: str, text: str, exists: bool = True) -> None:
        self._path = path
        self._text = text
        self._exists = exists

    @property
    def exists(self) -> bool:
        """Whether the file was there when it was read."""
        return self._exists

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

    def __init__(self, workpath: Path | str, roots: tuple[Path, ...], record: OwnRecord | None = None) -> None:
        self._workpath = Path(workpath).resolve()
        self._roots = tuple(Path(root).resolve() for root in roots)
        # The record of the session it reads for, whose session.json it reads and never saves; none for a project's files.
        self._record = record

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
        """List the entries of folder, a path from the session's workpath (the workpath when empty) inside one of its roots: folders first, then files, each with its path and size; no entries when the folder is not there, such as one deleted since a page listed it. What a change to a session.json leaves beside it, its lock file and a killed writer's staged text, is no one's work and is left out."""
        target = self._inside(folder)
        if not target.is_dir():
            return Folder(self._relative(target), [])
        entries = sorted((entry for entry in target.iterdir() if not self._is_left_beside_a_record(entry)), key=lambda entry: (not entry.is_dir(), entry.name.lower()))
        return Folder(self._relative(target), [self._entry(entry) for entry in entries])

    def _is_left_beside_a_record(self, entry: Path) -> bool:
        """Whether entry is a file a change to a session.json left beside it, as the session's record tells; a file
        manager reading for no session leaves nothing out."""
        return self._record is not None and entry.is_file() and self._record.is_left_beside(entry)

    @mcp
    @agent_tool
    @noSessionLog
    def read(self, path: str) -> FileText:
        """Return the text of path, a file inside one of the session's roots, named from its workpath; no text when the file is not there, such as one deleted since a page listed it."""
        target = self._inside(path)
        exists = target.is_file()
        text = target.read_text(encoding="utf-8", errors="replace") if exists else ""
        return FileText(self._relative(target), text, exists)

    @mcp
    @agent_tool
    @noSessionLog
    def write(self, path: str, text: str) -> FileText:
        """Save text as the whole of path, a file inside one of the session's roots, named from its workpath, making its folder when it has none; the file as saved. The session's own session.json is refused, since only the session's tools change it."""
        target = self._inside(path)
        if self._record is not None and self._record.is_its_file(target):
            raise SessionRecordWriteRefused(path)
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
        return sorted(Path(base, inside) for inside in self._files_under(str(base)) if matching.fullmatch(inside))

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
        return FolderEntry(self._relative(entry), is_folder, 0 if is_folder else entry.stat().st_size)

    def _glob_expression(self, pattern: str) -> re.Pattern[str]:
        """A glob pattern as a regular expression over a path written with `/`: `**/` is any number of folders, `*` and
        `?` stay inside one folder, the way Path.glob reads them."""
        parts = re.split(r"(\*\*/|\*\*|\*|\?)", pattern)
        wildcards = {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*", "?": "[^/]"}
        return re.compile("".join(wildcards.get(part, re.escape(part)) for part in parts))

    def search_again(self) -> None:
        """Walk the folders again on the next search: files were just written, such as the ones an alignment rendered,
        which a walk kept for FILES_KEPT_SECONDS does not hold."""
        _FILES_UNDER.clear()

    def _files_under(self, base: str) -> list[str]:
        """Every file under base that holds someone's work, as a path from base with forward slashes, walked once and kept
        for FILES_KEPT_SECONDS. Installed packages and hidden folders hold no one's work, so the walk skips them."""
        held = _FILES_UNDER.get(base)
        if held is not None and time.monotonic() - held[0] < FILES_KEPT_SECONDS:
            return held[1]
        files = []
        for folder, folders, names in os.walk(base):
            # Plain strings here: building a Path for every file in the repository made the search take a second.
            inside = folder[len(base):].strip("\\/").replace("\\", "/")
            folders[:] = [name for name in folders if holds_work(name)]
            files += [f"{inside}/{name}" if inside else name for name in names]
        _FILES_UNDER[base] = (time.monotonic(), files)
        return files


# How long the files under a folder are kept before it is walked again: a page lists many fidelities at once, each
# searching its patterns, and walking the checkout once for each pattern made fifteen fidelities take five seconds.
FILES_KEPT_SECONDS = 3.0
_FILES_UNDER: dict[str, tuple[float, list[str]]] = {}

