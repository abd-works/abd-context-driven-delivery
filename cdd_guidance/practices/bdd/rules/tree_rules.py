"""BDD sketch / spec tree rules."""

from __future__ import annotations

import re

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_INTERNAL_SUBJECT = re.compile(
    r"\b(Manager|Runner|Hub|Service|Controller|Handler|Helper|SessionLog|ToolsetRunner|"
    r"Factory|Builder|Impl|Internal)\b"
)
_WHEN_PREFIX = re.compile(r"^\s*when\b", re.I)


class DescribeSubjectNotInternal(PracticeGraphRule):
    slug = "describe-is-subject-not-internal"
    requires_judge = True
    node_types = ("Description", "Context")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        name = (node.name or "").strip()
        if _INTERNAL_SUBJECT.search(name):
            return [Finding(node, f"Describe/context {name!r} names an internal type, not a domain subject.")]
        return []


class StateNotWhen(PracticeGraphRule):
    slug = "state-not-when"
    node_types = ("Context",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        name = (node.name or "").strip()
        if _WHEN_PREFIX.match(name):
            return [Finding(node, f"Nested context {name!r} must not start with 'when'; use 'that' or 'with'.")]
        return []


class OneAssertionPerTest(PracticeGraphRule):
    slug = "one-assertion-per-test"
    node_types = ("Observation",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        count = node.get_fact("expect_count", 0)
        if count > 1:
            return [Finding(node, f"Observation {node.name!r} has {count} expects; use one outcome per it.")]
        return []


class NoImplementation(PracticeGraphRule):
    """A behavior-fidelity block holds signatures only. A finished spec (``developed``) has replaced every signature
    with its test body, so its blocks are not judged: the read keeps on each block whether its spec is finished
    (``in_developed_spec``)."""

    slug = "no-implementation"
    node_types = ("Observation", "Context")

    def check_practice(self, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"{node.type} {node.name!r} at behavior fidelity must not contain tests or imports.")
            for kind in self.node_types
            for node in context.nodes(kind)
            if not node.get_fact("in_developed_spec") and node.get_fact("has_implementation")
        ]
