"""What TypeScript story tests alone do: how a story file imports the step library, and how its outcomes chain.

What every language's story tests do is in `code_story_behaviours_spec.py` and `story_test_behaviours_spec.py`."""

import sys
from pathlib import Path

from expects import be_true, contain, equal, expect, have_len
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

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
        story_map.epics.append(Epic(f"Epic {i}", i))
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
            self.leaf_paths = sorted(path for path in self.tree if self.ts.is_story_file(path))

        with it("should not emit givens.ts — Given steps stay in story tests"):
            expect(any(p.endswith("/givens.ts") for p in self.tree)).to(equal(False))

        with it("should import story-test from the workspace deploy root"):
            leaf = next(p for p in self.leaf_paths)
            expect(self.tree[leaf]).to(contain('from "tests/story-test"'))

    with context("that overrides the deploy root"):
        with before.each:
            self.custom_root = "stories/create-customer"
            self.ts = TypeScriptStoryModel(tests_root=self.custom_root)
            self.tree = self.ts.render(_story_map_with_stories())

        with it("should import story-test from the stories workspace root"):
            leaf = next(p for p in self.tree if p.endswith("_story.test.ts"))
            expect(self.tree[leaf]).to(contain('from "stories/story-test"'))

    with context("that names the step library folder"):
        with before.each:
            self.ts = TypeScriptStoryModel(tests_root="tests", story_test_folder="test-utils/story-test")
            self.tree = self.ts.render(_story_map_with_stories())

        with it("should import story-test from the step library folder"):
            leaf = next(p for p in self.tree if p.endswith("_story.test.ts"))
            expect(self.tree[leaf]).to(contain('from "test-utils/story-test/story-test"'))

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
            from cdd_guidance.practices.stories.model.typescript.nodes import TypeScriptStory

            src = "\n".join(TypeScriptStoryModel().writing.story_lines(TypeScriptStory(story)) + [""])
            expect(".and(" in src).to(be_true)
            expect(src.count("then(")).to(equal(1))

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
