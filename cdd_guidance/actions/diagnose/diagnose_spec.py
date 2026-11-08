"""BDD spec for cdd_guidance/actions/diagnose/diagnose.py — Diagnose toolset sub-agent dispatch.
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.actions.diagnose.diagnose import Diagnose
from harness.agent_tools.agent_tools import AgentToolSet
from harness.agent_tools.agent_tools import SUB_AGENT_CALLER_PREAMBLE, SubAgentAnnotation
from space.session.throwaway_project import ThrowawayProject


def diagnose_tool():
    return AgentToolSet.instantiate(Diagnose).tools["diagnose"]


with description("Diagnose toolset"):
    with context("with its diagnose tool"):
        with it("exposes diagnose as a sub_agent tool"):
            # Arrange / Act
            tool = diagnose_tool()
            # Assert
            expect(SubAgentAnnotation.annotates(tool.callable)).to(equal(True))

        with it("launches non-blocking"):
            # Arrange / Act
            tool = diagnose_tool()
            # Assert
            expect(tool.description).to(contain(SUB_AGENT_CALLER_PREAMBLE))

    with context("diagnose sub-agent instructions"):
        with it("describes building a feedback loop in Phase 1"):
            # Arrange / Act
            instructions = diagnose_tool().description
            # Assert
            expect(instructions).to(contain("Phase 1"))
            expect(instructions).to(contain("feedback loop"))

        with it("requires reproduction before proceeding in Phase 2"):
            # Arrange / Act
            instructions = diagnose_tool().description
            # Assert
            expect(instructions).to(contain("Phase 2"))
            expect(instructions).to(contain("Reproduce"))

        with it("demands ranked falsifiable hypotheses in Phase 3"):
            # Arrange / Act
            instructions = diagnose_tool().description
            # Assert
            expect(instructions).to(contain("Phase 3"))
            expect(instructions).to(contain("falsifiable"))

        with it("requires targeted instrumentation in Phase 4"):
            # Arrange / Act
            instructions = diagnose_tool().description
            # Assert
            expect(instructions).to(contain("Phase 4"))
            expect(instructions).to(contain("Instrument"))

        with it("mandates regression test before fix in Phase 5"):
            # Arrange / Act
            instructions = diagnose_tool().description
            # Assert
            expect(instructions).to(contain("Phase 5"))
            expect(instructions).to(contain("regression test"))

        with it("requires cleanup and post-mortem in Phase 6"):
            # Arrange / Act
            instructions = diagnose_tool().description
            # Assert
            expect(instructions).to(contain("Phase 6"))
            expect(instructions).to(contain("post-mortem"))


with description("a diagnose action in a project being worked on"):
    with before.each:
        ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with context("that names a practice fidelity"):
        with before.each:
            self.rules = Diagnose().diagnose("stories-story-map")

        with it("should give the practice's shared rules"):
            expect(self.rules).to(contain("`do-not-invent-requirements`"))

        with it("should give that fidelity's own rules"):
            expect(self.rules).to(contain("`verb-noun-format`"))
