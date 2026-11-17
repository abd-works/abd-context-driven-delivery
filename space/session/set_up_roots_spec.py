"""BDD spec for a session's instructions to set up its roots: Session.set_up_roots (session.py)."""

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


# (E) Guide Work Through Practices On Board
# (S) Person --> Choose Session And Practice Roots
with description("a session's instructions to set up its roots, which switching to a session with unchecked roots points to"):
    with before.all:
        self.tool = AgentToolSet.instantiate(Session).tools["set_up_roots"]
        self.prompt = "\n".join(self.tool.prompt)

    with it("should be offered as instructions"):
        expect(self.tool.kind).to(equal("instructions"))

    with it("should run in the chat itself, which can ask the person, not on a sub-agent"):
        expect(SubAgentAnnotation.annotates(self.tool.callable)).to(equal(False))

    with it("should start from what the ticket names and the story map nodes it names"):
        expect(self.prompt).to(contain("story map nodes"))

    with it("should take the branch's changed files as evidence"):
        expect(self.prompt).to(contain("git diff --name-only"))

    with it("should read where each practice the session has on writes from its own declared outputs"):
        expect(self.prompt).to(contain("the `outputs` each fidelity declares"))

    with it("should ask each fidelity for the folders it proposes"):
        expect(self.prompt).to(contain("fidelity-session-output.propose_roots"))

    with it("should dig down to the narrowest folder that holds each piece"):
        expect(self.prompt).to(contain("narrowest folder that holds the piece"))

    with it("should confirm the proposed roots with the person before setting any"):
        expect(self.prompt).to(contain("set nothing before they answer"))

    with it("should set a fidelity's further folders beside its first with add_root"):
        expect(self.prompt).to(contain("fidelity-session-output.add_root"))

    with it("should set a practice's own root with practice-session-output.choose_root"):
        expect(self.prompt).to(contain("practice-session-output.choose_root"))

    with it("should name no practice of its own, leaving each practice to declare where it writes"):
        expect(self.prompt).not_to(contain("story_tests"))
