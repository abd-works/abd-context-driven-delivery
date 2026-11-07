"""BDD spec for Improvement — /repair inlines the manual diagnose recipe."""

import inspect
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.markdown import Markdown
from cdd_guidance.actions.improvement.improvement import Improvement
from harness.agent_tools.agent_tools import AgentToolSet
from space.session.throwaway_project import ThrowawayProject

_IMPROVEMENT = "cdd_guidance.actions.improvement.improvement:Improvement"


def _section(name: str) -> str:
    return Markdown.from_label(Improvement(), name).extract()


with description("Improvement repair recipe"):
    with it("should document diagnose then the proposed toolset change before any test"):
        content = _section("repair")
        expect("proposed toolset change" in content).to(be_true)
        expect("Diagnose" in content).to(be_true)
        expect("tactical file fixes" in content or "tactical diffs" in content).to(
            be_true
        )

    with context("that is expanded for repair"):
        with before.all:
            cls = type(AgentToolSet.instantiate(_IMPROVEMENT))
            self.action = cls()
            self.response = self.action.instructions["repair"].expand(
                {
                    "guidance": [],
                    "asset": "cdd_guidance/practices/base/base_context_tool.md",
                    "violation": "generate swallowed a whole model in one turn",
                },
            )

        with it("should inline the repair.md recipe"):
            expect(_section("repair") in self.response.instructions).to(be_true)

        with it("should require a proposed toolset change before any test"):
            expect("proposed toolset change" in self.response.instructions).to(be_true)

        with it("should tell the agent not to list tactical diffs"):
            expect("tactical diffs" in self.response.instructions).to(be_true)

        with it("should keep the turn open until after fail-first"):
            expect(
                "leave the turn open" in self.response.instructions.lower()
            ).to(be_true)
            expect("finish_turn" in inspect.getsource(type(self.action).repair)).to(
                equal(False)
            )


with description("an improvement action in a project being worked on"):
    with before.each:
        self.project = ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("that repairs a listed practice"):
        with before.each:
            Improvement().repair("stories-story-map")

        with it("should log the repair in the session's log"):
            log = self.project.root / ".sessions" / "main" / "session.log"
            expect(log.read_text(encoding="utf-8")).to(contain(" repair "))

    with context("that verifies the fix of a repair theme"):
        with it("should ask for that theme's fail-first test and original scenarios to be re-run"):
            reply = Improvement().verify_fix("stories-story-map", "generate does not cover the sketch")
            expect(reply).to(contain("Re-check the repair theme generate does not cover the sketch"))
