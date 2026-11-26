"""Specs for which scenarios of a markdown scenarios file are outlines: one whose heading says Scenario Outline, never
one whose name merely holds the word. The spec every practice shares found the scenarios template's plain scenario
"variation — delta from the outline" read as an outline and failed for having no example rows."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[5]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, description, it

from cdd_guidance.practices.stories.stories import Stories
from harness.graph.rule_fixture import RuleFixture

_STORY_MAP = "# (E) Sell Books\n## (E) Take Orders\n### (S) Customer --> Place Order\n### (S) Customer --> Cancel Order\n"
_SCENARIOS = (
    "# Sub-epic: Take Orders\n\n"
    "## Story: Place Order\n\n"
    "#### Scenario Outline: Order books\n\n"
    "*Given* a Customer with an empty basket\n*When* the Customer orders <copies> books\n*Then* the order holds <copies> lines\n\n"
    "#### Scenario: Show the outline of the order\n\n"
    "*Given* a Customer with an open order\n*When* the Customer views the order\n*Then* the outline of the order is shown\n"
)

with description("the scenarios of a markdown scenarios file") as self:
    with before.all:
        fixture = RuleFixture(Stories, {"story-map.md": _STORY_MAP, "story_tests/sell-books/take-orders/take_orders_story.test.md": _SCENARIOS})
        self.fixture = fixture
        self.outlines = {node.name: bool(node.facts.get("is_outline")) for node in fixture.practice.reading.in_graph.nodes("Scenario")}

    with it("should read a scenario headed Scenario Outline as an outline"):
        expect(self.outlines["Order books"]).to(equal(True))

    with it("should read a plain scenario whose name holds the word outline as no outline"):
        expect(self.outlines["Show the outline of the order"]).to(equal(False))
