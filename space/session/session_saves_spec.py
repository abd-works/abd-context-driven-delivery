"""The saves that keep every ticket's record on main: queued, made on their own thread, and shown when git refuses."""

import shutil
import sys
import tempfile
import time
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.process.git import RepoConnectError
from space.repo.mock_repo import MockGit, MockRepo
from space.session.session_saves import SessionSaves

_WAIT_SECONDS = 20
# No settle: every example queues its one change before it waits, so nothing is left to gather into the commit.
_SETTLE_SECONDS = 0


def _until(condition, poll: float = 0.01) -> bool:
    deadline = time.monotonic() + _WAIT_SECONDS
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(poll)
    return False


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

