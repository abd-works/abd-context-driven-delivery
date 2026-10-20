"""BDD spec — Generate runs validate, including the active fidelity's rules."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import before, context, description, it

from generate.generate import Generate
from harness.agent_tools.agent_tools import AgentInstructions
from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
)


def _expanded_generate(action, arguments):
    return AgentInstructions.for_callable(Generate.generate, action).expand(
        {}, arguments
    )


with description("a generate action on practice guidance") as self:
    with before.each:
        self.action = Generate()

    with context("with a fidelity active"):
        with it("should include that fidelity's rules in the generate instructions"):
            guidance = SamplePracticeGuidance(format="markdown", fidelity="sketch")
            expanded = _expanded_generate(self.action, {"guidance": [guidance]})
            prose = expanded.instructions
            expect(prose).to(contain("sample-rule-one"))
            expect(prose).to(contain("sketch-rule"))
            expect(prose).not_to(contain("spec-rule"))
            expect(
                prose.index("sketch-rule") < prose.index("call validate with this same guidance")
            ).to(equal(True))

        with it("should list validate as a tool to call after the artifact is written"):
            guidance = SamplePracticeGuidance(format="markdown", fidelity="sketch")
            expanded = _expanded_generate(self.action, {"guidance": [guidance]})
            expect("validate" in expanded.tools).to(equal(True))
            expect(expanded.instructions).to(contain("call validate with this same guidance"))

    with context("with Bdd listed"):
        with it("should run generate using the practice default generate_output"):
            self.action.generate(["bdd"])
