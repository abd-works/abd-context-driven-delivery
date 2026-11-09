"""A ticket's git checkout: its own branch, the worktree that branch is open in, and what opening and leaving the ticket
can do with them."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.chat.chat import Chat
from harness.installation.data_class import data_field
from space.kanban.leaving_handoff import LeavingHandoff
from space.repo.repo import Branch

if TYPE_CHECKING:
    from space.kanban.ticket import Ticket

LEAVE_COMMIT = "commit"
LEAVE_PUSH = "push"
LEAVE_MERGE = "merge"
LEAVE_HANDOFF = "handoff"
OPEN_BRANCH = "branch"
OPEN_WORKTREE = "worktree"


class TicketCheckout:
    """*TicketCheckout* is where one ticket's work sits in git: its own branch, named as the ticket, the worktree that
    branch is open in, and the chat working there. It answers what opening and leaving the ticket can do now and does
    it, so a dialog offers only what will be done. Made once per ticket, holding the ticket's *Branch*."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket
        self._repo = ticket.board.repo
        # The ticket's own branch, whether or not the repository has it yet; a Branch reads its state from git each time.
        self.branch: Branch = self._repo.branch_named(ticket.name)

    @property
    def work_branch(self) -> Branch:
        """The branch the ticket's work is on: its own branch while it is checked out, in the repository or in its own
        worktree, else the default branch while the repository has it checked out, as for a session with no branch of
        its own. Any other branch checked out is not the ticket's, so its own branch comes back not checked out."""
        if self.branch.is_checked_out or self.branch.worktree is not None:
            return self.branch
        default = self._repo.branch_named(self._repo.default_branch)
        return default if default.is_checked_out else self.branch

    @property
    def worktree(self) -> str:
        """The folder of the ticket's own worktree, where its chat works; empty while it has none."""
        found = self._ticket.board.worktrees.get(self.branch)
        return str(found.path) if found else ""

    @property
    def chat(self) -> Chat | None:
        """The connected chat working on the ticket: the one working in its worktree or a folder inside it, else one
        whose mod names no folder and that is titled by the ticket's name, as the board titles the chat it opens for it."""
        worktree = self.worktree
        chats = self._ticket.board.chats
        working = next((chat for chat in chats if worktree and chat.folder and Path(chat.folder).resolve().is_relative_to(Path(worktree).resolve())), None)
        return working or next((chat for chat in chats if not chat.folder and chat.name == self._ticket.name), None)

    @property
    def leave_choices(self) -> LeaveChoices:
        """What leaving the ticket for another can do with its work now, a merge included."""
        branch = self._checked_out_work_branch
        # A branch open in its own worktree cannot be merged and deleted from here; its worktree is closed first.
        return LeaveChoices(branch, merges=branch is not None and branch.is_checked_out)

    @property
    def close_choices(self) -> LeaveChoices:
        """What closing the ticket can do with its work now; closing never merges."""
        return LeaveChoices(self._checked_out_work_branch, merges=False)

    @property
    def open_choices(self) -> OpenChoices:
        """What opening the ticket can create for it now."""
        return OpenChoices(self.branch, self.worktree)

    @property
    def _checked_out_work_branch(self) -> Branch | None:
        """The branch the ticket's work is on while a checkout has it, the repository or its own worktree, which leaving
        acts on; none otherwise."""
        branch = self.work_branch
        return branch if branch.is_checked_out or branch.worktree is not None else None

    def open(self, opening: list[str]) -> None:
        """Create what opening names for the ticket: its own branch, checked out, and its own worktree."""
        if OPEN_BRANCH in opening:
            self._repo.switch_branch(self.branch.name)
        if OPEN_WORKTREE in opening:
            self._repo.switch_worktree(self.branch.name)

    def open_worktree(self) -> None:
        """Open the ticket's own worktree beside the repository, creating its branch when missing. The board lists
        worktrees once per read, so it forgets them and lists the new one next time."""
        self.branch.open_in_worktree()
        self._ticket.board.reread()

    def leave(self, leaving: list[str]) -> None:
        """Do what leaving names with the ticket's work: write a handoff for its session, then save the work."""
        self.write_handoff(leaving)
        self.save_work(leaving)

    def write_handoff(self, leaving: list[str]) -> None:
        """Write a handoff for the ticket's session when leaving names one."""
        if LEAVE_HANDOFF in leaving:
            self._ticket.session.handoffs.write(LeavingHandoff(self._ticket).document)

    def save_work(self, leaving: list[str]) -> None:
        """Commit, push, and merge the branch the ticket's work is on, as leaving names, in the checkout that has it:
        the repository, or the ticket's own worktree. Nothing while no checkout has it, because those steps act on
        whatever is checked out. Work on the default branch is committed and pushed there; it has no branch to merge and
        no worktree to remove."""
        if not set(leaving) & {LEAVE_COMMIT, LEAVE_PUSH, LEAVE_MERGE}:
            return
        branch = self._checked_out_work_branch
        if branch is None:
            return
        # Checked out in the repository itself, else in the ticket's own worktree.
        checkout = self._repo if branch.is_checked_out else branch.worktree.repository
        if LEAVE_COMMIT in leaving or LEAVE_PUSH in leaving:
            checkout.commit([str(checkout.root)], f"{self._ticket.name}: leave session", untracked=True)
        if LEAVE_PUSH in leaving:
            checkout.push_upstream()
        if LEAVE_MERGE in leaving and branch.is_checked_out and not branch.is_default:
            self._repo.close_branch(branch.name)

    def return_to_default_branch(self, leaving: list[str]) -> None:
        """A closed ticket's own branch leaves the repository's checkout once its work is committed, so the next
        session does not start on it. Uncommitted work keeps it checked out, so nothing is carried to the default branch."""
        if not (LEAVE_COMMIT in leaving or LEAVE_PUSH in leaving):
            return
        if not self.branch.is_checked_out:
            return
        self._repo.branch_named(self._repo.default_branch).check_out()


class LeaveChoices:
    """What leaving a ticket can do with its work now, closing it or switching to another: a handoff always, a commit
    and a push of the branch its work is on while that branch is checked out, since those steps act on whatever is
    checked out, and, when switching, a merge of that branch while it is not the default branch, which has nothing to
    merge into. Closing never merges. ``TicketCheckout.leave`` does exactly these, so a dialog offers only what will be
    done."""

    def __init__(self, branch: Branch | None, *, merges: bool) -> None:
        self._branch = branch
        self._merges = merges

    @property
    @data_field
    def branch(self) -> str:
        """The branch leaving commits, pushes, and merges; empty when nothing checked out is the ticket's."""
        return self._branch.name if self._branch is not None else ""

    @property
    @data_field
    def choices(self) -> list[str]:
        """Each choice leaving offers now, in the order leave does them."""
        if self._branch is None:
            return [LEAVE_HANDOFF]
        merge = [LEAVE_MERGE] if self._merges and not self._branch.is_default else []
        return [LEAVE_HANDOFF, LEAVE_COMMIT, LEAVE_PUSH, *merge]

    @property
    @data_field
    def chosen(self) -> list[str]:
        """The choices a person starts with chosen: every one offered but the merge, which waits for them."""
        return [choice for choice in self.choices if choice != LEAVE_MERGE]


class OpenChoices:
    """What opening a ticket can create for it now: its own branch while the repository has none, and its own worktree
    while it has none. ``TicketCheckout.open`` creates each one chosen."""

    def __init__(self, branch: Branch, worktree: str) -> None:
        self._branch = branch
        self._worktree = worktree

    @property
    @data_field
    def has_branch(self) -> bool:
        """Whether the ticket's own branch is in the repository already."""
        return self._branch.exists

    @property
    @data_field
    def choices(self) -> list[str]:
        """Each choice opening offers now, all chosen at first."""
        return [*([] if self.has_branch else [OPEN_BRANCH]), *([] if self._worktree else [OPEN_WORKTREE])]
