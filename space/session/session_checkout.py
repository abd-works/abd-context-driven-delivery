"""SessionCheckout - the one checkout a session works in: its own branch, the worktree that branch is open in, and the
chat a person assigned to it."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from space.repo.repo import Branch, Repo
from harness.process.answer_reads import HeldForAnswer

if TYPE_CHECKING:
    from space.session.session import Session

# The session that works on the whole repository, which has no branch or worktree of its own.
_MAIN = "main"


def names_ticket(branch: str, ticket: str) -> bool:
    """Whether the branch called branch holds ticket's name as a whole word, as the Claude desktop app names a branch
    around a ticket's name, such as claude/checkout-flow-cef4bc."""
    return re.search(rf"(^|[/_-]){re.escape(ticket)}($|[/_-])", branch) is not None


class SessionCheckout:
    """*SessionCheckout* is where one session works in git, and the one reader and writer of what its session.json
    records about it (``branch``, ``worktree``, ``chat``): its own branch, named as the session, else recorded, else the
    one branch holding its name as a whole word; the linked worktree that branch is open in; the session's one project,
    which is that worktree when it has one, else the checkout whose sessions hold it; and the chat a person assigned to
    it. Made once with its session, and asked again each time, since git and the record change."""

    def __init__(self, session: Session) -> None:
        self._session = session
        # Its branch, found once for each answer that asks: every part of one answer works on the same Branch.
        self._branch = HeldForAnswer[Branch]()

    @property
    def _main_clone(self) -> Repo:
        """The repository's main clone, where every branch is read: the board and every session read the same branches,
        whichever checkout loaded them."""
        return self._session.sessions.repo.main_clone

    @property
    def _has_own_branch(self) -> bool:
        return bool(self._session.name) and self._session.name != _MAIN

    @property
    def branch(self) -> Branch:
        """The session's own branch, whether or not the repository has it yet: the recorded branch while the repository
        has it, else the one named as the session, else the one branch whose name holds the session's name as a whole
        word. With several such branches none is chosen, and the one named as the session comes back, not there yet. It
        is found once for each answer that asks."""
        return self._branch.get(self._session.answer, self._found_branch)

    def _found_branch(self) -> Branch:
        repo = self._main_clone
        recorded = self._session.record.fields.branch
        if recorded and repo.branch_named(recorded).exists:
            return repo.branch_named(recorded)
        named = repo.branch_named(self._session.name)
        if named.exists or not self._has_own_branch:
            return named
        candidates = self.candidate_branches
        return candidates[0] if len(candidates) == 1 else named

    @property
    def candidate_branches(self) -> list[Branch]:
        """The branches whose name holds the session's name as a whole word, such as claude/chat-ui-defects-cef4bc. A
        branch named as another session is that session's own, so performance never claims repo-performance."""
        if not self._has_own_branch:
            return []
        sessions = self._session.sessions
        others = set(sessions.listing.open_names())
        repo = self._main_clone
        return [repo.branch_named(name) for name in sessions.worktrees.branch_names() if name not in others and names_ticket(name, self._session.name)]

    @property
    def own_worktree(self) -> Repo | None:
        """The linked worktree of the session's own: the one recorded while its folder is there, else the one its branch
        is checked out in; none for main, or a session with no worktree of its own."""
        if not self._has_own_branch:
            return None
        recorded = str(self._session.record.fields.worktree or "").strip()
        sessions = self._session.sessions
        folder = Path(recorded).resolve() if recorded and Path(recorded).is_dir() else sessions.worktrees.of_branch(self.branch.name)
        return sessions.repo.worktrees.repository_at(folder) if folder is not None else None

    @property
    def repo(self) -> Repo:
        """The session's one project: its own worktree, else the checkout whose sessions hold it."""
        worktree = self.own_worktree
        return worktree if worktree is not None else self._session.sessions.repo

    @property
    def root(self) -> Path:
        """The top folder of the session's one project."""
        return self.repo.root

    @property
    def assigned_chat(self) -> str:
        """The id of the chat a person assigned to the session; empty while none is."""
        return str(self._session.record.fields.chat or "")

    def assign_chat(self, chat: str) -> None:
        """Make chat, a chat's id, the session's chat from now on; an empty chat gives it back to the chat named after
        it. The record is committed on main and pushed."""
        self._session.record.update(lambda fields: setattr(fields, "chat", chat), f"chat {chat}")

    def record_opened(self) -> None:
        """Record the branch and the worktree the session was opened in, as git has them now."""
        branch = self.branch.name
        worktree = self.own_worktree
        folder = str(worktree.root) if worktree is not None else ""

        def opened(fields) -> None:
            fields.branch = branch
            fields.worktree = folder

        self._session.record.update(opened, f"branch {branch}, worktree {folder}")
