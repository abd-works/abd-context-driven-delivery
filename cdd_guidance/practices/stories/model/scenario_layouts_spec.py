"""The same two stories written in every layout a project keeps its scenarios in: one markdown file per story, one
markdown file per sub-epic holding several stories, the story map alone, code alone in Python or TypeScript, and
markdown beside a story test in Python or TypeScript. Each layout gives the graph the same stories, scenarios and steps.
Where markdown and code both write a story, they merge: the markdown gives each scenario and its steps, the code gives
their bodies, and a scenario only the code writes is added; no scenario of the markdown is lost to the code."""

import tempfile
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import after, before, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices a graph holds
from harness.graph.graph import Graph
from harness.graph.saved_graph import SavedGraph

from cdd_guidance.practices.ux.model.claude_design.project_story_canvas import NoCanvasFixtures, ProjectStoryCanvas

_MAP = ".context/story-map.md"
_MAP_TEXT = "# Story Map\n\n# (E) Check Out\n## (E) Pay\n### (S) Shopper --> Pay For Order\n### (S) Shopper --> Cancel Order\n"
# A story map written as headings and bullets lists each story's scenarios under it.
_MAP_LISTING_SCENARIOS = "# Check Out\n\n## Pay\n\n- Pay For Order\n  - Pay by card\n- Cancel Order\n  - Cancel an open order\n"

_PAY_SCENARIO = "#### Scenario: Pay by card\n\n*Given* a cart\n*When* the Shopper pays by card\n*Then* the order is paid\n"
_CANCEL_SCENARIO = "#### Scenario: Cancel an open order\n\n*Given* an open order\n*When* the Shopper cancels it\n*Then* the order is cancelled\n"

_PAY_FILE = "story_tests/check-out/pay/pay-for-order/pay_for_order_story.test.md"
_CANCEL_FILE = "story_tests/check-out/pay/cancel-order/cancel_order_story.test.md"
_ONE_STORY_PER_FILE = {
    _MAP: _MAP_TEXT,
    _PAY_FILE: f"# Story: Pay For Order\n\n{_PAY_SCENARIO}",
    _CANCEL_FILE: f"# Story: Cancel Order\n\n{_CANCEL_SCENARIO}",
}

_SUB_EPIC_FILE = "story_tests/check-out/pay/pay_story.test.md"
_SUB_EPIC_FILE_HOLDING_BOTH = {
    _MAP: _MAP_TEXT,
    _SUB_EPIC_FILE: f"# Sub-epic: Pay\n\n## Story: Pay For Order\n\n{_PAY_SCENARIO}\n## Story: Cancel Order\n\n{_CANCEL_SCENARIO}",
}

_PYTHON_PAY = '''\
from story_test import given, scenario, story, then, when

with story("Pay For Order"):
    with scenario("Pay by card"):
        with given("a cart"):
            cart = Cart()
        with when("the Shopper pays by card"):
            cart.pay_by_card()
        with then("the order is paid"):
            assert cart.paid
'''
_PYTHON_VOUCHER = '''
    with scenario("Pay with a voucher"):
        with given("a cart"):
            cart = Cart()
        with when("the Shopper pays with a voucher"):
            cart.pay_with_voucher()
        with then("the order is paid"):
            assert cart.paid
'''
_PYTHON_CANCEL = '''
with story("Cancel Order"):
    with scenario("Cancel an open order"):
        with given("an open order"):
            order = Order()
        with when("the Shopper cancels it"):
            order.cancel()
        with then("the order is cancelled"):
            assert order.cancelled
'''

_TYPESCRIPT_PAY = """\
import { scenario, shareStory } from 'test-utils/story-test/story-test';

shareStory('Pay For Order', () => {
  scenario('Pay by card', ({ given, when, then }) => {
    given('a cart', () => { cart = new Cart(); });
    when('the Shopper pays by card', () => { cart.payByCard(); });
    then('the order is paid', () => { expect(cart.paid).toBe(true); });
  });
"""
_TYPESCRIPT_VOUCHER = """
  scenario('Pay with a voucher', ({ given, when, then }) => {
    given('a cart', () => { cart = new Cart(); });
    when('the Shopper pays with a voucher', () => { cart.payWithVoucher(); });
    then('the order is paid', () => { expect(cart.paid).toBe(true); });
  });
"""
_TYPESCRIPT_CANCEL = """
shareStory('Cancel Order', () => {
  scenario('Cancel an open order', ({ given, when, then }) => {
    given('an open order', () => { order = new Order(); });
    when('the Shopper cancels it', () => { order.cancel(); });
    then('the order is cancelled', () => { expect(order.cancelled).toBe(true); });
  });
});
"""

_PYTHON_ONLY = {"story_tests/check-out/pay/pay_story.test.py": _PYTHON_PAY + _PYTHON_CANCEL}
_TYPESCRIPT_ONLY = {"story_tests/check-out/pay/pay.story.shared.ts": _TYPESCRIPT_PAY + "});\n" + _TYPESCRIPT_CANCEL}
_MARKDOWN_BESIDE_PYTHON = {**_SUB_EPIC_FILE_HOLDING_BOTH, "story_tests/check-out/pay/pay_story.test.py": _PYTHON_PAY + _PYTHON_VOUCHER}
_MARKDOWN_BESIDE_TYPESCRIPT = {**_ONE_STORY_PER_FILE, "story_tests/check-out/pay/pay.story.shared.ts": _TYPESCRIPT_PAY + _TYPESCRIPT_VOUCHER + "});\n"}

_STORIES = [
    ("Pay For Order", "Pay by card", ["given a cart", "when the Shopper pays by card", "then the order is paid"]),
    ("Cancel Order", "Cancel an open order", ["given an open order", "when the Shopper cancels it", "then the order is cancelled"]),
]
_ONLY_IN_CODE = ("Pay For Order", "Pay with a voucher", ["given a cart", "when the Shopper pays with a voucher", "then the order is paid"])


class _Layout:
    """One project written in a layout, read into a graph as a session's graph reads it."""

    def __init__(self, files: dict[str, str]) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.root = Path(self._folder.name)
        (self.root / ".git").mkdir()
        for name, text in files.items():
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(text, encoding="utf-8")
        self.graph = Graph()
        self.graph.load_working_copy(str(self.root), {"stories": "."}, force=True)

    def scenarios(self) -> list[tuple]:
        """Each story's scenarios, in the order the map gives them, each with its steps' names."""
        held = []
        for story in self._stories.nodes("Story"):
            for scenario in self._children("scenarios", story):
                held.append((story.name, scenario.name, [step.name for step in self._steps(scenario)]))
        return held

    def scenario_names(self) -> list[tuple]:
        return [(story, scenario) for story, scenario, _steps in self.scenarios()]

    def file_of(self, scenario_name: str) -> str:
        return next(node.source.file for node in self._stories.nodes("Scenario") if node.name == scenario_name)

    def step_has_a_body(self, step_name: str) -> bool:
        return any(bool(node.get_fact("body_text")) for node in self._stories.nodes() if node.name == step_name)

    def checked(self, file: str) -> list[str]:
        """The scenarios a validate of file is given: the nodes a refresh of the session's graph reads from it."""
        checked = self.root / "checked.json"
        self.graph.reads.refreshed([file], checked)
        return [node.name for node in SavedGraph.from_file(checked).practices["stories"].nodes if node.type == "Scenario"]

    def drawn(self) -> list[tuple]:
        """Each story's scenarios as the story explorer draws them, each with its steps' text."""
        story_map = ProjectStoryCanvas(self.root, self.root / "ux", self.root, NoCanvasFixtures([])).story_map()
        return [
            (story.name, scenario.name, [f"{step.keyword.lower()} {step.text}" for step in scenario.steps])
            for story in story_map.descendants.stories()
            for scenario in story.scenarios
        ]

    def close(self) -> None:
        self._folder.cleanup()

    @property
    def _stories(self):
        return self.graph.practices.named("stories").reading.in_graph

    def _children(self, edge: str, parent) -> list:
        return [found.child for found in self.graph.edges.from_parent(edge, parent)]

    def _steps(self, parent) -> list:
        steps = []
        for step in self._children("steps", parent):
            steps += [step, *self._steps_chained(step)]
        return steps

    def _steps_chained(self, step) -> list:
        chained = []
        for continued in self._children("ands", step):
            chained += [continued, *self._steps_chained(continued)]
        return chained


with description("two stories written in every layout a project keeps its scenarios in") as self:
    with before.all:
        self.layouts = {
            "one story per file": _Layout(_ONE_STORY_PER_FILE),
            "a sub-epic file": _Layout(_SUB_EPIC_FILE_HOLDING_BOTH),
            "the story map alone": _Layout({_MAP: _MAP_LISTING_SCENARIOS}),
            "Python alone": _Layout(_PYTHON_ONLY),
            "TypeScript alone": _Layout(_TYPESCRIPT_ONLY),
            "markdown beside Python": _Layout(_MARKDOWN_BESIDE_PYTHON),
            "markdown beside TypeScript": _Layout(_MARKDOWN_BESIDE_TYPESCRIPT),
        }

    with after.all:
        for layout in self.layouts.values():
            layout.close()

    with it("should read each story, scenario and step from one markdown file per story"):
        expect(self.layouts["one story per file"].scenarios()).to(equal(_STORIES))

    with it("should read each story, scenario and step from a sub-epic's markdown file holding both stories"):
        expect(self.layouts["a sub-epic file"].scenarios()).to(equal(_STORIES))

    with it("should read each story and the scenarios the story map lists under it, from the story map alone"):
        expect(self.layouts["the story map alone"].scenario_names()).to(equal([(story, scenario) for story, scenario, _steps in _STORIES]))

    with it("should read each story, scenario and step from story tests in Python alone"):
        expect(self.layouts["Python alone"].scenarios()).to(equal(_STORIES))

    with it("should read each story, scenario and step from story tests in TypeScript alone"):
        expect(self.layouts["TypeScript alone"].scenarios()).to(equal(_STORIES))

    with it("should keep every scenario and step of markdown beside Python, and add the scenario only Python writes"):
        expect(self.layouts["markdown beside Python"].scenarios()).to(equal([_STORIES[0], _ONLY_IN_CODE, _STORIES[1]]))

    with it("should keep every scenario and step of markdown beside TypeScript, and add the scenario only TypeScript writes"):
        expect(self.layouts["markdown beside TypeScript"].scenarios()).to(equal([_STORIES[0], _ONLY_IN_CODE, _STORIES[1]]))

    with it("should place a scenario both write in the sub-epic's markdown file"):
        expect(self.layouts["markdown beside Python"].file_of("Pay by card")).to(equal(_SUB_EPIC_FILE))

    with it("should place a scenario both write in the story's own markdown file"):
        expect(self.layouts["markdown beside TypeScript"].file_of("Pay by card")).to(equal(_PAY_FILE))

    with it("should give a markdown step the body Python gives the same step"):
        expect(self.layouts["markdown beside Python"].step_has_a_body("when the Shopper pays by card")).to(be_true)

    with it("should give a markdown step the body TypeScript gives the same step"):
        expect(self.layouts["markdown beside TypeScript"].step_has_a_body("when the Shopper pays by card")).to(be_true)

    with it("should give a validate of the sub-epic's markdown file every scenario it writes, beside Python"):
        expect(self.layouts["markdown beside Python"].checked(_SUB_EPIC_FILE)).to(contain("Pay by card", "Cancel an open order"))

    with it("should give a validate of a story's own markdown file its scenario, beside TypeScript"):
        expect(self.layouts["markdown beside TypeScript"].checked(_PAY_FILE)).to(equal(["Pay by card"]))

    with it("should draw in the story explorer the stories, scenarios and steps the graph reads, in every layout that writes steps"):
        drawn = {name: layout.drawn() for name, layout in self.layouts.items() if name != "the story map alone"}
        read = {name: layout.scenarios() for name, layout in self.layouts.items() if name != "the story map alone"}
        expect(drawn).to(equal(read))
