"""BDD spec — Rule and RulesCollection validate."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import before, context, description, it

from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
)


with description("a shared rules section containing scanner bullets") as self:
    with before.each:
        self.guidance = SamplePracticeGuidance(format="markdown")

    with context("with the rules property read"):
        with it("should parse bullets into a rules collection"):
            expect("sample-rule-one" in self.guidance.rules.entries).to(equal(True))

        with it("should expose appliesTo from the rules yaml fence"):
            expect(self.guidance.rules.appliesTo.always_apply).to(equal(False))
            expect(self.guidance.rules.appliesTo.globs).to(contain("**/*sample*"))

        with it("should expose slug, body, optional fidelity, and zero or one scanner on each rule"):
            rule = self.guidance.rules.entries["sample-rule-one"]
            expect(rule.slug).to(equal("sample-rule-one"))
            expect(rule.body).to(contain("sample rule one"))
            expect(rule.scanner is not None).to(equal(True))

    with context("with validate read on one rule"):
        with it("should return instructions to evaluate the current context against that rule"):
            rule = self.guidance.rules.entries["sample-rule-one"]
            expect(rule.validate()).to(contain("Evaluate the current context"))

        with it("should tell the agent to run the scanner when the rule has one"):
            rule = self.guidance.rules.entries["sample-rule-one"]
            expect(rule.validate()).to(contain("Run the scanner"))

    with context("with validate read on the rules collection"):
        with it("should return every child rule's validate instructions in one shot"):
            text = self.guidance.rules.validate()
            expect(text).to(contain("sample-rule-one"))
