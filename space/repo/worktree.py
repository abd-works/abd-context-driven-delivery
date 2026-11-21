"""Worktrees - the checkouts of one repository: the main clone and the linked worktrees beside it, each a *Repo*."""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from harness.hooks.hook_daemon import HookDaemon
from harness.git.git import RepoConnectError

if TYPE_CHECKING:
    from space.repo.repo import Branch, Repo, ServedCheckouts

logger = logging.getLogger(__name__)

# A worktree folder is named for its branch; a long branch name is cut to this many characters so the path stays short
# enough for Windows.
_FOLDER_BRANCH_LENGTH = 24
# A branch named for a ticket, such as `checkout-flow-87`, names its worktree folder by the ticket number alone.
_TICKET_NUMBER = re.compile(r"-(\d+)$")
# The number the second branch's folder ends with when two branches would get one worktree folder.
_SECOND_FOLDER_NUMBER = 2


class WorktreeNotRemovedError(RuntimeError):
    """Raised when a worktree's folder is still there after git, a forced delete, and the Windows fallbacks each tried
    to remove it, such as a checkout a running program holds open. It names the folder left behind. The branch's work
    was committed and pushed before the removal, and git no longer lists the folder as a checkout."""

    def __init__(self, folder: Path) -> None:
        super().__init__(f"could not remove the worktree at {folder}; close what holds it open and close it again")
        self.folder = folder


class WorktreeFolderTakenError(RuntimeError):
    """Raised when a branch is to be opened in a worktree whose folder is already there and is not that branch's
    checkout: a checkout left on no branch, or a folder holding files that git lists as no checkout. It names the
    branch and the folder, so a person moves or removes the folder and opens the branch again."""

    def __init__(self, branch: str, folder: Path) -> None:
        super().__init__(f"cannot open {branch} in a worktree at {folder}: that folder is already there and is not {branch}'s checkout; move or remove it and open {branch} again")
        self.branch = branch
        self.folder = folder


class Worktrees:
    """The checkouts of one repository, as ``git worktree`` lists them: the main clone and each linked worktree, each the
    *Repo* this process holds for its folder. A branch is opened in a sibling folder of the main clone. Which branch each
    checkout has out is read from the listing, so asking which checkout has a branch starts no git for each of them."""

    def __init__(self, repo: Repo, checkouts: ServedCheckouts) -> None:
        self._repo = repo
        self._checkouts = checkouts
        # Held while a branch is looked for and its worktree made, so two callers opening one branch get one worktree.
        self._opening = threading.Lock()

    def repository_at(self, folder: Path | str) -> Repo:
        """The repository as checked out at folder, one of these checkouts, as this process holds it: this checkout's own
        when folder is its."""
        resolved = Path(folder).resolve()
        return self._repo if resolved == self._repo.root else self._checkouts.at(resolved)

    def __iter__(self) -> Iterator[Repo]:
        for path, _ in self._on_disk():
            yield self.repository_at(path)

    def _on_disk(self) -> list[tuple[Path, str]]:
        """Each checkout with the branch it has out, empty when none is, as the main clone lists them: every checkout
        lists the same worktrees, and the main clone lists them even after the checkout these were read from is removed.
        git goes on listing a checkout whose folder was deleted by hand until it is pruned; with no folder there is no
        checkout to work in, so it is not one of these."""
        listed = self._repo.main_clone.checkout.facts.worktrees()
        return [(Path(path).resolve(), branch) for path, branch in listed if Path(path).is_dir()]

    @property
    def by_branch(self) -> dict[Branch, Repo]:
        """The checkout each branch is checked out in, for every branch some checkout has out."""
        return {self._repo.branch_named(name): self.repository_at(path) for path, name in self._on_disk() if name}

    def primary_root(self) -> Path:
        """The repository's main checkout. A linked worktree's ``.git`` is a file naming its git folder, whose
        ``commondir`` leads back to the main checkout's ``.git``; any other checkout is its own main checkout."""
        return self._repo.checkout.main_folder

    def at(self, folder: Path | str) -> Repo | None:
        """The checkout git lists at folder; none when git lists none there."""
        wanted = Path(folder).resolve()
        return next((self.repository_at(path) for path, _ in self._on_disk() if path == wanted), None)

    def of(self, branch: Branch) -> Repo | None:
        """The checkout that has branch checked out; none when no checkout has it."""
        return next((self.repository_at(path) for path, name in self._on_disk() if name and name == branch.name), None)

    def open(self, branch: Branch) -> Repo:
        """Check branch out in a sibling worktree, up to date with origin where origin can be reached, and return it:
        the worktree that already has it, or the main clone when the clone has it checked out. A folder in the way that
        is not branch's checkout raises ``WorktreeFolderTakenError``."""
        with self._opening:
            existing = self.of(branch)
            if existing is not None and existing.root != self._repo.root:
                existing.catch_up_with_origin()
                return existing
            if self._repo.current_branch == branch:
                self._repo.catch_up_with_origin()
                return self._repo
            return self._added_from_origin(branch)

    def _added_from_origin(self, branch: Branch) -> Repo:
        """A new sibling worktree for branch, up to date with origin, or from local refs when origin cannot be reached."""
        try:
            # Fetched first so a branch pushed from elsewhere starts from origin's copy.
            self._repo.origin.fetch()
        except RepoConnectError as exc:
            logger.warning("opening %s from local refs; fetch from origin failed: %s", branch.name, exc)
            opened = self.add(self.sibling_folder(branch), branch)
            opened.catch_up_with_origin()
            return opened
        # The worktree shares the clone's refs, so what was just fetched is what it merges.
        opened = self.add(self.sibling_folder(branch), branch)
        opened.catch_up_with_origin(fetched=True)
        return opened

    def sibling_folder(self, branch: Branch) -> Path:
        """The folder beside the main clone that branch's worktree gets: ``{abbreviated clone}-{short branch}``. Two
        branches whose short names are the same never share it: while another branch's checkout has that folder, branch
        gets the next one no other branch has, numbered ``-2``, ``-3``, and on."""
        primary = self.primary_root()
        slug = branch.name.replace("/", "-")
        ticket = _TICKET_NUMBER.search(slug)
        short = ticket.group(1) if ticket else slug[:_FOLDER_BRANCH_LENGTH].rstrip("-")
        first = primary.parent / f"{self._abbreviated(primary.name)}-{short}"
        of_other_branches = {path for path, name in self._on_disk() if name and name != branch.name}
        numbered = (first.with_name(f"{first.name}-{number}") for number in range(_SECOND_FOLDER_NUMBER, _SECOND_FOLDER_NUMBER + len(of_other_branches)))
        return next(folder for folder in (first, *numbered) if folder.resolve() not in of_other_branches)

    def _abbreviated(self, folder: str) -> str:
        """A clone folder's name shortened for its worktrees: `abd-context-driven` is `abd-cd`."""
        tokens = [part for part in re.split(r"[-_]+", folder or "") if part]
        if not tokens:
            return folder or "repo"
        return tokens[0] + ("-" + "".join(token[0] for token in tokens[1:]) if len(tokens) > 1 else "")

    def add(self, path: str | Path, branch: Branch) -> Repo:
        """Check branch out in a new worktree at path; the worktree that already has it, when one does. A folder already
        at path that is not branch's checkout raises ``WorktreeFolderTakenError``, unless it is the empty folder a
        removed worktree left, which is cleared."""
        existing = self.of(branch)
        if existing is not None:
            return existing
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        self._clear_folder_for(branch, dest)
        # git refuses a path and a branch it still lists for a checkout whose folder is gone.
        self._repo.git.run("worktree", "prune")
        if branch.exists:
            self._repo.git.run("worktree", "add", str(dest), branch.name)
        else:
            self._repo.git.run("worktree", "add", "-b", branch.name, str(dest), branch.start_point)
        return self.repository_at(dest)

    def _clear_folder_for(self, branch: Branch, dest: Path) -> None:
        """Make sure nothing is at dest before branch's worktree is made there. A folder holding no file is what a
        worktree removed while a program held it open left behind, and is deleted; a checkout git lists there, or a
        folder with files in it, is someone's work and is refused by name."""
        if not dest.exists():
            return
        holds_files = dest.is_file() or any(entry.is_file() for entry in dest.rglob("*"))
        if holds_files or self.at(dest) is not None:
            raise WorktreeFolderTakenError(branch.name, dest)
        self._rmtree_logged(dest)
        if dest.exists():
            raise WorktreeFolderTakenError(branch.name, dest)

    def remove(self, worktree: Repo) -> None:
        """Stop the checkout's hook daemon, then remove worktree's folder and forget it, forcing the folder away when git
        cannot delete a locked checkout. A folder still there afterwards raises WorktreeNotRemovedError, so a close is
        never reported done for a checkout that still exists. The main clone runs git for it, since these worktrees may
        have been listed from inside the checkout being removed."""
        dest = worktree.root
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
        if dest.exists():
            raise WorktreeNotRemovedError(dest)

    def _unregister_held(self, dest: Path) -> None:
        """A folder a running process works in (a chat, its shells) cannot be deleted on Windows. git forgets it all the
        same once its .git link is gone, so the folder left on disk holds no checkout, and its branch opens in a
        worktree again once the folder is free."""
        link = dest / ".git"
        if link.is_file():
            link.unlink()

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



