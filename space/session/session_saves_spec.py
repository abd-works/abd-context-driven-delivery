"""The saves that keep every ticket's record on main: queued, made on their own thread, and shown when git refuses."""

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
_SETTLE_SECONDS = 0.05


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


def _until(condition) -> bool:
    deadline = time.monotonic() + _WAIT_SECONDS
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.1)
    return False


def _subject(folder: Path) -> str:
    return _git(folder, "log", "-1", "--format=%s", "main")


with description("the saves of a repository's session folders on main"):
    with before.each:
        top = _REPOSITORIES.copy()
        self.clone, self.origin = top / "clone", top / "origin.git"
        self.folder = self.clone / ".sessions"
        (self.folder / "checkout-flow").mkdir(parents=True)
        (self.folder / "checkout-flow" / "session.json").write_text('{"stage": "Specification"}\n', encoding="utf-8")
        # Every example queues its changes before the save settles, so a short settle commits them together all the same.
        self.saves = SessionSaves(Repo(self.clone), self.folder, settle_seconds=_SETTLE_SECONDS)

    with after.each:
        shutil.rmtree(self.clone.parent, ignore_errors=True)

    with context("that a ticket's change is queued"):
        with before.each:
            self.saves.later("sessions: checkout-flow move Specification")

        with it("should be committed on main"):
            expect(_until(lambda: _subject(self.clone) == "sessions: checkout-flow move Specification")).to(equal(True))

        with it("should be pushed to origin"):
            expect(_until(lambda: _subject(self.origin) == "sessions: checkout-flow move Specification")).to(equal(True))

    with context("that is queued beside a session's progress cache"):
        with before.each:
            (self.folder / "checkout-flow" / "progress-cache.json").write_text("{}\n", encoding="utf-8")
            self.saves.later("sessions: checkout-flow move Specification")
            _until(lambda: _subject(self.clone) == "sessions: checkout-flow move Specification")

        with it("should leave the cache out of the commit, in a project whose own .gitignore does not name it"):
            expect(_git(self.clone, "ls-files", ".sessions").splitlines()).to(equal([".sessions/.gitignore", ".sessions/checkout-flow/session.json"]))

    with context("that origin refuses the push"):
        with before.each:
            _git(self.clone, "remote", "set-url", "origin", str(self.clone.parent / "missing.git"))
            self.saves.later("sessions: checkout-flow move Specification")

        with it("should keep the failure, naming the change not saved"):
            _until(lambda: self.saves.failure is not None)
            expect(self.saves.failure.changes).to(equal(["sessions: checkout-flow move Specification"]))

        with context("that is saved again once origin answers"):
            with before.each:
                _until(lambda: self.saves.failure is not None)
                _git(self.clone, "remote", "set-url", "origin", str(self.origin))
                self.saves.retry()

            with it("should push the change"):
                expect(_until(lambda: _subject(self.origin) == "sessions: checkout-flow move Specification")).to(equal(True))

            with it("should clear the failure"):
                expect(_until(lambda: self.saves.failure is None)).to(equal(True))

    with context("that work needs main saved before it goes on"):
        with it("should be committed before the save returns"):
            self.saves.now("sessions: open checkout-flow")
            expect(_subject(self.clone)).to(equal("sessions: open checkout-flow"))

        with it("should raise git's refusal to the caller"):
            _git(self.clone, "remote", "set-url", "origin", str(self.clone.parent / "missing.git"))
            expect(lambda: self.saves.now("sessions: open checkout-flow")).to(raise_error(RepoConnectError, contain("Cannot connect git")))
