"""WorktreeClearing - clearing away the checkouts of a repository whose work is done, and what they leave behind."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from harness.git.git import RepoConnectError
from harness.installation.data_class import data_field, data_fields
from harness.installation.json_file import JsonFile
from space.repo.folder_deletion import FolderDeletion
from space.repo.worktree import WorktreeNotRemovedError, Worktrees
from space.work_state import COMPLETE_FOLDER, SESSIONS_FOLDER

if TYPE_CHECKING:
    from space.repo.repo import Repo

logger = logging.getLogger(__name__)

# The file of a session folder that names the branch the session works on.
_SESSION_RECORD = "session.json"
# What the first line of a linked worktree's .git file starts with, before the path of its record in git's folder.
_GITDIR = "gitdir:"


@data_fields
@dataclass(frozen=True)
class ClearedFolder:
    """One folder a clearing looked at, and why it was removed or kept."""

    folder: str
    reason: str

    @property
    def line(self) -> str:
        return f"- {self.folder}: {self.reason}"


class ClearedWorktrees:
    """What clearing a repository's worktrees did: the folders and records it removed and the folders it kept, each with
    why, and the same said in words for the chat."""

    def __init__(self) -> None:
        self._removed: list[ClearedFolder] = []
        self._kept: list[ClearedFolder] = []

    @property
    @data_field
    def removed(self) -> list[ClearedFolder]:
        return list(self._removed)

    @property
    @data_field
    def kept(self) -> list[ClearedFolder]:
        return list(self._kept)

    @property
    @data_field
    def report(self) -> str:
        """Each folder removed and each kept, one line each with why."""
        return "\n".join([self._heading("Removed", self._removed), *(cleared.line for cleared in self._removed), self._heading("Kept", self._kept), *(cleared.line for cleared in self._kept)])

    def _heading(self, done: str, folders: list[ClearedFolder]) -> str:
        return f"{done} {len(folders)}:" if folders else f"{done} nothing."

    def remove(self, folder: Path, reason: str) -> None:
        self._removed.append(ClearedFolder(str(folder), reason))

    def keep(self, folder: Path, reason: str) -> None:
        self._kept.append(ClearedFolder(str(folder), reason))


class WorktreeClearing:
    """The clearing of one repository's checkouts once their work is done, as was done by hand on 2026-11-24. A worktree
    whose work is all on main and holds nothing uncommitted is removed, its branch kept; the main clone, the worktree the
    call works in, a worktree whose branch has commits not on main (whether or not its session is closed), and one holding
    work not committed are kept. A folder beside the main clone named as its worktrees are, which git no longer lists, is
    deleted; a repository of its own there is kept. git's record of a worktree whose folder is gone is deleted. Each is
    answered with why."""

    def __init__(self, worktrees: Worktrees, main_clone: Repo, keeping: Repo) -> None:
        self._worktrees = worktrees
        self._main_clone = main_clone
        self._keeping = keeping.root
        self._cleared = ClearedWorktrees()

    def clear(self) -> ClearedWorktrees:
        """Clear what is done and answer what was removed and what was kept. The stale records are read first, since
        removing a worktree prunes them."""
        stale = self._stale_records()
        listed = self._main_clone.checkout.facts.worktrees()
        for folder, branch in listed:
            if folder.is_dir():
                self._clear_checkout(folder.resolve(), branch)
        self._clear_leftover_folders({folder.resolve() for folder, _ in listed})
        self._delete_records(stale)
        return self._cleared

    def _clear_checkout(self, folder: Path, branch: str) -> None:
        reason = self._reason_to_keep(folder, branch)
        if reason:
            self._cleared.keep(folder, reason)
            return
        try:
            self._worktrees.remove(self._worktrees.repository_at(folder))
        except WorktreeNotRemovedError:
            self._cleared.keep(folder, "its work is all on main, but a running program holds its folder open")
            return
        self._cleared.remove(folder, self._reason_removed(branch))

    def _reason_to_keep(self, folder: Path, branch: str) -> str:
        """Why the checkout at folder stays; empty when its work is done."""
        if folder == self._main_clone.root:
            return "the main clone"
        if folder == self._keeping:
            return "the worktree this call works in"
        ahead = self._commits_not_on_main(branch or self._worktrees.repository_at(folder).current_commit)
        if ahead:
            return self._reason_kept_for_commits(branch, ahead)
        if self._worktrees.repository_at(folder).working_tree.is_dirty():
            return "it holds work not committed"
        return ""

    def _reason_kept_for_commits(self, branch: str, ahead: int) -> str:
        commits = f"{ahead} commit{'' if ahead == 1 else 's'} not on {self._main}"
        session = self._closed_sessions.get(branch, "")
        if session:
            return f"its session {session} is closed, but its branch {branch} has {commits}"
        return f"its branch {branch or '(none)'} has {commits}"

    def _reason_removed(self, branch: str) -> str:
        merged = f"its branch {branch} is merged into {self._main}" if branch else f"its commit is on {self._main}"
        session = self._closed_sessions.get(branch, "")
        return f"{merged} and its session {session} is closed" if session else merged

    def _commits_not_on_main(self, ref: str) -> int:
        return int(self._main_clone.git.run("rev-list", "--count", f"{self._main}..{ref}") or 0)

    @property
    def _main(self) -> str:
        return self._main_clone.default_branch.name

    @cached_property
    def _closed_sessions(self) -> dict[str, str]:
        """The closed session of each branch, by its folder's name, read from the sessions folder's closed sessions."""
        closed = self._main_clone.root / SESSIONS_FOLDER / COMPLETE_FOLDER
        records = sorted(closed.glob(f"*/{_SESSION_RECORD}")) if closed.is_dir() else []
        branches = ((str(JsonFile(record).read().get("branch", "")), record.parent.name) for record in records)
        return {branch: name for branch, name in branches if branch}

    def _clear_leftover_folders(self, listed: set[Path]) -> None:
        """Delete each folder beside the main clone named as its worktrees are that is no checkout git lists, keeping a
        repository of its own and a worktree of another repository."""
        beside = self._main_clone.root.parent
        prefix = self._worktrees.sibling_prefix
        for folder in sorted(beside.iterdir()):
            if folder.is_dir() and folder.name.startswith(prefix) and folder.resolve() not in listed:
                self._clear_leftover(folder.resolve())

    def _clear_leftover(self, folder: Path) -> None:
        link = folder / ".git"
        if link.is_dir():
            self._cleared.keep(folder, "a repository of its own")
            return
        if link.is_file() and not self._names_own_record(link):
            self._cleared.keep(folder, "a worktree of another repository")
            return
        if FolderDeletion(folder).delete():
            self._cleared.remove(folder, "it is no longer a worktree")
        else:
            self._cleared.keep(folder, "it is no longer a worktree, but a running program holds it open")

    def _names_own_record(self, link: Path) -> bool:
        """Whether a .git file names a record in this repository's git folder, as a worktree of this repository does."""
        named = link.read_text(encoding="utf-8").strip().removeprefix(_GITDIR).strip()
        return Path(named).resolve().is_relative_to(self._records_folder.resolve())

    @property
    def _records_folder(self) -> Path:
        return self._main_clone.checkout.facts.common_folder() / "worktrees"

    def _stale_records(self) -> dict[Path, Path]:
        """Each record git keeps of a worktree whose folder is gone, with the folder it names."""
        records = sorted(self._records_folder.iterdir()) if self._records_folder.is_dir() else []
        named = {record: self._folder_named_by(record) for record in records if record.is_dir()}
        return {record: folder for record, folder in named.items() if not folder.is_dir()}

    def _folder_named_by(self, record: Path) -> Path:
        gitdir = record / "gitdir"
        return Path(gitdir.read_text(encoding="utf-8").strip()).parent if gitdir.is_file() else record

    def _delete_records(self, stale: dict[Path, Path]) -> None:
        """Have git prune its records of worktrees whose folder is gone, then delete what it refused."""
        try:
            self._main_clone.git.run("worktree", "prune")
        except RepoConnectError as exc:
            logger.info("git worktree prune failed; deleting its records directly: %s", exc)
        for record, folder in stale.items():
            if FolderDeletion(record).delete():
                self._cleared.remove(folder, "its folder is gone, so git's record of it was deleted")
            else:
                self._cleared.keep(folder, f"its folder is gone, but git's record of it, {record}, could not be deleted")
