"""SessionFiles - the files of one session: the ones its practices declare, the ones in its folder, and the ones it reads."""

from __future__ import annotations

import os

import time
from pathlib import Path
from typing import TYPE_CHECKING

from harness.git.git import Git
from space.session.file_manager import FileEntry, FileManager, FileText

if TYPE_CHECKING:
    from space.session.session import Session


class NamedPathNotFoundError(FileNotFoundError):
    """Raised when a call names a path that is not in its session's project, or, for a reader that reads only under the
    session's root, such as its graph, not under that root: working on it would work on nothing, and an empty result
    reads as if all were well. It names the path, the project it was read from, and the root when the root refused it."""

    def __init__(self, named: str, project: Path, root: Path | None = None) -> None:
        self.named = named
        self.project = project
        self.root = root
        where = f" under the session's root {root}" if root is not None else ""
        super().__init__(f"nothing{where} at {named}, read from {project}; name paths from the project's root, or absolute")


class SessionFiles:
    """The files one session works with, read through two file managers that name paths from two tops: the session's
    own, named from its workpath, which a page lists and reads; and one named from the project's top, which reads and
    finds the files the board names that way. The folder files are its log, handoffs, kept notes, and reports. The files a practice declares are each fidelity's own, through its
    FidelitySessionOutput."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._file_manager: FileManager | None = None
        self._project_files: FileManager | None = None
        # The files the session's branch changed, which the board's changed-files filter reads.
        self.branch_changes = BranchChanges(session)

    @property
    def file_manager(self) -> FileManager:
        """The session's file manager, held in memory, reading under the session's roots: the folder each practice works
        in, as ``session.json`` records it or by the practice's default, the folder its declared outputs sit under, and
        each folder those outputs are written in, such as the ``story_tests`` beside the Stories root's ``.context``. A
        new one when those roots change."""
        practices = self._session.own_practices.values()
        roots = tuple(sorted({practice.folder for practice in practices} | {practice.output_root for practice in practices} | {folder.resolve() for practice in practices for folder in practice.output_folders}))
        if self._file_manager is None or self._file_manager.roots != roots:
            self._file_manager = FileManager(self._session.work_root, roots)
        return self._file_manager

    @property
    def _from_project(self) -> FileManager:
        """A file manager named from the project's top that reads the repository and the session's roots, such as its
        ticket's worktree beside the repository; held, and a new one when the session's roots change."""
        repo_root = self._session.repo.root
        roots = (repo_root, *self.file_manager.roots)
        if self._project_files is None or self._project_files.roots != tuple(Path(root).resolve() for root in roots):
            self._project_files = FileManager(repo_root, roots)
        return self._project_files

    def find(self, pattern: str) -> list[Path]:
        """The files pattern names, written from the top of the session's checkout, wherever they are in it: the
        file manager named from the project's top searches it."""
        return self._from_project.find(pattern)

    def in_folder(self) -> list[FileEntry]:
        """Every file in the session's folder, each with its path from the project."""
        repo = self._session.repo
        files = sorted(path for path in self._session.session_path.rglob("*") if path.is_file())
        return [FileEntry(repo.path_from_top(path), True) for path in files]

    def in_workpath(self) -> list[FileEntry]:
        """Every file directly in the folder the session works in, each with its path from the project; its folders
        are left out, so a workpath of the whole repository lists only the repository's top files."""
        repo = self._session.repo
        files = sorted(path for path in self._session.work_root.iterdir() if path.is_file())
        return [FileEntry(repo.path_from_top(path), True) for path in files]

    def under_root(self) -> list[FileEntry]:
        """Every file under the folder the session works in, its folders included, each with its path from the project
        and whether the session's branch changed it: in a repository the files git tracks or would track there, so what
        .gitignore leaves out, such as node_modules or a build, is left out; elsewhere every file under it but those
        folders' kind."""
        root = self._session.work_root
        files = self._tracked_under(root) if self._session.repo.is_clone else self._walked_under(root)
        changed = self.branch_changes.files()
        repo = self._session.repo
        return [FileEntry(repo.path_from_top(path), True, path.resolve() in changed) for path in sorted(files) if path.is_file()]

    def _tracked_under(self, root: Path) -> list[Path]:
        listed = Git(root).run("ls-files", "--cached", "--others", "--exclude-standard")
        return [root / line for line in dict.fromkeys(listed.splitlines()) if line]

    def _walked_under(self, root: Path) -> list[Path]:
        return [path for path in root.rglob("*") if not UNREAD_FOLDERS.intersection(path.relative_to(root).parts)]

    def read(self, path: str) -> FileText:
        """The text of path, a file in the session's repository or under a folder its practices write to, such as its
        ticket's worktree beside the repository; no text when the file is gone."""
        return self._from_project.read(path)

    def write(self, path: str, text: str) -> FileText:
        """Save text as path, a file in the session's repository or under a folder its practices write to, named from
        the project's top as ``read`` names it."""
        return self._from_project.write(path, text)

    def existing(self, named: str | Path) -> Path:
        """The path named, read as the session reads every path its agent writes (``SessionPaths.path_named``), once
        something is there; refused otherwise."""
        path = self._session.paths.path_named(named)
        if not path.exists():
            raise NamedPathNotFoundError(str(named), self._session.repo_path)
        return path

    def from_root(self, named: str | Path) -> str:
        """The path named, which must be there under one of the session's roots, written from the session's root the way
        the session's graph names its files, a file above it with ``..``, such as a story test in the story_tests a
        fidelity writes to; a path outside every root is refused, since the graph would read nothing for it."""
        path = self.existing(named)
        if not self.in_root(path):
            raise NamedPathNotFoundError(str(named), self._session.repo_path, self._session.work_root)
        return Path(os.path.relpath(path, self._session.work_root)).as_posix()

    def in_root(self, path: Path) -> bool:
        """Whether path lies under one of the session's roots: the folders its file manager reads, its root among them."""
        roots = (self._session.work_root, *self.file_manager.roots)
        return any(path == root or root in path.parents for root in (Path(root).resolve() for root in roots))


# The folders a root outside a repository never lists files from: version control, dependencies, builds, caches.

# How long the branch's changed files are kept, by checkout and session, before git is asked again.
CHANGED_KEPT_SECONDS = 3.0
_CHANGED: dict[tuple[str, str], tuple[float, set[Path]]] = {}


# The folders a walk under a root that is not a repository leaves out: tools, caches, and builds hold no one's work.
UNREAD_FOLDERS = frozenset({".git", "node_modules", "dist", "build", "__pycache__", ".venv", ".pytest_cache"})


class BranchChanges:
    """The files one session's branch changed since it left the default branch, which the board's changed-files filter
    reads."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def files(self) -> set[Path]:
        """The files the session's branch changed since it left the default branch, with its uncommitted changes when
        it is checked out; none for a project that is no clone, or a session with no branch of its own. Asking git takes
        a moment, and a page lists many fidelities at once, so the answer is kept for CHANGED_KEPT_SECONDS and shared."""
        repo = self._session.repo
        if not repo.is_clone:
            return set()
        # A branch checked out in a worktree of its own, such as a ticket's, has its changed files there, not in the
        # clone the session was reached through.
        key = (str(repo.root), self._session.name)
        held = _CHANGED.get(key)
        if held is not None and time.monotonic() - held[0] < CHANGED_KEPT_SECONDS:
            return held[1]
        branch = repo.branch_named(self._session.name)
        checkout = branch.checkout if branch.exists else None
        root = checkout.root if checkout is not None else repo.root
        changed = {(root / path).resolve() for path in branch.changed_files()}
        _CHANGED[key] = (time.monotonic(), changed)
        return changed
