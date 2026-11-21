"""The rule shape that judges only production code. A spec or a test fixture catches every exception on purpose, raises on
an empty value to prove a guard, and builds its collaborators inline; judging it by production rules buries the real
findings under hits nobody will fix. Which files are test code, the model's ``production_code`` module says."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.source_code import is_test_code

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext
    from harness.graph.violation import Finding


class ProductionCodeRule(PracticeGraphRule):
    """A rule about production code: it passes every node read from a spec, a test, or test support. Every Clean
    Engineering rule that judges one node at a time derives from it; specs are the BDD practice's to judge. A rule that
    judges the whole practice at once reads only the facts the build compared across the graph, which it records on
    production code alone (``model/compared_facts.py``)."""

    def check(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if is_test_code(node.source.file):
            return []
        return self.check_production(node, context)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        return []
