"""Sessions - the work sessions of one checkout, kept in its ``.sessions`` folder, and which of them is open."""

from __future__ import annotations

import threading
from functools import cached_property
from pathlib import Path

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.installation.files import command
from harness.mcp.mcp_server import mcp
from harness.annotations.name import Name
from space.repo.repo import Repo
from space.session.file_manager import FileManager
from space.session.session import COMPLETE_FOLDER, MAIN_SESSION_NAME, SESSION_FILE, Session, SessionNotFoundError

BACKLOG_FOLDER = "_backlog"
# Folders in `.sessions` whose names start with this are the ones the sessions share, such as the backlog.
_SHARED_FOLDER_MARK = "_"


class SessionNameRequiredError(ValueError):
    """Raised when switch-session has no name and ``.sessions/session.json`` has no session or branch."""

    def __init__(self) -> None:
        super().__init__(
            "session name is required: pass name, or switch to a branch first so "
            "the session can take its name"
        )


@agent_toolset
class Sessions:
    """The work sessions of one checkout: open ones in ``.sessions/{name}/``, closed ones in ``.sessions/_complete/``,
    and the one saved as open in ``.sessions/session.json``. ``main`` works on the whole repository and is open when no
    other is. The open session is read from that file each time it is asked for, so a switch or a close made by another
    chat or by the hook server is seen at once.

    One *Session* is kept here for each session folder, made the first time it is read and read again from its folder
    on each ask, so every call in a session, from any chat, works on the same object, which holds that session's graph
    and its one instance of each practice. A call's chat is the call's own: the lines it logs go through
    ``session.log.by(chat)``."""

    def __init__(self, project: Path | str) -> None:
        self.project = Path(project).resolve()
        # The checkout holding the project, made once: every session this loads works in it.
        self.repo = Repo.of_project(self.project)
        self.root = self.repo.root
        # This checkout's own choice of open session. A linked worktree keeps its own, so a chat there never changes the
        # session open in the main clone; in the main clone it is the repository's `work_state`.
        self._state = self.repo.own_work_state
        self._held: dict[Path, Session] = {}
        self._held_lock = threading.Lock()

    @classmethod
    @tool_subject
    def of_project(cls, project: Path) -> Sessions:
        """The sessions of project, the project the running call names, as this process holds them between calls."""
        return SERVED_SESSIONS.of_project(project)

    @cached_property
    def file_manager(self) -> FileManager:
        """Lists, finds, and reads the files anywhere in this checkout, named from its top; made once."""
        return FileManager(self.root, (self.root,))

    @property
    def folder(self) -> Path:
        """The `.sessions` folder that holds the sessions and what they share on the board."""
        return self._state.sessions_folder

    @property
    def backlog_folder(self) -> Path:
        """Where sessions wait before work starts, and where a session moved back is held."""
        return self.folder / BACKLOG_FOLDER

    def folder_of(self, name: str) -> Path:
        """The folder of the session called name. A ticket on the board lives in the main checkout's ``.sessions``, so
        a chat in the ticket's linked worktree logs there too and the board shows its work. Each checkout keeps its own
        main session."""
        preferred = self.folder / name
        candidates = [preferred]
        if name != MAIN_SESSION_NAME:
            candidates.insert(0, self.repo.work_state.sessions_folder / name)
        return next((folder for folder in candidates if (folder / SESSION_FILE).is_file()), preferred)

    def all(self) -> list[Session]:
        """The work sessions, open ones first then closed: not main, and not the folders the sessions share."""
        return [self.load(folder) for folder in self._work_session_folders()]

    def _work_session_folders(self) -> list[Path]:
        if not self.folder.is_dir():
            return []
        open_folders = [folder for folder in sorted(self.folder.iterdir()) if folder.is_dir() and self._is_work_session(folder.name)]
        closed = self.folder / COMPLETE_FOLDER
        closed_folders = sorted(folder for folder in closed.iterdir() if folder.is_dir()) if closed.is_dir() else []
        return open_folders + closed_folders

    def _is_work_session(self, name: str) -> bool:
        return bool(name) and name != MAIN_SESSION_NAME and not name.startswith(_SHARED_FOLDER_MARK)

    def named(self, name: str) -> Session | None:
        """The session called name: the main session, or a work session, open before closed; none when there is none.
        Only that session's folder is read, so a tool that names one session does not load every other."""
        if name == MAIN_SESSION_NAME:
            return self.load(self.folder_of(name))
        if not self._is_work_session(name):
            return None
        found = next((folder for folder in (self.folder / name, self.folder / COMPLETE_FOLDER / name) if folder.is_dir()), None)
        return self.load(found) if found is not None else None

    def with_file(self, session_file: str) -> Session:
        """The session whose session.json is session_file, a path from this checkout's top or an absolute one, read
        without opening it. A board command names its ticket's session this way, because it runs in whichever chat it
        is sent to, and that chat's open session can be another."""
        named = Path(session_file)
        found = named if named.is_absolute() else self.root / named
        if not session_file or not found.is_file():
            raise SessionNotFoundError(session_file)
        return self.load(found.parent)

    def load(self, folder: Path) -> Session:
        """The session kept in folder, read without opening it: the one object these sessions hold for that folder,
        with the workpath its session.json names now, so a change saved by another process is seen."""
        session = self._held_at(Path(folder))
        stored = session.fields.get("workpath", "")
        workpath = Path(stored) if stored else self.root
        if session.workpath is None or session.work_root != workpath.resolve():
            session.workpath = workpath
        return session

    def _held_at(self, folder: Path) -> Session:
        """The one Session held for folder, made the first time it is asked for."""
        key = folder.resolve()
        with self._held_lock:
            held = self._held.get(key)
            if held is None:
                held = self._held[key] = Session(self)
                held.session_path = folder
                held.name = folder.name
            return held

    def moved(self, session: Session, moved_from: Path) -> None:
        """Hold session under the folder it moved to, such as ``.sessions/_complete/alpha``, so reading it there finds
        the same object."""
        with self._held_lock:
            self._held.pop(Path(moved_from).resolve(), None)
            self._held[session.session_path.resolve()] = session

    @property
    def open_name(self) -> str:
        """The name of the session saved as open; main when none is."""
        return self._state.session or MAIN_SESSION_NAME

    def create(self, name: str, workpath: Path, *, title: str = "", scope: str = "", parent: str = "") -> Session:
        """A new session called name, working in workpath, with the title, scope, and parent a board ticket shows saved
        in its ``session.json``; it is not opened, because a session made for later, such as a board ticket, is not the
        one being worked on."""
        session = self._held_at(self.folder / Name(name).title_slug)
        session.workpath = Path(workpath).resolve()
        session.save()
        session.save_fields(**{key: value for key, value in (("title", title), ("scope", scope), ("parent", parent)) if value})
        session.log.seed_first_loop()
        return session

    def open(self, session: Session, workpath: Path | None = None) -> Session:
        """Make session the open session of this checkout, working in workpath when one is given."""
        if workpath is not None:
            session.workpath = Path(workpath).resolve()
        session.save()
        self._state.session = "" if session.name == MAIN_SESSION_NAME else session.name
        return session

    @mcp
    @command(name="current-session")
    @agent_tool
    def current(self) -> Session:
        """The open session of this project; the main session, which works on the whole repository, when none is named."""
        return self.load(self.folder_of(self.open_name))

    @mcp
    @command(name="switch-session")
    @agent_tool
    def switch(self, name: str = "", workpath: Path | None = None) -> str:
        """Open the session called ``name``, creating its folder when missing, and save it as the open session of this project. Returns how to keep its log.

        ``name`` defaults to ``session`` in ``.sessions/session.json``, then to the saved ``branch``.
        ``workpath`` is the folder it works in; a new session works in the project's folder when none is given.
        Does not touch branches or worktrees."""
        wanted = self._name_to_switch_to(name)
        folder = self.folder_of(wanted)
        is_kept = (folder / SESSION_FILE).is_file()
        session = self.load(folder) if is_kept else self.create(wanted, workpath if workpath is not None else self.project)
        return self.open(session, workpath).log.instructions()

    def _name_to_switch_to(self, name: str) -> str:
        cleaned = Name(name or self._state.session or self._state.branch_name).title_slug
        if not cleaned:
            raise SessionNameRequiredError()
        return cleaned

    def close(self, session: Session) -> None:
        """Close session: when it is the open one, main becomes the open session."""
        if session.name != self.open_name:
            return
        self._state.session = ""


class CallSessions:
    """The sessions of every project this process serves, each made once and held while it runs, so every call in a
    session works on the session's one graph and one instance of each practice, which those sessions keep. Through them
    a tool call finds the sessions it works in: the session open in the call's project, or the one a board command names
    by its session.json; and the session open in a project for work that serves no call, such as a hook event. Each is
    the one object its sessions hold for its folder; the lines a call logs point at the call's chat through
    ``session.log.by(call.chat)``. Registered with *ToolCall* when this module is imported,
    so the framework opens a session without importing space."""

    def __init__(self) -> None:
        self._of_project: dict[Path, Sessions] = {}
        self._lock = threading.Lock()

    def of_project(self, project: Path | str) -> Sessions:
        """The sessions of project, made the first time this process works on it."""
        folder = Path(project).resolve()
        with self._lock:
            held = self._of_project.get(folder)
            if held is None:
                held = self._of_project[folder] = Sessions(folder)
            return held

    def saved_in(self, project: Path) -> Session:
        return self.of_project(project).current()

    def open_in(self, call: ToolCall) -> Session:
        return self.saved_in(call.project)

    def named_in(self, session_file: str, call: ToolCall) -> Session:
        project = call.project if call.project is not None else Path(session_file).resolve().parent
        return self.of_project(project).with_file(session_file)


# The sessions this process serves, held for as long as it runs.
SERVED_SESSIONS = CallSessions()
ToolCall.open_sessions_with(SERVED_SESSIONS)
