"""The saves of a real clone's session folders on main: what only git answers, so each example starts git."""

import shutil
import subprocess
import sys
import time
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.process.git import RepoConnectError
from space.repo.built_once import BuiltOnce
from space.repo.repo import Repo
from space.session.session_saves import SessionSaves

_WAIT_SECONDS = 20
# No settle: every example queues its one change before it waits, so nothing is left to gather into the commit.
_SETTLE_SECONDS = 0


def _git(folder: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=folder, capture_output=True, text=True, check=True).stdout.strip()


def _repository_with_origin(top: Path) -> None:
    """A clone on main with one commit, and the bare repository it pushes to."""
    origin, clone = top / "origin.git", top / "clone"
    _git(top, "init", "--bare", "-b", "main", str(origin))
    _git(top, "init", "-b", "main", str(clone))
    _git(clone, "config", "user.email", "board@example.com")
    _git(clone, "config", "user.name", "Board")
    (clone / "README.md").write_text("project\n", encoding="utf-8")
    _git(clone, "add", "-A")
    _git(clone, "commit", "-m", "start")
    _git(clone, "remote", "add", "origin", str(origin))
    _git(clone, "push", "-u", "origin", "main")


_REPOSITORIES = BuiltOnce("cdd-session-saves-", _repository_with_origin)


def _until(condition, poll: float = 0.05) -> bool:
    deadline = time.monotonic() + _WAIT_SECONDS
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(poll)
    return False


def _subject(folder: Path) -> str:
    return _git(folder, "log", "-1", "--format=%s", "main")


def _ticket_folder(clone: Path) -> Path:
    folder = clone / ".sessions"
    (folder / "checkout-flow").mkdir(parents=True)
    (folder / "checkout-flow" / "session.json").write_text('{"stage": "Specification"}\n', encoding="utf-8")
    return folder


# What only git answers: a commit landing on a real origin, the session folders' own .gitignore, and git's refusal.
with description("the saves of a real clone's session folders on main"):
    with before.each:
        top = _REPOSITORIES.copy()
        self.clone, self.origin = top / "clone", top / "origin.git"
        self.folder = _ticket_folder(self.clone)
        self.saves = SessionSaves(Repo(self.clone), self.folder, settle_seconds=_SETTLE_SECONDS)

    with after.each:
        shutil.rmtree(self.clone.parent, ignore_errors=True)

    with context("that a ticket's change is queued"):
        with before.each:
            self.saves.later("sessions: checkout-flow move Specification")

        with it("should be pushed to origin"):
            expect(_until(lambda: _subject(self.origin) == "sessions: checkout-flow move Specification")).to(equal(True))

    with context("that is queued beside a session's progress cache"):
        with before.each:
            (self.folder / "checkout-flow" / "progress-cache.json").write_text("{}\n", encoding="utf-8")
            self.saves.later("sessions: checkout-flow move Specification")
            _until(lambda: _subject(self.clone) == "sessions: checkout-flow move Specification")

        with it("should leave the cache out of the commit, in a project whose own .gitignore does not name it"):
            expect(_git(self.clone, "ls-files", ".sessions").splitlines()).to(equal([".sessions/.gitignore", ".sessions/checkout-flow/session.json"]))

    with context("that work needs main saved before it goes on"):
        with it("should raise git's refusal to the caller"):
            _git(self.clone, "remote", "set-url", "origin", str(self.clone.parent / "missing.git"))
            expect(lambda: self.saves.now("sessions: open checkout-flow")).to(raise_error(RepoConnectError, contain("Cannot connect git")))
