"""The commits that keep every ticket's record on main, made and pushed on a thread of their own."""
from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import ClassVar

from harness.installation.data_class import data_field
from harness.installation.json_file import LEFT_BESIDE
from harness.git.git import RepoConnectError
from space.repo.repo import Repo

logger = logging.getLogger(__name__)

# How long a queued save waits before it commits, so every file one change writes, such as a ticket's folder moved to
# the Backlog and then its item file, goes into the one commit. Also how often it looks again while a merge is going on.
SETTLE_SECONDS = 0.5


class SaveFailure:
    """*SaveFailure* is a save on main that could not be made: the changes it was saving and why, such as what git said
    when it refused, or the branch the repository's own folder has checked out instead of main. The changes are still in
    the session folders, so saving again commits them."""

    def __init__(self, changes: list[str], error: str) -> None:
        self._changes = list(changes)
        self._error = error

    @property
    @data_field
    def changes(self) -> list[str]:
        """Each change that is not saved yet, such as ``sessions: checkout-flow move Specification``."""
        return list(self._changes)

    @property
    @data_field
    def error(self) -> str:
        return self._error


class DefaultBranchNotCheckedOut(Exception):
    """The session folders are saved on the default branch, and the repository's own folder has another branch checked
    out, so a commit there would put the records on that branch. The changes stay on disk until the default branch is
    checked out there again."""

    def __init__(self, folder: Path, checked_out: str, default: str) -> None:
        super().__init__(
            f"the session folders are saved on {default}, but {folder} has {checked_out} checked out; the changes stay "
            f"on disk and are saved once {default} is checked out there again")
        self.folder = folder
        self.checked_out = checked_out
        self.default = default


class SessionSaves:
    """*SessionSaves* commits the session folders of one repository on main and pushes main, so every chat and worktree
    reads the same board. A change to a ticket is written to its session folder at once and its save is queued here:
    git, and the push above all, can take seconds, and a person moving a card should not wait for it. Queued saves are
    made one at a time on a thread of their own, several waiting saves in one commit.

    A save git refuses is kept as the failure, which the board shows with a way to save again; the next save that
    succeeds clears it. Work that needs main committed before it goes on, such as opening a ticket's worktree, saves
    ``now``, which waits for the queued saves and makes its own in the caller's thread."""

    # The files in the session folders that no save commits, each a .gitignore pattern: what every JSON file's writes
    # leave beside it for a moment (``LEFT_BESIDE``), since git would add staged text that is renamed away as it reads
    # it; and each pattern a module that writes such a file registers when it is imported (``leave_out``), such as the
    # board's progress caches, which are worked out again wherever they are missing.
    _left_out: ClassVar[list[str]] = [f"**/{pattern}" for pattern in LEFT_BESIDE]

    @classmethod
    def leave_out(cls, pattern: str) -> None:
        """Leave every file pattern names, a .gitignore pattern such as ``**/progress-cache.json``, out of every save."""
        if pattern not in cls._left_out:
            cls._left_out.append(pattern)

    def __init__(self, repository: Repo, folder: Path, settle_seconds: float = SETTLE_SECONDS) -> None:
        self._repository = repository
        self._folder = folder
        # How long a queued save waits before it commits; a spec that queues one change at a time waits less.
        self._settle_seconds = settle_seconds
        self._pending: list[str] = []
        self._worker: threading.Thread | None = None
        # One commit on main at a time, whether queued or made now: two at once fight over git's index.
        self._saving = threading.Lock()
        self._queue = threading.Lock()
        self._failure: SaveFailure | None = None
        # A commit whose push failed is pushed by the next save, even when that save finds nothing new to commit.
        self._is_unpushed = False

    @property
    def failure(self) -> SaveFailure | None:
        """The latest save git refused, until a save succeeds."""
        return self._failure

    def later(self, message: str) -> None:
        """Queue a save with message; it is made on the saving thread, started when none is running. A project git does
        not hold has nothing to commit, so its save is not queued and no thread is started for it."""
        if not self._repository.is_clone:
            return
        with self._queue:
            self._pending.append(message)
            if self._worker is None:
                self._worker = threading.Thread(target=self._work, name="session-saves", daemon=True)
                self._worker.start()

    def now(self, message: str) -> None:
        """Save with message in this thread, with every save still queued; git's refusal is raised to the caller, and so
        is *DefaultBranchNotCheckedOut*, which leaves the queued saves waiting."""
        with self._saving:
            self._refuse_off_default_branch()
            changes = [*self._taken(), message]
            self._save(changes)

    def retry(self) -> None:
        """Save again what the latest failure did not save."""
        failed = self._failure
        if failed is not None:
            self.later(f"sessions: save again {', '.join(failed.changes)}")

    def _work(self) -> None:
        while True:
            time.sleep(self._settle_seconds)
            with self._queue:
                if not self._pending:
                    self._worker = None
                    return
            self._save_queued()

    def _save_queued(self) -> None:
        # A commit during a merge concludes the merge with everything staged, so the saves wait for it to finish.
        if self._repository.working_tree.is_merging:
            return
        with self._saving:
            try:
                self._refuse_off_default_branch()
            except DefaultBranchNotCheckedOut as away:
                self._wait_for_default_branch(away)
                return
            changes = self._taken()
            if not changes:
                return
            try:
                self._save(changes)
            except RepoConnectError as refused:
                logger.warning("the board's saves on main failed: %s", refused)
                self._failure = SaveFailure(changes, str(refused))

    def _refuse_off_default_branch(self) -> None:
        repository = self._repository
        if not repository.is_clone:
            return
        checked_out = repository.current_branch
        if checked_out != repository.default_branch:
            raise DefaultBranchNotCheckedOut(repository.root, checked_out.name, repository.default_branch.name)

    def _wait_for_default_branch(self, away: DefaultBranchNotCheckedOut) -> None:
        """Keep the queued saves queued, as during a merge, and say why on the board: the saving thread looks again
        after each settle, and saves them once the default branch is checked out in the repository's own folder."""
        with self._queue:
            waiting = list(self._pending)
        if self._failure is None or self._failure.error != str(away):
            logger.warning("the board's saves on main wait: %s", away)
        self._failure = SaveFailure(waiting, str(away))

    def _taken(self) -> list[str]:
        with self._queue:
            changes, self._pending = self._pending, []
        return changes

    def _save(self, changes: list[str]) -> None:
        """Commit the session folders with changes as the message and push main, which the caller found checked out in
        the repository's own folder; a save with nothing to commit or push does nothing. In a repository git init made,
        the first save is its first commit, so a ticket's branch has a commit to start from."""
        repository = self._repository
        if not repository.is_clone or not self._folder.is_dir():
            return
        self._keep_left_out()
        if repository.working_tree.is_dirty(self._folder):
            repository.working_tree.commit([str(self._folder)], "\n".join(changes), untracked=True)
            self._is_unpushed = True
        if self._is_unpushed and repository.has_origin:
            repository.origin.push_upstream()
        self._is_unpushed = False
        self._failure = None

    def _keep_left_out(self) -> None:
        """List each file the saves leave out (``leave_out``) in the session folders' own .gitignore, so a save never
        commits one, in a project whose own .gitignore does not name it."""
        ignore = self._folder / ".gitignore"
        written = ignore.read_text(encoding="utf-8") if ignore.is_file() else ""
        missing = [pattern for pattern in self._left_out if pattern not in written.splitlines()]
        if not missing:
            return
        lead = "" if not written or written.endswith("\n") else "\n"
        ignore.write_text(written + lead + "".join(f"{pattern}\n" for pattern in missing), encoding="utf-8")


class _ServedSaves:
    """The saves of every repository this process works in, each made once, by the folder of its main clone: the main
    checkout and its worktrees all save to the one ``.sessions`` there, so they share one queue."""

    def __init__(self) -> None:
        self._held: dict[Path, SessionSaves] = {}
        self._lock = threading.Lock()

    def of(self, repository: Repo, folder: Path) -> SessionSaves:
        """The saves of the session folder folder, kept in repository, the main clone that holds it."""
        with self._lock:
            held = self._held.get(folder)
            if held is None:
                held = self._held[folder] = SessionSaves(repository, folder)
            return held


SERVED_SAVES = _ServedSaves()
