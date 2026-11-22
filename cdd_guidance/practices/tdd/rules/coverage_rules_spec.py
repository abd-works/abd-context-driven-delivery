"""The parts of TDD's coverage rules the graph can decide. Each reads what a load already records: the links from
observations and steps to the operations they invoke, each test file's tier, and the test files' own text. Every
fixture is a small project read once, through the real working-copy build, for the examples that look at it."""

from expects import contain, equal, expect
from mamba import before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices and TDD with the practice catalogue
from cdd_guidance.practices.tdd.rules import BY_SLUG
from cdd_guidance.practices.tdd.tdd import Tdd
from cdd_guidance.practices.tdd.rules.rule_examples import EXAMPLES, specs_fixture, tested_code_fixture

_OPERATION = "operation-has-a-proving-test"
_EXCEPTION = "declared-exception-raised-by-a-test"
_STUB = "stubbed-boundary-has-heavy-coverage"

# add invokes count, so a test that invokes add reaches count through it.
_CART_THAT_COUNTS = """
class Cart:
    def add(self, item):
        self.count(item)

    def count(self, item):
        return 1
"""
_SPEC_OF_ADD_ALONE = """
from mamba import description, it
from cart import Cart

with description("a cart"):
    with it("should add an item"):
        Cart().add("book")
"""
# Operations the framework calls by name, never through a call the graph can follow: a graph rule's check, which the rule
# registry runs; an operation published as a tool or a hook; and an operation a class registered with a catalogue
# overrides, which the framework calls through the base. A helper beside each is called by nothing and stays listed.
_RULE = """
class PracticeGraphRule:
    def check(self, node):
        ...


class NamedRule(PracticeGraphRule):
    def check(self, node):
        return [node] if not node.name else []

    def label(self):
        return "named"
"""
_PUBLISHED = """
from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.hooks.hooks import hook


@agent_toolset
class Shop:
    @agent_tool
    def open_shop(self):
        return "open"

    @hook
    def on_prompt(self, prompt):
        return prompt
"""
_REGISTERED = """
class Practice:
    def instructions(self):
        ...


class Bookshop(Practice):
    def instructions(self):
        return "sell books"

    def price(self):
        return 1


CATALOGUE.register(Bookshop)
"""
_UNIT_SPEC_WITH_NO_STUB = """
from mamba import description, it

with description("a repository"):
    with it("should push its branch"):
        Repo().push()
"""


def _hits(slug: str, side: int) -> list[str]:
    """What the rule finds in its failing example (side 1) or its repaired one (side 2)."""
    make = EXAMPLES[slug][0]
    return make(EXAMPLES[slug][side]).hits(BY_SLUG[slug])


def _hits_with_no_test(slug: str) -> list[str]:
    """What the rule finds in its failing example's code alone, read with no spec beside it."""
    make, fault, _ = EXAMPLES[slug]
    return make({"cart.py": fault["cart.py"]}).hits(BY_SLUG[slug])


with description("a public operation TDD checks for a test in the graph") as self:
    with before.all:
        self.untested = _hits(_OPERATION, 1)
        self.tested = _hits(_OPERATION, 2)
        self.reached_through_another = tested_code_fixture({"cart.py": _CART_THAT_COUNTS, "cart_spec.py": _SPEC_OF_ADD_ALONE}).hits(BY_SLUG[_OPERATION])
        self.with_no_test_read = _hits_with_no_test(_OPERATION)

    with context("that no observation or step reaches"):
        with it("should be listed by name"):
            expect(self.untested).to(equal(["No observation or step reaches the public operation 'check_out', directly or through an operation it invokes: add a test that invokes it."]))

    with context("that an observation invokes"):
        with it("should pass"):
            expect(self.tested).to(equal([]))

    with context("that an operation an observation invokes goes on to invoke"):
        with it("should pass"):
            expect(self.reached_through_another).to(equal([]))

    with context("in a graph that read no test"):
        with it("should not be judged"):
            expect(self.with_no_test_read).to(equal([]))

    with context("that the framework calls by name, as a graph rule's check, a published tool or hook, or a registered class's override"):
        with it("should pass, leaving listed only the helpers nothing calls"):
            files = {**EXAMPLES[_OPERATION][1], "rules.py": _RULE, "shop.py": _PUBLISHED, "bookshop.py": _REGISTERED}
            listed = tested_code_fixture(files).hits(BY_SLUG[_OPERATION])
            expect(sorted(message.split("'")[1] for message in listed)).to(equal(["check_out", "label", "price"]))

    with it("should require a judge, since the links a load finds miss a call made by a name or through a tool"):
        expect(BY_SLUG[_OPERATION].requires_judge).to(equal(True))


with description("an exception a class declares, which TDD checks for a test in the graph") as self:
    with before.all:
        self.unnamed = _hits(_EXCEPTION, 1)
        self.raised = _hits(_EXCEPTION, 2)
        self.with_no_test_read = _hits_with_no_test(_EXCEPTION)

    with context("that no test file names"):
        with it("should be flagged by name"):
            expect(self.unnamed).to(equal(["No test names the exception 'CartAlreadyCheckedOut', so no test sees it raised: add a test that breaks its invariant and expects it."]))

    with context("that a test expects to be raised"):
        with it("should pass"):
            expect(self.raised).to(equal([]))

    with context("in a graph that read no test"):
        with it("should not be judged"):
            expect(self.with_no_test_read).to(equal([]))


with description("a boundary a unit spec stubs, which TDD checks for a heavy example in the graph") as self:
    with before.all:
        self.unchecked = _hits(_STUB, 1)
        self.run_for_real = _hits(_STUB, 2)
        self.with_no_stub = specs_fixture({"repo_spec.py": _UNIT_SPEC_WITH_NO_STUB}).hits(BY_SLUG[_STUB])

    with context("with no heavy example of the same sentence under the same subject"):
        with it("should be listed with the stub and its line"):
            expect(self.unchecked).to(equal(["repo_spec.py:6: a unit spec stubs a boundary with mock.patch, and no heavy or e2e example has one of its `should` sentences under the subject 'a repository': run that boundary for real in one."]))

    with context("with a heavy example of the same sentence under the same subject"):
        with it("should pass"):
            expect(self.run_for_real).to(equal([]))

    with context("in a unit spec that stubs nothing"):
        with it("should not be listed"):
            expect(self.with_no_stub).to(equal([]))

    with it("should require a judge, since the graph cannot tell a stand-in at a boundary from any other"):
        expect(BY_SLUG[_STUB].requires_judge).to(equal(True))


with description("how TDD's graph rules are decided, as its rule text says it") as self:
    with before.all:
        self.bodies = {rule.slug: rule.body for rule in Tdd().every_rule}

    with it("should say the declared exception rule is checked"):
        expect(self.bodies[_EXCEPTION]).to(contain("Checked: the graph decides this rule"))

    with it("should say the proving test rule is judged"):
        expect(self.bodies[_OPERATION]).to(contain("Judged: the graph only lists candidates"))

    with it("should say the heavy coverage rule is judged"):
        expect(self.bodies[_STUB]).to(contain("Judged: the graph only lists candidates"))
