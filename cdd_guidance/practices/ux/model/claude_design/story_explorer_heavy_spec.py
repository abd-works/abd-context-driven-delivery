"""The story explorer as a screen drives it: a screen's go(story, scenario, step) moves the explorer to that step, so an
action on the screen moves the reader on to the step it leads to. Runs the rendered explorer's logic in Node."""

import json
import re
import subprocess

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.story_map import Epic, Scenario, Step, StepType, Story, StoryMap
from cdd_guidance.practices.ux.model.claude_design.story_canvas import ClaudeDesignStoryMap, StoryCanvasSetup
from cdd_guidance.practices.ux.model.nodes import Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap

# Runs the explorer's Component in Node with a stub DCLogic, calls go with its arguments, and prints the step it shows.
_RUN = """
const code = require('fs').readFileSync(0, 'utf8');
const ctx = { window: { location: { hash: '' }, localStorage: { getItem() { return null; } } }, document: {} };
class DCLogic { constructor() { this.props = {}; this.state = null; } setState(next) { this.state = Object.assign({}, this.state || {}, next); } }
const Component = new Function('DCLogic', 'window', 'document', code + '; return Component;')(DCLogic, ctx.window, ctx.document);
const explorer = new Component();
JSON.parse(process.argv[1]).forEach((call) => explorer.renderVals().goToStory(...call));
const shown = explorer.renderVals();
console.log(JSON.stringify({ step: shown.stepText, index: shown.stepIndex }));
"""


def _story_map() -> StoryMap:
    story_map = StoryMap()
    epic = Epic("Choose Lines", 1)
    sub_epic = Epic("Choose Lines", 1)
    story = Story("Add Line To Cart", 1)
    story.actors.append("Customer")
    scenario = Scenario("Add one more line", 1)
    scenario.steps.append(Step("the Customer has a cart with one Atlas line", StepType.GIVEN, 1))
    scenario.steps.append(Step("the Customer adds one more line on plan Ace", StepType.WHEN, 2))
    scenario.steps.append(Step("the cart holds Atlas and Ace", StepType.THEN, 3))
    story.scenarios.append(scenario)
    sub_epic.stories.append(story)
    epic.epics.append(sub_epic)
    story_map.epics.append(epic)
    return story_map


def _two_actions_map() -> StoryMap:
    """A scenario with two actions, each with its outcome: Given, When, Then, When, Then."""
    story_map = StoryMap()
    epic = Epic("Choose Lines", 1)
    sub_epic = Epic("Choose Lines", 1)
    story = Story("Add Line To Cart", 1)
    scenario = Scenario("Add a line, then remove one", 1)
    scenario.steps.append(Step("the Customer has a cart with one Atlas line", StepType.GIVEN, 1))
    scenario.steps.append(Step("the Customer adds a line on plan Ace", StepType.WHEN, 2))
    scenario.steps.append(Step("the cart holds Atlas and Ace", StepType.THEN, 3))
    scenario.steps.append(Step("the Customer removes the Atlas line", StepType.WHEN, 4))
    scenario.steps.append(Step("the cart holds only Ace", StepType.THEN, 5))
    story.scenarios.append(scenario)
    sub_epic.stories.append(story)
    epic.epics.append(sub_epic)
    story_map.epics.append(epic)
    return story_map


def _two_actions_ux_map() -> UxMap:
    """The screen shows the step before each Then and the last step, so each action and its outcome is a group."""
    screen = Screen("Cart", 1)
    screen.prototype = "screens/add-line-to-cart.dc.html"
    screen.show_story("Add Line To Cart")
    for step in ("the Customer adds a line on plan Ace", "the Customer removes the Atlas line", "the cart holds only Ace"):
        screen.show_step(f"Add Line To Cart › Add a line, then remove one › {step}")
    ux_map = UxMap.create()
    ux_map.append_screen(screen)
    return ux_map


def _explored(story_map: StoryMap, ux_map: UxMap, *calls: list) -> dict:
    files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=ux_map)).render(story_map))
    code = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', files["project/screens/explorer.dc.html"]).group(1)
    answer = subprocess.run(["node", "-e", _RUN, json.dumps(list(calls))], input=code, capture_output=True, text=True, check=True)
    return json.loads(answer.stdout)


def _shown_step(*arguments: str) -> str:
    return _explored(_story_map(), _ux_map(), list(arguments))["step"]


def _ux_map() -> UxMap:
    screen = Screen("Cart", 1)
    screen.prototype = "screens/add-line-to-cart.dc.html"
    screen.show_story("Add Line To Cart")
    screen.show_step("Add Line To Cart › Add one more line › the Customer adds one more line on plan Ace")
    screen.show_step("Add Line To Cart › Add one more line › the cart holds Atlas and Ace")
    ux_map = UxMap.create()
    ux_map.append_screen(screen)
    return ux_map


with description("a story explorer that a screen moves") as self:
    with it("should move to the step a screen names, after the screen's action"):
        expect(_shown_step("Add Line To Cart", "Add one more line", "Then")).to(equal("Then the cart holds Atlas and Ace"))

    with it("should open a scenario at its first step when the screen names no step"):
        expect(_shown_step("Add Line To Cart", "Add one more line").startswith("Given")).to(equal(True))

    with context("whose scenario has two actions, each with its outcome"):
        with before.each:
            self.scenario = ["Add Line To Cart", "Add a line, then remove one"]

        with it("should list each action with what leads to it as a step group of its own"):
            shown = _explored(_two_actions_map(), _two_actions_ux_map(), self.scenario + ["Then the cart holds Atlas"])
            expect(shown).to(equal({"step": "Then the cart holds Atlas and Ace\nWhen the Customer removes the Atlas line", "index": 1}))

        with it("should move to the first outcome after the first action"):
            expect(_explored(_two_actions_map(), _two_actions_ux_map(), self.scenario, self.scenario + ["Then"])["index"]).to(equal(1))

        with it("should move to the next outcome after the next action, not back to the first"):
            shown = _explored(_two_actions_map(), _two_actions_ux_map(), self.scenario, self.scenario + ["Then"], self.scenario + ["Then"])
            expect(shown).to(equal({"step": "Then the cart holds only Ace", "index": 2}))
