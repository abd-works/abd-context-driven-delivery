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


class DevelopedSpecs:
    """The spec files of one check that are finished tests (``developed``): past behavior fidelity, so the rules that
    keep a behavior sketch free of test bodies leave their blocks alone. Made once per check, from each spec's fact."""

    def __init__(self, context: RuleCheckContext) -> None:
        self._files = {spec.source.file for spec in context.nodes("Spec") if spec.get_fact("developed", False)}

    def holds(self, node: Node) -> bool:
        """True when node was read from a finished spec."""
        return node.source.file in self._files


class NoImplementation(PracticeGraphRule):
    """A behavior-fidelity block holds signatures only. A finished spec has replaced every signature with its test
    body, so its blocks are not judged."""

    slug = "no-implementation"
    node_types = ("Observation", "Context")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if context.index(DevelopedSpecs).holds(node):
            return []
        if node.get_fact("has_implementation"):
            return [f"{node.type} {node.name!r} at behavior fidelity must not contain tests or imports."]
        return []
