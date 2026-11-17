"""OpenSessions - which session each chat has open in one checkout, and switching a chat to another."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.tool_call import CALLS_BEING_ANSWERED, ToolCall
from harness.annotations.name import Name
from space.session.session import MAIN_SESSION_NAME, Session
from space.session.session_folder import COMPLETE_FOLDER
from space.session.session_record import SESSION_FILE
from space.work_state import WorkState
from tools.prompt_queue.prompt_queue import PromptQueue

if TYPE_CHECKING:
    from space.session.sessions import Sessions

# Said first when a chat switches to a session whose own worktree is not where the chat works: work done here would
# land in the wrong folder.
_OUTSIDE_WORKTREE_NOTE = (
    "This chat works in {chat}, but {session}'s worktree is {worktree}. Do this session's work in a chat started there "
    "(start_session with cwd {worktree}), not in this chat.\n\n"
)
_HANDOFF_QUEUED_NOTE = (
    "**Handoff queued.** The {count} steps of {handoff}'s Approach for Next Agent are on this chat's prompt queue, in "
    "order: the prompt-queue mod sends the next one as each turn ends while it plays, and prompt-queue.show lists "
    "them.\n\n"
)
_DEFAULT_ROOTS_NOTE = (
    "**Output roots.** These practices write under their default folders, which nobody has checked: {roots}. Before "
    "generating anything, set up the session's roots with session.set_up_roots, so they cover exactly the pieces the "
    "ticket works on in every practice. A practice's documents and its code or tests can sit in different areas, each "
    "where the practice's declared outputs place them, and the pieces of one ticket are spread across them: a domain "
    "folder, the package that implements it, the story tests that cover it. Propose the roots from what the ticket "
    "names and what its branch changed (fidelity-session-output.propose_roots answers the folders each fidelity "
    "proposes), dig down to the most local folder that holds each piece rather than a parent that also holds its "
    "siblings, and confirm them with the person before setting any. Then set them: "
    "practice-session-output.choose_root for the practice's own root, fidelity-session-output.choose_root for a "
    "fidelity kept apart, and fidelity-session-output.add_root for each further folder beside it, so the Files app, the "
    "board and validate show this ticket's files and new work lands beside them. Leave a default that already holds "
    "them, or where none exist yet.\n\n"
)
_WORKTREE_TICKET_NOTE = (
    "This chat works in {ticket}'s own worktree, so its session is {ticket}, not {asked}. To work on {asked}, open it "
    "from the main chat.\n\n"
)


class SessionNameRequiredError(ValueError):
    """Raised when switch-session has no name and the chat has no session or branch open."""

    def __init__(self) -> None:
        super().__init__(
            "session name is required: pass name, or switch to a branch first so "
            "the session can take its name"
        )


class OpenSessions:
    """*OpenSessions* are which session each chat has open in one checkout, kept by the cdd server under ``~/.cdd``
    (*WorkState*), never in the checkout: the chat a call comes from keeps its own, and a call naming no chat keeps one
    for the checkout folder. ``main`` is open when no other is, and a chat in a ticket's own worktree always works on
    that ticket. The open session is read each time it is asked for, so a switch or a close made through another client
    of the same chat is seen at once."""

    def __init__(self, sessions: Sessions) -> None:
        self._sessions = sessions

    def state(self, chat: str = "") -> WorkState:
        """What chat keeps open, under ``~/.cdd``: the chat named, else the chat of the call being answered, else this
        checkout folder's own entry, for a call that names no chat."""
        if not chat:
            call = CALLS_BEING_ANSWERED.current
            chat = call.chat_id if call is not None else ""
        return WorkState(self._sessions.root, chat)

    def name_for(self, chat: str = "") -> str:
        """The name of the session chat works on: the ticket of the worktree these sessions serve, whatever any chat
        chose to open; else the session chat has open; main when none is."""
        ticket = self.ticket_of_worktree()
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
        return (not open_folder.is_dir() or sessions.listing.is_left_behind(open_folder)) and (sessions.folder / COMPLETE_FOLDER / name).is_dir()

    def open(self, session: Session, chat: str = "") -> Session:
        """Make session the one chat has open. Nothing is written in the checkout: the choice is kept under ``~/.cdd``."""
        self.state(chat).session = "" if session.name == MAIN_SESSION_NAME else session.name
        return session

    def current(self, chat: str = "") -> Session:
        """The session chat has open; main when none is."""
        sessions = self._sessions
        return sessions.held.load(sessions.folder_of(self.name_for(chat)))

    def close(self, session: Session) -> None:
        """Close session: when it is the one the call's chat has open, main becomes its open session."""
        state = self.state()
        if session.name != (state.session or MAIN_SESSION_NAME):
            return
        state.session = ""

    def ticket_of_worktree(self) -> Session | None:
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
        holding = [name for name in tickets if re.search(rf"(^|[/_-]){re.escape(name)}($|[/_-])", branch)]
        return sessions.named(holding[0]) if len(holding) == 1 else None

    def switch(self, name: str, workpath: Path | None, call: ToolCall | None) -> str:
        """Open the session called name for the call's chat, creating its folder when missing, and say how to keep its
        log; a chat in a ticket's own worktree always opens that ticket's session."""
        sessions = self._sessions
        chat = call.chat_id if call is not None else ""
        ticket = self.ticket_of_worktree()
        if ticket is not None:
            opened = self.open(ticket, chat)
            return self._worktree_ticket_note(ticket, name) + self._handoff_queued_note(opened, chat) + self._default_roots_note(opened) + opened.log.instructions()
        wanted = self._name_to_switch_to(name, chat)
        folder = sessions.folder_of(wanted)
        is_kept = (folder / SESSION_FILE).is_file() or wanted == MAIN_SESSION_NAME
        session = sessions.held.load(folder) if is_kept else sessions.create(wanted, workpath)
        opened = self.open(session, chat)
        return self._outside_worktree_note(session, call) + self._handoff_queued_note(opened, chat) + self._default_roots_note(opened) + opened.log.instructions()

    def _handoff_queued_note(self, session: Session, chat: str) -> str:
        """Queue the steps of session's latest handoff on chat's prompt queue, once per handoff, and say so; nothing for
        a call from no chat, or a session with no handoff."""
        handoff = session.handoffs.latest
        if not chat or handoff is None:
            return ""
        queued = PromptQueue.of_chat(chat).queue_handoff(handoff)
        return _HANDOFF_QUEUED_NOTE.format(count=queued, handoff=handoff.name) if queued else ""

    def _default_roots_note(self, session: Session) -> str:
        """What a chat opening session is told about the practices it works on whose roots nobody set, so it points each
        at the folder that already holds its artifacts; nothing for main, or when every root was set."""
        if session.name == MAIN_SESSION_NAME:
            return ""
        defaults = [
            f"{key} → {practice.root}"
            for key, practice in session.own_practices.items()
            if practice.enabled and practice.is_root_default
        ]
        return _DEFAULT_ROOTS_NOTE.format(roots=", ".join(defaults)) if defaults else ""

    def _worktree_ticket_note(self, ticket: Session, asked: str) -> str:
        """What a chat in ticket's worktree that asked for another session is told; nothing when it asked for none or
        for ticket."""
        cleaned = Name(asked).title_slug if asked else ""
        if not cleaned or cleaned == ticket.name:
            return ""
        return _WORKTREE_TICKET_NOTE.format(ticket=ticket.name, asked=cleaned)

    def _outside_worktree_note(self, session: Session, call: ToolCall | None) -> str:
        """What a chat working outside session's own worktree must do instead; nothing when it works there, or the
        session has none."""
        if call is None or call.project is None or session.name == MAIN_SESSION_NAME:
            return ""
        worktree = self._sessions.roots.worktree_of(session.name)
        if worktree is None or worktree == call.project or worktree in call.project.parents:
            return ""
        return _OUTSIDE_WORKTREE_NOTE.format(chat=call.project, session=session.name, worktree=worktree)

    def _name_to_switch_to(self, name: str, chat: str = "") -> str:
        cleaned = Name(name or self.state(chat).session).title_slug
        if not cleaned:
            raise SessionNameRequiredError()
        return cleaned
