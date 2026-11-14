"""The saves that keep every ticket's record on main: queued, made on their own thread, and shown when git refuses."""

import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.process.git import RepoConnectError
from space.repo.built_once import BuiltOnce
from space.repo.mock_repo import MockGit, MockRepo
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


def _until(condition, poll: float = 0.01) -> bool:
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


class _OriginThatMayRefuse(MockRepo):
    """A mocked clone whose origin refuses every push while ``refuses`` is set, as git does when origin is unreachable."""

    refuses = False

    def push_upstream(self) -> None:
        if self.refuses:
            raise RepoConnectError(f"Cannot connect git: git push -u origin main failed in {self.root}: origin does not answer.")
        super().push_upstream()


# What the saves do with a change, on a repository held in memory: no example here depends on what git itself does.
with description("the saves of a repository's session folders on main"):
    with before.each:
        self.clone = Path(tempfile.mkdtemp(prefix="cdd-session-saves-")).resolve()
        (self.clone / "README.md").write_text("project\n", encoding="utf-8")
        self.held = MockGit(self.clone)
        self.held.make_clone()
        self.held.add_origin()
        self.folder = _ticket_folder(self.clone)
        self.repository = _OriginThatMayRefuse(self.clone, self.held)
        self.saves = SessionSaves(self.repository, self.folder, settle_seconds=_SETTLE_SECONDS)

    with after.each:
        shutil.rmtree(self.clone, ignore_errors=True)

    with context("that a ticket's change is queued"):
        with before.each:
            self.saves.later("sessions: checkout-flow move Specification")

        with it("should be committed on main"):
            expect(_until(lambda: self.held.logs["main"][-1] == "sessions: checkout-flow move Specification")).to(equal(True))

    with context("that origin refuses the push"):
        with before.each:
            self.repository.refuses = True
            self.saves.later("sessions: checkout-flow move Specification")

        with it("should keep the failure, naming the change not saved"):
            _until(lambda: self.saves.failure is not None)
            expect(self.saves.failure.changes).to(equal(["sessions: checkout-flow move Specification"]))

        with context("that is saved again once origin answers"):
            with before.each:
                _until(lambda: self.saves.failure is not None)
                self.repository.refuses = False
                self.saves.retry()

            with it("should push the change"):
                expect(_until(lambda: self.held.origin_logs["main"][-1] == "sessions: checkout-flow move Specification")).to(equal(True))

            with it("should clear the failure"):
                expect(_until(lambda: self.saves.failure is None)).to(equal(True))

    with context("that work needs main saved before it goes on"):
        with it("should be committed before the save returns"):
            self.saves.now("sessions: open checkout-flow")
            expect(self.held.logs["main"][-1]).to(equal("sessions: open checkout-flow"))


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
            expect(_until(lambda: _subject(self.origin) == "sessions: checkout-flow move Specification", poll=0.05)).to(equal(True))

    with context("that is queued beside a session's progress cache"):
        with before.each:
            (self.folder / "checkout-flow" / "progress-cache.json").write_text("{}\n", encoding="utf-8")
            self.saves.later("sessions: checkout-flow move Specification")
            _until(lambda: _subject(self.clone) == "sessions: checkout-flow move Specification", poll=0.05)

        with it("should leave the cache out of the commit, in a project whose own .gitignore does not name it"):
            expect(_git(self.clone, "ls-files", ".sessions").splitlines()).to(equal([".sessions/.gitignore", ".sessions/checkout-flow/session.json"]))

    with context("that work needs main saved before it goes on"):
        with it("should raise git's refusal to the caller"):
            _git(self.clone, "remote", "set-url", "origin", str(self.clone.parent / "missing.git"))
            expect(lambda: self.saves.now("sessions: open checkout-flow")).to(raise_error(RepoConnectError, contain("Cannot connect git")))
