"""A ticket's git checkout: its own branch, the worktree that branch is open in, and what opening and leaving the ticket
can do with them."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.chat.chat import Chat
from harness.installation.data_class import data_field
from space.kanban.leaving_handoff import LeavingHandoff
from space.repo.latest_release import LatestRelease
from space.repo.repo import Branch, Repo
from space.repo.worktree import WorktreeFolderTakenError

if TYPE_CHECKING:
    from space.kanban.ticket import Ticket

LEAVE_COMMIT = "commit"
LEAVE_PUSH = "push"
LEAVE_MERGE = "merge"
LEAVE_DELETE_BRANCH = "delete_branch"
LEAVE_DELETE_WORKTREE = "delete_worktree"
LEAVE_HANDOFF = "handoff"
# Every step leaving can take, in the order a dialog lists them.
LEAVE_STEPS = (LEAVE_HANDOFF, LEAVE_COMMIT, LEAVE_PUSH, LEAVE_MERGE, LEAVE_DELETE_BRANCH, LEAVE_DELETE_WORKTREE)


class UnknownLeavingStepError(ValueError):
    """Raised when closing a ticket names a step leaving does not take, such as a misspelt one: it names the steps it
    did not know and the steps there are, and nothing of the ticket changes."""

    def __init__(self, unknown: list[str]) -> None:
        super().__init__(f"{', '.join(unknown)} is no step of leaving a ticket; the steps are {', '.join(LEAVE_STEPS)}")
        self.unknown = unknown


class Leaving:
    """*Leaving* is what a person chose to do with a ticket's work as it closes: write a handoff, commit and push the
    branch its work is on, merge its own branch, delete that branch, delete its worktree. A step leaving does not take
    is refused, so a misspelt one never passes for a choice made. Each step a checkout takes asks it what was chosen."""

    def __init__(self, steps: list[str]) -> None:
        unknown = [step for step in steps if step not in LEAVE_STEPS]
        if unknown:
            raise UnknownLeavingStepError(unknown)
        self._steps = frozenset(steps)

    @property
    def writes_handoff(self) -> bool:
        return LEAVE_HANDOFF in self._steps

    @property
    def commits(self) -> bool:
        return LEAVE_COMMIT in self._steps

    @property
    def pushes(self) -> bool:
        return LEAVE_PUSH in self._steps

    @property
    def merges(self) -> bool:
        return LEAVE_MERGE in self._steps

    @property
    def deletes_branch(self) -> bool:
        return LEAVE_DELETE_BRANCH in self._steps

    @property
    def deletes_worktree(self) -> bool:
        return LEAVE_DELETE_WORKTREE in self._steps

    @property
    def changes_branch(self) -> bool:
        """Whether it does anything to the ticket's own branch beyond saving the work on it: merges, deletes it, or
        deletes its worktree."""
        return self.merges or self.deletes_branch or self.deletes_worktree

    @property
    def saves_work(self) -> bool:
        """Whether it saves the ticket's work before anything is removed: a commit, a push, or a change of its branch,
        which saves what a worktree about to go holds."""
        return self.commits or self.pushes or self.changes_branch

    @property
    def removes_worktree(self) -> bool:
        """Whether the ticket's own worktree goes: deleted, or taken with the branch, since git deletes no branch a
        worktree has checked out."""
        return self.deletes_worktree or self.deletes_branch


class TicketCheckout:
    """*TicketCheckout* is where one ticket's work sits in git: its own branch, the worktree that branch is open in, and
    the chat working there. It answers what opening and leaving the ticket can do now and does it, so a dialog offers
    only what will be done. Made once per ticket, holding the ticket's *Branch*.

    Its branch, the worktree that branch is open in, and the chat a person assigned to it are its session's checkout's
    (*SessionCheckout*), which reads and records them; with several branches that could each be the ticket's none is
    chosen, and opening names them instead."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket
        self._repo = ticket.board.repo

    @property
    def branch(self) -> Branch:
        """The ticket's own branch, whether or not the repository has it yet, as its session's checkout finds it."""
        return self._ticket.session.checkout.branch

    @property
    def work_branch(self) -> Branch:
        """The branch the ticket's work is on: its own branch while it is checked out, in the repository or in its own
        worktree, else the default branch while the repository has it checked out, as for a session with no branch of
        its own. Any other branch checked out is not the ticket's, so its own branch comes back not checked out."""
        if self.branch.is_checked_out:
            return self.branch
        default = self._repo.default_branch
        return default if default.is_checked_out_here else self.branch

    @property
    def worktree(self) -> str:
        """The folder of the ticket's own worktree, where its chat works, as git lists it; empty while it has none. It
        is read from git each time and never written to the session, so switching never changes a tracked file."""
        found = self._ticket.board.worktrees.get(self.branch)
        return str(found.root) if found else ""

    @property
    def chat(self) -> Chat | None:
        """The connected chat the ticket works in. A chat a person assigned to it, kept in its session.json, is its chat
        and no other is looked for. Unassigned, it is the chat named after the ticket, as the board names the chat it
        opens for it, else the one working in its worktree or a folder inside it. None while no such chat is connected,
        and the board offers to open one."""
        chats = self._ticket.board.chats
        assigned = self._ticket.session.checkout.assigned_chat
        if assigned:
            return next((chat for chat in chats if chat.id == assigned), None)
        named = self._ticket.board.reads.chat_named(self._ticket.name)
        return named or self._chat_in_worktree(chats)

    def _chat_in_worktree(self, chats: list[Chat]) -> Chat | None:
        worktree = self.worktree
        if not worktree:
            return None
        return next((chat for chat in chats if chat.folder and Path(chat.folder).resolve().is_relative_to(Path(worktree).resolve())), None)

    @property
    def close_choices(self) -> LeaveChoices:
        """What closing the ticket can do with its work now."""
        work = self.work_branch
        return LeaveChoices(work if work.checkout is not None else None, self._own_branch)

    @property
    def _own_branch(self) -> Branch | None:
        """The ticket's own branch while git has it, checked out or not, and it is not the default branch: leaving can
        merge and delete it. None otherwise."""
        return self.branch if self.branch.exists and not self.branch.is_default else None

    def open(self) -> None:
        """Open the ticket in its own worktree, where its chat works: the worktree it has, else a new one on its own
        branch, made when missing, after the session folders not yet committed are committed on main and pushed, so the
        branch starts from a main that has them. The repository's own folder stays on main, and no chat's open session
        changes. The branch and worktree found are recorded in the ticket's session, and that record is committed on main
        and pushed. Two branches that could each be the ticket's are named instead of either being guessed, and a
        folder in the way of its worktree raises ``TicketWorktreeBlockedError``."""
        board = self._ticket.board
        if not self.worktree:
            self._refuse_unclear_branch()
            board.sessions.saves.now(f"sessions: save before opening {self._ticket.name}")
            self._open_worktree()
            board.placement.reread()
        self._ticket.session.checkout.record_opened()
        board.sessions.saves.now(f"sessions: open {self._ticket.name}")

    def _open_worktree(self) -> None:
        try:
            self.branch.open_in_worktree()
        except WorktreeFolderTakenError as taken:
            raise TicketWorktreeBlockedError(self._ticket.name, taken.folder) from taken
        self._ticket.board.sessions.worktrees.forget()

    def _refuse_unclear_branch(self) -> None:
        candidates = [] if self.branch.exists else self._ticket.session.checkout.candidate_branches
        if len(candidates) > 1:
            raise TicketBranchUnclearError(self._ticket.name, [branch.name for branch in candidates])

    def keep_landing_release(self, leaving: Leaving) -> None:
        """A ticket closed with its branch merged lands its release: its end-to-end results are the only ones kept, its
        screenshots pushed to e2e-latest. Done while its folder is still among the open sessions, where they are."""
        if leaving.merges:
            LatestRelease(self._repo.main_clone, self._ticket.name).keep()

    def write_handoff(self, leaving: Leaving) -> None:
        """Write a handoff for the ticket's session when leaving names one."""
        if leaving.writes_handoff:
            self._ticket.session.handoffs.write(LeavingHandoff(self._ticket).document)

    @property
    def _leave_message(self) -> str:
        """The message of the commit that saves the ticket's work as it is left."""
        return f"{self._ticket.name}: leave session"

    def save_work(self, leaving: Leaving) -> None:
        """Commit and push the branch the ticket's work is on, in the checkout that has it: the repository, or the
        ticket's own worktree; work on the default branch is committed and pushed there. Then merge the ticket's own
        branch into the default branch when leaving names merge. Nothing of the ticket is removed here, and this runs
        before anything is: a merge git refuses leaves its worktree, its branch, and its session as they were, and the
        commit is made where the ticket's work is, never from whatever the repository's own folder holds once the
        worktree is gone."""
        if not leaving.saves_work:
            return
        if leaving.commits or leaving.pushes:
            self.work_branch.save(self._leave_message, push=leaving.pushes)
        own = self._own_branch
        if own is None:
            return
        self._save_worktree_to_delete(own, leaving)
        if leaving.merges:
            own.land_on_default()

    def leave_branch(self, leaving: Leaving) -> None:
        """Do what leaving names with the ticket's own branch once its work is saved and merged: delete its worktree,
        and delete the branch, here and on origin. Each is its own choice: deleting never merges."""
        own = self._own_branch
        if own is None or not leaving.changes_branch:
            return
        self._delete_worktree(own, leaving)
        self._delete_branch(leaving)

    def free_worktree(self) -> None:
        """Remove the ticket's own worktree, its work committed and pushed on its branch first; the branch stays. A
        ticket that is archived or deleted takes its card away, so it leaves no checkout with unsaved work that no card
        reaches. A worktree a running program holds open stops it before the ticket changes."""
        own = self._own_branch
        if own is not None:
            self._delete_worktree(own, Leaving([LEAVE_DELETE_WORKTREE]))

    def _worktree_to_delete(self, branch: Branch, leaving: Leaving) -> Repo | None:
        """The branch's own worktree when leaving names delete_worktree or delete_branch: git deletes no branch a
        worktree has checked out, so deleting the branch takes its worktree with it. A merge needs neither, since the
        default branch's checkout merges it."""
        if not leaving.removes_worktree:
            return None
        return branch.linked_worktree

    def _save_worktree_to_delete(self, branch: Branch, leaving: Leaving) -> None:
        """Commit and push the work in a worktree leaving is about to delete, whether or not leaving names a commit, so
        the merge that follows carries all of it."""
        if self._worktree_to_delete(branch, leaving) is not None:
            branch.save(self._leave_message)

    def _delete_worktree(self, branch: Branch, leaving: Leaving) -> None:
        """Remove the branch's own worktree folder, its work committed and pushed there, when leaving names it."""
        worktree = self._worktree_to_delete(branch, leaving)
        if worktree is None:
            return
        worktree.close(self._leave_message)
        self._ticket.board.sessions.worktrees.forget()
        self._ticket.board.placement.reread()

    def _delete_branch(self, leaving: Leaving) -> None:
        """Delete the ticket's own branch, here and on origin, when leaving names delete_branch; unmerged unless leaving
        merged it. The branch is read where it is now, the main clone once its worktree is deleted."""
        if not leaving.deletes_branch:
            return
        branch = self.branch
        # git deletes no branch the checkout is on, so the checkout goes back to the default branch first.
        if branch.is_checked_out_here and not self._repo.is_linked_worktree:
            self._repo.default_branch.check_out()
        branch.delete(unmerged=not leaving.merges)
        self._ticket.board.sessions.worktrees.forget()

    def return_to_default_branch(self) -> None:
        """Closing a ticket opens main, the default branch in the repository's own folder, so the closed ticket's own
        branch leaves the repository's checkout. Work left uncommitted goes with the checkout, as git carries it."""
        if not self.branch.is_checked_out_here or self.branch.is_default:
            return
        # A linked worktree cannot check out the default branch while the main checkout has it; the chat goes back to
        # the main checkout instead, so the worktree keeps its branch.
        if self._repo.is_linked_worktree:
            return
        self._repo.default_branch.check_out()



class TicketWorktreeBlockedError(RuntimeError):
    """Raised when a ticket cannot open in its own worktree because the folder that worktree goes in is already there
    and is not the ticket's checkout: a checkout left on no branch, or a folder holding someone's files. It names the
    ticket and the folder, so a person moves or removes the folder and activates the ticket again."""

    def __init__(self, ticket: str, folder: Path) -> None:
        super().__init__(f"{ticket} cannot open in a worktree: the folder {folder} is already there and is not {ticket}'s checkout; move or remove that folder and activate {ticket} again")
        self.ticket = ticket
        self.folder = folder


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
        worktree = [LEAVE_DELETE_WORKTREE] if self._own_branch.linked_worktree is not None else []
        return [LEAVE_MERGE, LEAVE_DELETE_BRANCH, *worktree]

    @property
    @data_field
    def chosen(self) -> list[str]:
        """The choices a person starts with chosen: none, so leaving does only what the person ticks."""
        return []
