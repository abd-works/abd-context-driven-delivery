"""BDD spec - a JavaScript story-spec Story Map renders runnable GWT stories."""

import re
import sys
from pathlib import Path

from expects import be_true, contain, equal, expect, have_len, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from practices.stories.model.code_story_model import CodeStoryMapError
from practices.stories.model.javascript.javascript_story_model import JavaScriptStoryMap
from practices.stories.model.story_model import Epic, Story, StoryType, Epic
from practices.stories.model.story_model import StepType, Scenario, Step
from practices.stories.model.story_model import StoryMap


def _make_scenario(name: str, order: int, given_text: str = "a context") -> Scenario:
    sc = Scenario(name=name, sequential_order=order)
    sc.steps = [
        Step(given_text, StepType.GIVEN, 1),
        Step("the action occurs", StepType.WHEN, 2),
        Step("the outcome is observed", StepType.THEN, 3),
    ]
    return sc


def _story_map_with_stories() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = Epic(f"Epic 1.{j}", j)
        story = Story("Redeem a voucher", 1, StoryType.USER)
        story.actors = ["shopper"]
        story.scenarios.append(
            _make_scenario("Voucher is active", 1, "an active voucher exists")
        )
        story.scenarios.append(
            _make_scenario("Paid order is placed", 2, "a paid order is placed")
        )
        sub.stories.append(story)
        first.epics.append(sub)
    return story_map


with description("a JavaScript story-spec Story Map") as self:
    with before.each:
        self.js = JavaScriptStoryMap()

    with context(
        "that holds a rendered code Story Map with 4 Epics and 3 Epics under the first Epic"
    ):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.tree = self.js.render(self.canonical)
            self.leaf_paths = self.js.leaf_files_of(self.tree)
            self.leaf_contents = [self.tree[p] for p in self.leaf_paths]

        with context("every leaf file"):
            with it("should be named `<sub_epic_snake>_story.test.js` in the parent epic folder"):
                for path in self.leaf_paths:
                    expect(path.endswith("_story.test.js")).to(be_true)
                    expect("/epic-1/epic_1_" in path).to(be_true)
                    expect("/redeem-a-voucher/" in path).to(equal(False))

            with it("should import story-test"):
                for content in self.leaf_contents:
                    expect(content).to(contain("story-test.js"))

            with it("should balance braces and brackets"):
                for content in self.leaf_contents:
                    expect(content.count("{")).to(equal(content.count("}")))
                    expect(content.count("[")).to(equal(content.count("]")))

        with context("every Story file"):
            with it("should register story and scenarios"):
                for content in self.leaf_contents:
                    expect(content).to(contain("story('Redeem a voucher'"))
                    expect(content).to(contain("scenario('Voucher is active'"))
                    expect(content).to(contain("scenario('Paid order is placed'"))

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.parsed = self.js.parse(self.js.render(self.canonical))

        with it("should preserve Story and Scenario counts under each Epic"):
            first_sub = self.parsed.epics[0].epics[0]
            expect(first_sub.stories).to(have_len(1))
            expect(first_sub.stories[0].scenarios).to(have_len(2))

        with it("should restore the Story name and actor"):
            story = self.parsed.epics[0].epics[0].stories[0]
            expect(story.name).to(equal("Redeem a voucher"))
            expect(story.actors).to(equal(["shopper"]))

    with context("that is not a valid JavaScript story-spec tree"):
        with it("should reject parse"):
            expect(lambda: self.js.parse("not a tree")).to(raise_error(CodeStoryMapError))

    with context("for explore/spec story files"):
        with before.each:
            story_map = _story_map_with_stories()
            self.tree = self.js.render(story_map)
            leaf = [c for p, c in self.tree.items() if p.endswith("_story.test.js")]
            self.spec = leaf[0]

        with it("should not emit inventable examples tables on scenarios"):
            expect("examples: [" in self.spec).to(equal(False))
