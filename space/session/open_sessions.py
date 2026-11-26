"""OpenSessions - which session each chat has open in one checkout, and switching a chat to another."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, ClassVar

from harness.agent_tools.tool_call import ToolCall
from harness.annotations.name import Name
from space.session.session import MAIN_SESSION_NAME, Session
from space.session.session_checkout import names_ticket
from space.session.session_record import SESSION_FILE
from space.work_state import WorkState

if TYPE_CHECKING:
    from space.session.sessions import Sessions

# The notes a switch may open its answer with, one section each, filled in with the names of the switch.
_SWITCH_NOTES_FILE = Path(__file__).parent / "SESSION-SWITCH.md"


def _switch_note(heading: str) -> str:
    """The note under heading in SESSION-SWITCH.md, the one text it holds, unfilled."""
    text = _SWITCH_NOTES_FILE.read_text(encoding="utf-8")
    section = text.split(f"\n## {heading}\n", 1)[1]
    return section.split("\n## ", 1)[0].strip()


class SessionNameRequiredError(ValueError):
    """Raised when switch-session has no name and the chat has no session or branch open."""

    def __init__(self) -> None:
        super().__init__(
            "session name is required: pass name, or switch to a branch first so "
            "the session can take its name"
        )


class UnknownSessionError(LookupError):
    """Raised when a chat switches to a name no session has and did not ask for it to be made, such as a misspelt name:
    it names the name asked for and the sessions there are, and nothing is made or opened."""

    def __init__(self, name: str, there: list[str]) -> None:
        super().__init__(
            f"no session is called {name}; the sessions there are: {', '.join(there)}. Switch to one of them, or pass "
            f"create to make a session called {name}"
        )
        self.name = name
        self.there = there


# What a module outside the session does when a chat opens a session, such as queueing its latest handoff's steps on
# that chat's prompt queue: handed the session and the chat's id, it answers what the chat is told, empty for nothing.
SessionOpenedListener = Callable[[Session, str], str]


class OpenSessions:
    """*OpenSessions* are which session each chat has open in one checkout, kept by the cdd server under ``~/.cdd``
    (*WorkState*), never in the checkout: the chat a call comes from keeps its own, and a call naming no chat keeps one
    for the checkout folder. ``main`` is open when no other is, and a chat in a ticket's own worktree always works on
    that ticket. The open session is read each time it is asked for, so a switch or a close made through another client
    of the same chat is seen at once."""

    # Every listener a module registered (``on_session_opened``), for every checkout's sessions in this process.
    _opened_listeners: ClassVar[list[SessionOpenedListener]] = []

    def __init__(self, sessions: Sessions) -> None:
        self._sessions = sessions

    @classmethod
    def on_session_opened(cls, listener: SessionOpenedListener) -> None:
        """Call listener each time a chat switches to a session, and tell the chat what it answers: a module outside
        the session, such as tools/prompt_queue, registers here when it is imported, so the session imports none."""
        cls._opened_listeners.append(listener)

    def _told_on_opening(self, session: Session, chat: str) -> str:
        return "".join(listener(session, chat) for listener in self._opened_listeners)

    def state(self, chat: str) -> WorkState:
        """What chat keeps open, under ``~/.cdd``: an empty chat is a call that names none, which keeps this checkout
        folder's own entry."""
        return WorkState(self._sessions.root, chat)

    def name_for(self, chat: str) -> str:
        """The name of the session chat works on: the ticket of the worktree these sessions serve, whatever any chat
        chose to open; else the session chat has open; main when none is."""
        ticket = self._ticket_of_worktree()
        if ticket is not None:
            return ticket.name
        chosen = self.state(chat).session
        # Another chat may have closed the chosen session since. Working on it would write its folder back among the
        # open sessions, where the board lists it again, so a chat whose session was closed works on main.
        if not chosen or self._is_closed_since(chosen):
            return MAIN_SESSION_NAME
        return chosen

    def _is_closed_since(self, name: str) -> bool:
        sessions = self._sessions
        open_folder = sessions.folder_of(name)
        return (not open_folder.is_dir() or sessions.listing.is_left_behind(open_folder)) and (sessions.closed_folder / name).is_dir()

    def open(self, session: Session, chat: str) -> Session:
        """Make session the one chat has open. Nothing is written in the checkout: the choice is kept under ``~/.cdd``."""
        self.state(chat).session = "" if session.name == MAIN_SESSION_NAME else session.name
        return session

    def current(self, chat: str) -> Session:
        """The session chat has open; main when none is."""
        sessions = self._sessions
        return sessions.held.load(sessions.folder_of(self.name_for(chat)))

    def close(self, session: Session, chat: str) -> None:
        """Close session for chat: when it is the one chat has open, main becomes its open session."""
        state = self.state(chat)
        if session.name != (state.session or MAIN_SESSION_NAME):
            return
        state.session = ""

    def _ticket_of_worktree(self) -> Session | None:
        """The ticket whose own worktree these sessions serve: a chat there works on that ticket, whatever any chat
        chose to open. None in the repository's own folder, and in a worktree whose branch names no ticket."""
        sessions = self._sessions
        repo = sessions.repo
        if not repo.is_linked_worktree or not repo.is_on_branch:
            # A worktree on no branch, such as one detached at a commit, names no ticket.
            return None
        branch = repo.current_branch.name
        tickets = sessions.listing.open_names()
        if branch in tickets:
            return sessions.named(branch)
        # The Claude desktop app names a branch around the ticket's name, such as claude/checkout-flow-cef4bc.
        holding = [name for name in tickets if names_ticket(branch, name)]
        return sessions.named(holding[0]) if len(holding) == 1 else None

    def switch(self, name: str, workpath: Path | None, create: bool, call: ToolCall | None) -> SwitchedSession:
        """Open the session called name for the call's chat; a name no session has is made only when create asks for
        it, else refused with ``UnknownSessionError`` before anything is made. A chat in a ticket's own worktree always
        opens that ticket's session. Answers the switch, which says what the chat is told."""
        sessions = self._sessions
        chat = call.chat_id if call is not None else ""
        ticket = self._ticket_of_worktree()
        if ticket is not None:
            opened = self.open(ticket, chat)
            return SwitchedSession(opened, self._told_on_opening(opened, chat), asked_in_ticket_worktree=name)
        wanted = self._name_to_switch_to(name, chat)
        folder = sessions.folder_of(wanted)
        is_kept = (folder / SESSION_FILE).is_file() or wanted == MAIN_SESSION_NAME
        if not is_kept and not create:
            raise UnknownSessionError(wanted, [MAIN_SESSION_NAME, *sorted(sessions.listing.open_names())])
        session = sessions.held.load(folder) if is_kept else sessions.create(wanted, workpath)
        opened = self.open(session, chat)
        return SwitchedSession(opened, self._told_on_opening(opened, chat), chat_works_in=call.project if call is not None else None)

    def _name_to_switch_to(self, name: str, chat: str) -> str:
        cleaned = Name(name or self.state(chat).session).title_slug
        if not cleaned:
            raise SessionNameRequiredError()
        return cleaned


class SwitchedSession:
    """*SwitchedSession* is one switch of a chat to a session: the session opened, what the modules listening for an
    opening told the chat (``OpenSessions.on_session_opened``), and what the chat must know before it works there: the
    ticket whose own worktree it works in when it asked for another, the session's own worktree when the chat works
    elsewhere, and the practices whose roots nobody set. ``instructions`` says it in SESSION-SWITCH.md's words, before
    how to keep the session's log."""

    def __init__(self, session: Session, told_on_opening: str, *, asked_in_ticket_worktree: str | None = None,
                 chat_works_in: Path | None = None) -> None:
        self.session = session
        self.told_on_opening = told_on_opening
        # The name the chat asked for, when it works in the opened ticket's own worktree; None for any other switch.
        self._asked_in_ticket_worktree = asked_in_ticket_worktree
        # The folder the chat works in, when the call named one.
        self._chat_works_in = chat_works_in

    @property
    def opened_in_worktree_of(self) -> str:
        """The ticket the chat opened in place of the session it asked for, since it works in that ticket's own
        worktree; empty when it asked for none, for that ticket, or switched anywhere else."""
        asked = self._asked_in_ticket_worktree
        cleaned = Name(asked).title_slug if asked else ""
        return self.session.name if cleaned and cleaned != self.session.name else ""

    @property
    def outside_worktree(self) -> Path | None:
        """The session's own worktree, when the chat works in another folder, where work done would land in the wrong
        place; None when the chat works there, the session has none, or it is main."""
        works_in = self._chat_works_in
        if works_in is None or self.session.name == MAIN_SESSION_NAME:
            return None
        own = self.session.checkout.own_worktree
        worktree = own.root if own is not None else None
        if worktree is None or worktree == works_in or worktree in works_in.parents:
            return None
        return worktree

    @property
    def default_roots(self) -> list[str]:
        """Each practice the session works on whose root nobody set, with the default folder it writes under; none for
        main."""
        if self.session.name == MAIN_SESSION_NAME:
            return []
        return [f"{key} → {practice.root}" for key, practice in self.session.own_practices.items() if practice.enabled and practice.is_root_default]

    @property
    def instructions(self) -> str:
        """What the chat is told: the notes that apply, in SESSION-SWITCH.md's order, then how to keep the session's log."""
        said = []
        if self.opened_in_worktree_of:
            asked = Name(self._asked_in_ticket_worktree or "").title_slug
            said.append(_switch_note("Worktree ticket").format(ticket=self.session.name, asked=asked) + "\n\n")
        if self.outside_worktree is not None:
            said.append(_switch_note("Outside worktree").format(chat=self._chat_works_in, session=self.session.name, worktree=self.outside_worktree) + "\n\n")
        said.append(self.told_on_opening)
        if self.default_roots:
            said.append(_switch_note("Default roots").format(roots=", ".join(self.default_roots)) + "\n\n")
        return "".join(said) + self.session.log.instructions()
