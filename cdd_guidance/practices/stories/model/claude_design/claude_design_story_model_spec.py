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
        with it("puts the story map, the story explorer and each screen on its own page"):
            expect([page["id"] for page in self.canvas["pages"]]).to(equal(["story-map", "screens", "screen-plan-catalog"]))
            expect(self.canvas["boards"]["screens/plan-catalog.dc.html"]["page"]).to(equal("screen-plan-catalog"))

        with it("draws the whole story map on one artboard: epic, sub-epic and story cards"):
            story_map = self.files["project/Main.dc.html"]
            for name in ("Onboard A Customer", "Select Plan", "Choose Plan", "Create Credentials"):
                expect(story_map).to(contain(name))
            expect(self.canvas["boards"]["Main.dc.html"]["page"]).to(equal("story-map"))
            expect([name for name in self.canvas["boards"] if self.canvas["boards"][name]["page"] == "story-map"]).to(equal(["Main.dc.html"]))

        with it("sizes the story map to one column per story inside its margin"):
            board = self.canvas["boards"]["Main.dc.html"]
            expect(board["w"]).to(equal(2 * ClaudeDesignStory.width_px + ClaudeDesignStory.gap_px + 2 * ClaudeDesignStoryModel.margin))

        with it("puts the screen a story's step is shown on under the story, opening the explorer at that step"):
            story_map = self.files["project/Main.dc.html"]
            expect(story_map).to(contain('src="shots/plan-catalog.png"'))
            expect(story_map).to(contain('href="/screens/explorer.dc.html#story=Choose%20Plan&scenario=See%20the%20plan%20catalog'))

        with it("links only the thumbnails, not the story cards"):
            expect(self.files["project/Main.dc.html"].count("<a href")).to(equal(1))

        with it("draws each epic once, across all its sub-epics"):
            expect(self.files["project/Main.dc.html"].count("Onboard A Customer")).to(equal(1))

        with it("draws on the dark abd background, not white"):
            expect(self.files["project/Main.dc.html"]).to(contain("#0B0B0B"))
            expect(self.files["project/Main.dc.html"]).not_to(contain("#ffffff"))

        with it("places the explorer on its page and the prototype screen alone on its own page"):
            expect(self.canvas["boards"]["screens/explorer.dc.html"]["page"]).to(equal("screens"))
            expect(self.canvas["boards"]["screens/plan-catalog.dc.html"]["page"]).to(equal("screen-plan-catalog"))

        with it("draws the prototype screen inside the explorer for the scenario that shows it"):
            explorer = self.files["project/screens/explorer.dc.html"]
            expect(explorer).to(contain('<dc-import name="plan-catalog"'))
            expect(explorer).to(contain('go="{{goToStory}}"'))
            expect(explorer).to(contain('"p": "plan-catalog"'))

    with context("rendered from a story with no screens"):
        with it("gives that story no thumbnail"):
            expect(self.files["project/Main.dc.html"]).not_to(contain("story=Create%20Credentials"))

    with context("rendered with a screen that names a scenario, and a story whose screen names only the story"):
        with before.each:
            select_plan = Screen("Select plan", 2)
            select_plan.prototype = "select-plan.dc.html"
            select_plan.attach_scenario_name("Choose Plan \u203a Pick from the cart")
            credentials = Screen("Create account", 3)
            credentials.prototype = "create-credentials.dc.html"
            credentials.attach_story_name("Create Credentials")
            story_map = _story_map()
            choose_plan = story_map.epics[0].epics[0].stories[0]
            from_cart = Scenario("Pick from the cart", 2)
            from_cart.steps.append(Step("the cart has no plan", StepType.GIVEN, 1))
            choose_plan.scenarios.append(from_cart)
            create = story_map.epics[0].epics[0].stories[1]
            display = Scenario("Display Create Account", 1)
            display.steps.append(Step("the User opens sign-up", StepType.WHEN, 1))
            create.scenarios.append(display)
            files = json.loads(ClaudeDesignStoryModel().render(story_map, screens=[_catalog_screen(), select_plan, credentials]))
            self.explorer = files["project/screens/explorer.dc.html"]

        with it("shows a scenario whose steps show no screen on its own shownOn screen"):
            expect(self.explorer).to(contain('"n": "Pick from the cart", "b": false, "p": "select-plan"'))

        with it("shows a scenario with no screen of its own on its story's screen"):
            expect(self.explorer).to(contain('"n": "Display Create Account", "b": false, "p": "create-credentials"'))

    with context("rendered with the story code's locations"):
        with before.each:
            sources = {"Choose Plan": "tests/select_plan.story.shared.ts:69",
                       "Choose Plan \u203a See the plan catalog": "tests/select_plan.story.shared.ts:73"}
            files = json.loads(ClaudeDesignStoryModel().render(_story_map(), screens=[_catalog_screen()], sources=sources))
            self.explorer = files["project/screens/explorer.dc.html"]

        with it("gives the explorer each story's and scenario's location, for the copy-to-open request"):
            expect(self.explorer).to(contain('"n": "Choose Plan", "f": "tests/select_plan.story.shared.ts:69"'))
            expect(self.explorer).to(contain('"f": "tests/select_plan.story.shared.ts:73"'))
