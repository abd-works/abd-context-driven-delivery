"""BDD sketch / spec tree rules."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_INTERNAL_SUBJECT = re.compile(
    r"\b(Manager|Runner|Hub|Service|Controller|Handler|Helper|SessionLog|ToolsetRunner|"
    r"Factory|Builder|Impl|Internal)\b"
)
_WHEN_PREFIX = re.compile(r"^\s*when\b", re.I)


class DescribeSubjectNotInternal(PracticeGraphRule):
    slug = "describe-is-subject-not-internal"
    node_types = ("Description", "Context")

    def check(self, node, context) -> list[str]:
        name = (node.name or "").strip()
        if _INTERNAL_SUBJECT.search(name):
            return [f"Describe/context {name!r} names an internal type, not a domain subject."]
        return []


class StateNotWhen(PracticeGraphRule):
    slug = "state-not-when"
    node_types = ("Context",)

    def check(self, node, context) -> list[str]:
        name = (node.name or "").strip()
        if _WHEN_PREFIX.match(name):
            return [f"Nested context {name!r} must not start with 'when'; use 'that' or 'with'."]
        return []


class OneAssertionPerTest(PracticeGraphRule):
    slug = "one-assertion-per-test"
    node_types = ("Observation",)

    def check(self, node, context) -> list[str]:
        count = node.get_fact("expect_count", 0)
        if count > 1:
            return [f"Observation {node.name!r} has {count} expects; use one outcome per it."]
        return []


class NoImplementation(PracticeGraphRule):
    slug = "no-implementation"
    node_types = ("Observation", "Context")

    def check(self, node, context) -> list[str]:
        if node.get_fact("has_implementation"):
            return [f"{node.type} {node.name!r} at behavior fidelity must not contain tests or imports."]
        return []
