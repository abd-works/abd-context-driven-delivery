"""Scenario counts are not a 4–9 map band. A story holds 1–4 scenarios."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from expects import contain, equal, expect
from mamba import context, description, it

from cdd_guidance.practices.stories.model.story_model import Scenario, Story
from cdd_guidance.practices.stories.rules.story_map import FourToNineChildren, StoryScenariosOneToFour
from harness.graph.schema_rules import slugs_for_type


class _Node:
    def __init__(self, name: str, node_type: str, data: dict):
        self.name = name
        self.type = node_type
        self.data = data


def _story_node(name: str, scenario_count: int, *, band: str = "") -> _Node:
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
            expect(FourToNineChildren().check(node, None)).to(equal([]))

        with it("should leave a scenario's step count alone"):
            node = _Node("Enter validation code", "Scenario", {"child_count": 2, "child_label": "steps", "child_band": "error"})
            expect(FourToNineChildren().check(node, None)).to(equal([]))

        with it("should still flag an epic outside 4-9 children"):
            node = _Node("Onboard A Customer", "Epic", {"child_count": 1, "child_label": "children", "child_band": "error"})
            expect(FourToNineChildren().check(node, None)).to(
                equal(["epic 'Onboard A Customer': 1 children (target 4-9)"])
            )

    with context("story-scenarios-one-to-four"):
        with it("should accept one to four scenarios"):
            rule = StoryScenariosOneToFour()
            for count in (1, 2, 4):
                expect(rule.check(_story_node("Enter Validation Code", count), None)).to(equal([]))

        with it("should call a story with more than four scenarios huge"):
            hits = StoryScenariosOneToFour().check(_story_node("Create Account", 5), None)
            expect(hits).to(equal(["story 'Create Account': 5 scenarios — story is huge (target 1-4)"]))

        with it("should flag a story with no scenarios"):
            hits = StoryScenariosOneToFour().check(_story_node("Enter Validation Code", 0), None)
            expect(hits).to(equal(["story 'Enter Validation Code': 0 scenarios (target 1-4)"]))

    with context("a story that records its scenario count"):
        with it("should not mark two scenarios as a 4-9 child-band error"):
            story = Story("Enter Validation Code", 1)
            story.scenarios = [Scenario("Enter validation code", 1), Scenario("Resend validation code", 2)]
            story.load_map_facts()
            expect(story.scenario_count).to(equal(2))
            expect(story.child_band).to(equal(""))

    with context("schema"):
        with it("should size story scenarios with the 1-4 rule"):
            expect(slugs_for_type("stories", "Story")).to(contain("story-scenarios-one-to-four"))
            expect("four-to-nine-children" in slugs_for_type("stories", "Story")).to(equal(False))

        with it("should keep four-to-nine on an epic"):
            expect(slugs_for_type("stories", "Epic")).to(contain("four-to-nine-children"))
