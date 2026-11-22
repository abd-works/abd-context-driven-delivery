"""The fidelity BDD reads each spec at, which its reading records on the spec by what the spec holds: a spec whose
observations are still signatures is at behavior, and one whose every observation has its test body is at development.
Its describes, contexts and observations take the spec's fidelity."""

from expects import equal, expect
from mamba import before, context, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.bdd.rules.rule_examples import spec_fixture

_SIGNATURES = '''
from mamba import description, it

with description("a cart"):
    with it("should total zero"):
        # BDD: SIGNATURE
        pass
'''
_DEVELOPED = '''
from expects import equal, expect
from mamba import description, it

with description("a cart"):
    with it("should total zero"):
        expect(Cart().total).to(equal(0))
'''


def _read(source: str) -> dict[str, str]:
    """The fidelity each node read from one spec answers, by the node's type."""
    return {node.type: node.fidelity_read_at for node in spec_fixture(source).practice.reading.in_graph.nodes()}


with description("the fidelity BDD reads a spec at") as self:
    with context("whose observations are still signatures"):
        with before.all:
            self.read = _read(_SIGNATURES)

        with it("should be behavior"):
            expect(self.read["Spec"]).to(equal("behavior"))

        with it("should be behavior for its describe and its observation, which take the spec's fidelity"):
            expect((self.read["Description"], self.read["Observation"])).to(equal(("behavior", "behavior")))

    with context("whose every observation has its test body"):
        with before.all:
            self.read = _read(_DEVELOPED)

        with it("should be development"):
            expect(self.read["Spec"]).to(equal("development"))

        with it("should be development for its observation"):
            expect(self.read["Observation"]).to(equal("development"))
