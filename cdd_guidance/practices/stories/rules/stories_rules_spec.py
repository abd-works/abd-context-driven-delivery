"""Stories scenario rules — shape and and-chaining."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import before, context, description, it

from harness.graph.edge import EdgeType
from harness.graph.graph import Graph, Node, Source
from harness.graph.rule_context import RuleCheckContext
from harness.graph.rule_fixture import SchemaRuleRun
from cdd_guidance.practices.stories.model.story_model import Step, StepType
from cdd_guidance.practices.stories.rules.scenarios import AndChaining, ScenariosShape


def _scenario(practice, name: str = "Display Create Account") -> Node:
    """A scenario the practice holds, as a read holds it, so the graph's check reaches it."""
    scenario = Node(practice, "Scenario", f"stories:Scenario:story.ts:{name}", name, Source("story.ts", 1, 1))
    practice.in_graph.hold(scenario)
    return scenario


def _step(practice, semantic: str, text: str, line: int) -> Node:
    """The Step its story model read, as its own node: ``When`` with ``the User proceeds``."""
    label = f"{semantic.lower()} {text}"
    step = Step(text, StepType(semantic.lower()), line, keyword=semantic)
    step.name = label
    step.type = semantic
    return practice.in_graph.add(step, f"stories:{semantic}:story.ts:{line}:{hash(label) & 0xFFFFFF}", "story.ts", line, line)


def _record_steps(practice, scenario: Node, steps: list[Node]) -> None:
    edge_type = EdgeType("steps", 4, "direct")
    for step in steps:
        practice.graph.record(edge_type, scenario, step)


with description("ScenariosShape"):
    with context("with When and Then only"):
        with before.each:
            self.practice = Graph().practice("stories")
            self.scenario = _scenario(self.practice)
            when = _step(self.practice, "When", "the User proceeds", 1)
            then = _step(self.practice, "Then", "the User can enter account credentials", 2)
            _record_steps(self.practice, self.scenario, [when, then])
            self.context = RuleCheckContext(self.practice, None)

        with it("should not require Given"):
            expect(SchemaRuleRun(ScenariosShape(), self.context).node_hits(self.scenario)).to(equal([]))

    with context("with a second When before Then"):
        with before.each:
            self.practice = Graph().practice("stories")
            self.scenario = _scenario(self.practice)
            steps = [
                _step(self.practice, "When", "first", 1),
                _step(self.practice, "When", "second", 2),
                _step(self.practice, "Then", "outcome", 3),
            ]
            _record_steps(self.practice, self.scenario, steps)
            self.context = RuleCheckContext(self.practice, None)

        with it("should flag and-chaining"):
            hits = SchemaRuleRun(AndChaining(), self.context).node_hits(self.scenario)
            expect(len(hits)).to(equal(1))

    with context("with When then When then"):
        with before.each:
            self.practice = Graph().practice("stories")
            self.scenario = _scenario(self.practice)
            steps = [
                _step(self.practice, "When", "first", 1),
                _step(self.practice, "Then", "first", 2),
                _step(self.practice, "When", "second", 3),
                _step(self.practice, "Then", "second", 4),
            ]
            _record_steps(self.practice, self.scenario, steps)
            self.context = RuleCheckContext(self.practice, None)

        with it("should allow a second interaction after Then"):
            expect(SchemaRuleRun(AndChaining(), self.context).node_hits(self.scenario)).to(equal([]))


with description("ExamplesTraceDomainModel concepts"):
    with it("should not count the actor a step names as a domain concept"):
        from cdd_guidance.practices.stories.model.story_model import Step, StepType
        from cdd_guidance.practices.stories.rules.scenarios import scenario_domain_concepts

        steps = [
            Step("**My Paradise** provides the device wallet merchant certificate", StepType.WHEN, 1,
                 concepts=["My Paradise"], actor="My Paradise"),
            Step("**Customer** sees the **certificate** My Paradise returned", StepType.THEN, 2,
                 concepts=["Customer", "certificate"], actor="Customer"),
        ]
        expect(scenario_domain_concepts(steps)).to(equal({"certificate"}))
