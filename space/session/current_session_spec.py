"""The current session, which one cdd server keeps for every project its chats work on."""

import shutil
import sys
import tempfile
import threading
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from space.session import Session
from space.work_state import working_on


def _project() -> Path:
    root = Path(tempfile.mkdtemp(prefix="cdd-current-session-"))
    (root / ".git").mkdir()
    return root.resolve()


with description("the current session"):
    with before.each:
        self.first = _project()
        self.second = _project()
        with working_on(self.first):
            Session.switch("alpha")
        with working_on(self.second):
            Session.switch("beta")

    with after.each:
        shutil.rmtree(self.first, ignore_errors=True)
        shutil.rmtree(self.second, ignore_errors=True)

    with context("that two projects each have a session switched on"):
        with it("should be each project's own session for a call on that project"):
            with working_on(self.first):
                first = Session.current().name
            with working_on(self.second):
                second = Session.current().name
            expect((first, second)).to(equal(("alpha", "beta")))

        with context("with calls on both projects running at the same time"):
            with it("should give each call its own project's session"):
                seen: dict[str, str] = {}
                both_inside = threading.Barrier(2)

                def look(project: Path) -> None:
                    with working_on(project):
                        Session.current()
                        both_inside.wait(timeout=5)
                        seen[project.name] = Session.current().name

                calls = [threading.Thread(target=look, args=(project,)) for project in (self.first, self.second)]
                for call in calls:
                    call.start()
                for call in calls:
                    call.join()
                expect(seen).to(equal({self.first.name: "alpha", self.second.name: "beta"}))
