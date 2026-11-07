"""What the graph's tools answer with besides the graph's own objects: a node's place in the explorer tree, a node's
source, and the nodes a filter matches. Each holds the node it describes and reads its data from it, so an application
outside Python reads the same objects the agent does. A node's rules are its own GraphRulesCollection, and each rule's
violations are Violations, so neither has a copy here."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from harness.installation.destination import SourceFile, data_field

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.graph_rules_collection import GraphRule


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


class ExplorerEntry:
    """One node at one place in the explorer tree, with the entries written below it there. A node sits at many places
    (under its home parent and under every relationship that names it) but only its home place lists its children, and
    a node already on the path to this place lists none, so the place is not the node."""

    def __init__(self, node: Node, children: list | None = None) -> None:
        self._node = node
        self._children = list(children or [])

    @property
    @data_field
    def type(self) -> str:
        return self._node.type

    @property
    @data_field
    def name(self) -> str:
        return self._node.name

    @property
    @data_field
    def node_id(self) -> str:
        return self._node.node_id

    @property
    @data_field
    def children(self) -> list:
        """The entries below this one, and last the node's rules when it has any to show."""
        return list(self._children)


class Overlay:
    """The pattern overlay a folder holds."""

    def __init__(self, overlay: str) -> None:
        self._overlay = overlay

    @property
    @data_field
    def overlay(self) -> str:
        return self._overlay


class FilteredNode:
    """One node a filter matches, with the names above and below it and its rules."""

    def __init__(self, node: Node, ancestors: list[str], rules: list[GraphRule]) -> None:
        self._node = node
        self._ancestors = list(ancestors)
        self._rules = list(rules)

    @property
    @data_field
    def practice(self) -> str:
        return self._node.practice.name

    @property
    @data_field
    def type(self) -> str:
        return self._node.type

    @property
    @data_field
    def name(self) -> str:
        return self._node.name

    @property
    @data_field
    def node_id(self) -> str:
        return self._node.node_id

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


class Member:
    """A class, operation, or property the loaded graph holds, at its place in its file, so a call to it can be opened."""

    def __init__(self, node: Node, owner: str) -> None:
        self._node = node
        self._owner = owner

    @property
    @data_field
    def id(self) -> str:
        return self._node.node_id

    @property
    @data_field
    def name(self) -> str:
        return self._node.name

    @property
    @data_field
    def kind(self) -> str:
        return self._node.type

    @property
    @data_field
    def owner(self) -> str:
        """The class an operation or property belongs to; empty for a class."""
        return self._owner

    @property
    @data_field
    def text(self) -> str:
        return self._node.source.text

    @property
    @data_field
    def file(self) -> str:
        return self._node.source.file

    @property
    @data_field
    def start(self) -> int:
        return self._node.source.start_line

    @property
    @data_field
    def end(self) -> int:
        return self._node.source.end_line


class NodeSource:
    """A node's source: its file, text, and lines, with every member the loaded graph holds."""

    def __init__(self, node: Node, members: list[Member]) -> None:
        self._node = node
        self._members = list(members)

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
    def members(self) -> list[Member]:
        return list(self._members)
