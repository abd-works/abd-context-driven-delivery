"""SessionFiles - the files of one session: the ones its practices declare, the ones in its folder, and the ones it reads."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from space.session.file_manager import FileEntry, FileManager, FileText

if TYPE_CHECKING:
    from space.session.session import Session


class SessionFiles:
    """The files one session works with. Its file manager reads under the session's roots; the folder files are its log,
    handoffs, kept notes, and reports. The files a practice declares are each fidelity's own, through its
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
            self._file_manager = FileManager(self._session.root, roots)
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
        checkout's file manager, which its sessions hold, searches it."""
        return self._session.sessions.file_manager.find(pattern)

    def in_folder(self) -> list[FileEntry]:
        """Every file in the session's folder, each with its path from the project."""
        repo = self._session.repo
        files = sorted(path for path in self._session.session_path.rglob("*") if path.is_file())
        return [FileEntry(repo.path_from_top(path), True) for path in files]

    def read(self, path: str) -> FileText:
        """The text of path, a file in the session's repository or under a folder its practices write to, such as its
        ticket's worktree beside the repository; no text when the file is gone."""
        return self._from_project.read(path)

    def worked_on(self) -> set[Path] | None:
        """The files that are the session's work: every file when it works in a folder of its own, which holds only its
        work; on the whole repository, only the files its branch changed."""
        repo = self._session.repo
        if self._session.root != repo.root:
            return None
        return {(repo.root / path).resolve() for path in repo.branch_named(self._session.name).changed_files()}
