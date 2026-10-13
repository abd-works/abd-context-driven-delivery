"""A graph rule checks one loaded node using the practice model where possible."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.graph.rule_context import RuleCheckContext


class PracticeGraphRule:
    slug = ""
    node_types: tuple[str, ...] = ()

    def check(self, node, context: "RuleCheckContext") -> list[str]:
        return []

    def applies_to(self, node_type: str) -> bool:
        return node_type in self.node_types
