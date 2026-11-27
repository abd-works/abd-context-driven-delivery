"""SessionFolder - where one session's folder is kept among its sessions, and the files it keeps there."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from space.repo.repo import Repo
from space.session.session_log import HookLog
from space.work_state import COMPLETE_FOLDER
from space.session.validation.violation_history import VIOLATION_HISTORY_FILE, ViolationHistory

if TYPE_CHECKING:
    from space.session.session import Session

ARCHIVE_FOLDER = "_archive"
_HOOK_LOGS_FOLDER = "logs"
# The name a record folder takes for the moment between leaving the sessions and being deleted; its first character
# marks a folder the sessions share, so no board lists it as a session.
_BEING_REMOVED = "_removing-"


class SessionFolderHeldError(RuntimeError):
    """Raised when a session's record folder cannot be removed because a running program holds it open, such as a shell
    or an editor working in it. Nothing in the folder was deleted. It names the folder."""

    def __init__(self, folder: Path) -> None:
        super().__init__(f"could not remove the session folder {folder}; close what holds it open and delete it again")
        self.folder = folder


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
        return self._move_to(self._session.sessions.closed_folder)

    def move_to_archive(self) -> Session:
        return self._move_to(self._session.sessions.folder / ARCHIVE_FOLDER)

    def move_to_backlog(self) -> Session:
        return self._move_to(self._session.sessions.backlog_folder)

    def reopen(self) -> Session:
        """Back among the open sessions, from closed or the backlog."""
        return self._move_to(self._session.sessions.folder)

    def remove(self) -> None:
        """Delete this session's record folder and its work folder, log, files, and all; its sessions no longer hold it.
        A record folder a running program holds open raises ``SessionFolderHeldError`` with every file still in it. Once
        the folder is set aside the session is removed whatever happens next: a file that cannot be removed stays in the
        set-aside folder, which no board lists, and the next removal of a session of that name clears it."""
        session = self._session
        _removed_whole(self._set_aside(session.record_folder))
        if session.work_folder != session.record_folder and session.work_folder.is_dir():
            _removed_whole(session.work_folder)
        session.sessions.held.removed(session)
        session.record.saved("removed")

    def _set_aside(self, record_folder: Path) -> Path:
        """Rename record_folder out from among the sessions and answer where it is now. The operating system renames a
        folder whole or not at all, and refuses one a running program holds open, so the refusal comes before any file is
        deleted; deleting file by file would stop halfway and leave a session with a folder and no record."""
        aside = _free_name_beside(record_folder)
        try:
            record_folder.rename(aside)
        except PermissionError as held:
            raise SessionFolderHeldError(record_folder) from held
        return aside

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


def _free_name_beside(record_folder: Path) -> Path:
    """The name record_folder takes while it is removed, free to rename onto: the folder an earlier removal left under
    that name is removed first, and where some of it cannot be, the name takes a number."""
    aside = record_folder.with_name(f"{_BEING_REMOVED}{record_folder.name}")
    if not aside.exists() or _removed_whole(aside):
        return aside
    taken = 2
    while aside.with_name(f"{aside.name}-{taken}").exists():
        taken += 1
    return aside.with_name(f"{aside.name}-{taken}")


def _removed_whole(folder: Path) -> bool:
    """Remove folder and everything in it, and answer whether nothing of it is left. Windows refuses to remove a folder
    another process has open, as a file watcher does for a moment, and a file a program holds open; what it refuses
    stays, and the session it belonged to is removed all the same. The folder is removed by its extended-length path,
    since setting it aside lengthens every path in it, and Windows refuses to remove a file whose path is over 260
    characters when it is named the ordinary way."""
    try:
        shutil.rmtree(_extended_length(folder))
    except OSError:
        return not folder.exists()
    return True


# What Windows puts before a path to lift its 260 character limit.
_EXTENDED_LENGTH_PREFIX = "\\\\?\\"


def _extended_length(folder: Path) -> Path:
    """folder as Windows reads a path of any length; folder itself on any other system."""
    return Path(f"{_EXTENDED_LENGTH_PREFIX}{folder.resolve()}") if os.name == "nt" else folder
