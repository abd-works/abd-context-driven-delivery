"""Shared context for graph rule checks: the practice being checked and graph helpers.

A node is the object its practice parsed, so rules read its measurements from it; ``node.get_fact`` reads its saved facts,
which is all a node read back from graph.json holds.
"""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.graph.edge import Edge
    from harness.graph.graph import Node
    from harness.guidance.guidance import PracticeGuidance


class RuleCheckContext:
    """The practice one load checks and the graph that holds it."""

    def __init__(self, practice: PracticeGuidance) -> None:
        self.practice = practice
        self.graph = practice.reading.graph

    @cached_property
    def read_node_types(self) -> frozenset[str]:
        """Every node type the schemas of the practices open in the graph name: the types a node this load read can be.
        A relationship to a type no open practice names, such as a step's invokes of an operation while Clean
        Engineering is off, leads to nothing the graph can hold."""
        practices = self.graph.practices.opened.values()
        return frozenset(node_type for practice in practices for node_type in practice.reading.in_graph.rule_run.schema.types)

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
