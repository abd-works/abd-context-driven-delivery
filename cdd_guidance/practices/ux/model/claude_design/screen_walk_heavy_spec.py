"""The walk of a story canvas's screens: each screen the explorer plays, rendered in Node at the step before its
scenario's first Then and at its last Then, with the values each step names found or left out. Heavy: runs Node."""

import json
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.practices.stories.model.story_map import Epic, Scenario, Step, StepType, Story, StoryMap
from cdd_guidance.practices.ux.model.claude_design.screen_walk import StoryCanvasWalk
from cdd_guidance.practices.ux.model.claude_design.story_canvas import ClaudeDesignStoryMap, StoryCanvasSetup
from cdd_guidance.practices.ux.model.nodes import Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap
from harness.design_canvas.versions import CanvasVersions

# A component the screen imports from the global scope, as a design system's bundle defines one: it uses hooks.
_SHOP_JS = """
window.Shop = {
  LineRow: function (props) {
    const opened = React.useState(false)[0];
    const id = React.useId();
    return React.createElement('div', { id: id, 'aria-label': 'Line ' + props.plan }, props.plan + ' ' + props.price + (opened ? ' open' : ''));
  }
};
"""

# A screen that follows the explorer: it reads the scenario and the step, and shows the Then state at a Then.
_FOLLOWS = """class Component extends DCLogic {
  scenarioStates() { return {"Add one more line": {"given": {"lines": [{"plan": "Atlas", "price": 193}]}, "then": {"lines": [{"plan": "Atlas", "price": 193}, {"plan": "Ace", "price": 153}]}}}; }
  renderVals() {
    const scenario = this.scenarioStates()[this.props.scenario || ''];
    const atThen = /(^|\\n)\\s*Then\\b/.test(this.props.step || '');
    const state = scenario ? (atThen ? scenario.then : scenario.given) : { lines: [] };
    const total = state.lines.reduce((sum, line) => sum + line.price, 0);
    return { lines: state.lines.map((line) => ({ plan: line.plan, price: '$' + line.price + '/mo' })), total: '$' + total + '/mo' };
  }
}"""

# The same screen frozen at one state: it ignores the scenario and the step the explorer hands it.
_FROZEN = """class Component extends DCLogic {
  renderVals() { return { lines: [{ plan: 'Atlas', price: '$193/mo' }], total: '$193/mo' }; }
}"""

_BROKEN = """class Component extends DCLogic {
  renderVals() { return { lines: Missing.lines, total: '' }; }
}"""


def _artboard(logic: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Cart</title>
<script src="./support.js"></script>
<script src="../shop.js"></script>
</head>
<body>
<x-dc>
<helmet><style>body{{margin:0}}</style></helmet>
<div class="cart">
<h1>Your cart</h1>
<sc-for list="{{{{lines}}}}" as="line"><x-import component-from-global-scope="Shop.LineRow" plan="{{{{line.plan}}}}" price="{{{{line.price}}}}"></x-import></sc-for>
<p>Total {{{{total}}}}</p>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"story":{{"editor":null}},"scenario":{{"editor":null}},"step":{{"editor":null}},"go":{{"editor":null}}}}'>
{logic}
</script>
</body>
</html>
"""


def _story_map() -> StoryMap:
    story_map = StoryMap()
    epic = Epic("Choose Lines", 1)
    sub_epic = Epic("Choose Lines", 1)
    story = Story("Add Line To Cart", 1)
    scenario = Scenario("Add one more line", 1)
    given = Step('the Customer has a cart with one "Atlas" line at $193/mo', StepType.GIVEN, 1)
    given.keyword = "Given"
    when = Step("the Customer adds one more line", StepType.WHEN, 2)
    when.keyword = "When"
    then = Step('the cart holds "Atlas" and "Ace"', StepType.THEN, 3)
    then.keyword = "Then"
    then.continue_with("And", "the total is $346/mo")
    scenario.steps.extend([given, when, then])
    story.scenarios.append(scenario)
    sub_epic.stories.append(story)
    epic.epics.append(sub_epic)
    story_map.epics.append(epic)
    return story_map


def _ux_map() -> UxMap:
    screen = Screen("Cart", 1)
    screen.prototype = "screens/cart.dc.html"
    screen.show_story("Add Line To Cart")
    ux_map = UxMap.create()
    ux_map.append_screen(screen)
    return ux_map


def _walk(root: Path, logic: str):
    version = CanvasVersions(root).start_next()
    project = version.folder / "project"
    for name, text in json.loads(ClaudeDesignStoryMap(setup=StoryCanvasSetup(ux_map=_ux_map())).render(_story_map())).items():
        (version.folder / name).parent.mkdir(parents=True, exist_ok=True)
        (version.folder / name).write_text(text, encoding="utf-8")
    (project / "shop.js").write_text(_SHOP_JS, encoding="utf-8")
    (project / "screens" / "cart.dc.html").write_text(_artboard(logic), encoding="utf-8")
    return StoryCanvasWalk(version).walk(_story_map())


with description("a walk of a story canvas's screens") as self:
    with before.each:
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name) / "design-canvas"

    with after.each:
        self.folder.cleanup()

    with context("whose screen follows the scenario and the step the explorer hands it"):
        with before.each:
            self.report = _walk(self.root, _FOLLOWS)

        with it("should find every value the steps name"):
            expect(self.report.misses).to(equal([]))

        with it("should report each step it walked with the values it found"):
            expect(self.report.markdown()).to(contain('| Add Line To Cart › Add one more line | cart | Then the cart holds "Atlas" and "Ace" | "Atlas", "Ace" |  |'))

    with context("whose screen is frozen at one state"):
        with it("should name each value of the Then that the screen leaves out"):
            expect(_walk(self.root, _FROZEN).misses).to(equal(['Add Line To Cart › Add one more line › "Ace"', "Add Line To Cart › Add one more line › $346"]))

    with context("whose screen fails to render"):
        with before.each:
            self.report = _walk(self.root, _BROKEN)

        with it("should name the screen as left out"):
            expect(self.report.misses).to(equal(["Add Line To Cart › Add one more line › (screen did not render)"]))

        with it("should say why in the report"):
            expect(self.report.markdown()).to(contain("Missing is not defined"))
