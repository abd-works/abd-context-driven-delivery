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
from harness.graph.graph import PracticeGraph

# Five parameters, over the three limit-operation-parameters allows.
_OVER_LIMIT = """
class Order:
    def place(self, customer, address, items, discount, note):
        pass
"""


with description("rule violations a practice's graph finds on its nodes") as self:
    with context("with a class whose operation takes too many parameters"):
        with before.each:
            self.handed_again = []
            apply_rules = PracticeGraph.apply_rules

            def apply_and_note(practice, slug, rows):
                self.handed_again.extend(rows)
                apply_rules(practice, slug, rows)

            PracticeGraph.apply_rules = apply_and_note
            try:
                self.practice, _ = practice_from_source(_OVER_LIMIT)
            finally:
                PracticeGraph.apply_rules = apply_rules

        with it("should keep the violation on the operation's node"):
            slugs = [slug for nodes in self.practice.nodes.values() for node in nodes for slug, _ in node.rules.violations]
            expect(slugs).to(contain("limit-operation-parameters"))

        # A violation recorded on its node and then handed to the practice again counts twice unless something removes the copy.
        with it("should record each violation once, without handing it to the practice again"):
            expect(self.handed_again).to(equal([]))
