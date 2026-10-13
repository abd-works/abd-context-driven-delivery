"""A graph rule checks one loaded node against source text."""

from __future__ import annotations


class PracticeGraphRule:
    slug = ""
    node_types: tuple[str, ...] = ()

    def check(self, node, text: str) -> list[str]:
        return []

    def applies_to(self, node_type: str) -> bool:
        return node_type in self.node_types
