"""The commits that keep every ticket's record on main, made and pushed on a thread of their own."""
from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

from harness.installation.data_class import data_field
from harness.process.git import RepoConnectError
from space.repo.repo import Repo
from space.session.progress_cache import PROGRESS_CACHE_FILE

logger = logging.getLogger(__name__)

# How long a queued save waits before it commits, so every file one change writes, such as a ticket's folder moved to
# the Backlog and then its item file, goes into the one commit. Also how often it looks again while a merge is going on.
SETTLE_SECONDS = 0.5
# The line in the session folders' .gitignore that keeps every session's progress cache out of the saves.
_IGNORED_CACHES = f"**/{PROGRESS_CACHE_FILE}"


class SaveFailure:
    """*SaveFailure* is a save on main that git refused: the changes it was saving and what git said. The changes are
    still in the session folders, so saving again commits them."""

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


class SessionSaves:
    """*SessionSaves* commits the session folders of one repository on main and pushes main, so every chat and worktree
    reads the same board. A change to a ticket is written to its session folder at once and its save is queued here:
    git, and the push above all, can take seconds, and a person moving a card should not wait for it. Queued saves are
    made one at a time on a thread of their own, several waiting saves in one commit.

    A save git refuses is kept as the failure, which the board shows with a way to save again; the next save that
    succeeds clears it. Work that needs main committed before it goes on, such as opening a ticket's worktree, saves
    ``now``, which waits for the queued saves and makes its own in the caller's thread."""

    def __init__(self, repository: Repo, folder: Path) -> None:
        self._repository = repository
        self._folder = folder
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
        """Queue a save with message; it is made on the saving thread, started when none is running."""
        with self._queue:
            self._pending.append(message)
            if self._worker is None:
                self._worker = threading.Thread(target=self._work, name="session-saves", daemon=True)
                self._worker.start()

    def now(self, message: str) -> None:
        """Save with message in this thread, with every save still queued; git's refusal is raised to the caller."""
        with self._saving:
            changes = [*self._taken(), message]
            self._save(changes)

    def retry(self) -> None:
        """Save again what the latest failure did not save."""
        failed = self._failure
        if failed is not None:
            self.later(f"sessions: save again {', '.join(failed.changes)}")

    def _work(self) -> None:
        while True:
            time.sleep(SETTLE_SECONDS)
            with self._queue:
                if not self._pending:
                    self._worker = None
                    return
            self._save_queued()

    def _save_queued(self) -> None:
        # A commit during a merge concludes the merge with everything staged, so the saves wait for it to finish.
        if self._repository.is_merging:
            return
        with self._saving:
            changes = self._taken()
            if not changes:
                return
            try:
                self._save(changes)
            except RepoConnectError as refused:
                logger.warning("the board's saves on main failed: %s", refused)
                self._failure = SaveFailure(changes, str(refused))

    def _taken(self) -> list[str]:
        with self._queue:
            changes, self._pending = self._pending, []
        return changes

    def _save(self, changes: list[str]) -> None:
        """Commit the session folders with changes as the message and push main, while main is checked out in the
        repository's own folder; a save with nothing to commit or push does nothing."""
        repository = self._repository
        if not repository.branch_named(repository.default_branch).is_checked_out or not self._folder.is_dir():
            return
        self._keep_caches_out()
        if repository.is_dirty(self._folder):
            repository.commit([str(self._folder)], "\n".join(changes), untracked=True)
            self._is_unpushed = True
        if self._is_unpushed and repository.has_origin:
            repository.push_upstream()
        self._is_unpushed = False
        self._failure = None

    def _keep_caches_out(self) -> None:
        """List the board's progress caches in the session folders' own .gitignore, so a save never commits one, in a
        project whose own .gitignore does not name them: a cache is worked out again wherever it is missing."""
        ignore = self._folder / ".gitignore"
        written = ignore.read_text(encoding="utf-8") if ignore.is_file() else ""
        if _IGNORED_CACHES in written.splitlines():
            return
        lead = "" if not written or written.endswith("\n") else "\n"
        ignore.write_text(f"{written}{lead}{_IGNORED_CACHES}\n", encoding="utf-8")


class ServedSaves:
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


SERVED_SAVES = ServedSaves()
