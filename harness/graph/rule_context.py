"""Shared context for graph rule checks: the practice being checked and graph helpers.

A node is the object its practice parsed, so rules read its measurements from it; ``node.get_fact`` reads its saved facts,
which is all a node read back from graph.json holds.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from harness.graph.edge import Edge
    from harness.graph.graph import Node
    from harness.guidance.guidance import PracticeGuidance

# An index a rule asks the context for, made from the context once: any class whose constructor takes the context.
Index = TypeVar("Index")


class RuleCheckContext:
    """The practice one load checks, the graph that holds it, and the folder its source was read from."""

    def __init__(self, practice: PracticeGuidance, source_root: Path | None) -> None:
        self.practice = practice
        self.graph = practice.reading.graph
        self.source_root = source_root
        self._indexes: dict[type, object] = {}

    def index(self, kind: type[Index]) -> Index:
        """The index of kind over the checked practice, such as every class by name: made from this context the first
        time a rule asks, then kept, so the rules of one check share it instead of each rebuilding it."""
        if kind not in self._indexes:
            self._indexes[kind] = kind(self)
        return self._indexes[kind]

    def targets(self, node: Node, kind: str) -> list[Node]:
        """The nodes an edge of kind leads to from node."""
        return [edge.child for edge in self.graph.edges.from_parent(kind, node)]

    def held_by(self, node: Node) -> list[Node]:
        """The nodes an edge of any kind leads to from node, but the ``belongsTo`` back-edge to the node holding it: what
        node holds, whatever kind its practice records each under (an operation's parameters under ``hasParameter``)."""
        kinds = [kind for kind in self.practice.reading.in_graph.edge_index.types if kind != "belongsTo"]
        return [target for kind in kinds for target in self.targets(node, kind)]

    def nodes(self, type: str | None = None) -> list[Node]:
        """The checked practice's nodes, or only those of type."""
        return self.practice.reading.in_graph.nodes(type)

    def edges(self, kind: str) -> list[Edge[Node]]:
        """The checked practice's edges of kind."""
        return self.practice.reading.in_graph.edge_index.of(kind)

    def node(self, node_id: str) -> Node | None:
        """The node called node_id in the graph; none when no practice holds one."""
        return self.graph.node(node_id)

    def child_count(self, node: Node, edge_kinds: tuple[str, ...]) -> int:
        return sum(1 for kind in edge_kinds for edge in self.edges(kind) if edge.parent is node)

    def children(self, node: Node, edge_kind: str) -> list[Node]:
        return [edge.child for edge in self.edges(edge_kind) if edge.parent is node]

