"""Graph membership and relationships — internal to PracticeGraph."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
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
    MANAGES = "manages"
    SCOPES = "scopes"
    SCOPED_BY = "scopedBy"
    USES = "uses"
    DEMONSTRATES = "demonstrates"
    DESCRIBES = "describes"
    NAMES_STATE = "namesState"
    OBSERVES = "observes"
    USED_BY = "usedBy"


@dataclass(frozen=True)
class GraphRelationship:
    """Explicit edge: from — kind — to (by registered node id)."""

    from_id: str
    kind: str
    to_id: str


_GRAPH: Optional["PracticeGraph"] = None


class GraphNodeMixin:
    """Mixed into practice model types. Public surface stays the domain type."""

    _graph: Optional["PracticeGraph"] = None
    _node_id: str = ""
    practice: str = ""

    def _bind_graph(self, graph: "PracticeGraph", node_id: str) -> None:
        self._graph = graph
        self._node_id = node_id

    @property
    def graph(self) -> "PracticeGraph":
        if self._graph is None:
            raise RuntimeError(f"{type(self).__name__} is not registered on a PracticeGraph")
        return self._graph

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def used_by(self) -> List["GraphNodeMixin"]:
        return self.graph.incoming_nodes(self, Kind.USED_BY)

    def related(
        self,
        kind: str,
        *,
        direction: str = "out",
    ) -> List["GraphNodeMixin"]:
        if direction == "out":
            return self.graph.outgoing_nodes(self, kind)
        if direction == "in":
            return self.graph.incoming_nodes(self, kind)
        raise ValueError("direction must be 'out' or 'in'")

    def relate(self, kind: str, to: "GraphNodeMixin") -> GraphRelationship:
        return self.graph.relate(self, kind, to)


def bind_graph_registry(graph: "PracticeGraph") -> None:
    global _GRAPH
    _GRAPH = graph
