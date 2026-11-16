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
    """One session's folder, ``.sessions/{name}/``, as it moves among the open, closed, archived, and backlog sessions.
    A moved session stays the one object its sessions hold for it, and every move is queued to be saved on main."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def hook_log(self, filename: str) -> HookLog:
        """The log called filename that a hook appends to while this session is open, such as dispatch.debug, in the
        ``logs`` folder of the session's folder."""
        return HookLog(self._session.session_path / _HOOK_LOGS_FOLDER / filename)

    @property
    def violation_history(self) -> ViolationHistory:
        """The history of every graph hit this session's validations found, judged, and fixed, kept in its folder and
        tracked with it, stamped with the commits of the checkout the session works in. Made from wherever the folder is
        now, since a session's folder moves when it closes."""
        return ViolationHistory(self._session.session_path / VIOLATION_HISTORY_FILE, Repo.of_project(self._session.work_root))

    def keep_file(self, file: Path) -> Path:
        """Move ``file`` into this session's folder, where it stays with the session's work until it becomes lasting
        context, such as part of a story map. A started backlog item's text is the only copy of the idea."""
        kept = self._session.session_path / file.name
        file.replace(kept)
        self._session.record.saved(f"keeps {file.name}")
        return kept

    def move_to_closed(self) -> Session:
        """Move this session's folder among the closed sessions, where the board lists closed work."""
        return self._move_to(self._session.sessions.folder / COMPLETE_FOLDER)

    def move_to_archive(self) -> Session:
        return self._move_to(self._session.sessions.folder / ARCHIVE_FOLDER)

    def move_to_backlog(self) -> Session:
        return self._move_to(self._session.sessions.backlog_folder)

    def reopen(self) -> Session:
        """Back among the open sessions, from closed or the backlog."""
        return self._move_to(self._session.sessions.folder)

    def remove(self) -> None:
        """Delete this session's folder, log, files, and all; its sessions no longer hold it."""
        shutil.rmtree(self._session.session_path)
        self._session.sessions.held.removed(self._session)
        self._session.record.saved("removed")

    def _move_to(self, parent: Path) -> Session:
        """Move this session's folder under ``parent``, such as ``.sessions/_complete/``; the session, now kept there,
        and still the one object its sessions hold for it."""
        session = self._session
        parent.mkdir(parents=True, exist_ok=True)
        moved_from = session.session_path
        shutil.move(str(moved_from), str(parent / session.name))
        session.session_path = parent / session.name
        session.sessions.held.moved(session, moved_from)
        session.record.saved(f"moves to {parent.name}")
        return session
