"""BDD spec — Rule and RulesCollection validate."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
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

        with it("should bind globs from the yaml fence onto glob"):
            expect(self.guidance.rules.glob).to(contain("**/*sample*"))

        with it("should match a path against glob"):
            expect(self.guidance.rules.matches("pkg/foo_sample_bar.py")).to(equal(True))
            expect(self.guidance.rules.matches("pkg/other.py")).to(equal(False))

        with it("should match any file when always_apply and the bag has no glob"):
            from harness.guidance.rule import AppliesTo, RulesCollection

            bag = RulesCollection(applies_to=AppliesTo(always_apply=True))
            expect(bag.matches("pkg/notes.md")).to(equal(True))
            expect(bag.matches("C:/dev/repo/src/app.py")).to(equal(True))

        with it("should not treat a trailing directory ** as every filename"):
            from harness.guidance.rule import AppliesTo, RulesCollection

            bag = RulesCollection(
                applies_to=AppliesTo(globs="**/*agent_spec*,**/.agent_bdd_sessions/**")
            )
            expect(bag.matches("harness/guidance/rule.py")).to(equal(False))
            expect(bag.matches("foo/bar_agent_spec.py")).to(equal(True))

        with it("should not inject AgentBdd rules for a production python file"):
            from practices.agent_bdd.agent_bdd import AgentBdd

            result = AgentBdd().rules.inject_rules(
                {
                    "tool_name": "Write",
                    "tool_input": {"path": "harness/guidance/rule.py"},
                }
            )
            expect(result).to(equal({}))

        with it("should inject rules markdown when the written path matches"):
            result = self.guidance.rules.inject_rules(
                {
                    "tool_name": "Write",
                    "tool_input": {"path": "pkg/foo_sample_bar.py"},
                }
            )
            expect(result.get("additional_context")).to(contain("sample rule one"))

        with it("should inject when the path matches regardless of tool name"):
            result = self.guidance.rules.inject_rules(
                {"tool_input": {"path": "pkg/foo_sample_bar.py"}}
            )
            expect(result.get("additional_context")).to(contain("sample rule one"))

        with it("should inject nothing from a rules collection that has no parent"):
            from harness.guidance.rule import RulesCollection

            result = RulesCollection().inject_rules(
                {
                    "tool_name": "Write",
                    "tool_input": {"path": "actions/validate/validate.py"},
                }
            )
            expect(result).to(equal({}))

        with it("should list inject_rules on the collection tools"):
            expect("inject_rules" in self.guidance.rules.tools).to(equal(True))

        with it("should keep the guidance as parent and each rule's parent as the collection"):
            expect(self.guidance.rules.parent).to(equal(self.guidance))
            for rule in self.guidance.rules:
                expect(rule.parent).to(equal(self.guidance.rules))

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
            text = self.guidance.rules.validate
            expect(text).to(contain("sample-rule-one"))
