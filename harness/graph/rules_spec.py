"""BDD spec — rule violations a practice's graph finds and keeps on its nodes."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from expects import contain, equal, expect
from mamba import before, context, description, it

from harness.graph.ce_rule_eval_harness import practice_from_source

# Five parameters, over the three limit-operation-parameters allows.
_OVER_LIMIT = """
class Order:
    def place(self, customer, address, items, discount, note):
        pass
"""


with description("rule violations a practice's graph finds on its nodes") as self:
    with context("with a class whose operation takes too many parameters"):
        with before.each:
            self.practice, _ = practice_from_source(_OVER_LIMIT)
            self.place = next(node for node in self.practice.nodes["Operation"] if node.name == "place")

        with it("should keep the violation on the operation's node"):
            expect(self.place.failed_rules).to(contain("limit-operation-parameters"))

        with it("should record each violation once"):
            hits = [violation for violation in self.place.rules.violations if violation.rule == "limit-operation-parameters"]
            expect(len(hits)).to(equal(1))
