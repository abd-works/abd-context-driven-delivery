"""BDD spec — Validate action."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, expect
from mamba import before, context, description, it

from harness.agent_tools.agent_tools import AgentInstructions
from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
)
from validate.validate import Validate


def _expanded_validate(action, arguments):
    return AgentInstructions.for_callable(Validate.validate, action).expand(
        {}, arguments
    ).instructions


with description("a validate action on practice guidance") as self:
    with before.each:
        self.guidance = SamplePracticeGuidance(format="markdown")
        self.action = Validate()

    with context("with no rule passed"):
        with it("should return validate instructions for every rule in one shot"):
            prose = _expanded_validate(
                self.action, {"guidance": [self.guidance]}
            )
            expect(prose).to(contain("sample-rule-one"))

    with context("with one rule passed"):
        with it("should return validate instructions for that rule only"):
            rule = self.guidance.rules.entries["sample-rule-one"]
            prose = _expanded_validate(
                self.action, {"guidance": [self.guidance], "rule": rule}
            )
            expect(prose).to(contain("sample-rule-one"))
