"""What the graph's tools answer with besides the graph's own objects: a node's place in the explorer tree, a node's
source, and the nodes a filter matches. Each is a NodeAnswer: it holds the node it describes and reads its data from
it, so an application outside Python reads the same objects the agent does. A node's rules are its own GraphRulesCollection, and each rule's
violations are Violations, so neither has a copy here."""

from __future__ import annotations

from collections import defaultdict
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Annotated

from harness.graph.graph_rules_collection import GraphRule, GraphRulesCollection
from harness.installation.data_class import SourceFile, data_field
from harness.markdown.markdown import link_words

if TYPE_CHECKING:
    from harness.graph.graph import Graph, Node
    from harness.graph.node_filter import Filter
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

    def __init__(self, node: Node, children: list | None = None, children_left_out: int = 0, label: str = "") -> None:
        super().__init__(node)
        self._children = list(children or [])
        self._children_left_out = children_left_out
        self._label = label or node.name

    @property
    @data_field
    def label(self) -> str:
        """What the tree shows for the node at this place, which tells it apart from the entries beside it: a folder's
        path from the folder above it, a node another beside it shares a name with followed by its file, and a step's
        sentence with each link's text in place of the link. ``name`` stays the node's own name."""
        return self._label

    @property
    @data_field
    def children(self) -> list[ExplorerEntry | GraphRulesCollection]:
        """The entries below this one, and last the node's rules when it has any to show."""
        return list(self._children)

    @property
    @data_field
    def children_left_out(self) -> int:
        """How many entries below this one an answer left out; ``graph.explorer_branch`` answers them."""
        return self._children_left_out

    def opened(self) -> ExplorerEntry:
        """This entry with the entries below it, each closed. A whole repository's tree runs to hundreds of megabytes,
        so an answer sends one level and a person opens the next."""
        return ExplorerEntry(self._node, [child.closed() if isinstance(child, ExplorerEntry) else child for child in self._children], label=self._label)

    def closed(self) -> ExplorerEntry:
        """This entry with its rules, which mark it and show when it is picked, and the entries below it left out."""
        entries = [child for child in self._children if isinstance(child, ExplorerEntry)]
        rules = [child for child in self._children if not isinstance(child, ExplorerEntry)]
        return ExplorerEntry(self._node, rules, children_left_out=len(entries), label=self._label)

    def kept_by(self, wanted: Filter) -> ExplorerEntry | None:
        """This entry with only what the filter keeps below it: a node the filter matches keeps its rules, a practice's
        root always stays, and any other node stays, without its rules, only as the way to an entry kept below it."""
        entries = [kept for child in self._children if isinstance(child, ExplorerEntry) and (kept := child.kept_by(wanted)) is not None]
        rules = [child.kept_by(wanted) for child in self._children if isinstance(child, GraphRulesCollection)]
        if self._node.type == "Practice" or wanted.matches(self._node):
            return ExplorerEntry(self._node, [*entries, *rules], label=self._label)
        return ExplorerEntry(self._node, entries, label=self._label) if entries else None


class PlaceLabels:
    """The label of each entry one place in the explorer tree holds, decided together, since a label tells its entry
    apart from the entries beside it: a folder reads as its path from the place's folder, or from the practice's root
    when the place is no folder; a step's text reads with each link's words in place of the link; and entries of one
    label read with their file after them, its name, or its whole path when two files share a name."""

    def __init__(self, place: Node) -> None:
        self._place = place

    def of(self, node: Node) -> str:
        """The label of node at the place; node's own name when the place does not hold it."""
        return self.by_node_id().get(node.node_id, node.name)

    def by_node_id(self) -> dict[str, str]:
        """Each entry's label, by its node's id."""
        nodes = list({child.node_id: child for child in self._place.children}.values())
        shown = {node.node_id: self._shown(node) for node in nodes}
        sharing: dict[str, list[Node]] = defaultdict(list)
        for node in nodes:
            sharing[shown[node.node_id]].append(node)
        return {node.node_id: self._told_apart(shown[node.node_id], node, sharing[shown[node.node_id]]) for node in nodes}

    def _shown(self, node: Node) -> str:
        if not self._is_folder(node):
            return link_words(node.name)
        folder = self._file_of(node)
        above = self._file_of(self._place) if self._is_folder(self._place) else None
        return folder.relative_to(above).as_posix() if above and folder.is_relative_to(above) and folder != above else folder.as_posix()

    def _is_folder(self, node: Node) -> bool:
        return node.type in node.practice.reading.folder_types and bool(node.source.file)

    def _told_apart(self, shown: str, node: Node, sharing: list[Node]) -> str:
        if len(sharing) < 2 or not node.source.file:
            return shown
        file = self._file_of(node)
        names = [self._file_of(other).name for other in sharing if other.source.file]
        return f"{shown} ({file.name if names.count(file.name) < 2 else file.as_posix()})"

    def _file_of(self, node: Node) -> PurePosixPath:
        return PurePosixPath(node.source.file.replace("\\", "/"))


class PracticeInventory:
    """One loaded practice as the explorer's inventory shows it, read from the graph that holds it: how many nodes of
    each type it holds, how many edges, its node types, edge kinds, and rules. Its explorer tree comes from
    ``graph.explorer_trees``, as the explorer's filter leaves it: a whole repository's tree runs to hundreds of
    megabytes, which no page reads and no call sends within its ten minutes."""

    def __init__(self, practice: PracticeGuidance) -> None:
        self._practice = practice

    @property
    @data_field
    def node_counts(self) -> dict[str, int]:
        """How many nodes of each type the practice holds."""
        return {type: len(self._practice.reading.in_graph.nodes(type)) for type in self._practice.reading.in_graph.node_types}

    @property
    @data_field
    def edge_count(self) -> int:
        return len(self._practice.reading.in_graph.edge_index.of())

    @property
    @data_field
    def node_types(self) -> list[str]:
        """The node types the practice holds, sorted by name."""
        return sorted(self._practice.reading.in_graph.node_types)

    @property
    @data_field
    def edge_types(self) -> list[str]:
        """The edge kinds the practice holds that a person filters by, in the order the explorer tree shows them."""
        ordered = sorted(self._practice.reading.in_graph.edge_index.types.values(), key=lambda edge_type: edge_type.order)
        return [edge_type.kind for edge_type in ordered if edge_type.is_offered]

    @property
    @data_field
    def rules(self) -> list[str]:
        """Each rule the practice runs, named ``practice.node.rule`` with the pattern that owns it in front."""
        return self._practice.reading.in_graph.rule_run.rule_labels


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
