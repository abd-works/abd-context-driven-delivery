"""SessionFiles - the files of one session: the ones its practices declare, the ones in its folder, and the ones it reads."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

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

    @property
    def file_manager(self) -> FileManager:
        """The session's file manager, held in memory, reading under the session's roots: the folder each practice works
        in, as ``session.json`` records it or by the practice's default, and the folder its declared outputs sit under. A
        new one when those roots change."""
        practices = self._session.practices.values()
        roots = tuple(sorted({practice.folder for practice in practices} | {practice.output_root for practice in practices}))
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

    def read(self, path: str) -> FileText:
        """The text of path, a file in the session's repository or under a folder its practices write to, such as its
        ticket's worktree beside the repository; no text when the file is gone."""
        return self._from_project.read(path)

    def existing(self, named: str | Path) -> Path:
        """The path named, read as the session reads every path its agent writes (``Session.path_named``), once
        something is there; refused otherwise."""
        path = self._session.path_named(named)
        if not path.exists():
            raise NamedPathNotFoundError(str(named), self._session.repo_path)
        return path

    def from_root(self, named: str | Path) -> str:
        """The path named, which must be there under the session's root, written from that root, the way the session's
        graph names its files; a path outside the root is refused, since the graph would read nothing for it."""
        path = self.existing(named)
        if not self.in_root(path):
            raise NamedPathNotFoundError(str(named), self._session.repo_path, self._session.work_root)
        return path.relative_to(self._session.work_root).as_posix()

    def in_root(self, path: Path) -> bool:
        """Whether path is the session's root or lies under it."""
        root = self._session.work_root
        return path == root or root in path.parents

    def worked_on(self) -> set[Path] | None:
        """The files that are the session's work: every file when it works in a folder of its own, which holds only its
        work; on the whole repository, only the files its branch changed."""
        repo = self._session.repo
        if self._session.work_root != repo.root:
            return None
        return {(repo.root / path).resolve() for path in repo.branch_named(self._session.name).changed_files()}
