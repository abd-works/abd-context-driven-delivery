"""Scenario counts are not a 4–9 map band. A story holds 1–4 scenarios."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect
from mamba import context, description, it

from cdd_guidance.practices.stories.model.story_model import Scenario, Story
from cdd_guidance.practices.stories.rules.story_map import FourToNineChildren, StoryScenariosAtMostSeven
from harness.graph.graph import Graph, Node, Source
from harness.graph.rule_context import RuleCheckContext
from harness.graph.rule_fixture import SchemaRuleRun
from harness.graph.schema_rules import PracticeSchema
from harness.guidance.practice_catalogue import PracticeCatalogue


def _Node(name: str, node_type: str, facts: dict) -> Node:
    """A stories graph node carrying the given facts, held by its practice as a read holds it."""
    node = Node(Graph().practice("stories"), node_type, f"stories:{node_type}:{name}", name, Source(".", 1, 1))
    for key, value in facts.items():
        node.set_fact(key, value)
    node.practice.reading.in_graph.hold(node)
    return node


def _hits(rule, node: Node) -> list[str]:
    """What the rule reports on node where validate runs it: only when the schema gives node's type the rule."""
    return SchemaRuleRun(rule, RuleCheckContext(node.practice, None)).node_hits(node)


def _story_node(name: str, scenario_count: int, *, band: str = "") -> Node:
    return _Node(
        name,
        "Story",
        {
            "scenario_count": scenario_count,
            "child_count": scenario_count,
            "child_label": "scenarios",
            "child_band": band,
        },
    )


with description("story scenario count"):
    with context("four-to-nine-children"):
        with it("should leave a story with two scenarios alone"):
            node = _story_node("Enter Validation Code", 2, band="error")
            expect(_hits(FourToNineChildren(), node)).to(equal([]))

        with it("should leave a scenario's step count alone"):
            node = _Node("Enter validation code", "Scenario", {"child_count": 2, "child_label": "steps", "child_band": "error"})
            expect(_hits(FourToNineChildren(), node)).to(equal([]))

        with it("should still flag an epic outside 4-9 children"):
            node = _Node("Onboard A Customer", "Epic", {"child_count": 1, "child_label": "children", "child_band": "error"})
            expect(_hits(FourToNineChildren(), node)).to(
                equal(["epic 'Onboard A Customer': 1 children (target 4-9)"])
            )

    with context("story-scenarios-at-most-seven"):
        with it("should accept one to seven scenarios"):
            rule = StoryScenariosAtMostSeven()
            for count in (1, 4, 7):
                expect(_hits(rule, _story_node("Enter Validation Code", count))).to(equal([]))

        with it("should call a story with more than seven scenarios huge"):
            hits = _hits(StoryScenariosAtMostSeven(), _story_node("Pick Number", 8))
            expect(hits).to(equal(["story 'Pick Number': 8 scenarios — story is huge (target 1-7)"]))

        with it("should accept a story with no scenarios, whose scenarios are not written yet"):
            expect(_hits(StoryScenariosAtMostSeven(), _story_node("Enter Validation Code", 0))).to(equal([]))

    with context("a story that records its scenario count"):
        with it("should not mark two scenarios as a 4-9 child-band error"):
            story = Story("Enter Validation Code", 1)
            story.scenarios = [Scenario("Enter validation code", 1), Scenario("Resend validation code", 2)]
            story.load_map_facts()
            expect(story.scenario_count).to(equal(2))
            expect(story.child_band).to(equal(""))

    with context("schema"):
        with it("should size story scenarios with the at-most-seven rule"):
            expect(PracticeSchema(PracticeCatalogue.create("stories")).slugs_for("Story")).to(contain("story-scenarios-at-most-seven"))
            expect("four-to-nine-children" in PracticeSchema(PracticeCatalogue.create("stories")).slugs_for("Story")).to(equal(False))

        with it("should keep four-to-nine on an epic"):
            expect(PracticeSchema(PracticeCatalogue.create("stories")).slugs_for("Epic")).to(contain("four-to-nine-children"))
