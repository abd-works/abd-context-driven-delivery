"""What JavaScript story tests alone do: how a story file imports the step library.

What every language's story tests do is in `code_story_behaviours_spec.py` and `story_test_behaviours_spec.py`."""

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.javascript.javascript_story_map import JavaScriptStoryMap
from cdd_guidance.practices.stories.model.story_map import Epic, Scenario, Step, StepType, Story, StoryMap, StoryType


def _story_map_with_a_story() -> StoryMap:
    """An epic with a sub-epic that holds the story Redeem a voucher and one scenario."""
    story_map = StoryMap()
    epic = Epic("Epic 1", 1)
    sub_epic = Epic("Epic 1.1", 1)
    story = Story("Redeem a voucher", 1, StoryType.USER)
    scenario = Scenario(name="Voucher is active", sequential_order=1)
    scenario.steps = [Step("an active voucher exists", StepType.GIVEN, 1), Step("the action occurs", StepType.WHEN, 2), Step("the outcome is observed", StepType.THEN, 3)]
    story.scenarios.append(scenario)
    sub_epic.stories.append(story)
    epic.epics.append(sub_epic)
    story_map.epics.append(epic)
    return story_map


def _story_test_of(tree: dict) -> str:
    return next(text for path, text in tree.items() if path.endswith("_story.test.js"))


with description("a JavaScript story test") as self:
    with context("written under the tests root"):
        with before.all:
            self.story_test = _story_test_of(JavaScriptStoryMap().render(_story_map_with_a_story()))

        with it("should import the step library by the path from the story's own folder, with the file's extension"):
            expect(self.story_test).to(contain('import { background, scenario, story } from "../../../story-test.js";'))

        with it("should write no examples table on a scenario, whose rows nobody gave"):
            expect("examples: [" in self.story_test).to(equal(False))

    with context("written for a project whose pattern names the step library's folder"):
        with before.all:
            model = JavaScriptStoryMap(tests_root="tests", story_test_folder="test-utils/story-test")
            self.story_test = _story_test_of(model.render(_story_map_with_a_story()))

        with it("should import the step library by the path from the story's own folder to that folder"):
            expect(self.story_test).to(contain('from "../../../../test-utils/story-test/story-test.js";'))
