"""Operation rules about responsibilities, errors, and state-change contracts."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_LIFECYCLE_WITH_VALIDATION = frozenset(
    {
        "load",
        "hydrate",
        "update",
        "loadState",
        "postOnboarding",
        "refresh",
        "importStoredPortabilities",
        "exportStoredPortabilities",
    }
)

_ROUTE_REGISTRAR = re.compile(r"^register\w+Route$")


class KeepOperationsSingleResponsibility(PracticeGraphRule):
    """Flag operations that mix I/O-style calls with domain calculation in one body."""

    slug = "keep-operations-single-responsibility"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if node.name.endswith("Routes") and node.name.startswith("create"):
            return []
        if _ROUTE_REGISTRAR.match(node.name) or node.name in _LIFECYCLE_WITH_VALIDATION:
            return []
        if node.get_fact("io_and_domain"):
            return [
                f"Operation '{node.name}' mixes I/O-style calls with domain calculation; split responsibilities."
            ]
        if node.get_fact("io_and_domain_callees"):
            return [f"Operation '{node.name}' delegates to both I/O and domain helpers; give it one job."]
        return []


class ErrorsOutOfExistence(PracticeGraphRule):
    """Ordinary empty/absent cases should not raise."""

    slug = "errors-out-of-existence"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if not node.get_fact("raises_on_empty"):
            return []
        return [f"Operation '{node.name}' raises on an empty or missing value; return a quiet result instead."]


class StateChangeReturnsRecordOrNamedFailure(PracticeGraphRule):
    """Mutating operations should return the record or an explicit outcome."""

    slug = "state-change-returns-record-or-named-failure"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if not node.get_fact("mutates_without_record"):
            return []
        return [f"Operation '{node.name}' mutates state but does not return the record or a named failure."]


class DomainExceptionCarriesContext(PracticeGraphRule):
    slug = "domain-exception-carries-context"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        exception = node.get_fact("exception_without_message", "")
        if exception:
            return [f"Operation '{node.name}' raises {exception} without context; name the rejected rule."]
        if node.get_fact("generic_exception_message"):
            return [f"Operation '{node.name}' raises a generic message; carry domain context."]
        return []


SEMANTIC_RULES: tuple[PracticeGraphRule, ...] = (
    KeepOperationsSingleResponsibility(),
    ErrorsOutOfExistence(),
    StateChangeReturnsRecordOrNamedFailure(),
    DomainExceptionCarriesContext(),
)
