"""The stories a graph reads at a fidelity that lists no markdown, such as acceptance tests: every scenario comes from
code, its story tests, shared stories, and screen specs, never from a story test written in markdown; a story no code
holds has no scenarios there."""

import tempfile
from pathlib import Path

from expects import be_empty, contain, equal, expect
from mamba import after, before, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices a graph holds
from harness.graph.graph import Graph

_MAP = """\
# Story Map — Checkout

(E) Check Out
    (E) Pay
        (S) Shopper --> Pay For Order
        (S) Shopper --> Cancel Order
"""

_MARKDOWN_TEST = """\
# Sub-epic: Pay

## Story: Pay For Order

#### Scenario: Pay in words

*Given* a cart
*When* the Shopper pays
*Then* the order is paid

## Story: Cancel Order

#### Scenario: Cancel in words

*Given* an order
*When* the Shopper cancels it
*Then* the order is cancelled
"""

_SHARED = """\
shared_stories = SharedStories("Pay")


@shared_stories.scenario("Pay For Order", "Pay by card")
def _(s):
    @s.when("the Shopper pays by card")
    def _(world):
        world.order = world.cart.checkout()
"""

_SCREEN_SPEC = """\
import { expect, test } from './story-ui'

test.describe('Pay For Order', () => {
  test('Pay on the page', async ({ page }) => {
    await page.getByRole('button', { name: 'Pay' }).click()
    await expect(page.getByText('Paid')).toBeVisible()
  })
})
"""


def _scenarios(practice, story: str) -> list[str]:
    part = practice.reading.in_graph
    found = next(node for node in part.nodes("Story") if node.name == story)
    return sorted(edge.child.name for edge in practice.reading.graph.edges_from("scenarios", found))


with description("the stories a graph reads at acceptance tests"):
    with before.all:
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        files = {
            "story-map.md": _MAP,
            "check-out/pay/pay_story.test.md": _MARKDOWN_TEST,
            "pay.story.shared.py": _SHARED,
            "pay.story.ui.spec.ts": _SCREEN_SPEC,
        }
        for name, text in files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text, encoding="utf-8")
        graph = Graph()
        self.practice = graph.practice("stories")
        self.practice.fidelities.current = self.practice.fidelities.entries["acceptance_tests"]
        graph.load_working_copy(str(root), {"stories": str(root)}, force=True)

    with after.all:
        self.folder.cleanup()

    with it("should take a story's scenarios from its shared story file and its screen spec"):
        expect(_scenarios(self.practice, "Pay For Order")).to(equal(["Pay by card", "Pay on the page"]))

    with it("should read no scenario from a story test written in markdown"):
        expect(_scenarios(self.practice, "Pay For Order")).not_to(contain("Pay in words"))

    with it("should leave a story no code holds with no scenarios"):
        expect(_scenarios(self.practice, "Cancel Order")).to(be_empty)

    with it("should report that story's missing scenarios"):
        cancel = next(node for node in self.practice.reading.in_graph.nodes("Story") if node.name == "Cancel Order")
        messages = [violation.message for violation in cancel.rules.violations]
        expect(messages).to(contain("Story 'Cancel Order' has no scenarios relationship to Scenario, which the stories practice schema requires."))
