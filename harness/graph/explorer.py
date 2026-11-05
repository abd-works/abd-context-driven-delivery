"""What the graph's tools answer with: the explorer tree, each practice's inventory, a node's source, and a filter's
choices. An application outside Python reads the same objects the agent does."""

from __future__ import annotations

from typing import Annotated

from harness.installation.destination import SourceFile, data_field


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


class RuleHit:
    """One violation a rule recorded on a node, at the node's file and lines; a hit with no source has neither."""

    def __init__(self, message: str, file: str, start: int, end: int) -> None:
        self._message = message
        self._file = file
        self._start = start
        self._end = end

    @classmethod
    def from_stored(cls, hit: dict) -> RuleHit:
        return cls(hit["message"], hit.get("file", ""), hit.get("start", 0), hit.get("end", 0))

    @property
    @data_field
    def message(self) -> str:
        return self._message

    @property
    @data_field
    def file(self) -> Annotated[str, SourceFile]:
        return self._file

    @property
    @data_field
    def start(self) -> int:
        return self._start

    @property
    @data_field
    def end(self) -> int:
        return self._end


class ExplorerEntry:
    """One entry of the explorer tree: a node, or the rules category under it, with the entries below it."""

    def __init__(self, type: str, name: str, node_id: str, children: list[ExplorerEntry] | None = None) -> None:
        self._type = type
        self._name = name
        self._node_id = node_id
        self._children = list(children or [])

    @property
    @data_field
    def type(self) -> str:
        return self._type

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def node_id(self) -> str:
        return self._node_id

    @property
    @data_field
    def children(self) -> list[ExplorerEntry]:
        return list(self._children)


class RuleEntry(ExplorerEntry):
    """One rule under a node: whether it is violating, passing, or a prompt, and every hit it recorded there."""

    def __init__(self, slug: str, node_id: str, status: str, violations: list[RuleHit]) -> None:
        super().__init__("Rule", slug, node_id)
        self._status = status
        self._violations = list(violations)

    @property
    @data_field
    def status(self) -> str:
        return self._status

    @property
    @data_field
    def violations(self) -> list[RuleHit]:
        return list(self._violations)


class PracticeInventory:
    """One loaded practice: its node and edge counts, node and edge types, the rules it runs, and its explorer tree."""

    def __init__(self, node_counts: dict[str, int], edge_count: int, node_types: list[str], edge_types: list[str], rules: list[str], tree: ExplorerEntry) -> None:
        self._node_counts = dict(node_counts)
        self._edge_count = edge_count
        self._node_types = list(node_types)
        self._edge_types = list(edge_types)
        self._rules = list(rules)
        self._tree = tree

    @property
    @data_field
    def node_counts(self) -> dict[str, int]:
        return dict(self._node_counts)

    @property
    @data_field
    def edge_count(self) -> int:
        return self._edge_count

    @property
    @data_field
    def node_types(self) -> list[str]:
        return list(self._node_types)

    @property
    @data_field
    def edge_types(self) -> list[str]:
        return list(self._edge_types)

    @property
    @data_field
    def rules(self) -> list[str]:
        return list(self._rules)

    @property
    @data_field
    def tree(self) -> ExplorerEntry:
        return self._tree


class Inventory:
    """Every loaded practice's inventory, with the pattern overlays applied and those available."""

    def __init__(self, practices: dict[str, PracticeInventory], overlays: list[str], available_overlays: list[str]) -> None:
        self._practices = dict(practices)
        self._overlays = list(overlays)
        self._available_overlays = list(available_overlays)

    @property
    @data_field
    def practices(self) -> dict[str, PracticeInventory]:
        return dict(self._practices)

    @property
    @data_field
    def overlays(self) -> list[str]:
        return list(self._overlays)

    @property
    @data_field
    def available_overlays(self) -> list[str]:
        return list(self._available_overlays)


class AppliedOverlays(Inventory):
    """The inventory after a change of pattern overlays, with a sentence naming the overlays now applied."""

    def __init__(self, message: str, inventory: Inventory) -> None:
        super().__init__(inventory.practices, inventory.overlays, inventory.available_overlays)
        self._message = message

    @property
    @data_field
    def message(self) -> str:
        return self._message


class Overlay:
    """The pattern overlay a folder holds."""

    def __init__(self, overlay: str) -> None:
        self._overlay = overlay

    @property
    @data_field
    def overlay(self) -> str:
        return self._overlay


class FilterChoices:
    """The node types, relationships, and rules a filter offers once practices and node types are chosen."""

    def __init__(self, node_types: list[str], relationships: list[str], rules: list[str]) -> None:
        self._node_types = list(node_types)
        self._relationships = list(relationships)
        self._rules = list(rules)

    @property
    @data_field
    def node_types(self) -> list[str]:
        return list(self._node_types)

    @property
    @data_field
    def relationships(self) -> list[str]:
        return list(self._relationships)

    @property
    @data_field
    def rules(self) -> list[str]:
        return list(self._rules)


class FilteredNode:
    """One node a filter matches, with the names above and below it and its rules."""

    def __init__(self, practice: str, type: str, name: str, node_id: str, ancestors: list[str], children: list[str], rules: list[RuleEntry]) -> None:
        self._practice = practice
        self._type = type
        self._name = name
        self._node_id = node_id
        self._ancestors = list(ancestors)
        self._children = list(children)
        self._rules = list(rules)

    @property
    @data_field
    def practice(self) -> str:
        return self._practice

    @property
    @data_field
    def type(self) -> str:
        return self._type

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def node_id(self) -> str:
        return self._node_id

    @property
    @data_field
    def ancestors(self) -> list[str]:
        return list(self._ancestors)

    @property
    @data_field
    def children(self) -> list[str]:
        return list(self._children)

    @property
    @data_field
    def rules(self) -> list[RuleEntry]:
        return list(self._rules)


class Member:
    """A class, operation, or property the loaded graph holds, at its place in its file, so a call to it can be opened."""

    def __init__(self, id: str, name: str, kind: str, owner: str, text: str, file: str, start: int, end: int) -> None:
        self._id = id
        self._name = name
        self._kind = kind
        self._owner = owner
        self._text = text
        self._file = file
        self._start = start
        self._end = end

    @property
    @data_field
    def id(self) -> str:
        return self._id

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def kind(self) -> str:
        return self._kind

    @property
    @data_field
    def owner(self) -> str:
        return self._owner

    @property
    @data_field
    def text(self) -> str:
        return self._text

    @property
    @data_field
    def file(self) -> str:
        return self._file

    @property
    @data_field
    def start(self) -> int:
        return self._start

    @property
    @data_field
    def end(self) -> int:
        return self._end


class NodeSource:
    """A node's source: its file, text, and lines, with every member the loaded graph holds."""

    def __init__(self, node_id: str, name: str, type: str, file: str, text: str, start_line: int, end_line: int, members: list[Member]) -> None:
        self._node_id = node_id
        self._name = name
        self._type = type
        self._file = file
        self._text = text
        self._start_line = start_line
        self._end_line = end_line
        self._members = list(members)

    @property
    @data_field
    def node_id(self) -> str:
        return self._node_id

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def type(self) -> str:
        return self._type

    @property
    @data_field
    def file(self) -> Annotated[str, SourceFile]:
        return self._file

    @property
    @data_field
    def text(self) -> str:
        return self._text

    @property
    @data_field
    def start_line(self) -> int:
        return self._start_line

    @property
    @data_field
    def end_line(self) -> int:
        return self._end_line

    @property
    @data_field
    def members(self) -> list[Member]:
        return list(self._members)
