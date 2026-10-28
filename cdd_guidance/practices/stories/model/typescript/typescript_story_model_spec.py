"""BDD spec - TypeScript runnable-story Story Map."""

import sys
from pathlib import Path

from expects import be_true, contain, equal, expect, have_len, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModelError
from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryType, Epic
from cdd_guidance.practices.stories.model.story_model import StepType, Scenario, Step
from cdd_guidance.practices.stories.model.story_model import StoryModel


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

        with it("should not emit givens.ts — Given steps stay in story tests"):
            expect(any(p.endswith("/givens.ts") for p in self.tree)).to(equal(False))

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

    with context("that names the step library folder"):
        with before.each:
            self.ts = TypeScriptStoryModel(tests_root="tests", story_test_folder="test-utils/story-test")
            self.tree = self.ts.render(_story_map_with_stories())

        with it("should place story-test in the step library folder"):
            expect("test-utils/story-test/story-test.ts" in self.tree).to(be_true)
            expect("tests/story-test.ts" in self.tree).to(equal(False))

        with it("should keep story files under the tests root"):
            leaf = next(p for p in self.tree if p.endswith("_story.test.ts"))
            expect(leaf.startswith("tests/")).to(be_true)

        with it("should import story-test from the step library folder"):
            leaf = next(p for p in self.tree if p.endswith("_story.test.ts"))
            expect(self.tree[leaf]).to(contain('from "test-utils/story-test/story-test"'))

        with it("should still skip story-test when parsing the tree back"):
            parsed = TypeScriptStoryModel("tests").parse(self.tree)
            expect(parsed.epics[0].epics[0].stories[0].name).to(equal("Redeem a voucher"))
            expect(
                TypeScriptStoryModel("tests").leaf_files_of(self.tree)
            ).not_to(contain("test-utils/story-test/story-test.ts"))

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
            from cdd_guidance.practices.stories.model.typescript.story_file import render_story_file

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

    with context("a story file that sits directly in its epic folder"):
        with before.each:
            content = (
                "/**\n * Epic: Access My Paradise\n * Evidence: observed\n */\n\n"
                "import { scenario, shareStory } from 'tests/story-test';\n\n"
                "/**\n * Story: Create Account\n * Actor: Customer\n */\n"
                "shareStory('Create Account', () => {\n"
                "  scenario('Display Create Account', ({ when, then }) => {\n"
                "    when('the User proceeds to create an account', () => {});\n"
                "    then('the User can enter credentials', () => {});\n"
                "  });\n"
                "});\n\n"
                "/**\n * Story: Sign In\n * Actor: Customer\n */\n"
                "shareStory('Sign In', () => {\n"
                "  scenario('Sign in with credentials', ({ when, then }) => {\n"
                "    when('the Customer signs in', () => {});\n"
                "    then('My Paradise opens', () => {});\n"
                "  });\n"
                "});\n"
            )
            path = "tests/access-my-paradise/access_my_paradise.story.shared.ts"
            self.model = TypeScriptStoryModel("tests").load({path: content})

        with it("should keep the epic with its name"):
            expect([epic.name for epic in self.model.epics]).to(equal(["Access My Paradise"]))

        with it("should hold its stories on the epic, not on an invented sub-epic"):
            epic = self.model.epics[0]
            expect([story.name for story in epic.stories]).to(equal(["Create Account", "Sign In"]))
            expect(epic.epics).to(have_len(0))

    with context("a story whose scenarios repeat inside a forEach outline"):
        with it("should count each templated scenario in the outline"):
            content = (
                "/**\n * Sub-epic: Get Sim\n */\n\n"
                "import { scenario, shareStory } from 'tests/story-test';\n"
                "import { simChoiceOutlines } from './examples/sim-choice.examples';\n\n"
                "/**\n * Story: Select Sim\n * Actor: Customer\n */\n"
                "shareStory('Select Sim', () => {\n"
                "  simChoiceOutlines.forEach(({ example, label }) => {\n"
                "    scenario(`Choose ${example}`, ({ when, then }) => {\n"
                "      when(`the Customer selects ${example}`, () => {});\n"
                "      then(`the stored cart holds SIM type ${label}`, () => {});\n"
                "    });\n\n"
                "    scenario(`Choose ${example} — already on the cart`, ({ when, then }) => {\n"
                "      when(`the Customer selects ${example}`, () => {});\n"
                "      then(`the stored cart still holds ${label}`, () => {});\n"
                "    });\n"
                "  });\n"
                "});\n"
            )
            path = "tests/onboard-a-customer/get-sim/get_sim.story.shared.ts"
            model = TypeScriptStoryModel("tests").load({path: content})
            story = model.epics[0].epics[0].stories[0]
            expect([scenario.name for scenario in story.scenarios]).to(
                equal(["Choose ${example}", "Choose ${example} — already on the cart"])
            )
            expect(story.scenarios[0].steps).to(have_len(2))
