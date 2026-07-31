"""BDD spec - a JavaScript story-spec Story Map renders runnable GWT stories."""

import re
import sys
from pathlib import Path

from expects import be_true, contain, equal, expect, have_len, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from context_tools.stories.code.code_story_map import CodeStoryMapError, to_kebab
from context_tools.stories.code.javascript.javascript_story_map import JavaScriptStoryMap
from context_tools.stories.story_model.nodes import Epic, Story, StoryType, SubEpic
from context_tools.stories.story_model.scenario import Clause, Interaction, Phase, Scenario
from context_tools.stories.story_model.story_map import StoryMap


def _make_scenario(name: str, order: int, given_text: str = "a context") -> Scenario:
    sc = Scenario(name=name, sequential_order=order)
    sc.given = [Clause(text=given_text, phase=Phase.GIVEN)]
    sc.interactions = [
        Interaction(
            when=[Clause(text="the action occurs", phase=Phase.WHEN)],
            then=[Clause(text="the outcome is observed", phase=Phase.THEN)],
        )
    ]
    return sc


def _story_map_with_stories() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story("Redeem a voucher", 1, StoryType.USER)
        story.users = ["shopper"]
        story.scenarios.append(
            _make_scenario("Voucher is active", 1, "an active voucher exists")
        )
        story.scenarios.append(
            _make_scenario("Paid order is placed", 2, "a paid order is placed")
        )
        sub.stories.append(story)
        first.sub_epics.append(sub)
    return story_map


with description("a JavaScript story-spec Story Map") as self:
    with before.each:
        self.js = JavaScriptStoryMap()

    with context(
        "that holds a rendered code Story Map with 4 Epics and 3 SubEpics under the first Epic"
    ):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.tree = self.js.render(self.canonical)
            self.leaf_paths = self.js.leaf_files_of(self.tree)
            self.leaf_contents = [self.tree[p] for p in self.leaf_paths]

        with context("every leaf file"):
            with it("should be named `<story_snake>_story.js` under a story folder"):
                for path in self.leaf_paths:
                    expect(path.endswith("_story.js")).to(be_true)
                    expect("/redeem-a-voucher/" in path).to(be_true)

            with it("should import story-test GWT helpers"):
                for content in self.leaf_contents:
                    expect(content).to(contain("story-test.js"))
                    expect(content).to(contain("export function create"))

            with it("should balance braces and brackets"):
                for content in self.leaf_contents:
                    expect(content.count("{")).to(equal(content.count("}")))
                    expect(content.count("[")).to(equal(content.count("]")))

        with context("every Story file"):
            with it("should export createRedeemAVoucherStory(mode)"):
                for content in self.leaf_contents:
                    expect(content).to(contain("export function createRedeemAVoucherStory(mode)"))

            with it("should register story and scenarios with GWT helpers"):
                for content in self.leaf_contents:
                    expect(content).to(contain("story('Redeem a voucher'"))
                    expect(content).to(contain("scenario('Voucher is active'"))
                    expect(content).to(contain("scenario('Paid order is placed'"))

            with it("should wire fake mode when the file is the test entry"):
                for content in self.leaf_contents:
                    expect(content).to(contain('createRedeemAVoucherStory("fake")'))

        with context("every Epic folder"):
            with it("should hold an `<epic-slug>-helper.js` exporting an Epic Helper class"):
                helper_paths = [p for p in self.tree if p.endswith("-helper.js")]
                expect(helper_paths).to(have_len(4))
                for path in helper_paths:
                    expect("export class " in self.tree[path]).to(be_true)
                    expect("Helper {" in self.tree[path]).to(be_true)

    with context("that has been rendered and parsed back without edits"):
        with before.each:
            self.canonical = _story_map_with_stories()
            self.parsed = self.js.parse(self.js.render(self.canonical))

        with it("should preserve Story and Scenario counts under each SubEpic"):
            first_sub = self.parsed.epics[0].sub_epics[0]
            expect(first_sub.stories).to(have_len(1))
            expect(first_sub.stories[0].scenarios).to(have_len(2))

        with it("should restore the Story name and actor"):
            story = self.parsed.epics[0].sub_epics[0].stories[0]
            expect(story.name).to(equal("Redeem a voucher"))
            expect(story.users).to(equal(["shopper"]))

    with context("that is not a valid JavaScript story-spec tree"):
        with it("should reject parse"):
            expect(lambda: self.js.parse("not a tree")).to(raise_error(CodeStoryMapError))

    with context("for an Epic that declares CartExampleFactory"):
        with before.each:
            story_map = _story_map_with_stories()
            story_map.epics[0].example_factories = ["CartExampleFactory"]
            self.tree = self.js.render(story_map)
            helper_paths = [
                p
                for p in self.tree
                if p.endswith("-helper.js") and to_kebab("Epic 1") in p
            ]
            self.helper = self.tree[helper_paths[0]]

        with it("should import CartExampleFactory in the epic helper"):
            expect(self.helper).to(contain("CartExampleFactory"))

        with it("should expose a cartExampleFactory accessor"):
            expect(self.helper).to(contain("cartExampleFactory()"))

    with context("for explore/spec story files"):
        with before.each:
            story_map = _story_map_with_stories()
            self.tree = self.js.render(story_map)
            leaf = [c for p, c in self.tree.items() if p.endswith("_story.js")]
            self.spec = leaf[0]

        with it("should instruct assertions against the public interface"):
            expect(self.spec).to(contain("public interface"))

        with it("should not emit inventable examples tables on scenarios"):
            expect("examples: [" in self.spec).to(equal(False))
