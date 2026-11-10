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

from harness.hooks.hook_daemon import HookDaemon
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
    """One checkout of the repository, as the *Worktrees* that listed it found it: its folder, its own *Repo*, and the
    branch checked out there, each made once when it is listed. Its repository is the one this process holds for its
    folder; the main clone's is the repository that listed it."""

    __slots__ = ("path", "repository", "branch", "_worktrees", "sync_failure")

    def __init__(self, worktrees: Worktrees, path: Path | str, branch_name: str) -> None:
        self._worktrees = worktrees
        self.path = Path(path).resolve()
        self.repository: Repo = worktrees.repository_at(self.path)
        name = (branch_name or "").strip()
        # The branch checked out here, acting in this checkout; none for a checkout on no branch.
        self.branch: Branch | None = self.repository.branch_named(name) if name else None
        # Why the last fetch or pull from origin failed; empty while this checkout is up to date with origin.
        self.sync_failure = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Worktree):
            return NotImplemented
        return self.path == other.path and self.branch == other.branch

    def __hash__(self) -> int:
        return hash((self.path, self.branch))

    def __repr__(self) -> str:
        return f"Worktree(path={self.path!r}, branch={self.branch!r})"

    def fetch_pull(self) -> None:
        """Bring this checkout up to date with origin. A checkout that cannot reach origin, or whose branch has moved
        apart from origin's, still opens as it is; ``sync_failure`` then says why, so the caller can tell the user the
        work may be behind origin."""
        repository = self.repository
        try:
            repository.catch_up_with_origin()
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

    def repository_at(self, folder: Path) -> Repo:
        """The repository as checked out at folder, one of these checkouts: the main clone's own when folder is its."""
        return self._repo if folder == self._repo.root else self._repo.checkout_at(folder)

    def __iter__(self) -> Iterator[Worktree]:
        # Every checkout lists the same worktrees; the main clone lists them even after the checkout these were read
        # from is removed.
        listing = self._repo.main_clone.git.run("worktree", "list", "--porcelain")
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
        return Worktree(self, path, branch_name)

    def remove(self, worktree: Worktree) -> None:
        """Stop the checkout's hook daemon, then remove worktree's folder and forget it, forcing the folder away when git
        cannot delete a locked checkout. A folder still there afterwards raises WorktreeNotRemovedError, so a close is
        never reported done for a checkout that still exists. The main clone runs git for it, since these worktrees may
        have been listed from inside the checkout being removed."""
        dest = worktree.path
        git = self._repo.main_clone.git
        # The checkout's hook daemon runs from its folder; stopped first, it neither outlives the checkout nor holds it.
        HookDaemon(dest).stop()
        try:
            git.run("worktree", "remove", "--force", str(dest))
        except RepoConnectError as exc:
            logger.info("worktree remove failed; forcing directory delete: %s", exc)
        if dest.exists():
            self._rmtree_logged(dest)
        if dest.exists():
            self._force_remove_directory_windows(dest)
        if dest.exists():
            self._unregister_held(dest)
        git.run("worktree", "prune")

    def _unregister_held(self, dest: Path) -> None:
        """A folder a running process works in (a chat, its shells) cannot be deleted on Windows. git forgets it all the
        same once its .git link is gone, so its branch is free to delete; the folder left on disk holds no checkout."""
        link = dest / ".git"
        if link.is_file():
            link.unlink()
        if (dest / ".git").exists():
            raise WorktreeNotRemovedError(dest)
        logger.warning("worktree %s is in use; git no longer lists it, and its folder is left to delete once free", dest)

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
            shutil.rmtree(self._long_path(target), ignore_errors=True)
        except OSError as exc:
            logger.info("rmtree failed for %s: %s", target, exc)

    def _long_path(self, target: Path) -> str:
        """Windows refuses paths past 260 characters unless they carry the \\\\?\\ prefix, and a checkout's retired
        fixtures run past it, so their files would outlive the worktree."""
        resolved = str(target.resolve())
        if os.name != "nt" or resolved.startswith("\\\\?\\"):
            return resolved
        return "\\\\?\\" + resolved

    def _powershell_remove_item(self, target: Path) -> None:
        command = f'Remove-Item -LiteralPath "{target}" -Recurse -Force -ErrorAction SilentlyContinue'
        try:
            subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", command], capture_output=True, check=False)
        except OSError as exc:
            logger.info("powershell Remove-Item failed for %s: %s", target, exc)



