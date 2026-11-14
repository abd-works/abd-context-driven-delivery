"""A ticket's git checkout: its own branch, the worktree that branch is open in, and what opening and leaving the ticket
can do with them."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from harness.chat.chat import Chat
from harness.installation.data_class import data_field
from space.kanban.leaving_handoff import LeavingHandoff
from space.repo.latest_release import LatestRelease
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
# The session.json field that keeps the chat a person assigned to a ticket.
ASSIGNED_CHAT = "chat"


def own_worktree_of(branch: Branch) -> Worktree | None:
    """The linked worktree beside the main clone that has branch checked out; none while the main clone itself has it,
    since git lists the main clone among its worktrees too. Asked from inside that worktree, the branch is checked out
    there, and the worktree is still its own."""
    worktree = branch.worktree
    if worktree is None or worktree.path == branch.repo.main_clone.root:
        return None
    return worktree


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

    def _found_branch(self) -> Branch:
        """The recorded branch while the repository has it, else the ticket's branch found in git and recorded."""
        existing = {branch.name for branch in self._ticket.board.branches}
        recorded = self._recorded.get("branch", "")
        if recorded and recorded in existing:
            return self._repo.branch_named(recorded)
        named = self._repo.branch_named(self._ticket.name)
        if named.name in existing:
            return named
        candidates = self.candidate_branches
        return candidates[0] if len(candidates) == 1 else named

    @property
    def candidate_branches(self) -> list[Branch]:
        """The branches whose name holds the ticket's name as a whole word, such as claude/chat-ui-defects-cef4bc. A
        branch named as another ticket is that ticket's own, so performance never claims repo-performance."""
        word = re.compile(rf"(^|[/_-]){re.escape(self._ticket.name)}($|[/_-])")
        board = self._ticket.board
        return [branch for branch in board.branches if branch.name not in board.ticket_names and word.search(branch.name)]

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
        """The folder of the ticket's own worktree, where its chat works, as git lists it; empty while it has none. It
        is read from git each time and never written to the session, so switching never changes a tracked file."""
        found = self._ticket.board.worktrees.get(self.branch)
        return str(found.path) if found else ""

    @property
    def chat(self) -> Chat | None:
        """The connected chat the ticket works in. A chat a person assigned to it, kept in its session.json, is its chat
        and no other is looked for. Unassigned, it is the chat named after the ticket, as the board names the chat it
        opens for it, else the one working in its worktree or a folder inside it. None while no such chat is connected,
        and the board offers to open one."""
        chats = self._ticket.board.chats
        assigned = self.assigned_chat
        if assigned:
            return next((chat for chat in chats if chat.id == assigned), None)
        named = next((chat for chat in chats if chat.name == self._ticket.name), None)
        return named or self._chat_in_worktree(chats)

    @property
    def assigned_chat(self) -> str:
        """The id of the chat a person assigned to the ticket; empty while none is."""
        return str(self._ticket.session.fields.get(ASSIGNED_CHAT, "") or "")

    def assign_chat(self, chat: str) -> None:
        """Make chat, a chat's id, the ticket's chat from now on; an empty chat gives it back to the chat named after
        it. The record is committed on main and pushed."""
        self._ticket.session.save_fields(**{ASSIGNED_CHAT: chat})

    def _chat_in_worktree(self, chats: list[Chat]) -> Chat | None:
        worktree = self.worktree
        if not worktree:
            return None
        return next((chat for chat in chats if chat.folder and Path(chat.folder).resolve().is_relative_to(Path(worktree).resolve())), None)

    @property
    def close_choices(self) -> LeaveChoices:
        """What closing the ticket can do with its work now."""
        return LeaveChoices(self._checked_out_work_branch, self._own_branch)

    @property
    def _own_branch(self) -> Branch | None:
        """The ticket's own branch while git has it, checked out or not, and it is not the default branch: leaving can
        merge and delete it. None otherwise."""
        return self.branch if self.branch.exists and not self.branch.is_default else None

    @property
    def _checked_out_work_branch(self) -> Branch | None:
        """The branch the ticket's work is on while a checkout has it, the repository or its own worktree, which leaving
        acts on; none otherwise."""
        branch = self.work_branch
        return branch if branch.is_checked_out or branch.worktree is not None else None

    def open(self) -> None:
        """Open the ticket in its own worktree, where its chat works: the worktree it has, else a new one on its own
        branch, made when missing, after the session folders not yet committed are committed on main and pushed, so the
        branch starts from a main that has them. The repository's own folder stays on main, and no chat's open session
        changes. The branch and worktree found are recorded in the ticket's session, and that record is committed on main
        and pushed. Two branches that could each be the ticket's are named instead of either being guessed."""
        board = self._ticket.board
        if not self.worktree:
            self._refuse_unclear_branch()
            board.sessions.saves.now(f"sessions: save before opening {self._ticket.name}")
            self.branch.open_in_worktree()
            board.reread()
        self._ticket.session.save_fields(branch=self.branch.name, worktree=self.worktree)
        board.sessions.saves.now(f"sessions: open {self._ticket.name}")

    def _refuse_unclear_branch(self) -> None:
        candidates = [] if self.branch.exists else self.candidate_branches
        if len(candidates) > 1:
            raise TicketBranchUnclearError(self._ticket.name, [branch.name for branch in candidates])

    def keep_landing_release(self, leaving: list[str]) -> None:
        """A ticket closed with its branch merged lands its release: its end-to-end results are the only ones kept, its
        screenshots pushed to e2e-latest. Done while its folder is still among the open sessions, where they are."""
        if LEAVE_MERGE in leaving:
            LatestRelease(self._repo.main_clone, self._ticket.name).keep()

    def write_handoff(self, leaving: list[str]) -> None:
        """Write a handoff for the ticket's session when leaving names one."""
        if LEAVE_HANDOFF in leaving:
            self._ticket.session.handoffs.write(LeavingHandoff(self._ticket).document)

    def save_work(self, leaving: list[str]) -> None:
        """Commit and push the branch the ticket's work is on, in the checkout that has it: the repository, or the
        ticket's own worktree; work on the default branch is committed and pushed there. Then do what leaving names with
        the ticket's own branch, checked out or not: delete its worktree, merge it into the default branch, or merge and
        delete it."""
        if not set(leaving) & {LEAVE_COMMIT, LEAVE_PUSH, *LEAVE_BRANCH_STEPS}:
            return
        branch = self._checked_out_work_branch
        if branch is not None:
            self._commit_and_push(branch, leaving)
        own = self._own_branch
        if own is None or not set(leaving) & LEAVE_BRANCH_STEPS:
            return
        self._delete_worktree(own, leaving)
        self._merge(own, leaving)

    def free_worktree(self, leaving: list[str]) -> None:
        """Delete the ticket's own worktree, its work committed and pushed there, when leaving names a step that needs
        its branch free; ahead of anything else leaving changes, so a worktree held open stops it before it starts."""
        own = self._own_branch
        if own is not None and set(leaving) & LEAVE_BRANCH_STEPS:
            self._delete_worktree(own, leaving)

    def _commit_and_push(self, branch: Branch, leaving: list[str]) -> None:
        # Checked out in the repository itself, else in the ticket's own worktree.
        checkout = self._repo if branch.is_checked_out else branch.worktree.repository
        if LEAVE_COMMIT in leaving or LEAVE_PUSH in leaving:
            checkout.commit([str(checkout.root)], f"{self._ticket.name}: leave session", untracked=True)
        if LEAVE_PUSH in leaving:
            checkout.push_upstream()

    def _delete_worktree(self, branch: Branch, leaving: list[str]) -> None:
        """Remove the branch's own worktree folder, its work committed and pushed there, when leaving names
        delete_worktree or delete_branch: git deletes no branch a worktree has checked out, so deleting the branch takes
        its worktree with it. A merge needs neither, since the default branch's checkout merges it."""
        worktree = own_worktree_of(branch)
        if worktree is None or not {LEAVE_DELETE_WORKTREE, LEAVE_DELETE_BRANCH} & set(leaving):
            return
        worktree.close(f"{self._ticket.name}: leave session")
        self._work_from_main_clone()
        self._ticket.board.reread()

    def _work_from_main_clone(self) -> None:
        """The ticket may have been read from the worktree just deleted, where git can no longer run, so its branch is
        read from the main clone from now on."""
        self._repo = self._repo.main_clone
        self.branch = self._repo.branch_named(self.branch.name)

    def _merge(self, branch: Branch, leaving: list[str]) -> None:
        """Merge the branch into the default branch and push it when leaving names merge; delete it, here and on
        origin, when leaving names delete_branch. Each is its own choice: deleting never merges."""
        if LEAVE_MERGE in leaving:
            branch.land_on_default()
        if LEAVE_DELETE_BRANCH in leaving:
            # git deletes no branch the checkout is on, so the checkout goes back to the default branch first.
            if branch.is_checked_out and self._repo.root == self._repo.main_clone.root:
                self._repo.branch_named(self._repo.default_branch).check_out()
            branch.delete(unmerged=LEAVE_MERGE not in leaving)

    def return_to_default_branch(self) -> None:
        """Closing a ticket opens main, the default branch in the repository's own folder, so the closed ticket's own
        branch leaves the repository's checkout. Work left uncommitted goes with the checkout, as git carries it."""
        if not self.branch.is_checked_out or self.branch.is_default:
            return
        # A linked worktree cannot check out the default branch while the main checkout has it; the chat goes back to
        # the main checkout instead, so the worktree keeps its branch.
        if self._repo.root != self._repo.main_clone.root:
            return
        self._repo.branch_named(self._repo.default_branch).check_out()



class TicketBranchUnclearError(LookupError):
    """Raised when a ticket with no branch of its own is opened while several branches hold its name, as the Claude
    desktop app names them; it names the ticket and those branches, so a person picks one rather than a guess."""

    def __init__(self, ticket: str, branches: list[str]) -> None:
        super().__init__(f"{', '.join(sorted(branches))} could each be {ticket}'s branch; record the one that is in its session")
        self.ticket = ticket
        self.branches = sorted(branches)


class LeaveChoices:
    """What closing a ticket can do with its work now: a handoff always; a commit and a push of the branch its work is
    on while a checkout has it, since those steps act on whatever is checked out; and, for the ticket's own branch, not
    the default branch, a merge into the default branch, a delete of the branch once merged, and a delete of its
    worktree while it has one. ``Ticket.close`` does exactly these, so a dialog offers only what will be done."""

    def __init__(self, branch: Branch | None, own_branch: Branch | None) -> None:
        self._branch = branch
        self._own_branch = own_branch

    @property
    @data_field
    def branch(self) -> str:
        """The branch leaving commits and pushes; empty when nothing checked out is the ticket's."""
        return self._branch.name if self._branch is not None else ""

    @property
    @data_field
    def own_branch(self) -> str:
        """The ticket's own branch, which leaving merges and deletes, checked out or not; empty while git has none."""
        return self._own_branch.name if self._own_branch is not None else ""

    @property
    @data_field
    def choices(self) -> list[str]:
        """Each choice leaving offers now, in the order a dialog lists them."""
        saving = [LEAVE_COMMIT, LEAVE_PUSH] if self._branch is not None else []
        return [LEAVE_HANDOFF, *saving, *self._branch_steps]

    @property
    def _branch_steps(self) -> list[str]:
        if self._own_branch is None:
            return []
        worktree = [LEAVE_DELETE_WORKTREE] if own_worktree_of(self._own_branch) is not None else []
        return [LEAVE_MERGE, LEAVE_DELETE_BRANCH, *worktree]

    @property
    @data_field
    def chosen(self) -> list[str]:
        """The choices a person starts with chosen: none, so leaving does only what the person ticks."""
        return []
