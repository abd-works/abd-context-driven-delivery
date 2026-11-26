"""The fidelity DDD reads each building block at, which its reading records on the block by what its class holds and
never by the format it is written in: a class one of whose operations has a body is at tactics, DDD's code fidelity, and
a class with no bodies is at the model. A rule only the tactics fidelity holds leaves a block at the model out, since a
class with no bodies has no code for it to judge."""

from expects import equal, expect, have_len
from mamba import before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.ddd.rules import BY_SLUG
from cdd_guidance.practices.ddd.rules.rule_examples import ddd_fixture, violations_for_ddd_rule

# An entity whose public derive operation should be private, first with no body, then with one.
_WITHOUT_BODIES = '# <<Entity>>\nclass Cart:\n    def derive_total(self) -> int:\n        """The total of the cart\'s lines."""\n'
_WITH_A_BODY = "# <<Entity>>\nclass Cart:\n    def derive_total(self) -> int:\n        return 0\n"


def _read_at(source: str) -> str:
    """The fidelity the building block read from source answers."""
    blocks = [node for node in ddd_fixture({"cart.py": source}).context.nodes() if node.name == "Cart" and node.practice.key == "ddd"]
    return blocks[0].fidelity_read_at


with description("the fidelity DDD reads a building block at") as self:
    with context("whose class has an operation with a body"):
        with it("should be tactics"):
            expect(_read_at(_WITH_A_BODY)).to(equal("tactics"))

        with it("should be judged by a rule only tactics holds"):
            expect(violations_for_ddd_rule(BY_SLUG["private-method-naming"], _WITH_A_BODY, class_name="Cart")).to(have_len(1))

    with context("whose class has no bodies"):
        with before.all:
            self.source = _WITHOUT_BODIES

        with it("should be the model"):
            expect(_read_at(self.source)).to(equal("model"))

        with it("should be left out by a rule only tactics holds"):
            expect(violations_for_ddd_rule(BY_SLUG["private-method-naming"], self.source, class_name="Cart")).to(equal([]))
