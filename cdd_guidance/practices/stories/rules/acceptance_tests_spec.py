"""Example fixtures live in an examples file named the way each acceptance-test language names one."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect  # noqa: E402
from mamba import before, context, description, it  # noqa: E402

from cdd_guidance.practices.stories.rules.acceptance_tests import DomainFixtureExampleFiles  # noqa: E402
from harness.graph.graph import Graph, Node, Source  # noqa: E402
from harness.graph.saved_graph import NodeIdentity
from harness.graph.rule_context import RuleCheckContext  # noqa: E402
from harness.graph.rule_fixture import SchemaRuleRun  # noqa: E402


def _hits(file: str, *, imported_from: str | None = None) -> list[str]:
    """What the rule says about the example validCustomer, read from file or imported into file from a module."""
    practice = Graph().practices.named("stories")
    node = Node(practice, NodeIdentity(type="Example", node_id=f"stories:Example:{file}:validCustomer", name="validCustomer"), Source(file, 1, 1))
    if imported_from is not None:
        node.set_fact("imported_modules", {"validCustomer": imported_from})
    practice.reading.in_graph.hold(node)
    return SchemaRuleRun(DomainFixtureExampleFiles(), RuleCheckContext(practice)).node_hits(node)


with description("an example fixture in an acceptance test"):
    # A process reads the practices' guidance once, for its first graph; read it here, not in the first example.
    with before.all:
        Graph()

    with context("that a TypeScript story test imports from an examples module"):
        with it("should pass"):
            expect(_hits("tests/onboard/onboard.story.shared.ts", imported_from="./examples/customers.examples")).to(equal([]))

    with context("that a JavaScript story test imports from an examples module"):
        with it("should pass"):
            expect(_hits("tests/onboard/onboard.story.shared.js", imported_from="./examples/customers.examples")).to(equal([]))

    with context("that sits in a Python examples file"):
        with it("should pass"):
            expect(_hits("tests/onboard/examples/customers_examples.py")).to(equal([]))

    # A Python story test imports its examples from a package Python can import, which a story folder with a hyphen
    # in its name is not: this repository keeps them beside the code they build (space/kanban/session_board_examples.py).
    with context("that sits in a Python examples file beside the code it builds, in no examples folder"):
        with it("should pass"):
            expect(_hits("src/shop/order_examples.py")).to(equal([]))

    with context("that sits in a Python file not named for examples"):
        with it("should be told the Python examples-file ending"):
            expect(_hits("tests/onboard/examples/customers.py")).to(equal(
                ["Example file 'customers.py' should end with _examples.py."]
            ))

    with context("that sits in an examples file outside an examples folder"):
        with it("should be told to move it under an examples folder"):
            expect(_hits("tests/onboard/customers.examples.ts")).to(equal(
                ["Example file 'customers.examples.ts' should live under an examples/ folder."]
            ))

    # Markdown is a format the scenarios fidelity writes, and its examples are rows of a table in the scenarios file:
    # no examples module holds them, so the rule has nothing to say about where they sit.
    with context("that is a row of an examples table in a markdown scenarios file"):
        with it("should pass"):
            expect(_hits("story_tests/fill-cart/add-books/add_book_to_cart_story.test.md")).to(equal([]))
