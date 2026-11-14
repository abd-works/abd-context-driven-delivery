"""BDD spec — Validate calls answering chats at once. Heavy: each call builds its graph in a worker process."""
import sys
import threading
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.agent_tools.tool_call import ToolCall
from space.session.throwaway_project import ThrowawayProject
from cdd_guidance.actions.validate.validate import Validate
from cdd_guidance.actions.validate.validate_examples import ENTITY_ROOT_FILE, SPEC_FILE, SampleWorkingCopy
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue


with description("a validate action on edited files of a working copy that every graph practice reads") as self:
    # Two chats' validates refresh the one graph their session holds; neither may see the other's refresh half done.
    with context("that two calls answering chats check at once"):
        with before.each:
            self.project = ThrowawayProject()
            session = SampleWorkingCopy(self.project).action.session
            self.reports: dict[str, str] = {}
            self.failures: list[BaseException] = []

            def check(guidance: str, path: str) -> None:
                try:
                    action = Validate(session=session, call=ToolCall(answers_a_chat=True))
                    self.reports[guidance] = action.validate(guidance=[guidance], paths=[path])
                except BaseException as failure:
                    self.failures.append(failure)

            checks = [threading.Thread(target=check, args=pair) for pair in (("ddd-tactics", ENTITY_ROOT_FILE), ("bdd-development", SPEC_FILE))]
            for running in checks:
                running.start()
            for running in checks:
                running.join()

        with after.each:
            self.project.close()

        with it("should report to each call the violations of the file it checks"):
            expect(self.failures).to(equal([]))
            expect(self.reports["ddd-tactics"]).to(contain("private-method-naming"))
            expect(self.reports["bdd-development"]).to(contain("observable-behavior"))
