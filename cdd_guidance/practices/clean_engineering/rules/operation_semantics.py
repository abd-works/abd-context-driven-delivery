"""Operation rules about responsibilities, errors, and state-change contracts."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

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

# A route registrar wires one route or a group of routes (`registerChoosePlanRoute`, `registerSelfCareRoutes`).
_ROUTE_REGISTRAR = re.compile(r"^register\w+Routes?$")


class KeepOperationsSingleResponsibility(ProductionCodeRule):
    """Flag operations that mix I/O-style calls with domain calculation in one body."""

    slug = "keep-operations-single-responsibility"
    # Requires a judge: whether an operation does two jobs is read from what its calls are for; the check matches the names it calls.
    requires_judge = True
    node_types = ("Operation",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if node.name.endswith("Routes") and node.name.startswith("create"):
            return []
        if _ROUTE_REGISTRAR.match(node.name) or node.name in _LIFECYCLE_WITH_VALIDATION:
            return []
        if node.get_fact("io_and_domain"):
            return [Finding(node, f"Operation '{node.name}' mixes I/O-style calls with domain calculation; split responsibilities.")]
        if node.get_fact("io_and_domain_callees"):
            return [Finding(node, f"Operation '{node.name}' delegates to both I/O and domain helpers; give it one job.")]
        return []


class ErrorsOutOfExistence(ProductionCodeRule):
    """Reports a builtin failure raised on an empty or missing value, and says which of the rule's three cases asks
    for which answer: nothing there answers empty, and what cannot be read or done is refused with a failure the
    program names. A raise of a failure the program declares (``raise UnknownPractice(key, known)``,
    ``raise CommitPathsRequiredError()``) is such a named refusal and passes. Which case a raise is in takes reading,
    so the message names all three and never asks only for the quiet answer. A spec helper raises on a missing value
    to fail its example, so only production code is judged."""

    slug = "errors-out-of-existence"
    # Requires a judge: which of the rule's three cases a raise is in is read from what the value is; the check sees only a built-in failure raised on an empty value.
    requires_judge = True
    node_types = ("Operation",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if not node.get_fact("raises_on_empty"):
            return []
        return [
            Finding(
                node,
                f"Operation '{node.name}' raises a built-in failure on an empty or missing value. When nothing is there, answer an empty result; "
                "when what is there cannot be read, or the call cannot do what was asked, refuse with a failure the program declares and names.",
            )
        ]


class StateChangeReturnsRecordOrNamedFailure(ProductionCodeRule):
    """Mutating operations should return the record or an explicit outcome."""

    slug = "state-change-returns-record-or-named-failure"
    # Requires a judge: whether an operation changes state a caller needs back is read from what it changes; the check matches assignments and returns.
    requires_judge = True
    node_types = ("Operation",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if not node.get_fact("mutates_without_record"):
            return []
        return [Finding(node, f"Operation '{node.name}' mutates state but does not return the record or a named failure.")]


class DomainExceptionCarriesContext(ProductionCodeRule):
    """A failure raised with no message must name the rule it rejects. A failure the program declares, whose own
    constructor gives its base the message, carries that context however it is raised; the build keeps whether it does on
    the operation (``exception_gives_own_message``)."""

    slug = "domain-exception-carries-context"
    node_types = ("Operation",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        exception = node.get_fact("exception_without_message", "")
        if exception and not node.get_fact("exception_gives_own_message"):
            return [Finding(node, f"Operation '{node.name}' raises {exception} without context; name the rejected rule.")]
        if node.get_fact("generic_exception_message"):
            return [Finding(node, f"Operation '{node.name}' raises a generic message; carry domain context.")]
        return []


SEMANTIC_RULES: tuple[PracticeGraphRule, ...] = (
    KeepOperationsSingleResponsibility(),
    ErrorsOutOfExistence(),
    StateChangeReturnsRecordOrNamedFailure(),
    DomainExceptionCarriesContext(),
)
