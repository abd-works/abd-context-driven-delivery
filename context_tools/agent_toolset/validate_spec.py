"""BDD spec — Validate action."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, expect
from mamba import before, context, description, it

from context_tools.agent_toolset.validate import Validate
from context_tools.context_guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
)


with description("a validate action on practice guidance") as self:
    with before.each:
        self.host = SamplePracticeGuidance(format="markdown")
        self.action = Validate()

    with context("with no rule passed"):
        with it("should return validate instructions for every rule in one shot"):
            expect(self.action.validate(self.host)).to(contain("sample-rule-one"))

    with context("with one rule passed"):
        with it("should return validate instructions for that rule only"):
            rule = self.host.rules.entries["sample-rule-one"]
            expect(self.action.validate(self.host, rule)).to(contain("sample-rule-one"))
