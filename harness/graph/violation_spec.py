"""BDD spec for harness/graph/violation: where a broken rule is marked in its file."""

from types import SimpleNamespace

from expects import equal, expect
from mamba import before, context, description, it

from harness.graph.violation import Finding, NodeViolation


def _rule_on_class_at(start_line: int, end_line: int) -> SimpleNamespace:
    """A rule of a class node in order.py, which a found violation is marked against."""
    node = SimpleNamespace(source=SimpleNamespace(file="src/order.py", start_line=start_line, end_line=end_line))
    return SimpleNamespace(node=node)


# A viewer highlights a violation's lines, so they must be where the rule found the problem.
with description("a broken rule found on a class"):
    with before.each:
        self.found_by = _rule_on_class_at(129, 149)

    with context("that names no lines of its own"):
        with it("should be marked on the class's lines"):
            violation = NodeViolation.at_node(self.found_by, Finding(self.found_by.node, "Class 'Order' has two jobs."))
            expect([violation.line, violation.end_line]).to(equal([129, 149]))

    # prefer-class-operations finds a module helper on the class that uses it; the helper is what moves.
    with context("that names the line of a module helper the class alone uses"):
        with it("should be marked on the helper's line"):
            violation = NodeViolation.at_node(self.found_by, Finding(self.found_by.node, "Module function '_total' (line 115) is only used from 'Order'.", (115, 115)))
            expect([violation.line, violation.end_line]).to(equal([115, 115]))
