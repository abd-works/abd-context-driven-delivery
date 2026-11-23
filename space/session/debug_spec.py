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
from mamba import before, context, description, it

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

    with it("should ask the person whether to fix the bug or log a defect"):
        expect([option in self.prompt for option in ('"Fix the bug"', '"Log a defect"', "AskUserQuestion")]).to(equal([True, True, True]))

    with it("should always log the defect as an issue on the CDD repository on GitHub, whichever the person chooses"):
        expect(self.prompt).to(contain("Always log the defect"))

    with it("should log the defect with gh issue create, so a person or an agent can fix it from there"):
        expect(self.prompt).to(contain("gh issue create"))

    with it("should no longer email the CDD maintainer"):
        expect(self.prompt).not_to(contain("mailto:"))

    with it("should hand a fix to a background sub-agent"):
        expect(self.prompt).to(contain("run_in_background"))

    with it("should tell the person the fix goes to this branch and is served on the dev lane"):
        expect(self.prompt).to(contain("fixes it on this branch and serves it on the dev lane"))

    with it("should never merge the fix to main"):
        expect(self.prompt).not_to(contain("merge to main"))

    with it("should never push the fix with push_to_main"):
        expect(self.prompt).not_to(contain("push_to_main"))

    with context("with the chat working in a ticket's worktree of the CDD checkout"):
        with it("should fix it in that worktree, on that branch, and push it to the branch"):
            expect(self.prompt).to(contain("work in that worktree on that branch"))

        with it("should serve the fix by repinning the dev lane from the worktree"):
            expect(self.prompt).to(contain("repin the dev lane with `python scripts/install.py --ide Claude --pin-runtime`"))

        with it("should open each app the fix changed"):
            expect(self.prompt).to(contain("app.open"))

    with context("with the chat working in the CDD checkout's main"):
        with it("should push the fix to main and repin the stable lane after messaging its sessions"):
            expect(self.prompt).to(contain("repin the stable lane"))

    with context("with CDD installed in another project"):
        with it("should open a pull request to the CDD repository from a fork"):
            expect(self.prompt).to(contain("gh pr create"))

    with context("with no permission to push to the CDD repository"):
        with it("should open a pull request instead of pushing"):
            expect(self.prompt).to(contain("no permission to push"))

    with context("with the fix pushed or its pull request opened"):
        with it("should link the fix in the defect's issue"):
            expect(self.prompt).to(contain("gh issue comment"))
