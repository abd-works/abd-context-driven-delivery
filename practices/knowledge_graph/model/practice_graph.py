"""PracticeGraph — one navigable object model across practices."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Type, TypeVar

from practices.stories.model.nodes import Epic

from .graph_node import GraphNodeMixin, GraphRelationship, Kind, bind_graph_registry
from .nodes import GraphDescription, GraphModule, slug

T = TypeVar("T", bound=GraphNodeMixin)


class PracticeGraph:
    """Public API reads like an object model; edges live in ``relationships``."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.story_map = None
        self.ce_model = None
        self.epics: Dict[str, Epic] = {}
        self.modules: Dict[str, GraphModule] = {}
        self.descriptions: Dict[str, GraphDescription] = {}
        self.nodes: Dict[str, GraphNodeMixin] = {}
        self.relationships: List[GraphRelationship] = []
        self._used_by: Dict[str, List[str]] = {}
        bind_graph_registry(self)

    @classmethod
    def load(cls, path: str | Path) -> "PracticeGraph":
        from .loader import load_practice_graph

        return load_practice_graph(path)

    # -- registration --------------------------------------------------------

    def register(self, node: GraphNodeMixin, node_id: Optional[str] = None) -> GraphNodeMixin:
        if node_id is None:
            node_id = self._make_id(node)
        node._bind_graph(self, node_id)
        self.nodes[node_id] = node
        return node

    def _make_id(self, node: GraphNodeMixin) -> str:
        practice = getattr(node, "practice", "node")
        semantic = getattr(node, "_semantic_type_name", type(node).__name__)
        return f"{practice}:{semantic}:{slug(node.name)}:{id(node)}"

    def index_epic(self, epic: Epic) -> None:
        self.epics[slug(epic.name)] = epic

    def index_module(self, module: GraphModule) -> None:
        self.modules[slug(module.name)] = module

    def index_description(self, description: GraphDescription) -> None:
        self.descriptions[slug(description.name)] = description

    # -- relationships -------------------------------------------------------

    def relate(
        self,
        from_node: GraphNodeMixin,
        kind: str,
        to_node: GraphNodeMixin,
        *,
        mirror_used_by: bool = True,
    ) -> GraphRelationship:
        edge = GraphRelationship(
            from_id=from_node.node_id,
            kind=kind,
            to_id=to_node.node_id,
        )
        self.relationships.append(edge)
        if mirror_used_by:
            self._used_by.setdefault(to_node.node_id, []).append(from_node.node_id)
        return edge

    def outgoing(
        self,
        node: GraphNodeMixin,
        kind: Optional[str] = None,
    ) -> List[Tuple[str, GraphNodeMixin]]:
        pairs: List[Tuple[str, GraphNodeMixin]] = []
        for edge in self.relationships:
            if edge.from_id != node.node_id:
                continue
            if kind is not None and edge.kind != kind:
                continue
            pairs.append((edge.kind, self.nodes[edge.to_id]))
        return pairs

    def incoming(
        self,
        node: GraphNodeMixin,
        kind: Optional[str] = None,
    ) -> List[Tuple[str, GraphNodeMixin]]:
        pairs: List[Tuple[str, GraphNodeMixin]] = []
        for edge in self.relationships:
            if edge.to_id != node.node_id:
                continue
            if kind is not None and edge.kind != kind:
                continue
            pairs.append((edge.kind, self.nodes[edge.from_id]))
        return pairs

    def outgoing_nodes(
        self,
        node: GraphNodeMixin,
        kind: Optional[str] = None,
    ) -> List[GraphNodeMixin]:
        return [target for _, target in self.outgoing(node, kind)]

    def incoming_nodes(
        self,
        node: GraphNodeMixin,
        kind: Optional[str] = None,
    ) -> List[GraphNodeMixin]:
        result: List[GraphNodeMixin] = []
        if kind is None or kind == Kind.USED_BY:
            for source_id in self._used_by.get(node.node_id, []):
                result.append(self.nodes[source_id])
        if kind not in (None, Kind.USED_BY):
            result.extend([source for _, source in self.incoming(node, kind)])
        elif kind is None:
            result.extend([source for _, source in self.incoming(node, None)])
        return _dedupe_nodes(result)

    def find_class(self, name: str) -> Optional[GraphNodeMixin]:
        from practices.clean_engineering.model.base_class_model import OoadClass

        from .nodes import GraphClass

        plain = name.strip()
        for node in self.nodes.values():
            if isinstance(node, (GraphClass, OoadClass)) and node.name == plain:
                return node
        return None

    def find_operation(self, class_name: str, operation_name: str) -> Optional[GraphNodeMixin]:
        from .nodes import GraphOperation

        cls = self.find_class(class_name)
        if cls is None:
            return None
        for node in self.outgoing_nodes(cls, Kind.OWNS):
            if isinstance(node, GraphOperation) and node.name == operation_name:
                return node
        return None

    def nodes_of_type(self, cls: Type[T]) -> List[T]:
        return [n for n in self.nodes.values() if isinstance(n, cls)]


def _dedupe_nodes(nodes: Iterable[GraphNodeMixin]) -> List[GraphNodeMixin]:
    seen: set[str] = set()
    out: List[GraphNodeMixin] = []
    for node in nodes:
        if node.node_id in seen:
            continue
        seen.add(node.node_id)
        out.append(node)
    return out
