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

from space.repo.git import RepoConnectError

if TYPE_CHECKING:
    from space.repo.repo import Branch, Repo

logger = logging.getLogger(__name__)

_BRANCH_REF = "refs/heads/"
# A worktree folder is named for its branch; a long branch name is cut to this many characters so the path stays short
# enough for Windows.
_FOLDER_BRANCH_LENGTH = 24
# A branch named for a ticket, such as `checkout-flow-87`, names its worktree folder by the ticket number alone.
_TICKET_NUMBER = re.compile(r"-(\d+)$")


class Worktree:
    """One checkout of the repository: its folder and the branch checked out there."""

    __slots__ = ("path", "branch", "_repository", "sync_failure")

    def __init__(self, path: Path | str, branch: Branch | None, *, repository: Repo | None = None) -> None:
        self.path = Path(path)
        self.branch = branch
        self._repository = repository
        # Why the last fetch or pull from origin failed; empty while this checkout is up to date with origin.
        self.sync_failure = ""

    @classmethod
    def from_repo(cls, repository: Repo) -> Worktree:
        """The checkout ``repository`` works in, with the branch it has checked out."""
        name = (repository.current_branch or "").strip()
        return cls(repository.root, repository.branch_named(name) if name else None, repository=repository)

    @classmethod
    def from_checkout(cls, path: Path | str, branch_name: str) -> Worktree:
        """The checkout at ``path`` with ``branch_name`` checked out; its branch acts in that checkout."""
        repository = _repo_at(path)
        name = (branch_name or "").strip()
        return cls(repository.root, repository.branch_named(name) if name else None, repository=repository)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Worktree):
            return NotImplemented
        return self.path == other.path and self.branch == other.branch

    def __hash__(self) -> int:
        return hash((self.path, self.branch))

    def __repr__(self) -> str:
        branch = self.branch.name if self.branch is not None else ""
        return f"Worktree(path={self.path!r}, branch={branch!r})"

    @property
    def repository(self) -> Repo:
        if self._repository is None:
            self._repository = _repo_at(self.path)
        return self._repository

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
        repository = self.repository
        branch = repository.branch_named(repository.current_branch)
        branch.save(commit_message)
        _repo_at(repository.primary_root()).worktrees.remove(self)
        return branch


class Worktrees:
    """The checkouts of one repository, as ``git worktree`` lists them: the main clone and each linked worktree, each
    with the branch checked out there. A branch is opened in a sibling folder of the main clone."""

    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    def __iter__(self) -> Iterator[Worktree]:
        listing = self._repo.git.run("worktree", "list", "--porcelain")
        for block in listing.split("\n\n"):
            fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
            if "worktree" in fields:
                yield Worktree.from_checkout(Path(fields["worktree"]), fields.get("branch", "").removeprefix(_BRANCH_REF))

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
        if self._repo.current_branch == branch.name:
            opened = Worktree.from_repo(self._repo)
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
        return primary.parent / f"{_abbreviated(primary.name)}-{short}"

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
        return Worktree.from_checkout(dest, branch.name)

    def remove(self, worktree: Worktree) -> None:
        """Remove worktree's folder and forget it, forcing the folder away when git cannot delete a locked checkout."""
        dest = worktree.path
        try:
            self._repo.git.run("worktree", "remove", "--force", str(dest))
        except RepoConnectError as exc:
            logger.info("worktree remove failed; forcing directory delete: %s", exc)
            self._force_remove_directory_windows(dest)
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        if dest.exists():
            self._force_remove_directory_windows(dest)
        if dest.exists():
            return
        try:
            self._repo.git.run("worktree", "prune")
        except RepoConnectError as exc:
            logger.info("worktree prune failed: %s", exc)

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


def _abbreviated(folder: str) -> str:
    """A clone folder's name shortened for its worktrees: `abd-context-driven` is `abd-cd`."""
    tokens = [part for part in re.split(r"[-_]+", folder or "") if part]
    if not tokens:
        return folder or "repo"
    return tokens[0] + ("-" + "".join(token[0] for token in tokens[1:]) if len(tokens) > 1 else "")
