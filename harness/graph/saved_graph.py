"""SavedGraph. The graph a folder keeps in its ``.context/graph.json``: every practice's nodes, edges, and violations,
each written and read by field name, so the graph's loader, the Validate action's reader, and the board read one shape.

A saved node names its ``node_id``, ``name``, ``type``, and ``practice`` the way ``graph.return_nodes`` names them, and a
saved violation is the same Violation data a returned node's rule lists, so a reader of either needs one set of names.
"""

from __future__ import annotations

import json
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from harness.graph.pattern_overlays import PatternOverlays
from harness.graph.violation import Violation
from harness.installation.data_class import data_of

if TYPE_CHECKING:
    from harness.graph.edge import Edge
    from harness.graph.graph import Graph, Node
    from harness.guidance.guidance import PracticeGuidance

GRAPH_FILE_NAME = "graph.json"
# The shape this code writes. A saved graph of any other shape is read as no saved graph, so the next load replaces it.
SAVED_SHAPE_VERSION = 2


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
    def from_node(cls, node: Node) -> SavedNode:
        source = node.source
        return cls(node.node_id, node.name, node.type, node.practice.key, source.file, source.start_line, source.end_line, node.stage, node.facts)

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
    """One edge as the saved graph keeps it, by the ids of the nodes it joins."""

    def __init__(self, parent: str, child: str, kind: str, order: int, display: str) -> None:
        self.parent = parent
        self.child = child
        self.kind = kind
        self.order = order
        self.display = display

    @classmethod
    def from_edge(cls, edge: Edge) -> SavedEdge:
        return cls(edge.parent.node_id, edge.child.node_id, edge.kind, edge.order, edge.display)

    @classmethod
    def from_record(cls, record: dict) -> SavedEdge:
        return cls(str(record["parent"]), str(record["child"]), str(record["kind"]), int(record.get("order") or 0), str(record.get("display") or "direct"))

    @property
    def record(self) -> dict:
        return {"parent": self.parent, "child": self.child, "kind": self.kind, "order": self.order, "display": self.display}


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
        graph = practice.graph
        nodes = [node for node in practice.in_graph.nodes() if _read_from(node, files)]
        edges = [edge for edge in practice.in_graph.edges() if _joins_kept(edge, files)]
        return cls(
            practice.key,
            practice.in_graph.source_root,
            practice.in_graph.root.facts,
            [SavedNode.from_node(node) for node in nodes],
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
    """Every practice a folder's saved graph keeps, with the pattern overlays it was loaded with."""

    def __init__(self, overlays: list[str], practices: dict[str, SavedPractice]) -> None:
        self.overlays = list(overlays)
        self.practices = dict(practices)

    @classmethod
    def from_graph(cls, graph: Graph, files: list[str] | None = None) -> SavedGraph:
        """The graph as it is now; with files, only the nodes read from them."""
        return cls(graph.overlays, {name: SavedPractice.from_practice(practice, files) for name, practice in graph.practices.items()})

    @classmethod
    def from_document(cls, document: dict, source: str = "") -> SavedGraph:
        """The saved graph a JSON document holds; ``SavedGraphOutdated`` when it is in another shape."""
        version = document.get("version")
        if version != SAVED_SHAPE_VERSION:
            raise SavedGraphOutdated(source, version)
        practices = document.get("practices") or {}
        return cls(list(document.get("overlays") or []), {name: SavedPractice.from_record(name, record) for name, record in practices.items()})

    @classmethod
    def from_text(cls, text: str, source: str = "") -> SavedGraph:
        return cls.from_document(json.loads(text) if text.strip() else {"version": SAVED_SHAPE_VERSION}, source)

    @classmethod
    def from_file(cls, path: Path) -> SavedGraph:
        """The graph a checked graph file holds: a saved graph document, or the node list ``graph.return_nodes`` answers
        with; an empty file holds no practices. ``SavedGraphOutdated`` for a saved graph in another shape."""
        text = path.read_text(encoding="utf-8")
        document = json.loads(text) if text.strip() else {"version": SAVED_SHAPE_VERSION}
        if isinstance(document, list):
            return cls.from_nodes(document)
        if not isinstance(document, dict):
            raise SavedGraphOutdated(str(path), type(document).__name__)
        return cls.from_document(document, str(path))

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
        return {
            "version": SAVED_SHAPE_VERSION,
            "overlays": list(self.overlays),
            "practices": {name: practice.record for name, practice in self.practices.items()},
        }

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

    def checks_of(self, practice: PracticeGuidance) -> dict[str, Any]:
        """The graph rules practice checks with the overlays this graph was saved with, by slug, answered by practice
        itself: no graph is read back to ask it. A graph is read back into a graph that holds it
        (``graph.restored_from(saved)``)."""
        return self.applied_patterns.checks_of(practice)

    @cached_property
    def applied_patterns(self) -> PatternOverlays:
        """The pattern overlays this graph was saved with, each pattern made once."""
        return PatternOverlays(self.overlays)


class SavedGraphFile:
    """The ``.context/graph.json`` a folder's graph is saved in, and whether it holds the practices a load asks for."""

    def __init__(self, folder: Path, report_progress: Callable[[str], None]) -> None:
        self.path = folder / ".context" / GRAPH_FILE_NAME
        self._report_progress = report_progress

    def read(self) -> SavedGraph | None:
        """The saved graph; none when there is no file, or it is not a saved graph of the shape this code writes. The
        file is a copy of what a load reads from the folder, so a load reads the folder again instead."""
        if not self.path.is_file():
            return None
        self._report_progress("Reading the saved graph")
        try:
            document = json.loads(self.path.read_text(encoding="utf-8"))
            return SavedGraph.from_document(document, str(self.path)) if isinstance(document, dict) else None
        except (json.JSONDecodeError, SavedGraphOutdated):
            return None

    def write(self, saved: SavedGraph) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(saved.text, encoding="utf-8")
        return self.path

    def holding(self, practice_roots: dict[str, Path], overlays: list[str]) -> SavedGraph | None:
        """The saved graph, when it holds these practices, each on the same root, and these overlays. It is not checked
        against the files' dates: a file changed since reaches the graph only when an action refreshes it."""
        saved = self.read()
        if saved is None or not saved.holds(practice_roots, overlays):
            return None
        return saved


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
