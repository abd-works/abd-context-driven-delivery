"""BDD spec for a session's debug instructions, the chat bar's debug button and Fix: Session.debug_session (session.py)."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import before, description, it

from harness.agent_tools.agent_tools import AgentToolSet, SubAgentAnnotation
from space.session.session import Session


# (E) Steer Sessions
# (S) Person --> Debug A Failure From Chat Bar
with description("a session's debug instructions, which the chat bar's debug button and Fix start"):
    with before.all:
        self.tool = AgentToolSet.instantiate(Session).tools["debug_session"]
        self.prompt = "\n".join(self.tool.prompt)

    with it("should be offered as instructions"):
        expect(self.tool.kind).to(equal("instructions"))

    with it("should run in the chat itself, which can ask the person, not on a sub-agent"):
        expect(SubAgentAnnotation.annotates(self.tool.callable)).to(equal(False))

    with it("should capture the server's health and the session's log first"):
        expect(self.prompt).to(contain("server-health.report"))

    with it("should write what it captured to a debug report in the session's folder"):
        expect(self.prompt).to(contain("session.write_file"))

    with it("should ask the person for more detail and whether to fix the bug or request help"):
        expect(self.prompt).to(contain("AskUserQuestion"))

    with it("should draft the request for help as an email to the CDD maintainer, for the person to send"):
        expect(self.prompt).to(contain("mailto:jeff.anderson@abdworks.com"))

    with it("should hand a fix to a background sub-agent"):
        expect(self.prompt).to(contain("run_in_background"))

    with it("should push the fix to main where the person can push there"):
        expect(self.prompt).to(contain(".permissions.push"))

    with it("should open a pull request to the CDD repository where the person cannot"):
        expect(self.prompt).to(contain("gh pr create"))
