"""The story explorer as a screen drives it: a screen's go(story, scenario, step) moves the explorer to that step, so an
action on the screen moves the reader on to the step it leads to. Runs the rendered explorer's logic in Node."""

import json
import re
import subprocess

from expects import equal, expect
from mamba import before, description, it

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
explorer.renderVals().goToStory(...JSON.parse(process.argv[1]));
console.log(JSON.stringify(explorer.renderVals().stepText));
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


def _shown_step(*arguments: str) -> str:
    files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map())).render(_story_map()))
    code = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', files["project/screens/explorer.dc.html"]).group(1)
    answer = subprocess.run(["node", "-e", _RUN, json.dumps(list(arguments))], input=code, capture_output=True, text=True, check=True)
    return json.loads(answer.stdout)


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
