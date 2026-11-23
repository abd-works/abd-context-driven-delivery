"""SessionFolder - where one session's folder is kept among its sessions, and the files it keeps there."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from space.repo.repo import Repo
from space.session.session_log import HookLog
from space.session.violation_history import VIOLATION_HISTORY_FILE, ViolationHistory

if TYPE_CHECKING:
    from space.session.session import Session

COMPLETE_FOLDER = "_complete"
ARCHIVE_FOLDER = "_archive"
_HOOK_LOGS_FOLDER = "logs"


class SessionFolder:
    """One session's folders: its record folder on main, ``.sessions/{name}/``, as it moves among the open, closed,
    archived, and backlog sessions, and its work folder, which holds the files its work writes. A moved session stays the
    one object its sessions hold for it, and every move is queued to be saved on main."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def hook_log(self, filename: str) -> HookLog:
        """The log called filename that a hook appends to while this session is open, such as dispatch.debug, in the
        ``logs`` folder of the session's work folder."""
        return HookLog(self._session.work_folder / _HOOK_LOGS_FOLDER / filename)

    @property
    def violation_history(self) -> ViolationHistory:
        """The history of every graph hit this session's validations found, judged, and fixed, kept in its work folder
        and tracked with it, stamped with the commits of the checkout the session works in. Made from wherever the work
        folder is now, since it moves with the record when the two are one folder."""
        return ViolationHistory(self._session.work_folder / VIOLATION_HISTORY_FILE, Repo.of_project(self._session.work_root))

    def keep_file(self, file: Path) -> Path:
        """Move ``file`` into this session's record folder, where it stays with the session's record until it becomes
        lasting context, such as part of a story map. A started backlog item's text is the only copy of the idea, and the
        board shows it on the ticket's card as the session's idea file, so it is kept with the record on main."""
        kept = self._session.record_folder / file.name
        file.replace(kept)
        self._session.record.saved(f"keeps {file.name}")
        return kept

    def move_to_closed(self) -> Session:
        """Move this session's record folder among the closed sessions, where the board lists closed work."""
        return self._move_to(self._session.sessions.folder / COMPLETE_FOLDER)

    def move_to_archive(self) -> Session:
        return self._move_to(self._session.sessions.folder / ARCHIVE_FOLDER)

    def move_to_backlog(self) -> Session:
        return self._move_to(self._session.sessions.backlog_folder)

    def reopen(self) -> Session:
        """Back among the open sessions, from closed or the backlog."""
        return self._move_to(self._session.sessions.folder)

    def remove(self) -> None:
        """Delete this session's record folder and its work folder, log, files, and all; its sessions no longer hold it."""
        session = self._session
        _remove_files_of(session.record_folder)
        if session.work_folder != session.record_folder and session.work_folder.is_dir():
            _remove_files_of(session.work_folder)
        session.sessions.held.removed(session)
        session.record.saved("removed")

    def _move_to(self, parent: Path) -> Session:
        """Move this session's record folder under ``parent``, such as ``.sessions/_complete/``; the session, now kept
        there, and still the one object its sessions hold for it. A work folder that is the record folder moves with it,
        and so does one whose worktree is gone, its work merged beside the record when the ticket closed; one in a
        worktree still there stays with the work."""
        session = self._session
        parent.mkdir(parents=True, exist_ok=True)
        moved_from = session.record_folder
        works_beside_record = session.work_folder == moved_from or not session.work_folder.is_dir()
        shutil.move(str(moved_from), str(parent / session.name))
        session.record_folder = parent / session.name
        if works_beside_record:
            session.work_folder = session.record_folder
        session.sessions.held.moved(session, moved_from)
        session.record.saved(f"moves to {parent.name}")
        return session


def _remove_files_of(folder: Path) -> None:
    """Remove folder and everything in it. Windows refuses to remove a folder another process has open, as a file watcher
    does for a moment; once every file inside is gone the session is removed all the same, and the empty folders left
    behind hold nothing a session reads. A file still there is refused, naming it."""
    try:
        shutil.rmtree(folder)
    except PermissionError:
        if any(inner.is_file() for inner in folder.rglob("*")):
            raise
