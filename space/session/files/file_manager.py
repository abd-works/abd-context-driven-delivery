"""The session's file manager: lists and reads the files under a session's roots, so every application shows files the
same way instead of each object growing a read operation of its own.

A session's roots are its workpath: the folder each of its practices works in, as its `session.json` records it, or the
practice's default folder when it records none. The session's own folder under `.sessions/` is not one of them."""

from __future__ import annotations

import hashlib
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


# The folder git keeps its own record in: its config, its objects, and the hooks it runs on the next commit.
VERSION_CONTROL_FOLDER = ".git"


def inside_version_control(parts: tuple[str, ...]) -> bool:
    """Whether a path of these parts lies in a .git folder or is one, in any case, as Windows reads ``.GIT`` as the same
    folder."""
    return any(part.casefold() == VERSION_CONTROL_FOLDER for part in parts)


def is_link(path: Path | os.DirEntry[str]) -> bool:
    """Whether path is a link to another file or folder: a symbolic link, or a junction, the link to a folder Windows
    makes without the privilege a symbolic link needs. A link is followed by a read, but a delete removes the link only."""
    return path.is_symlink() or path.is_junction()


class VersionControlPathRefused(PermissionError):
    """A read or write aimed inside a repository's .git folder, which holds git's own record: a hook written there runs
    on the person's next commit, and its config holds where the repository pushes; or a delete of a folder that holds
    one, such as a nested repository's, which would leave it half deleted, as git keeps its objects read-only. It names
    the path refused, and the .git folder it holds."""

    def __init__(self, path: str, held: str = "") -> None:
        where = f"holds {held}, a .git folder" if held else "is inside a .git folder"
        super().__init__(f"{path} {where}, which holds git's own record (its config, objects and hooks): it is neither read, written nor deleted as a file")
        self.path = path


class FileChangedSinceReadError(RuntimeError):
    """A write of a file that is no longer as its caller read it: someone changed it, made it, or deleted it on disk
    since, and saving over it would lose that change unseen. It names the path, the version the write gave, and the
    version on disk now."""

    def __init__(self, path: str, version: str, on_disk: str) -> None:
        given = version or "none, as for a new file"
        now = on_disk or "no file"
        super().__init__(
            f"{path} changed on disk since it was read: the write gave version {given}, and the disk holds {now}; "
            "read it again with read_file and write from what it holds now, passing the version that read answers"
        )
        self.path = path
        self.version = version
        self.on_disk = on_disk


def version_of(data: bytes) -> str:
    """The version of a file's content, a hash of its bytes, which read_file answers and write_file takes back."""
    return hashlib.sha256(data).hexdigest()


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
    """Where a file is published in Claude, which a page opens instead of the file: the link, what is published there,
    a ``whiteboard`` board or a ``design canvas``, and the title it is published under, such as ``ux-mockup``; no link and
    no kind for a file not published, and no title where the page names it from its path."""

    link: str = ""
    kind: str = ""
    name: str = ""


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
        self._hidden_by_formats: tuple[str, ...] = ()

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
    def published_name(self) -> str:
        """The title it is published under in Claude, such as ``ux-mockup`` for a design canvas, so a page names it as
        the published artifact is named; none where the page names it from its path, as a whiteboard by its file."""
        return self._published.name

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

    @property
    @data_field
    def hidden_by_formats(self) -> list[str]:
        """The format groups selected, such as markdown or diagram, when they alone leave the file out of a page's
        list, as the listing that answered it decided; none for a file listed, or one left out for its fidelity."""
        return list(self._hidden_by_formats)

    def listed_as(self, is_listed: bool, is_session_work: bool, hidden_by_formats: list[str] | None = None) -> FileEntry:
        """This file, listed or not, the session's own work or not, and left out by the formats selected or not, as a
        listing decided."""
        copy = self._copied(self._published, self._fidelities)
        copy._is_listed = is_listed
        copy._is_session_work = is_session_work
        copy._hidden_by_formats = tuple(hidden_by_formats or ())
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
        copy._hidden_by_formats = self._hidden_by_formats
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
# The form a viewer renders a file in beside its source, by its suffix: markdown as the page it describes, an HTML page,
# an SVG drawing, and JSON laid out; a file of any other suffix shows only as source.
RENDERED_FORMS = {".md": "markdown", ".markdown": "markdown", ".html": "html", ".htm": "html", ".svg": "svg", ".json": "json"}


class FileText:
    """The text of one file, with its path from the workpath and the version of its content, which a write of the file
    gives back; no text and no version for a file that is not there, which ``exists`` tells from a file that is there
    and empty."""

    def __init__(self, path: str, text: str, version: str, exists: bool = True) -> None:
        self._path = path
        self._text = text
        self._version = version
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
    def version(self) -> str:
        """The version of the file's content as read or saved, a hash of its bytes, which a write of the file passes
        back so a change made on disk since is refused rather than lost; none for a file that is not there."""
        return self._version

    @property
    @data_field
    def language(self) -> str:
        """The language a viewer shows the text in, from the file's suffix, such as python or markdown."""
        return LANGUAGES.get(Path(self._path).suffix.lower(), PLAIN_TEXT)

    @property
    @data_field
    def rendered_form(self) -> str:
        """The form a viewer renders the text in beside its source, from the file's suffix: markdown, html, svg or
        json; none for a file a viewer shows only as source, such as code or a draw.io file."""
        return RENDERED_FORMS.get(Path(self._path).suffix.lower(), "")


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
        """Return the text of path, a file inside one of the session's roots, named from its workpath, with the version of its content, which a write of it passes back; no text and no version when the file is not there, such as one deleted since a page listed it. A path inside a .git folder is refused."""
        target = self._inside(path)
        if not target.is_file():
            return FileText(self._relative(target), "", "", exists=False)
        data = target.read_bytes()
        # Line ends read as a text file reads them, so \r\n and \r are each one \n.
        text = data.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
        return FileText(self._relative(target), text, version_of(data))

    @mcp
    @agent_tool
    @noSessionLog
    def write(self, path: str, text: str, version: str = "") -> FileText:
        """Save text as the whole of path, a file inside one of the session's roots, named from its workpath, making its folder when it has none; the file as saved, with its new version. version is the one read answered for the file; none for a file not there yet. A file on disk that is no longer that version, changed, made or deleted since it was read, is refused (FileChangedSinceReadError) and left as it is. The session's own session.json is refused, since only the session's tools change it, and so is a path inside a .git folder."""
        target = self._inside(path)
        if self._record is not None and self._record.is_its_file(target):
            raise SessionRecordWriteRefused(path)
        on_disk = version_of(target.read_bytes()) if target.is_file() else ""
        if on_disk != version:
            raise FileChangedSinceReadError(path, version, on_disk)
        data = text.encode("utf-8")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return FileText(self._relative(target), text, version_of(data))

    def unfollowed(self, path: str) -> Path:
        """The path named from the workpath, with the folders above it read through any link but not its own last part,
        so a link names itself, not the folder it points to, as a delete must; refused as a read refuses a path outside
        every root or inside a .git folder."""
        named = self._workpath / path
        if named.name in ("", ".", ".."):
            return self._inside(path)
        return self._within_roots(path, named.parent.resolve() / named.name)

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
        """The path resolved from the workpath; a page names paths, so one outside every root is refused, and so is one
        inside a .git folder under its root, in any case, as Windows reads ``.GIT`` as the same folder."""
        return self._within_roots(path, (self._workpath / path).resolve())

    def _within_roots(self, path: str, target: Path) -> Path:
        """target, the absolute path path names, once it lies under one of the roots and not inside a .git folder there."""
        root = next((root for root in self._roots if target == root or root in target.parents), None)
        if root is None:
            raise PathOutsideRootsError(path)
        if inside_version_control(target.relative_to(root).parts):
            raise VersionControlPathRefused(path)
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

