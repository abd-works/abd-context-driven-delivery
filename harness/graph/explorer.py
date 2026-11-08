"""What the graph's tools answer with besides the graph's own objects: a node's place in the explorer tree, a node's
source, and the nodes a filter matches. Each is a NodeAnswer: it holds the node it describes and reads its data from
it, so an application outside Python reads the same objects the agent does. A node's rules are its own GraphRulesCollection, and each rule's
violations are Violations, so neither has a copy here."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from harness.graph.graph_rules_collection import GraphRule
from harness.installation.data_class import SourceFile, data_field

if TYPE_CHECKING:
    from harness.graph.graph import Filter, Graph, Node
    from harness.guidance.guidance import PracticeGuidance


class GraphLoaded:
    """What a load did: the saved graph read back, the working copies scanned, or the edited files read."""

    def __init__(self, message: str) -> None:
        self._message = message

    @property
    @data_field
    def message(self) -> str:
        return self._message


class GraphSaved:
    """Where a graph was saved; no path when no folder is loaded."""

    def __init__(self, path: str) -> None:
        self._path = path

    @property
    @data_field
    def path(self) -> str:
        return self._path


class NodeAnswer:
    """A node as a graph tool's answer names it: its id, name, and type, read from the node itself. Every answer about a
    node builds on this one, so each names its node the same way."""

    def __init__(self, node: Node) -> None:
        self._node = node

    @property
    @data_field
    def node_id(self) -> str:
        return self._node.node_id

    @property
    @data_field
    def name(self) -> str:
        return self._node.name

    @property
    @data_field
    def type(self) -> str:
        return self._node.type


class ExplorerEntry(NodeAnswer):
    """One node at one place in the explorer tree, with the entries written below it there. A node sits at many places
    (under its home parent and under every relationship that names it) but only its home place lists its children, and
    a node already on the path to this place lists none, so the place is not the node."""

    def __init__(self, node: Node, children: list | None = None) -> None:
        super().__init__(node)
        self._children = list(children or [])

    @property
    @data_field
    def children(self) -> list:
        """The entries below this one, and last the node's rules when it has any to show."""
        return list(self._children)

    def kept_by(self, wanted: Filter) -> ExplorerEntry | None:
        """This entry with only what the filter keeps below it: a node the filter matches keeps its rules, a practice's
        root always stays, and any other node stays, without its rules, only as the way to an entry kept below it."""
        entries = [kept for child in self._children if isinstance(child, ExplorerEntry) and (kept := child.kept_by(wanted)) is not None]
        rules = [child for child in self._children if not isinstance(child, ExplorerEntry)]
        if self._node.type == "Practice" or wanted.matches(self._node):
            return ExplorerEntry(self._node, [*entries, *rules])
        return ExplorerEntry(self._node, entries) if entries else None


class PracticeInventory:
    """One loaded practice as the explorer's inventory shows it, read from the graph that holds it: how many nodes of
    each type it holds, how many edges, its node types, edge kinds, rules, and explorer tree."""

    def __init__(self, graph: Graph, practice: PracticeGuidance) -> None:
        self._graph = graph
        self._practice = practice

    @property
    @data_field
    def node_counts(self) -> dict[str, int]:
        """How many nodes of each type the practice holds."""
        return {type: len(self._practice.in_graph.nodes(type)) for type in self._practice.in_graph.node_types}

    @property
    @data_field
    def edge_count(self) -> int:
        return len(self._practice.in_graph.edges())

    @property
    @data_field
    def node_types(self) -> list[str]:
        """The node types the practice holds, sorted by name."""
        return sorted(self._practice.in_graph.node_types)

    @property
    @data_field
    def edge_types(self) -> list[str]:
        """The edge kinds the practice holds that a person filters by, in the order the explorer tree shows them."""
        ordered = sorted(self._practice.in_graph.edge_types.values(), key=lambda edge_type: edge_type.order)
        return [edge_type.kind for edge_type in ordered if edge_type.is_offered]

    @property
    @data_field
    def rules(self) -> list[str]:
        """Each rule the practice runs, named ``practice.node.rule`` with the pattern that owns it in front."""
        return self._practice.in_graph.rule_labels

    @property
    @data_field
    def tree(self) -> ExplorerEntry:
        """The explorer tree, from the practice's root."""
        return self._practice.in_graph.root.serialize()


class Overlay:
    """The pattern overlay a folder holds."""

    def __init__(self, overlay: str) -> None:
        self._overlay = overlay

    @property
    @data_field
    def overlay(self) -> str:
        return self._overlay


class FilteredNode(NodeAnswer):
    """One node a filter matches, with the names above and below it and its rules."""

    def __init__(self, node: Node, ancestors: list[str], rules: list[GraphRule]) -> None:
        super().__init__(node)
        self._ancestors = list(ancestors)
        self._rules = list(rules)

    @property
    @data_field
    def practice(self) -> str:
        return self._node.practice.key

    @property
    @data_field
    def ancestors(self) -> list[str]:
        return list(self._ancestors)

    @property
    @data_field
    def children(self) -> list[str]:
        return [child.name for child in self._node.children]

    @property
    @data_field
    def rules(self) -> list[GraphRule]:
        return list(self._rules)


class NodeSource(NodeAnswer):
    """A node's source: its file, text, and lines, and the class it belongs to when it is an operation or property. The
    node a person opens also lists every class, operation, and property the loaded graph holds, each as its own source,
    so a call in it can be opened in place."""

    def __init__(self, node: Node, owner: str = "", members: list[NodeSource] | None = None) -> None:
        super().__init__(node)
        self._owner = owner
        self._members = list(members or [])

    @property
    @data_field
    def owner(self) -> str:
        """The class an operation or property belongs to; empty for a class and for any other node."""
        return self._owner

    @property
    @data_field
    def file(self) -> Annotated[str, SourceFile]:
        return self._node.source.file

    @property
    @data_field
    def text(self) -> str:
        return self._node.source.text

    @property
    @data_field
    def start_line(self) -> int:
        return self._node.source.start_line

    @property
    @data_field
    def end_line(self) -> int:
        return self._node.source.end_line

    @property
    @data_field
    def members(self) -> list[NodeSource]:
        return list(self._members)
