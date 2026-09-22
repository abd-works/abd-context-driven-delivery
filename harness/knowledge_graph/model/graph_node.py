"""Graph membership and relationships — Node mixed into live practice types."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .node_rules import NodeRules
    from .practice_graph import PracticeGraph


class Kind:
    """Relationship kinds — Left — kind — Right."""

    OWNS = "owns"
    BELONGS_TO = "belongsTo"
    ASSOCIATES = "associates"
    DEPENDS_ON = "dependsOn"
    HAS_TYPE = "hasType"
    HAS_PARAMETER = "hasParameter"
    RETURNS = "returns"
    INVOKES = "invokes"
    HAS_IDENTITY = "hasIdentity"
    ROOT = "root"
    ACCESSES = "accesses"
    SCOPES = "scopes"
    SCOPED_BY = "scopedBy"
    USES = "uses"
    DEMONSTRATES = "demonstrates"
    DEMONSTRATED_THROUGH = "demonstratedThrough"
    DESCRIBES = "describes"
    NAMES_STATE = "namesState"
    OBSERVES = "observes"
    USED_BY = "usedBy"


class Relationship:
    """Explicit edge: from — kind — to."""

    def __init__(self, kind: str, from_node: "Node", to_node: "Node") -> None:
        self.kind = kind
        self.from_node = from_node
        self.to_node = to_node

    @property
    def from_id(self) -> str:
        return self.from_node.node_id

    @property
    def to_id(self) -> str:
        return self.to_node.node_id


class Node:
    """Mixed into live Epic, Module, OoadClass, … — wrap or extend, do not scrape."""

    _graph: Optional["PracticeGraph"] = None
    _node_id: str = ""
    practice: str = ""

    def semantic_type(self) -> str:
        return getattr(type(self), "_semantic_type_name", type(self).__name__)

    @staticmethod
    def slug(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    def join(self, graph: "PracticeGraph", node_id: Optional[str] = None) -> "Node":
        if node_id is None:
            node_id = graph.id_for(self)
        self._graph = graph
        self._node_id = node_id
        return self

    @property
    def graph(self) -> "PracticeGraph":
        if self._graph is None:
            raise RuntimeError(f"{type(self).__name__} is not registered on a PracticeGraph")
        return self._graph

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def used_by(self) -> List["Node"]:
        return self.related(Kind.USED_BY, direction="in")

    @property
    def home_module(self) -> Optional["Node"]:
        try:
            owners = [
                n
                for n in self.related(Kind.BELONGS_TO)
                if n.semantic_type() == "Module"
            ]
            if not owners:
                owners = [
                    n
                    for n in self.related(Kind.OWNS, direction="in")
                    if n.semantic_type() == "Module"
                ]
            if owners:
                return owners[0]
            error: BaseException = RuntimeError(f"{self.name} has no owning Module")
        except Exception as caught:
            error = caught
        graph = getattr(self, "_graph", None)
        if graph is not None:
            graph.record_partial_failure(f"home_module {getattr(self, 'name', self.node_id)}", error)
            return None
        raise error

    @property
    def rules(self) -> "NodeRules":
        from .node_rules import NodeRules

        return NodeRules(self)

    @property
    def hierarchy(self) -> List[tuple]:
        from .dot_graph import walk_hierarchy

        return list(walk_hierarchy(self))

    @property
    def hierarchy_text(self) -> str:
        from .dot_graph import hierarchy_text as render_hierarchy

        return render_hierarchy(self)

    @property
    def dot_graph(self) -> str:
        from .dot_graph import dot_graph_from_node

        return dot_graph_from_node(self)

    def relate(self, kind: str, to: "Node") -> Relationship:
        return self.graph.relate(Relationship(kind, self, to))

    def related(self, kind: Optional[str] = None, *, direction: str = "out") -> List["Node"]:
        if direction == "out":
            nodes = [
                edge.to_node
                for edge in self.graph.relationships
                if edge.from_id == self.node_id and (kind is None or edge.kind == kind)
            ]
            return _dedupe_nodes(nodes)
        if direction == "in":
            nodes: List[Node] = []
            if kind is None or kind == Kind.USED_BY:
                for source_id in self.graph._used_by.get(self.node_id, []):
                    nodes.append(self.graph.nodes[source_id])
            if kind not in (None, Kind.USED_BY):
                nodes.extend(
                    edge.from_node
                    for edge in self.graph.relationships
                    if edge.to_id == self.node_id and edge.kind == kind
                )
            elif kind is None:
                nodes.extend(
                    edge.from_node
                    for edge in self.graph.relationships
                    if edge.to_id == self.node_id
                )
            return _dedupe_nodes(nodes)
        raise ValueError("direction must be 'out' or 'in'")

    def outgoing(self, kind: Optional[str] = None) -> List[tuple]:
        return [
            (edge.kind, edge.to_node)
            for edge in self.graph.relationships
            if edge.from_id == self.node_id and (kind is None or edge.kind == kind)
        ]

    def invoked_operations(self, *, depth: int = 3) -> List["Node"]:
        found: List[Node] = []
        seen: set[str] = set()

        def walk(op: Node, remaining: int, path: set[str]) -> None:
            if remaining <= 0 or op.node_id in path:
                return
            nxt = path | {op.node_id}
            for callee in op.related(Kind.INVOKES):
                if callee.semantic_type() != "Operation":
                    continue
                if callee.node_id in seen:
                    continue
                seen.add(callee.node_id)
                found.append(callee)
                walk(callee, remaining - 1, nxt)

        walk(self, depth, set())
        return found


def _dedupe_nodes(nodes: List[Node]) -> List[Node]:
    seen: set[str] = set()
    out: List[Node] = []
    for node in nodes:
        if node.node_id in seen:
            continue
        seen.add(node.node_id)
        out.append(node)
    return out
