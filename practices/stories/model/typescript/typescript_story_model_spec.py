"""BDD spec - TypeScript runnable-story Story Map."""

import sys
from pathlib import Path

from expects import be_true, contain, equal, expect, have_len, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from practices.stories.model.code_story_model import CodeStoryModelError
from practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel
from practices.stories.model.story_model import Epic, Story, StoryType, Epic
from practices.stories.model.story_model import StepType, Scenario, Step
from practices.stories.model.story_model import StoryModel


def _make_scenario(name: str, order: int) -> Scenario:
    sc = Scenario(name=name, sequential_order=order)
    sc.steps = [
        Step("a context", StepType.GIVEN, 1),
        Step("the action occurs", StepType.WHEN, 2),
        Step("the outcome is observed", StepType.THEN, 3),
    ]
    return sc


def _story_map_with_stories() -> StoryModel:
    story_map = StoryModel()
    for i in range(1, 5):
        story_map.append_epic(Epic(f"Epic {i}", i))
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = Epic(f"Epic 1.{j}", j)
        story = Story("Redeem a voucher", 1, StoryType.USER)
        story.actors = ["shopper"]
        story.scenarios.append(_make_scenario("Voucher is active", 1))
        sub.stories.append(story)
        first.epics.append(sub)
    return story_map


with description("a TypeScript runnable-story Story Map") as self:
    with before.each:
        self.ts = TypeScriptStoryModel()

    with context("that holds rendered stories"):
        with before.each:
            self.tree = self.ts.render(_story_map_with_stories())
            self.leaf_paths = self.ts.leaf_files_of(self.tree)

        with it("should emit one `{sub_epic_snake}_story.test.ts` in the parent epic folder"):
            for path in self.leaf_paths:
                expect(path.endswith("_story.test.ts")).to(be_true)
                expect("/epic-1/epic_1_" in path).to(be_true)
                expect("/redeem-a-voucher/" in path).to(equal(False))

        with it("should include givens.ts at epic and sub-epic"):
            expect(any(p.endswith("/givens.ts") for p in self.tree)).to(be_true)

        with it("should contain story() call directly"):
            for path in self.leaf_paths:
                expect(self.tree[path]).to(contain("story('Redeem a voucher', () => {"))

        with it("should include examples/ at epic and sub-epic"):
            expect(any("/examples/" in p for p in self.tree)).to(be_true)

        with it("should include story-test shared helper"):
            expect("tests/story-test.ts" in self.tree).to(be_true)

        with it("should default output under tests/"):
            expect(self.ts.tests_root).to(equal("tests"))
            expect(any(p.startswith("tests/") for p in self.tree)).to(be_true)

        with it("should import story-test from the workspace deploy root"):
            leaf = next(p for p in self.leaf_paths)
            expect(self.tree[leaf]).to(contain('from "tests/story-test"'))

    with context("that overrides the deploy root"):
        with before.each:
            self.custom_root = "stories/create-customer"
            self.ts = TypeScriptStoryModel(tests_root=self.custom_root)
            self.tree = self.ts.render(_story_map_with_stories())

        with it("should place story-test at the stories workspace root"):
            expect("stories/story-test.ts" in self.tree).to(be_true)

        with it("should emit story files under the custom root"):
            expect(
                any(
                    p.startswith(f"{self.custom_root}/")
                    and p.endswith("_story.test.ts")
                    for p in self.tree
                )
            ).to(be_true)

        with it("should import story-test from the stories workspace root"):
            leaf = next(p for p in self.tree if p.endswith("_story.test.ts"))
            expect(self.tree[leaf]).to(contain('from "stories/story-test"'))

    with context("a scenario with two Then outcomes"):
        with it("should chain the second outcome with .and()"):
            story = Story("Select Plan", 1, StoryType.USER)
            sc = Scenario(name="catalog listed", sequential_order=1)
            sc.steps = [
                Step("plans exist", StepType.GIVEN, 1),
                Step("they view the catalog", StepType.WHEN, 2),
                Step("names are shown", StepType.THEN, 3),
                Step("prices are shown", StepType.THEN, 4),
            ]
            story.scenarios.append(sc)
            from practices.stories.model.typescript.story_file import render_story_file

            src = render_story_file(story)
            expect(".and(" in src).to(be_true)
            expect(src.count("then(")).to(equal(1))

    with context("round-trip"):
        with before.each:
            self.parsed = self.ts.parse(self.ts.render(_story_map_with_stories()))

        with it("should preserve story and scenario"):
            story = self.parsed.epics[0].epics[0].stories[0]
            expect(story.name).to(equal("Redeem a voucher"))
            expect(story.scenarios).to(have_len(1))

    with context("invalid parse input"):
        with it("should reject"):
            expect(lambda: self.ts.parse("not a tree")).to(raise_error(CodeStoryModelError))
