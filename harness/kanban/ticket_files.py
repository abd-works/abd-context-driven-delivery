"""A ticket's files: the outputs its fidelities declare, the files in its session folder, and reading any of them."""

from __future__ import annotations

import os
import re
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from harness.installation.destination import data_field
from tools.file_manager.file_manager import FileManager, FileText

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from space.repo.repo import Repo
    from space.session import Session

SKIPPED_FOLDERS = frozenset({"node_modules"})
# Hidden folders hold tools and caches, but a module's .context folder holds its models and maps.
SEARCHED_HIDDEN_FOLDERS = frozenset({".context"})
NAMED_PART = re.compile(r"\{[^{}/]+\}")


class FileEntry:
    """One file a ticket lists, as a path from the project, and whether it is there yet."""

    def __init__(self, path: str, exists: bool) -> None:
        self._path = path
        self._exists = exists

    @property
    @data_field
    def path(self) -> str:
        return self._path

    @property
    @data_field
    def exists(self) -> bool:
        return self._exists


class TicketFiles:
    """The files of one ticket's session: what its fidelities declare, what its session folder holds, and their text."""

    def __init__(self, session: Session, repo: Repo, branch: str) -> None:
        self._session = session
        self._repo = repo
        self._branch = branch

    def declared_by(self, fidelity: FidelityGuidance) -> dict[str, list[FileEntry]]:
        """The files fidelity declares, by format. A pattern lists the files this ticket worked on, not every match in the repository."""
        outputs = self._session.fidelity_outputs(fidelity.practice_guidance, fidelity)
        return {label: [entry for path in paths for entry in self._entries(path)] for label, paths in outputs.items()}

    def in_session_folder(self) -> list[FileEntry]:
        """Every file in the session folder: its log, handoffs, kept notes, and validation reports."""
        files = sorted(path for path in self._session.session_path.rglob("*") if path.is_file())
        return [FileEntry(self._repo.path_from_top(path), True) for path in files]

    def read(self, path: str) -> FileText:
        """The text of path, a file in the repository; no text when it is gone, such as one deleted since the board listed it."""
        return FileManager(self._repo.root, (self._repo.root,)).read(path)

    @property
    def _workpath(self) -> Path:
        return Path(self._session.workpath or self._repo.root).resolve()

    def _entries(self, declared: str) -> list[FileEntry]:
        """A declared path, or each file of this ticket's that a pattern finds; a pattern that finds none stays as
        written, not yet there."""
        relative = self._repo.path_from_top(declared)
        pattern = _named_parts_as_wildcards(relative)
        if "*" not in pattern:
            return [FileEntry(relative, (self._repo.root / relative).exists())]
        found = self._worked_on(_files_matching_from(self._repo.root, pattern))
        return [FileEntry(self._repo.path_from_top(path), True) for path in found] or [FileEntry(relative, False)]

    def _worked_on(self, found: list[Path]) -> list[Path]:
        """The files of a pattern that are this ticket's. A folder of its own holds only its work; on the whole repository, only what its branch changed is."""
        if not found or self._workpath != self._repo.root:
            return found
        return [path for path in found if path.resolve() in self._changed_on_branch]

    @cached_property
    def _changed_on_branch(self) -> set[Path]:
        root = self._repo.root
        return {(root / path).resolve() for path in self._repo.files_changed_on(self._branch)}


def _files_matching_from(root: Path, pattern: str) -> list[Path]:
    """The files a pattern names, from the repository's top. A session can work outside the repository, so a pattern
    that stayed absolute searches from its drive."""
    anchor = Path(pattern).anchor
    return _files_matching(Path(anchor or root), pattern[len(anchor):])


def _files_matching(start: Path, pattern: str) -> list[Path]:
    """The files under start that pattern names. Installed packages and hidden folders hold no fidelity's work, and
    searching node_modules alone made a pattern take over a second."""
    parts = pattern.split("/")
    fixed = next((index for index, part in enumerate(parts) if set(part) & set("*?")), len(parts))
    # The search starts at the deepest folder the pattern names outright, so a pattern under one folder never walks the drive.
    base = start.joinpath(*parts[:fixed])
    matching = _pattern_matcher("/".join(parts[fixed:]))
    base_text = str(base)
    found = []
    for folder, folders, files in os.walk(base_text):
        folders[:] = [name for name in folders if name not in SKIPPED_FOLDERS and (not name.startswith(".") or name in SEARCHED_HIDDEN_FOLDERS)]
        # Plain strings here: building a Path for every file in the repository made the search take a second.
        inside = folder[len(base_text):].strip("\\/").replace("\\", "/")
        found += [Path(folder, name) for name in files if matching.fullmatch(f"{inside}/{name}" if inside else name)]
    return sorted(found)


def _named_parts_as_wildcards(path: str) -> str:
    """A declared path with its named parts, such as `{module}/{module}-model.md`, as a pattern. A named folder can be
    a module several folders deep, so it matches folders at any depth; a named part of a file name matches within it."""
    folders = re.sub(r"\{[^{}/]+\}/", "**/", path)
    return NAMED_PART.sub("*", folders)


def _pattern_matcher(pattern: str) -> re.Pattern[str]:
    """A glob pattern as a regular expression over a path written with `/`: `**/` is any number of folders, `*` and `?`
    stay inside one folder, the way Path.glob reads them."""
    parts = re.split(r"(\*\*/|\*\*|\*|\?)", pattern)
    wildcards = {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*", "?": "[^/]"}
    return re.compile("".join(wildcards.get(part, re.escape(part)) for part in parts))
