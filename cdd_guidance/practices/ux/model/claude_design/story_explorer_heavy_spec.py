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


def _rows(story_map: StoryMap, open_all: bool = False) -> list:
    """The rows the explorer's tree draws for story_map, each as (label, indent), every row opened when open_all."""
    run = _RUN.replace("const shown = explorer.renderVals();", (
        "for (let round = 0; OPEN && round < 10; round += 1) explorer.renderVals().rows.filter((row) => row.mark === '›' && row.markCls === 'sm-chev').forEach((row) => row.pick());\n"
        "const shown = explorer.renderVals();").replace("OPEN", "true" if open_all else "false")).replace(
        "console.log(JSON.stringify({ step: shown.stepText, index: shown.stepIndex }));",
        "console.log(JSON.stringify(shown.rows.filter((row) => row.is_epic || row.is_subEpic || row.is_story).map((row) => [row.label, row.indent])));")
    files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=UxMap.create())).render(story_map))
    code = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', files["project/screens/explorer.dc.html"]).group(1)
    answer = subprocess.run(["node", "-e", run, "[]"], input=code, capture_output=True, text=True, check=True)
    return [tuple(row) for row in json.loads(answer.stdout)]


def _story_with_a_scenario(name: str) -> Story:
    story = Story(name, 1)
    scenario = Scenario(f"Use {name}", 1)
    scenario.steps.append(Step("the Customer opens the screen", StepType.WHEN, 1))
    story.scenarios.append(scenario)
    return story


def _ux_map() -> UxMap:
    screen = Screen("Cart", 1)
    screen.prototype = "screens/add-line-to-cart.dc.html"
    screen.show_story("Add Line To Cart")
    screen.show_step("Add Line To Cart › Add one more line › the Customer adds one more line on plan Ace")
    screen.show_step("Add Line To Cart › Add one more line › the cart holds Atlas and Ace")
    ux_map = UxMap.create()
    ux_map.append_screen(screen)
    return ux_map


def _outline_map() -> StoryMap:
    """Create Credentials with an outline whose steps name its columns, and two rows in its Examples table."""
    story_map = StoryMap()
    epic = Epic("Create Account", 1)
    story = Story("Create Credentials", 1)
    outline = Scenario("Enter Invalid credentials", 1)
    outline.steps.append(Step("the Customer has entered {example}", StepType.GIVEN, 1))
    outline.steps.append(Step("the Customer registers the credentials", StepType.WHEN, 2))
    outline.steps.append(Step("the {message} message is shown", StepType.THEN, 3))
    outline.examples["missing email"] = {"message": "++email required++"}
    outline.examples["password missing letters"] = {"message": "password rule"}
    story.scenarios.append(outline)
    epic.stories.append(story)
    story_map.epics.append(epic)
    return story_map


def _outline_steps(*calls: list, rows: bool = True) -> dict:
    """The step rows and the step text the explorer shows for the outline after calls, its rows listed by the fixtures
    bundle when rows."""
    listed = "['Enter Invalid credentials: missing email', 'Enter Invalid credentials: password missing letters']" if rows else "[]"
    run = _RUN.replace("const explorer = new Component();", f"globalThis.CanvasFixtures = {{ scenarios: () => {listed} }};\nconst explorer = new Component();").replace(
        "console.log(JSON.stringify({ step: shown.stepText, index: shown.stepIndex }));",
        "console.log(JSON.stringify({ steps: shown.rows.filter((row) => /^(Given|Then)/.test(row.label || '')).map((row) => row.label), step: shown.stepText }));")
    files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=UxMap.create())).render(_outline_map()))
    code = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', files["project/screens/explorer.dc.html"]).group(1)
    answer = subprocess.run(["node", "-e", run, json.dumps(list(calls))], input=code, capture_output=True, text=True, check=True)
    return json.loads(answer.stdout)


with description("a story explorer that a screen moves") as self:
    with it("should move to the step a screen names, after the screen's action"):
        expect(_shown_step("Add Line To Cart", "Add one more line", "Then")).to(equal("Then the cart holds Atlas and Ace"))

    with it("should open a scenario at its first step when the screen names no step"):
        expect(_shown_step("Add Line To Cart", "Add one more line").startswith("Given")).to(equal(True))

    with context("whose outline's example rows run as '<outline>: <row>'"):
        with it("should list each row under the outline, so the screen loads that row's fixture"):
            run = _RUN.replace("const explorer = new Component();", "globalThis.CanvasFixtures = { scenarios: () => ['Add one more line: Ace', 'Add one more line: Atlas'] };\nconst explorer = new Component();").replace(
                "console.log(JSON.stringify({ step: shown.stepText, index: shown.stepIndex }));",
                "console.log(JSON.stringify({ rows: shown.rows.filter((row) => row.is_example).map((row) => row.label), scenario: shown.scenarioName }));")
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map())).render(_story_map()))
            code = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', files["project/screens/explorer.dc.html"]).group(1)
            answer = subprocess.run(["node", "-e", run, json.dumps([["Add Line To Cart", "Add one more line"]])], input=code, capture_output=True, text=True, check=True)
            expect(json.loads(answer.stdout)).to(equal({"rows": ["Ace", "Atlas"], "scenario": "Add one more line: Ace"}))

        with it("should keep the row picked when a step group of the outline is picked"):
            run = _RUN.replace("const explorer = new Component();", "globalThis.CanvasFixtures = { scenarios: () => ['Add one more line: Ace', 'Add one more line: Atlas'] };\nconst explorer = new Component();").replace(
                "const shown = explorer.renderVals();",
                "explorer.renderVals().rows.filter((row) => /^Then/.test(row.label || ''))[0].pick();\nconst shown = explorer.renderVals();").replace(
                "console.log(JSON.stringify({ step: shown.stepText, index: shown.stepIndex }));",
                "console.log(JSON.stringify(shown.scenarioName));")
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map())).render(_story_map()))
            code = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', files["project/screens/explorer.dc.html"]).group(1)
            answer = subprocess.run(["node", "-e", run, json.dumps([["Add Line To Cart", "Add one more line: Atlas"]])], input=code, capture_output=True, text=True, check=True)
            expect(json.loads(answer.stdout)).to(equal("Add one more line: Atlas"))

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

    with context("whose story map holds stories directly under an epic"):
        with it("should draw the epic once and its stories under it, with no repeated row"):
            story_map = StoryMap()
            epic = Epic("Choose Lines", 1)
            epic.stories.append(_story_with_a_scenario("Display Plans"))
            epic.stories.append(_story_with_a_scenario("View Cart"))
            story_map.epics.append(epic)
            expect(_rows(story_map)).to(equal([("Choose Lines", "margin-left: 0px"), ("Display Plans", "margin-left: 0px"), ("View Cart", "margin-left: 0px")]))

    with context("whose story map nests epics three deep"):
        with it("should draw each level once, set in by its depth below the first sub-epic, and open and close at every level"):
            story_map = StoryMap()
            epic, sub_epic, inner = Epic("Onboard A Customer", 1), Epic("Choose Lines", 1), Epic("Pick Plans", 1)
            inner.stories.append(_story_with_a_scenario("Display Plans"))
            sub_epic.epics.append(inner)
            epic.epics.append(sub_epic)
            story_map.epics.append(epic)
            expect(_rows(story_map)).to(equal([("Onboard A Customer", "margin-left: 0px"), ("Choose Lines", "margin-left: 0px"),
                                               ("Pick Plans", "margin-left: 10px"), ("Display Plans", "margin-left: 10px")]))

        with it("should close a nested epic's stories away when that epic is closed"):
            story_map = StoryMap()
            epic, sub_epic, inner = Epic("Onboard A Customer", 1), Epic("Choose Lines", 1), Epic("Pick Plans", 1)
            inner.stories.append(_story_with_a_scenario("Display Plans"))
            sub_epic.epics.append(inner)
            epic.epics.append(sub_epic)
            story_map.epics.append(epic)
            closed = _RUN.replace("const shown = explorer.renderVals();",
                                  "explorer.renderVals().rows.filter((row) => row.label === 'Pick Plans')[0].pick();\nconst shown = explorer.renderVals();").replace(
                "console.log(JSON.stringify({ step: shown.stepText, index: shown.stepIndex }));",
                "console.log(JSON.stringify(shown.rows.map((row) => row.label)));")
            files = json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=UxMap.create())).render(story_map))
            code = re.search(r'<script type="text/x-dc"[^>]*>([\s\S]*?)</script>', files["project/screens/explorer.dc.html"]).group(1)
            answer = subprocess.run(["node", "-e", closed, "[]"], input=code, capture_output=True, text=True, check=True)
            expect(json.loads(answer.stdout)).to(equal(["Onboard A Customer", "Choose Lines", "Pick Plans"]))

    with context("whose outline has a row picked"):
        with it("should show the picked row's values in the steps, as its Examples table gives them"):
            shown = _outline_steps(["Create Credentials", "Enter Invalid credentials: password missing letters"])
            expect(shown).to(equal({"steps": ["Given the Customer has entered password missing letters\nWhen the Customer registers the credentials\nThen the password rule message is shown"], "step": "Given the Customer has entered password missing letters\nWhen the Customer registers the credentials\nThen the password rule message is shown"}))

    with context("whose outline has no row to pick"):
        with it("should show the outline's placeholders"):
            shown = _outline_steps(["Create Credentials", "Enter Invalid credentials"], rows=False)
            expect(shown["step"]).to(equal("Given the Customer has entered {example}\nWhen the Customer registers the credentials\nThen the {message} message is shown"))
