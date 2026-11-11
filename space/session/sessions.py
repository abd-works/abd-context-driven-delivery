"""Sessions - the work sessions of one checkout, kept in its ``.sessions`` folder, and which of them is open."""

from __future__ import annotations

import re
import threading
import time
from functools import cached_property
from pathlib import Path

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.catalog_generator.catalog_practice import CatalogPractice
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.installation.files import command
from harness.mcp.mcp_server import mcp
from harness.annotations.name import Name
from space.repo.repo import Repo
from space.session.file_manager import FileManager
from space.session.session import COMPLETE_FOLDER, MAIN_SESSION_NAME, SESSION_FILE, Session, SessionNotFoundError
from space.work_state import SESSIONS_FOLDER, WorkState

BACKLOG_FOLDER = "_backlog"
# Folders in `.sessions` whose names start with this are the ones the sessions share, such as the backlog.
_SHARED_FOLDER_MARK = "_"
# How long one ``git worktree list`` answers for, so a board read that loads every session asks git once.
_WORKTREE_LISTING_SECONDS = 2.0
_BRANCH_REF = "refs/heads/"


class SessionNameRequiredError(ValueError):
    """Raised when switch-session has no name and the chat has no session or branch open."""

    def __init__(self) -> None:
        super().__init__(
            "session name is required: pass name, or switch to a branch first so "
            "the session can take its name"
        )


class PracticeNotFoundError(LookupError):
    """Raised when a caller names a practice, such as clean_engineering, that the board or ticket does not have. It
    names the practice and what was searched for it."""

    def __init__(self, practice: str, within: str) -> None:
        self.practice = practice
        self.within = within
        super().__init__(f"no practice named {practice!r} on {within}")


class BoardPractices:
    """*BoardPractices* are the practices a checkout's session board works through, each as the catalog shows it: its
    name, colour, fidelities, pages, and skills. They are the same for every session, so they are made once for the
    checkout and kept by its *Sessions*; every board read asks them for a practice by its class, which the board's own
    instance and each session's share, rather than searching the list again."""

    def __init__(self, catalogued: list[CatalogPractice]) -> None:
        # Each practice's catalog view by the practice's class, in the order the board shows them.
        self._by_class = {type(entry.practice): entry for entry in catalogued}

    @property
    def catalogued(self) -> list[CatalogPractice]:
        """The catalog's view of each practice, in the order the board shows them."""
        return list(self._by_class.values())

    def of(self, kind: type) -> CatalogPractice:
        """The catalog's view of the practice of class kind, the class of the board's own instance and of every
        session's."""
        found = self._by_class.get(kind)
        if found is None:
            raise PracticeNotFoundError(kind.__name__, "the board")
        return found

    def works_through(self, kind: type) -> bool:
        """Whether the practice of class kind is one the board works through."""
        return kind in self._by_class

    def keyed(self, key: str) -> CatalogPractice:
        """The catalog's view of the board's practice whose folder name is key, such as clean_engineering, as a tool
        names it."""
        found = next((entry for entry in self._by_class.values() if entry.practice.key == key), None)
        if found is None:
            raise PracticeNotFoundError(key, "the board")
        return found


@agent_toolset
class Sessions:
    """The work sessions of one checkout: open ones in ``.sessions/{name}/``, closed ones in ``.sessions/_complete/``.
    Which one is open is kept per chat by the cdd server under ``~/.cdd`` (*WorkState*), never in the checkout: the
    chat a call comes from keeps its own, and a call naming no chat keeps one for this checkout folder. ``main`` works
    on the whole repository and is open when no other is. The open session is read each time it is asked for, so a
    switch or a close made through another client of the same chat is seen at once.

    One *Session* is kept here for each session folder, made the first time it is read and read again from its folder
    on each ask, so every call in a session, from any chat, works on the same object, which holds that session's graph
    and its one instance of each practice. A call's chat is the call's own: the lines it logs go through
    ``session.log.by(chat)``."""

    def __init__(self, project: Path | str) -> None:
        # The checkout holding the project, made once: every session this loads works in it.
        self.repo = Repo.of_project(project)
        self.root = self.repo.root
        # One ``git worktree list``, read again after a moment, from which each session's root is derived.
        self._worktree_listing: tuple[float, dict[str, Path]] = (0.0, {})
        self._held: dict[Path, Session] = {}
        self._held_lock = threading.Lock()

    @classmethod
    @tool_subject
    def of_project(cls, project: Path) -> Sessions:
        """The sessions of project, the project the running call names, as this process holds them between calls."""
        return SERVED_SESSIONS.of_project(project)

    @cached_property
    def board_practices(self) -> BoardPractices:
        """Every practice CDD has, as the catalog shows it, made once for this checkout's board with the one skill
        install their slash commands are named by: what the board shows of a practice, its name, colour, fidelities,
        pages, and skills, is the same for every session, so no single session's instances stand for it, and no other
        reader changes these. The board is made again for every call, so it is held here, where the process keeps the
        checkout's sessions."""
        return BoardPractices(CatalogPractice.of_practices(PracticeCatalogue.create_all()))

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
    def backlog_folder(self) -> Path:
        """Where sessions wait before work starts, and where a session moved back is held."""
        return self.folder / BACKLOG_FOLDER

    def folder_of(self, name: str) -> Path:
        """The folder of the session called name, in the repository's own ``.sessions``."""
        return self.folder / name

    def all(self) -> list[Session]:
        """Every session the board shows: main first, the default session that works on the whole repository, then the
        work sessions, open ones before closed; never the folders the sessions share."""
        return [self.load(self.folder_of(MAIN_SESSION_NAME)), *(self.load(folder) for folder in self._work_session_folders())]

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
        working in the root ``root_of`` derives now, so a worktree opened or a workpath chosen since is seen."""
        session = self._held_at(Path(folder))
        workpath = self.root_of(session)
        if session.workpath is None or session.work_root != workpath:
            session.workpath = workpath
        return session

    def root_of(self, session: Session) -> Path:
        """Where session writes, derived when asked and never saved on a switch: a workpath a person chose by hand in
        its session.json, else its own worktree as git lists it, else this checkout."""
        stored = str(session.fields.get("workpath", "") or "").strip()
        chosen = Path(stored).resolve() if stored else None
        # WHY: older switches saved the checkout itself, or a worktree since removed, as the workpath; neither was chosen.
        if chosen is not None and chosen.is_dir() and chosen not in (self.root, self.repo.main_clone.root):
            return chosen
        if session.name and session.name != MAIN_SESSION_NAME:
            worktree = self._worktree_of(session.name)
            if worktree is not None:
                return worktree
        return self.root

    def _worktree_of(self, name: str) -> Path | None:
        """The linked worktree of the branch called name, else of the one branch whose name holds name as a whole word,
        as git lists them now."""
        listed = self._worktrees_by_branch()
        if name in listed:
            return listed[name]
        word = re.compile(rf"(^|[/_-]){re.escape(name)}($|[/_-])")
        matches = [folder for branch, folder in listed.items() if word.search(branch)]
        return matches[0] if len(matches) == 1 else None

    def _worktrees_by_branch(self) -> dict[str, Path]:
        read_at, listed = self._worktree_listing
        if read_at and time.monotonic() - read_at < _WORKTREE_LISTING_SECONDS:
            return listed
        main = self.repo.main_clone.root
        try:
            listing = self.repo.main_clone.git.run("worktree", "list", "--porcelain")
        except (RuntimeError, OSError):  # a folder in no repository has no worktrees
            listing = ""
        listed = {}
        for block in listing.split("\n\n"):
            fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
            folder = Path(fields["worktree"]).resolve() if fields.get("worktree") else None
            branch = fields.get("branch", "").removeprefix(_BRANCH_REF)
            if folder is not None and branch and folder != main and folder.is_dir():
                listed[branch] = folder
        self._worktree_listing = (time.monotonic(), listed)
        return listed

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

    def removed(self, session: Session) -> None:
        """Hold session no more, its folder deleted."""
        with self._held_lock:
            self._held.pop(session.session_path.resolve(), None)

    def open_state(self, chat: str = "") -> WorkState:
        """What chat keeps open, under ``~/.cdd``: the chat named, else the chat of the call being answered, else this
        checkout folder's own entry, for a call that names no chat."""
        if not chat:
            call = ToolCall.answering()
            chat = call.chat_id if call is not None else ""
        return WorkState(self.root, chat)

    def open_name_for(self, chat: str = "") -> str:
        """The name of the session chat has open; main when none is."""
        return self.open_state(chat).session or MAIN_SESSION_NAME

    @property
    def open_name(self) -> str:
        """The name of the session open for the call being answered; main when none is."""
        return self.open_name_for()

    def create(self, name: str, workpath: Path | None = None, *, title: str = "", scope: str = "", parent: str = "") -> Session:
        """A new session called name, its name, title, scope, and parent written once in its ``session.json``. workpath
        is kept only when it is a folder chosen other than this checkout, since the root is otherwise derived. It is not
        opened, because a session made for later, such as a board ticket, is not the one being worked on."""
        session = self._held_at(self.folder / Name(name).title_slug)
        chosen = Path(workpath).resolve() if workpath is not None else None
        kept = chosen if chosen is not None and chosen != self.root else None
        fields = (("name", session.name), ("title", title), ("scope", scope), ("parent", parent), ("workpath", str(kept) if kept else ""))
        session.save_fields(**{key: value for key, value in fields if value})
        session.workpath = self.root_of(session)
        session.log.seed_first_loop()
        return session

    def open(self, session: Session, chat: str = "") -> Session:
        """Make session the one chat has open. Nothing is written in the checkout: the choice is kept under ``~/.cdd``."""
        self.open_state(chat).session = "" if session.name == MAIN_SESSION_NAME else session.name
        return session

    @mcp
    @command(name="current-session")
    @agent_tool
    def current(self, call: ToolCall | None = None) -> Session:
        """The open session of this chat; the main session, which works on the whole repository, when none is named."""
        ticket = self._ticket_of_worktree()
        if ticket is not None:
            return ticket
        return self.load(self.folder_of(self.open_name_for(call.chat_id if call is not None else "")))

    def _ticket_of_worktree(self) -> Session | None:
        """The ticket whose own worktree these sessions serve: a chat there works on that ticket, whatever any chat
        chose to open. None in the repository's own folder, and in a worktree whose branch names no ticket."""
        if not self.repo.is_linked_worktree() or not self.repo.git.succeeds("symbolic-ref", "-q", "HEAD"):
            # A worktree on no branch, such as one detached at a commit, names no ticket.
            return None
        branch = self.repo.current_branch.name
        tickets = self._open_ticket_names()
        if branch in tickets:
            return self.named(branch)
        # The Claude desktop app names a branch around the ticket's name, such as claude/checkout-flow-cef4bc.
        holding = [name for name in tickets if re.search(rf"(^|[/_-]){re.escape(name)}($|[/_-])", branch)]
        return self.named(holding[0]) if len(holding) == 1 else None

    def _open_ticket_names(self) -> list[str]:
        """The names of the open work sessions in the repository's own .sessions."""
        if not self.folder.is_dir():
            return []
        return [folder.name for folder in self.folder.iterdir() if folder.is_dir() and self._is_work_session(folder.name)]

    @mcp
    @command(name="switch-session")
    @agent_tool
    def switch(self, name: str = "", workpath: Path | None = None, call: ToolCall | None = None) -> str:
        """Open the session called ``name`` for this chat, creating its folder when missing. Returns how to keep its log.

        ``name`` defaults to the session this chat has open, then to its open ``branch``.
        ``workpath`` is a folder a new session works in; without one its root is derived: its worktree, else the checkout.
        A switch writes nothing in the checkout and does not touch branches or worktrees."""
        chat = call.chat_id if call is not None else ""
        wanted = self._name_to_switch_to(name, chat)
        folder = self.folder_of(wanted)
        is_kept = (folder / SESSION_FILE).is_file() or wanted == MAIN_SESSION_NAME
        session = self.load(folder) if is_kept else self.create(wanted, workpath)
        return self.open(session, chat).log.instructions()

    def _name_to_switch_to(self, name: str, chat: str = "") -> str:
        state = self.open_state(chat)
        cleaned = Name(name or state.session).title_slug
        if not cleaned:
            raise SessionNameRequiredError()
        return cleaned

    def close(self, session: Session) -> None:
        """Close session: when it is the one the call's chat has open, main becomes its open session."""
        state = self.open_state()
        if session.name != (state.session or MAIN_SESSION_NAME):
            return
        state.session = ""


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
        """The sessions of the checkout holding project, made the first time this process works in it. They are held by
        the checkout's top, as its one Repo is, so a call naming a folder inside the checkout, or a session.json with no
        project, reaches the same sessions, and through them the one Session of each folder."""
        repo = Repo.of_project(project)
        with self._lock:
            held = self._of_project.get(repo.root)
            if held is None:
                held = self._of_project[repo.root] = Sessions(repo.root)
            return held

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
ToolCall.open_sessions_with(SERVED_SESSIONS)
