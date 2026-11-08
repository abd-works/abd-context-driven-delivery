"""Worktrees - the checkouts of one repository: the main clone and the linked worktrees beside it."""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from harness.process.git import RepoConnectError

if TYPE_CHECKING:
    from space.repo.repo import Branch, Repo

logger = logging.getLogger(__name__)

_BRANCH_REF = "refs/heads/"
# A worktree folder is named for its branch; a long branch name is cut to this many characters so the path stays short
# enough for Windows.
_FOLDER_BRANCH_LENGTH = 24
# A branch named for a ticket, such as `checkout-flow-87`, names its worktree folder by the ticket number alone.
_TICKET_NUMBER = re.compile(r"-(\d+)$")


class WorktreeNotRemovedError(RuntimeError):
    """Raised when a worktree's folder is still there after git, a forced delete, and the Windows fallbacks each tried
    to remove it, such as a checkout a running program holds open. It names the folder left behind."""

    def __init__(self, folder: Path) -> None:
        super().__init__(f"could not remove the worktree at {folder}; close what holds it open and close it again")
        self.folder = folder


class Worktree:
    """One checkout of the repository, as the *Worktrees* that listed it found it: its folder and the branch checked out
    there. Its repository is the checkout's own *Repo*, made once when first asked for; the main clone's is the
    repository that listed it."""

    __slots__ = ("path", "_branch_name", "_branch", "_worktrees", "_repository", "sync_failure")

    def __init__(self, worktrees: Worktrees, path: Path | str, branch_name: str, *, repository: Repo | None = None) -> None:
        self._worktrees = worktrees
        self.path = Path(path).resolve()
        self._branch_name = (branch_name or "").strip()
        self._branch: Branch | None = None
        self._repository = repository
        # Why the last fetch or pull from origin failed; empty while this checkout is up to date with origin.
        self.sync_failure = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Worktree):
            return NotImplemented
        return self.path == other.path and self._branch_name == other._branch_name

    def __hash__(self) -> int:
        return hash((self.path, self._branch_name))

    def __repr__(self) -> str:
        return f"Worktree(path={self.path!r}, branch={self._branch_name!r})"

    @property
    def repository(self) -> Repo:
        if self._repository is None:
            self._repository = _repo_at(self.path)
        return self._repository

    @property
    def branch(self) -> Branch | None:
        """The branch checked out here, acting in this checkout; none for a checkout on no branch."""
        if self._branch is None and self._branch_name:
            self._branch = self.repository.branch_named(self._branch_name)
        return self._branch

    def fetch_pull(self) -> None:
        """Bring this checkout up to date with origin. A checkout that cannot reach origin, or whose branch has moved
        apart from origin's, still opens as it is; ``sync_failure`` then says why, so the caller can tell the user the
        work may be behind origin."""
        repository = self.repository
        try:
            repository.fetch()
            repository.pull()
        except RepoConnectError as exc:
            self.sync_failure = str(exc)
            logger.warning("worktree %s is not up to date with origin: %s", self.path, exc)
            return
        self.sync_failure = ""

    def close(self, commit_message: str) -> Branch:
        """Commit and push the branch checked out here, then remove this checkout; the branch stays open."""
        branch = self.repository.current_branch
        branch.save(commit_message)
        self._worktrees.remove(self)
        return branch


class Worktrees:
    """The checkouts of one repository, as ``git worktree`` lists them: the main clone and each linked worktree, each
    with the branch checked out there. A branch is opened in a sibling folder of the main clone. Each listed *Worktree*
    keeps the *Worktrees* that listed it, which removes it when it closes."""

    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    def __iter__(self) -> Iterator[Worktree]:
        listing = self._repo.git.run("worktree", "list", "--porcelain")
        for block in listing.split("\n\n"):
            fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
            if "worktree" in fields:
                yield self._listed(Path(fields["worktree"]), fields.get("branch", "").removeprefix(_BRANCH_REF))

    def at(self, folder: Path | str) -> Worktree | None:
        """The checkout git lists at folder; none when git lists none there."""
        wanted = Path(folder).resolve()
        return next((tree for tree in self if tree.path == wanted), None)

    def of(self, branch: Branch) -> Worktree | None:
        """The checkout that has branch checked out; none when no checkout has it."""
        return next((tree for tree in self if tree.branch == branch), None)

    def open(self, branch: Branch) -> Worktree:
        """Check branch out in a sibling worktree, up to date with origin where origin can be reached, and return it:
        the worktree that already has it, or the main clone when the clone has it checked out."""
        existing = self.of(branch)
        if existing is not None and existing.path.resolve() != self._repo.root:
            existing.fetch_pull()
            return existing
        if self._repo.current_branch == branch:
            opened = self._listed(self._repo.root, branch.name)
            opened.fetch_pull()
            return opened
        try:
            # Fetched first so a branch pushed from elsewhere starts from origin's copy.
            self._repo.fetch()
        except RepoConnectError as exc:
            logger.warning("opening %s from local refs; fetch from origin failed: %s", branch.name, exc)
        opened = self.add(self.sibling_folder(branch), branch)
        opened.fetch_pull()
        return opened

    def sibling_folder(self, branch: Branch) -> Path:
        """The folder beside the main clone that branch's worktree gets: ``{abbreviated clone}-{short branch}``."""
        primary = self._repo.primary_root()
        slug = branch.name.replace("/", "-")
        ticket = _TICKET_NUMBER.search(slug)
        short = ticket.group(1) if ticket else slug[:_FOLDER_BRANCH_LENGTH].rstrip("-")
        return primary.parent / f"{self._abbreviated(primary.name)}-{short}"

    def _abbreviated(self, folder: str) -> str:
        """A clone folder's name shortened for its worktrees: `abd-context-driven` is `abd-cd`."""
        tokens = [part for part in re.split(r"[-_]+", folder or "") if part]
        if not tokens:
            return folder or "repo"
        return tokens[0] + ("-" + "".join(token[0] for token in tokens[1:]) if len(tokens) > 1 else "")

    def add(self, path: str | Path, branch: Branch) -> Worktree:
        """Check branch out in a new worktree at path; the worktree that already has it, when one does."""
        existing = self.of(branch)
        if existing is not None:
            return existing
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if branch.exists:
            self._repo.git.run("worktree", "add", str(dest), branch.name)
        else:
            self._repo.git.run("worktree", "add", "-b", branch.name, str(dest), branch.start_point)
        return self._listed(dest, branch.name)

    def _listed(self, folder: Path, branch_name: str) -> Worktree:
        """The checkout at folder with branch_name checked out; the main clone's repository is the one held here."""
        path = Path(folder).resolve()
        return Worktree(self, path, branch_name, repository=self._repo if path == self._repo.root else None)

    def remove(self, worktree: Worktree) -> None:
        """Remove worktree's folder and forget it, forcing the folder away when git cannot delete a locked checkout.
        A folder still there afterwards raises WorktreeNotRemovedError, so a close is never reported done for a checkout
        that still exists."""
        dest = worktree.path
        try:
            self._repo.git.run("worktree", "remove", "--force", str(dest))
        except RepoConnectError as exc:
            logger.info("worktree remove failed; forcing directory delete: %s", exc)
        if dest.exists():
            self._rmtree_logged(dest)
        if dest.exists():
            self._force_remove_directory_windows(dest)
        if dest.exists():
            raise WorktreeNotRemovedError(dest)
        self._repo.git.run("worktree", "prune")

    def _force_remove_directory_windows(self, path: Path) -> bool:
        """Last resort when git/shutil cannot delete a locked checkout (Windows only)."""
        if os.name != "nt":
            return False
        target = path.resolve()
        if not target.exists():
            return True
        user = os.environ.get("USERNAME", "").strip()
        if not user:
            return False
        self._take_windows_ownership(target, user)
        self._rmtree_logged(target)
        if target.exists():
            self._powershell_remove_item(target)
        return not target.exists()

    def _take_windows_ownership(self, target: Path, user: str) -> None:
        for args in (
            ("takeown", "/f", str(target), "/r", "/d", "y"),
            ("icacls", str(target), "/grant", f"{user}:(F)", "/t"),
        ):
            try:
                subprocess.run(list(args), capture_output=True, check=False)
            except OSError as exc:
                logger.info("windows ownership command failed: %s", exc)

    def _rmtree_logged(self, target: Path) -> None:
        try:
            shutil.rmtree(target, ignore_errors=True)
        except OSError as exc:
            logger.info("rmtree failed for %s: %s", target, exc)

    def _powershell_remove_item(self, target: Path) -> None:
        command = f'Remove-Item -LiteralPath "{target}" -Recurse -Force -ErrorAction SilentlyContinue'
        try:
            subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", command], capture_output=True, check=False)
        except OSError as exc:
            logger.info("powershell Remove-Item failed for %s: %s", target, exc)


def _repo_at(folder: Path | str) -> Repo:
    # WHY: space.repo.repo builds its Worktrees from this module, so Repo is imported when a checkout is first read.
    from space.repo.repo import Repo

    return Repo(folder)

