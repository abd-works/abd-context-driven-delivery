"""Mamba spec for a Claude Design story map. Render writes the canvas: the map page and the screens page."""

import json

from mamba import description, context, it, before
from expects import contain, equal, expect, have_keys, have_len

from cdd_guidance.practices.stories.model.claude_design.nodes import (
    ClaudeDesignEpic,
    ClaudeDesignStory,
    ClaudeDesignStoryModel,
)
from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Step, StepType, Story, StoryModel
from cdd_guidance.practices.ux.model.nodes import Screen


def _story_map() -> StoryModel:
    story_map = StoryModel()
    epic = Epic("Onboard A Customer", 1)
    sub_epic = Epic("Select Plan", 1)
    story = Story("Choose Plan", 1)
    story.actors.append("Customer")
    scenario = Scenario("See the plan catalog", 1)
    scenario.steps.append(Step("the Customer has no account", StepType.GIVEN, 1))
    scenario.steps.append(Step("the Customer opens My Paradise", StepType.WHEN, 2))
    story.scenarios.append(scenario)
    sub_epic.append_story(story)
    sub_epic.append_story(Story("Create Credentials", 2))
    epic.append_epic(sub_epic)
    story_map.append_epic(epic)
    return story_map


def _catalog_screen() -> Screen:
    screen = Screen("Plan catalog", 1)
    screen.image = "shots/plan-catalog.png"
    screen.prototype = "plan-catalog.dc.html"
    screen.attach_step_name("Choose Plan \u203a See the plan catalog \u203a the Customer opens My Paradise")
    return screen


with description("a Claude Design story map") as self:
    with before.each:
        self.files = json.loads(ClaudeDesignStoryModel().render(_story_map(), screens=[_catalog_screen()]))
        self.canvas = json.loads(self.files["project/canvas.json"])

    with context("rendered from a story map whose step is shown on a screen"):
        with it("puts the story map and the screens on their own pages"):
            expect([page["id"] for page in self.canvas["pages"]]).to(equal(["story-map", "screens"]))

        with it("draws the first sub-epic as the entry header with its stories as cards"):
            header = self.files["project/Main.dc.html"]
            expect(header).to(contain("Onboard A Customer"))
            expect(header).to(contain("Select Plan"))
            expect(header).to(contain("Choose Plan"))
            expect(header).to(contain("Create Credentials"))

        with it("sizes the header to one column per story"):
            board = self.canvas["boards"]["Main.dc.html"]
            expect(board["w"]).to(equal(2 * ClaudeDesignStory.width_px + ClaudeDesignStory.gap_px))
            expect(board["page"]).to(equal("story-map"))

        with it("puts a thumbnail under the story for the screen its step is shown on"):
            thumbnail = self.files["project/story-map/choose-plan-01.dc.html"]
            expect(thumbnail).to(contain('src="../shots/plan-catalog.png"'))
            expect(thumbnail).to(contain('href="/screens/plan-catalog.dc.html"'))

        with it("places the explorer and the prototype screen on the screens page"):
            expect(self.canvas["boards"]["screens/explorer.dc.html"]["page"]).to(equal("screens"))
            expect(self.canvas["boards"]["screens/plan-catalog.dc.html"]["page"]).to(equal("screens"))

        with it("draws the prototype screen inside the explorer for the scenario that shows it"):
            explorer = self.files["project/screens/explorer.dc.html"]
            expect(explorer).to(contain('<dc-import name="plan-catalog"'))
            expect(explorer).to(contain('"p": "plan-catalog"'))

    with context("rendered from a story with no screens"):
        with it("gives that story no thumbnails"):
            expect(self.files).not_to(have_keys("project/story-map/create-credentials-01.dc.html"))
