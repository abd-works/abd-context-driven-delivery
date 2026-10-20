"""Stories scenario rules — shape and and-chaining."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import equal, expect
from mamba import before, context, description, it

from graph import Node, PracticeGraph, Source
from harness.graph.rule_context import RuleCheckContext
from cdd_guidance.practices.stories.rules.scenarios import AndChaining, ScenariosShape


def _scenario(practice, name: str = "Display Create Account") -> Node:
    return Node(
        practice,
        "Scenario",
        f"stories:Scenario:story.ts:{name}",
        name,
        Source("story.ts", 1, 1),
    )


def _step(practice, semantic: str, label: str, line: int) -> Node:
    return Node(
        practice,
        semantic,
        f"stories:{semantic}:story.ts:{line}:{hash(label) & 0xFFFFFF}",
        label,
        Source("story.ts", line, line),
    )


def _record_steps(practice, scenario: Node, steps: list[Node]) -> None:
    fact = {"kind": "steps", "order": 4, "display": "direct"}
    for step in steps:
        practice.record(fact, scenario, step)


with description("ScenariosShape"):
    with context("with When and Then only"):
        with before.each:
            self.practice = PracticeGraph("stories")
            self.scenario = _scenario(self.practice)
            when = _step(self.practice, "When", "when the User proceeds", 1)
            then = _step(self.practice, "Then", "then the User can enter account credentials", 2)
            _record_steps(self.practice, self.scenario, [when, then])
            self.context = RuleCheckContext(self.practice, None)

        with it("should not require Given"):
            expect(ScenariosShape().check(self.scenario, self.context)).to(equal([]))

    with context("with a second When before Then"):
        with before.each:
            self.practice = PracticeGraph("stories")
            self.scenario = _scenario(self.practice)
            steps = [
                _step(self.practice, "When", "when first", 1),
                _step(self.practice, "When", "when second", 2),
                _step(self.practice, "Then", "then outcome", 3),
            ]
            _record_steps(self.practice, self.scenario, steps)
            self.context = RuleCheckContext(self.practice, None)

        with it("should flag and-chaining"):
            hits = AndChaining().check(self.scenario, self.context)
            expect(len(hits)).to(equal(1))

    with context("with When then When then"):
        with before.each:
            self.practice = PracticeGraph("stories")
            self.scenario = _scenario(self.practice)
            steps = [
                _step(self.practice, "When", "when first", 1),
                _step(self.practice, "Then", "then first", 2),
                _step(self.practice, "When", "when second", 3),
                _step(self.practice, "Then", "then second", 4),
            ]
            _record_steps(self.practice, self.scenario, steps)
            self.context = RuleCheckContext(self.practice, None)

        with it("should allow a second interaction after Then"):
            expect(AndChaining().check(self.scenario, self.context)).to(equal([]))
