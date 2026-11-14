"""BDD development — what a session reads from its files is read once for each answer."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import after, before, context, description, it

from space.session import Sessions
from space.session.throwaway_project import SpecRunHome


def _written_by_another_process(session, **fields) -> None:
    """Write session's session.json behind its back, as another process would."""
    held = json.loads(session.session_file.read_text(encoding="utf-8"))
    session.session_file.write_text(json.dumps({**held, **fields}), encoding="utf-8")


with description("a session's reads"):
    with before.each:
        SpecRunHome.ensure()
        self.repo = Path(tempfile.mkdtemp())
        Sessions(self.repo).create("alpha", title="First title")

    with after.each:
        shutil.rmtree(self.repo, ignore_errors=True)

    with context("that the process serves calls from"):
        with before.each:
            self.session = Sessions.of_project(self.repo).named("alpha")
            expect(self.session.title).to(equal("First title"))

        with it("should answer what it read for the rest of the answer"):
            _written_by_another_process(self.session, title="A much longer second title")
            expect(self.session.title).to(equal("First title"))

        with it("should read what another process wrote in the next answer"):
            _written_by_another_process(self.session, title="A much longer second title")
            expect(Sessions.of_project(self.repo).named("alpha").title).to(equal("A much longer second title"))

        with it("should read its own write at once"):
            self.session.save_fields(title="Its own title")
            expect(self.session.title).to(equal("Its own title"))

        with it("should keep what another process wrote when it writes"):
            _written_by_another_process(self.session, scope="story")
            self.session.save_fields(title="Its own title")
            expect(self.session.scope).to(equal("story"))

    with context("that the process serves no calls from"):
        with before.each:
            self.session = Sessions(self.repo).named("alpha")
            expect(self.session.title).to(equal("First title"))

        with it("should read what another process wrote at once"):
            _written_by_another_process(self.session, title="A much longer second title")
            expect(self.session.title).to(equal("A much longer second title"))
