"""A ticket's git checkout: its own branch, the worktree that branch is open in, and what opening and leaving the ticket
can do with them."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from harness.chat.chat import Chat
from harness.installation.data_class import data_field
from space.kanban.leaving_handoff import LeavingHandoff
from space.repo.repo import Branch

if TYPE_CHECKING:
    from space.kanban.ticket import Ticket
    from space.repo.worktree import Worktree

LEAVE_COMMIT = "commit"
LEAVE_PUSH = "push"
LEAVE_MERGE = "merge"
LEAVE_DELETE_BRANCH = "delete_branch"
LEAVE_DELETE_WORKTREE = "delete_worktree"
LEAVE_HANDOFF = "handoff"
# What leaving does to the branch itself, beyond saving the work on it.
LEAVE_BRANCH_STEPS = {LEAVE_MERGE, LEAVE_DELETE_BRANCH, LEAVE_DELETE_WORKTREE}
OPEN_BRANCH = "branch"
OPEN_WORKTREE = "worktree"


def own_worktree_of(branch: Branch) -> Worktree | None:
    """The worktree beside the repository that has branch checked out; none while the repository itself has it, since
    git lists the main checkout among its worktrees too."""
    return None if branch.is_checked_out else branch.worktree


class LeaveRefused(ValueError):
    """Leaving cannot do what it was asked with the ticket's branch, such as merge it while its worktree still has it
    checked out, which git refuses."""

    def __init__(self, branch: str, reason: str) -> None:
        super().__init__(f"{branch}: {reason}")
        self.branch = branch


class TicketCheckout:
    """*TicketCheckout* is where one ticket's work sits in git: its own branch, the worktree that branch is open in, and
    the chat working there. It answers what opening and leaving the ticket can do now and does it, so a dialog offers
    only what will be done. Made once per ticket, holding the ticket's *Branch*.

    The ticket's session records its branch and worktree, which are read first. A record git no longer agrees with,
    or none, is found again from git and recorded: the branch named as the ticket, else the one branch whose name holds
    the ticket's name as a whole word, as the Claude desktop app names one (``claude/chat-ui-defects-cef4bc``). With
    several such branches none is chosen, and they are named instead."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket
        self._repo = ticket.board.repo
        # The ticket's own branch, whether or not the repository has it yet; a Branch reads its state from git each time.
        self.branch: Branch = self._found_branch()

    @property
    def _recorded(self) -> dict:
        return self._ticket.session.fields

    def _record(self, **checkout: str) -> None:
        if any(self._recorded.get(key, "") != value for key, value in checkout.items()):
            self._ticket.session.save_fields(**checkout)

    def _found_branch(self) -> Branch:
        """The recorded branch while the repository has it, else the ticket's branch found in git and recorded."""
        recorded = self._recorded.get("branch", "")
        if recorded and self._repo.branch_named(recorded).exists:
            return self._repo.branch_named(recorded)
        named = self._repo.branch_named(self._ticket.name)
        candidates = [] if named.exists else self.candidate_branches
        found = named if named.exists or len(candidates) != 1 else candidates[0]
        if found.exists:
            self._record(branch=found.name)
        return found

    @property
    def candidate_branches(self) -> list[Branch]:
        """The branches whose name holds the ticket's name as a whole word, such as claude/chat-ui-defects-cef4bc."""
        word = re.compile(rf"(^|[/_-]){re.escape(self._ticket.name)}($|[/_-])")
        return [branch for branch in self._repo.branches if branch.name != self._ticket.name and word.search(branch.name)]

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
        """The folder of the ticket's own worktree, where its chat works; empty while it has none. The recorded folder
        while git lists the branch's worktree there, else the folder git lists, recorded."""
        found = self._ticket.board.worktrees.get(self.branch)
        folder = str(found.path) if found else ""
        recorded = self._recorded.get("worktree", "")
        if found and recorded and Path(recorded).resolve() == found.path:
            return recorded
        if self.branch.exists:
            self._record(worktree=folder)
        return folder

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
        """What leaving the ticket for another can do with its work now."""
        return LeaveChoices(self._checked_out_work_branch)

    @property
    def close_choices(self) -> LeaveChoices:
        """What closing the ticket can do with its work now: the same as leaving it for another."""
        return LeaveChoices(self._checked_out_work_branch)

    @property
    def open_choices(self) -> OpenChoices:
        """What opening the ticket can create for it now."""
        candidates = [] if self.branch.exists else self.candidate_branches
        return OpenChoices(self.branch, self.worktree, [branch.name for branch in candidates] if len(candidates) > 1 else [])

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
        if opening:
            self._ticket.board.reread()
            self._record(branch=self.branch.name, worktree=self.worktree)

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
        """Commit and push the branch the ticket's work is on, in the checkout that has it: the repository, or the
        ticket's own worktree. Then do what leaving names with the branch: delete its worktree, merge it into the default
        branch, or merge and delete it. Nothing while no checkout has it, because those steps act on whatever is checked
        out. Work on the default branch is committed and pushed there; it has no branch to merge and no worktree to
        remove."""
        if not set(leaving) & {LEAVE_COMMIT, LEAVE_PUSH, *LEAVE_BRANCH_STEPS}:
            return
        branch = self._checked_out_work_branch
        if branch is None:
            return
        self._commit_and_push(branch, leaving)
        if branch.is_default or not set(leaving) & LEAVE_BRANCH_STEPS:
            return
        self._delete_worktree(branch, leaving)
        self._merge(branch, leaving)

    def _commit_and_push(self, branch: Branch, leaving: list[str]) -> None:
        # Checked out in the repository itself, else in the ticket's own worktree.
        checkout = self._repo if branch.is_checked_out else branch.worktree.repository
        if LEAVE_COMMIT in leaving or LEAVE_PUSH in leaving:
            checkout.commit([str(checkout.root)], f"{self._ticket.name}: leave session", untracked=True)
        if LEAVE_PUSH in leaving:
            checkout.push_upstream()

    def _delete_worktree(self, branch: Branch, leaving: list[str]) -> None:
        """Remove the branch's own worktree folder; the branch stays. git merges or deletes a branch only once no
        worktree has it checked out, so a merge asked for while the worktree stays is refused."""
        worktree = own_worktree_of(branch)
        if worktree is None:
            return
        if LEAVE_DELETE_WORKTREE in leaving:
            worktree.close(f"{self._ticket.name}: leave session")
            self._ticket.board.reread()
        elif {LEAVE_MERGE, LEAVE_DELETE_BRANCH} & set(leaving):
            raise LeaveRefused(branch.name, "its worktree still has it checked out; delete the worktree too")

    def _merge(self, branch: Branch, leaving: list[str]) -> None:
        """Merge the branch into the default branch and push it; delete it too when leaving says so."""
        if LEAVE_DELETE_BRANCH in leaving:
            self._repo.close_branch(branch.name)
        elif LEAVE_MERGE in leaving:
            branch.land_on_default()

    def return_to_default_branch(self, leaving: list[str]) -> None:
        """A closed ticket's own branch leaves the repository's checkout once its work is committed, so the next
        session does not start on it. Uncommitted work keeps it checked out, so nothing is carried to the default branch."""
        if not (LEAVE_COMMIT in leaving or LEAVE_PUSH in leaving):
            return
        if not self.branch.is_checked_out:
            return
        self._repo.branch_named(self._repo.default_branch).check_out()


class LeaveChoices:
    """What leaving a ticket can do with its work now, closing it or switching to another: a handoff always; a commit
    and a push of the branch its work is on while a checkout has it, since those steps act on whatever is checked out;
    and, for the ticket's own branch, not the default branch, a merge into the default branch, a delete of the branch
    once merged, and a delete of its worktree while it has one. ``TicketCheckout.leave`` does exactly these, so a dialog
    offers only what will be done."""

    def __init__(self, branch: Branch | None) -> None:
        self._branch = branch

    @property
    @data_field
    def branch(self) -> str:
        """The branch leaving commits, pushes, and merges; empty when nothing checked out is the ticket's."""
        return self._branch.name if self._branch is not None else ""

    @property
    @data_field
    def choices(self) -> list[str]:
        """Each choice leaving offers now, in the order a dialog lists them."""
        if self._branch is None:
            return [LEAVE_HANDOFF]
        if self._branch.is_default:
            return [LEAVE_HANDOFF, LEAVE_COMMIT, LEAVE_PUSH]
        worktree = [LEAVE_DELETE_WORKTREE] if own_worktree_of(self._branch) is not None else []
        return [LEAVE_HANDOFF, LEAVE_COMMIT, LEAVE_PUSH, LEAVE_MERGE, LEAVE_DELETE_BRANCH, *worktree]

    @property
    @data_field
    def chosen(self) -> list[str]:
        """The choices a person starts with chosen: a handoff, a commit and a push; what changes the branch waits for
        them."""
        return [choice for choice in self.choices if choice not in LEAVE_BRANCH_STEPS]


class OpenChoices:
    """What opening a ticket can create for it now: its own branch while the repository has none, and its own worktree
    while it has none. ``TicketCheckout.open`` creates each one chosen."""

    def __init__(self, branch: Branch, worktree: str, candidate_branches: list[str]) -> None:
        self._branch = branch
        self._worktree = worktree
        self._candidate_branches = list(candidate_branches)

    @property
    @data_field
    def has_branch(self) -> bool:
        """Whether the ticket's own branch is in the repository already."""
        return self._branch.exists

    @property
    @data_field
    def candidate_branches(self) -> list[str]:
        """The branches that could each be the ticket's, when more than one holds its name and none is chosen."""
        return list(self._candidate_branches)

    @property
    @data_field
    def choices(self) -> list[str]:
        """Each choice opening offers now, all chosen at first."""
        return [*([] if self.has_branch else [OPEN_BRANCH]), *([] if self._worktree else [OPEN_WORKTREE])]
