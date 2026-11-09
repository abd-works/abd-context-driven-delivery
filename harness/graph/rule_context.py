"""Shared context for graph rule checks: the practice being checked and graph helpers.

A node is the object its practice parsed, so rules read its measurements from it; ``node.get_fact`` reads its saved facts,
which is all a node read back from graph.json holds.
"""

from __future__ import annotations

from pathlib import Path


class RuleCheckContext:
    """The practice one load checks, the graph that holds it, and the folder its source was read from."""

    def __init__(self, practice, source_root: Path | None) -> None:
        self.practice = practice
        self.graph = practice.reading.graph
        self.source_root = source_root
        self._indexes: dict[type, object] = {}

    def index(self, kind: type):
        """The index of kind over the checked practice, such as every class by name: made from this context the first
        time a rule asks, then kept, so the rules of one check share it instead of each rebuilding it."""
        if kind not in self._indexes:
            self._indexes[kind] = kind(self)
        return self._indexes[kind]

    def targets(self, node, kind: str) -> list:
        """The nodes an edge of kind leads to from node."""
        return [edge.child for edge in self.graph.edges_from(kind, node)]

    def nodes(self, type: str | None = None) -> list:
        """The checked practice's nodes, or only those of type."""
        return self.practice.reading.in_graph.nodes(type)

    def edges(self, kind: str) -> list:
        """The checked practice's edges of kind."""
        return self.practice.reading.in_graph.edges(kind)

    def node(self, node_id: str):
        """The node called node_id in the graph; none when no practice holds one."""
        return self.graph.node(node_id)

    def child_count(self, node, edge_kinds: tuple[str, ...]) -> int:
        return sum(1 for kind in edge_kinds for edge in self.edges(kind) if edge.parent is node)

    def children(self, node, edge_kind: str) -> list:
        return [edge.child for edge in self.edges(edge_kind) if edge.parent is node]

    def node_data(self, node) -> dict:
        """Every fact the node records: its parsed object's saved attributes and the loader's own facts."""
        return node.facts

    def scenario_outline(self, node) -> bool:
        return bool(self.node_data(node).get("is_outline"))

    def scenario_evidence(self, node) -> list[str]:
        raw = self.node_data(node).get("evidence")
        return [str(item) for item in raw] if isinstance(raw, list) else []
