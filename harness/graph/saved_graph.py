"""SavedGraph. The graph a folder keeps in its ``.context/graph.json``: every practice's nodes, edges, and violations,
each written and read by field name, so the graph's loader, the Validate action's reader, and the board read one shape.

A saved node names its ``node_id``, ``name``, ``type``, and ``practice`` the way ``graph.return_nodes`` names them, and a
saved violation is the same Violation data a returned node's rule lists, so a reader of either needs one set of names.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from harness.graph.skipped_folders import SKIPPED_FOLDERS, skips_folder
from harness.graph.violation import Violation
from harness.installation.destination import data_of

if TYPE_CHECKING:
    from harness.graph.graph import Edge, Graph, Node, PracticeGraph

GRAPH_FILE_NAME = "graph.json"
# The shape this code writes. A saved graph of any other shape is read as no saved graph, so the next load replaces it.
SAVED_SHAPE_VERSION = 2

_REPO = Path(__file__).resolve().parents[2]
_GRAPH_FOLDER = Path(__file__).resolve().parent
# Files whose change can change what a load finds, so a saved graph older than any of them is rebuilt.
_GRAPH_RULE_MODULES = (
    "rules.py",
    "schema_rules.py",
    "schema_edges.py",
    "practice_rule.py",
    "graph_practice.py",
    "rule_context.py",
    "graph_rules_collection.py",
)
_RULE_FILE_NAMES = ("rules.py", "schema.yaml", "rules.yaml")
_SOURCE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".py", ".md"}
# How many files a freshness check reads between two progress reports.
_FILES_PER_PROGRESS_REPORT = 400


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
        return cls(node.node_id, node.name, node.type, node.practice.name, source.file, source.start_line, source.end_line, node.stage, node.facts)

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
    def fact(self) -> dict:
        """The edge's kind, order, and display, as ``PracticeGraph.record`` takes them."""
        return {"kind": self.kind, "order": self.order, "display": self.display}

    @property
    def record(self) -> dict:
        return {"parent": self.parent, "child": self.child, **self.fact}


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
    def from_practice(cls, practice: PracticeGraph) -> SavedPractice:
        nodes = [node for group in practice.nodes.values() for node in group]
        return cls(
            practice.name,
            practice.source_root,
            practice.root_node.facts,
            [SavedNode.from_node(node) for node in nodes],
            [SavedEdge.from_edge(edge) for group in practice.edges.values() for edge in group],
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
    def from_graph(cls, graph: Graph) -> SavedGraph:
        return cls(graph.overlays, {name: SavedPractice.from_practice(practice) for name, practice in graph.practices.items()})

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

    def restored_graph(self) -> Graph:
        """A graph holding every saved practice: each practice's nodes first, then the edges between them, which may
        cross practices, and the violations on them."""
        from harness.graph.graph import Graph

        graph = Graph()
        for name, saved in self.practices.items():
            graph.practice(name).restore(saved)
        for name, saved in self.practices.items():
            graph.practice(name).restore_links(saved)
        return graph


class SavedGraphFile:
    """The ``.context/graph.json`` a folder's graph is saved in, and whether it is still current: it holds the practices
    asked for, and neither their source nor any rule file has changed since it was written."""

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

    def current_for(self, practice_roots: dict[str, Path], overlays: list[str]) -> SavedGraph | None:
        """The saved graph, when it holds these practices and overlays and nothing it was read from has changed since."""
        saved = self.read()
        if saved is None or not saved.holds(practice_roots, overlays):
            return None
        stamp = self.path.stat().st_mtime
        if self._rules_changed_since(stamp) or any(self._is_dirty(Path(root), stamp) for root in practice_roots.values()):
            return None
        return saved

    def _rules_changed_since(self, stamp: float) -> bool:
        folders = (_REPO / "cdd_guidance" / "practices", _REPO / "cdd_guidance" / "patterns")
        if any(folder.is_dir() and self._rule_file_newer_than(folder, stamp) for folder in folders):
            return True
        return any(self._file_newer_than(_GRAPH_FOLDER / name, stamp) for name in _GRAPH_RULE_MODULES)

    def _rule_file_newer_than(self, folder: Path, stamp: float) -> bool:
        for dirpath, dirnames, filenames in os.walk(folder):
            dirnames[:] = [name for name in dirnames if name not in SKIPPED_FOLDERS]
            paths = (Path(dirpath, filename) for filename in filenames)
            if any(self._is_rule_file(path) and path.stat().st_mtime > stamp for path in paths):
                return True
        return False

    def _is_rule_file(self, path: Path) -> bool:
        return path.name in _RULE_FILE_NAMES or (path.suffix == ".py" and "rules" in path.parts)

    def _is_dirty(self, path: Path, stamp: float) -> bool:
        if not path.exists():
            return True
        if path.is_file():
            return path.stat().st_mtime > stamp
        return self._contents_newer_than(path, stamp)

    def _contents_newer_than(self, folder: Path, stamp: float) -> bool:
        seen = 0
        for dirpath, dirnames, filenames in os.walk(folder):
            dirnames[:] = [name for name in dirnames if not skips_folder(name)]
            for path in (Path(dirpath, filename) for filename in filenames if Path(filename).suffix.lower() in _SOURCE_SUFFIXES):
                seen += 1
                if seen == 1 or seen % _FILES_PER_PROGRESS_REPORT == 0:
                    self._report_progress(f"Checking folder dates · {seen}")
                if path.stat().st_mtime > stamp:
                    return True
        return False

    def _file_newer_than(self, path: Path, stamp: float) -> bool:
        return path.is_file() and path.stat().st_mtime > stamp
