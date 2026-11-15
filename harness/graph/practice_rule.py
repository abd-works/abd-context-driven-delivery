"""A graph rule checks one loaded node using the practice model where possible."""

from __future__ import annotations

import copy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.graph.rule_context import RuleCheckContext


class PracticeGraphRule:
    slug = ""
    node_types: tuple[str, ...] = ()

    def check(self, node, context: "RuleCheckContext") -> list[str]:
        return []

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        """Optional whole-practice pass. Returns (node_id, message) pairs."""
        return []

    def applies_to(self, node_type: str) -> bool:
        return node_type in self.node_types


class SharedPracticeGraphRule(PracticeGraphRule):
    """One rule an overlay checks on several practices' nodes, such as TDD's one-outcome-per-test on BDD observations
    and Stories Thens. It lives once, in the overlay's ``rules`` package; each practice runs a copy bound to its own
    node types. Its check reads only facts every practice it names records on its nodes."""

    node_types_by_practice: dict[type, tuple[str, ...]] = {}
    """Each practice's class to the node types the rule checks there."""

    def for_practice(self, practice) -> PracticeGraphRule | None:
        """A copy whose node types are practice's, matched by its class; none for a practice it does not name."""
        node_types = next(
            (types for practice_class, types in self.node_types_by_practice.items() if isinstance(practice, practice_class)),
            None,
        )
        if node_types is None:
            return None
        bound = copy.copy(self)
        bound.node_types = node_types
        return bound
