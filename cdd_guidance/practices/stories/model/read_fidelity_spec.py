"""The fidelity Stories reads each story at, which its reading records on the story by what the story holds, whatever
format it is written in: a story with no scenarios is at the story map, one whose scenarios' steps have no bodies is at
scenarios, and one whose steps have bodies is at acceptance tests. Its scenarios and steps take the story's fidelity."""

from expects import equal, expect, have_len
from mamba import before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.stories.stories import Stories
from harness.graph.rule_fixture import RuleFixture, SchemaRuleRun
from cdd_guidance.practices.stories.rules import BY_SLUG

_MAP = "# (E) Sell Books\n## (E) Take Orders\n### (S) Customer --> Place Order\n### (S) Customer --> Cancel Order\n"
_SCENARIOS = (
    "# Sub-epic: Take Orders\n\n## Story: Place Order\n\n#### Scenario: Order one book\n\n"
    "*Given* a Customer with an empty basket\n*When* the Customer places an order for one book\n*Then* the order holds one line\n"
)
_STORY_TEST = '''from story_test import given, scenario, story, then, when

# Epic: Sell Books
# Sub-epic: Take Orders

# Story: Place Order
# Actor: Customer
with story("Place Order"):
    with scenario("Order one book"):
        with given("a Customer with an empty basket"):
            {given}
        with when("the Customer places an order for one book"):
            {when}
        with then("the order holds one line"):
            {then}
'''
_SCENARIOS_FILE = "story_tests/sell-books/take-orders/take_orders_story.test.md"
_STORY_TEST_FILE = "story_tests/sell-books/take-orders/place_order_story.test.py"


def _read(files: dict[str, str]) -> dict[str, str]:
    """The fidelity each story and step read from files answers, by the node's type and name."""
    nodes = RuleFixture(Stories, files).practice.reading.in_graph.nodes()
    return {f"{node.type} {node.name}": node.fidelity_read_at for node in nodes if node.type in ("Story", "Scenario", "When")}


with description("the fidelity Stories reads a story at") as self:
    with context("with no scenarios, on a story map"):
        with before.all:
            self.read = _read({"story-map.md": _MAP})

        with it("should be the story map"):
            expect(self.read["Story Place Order"]).to(equal("story_map"))

    with context("with scenarios whose steps have no bodies, in a markdown scenarios file"):
        with before.all:
            self.read = _read({"story-map.md": _MAP, _SCENARIOS_FILE: _SCENARIOS})

        with it("should be scenarios"):
            expect(self.read["Story Place Order"]).to(equal("scenarios"))

        with it("should be scenarios for its scenario and its steps, which take the story's fidelity"):
            expect((self.read["Scenario Order one book"], self.read["When when the Customer places an order for one book"])).to(equal(("scenarios", "scenarios")))

        with it("should stay the story map for the story beside it that has no scenarios"):
            expect(self.read["Story Cancel Order"]).to(equal("story_map"))

    with context("with scenarios whose steps have no bodies, in a story test in code"):
        with before.all:
            self.read = _read({"story-map.md": _MAP, _STORY_TEST_FILE: _STORY_TEST.format(given="pass", when="pass", then="pass")})

        with it("should be scenarios, since the format plays no part"):
            expect(self.read["Story Place Order"]).to(equal("scenarios"))

    with context("with a step that has a body"):
        with before.all:
            self.read = _read({"story-map.md": _MAP, _STORY_TEST_FILE: _STORY_TEST.format(given="basket = Basket()", when="order = basket.place()", then="expect(order.lines).to(have_len(1))")})

        with it("should be acceptance tests"):
            expect(self.read["Story Place Order"]).to(equal("acceptance_tests"))

        with it("should be acceptance tests for its steps"):
            expect(self.read["When when the Customer places an order for one book"]).to(equal("acceptance_tests"))


# code-steps-invoke-code is a rule of the acceptance tests fidelity, so it judges a When by the fidelity its story is
# read at, never by the format the step is written in.
with description("a When that calls nothing, judged by code-steps-invoke-code") as self:
    with context("in a story test whose steps have no bodies yet, at scenarios"):
        with it("should be left out"):
            files = {"story-map.md": _MAP, _STORY_TEST_FILE: _STORY_TEST.format(given="pass", when="pass", then="pass")}
            expect(SchemaRuleRun(BY_SLUG["code-steps-invoke-code"], RuleFixture(Stories, files, beside=(CleanEngineering,)).context).hits()).to(equal([]))

    with context("in a story test with a step that has a body, at acceptance tests"):
        with it("should be flagged"):
            files = {"story-map.md": _MAP, _STORY_TEST_FILE: _STORY_TEST.format(given="basket = Basket()", when="pass", then="pass")}
            expect(SchemaRuleRun(BY_SLUG["code-steps-invoke-code"], RuleFixture(Stories, files, beside=(CleanEngineering,)).context).hits()).to(have_len(1))
