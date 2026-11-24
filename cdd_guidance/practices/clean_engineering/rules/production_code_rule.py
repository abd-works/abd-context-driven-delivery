"""The rule shape that judges only production code. A spec or a test fixture catches every exception on purpose, raises on
an empty value to prove a guard, and builds its collaborators inline; judging it by production rules buries the real
findings under hits nobody will fix. Which files are test code, the model's ``production_code`` module says."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.reading.code_read import CODE_FIDELITY

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext
    from harness.graph.violation import Finding


class ProductionCodeRule(PracticeGraphRule):
    """A rule about production code: it passes every node read from a spec, a test, or test support. Every Clean
    Engineering rule that judges one node at a time derives from it; specs are the BDD practice's to judge. A rule that
    judges the whole practice at once reads only the facts the build compared across the graph, which it records on
    production code alone (``model/compared_facts.py``)."""

    # True for a rule the practice's document states at the code fidelity and at no other: it judges bodies, so it
    # leaves out every node that is not read at the code fidelity, such as a class whose operations have no bodies yet.
    code_fidelity_only = False

    def check(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        """Judge node unless it is test code, as the project tells it through the reading of the node's practice."""
        if node.practice.reading.test_code.is_test_code(node.source.file):
            return []
        if self.code_fidelity_only and not self.is_judged(node):
            return []
        return self.check_production(node, context)

    def is_judged(self, node: "Node") -> bool:
        """Whether a rule of the code fidelity alone judges node: a node read at the code fidelity, such as a class one
        of whose operations has a body."""
        return node.is_read_at(CODE_FIDELITY)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        return []
