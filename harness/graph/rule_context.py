"""Shared context for graph rule checks: the practice being checked and graph helpers.

Rules read what the loader parsed through each node: ``node.model`` is the parsed object, ``node.get_fact`` its saved facts.
"""

from __future__ import annotations

from pathlib import Path


class RuleCheckContext:
    """The practice one load checks, and the folder its source was read from."""

    def __init__(self, practice, source_root: Path | None) -> None:
        self.practice = practice
        self.source_root = source_root

    def child_count(self, node, edge_kinds: tuple[str, ...]) -> int:
        count = 0
        for kind in edge_kinds:
            for edge in self.practice.edges.get(kind, []):
                if edge.parent is node:
                    count += 1
        return count

    def children(self, node, edge_kind: str) -> list:
        return [
            edge.child
            for edge in self.practice.edges.get(edge_kind, [])
            if edge.parent is node
        ]

    def node_data(self, node) -> dict:
        """Every fact the node records: its parsed object's saved attributes and the loader's own facts."""
        return node.facts

    def step_keyword(self, node) -> str:
        data = self.node_data(node)
        if data.get("keyword"):
            return str(data["keyword"])
        name = (node.name or "").strip()
        for prefix in ("Given", "When", "Then", "And", "But"):
            if name.casefold().startswith(prefix.casefold() + " "):
                return prefix
        return ""

    def step_text(self, node) -> str:
        data = self.node_data(node)
        if data.get("text"):
            return str(data["text"])
        name = (node.name or "").strip()
        for prefix in ("Given", "When", "Then", "And", "But"):
            if name.casefold().startswith(prefix.casefold() + " "):
                return name[len(prefix) :].strip()
        return name

    def scenario_outline(self, node) -> bool:
        return bool(self.node_data(node).get("is_outline"))

    def scenario_evidence(self, node) -> list[str]:
        raw = self.node_data(node).get("evidence")
        return [str(item) for item in raw] if isinstance(raw, list) else []
