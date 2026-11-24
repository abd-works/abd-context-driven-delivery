"""Sessions - the work sessions of one checkout, kept in its ``.sessions`` folder, and which of them is open."""

from __future__ import annotations

import threading
from functools import cached_property
from pathlib import Path

from harness.installation.json_file import JsonFileUnreadable
from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.agent_tools.tool_call import SESSION_OPENING, ToolCall
from harness.installation.files import command
from harness.mcp.mcp_annotations import mcp
from harness.annotations.name import Name
from space.repo.repo import Repo
from space.session.files.file_manager import FileManager
from space.session.session_saves import SERVED_SAVES, SessionSaves
from harness.process.answer_reads import ServedAnswers
from space.session.open_sessions import OpenSessions
from space.session.session import MAIN_SESSION_NAME, Session, SessionNotFoundError
from space.session.session_record import SESSION_FILE, SessionFields
from space.session.checkout_worktrees import CheckoutWorktrees
from space.work_state import COMPLETE_FOLDER, SESSIONS_FOLDER

BACKLOG_FOLDER = "_backlog"
# Folders in `.sessions` whose names start with this are the ones the sessions share, such as the backlog.
_SHARED_FOLDER_MARK = "_"
@agent_toolset
class Sessions:
    """The work sessions of one checkout: open ones in ``.sessions/{name}/``, closed ones in ``.sessions/_complete/``.
    Which one each chat has open is its part *OpenSessions* (``sessions.opened``); ``main`` works on the whole
    repository and is open when no other is. Whether the process is giving an answer from them, which their sessions
    hold what they read for, is its part *ServedAnswers* (``sessions.answers``).

    One *Session* is kept here for each session folder, made the first time it is read and read again from its folder
    on each ask, so every call in a session, from any chat, works on the same object, which holds that session's graph
    and its one instance of each practice. A call's chat is the call's own: the lines it logs go through
    ``session.log.by(chat)``."""

    def __init__(self, project: Path | str) -> None:
        # The checkout holding the project, made once: every session this loads works in it.
        self.repo = Repo.of_project(project)
        self.root = self.repo.root
        # The worktrees and branches each session's checkout is found among, listed once and read again after a moment.
        self.worktrees = CheckoutWorktrees(self)
        # Which folders in ``.sessions`` hold a session, and the one Session held for each.
        self.listing = SessionListing(self)
        self.held = HeldSessions(self)
        # The answer the process gives from these sessions, while it serves calls from them (*CallSessions*).
        self.answers = ServedAnswers()
        # Which session each chat has open in this checkout, and switching a chat to another.
        self.opened = OpenSessions(self)

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
        """The `.sessions` folder that holds the sessions and what they share on the board: the repository's own, in its
        main clone, whichever checkout these sessions serve. A ticket's record stays on main, and its worktree's branch
        carries only the work."""
        return self.repo.main_clone.root / SESSIONS_FOLDER

    @property
    def saves(self) -> SessionSaves:
        """The commits that keep the sessions' records on main, shared with every checkout of the repository."""
        return SERVED_SAVES.of(self.repo.main_clone, self.folder)

    @property
    def backlog_folder(self) -> Path:
        """Where sessions wait before work starts, and where a session moved back is held."""
        return self.folder / BACKLOG_FOLDER

    @property
    def closed_folder(self) -> Path:
        """Where closed sessions are kept, each in its own folder under its name."""
        return self.folder / COMPLETE_FOLDER

    def folder_of(self, name: str) -> Path:
        """The folder of the session called name, in the repository's own ``.sessions``."""
        return self.folder / name

    def all(self) -> list[Session]:
        """Every session the board shows: main first, the default session that works on the whole repository, then the
        work sessions, open ones before closed; never the folders the sessions share."""
        return [self.held.load(folder) for folder in self._shown_folders()]

    def _shown_folders(self) -> list[Path]:
        return [self.folder_of(MAIN_SESSION_NAME), *self.listing.work_folders()]

    def read_apart(self) -> SessionsRead:
        """Every session ``all`` lists whose session.json reads, with the failure of each one that does not, such as a
        file cut off half way: a reader that shows many sessions, such as the board, shows the rest and names the file,
        where ``all`` stops at the first."""
        read = SessionsRead()
        for folder in self._shown_folders():
            try:
                read.sessions.append(self.held.load(folder))
            except JsonFileUnreadable as failure:
                read.failures.append(failure)
        return read

    def named(self, name: str) -> Session | None:
        """The session called name: the main session, or a work session, open before closed; none when there is none.
        Only that session's folder is read, so a tool that names one session does not load every other."""
        found = self.folder_named(name)
        return self.held.load(found) if found is not None else None

    def folder_named(self, name: str) -> Path | None:
        """The record folder of the session called name: main's, or a work session's, open before closed; none when
        there is none."""
        if name == MAIN_SESSION_NAME:
            return self.folder_of(name)
        if not self.listing.is_work_session(name):
            return None
        open_folder = self.folder / name
        candidates = (open_folder, self.closed_folder / name) if self.listing.is_open(open_folder) else (self.closed_folder / name,)
        return next((folder for folder in candidates if folder.is_dir()), None)

    def with_file(self, session_file: str) -> Session:
        """The session whose session.json is session_file, a path from this checkout's top or an absolute one, read
        without opening it. A board command names its ticket's session this way, because it runs in whichever chat it
        is sent to, and that chat's open session can be another. The main session always exists, as ``named`` and
        ``switch`` treat it, so its own session.json path finds it before anything has written that file. A bare name,
        such as ``checkout-flow``, finds the session ``named`` finds, as ``switch`` opens it by that name."""
        if self._is_bare_name(session_file):
            return self._by_name(session_file)
        named = Path(session_file)
        found = named if named.is_absolute() else self.root / named
        is_main = found.name == SESSION_FILE and found.parent.resolve() == self.folder_of(MAIN_SESSION_NAME).resolve()
        if not session_file or not (found.is_file() or is_main):
            raise SessionNotFoundError(session_file)
        return self.held.load(found.parent)

    def _is_bare_name(self, session_file: str) -> bool:
        return bool(session_file) and Path(session_file).name == session_file and session_file != SESSION_FILE

    def _by_name(self, name: str) -> Session:
        found = self.named(name)
        if found is None:
            raise SessionNotFoundError(name)
        return found

    def create(self, name: str, workpath: Path | None = None, *, title: str = "", scope: str = "", parent: str = "") -> Session:
        """A new session called name, its name, title, scope, and parent written once in its ``session.json``. workpath
        is kept only when it is a folder chosen other than this checkout, since the root is otherwise derived. It is not
        opened, because a session made for later, such as a board ticket, is not the one being worked on."""
        session = self.held.at(self.folder / Name(name).title_slug)
        chosen = Path(workpath).resolve() if workpath is not None else None
        kept = self.repo.path_from_top(chosen) if chosen is not None and chosen != self.root else ""
        given = {key: value for key, value in (("name", session.name), ("title", title), ("scope", scope), ("parent", parent), ("workpath", kept)) if value}

        def made(fields: SessionFields) -> None:
            for key, value in given.items():
                setattr(fields, key, value)

        session.record.update(made, ", ".join(f"{key} {value}" for key, value in given.items()))
        session.placed()
        session.log.seed_first_loop()
        return session

    @mcp
    @command(name="current-session")
    @agent_tool
    def current(self, call: ToolCall | None = None) -> Session:
        """The open session of this chat; the main session, which works on the whole repository, when none is named."""
        return self.opened.current(call.chat_id if call is not None else "")

    @mcp
    @command(name="switch-session")
    @agent_tool
    def switch(self, name: str = "", workpath: Path | None = None, create: bool = False, call: ToolCall | None = None) -> str:
        """Open the session called ``name`` for this chat. Returns how to keep its log.

        ``name`` defaults to the session this chat has open, then to its open ``branch``.
        A name no session has is refused, naming the sessions there are, so a misspelt name never makes a session and a
        card on the board nobody asked for; pass ``create`` true only when the person asked for a new session, and it
        makes the session's folder.
        ``workpath`` is a folder a new session works in; without one its root is derived: its worktree, else the checkout.
        A switch writes nothing in the checkout and does not touch branches or worktrees: when the session has its own
        worktree and the call's chat works elsewhere, the answer opens by saying to start a chat in that worktree.
        A chat in a ticket's own worktree always opens that ticket's session, whatever name it asks for, because the
        worktree holds only that ticket's work; the answer says so when it asked for another."""
        return self.opened.switch(name, workpath, create, call).instructions


class SessionsRead:
    """*SessionsRead* is one read of a checkout's sessions that went on past a session.json it could not read: the
    sessions that read, in the board's order, and the failure of each that did not, which names its file."""

    def __init__(self) -> None:
        self.sessions: list[Session] = []
        self.failures: list[JsonFileUnreadable] = []


class SessionListing:
    """Which folders in a checkout's ``.sessions`` hold a session: main, the open work sessions, and the closed ones,
    never the folders the sessions share or what a closed session left behind among the open ones."""

    def __init__(self, sessions: Sessions) -> None:
        self._sessions = sessions

    def work_folders(self) -> list[Path]:
        if not self._sessions.folder.is_dir():
            return []
        open_folders = [folder for folder in sorted(self._sessions.folder.iterdir()) if self.is_open(folder)]
        closed = self._sessions.closed_folder
        closed_folders = sorted(folder for folder in closed.iterdir() if folder.is_dir()) if closed.is_dir() else []
        return open_folders + closed_folders

    def is_work_session(self, name: str) -> bool:
        return bool(name) and name != MAIN_SESSION_NAME and not name.startswith(_SHARED_FOLDER_MARK)

    def is_open(self, folder: Path) -> bool:
        return folder.is_dir() and self.is_work_session(folder.name) and not self.is_left_behind(folder)

    def is_left_behind(self, folder: Path) -> bool:
        """Whether folder, among the open sessions, is only what a closed session of its name left there, such as a
        progress cache written before its move or a folder Windows would not let go of: it holds no session.json, and
        the session is kept among the closed ones. The board would otherwise list that session twice."""
        return not (folder / SESSION_FILE).is_file() and (self._sessions.closed_folder / folder.name).is_dir()

    def open_names(self) -> list[str]:
        """The names of the open work sessions in the repository's own .sessions."""
        if not self._sessions.folder.is_dir():
            return []
        return [folder.name for folder in self._sessions.folder.iterdir() if self.is_open(folder)]


class HeldSessions:
    """The one *Session* a checkout's sessions hold for each record folder, made the first time it is read, so every
    call in a session, from any chat, works on the same object, and held under the record folder it moves to."""

    def __init__(self, sessions: Sessions) -> None:
        self._sessions = sessions
        self._held: dict[Path, Session] = {}
        self._held_lock = threading.Lock()

    def load(self, folder: Path) -> Session:
        """The session whose record folder is folder, read without opening it: the one object these sessions hold for
        that folder, placed where it works now, so a worktree opened or a workpath chosen since is seen."""
        return self.at(Path(folder)).placed()

    def at(self, folder: Path) -> Session:
        """The one Session held for the record folder folder, made the first time it is asked for, its work kept beside
        its record until it is placed."""
        key = folder.resolve()
        with self._held_lock:
            held = self._held.get(key)
            if held is None:
                held = self._held[key] = Session(self._sessions, folder)
            return held

    def moved(self, session: Session, moved_from: Path) -> None:
        """Hold session under the record folder it moved to, such as ``.sessions/_complete/alpha``, so reading it there
        finds the same object."""
        with self._held_lock:
            self._held.pop(Path(moved_from).resolve(), None)
            self._held[session.record_folder.resolve()] = session

    def removed(self, session: Session) -> None:
        """Hold session no more, its folders deleted."""
        with self._held_lock:
            self._held.pop(session.record_folder.resolve(), None)


class CallSessions:
    """The sessions of every project this process serves, each made once and held while it runs, so every call in a
    session works on the session's one graph and one instance of each practice, which those sessions keep. Through them
    a tool call finds the sessions it works in: the session open in the call's project, or the one a board command names
    by its session.json; and the session open in a project for work that serves no call, such as a hook event. Each is
    the one object its sessions hold for its folder; the lines a call logs point at the call's chat through
    ``session.log.by(call.request.chat)``. Registered with ``SESSION_OPENING`` when this module is imported,
    so the framework opens a session without importing space."""

    def __init__(self) -> None:
        self._of_project: dict[Path, Sessions] = {}
        self._lock = threading.Lock()

    def of_project(self, project: Path | str) -> Sessions:
        """The sessions of the checkout holding project, made the first time this process works in it. They are held by
        the checkout's top, as its one Repo is, so a call naming a folder inside the checkout, or a session.json with no
        project, reaches the same sessions, and through them the one Session of each folder."""
        repo = Repo.of_project(project)
        with self._lock:
            held = self._of_project.get(repo.root)
            if held is None:
                held = self._of_project[repo.root] = Sessions(repo.root)
        # Each call, and each hook event, finds its sessions here, so each begins an answer of its own.
        held.answers.begin()
        return held

    def forget_under(self, folder: Path) -> None:
        """Let go of the sessions of every checkout inside folder, such as a spec's throwaway project once it is removed,
        so their graphs and practices are not kept for as long as the process runs; a later call in a project there
        makes its sessions again."""
        top = folder.resolve()
        with self._lock:
            for root in [root for root in self._of_project if root.is_relative_to(top)]:
                del self._of_project[root]

    def saved_in(self, project: Path) -> Session:
        return self.of_project(project).current()

    def open_in(self, call: ToolCall) -> Session:
        """The session the call's chat has open, read from the checkout the chat works in: a chat whose ticket is open
        in its own worktree keeps that session's details in the worktree's ``.sessions``."""
        return self.of_project(call.project).current(call)

    def named_in(self, session_file: str, call: ToolCall) -> Session:
        project = call.project if call.project is not None else Path(session_file).resolve().parent
        return self.of_project(project).with_file(session_file)


# The sessions this process serves, held for as long as it runs.
SERVED_SESSIONS = CallSessions()
SESSION_OPENING.open_with(SERVED_SESSIONS)
