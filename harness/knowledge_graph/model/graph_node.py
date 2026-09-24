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


class NodeWalk:
    """Walk ownership and incident edges from this node."""

    def children(self) -> List["Node"]:
        owned = self.related(Kind.OWNS)
        return owned if owned else self.related()

    def ancestors(self) -> List["Node"]:
        found: List[Node] = []
        current: Node = self
        for _ in range(16):
            parents = current.related(Kind.BELONGS_TO) or current.related(
                Kind.OWNS, direction="in"
            )
            if not parents:
                break
            current = parents[0]
            found.append(current)
        return found

    def descendants(self) -> List["Node"]:
        found: List[Node] = []
        stack = list(self.children())
        seen = {self.node_id}
        while stack:
            child = stack.pop()
            if child.node_id in seen:
                continue
            seen.add(child.node_id)
            found.append(child)
            stack.extend(child.children())
        return found

    def incident(self) -> List["Node"]:
        return self.related() + self.related(direction="in")

    def has_kind(self, kinds: list[str]) -> bool:
        names = set(kinds)
        return any(edge.kind in names for edge in self.graph.edges_at(self))

    def matches_source(self, file: str, line: int) -> bool:
        src = getattr(self, "source", None)
        node_file = str(getattr(src, "file", "") or "").replace("\\", "/")
        if not node_file or line <= 0:
            return False
        hit = file.replace("\\", "/")
        if not (
            node_file.endswith(hit)
            or hit.endswith(node_file)
            or node_file.split("/")[-1] == hit.split("/")[-1]
        ):
            return False
        start = int(getattr(src, "line", 0) or 0)
        end = int(getattr(src, "end_line", 0) or start)
        if start <= 0:
            return False
        return start <= line <= max(end, start)

    def owner_class(self):
        for kind in (Kind.BELONGS_TO, Kind.OWNS):
            for other in self.related(kind):
                if other.semantic_type() == "OoadClass":
                    return other
        for other in self.used_by:
            if other.semantic_type() == "OoadClass":
                return other
        return None


class NodeRelations:
    """Record and read this node's relationships."""

    def relate(self, kind: str, to: "Node") -> Relationship:
        return self.graph.relate(Relationship(kind, self, to))

    def related(self, kind: Optional[str] = None, *, direction: str = "out") -> List["Node"]:
        if direction == "out":
            return self._unique(
                [
                    edge.to_node
                    for edge in self.graph.edges_from(self)
                    if kind is None or edge.kind == kind
                ]
            )
        if direction != "in":
            raise ValueError("direction must be 'out' or 'in'")
        nodes: List[Node] = []
        if kind is None or kind == Kind.USED_BY:
            for source_id in self.graph.users_of(self):
                nodes.append(self.graph.nodes[source_id])
        if kind not in (None, Kind.USED_BY):
            nodes.extend(
                edge.from_node
                for edge in self.graph.edges_to(self)
                if edge.kind == kind
            )
        elif kind is None:
            nodes.extend(edge.from_node for edge in self.graph.edges_to(self))
        return self._unique(nodes)

    def outgoing(self, kind: Optional[str] = None) -> List[tuple]:
        return [
            (edge.kind, edge.to_node)
            for edge in self.graph.edges_from(self)
            if kind is None or edge.kind == kind
        ]

    def invoked_operations(self, *, depth: int = 3) -> List["Node"]:
        self._invoke_found = []
        self._invoke_seen: set[str] = set()
        self._invoke_path: set[str] = set()
        self._walk_invokes(self, depth)
        return self._invoke_found

    def _walk_invokes(self, op: "Node", remaining: int) -> None:
        if remaining <= 0 or op.node_id in self._invoke_path:
            return
        self._invoke_path.add(op.node_id)
        for callee in op.related(Kind.INVOKES):
            if callee.semantic_type() != "Operation":
                continue
            if callee.node_id in self._invoke_seen:
                continue
            self._invoke_seen.add(callee.node_id)
            self._invoke_found.append(callee)
            self._walk_invokes(callee, remaining - 1)
        self._invoke_path.discard(op.node_id)

    def _unique(self, nodes: List["Node"]) -> List["Node"]:
        seen: set[str] = set()
        out: List[Node] = []
        for node in nodes:
            if node.node_id in seen:
                continue
            seen.add(node.node_id)
            out.append(node)
        return out


class NodeView:
    """Hierarchy and DOT rendering for this node."""

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


class Node(NodeWalk, NodeRelations, NodeView):
    """Mixed into live Epic, Module, OoadClass, … — wrap or extend, do not scrape."""

    _graph: Optional["PracticeGraph"] = None
    _node_id: str = ""
    practice: str = ""
    source = None

    def semantic_type(self) -> str:
        return getattr(type(self), "_semantic_type_name", type(self).__name__)

    def slug(self, name: str) -> str:
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
            owners = self._module_owners()
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

    def _module_owners(self) -> List["Node"]:
        owners = [
            n for n in self.related(Kind.BELONGS_TO) if n.semantic_type() == "Module"
        ]
        if owners:
            return owners
        owners = [
            n
            for n in self.related(Kind.OWNS, direction="in")
            if n.semantic_type() == "Module"
        ]
        if owners:
            return owners
        for parent in self.related(Kind.BELONGS_TO):
            nested = parent.home_module
            if nested is not None:
                return [nested]
        return []

    @property
    def rules(self) -> "NodeRules":
        from .node_rules import NodeRules

        return NodeRules(self)


GraphNodeMixin = Node
