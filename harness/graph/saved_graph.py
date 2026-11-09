"""SavedGraph. The graph a folder keeps in its ``.context/graph.json``: every practice's nodes, edges, and violations,
each written and read by field name, so the graph's loader, the Validate action's reader, and the board read one shape.

A saved node names its ``node_id``, ``name``, ``type``, and ``practice`` the way ``graph.return_nodes`` names them, and a
saved violation is the same Violation data a returned node's rule lists, so a reader of either needs one set of names.
"""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, Callable

from harness.graph.edge import EdgeType
from harness.graph.violation import Violation
from harness.installation.data_class import data_of
from harness.installation.json_file import JsonFile, JsonFileUnreadable

if TYPE_CHECKING:
    from harness.graph.edge import Edge
    from harness.graph.graph import Graph, Node
    from harness.guidance.guidance import PracticeGuidance

GRAPH_FILE_NAME = "graph.json"
# The shape this code writes. A saved graph of any other shape is read as no saved graph, so the next load replaces it.
SAVED_SHAPE_VERSION = 3


class SavedGraphOutdated(Exception):
    """A saved graph in another shape than this code writes. Load the working copy again to replace it."""

    def __init__(self, source: str, version: object) -> None:
        super().__init__(f"{source or 'The saved graph'} is in shape {version!r}, not {SAVED_SHAPE_VERSION}; load the working copy again.")
        self.source = source
        self.version = version


class SavedNode:
    """One node as the saved graph keeps it: what it is, where it sits in its file, its stage, and its facts."""

    def __init__(self, node_id: str, name: str, type: str, practice: str, file: str, line: int, end_line: int, stage: str, facts: dict) -> None:
        self.node_id = node_id
        self.name = name
        self.type = type
        self.practice = practice
        self.file = file
        self.line = line
        self.end_line = end_line
        self.stage = stage
        self.facts = facts

    @classmethod
    def from_record(cls, record: dict) -> SavedNode:
        return cls(
            str(record["node_id"]),
            str(record["name"]),
            str(record["type"]),
            str(record["practice"]),
            str(record.get("file") or ""),
            int(record.get("line") or 1),
            int(record.get("end_line") or 1),
            str(record.get("stage") or ""),
            dict(record.get("facts") or {}),
        )

    @property
    def record(self) -> dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "type": self.type,
            "practice": self.practice,
            "file": self.file,
            "line": self.line,
            "end_line": self.end_line,
            "stage": self.stage,
            "facts": self.facts,
        }


class SavedEdge:
    """One edge as the saved graph keeps it: the ids of the nodes it joins, and the EdgeType of its kind."""

    def __init__(self, parent: str, child: str, type: EdgeType) -> None:
        self.parent = parent
        self.child = child
        self.type = type

    @classmethod
    def from_edge(cls, edge: Edge) -> SavedEdge:
        return cls(edge.parent.node_id, edge.child.node_id, edge.type)

    @classmethod
    def from_record(cls, record: dict) -> SavedEdge:
        edge_type = EdgeType(str(record["kind"]), int(record.get("order") or 0), str(record.get("display") or "direct"))
        return cls(str(record["parent"]), str(record["child"]), edge_type)

    @property
    def key(self) -> tuple[str, str, str]:
        """What tells this edge apart from another of the practice's: its kind and the ids of its ends."""
        return (self.type.kind, self.parent, self.child)

    @property
    def record(self) -> dict:
        edge_type = self.type
        return {"parent": self.parent, "child": self.child, "kind": edge_type.kind, "order": edge_type.order, "display": edge_type.display}


class SavedPractice:
    """One practice as the saved graph keeps it: the folder its source was read from, the facts about the practice as a
    whole (kept on its root, such as the Clean Engineering model's members), and its nodes, edges, and violations."""

    def __init__(self, name: str, source_root: str, root_facts: dict, nodes: list[SavedNode], edges: list[SavedEdge], violations: list[Violation]) -> None:
        self.name = name
        self.source_root = source_root
        self.root_facts = root_facts
        self.nodes = nodes
        self.edges = edges
        self.violations = violations

    @classmethod
    def from_practice(cls, practice: PracticeGuidance, files: list[str] | None = None) -> SavedPractice:
        """The practice as the graph that holds it has it now; with files, only its nodes read from them (each a file
        or folder from its source root) and the edges that join two of them or one of them to the practice's root."""
        graph = practice.reading.graph
        nodes = [node for node in practice.reading.in_graph.nodes() if _read_from(node, files)]
        edges = [edge for edge in practice.reading.in_graph.edges() if _joins_kept(edge, files)]
        return cls(
            practice.key,
            practice.reading.in_graph.source_root,
            practice.reading.in_graph.root.facts,
            [SavedNode(node.node_id, node.name, node.type, node.practice.key, node.source.file, node.source.start_line, node.source.end_line, node.stage, node.facts) for node in nodes],
            [SavedEdge.from_edge(edge) for edge in edges],
            [violation for node in nodes for violation in node.rules.violations],
        )

    @classmethod
    def from_record(cls, name: str, record: dict) -> SavedPractice:
        return cls(
            name,
            str(record.get("source_root") or ""),
            dict(record.get("root_facts") or {}),
            [SavedNode.from_record(item) for item in record.get("nodes") or []],
            [SavedEdge.from_record(item) for item in record.get("edges") or []],
            [Violation.from_data(item) for item in record.get("violations") or []],
        )

    def root_in(self, folder: Path | None) -> Path | None:
        """The folder the practice's source was read from; folder when it was saved with none."""
        return Path(self.source_root) if self.source_root else folder

    @property
    def violations_by_node(self) -> dict[str, list[Violation]]:
        """The practice's violations, by the id of the node each was found on."""
        return _violations_by_node(self.violations)

    @property
    def record(self) -> dict:
        return {
            "source_root": self.source_root,
            "root_facts": self.root_facts,
            "nodes": [node.record for node in self.nodes],
            "edges": [edge.record for edge in self.edges],
            "violations": [data_of(violation) for violation in self.violations],
        }


class SavedGraph:
    """Every practice a folder's saved graph keeps, with the pattern overlays it was loaded with. A graph kept for the
    files a validate checks also names the folders of the other files the graph held (``held_beside``): a rule over a
    whole practice compared the checked files with those too, so its hits depend on them."""

    def __init__(self, overlays: list[str], practices: dict[str, SavedPractice], held_beside: list[str] | None = None) -> None:
        self.overlays = list(overlays)
        self.practices = dict(practices)
        self.held_beside = list(held_beside or [])

    @classmethod
    def from_graph(cls, graph: Graph, files: list[str] | None = None) -> SavedGraph:
        """The graph as it is now; with files, only the nodes read from them, and the folders, two levels deep, of every
        other file the graph held a node of."""
        opened = graph.practices.opened
        beside = [] if files is None else _folders_beside(graph, files)
        return cls(graph.overlays, {name: SavedPractice.from_practice(practice, files) for name, practice in opened.items()}, beside)

    @classmethod
    def from_document(cls, document: dict, source: str = "") -> SavedGraph:
        """The saved graph a JSON document holds; ``SavedGraphOutdated`` when it is in another shape."""
        version = document.get("version")
        if version != SAVED_SHAPE_VERSION:
            raise SavedGraphOutdated(source, version)
        practices = document.get("practices") or {}
        kept = {name: SavedPractice.from_record(name, record) for name, record in practices.items()}
        return cls(list(document.get("overlays") or []), kept, list(document.get("held_beside") or []))

    @classmethod
    def from_text(cls, text: str, source: str = "") -> SavedGraph:
        """The graph a checked graph's text holds: a saved graph document, or the node list ``graph.return_nodes``
        answers with; empty text holds no practices. ``SavedGraphOutdated`` for a saved graph in another shape."""
        document = json.loads(text) if text.strip() else {"version": SAVED_SHAPE_VERSION}
        if isinstance(document, list):
            return cls.from_nodes(document)
        if not isinstance(document, dict):
            raise SavedGraphOutdated(source, type(document).__name__)
        return cls.from_document(document, source)

    @classmethod
    def from_file(cls, path: Path) -> SavedGraph:
        """The graph a checked graph file holds, read as ``from_text`` reads its text."""
        return cls.from_text(path.read_text(encoding="utf-8"), str(path))

    @classmethod
    def from_nodes(cls, nodes: list[dict]) -> SavedGraph:
        """The violations of each violating rule on the nodes ``graph.return_nodes`` answers with, each under the
        practice of its node. A node list keeps no pattern overlays, so only each practice's own scanners count."""
        return cls.from_violations([
            Violation.from_data({"practice": node.get("practice", ""), **hit})
            for node in nodes
            for rule in node.get("rules") or []
            if rule.get("status") == "violating"
            for hit in rule.get("violations") or []
        ])

    @classmethod
    def from_violations(cls, violations: list[Violation], overlays: list[str] | None = None) -> SavedGraph:
        """A graph that keeps only violations, each under the practice that found it: what a node list holds, or the
        violations of several graph files read together."""
        found: dict[str, list[Violation]] = {}
        for violation in violations:
            found.setdefault(violation.practice, []).append(violation)
        return cls(list(overlays or []), {name: SavedPractice(name, "", {}, [], [], hits) for name, hits in found.items()})

    @property
    def document(self) -> dict:
        document = {
            "version": SAVED_SHAPE_VERSION,
            "overlays": list(self.overlays),
            "practices": {name: practice.record for name, practice in self.practices.items()},
        }
        return {**document, "held_beside": list(self.held_beside)} if self.held_beside else document

    @property
    def text(self) -> str:
        return json.dumps(self.document, separators=(",", ":"))

    def of_practices(self, keys: list[str]) -> SavedGraph:
        """This saved graph holding only the practices keys names."""
        return SavedGraph(self.overlays, {key: self.practices[key] for key in keys if key in self.practices})

    def merged_over(self, older: SavedGraph | None) -> SavedGraph:
        """This graph, keeping the practices an older saved graph holds that this one did not load."""
        kept = dict(older.practices) if older is not None else {}
        kept.update(self.practices)
        return SavedGraph(self.overlays, kept)

    def holds(self, practice_roots: dict[str, Path], overlays: list[str]) -> bool:
        """True when this saved graph holds every practice asked for, each read from the same folder, with the same
        overlays applied."""
        for name, root in practice_roots.items():
            saved = self.practices.get(name)
            if saved is None or Path(saved.source_root).resolve() != Path(root).resolve():
                return False
        return self.overlays == list(overlays)

    def violations(self, practices: list[str] | None = None) -> list[Violation]:
        """Every violation the saved practices hold; with practices, only those the named practices found."""
        return [violation for name, saved in self.practices.items() if not practices or name in practices for violation in saved.violations]


class SavedGraphFile:
    """The ``.context/graph.json`` a folder's graph is saved in, and whether it holds the practices a load asks for."""

    def __init__(self, folder: Path, report_progress: Callable[[str], None]) -> None:
        self.path = folder / ".context" / GRAPH_FILE_NAME
        self._report_progress = report_progress
        # Written whole and swapped in, so a chat reading it never meets half a graph another chat's worker is saving.
        self._file = JsonFile(self.path, compact=True)

    def read(self) -> SavedGraph | None:
        """The saved graph; none when there is no file, or it is not a saved graph of the shape this code writes. The
        file is a copy of what a load reads from the folder, so a load reads the folder again instead."""
        if not self._file.exists():
            return None
        self._report_progress("Reading the saved graph")
        try:
            return SavedGraph.from_document(self._file.read(), str(self.path))
        except (JsonFileUnreadable, SavedGraphOutdated):
            return None

    def write(self, saved: SavedGraph) -> Path:
        return self._file.write(saved.document)

    def holding(self, practice_roots: dict[str, Path], overlays: list[str]) -> SavedGraph | None:
        """The saved graph, when it holds these practices, each on the same root, and these overlays. It is not checked
        against the files' dates: a file changed since reaches the graph only when an action refreshes it."""
        saved = self.read()
        if saved is None or not saved.holds(practice_roots, overlays):
            return None
        return saved


class PracticeChanges:
    """How one practice of a graph changed in a build, by saved records: the nodes it no longer holds, the nodes it
    holds new or changed, the edges kept on it that went or changed, the edges new or changed, each node whose
    violations changed with the violations it has now, and the facts about the practice as a whole when they changed."""

    def __init__(
        self,
        dropped_nodes: list[str],
        nodes: list[SavedNode],
        dropped_edges: list[tuple[str, str, str]],
        edges: list[SavedEdge],
        violations: dict[str, list[Violation]],
        root_facts: dict | None,
    ) -> None:
        self.dropped_nodes = dropped_nodes
        self.nodes = nodes
        self.dropped_edges = dropped_edges
        self.edges = edges
        self.violations_by_node = violations
        self.root_facts = root_facts

    @classmethod
    def between(cls, before: SavedPractice, after: SavedPractice) -> PracticeChanges:
        nodes = RecordChanges({node.node_id: node for node in before.nodes}, {node.node_id: node for node in after.nodes})
        edges = RecordChanges({edge.key: edge for edge in before.edges}, {edge.key: edge for edge in after.edges})
        return cls(
            nodes.gone,
            nodes.changed,
            [*edges.gone, *edges.replaced],
            edges.changed,
            _violations_changed(before, after, nodes),
            after.root_facts if after.root_facts != before.root_facts else None,
        )

    @classmethod
    def from_record(cls, record: dict) -> PracticeChanges:
        return cls(
            [str(node_id) for node_id in record.get("dropped_nodes") or []],
            [SavedNode.from_record(item) for item in record.get("nodes") or []],
            [(str(kind), str(parent), str(child)) for kind, parent, child in record.get("dropped_edges") or []],
            [SavedEdge.from_record(item) for item in record.get("edges") or []],
            {node_id: [Violation.from_data(item) for item in hits] for node_id, hits in (record.get("violations") or {}).items()},
            record.get("root_facts"),
        )

    @property
    def record(self) -> dict:
        return {
            "dropped_nodes": self.dropped_nodes,
            "nodes": [node.record for node in self.nodes],
            "dropped_edges": [list(key) for key in self.dropped_edges],
            "edges": [edge.record for edge in self.edges],
            "violations": {node_id: [data_of(hit) for hit in hits] for node_id, hits in self.violations_by_node.items()},
            "root_facts": self.root_facts,
        }

    @property
    def is_empty(self) -> bool:
        return not (self.dropped_nodes or self.nodes or self.dropped_edges or self.edges or self.violations_by_node or self.root_facts is not None)


class RecordChanges:
    """How saved records, each by the key that tells it apart, changed between two builds: the keys gone, the records new
    or different, and the keys of those different."""

    def __init__(self, before: dict[Any, Any], after: dict[Any, Any]) -> None:
        self._before = {key: item.record for key, item in before.items()}
        self.after = after

    @property
    def gone(self) -> list[Any]:
        return [key for key in self._before if key not in self.after]

    @property
    def changed(self) -> list[Any]:
        return [item for key, item in self.after.items() if self._before.get(key) != item.record]

    @property
    def replaced(self) -> list[Any]:
        return [key for key, item in self.after.items() if key in self._before and self._before[key] != item.record]


class GraphChanges:
    """How a build changed the graph it was given, practice by practice: what a worker answers for a refresh, so the
    server changes the graph it holds by what the refresh changed instead of reading back the whole graph. A build
    that changed which practices the graph holds, their roots, or its overlays has no changes to answer (``between``
    answers none), and its whole graph is read back."""

    def __init__(self, practices: dict[str, PracticeChanges]) -> None:
        self.practices = practices

    @classmethod
    def between(cls, before: SavedGraph, after: SavedGraph) -> GraphChanges | None:
        if set(before.practices) != set(after.practices) or before.overlays != after.overlays:
            return None
        if any(before.practices[key].source_root != practice.source_root for key, practice in after.practices.items()):
            return None
        return cls({key: PracticeChanges.between(before.practices[key], practice) for key, practice in after.practices.items()})

    @classmethod
    def from_text(cls, text: str) -> GraphChanges:
        document = json.loads(text)
        return cls({key: PracticeChanges.from_record(record) for key, record in (document.get("practices") or {}).items()})

    @property
    def text(self) -> str:
        return json.dumps({"practices": {key: changes.record for key, changes in self.practices.items()}}, separators=(",", ":"))


def _violations_changed(before: SavedPractice, after: SavedPractice, nodes: RecordChanges) -> dict[str, list[Violation]]:
    """Each node after holds whose violations changed, with those it has now. A node changed in place is given its
    violations again, since a node of another type carries other rules."""
    old_hits, new_hits = before.violations_by_node, after.violations_by_node
    differ = {node_id for node_id in {*old_hits, *new_hits} if _records(old_hits.get(node_id)) != _records(new_hits.get(node_id))}
    hit = {node.node_id for node in nodes.changed} | differ
    return {node_id: new_hits.get(node_id, []) for node_id in sorted(hit) if node_id in nodes.after}


def _violations_by_node(violations: list[Violation]) -> dict[str, list[Violation]]:
    found: dict[str, list[Violation]] = {}
    for violation in violations:
        found.setdefault(violation.node_id, []).append(violation)
    return found


def _records(violations: list[Violation] | None) -> list[dict]:
    return [data_of(violation) for violation in violations or []]


def _folders_beside(graph: Graph, files: list[str]) -> list[str]:
    """The folders, two levels deep, of the files graph holds a node of besides files."""
    held = (node for practice in graph.practices.opened.values() for node in practice.reading.in_graph.nodes())
    beside = {PurePosixPath(node.source.file.replace("\\", "/")).parent for node in held if node.source.file not in ("", ".") and not _read_from(node, files)}
    return sorted({"/".join(folder.parts[:2]) or "." for folder in beside})


def _read_from(node: Node, files: list[str] | None) -> bool:
    """Whether node was read from one of files, each a file or folder from its practice's source root; every node is
    when no files are named."""
    if files is None:
        return True
    file = (node.source.file or "").replace("\\", "/")
    named = [entry.replace("\\", "/").rstrip("/") for entry in files]
    return any(file == item or file.startswith(f"{item}/") for item in named)


def _joins_kept(edge: Edge, files: list[str] | None) -> bool:
    """Whether edge joins two nodes read from files, or one of them to its practice's root."""
    ends = (edge.parent, edge.child)
    return all(_read_from(end, files) or end.type == "Practice" for end in ends) and any(_read_from(end, files) for end in ends)
