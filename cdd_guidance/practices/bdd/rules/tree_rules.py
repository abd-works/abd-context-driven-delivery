"""BDD sketch / spec tree rules."""

from __future__ import annotations

import re

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

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
    node_types = ("Description", "Context")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        name = (node.name or "").strip()
        if _INTERNAL_SUBJECT.search(name):
            return [f"Describe/context {name!r} names an internal type, not a domain subject."]
        return []


class StateNotWhen(PracticeGraphRule):
    slug = "state-not-when"
    node_types = ("Context",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        name = (node.name or "").strip()
        if _WHEN_PREFIX.match(name):
            return [f"Nested context {name!r} must not start with 'when'; use 'that' or 'with'."]
        return []


class OneAssertionPerTest(PracticeGraphRule):
    slug = "one-assertion-per-test"
    node_types = ("Observation",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        count = node.get_fact("expect_count", 0)
        if count > 1:
            return [f"Observation {node.name!r} has {count} expects; use one outcome per it."]
        return []


class NoImplementation(PracticeGraphRule):
    """A behavior-fidelity block holds signatures only. A finished spec (``developed``) has replaced every signature
    with its test body, so its blocks are not judged. Judged over the whole practice, so each spec's fact is read once
    for all its blocks."""

    slug = "no-implementation"
    node_types = ("Observation", "Context")

    def check_practice(self, context: RuleCheckContext) -> list[tuple[str, str]]:
        finished = {spec.source.file for spec in context.nodes("Spec") if spec.get_fact("developed", False)}
        return [
            (node.node_id, f"{node.type} {node.name!r} at behavior fidelity must not contain tests or imports.")
            for kind in self.node_types
            for node in context.nodes(kind)
            if node.source.file not in finished and node.get_fact("has_implementation")
        ]
