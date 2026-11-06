"""Graph. Practice graphs, nodes, edges, and the explorer tree."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
for _category in ("tools", "cdd_guidance/practices", "cdd_guidance/actions", "cdd_guidance/patterns"):
    _entry = str(_REPO / _category)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.agent_tools.progress import report_progress
from harness.installation.destination import data_field, language_adapter
from harness.installation.files import command, skill
from harness.mcp.mcp_server import mcp
from harness.graph.explorer import (
    ExplorerEntry,
    FilteredNode,
    GraphLoaded,
    GraphSaved,
    Member,
    NodeSource,
    Overlay,
    RuleCategory,
    RuleEntry,
    RuleHit,
)
from harness.graph.skipped_folders import SKIPPED_FOLDERS, scanned_files, skips_folder

Display = str
Tuple = list[str]
_GRAPH_JSON_NAME = "graph.json"
_DIRTY_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".py", ".md"}
_RULE_FILE_NAMES = ("rules.py", "schema.yaml", "rules.yaml")

def _under_any(file: str | None, prefixes: list[str]) -> bool:
    """True when ``file`` is one of the prefixes or sits under one."""
    location = (file or "").replace("\\", "/").strip("/")
    for prefix in prefixes:
        folder = str(prefix).replace("\\", "/").strip("/")
        if folder and (location == folder or location.startswith(folder + "/")):
            return True
    return False


def pattern_overlay_root(pattern: str) -> Path:
    return _REPO / "cdd_guidance" / "patterns" / pattern


def resolve_overlay_root(overlay: str) -> Path:
    """Overlay root is a folder that contains ``practices/``."""
    candidate = Path(overlay)
    if candidate.is_dir():
        resolved = candidate.resolve()
        if (resolved / "practices").is_dir():
            return resolved
    named = pattern_overlay_root(overlay)
    if named.is_dir() and (named / "practices").is_dir():
        return named.resolve()
    if candidate.is_dir():
        return candidate.resolve()
    return named.resolve()


def normalize_overlay(overlay: str) -> str:
    return str(resolve_overlay_root(overlay))


def _normalize_overlay_list(overlays: list[str]) -> list[str]:
    found: list[str] = []
    for item in overlays:
        text = str(item).strip()
        if not text:
            continue
        resolved = normalize_overlay(text)
        if resolved not in found:
            found.append(resolved)
    return found


def available_pattern_overlays() -> list[str]:
    patterns = _REPO / "cdd_guidance" / "patterns"
    if not patterns.is_dir():
        return []
    found: list[str] = []
    for entry in sorted(patterns.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        practices = entry / "practices"
        if not practices.is_dir():
            continue
        if any(child.is_dir() and not child.name.startswith(".") for child in practices.iterdir()):
            found.append(entry.name)
    return found


# The node kinds a source view opens a call into: classes, whose operations and properties it folds in place.
_CLASS_KINDS = frozenset(
    {"OoadClass", "Entity", "EntityRoot", "ValueObject", "Aggregate", "Repository", "DomainEvent", "DomainService", "Specification"}
)


class GraphFailure(Exception):
    def __init__(self, query: str, detail: str) -> None:
        super().__init__(f"{query}\n{detail}")
        self.query = query
        self.detail = detail


# Where each edge kind's group sits under a node in the explorer tree, lowest first. A practice orders its groups
# by these numbers, and graph.json saves them on each edge, so every loader and model reads them from here.
EDGE_ORDER: dict[str, int] = {
    "decomposedInto": 1,
    "relative": 1,
    "root": 1,
    "descriptions": 1,
    "participants": 1,
    "screens": 1,
    "owns": 2,
    "background": 2,
    "contexts": 2,
    "parameters": 2,
    "aggregates": 2,
    "given": 2,
    "scenarios": 3,
    "properties": 3,
    "observations": 3,
    "steps": 4,
    "demonstrates": 4,
    "shownOn": 4,
    "specifiedBy": 4,
    "specifies": 4,
    "examples": 5,
    "belongsTo": 5,
    "hasParameter": 6,
    "increments": 6,
    "accesses": 6,
    "hasType": 7,
    "returnType": 7,
    "stories": 7,
    "associates": 7,
    "observes": 8,
    "demonstratedThrough": 8,
    "ands": 9,
    "uses": 9,
    "invokedBy": 9,
    "returns": 10,
    "retrievedUsing": 11,
    "invokes": 12,
    "dependsOn": 13,
    "usedBy": 14,
}
# A kind only a pattern overlay's schema names: a child sits with the owned children, a relationship after them.
_DIRECT_KIND_ORDER = 2
_RELATIONSHIP_KIND_ORDER = 7


def edge_order(kind: str, display: Display = "direct") -> int:
    """Where this kind's group sits under a node in the explorer tree."""
    if kind in EDGE_ORDER:
        return EDGE_ORDER[kind]
    return _DIRECT_KIND_ORDER if display == "direct" else _RELATIONSHIP_KIND_ORDER


class EdgeType:
    def __init__(self, kind: str, order: int, display: Display) -> None:
        self.kind = kind
        self.order = order
        self.display = display


class Edge:
    def __init__(self, kind: str, order: int, display: Display, parent: Node, child: Node) -> None:
        self.kind = kind
        self.order = order
        self.display = display
        self.parent = parent
        self.child = child

    @property
    def stage(self) -> str:
        """The child node's stage. An edge does not store one of its own."""
        return self.child.stage

    @staticmethod
    def fact(row: Tuple) -> dict | None:
        parent_id, child_id, kind, order, display = (row + [""] * 5)[:5]
        if not parent_id or not child_id or not kind:
            return None
        shown = display if display in {"grouped", "relationship"} else "direct"
        return {
            "parent_id": parent_id,
            "child_id": child_id,
            "kind": kind,
            "order": int(order or 0),
            "display": shown,
        }


class Call:
    """A call found in source. operation is the callee text Monaco marks."""

    def __init__(self, line: int, order: int, operation: str) -> None:
        self.line = line
        self.order = order
        self.operation = operation


class Source:
    """Source text Monaco displays: file, startLine, endLine, and text with each call marked."""

    _SKIP = {"if", "for", "while", "function", "def", "switch", "catch", "constructor"}
    _SKIP_RECEIVER = {"console", "Math", "JSON", "Object", "Promise", "Array", "expect", "vi"}

    def __init__(self, path: str, line_start: int, line_end: int, root: str = "") -> None:
        self.file = path
        self.start_line = line_start
        self.end_line = line_end
        self.root = root
        self.calls: list[Call] = []
        self._text: str | None = None

    @property
    def startLine(self) -> int:
        return self.start_line

    @property
    def endLine(self) -> int:
        return self.end_line

    @property
    def language(self) -> str:
        if self.file.endswith(".py"):
            return "python"
        if self.file.endswith(".ts") or self.file.endswith(".tsx"):
            return "typescript"
        return "javascript"

    @property
    def text(self) -> str:
        if self._text is None:
            raw = self._read()
            self.load_calls(raw)
            self._text = self.insert_calls(raw)
        return self._text

    @property
    def contents(self) -> str:
        return self.text

    def load_calls(self, raw: str) -> None:
        self.calls = []
        for index, line in enumerate(raw.splitlines()):
            self._calls_on_line(line, index + 1)

    def insert_calls(self, raw: str) -> str:
        lines = raw.splitlines()
        for call in self.calls:
            index = call.line - 1
            marker = f"/* call:{call.operation} */"
            if 0 <= index < len(lines) and marker not in lines[index]:
                lines[index] = f"{lines[index]} {marker}"
        return "\n".join(lines)

    def align_to_label(self, label: str) -> None:
        """Point this slice at the call that contains the step label, through that call's close."""
        quote = label.split(" ", 1)[1] if " " in label else label
        lines = self._file_lines()
        if not quote or not lines:
            return
        hits = [index for index, line in enumerate(lines) if quote in line]
        if not hits:
            return
        chosen = min(hits, key=lambda index: (abs(index + 1 - self.start_line), index))
        self.start_line = chosen + 1
        self.end_line = self._call_end(lines, chosen)
        self._text = None

    def widen_to_call_close(self) -> None:
        """Extend ``end_line`` through the call or block that starts on ``start_line``."""
        lines = self._file_lines()
        if not lines:
            return
        start_index = max(0, self.start_line - 1)
        closed = self._call_end(lines, start_index)
        if closed > self.end_line:
            self.end_line = closed
        self._text = None

    def align_to_example_export(self, root: str, name: str) -> None:
        """Point this slice at the fixture named ``name`` under ``root``: a fixture function, or an exported constant
        such as ``export const DONE = {...}``. A story test imports both from its examples file, so an example it
        names belongs there, not at the test that uses it."""
        if not root or not name:
            return
        root_path = Path(root)
        if not root_path.is_dir():
            return
        function = re.compile(rf"(?:export\s+)?function\s+{re.escape(name)}\b")
        constant = re.compile(rf"\bexport\s+const\s+{re.escape(name)}\b")
        for path in sorted(root_path.rglob("*.ts")):
            if any(part in {"node_modules", "dist", "build"} for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            for index, line in enumerate(lines, start=1):
                if function.search(line):
                    end = self._call_end(lines, index - 1)
                elif constant.search(line):
                    end = self._declaration_end(lines, index - 1)
                else:
                    continue
                self.file = path.relative_to(root_path).as_posix()
                self.root = root
                self.start_line = index
                self.end_line = end
                self._text = None
                return

    def _declaration_end(self, lines: list[str], start: int) -> int:
        """The line a declaration ends on: the first from start where its braces, brackets and parentheses are all
        closed, so a multi-line object or list is read whole."""
        paren = 0
        brace = 0
        bracket = 0
        quote = ""
        for index in range(start, len(lines)):
            line = lines[index]
            paren, brace, quote, _ = self._scan_call(line, paren, brace, quote)
            bracket += line.count("[") - line.count("]")
            if paren <= 0 and brace <= 0 and bracket <= 0 and not quote:
                return index + 1
        return len(lines)

    def _file_lines(self) -> list[str]:
        full = self._full_path()
        if full is None:
            return []
        if full.is_dir():
            lines: list[str] = []
            for path in sorted(full.rglob("*")):
                if path.suffix.lower() not in {".ts", ".tsx", ".js", ".py"} or not path.is_file():
                    continue
                lines.append(f"// {path.relative_to(full).as_posix()}")
                lines.extend(path.read_text(encoding="utf-8").splitlines())
            return lines
        return full.read_text(encoding="utf-8").splitlines()

    def _directory(self) -> bool:
        full = self._full_path()
        return full is not None and full.is_dir()

    def _full_path(self) -> Path | None:
        if not self.root or not self.file or self.file == ".":
            return None
        full = Path(self.root, self.file)
        return full if full.exists() else None

    def _call_end(self, lines: list[str], start: int) -> int:
        paren = 0
        brace = 0
        quote = ""
        opened = False
        for index in range(start, len(lines)):
            paren, brace, quote, saw_paren = self._scan_call(lines[index], paren, brace, quote)
            opened = opened or saw_paren
            if opened and paren <= 0 and brace <= 0:
                return index + 1
        return max(self.end_line, start + 1)

    def _scan_call(self, line: str, paren: int, brace: int, quote: str) -> tuple[int, int, str, bool]:
        saw_paren = False
        index = 0
        while index < len(line):
            char = line[index]
            if quote:
                if char == "\\":
                    index += 2
                    continue
                if char == quote:
                    quote = ""
            elif char in "\"'`":
                quote = char
            elif char == "(":
                paren += 1
                saw_paren = True
            elif char == ")":
                paren -= 1
            elif char == "{":
                brace += 1
            elif char == "}":
                brace -= 1
            index += 1
        return paren, brace, quote, saw_paren

    def _read(self) -> str:
        lines = self._file_lines()
        if not lines:
            return ""
        if self._directory():
            return "\n".join(lines)
        return "\n".join(lines[max(0, self.start_line - 1) : self.end_line])

    def _calls_on_line(self, line: str, line_number: int) -> None:
        order = 0
        for found in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?)\s*\(", line):
            name = found.group(1)
            receiver = name.split(".", 1)[0] if "." in name else ""
            method = name.rsplit(".", 1)[-1]
            if method in self._SKIP or receiver in self._SKIP_RECEIVER or self._declares(line, found.start()):
                continue
            order += 1
            self.calls.append(Call(line_number, order, name))

    def _declares(self, line: str, start: int) -> bool:
        return re.search(r"(?:async|function|def|public|private|protected|static|get|set)\s+$", line[:start]) is not None


class Filter:
    """Narrows a loaded graph. A practice choice reads that practice's node queries, and a node-type choice sets the relationships and rules."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.practices: list[str] = []
        self._node_types: list[str] = []
        self._relationships: list[str] = []
        self._rules: list[str] = []
        self.violations = False
        self.relationships_selected = False
        self.name = ""
        self.paths: list[str] = []

    @property
    @data_field
    def node_types(self) -> list[str]:
        """The node types chosen, or offered once practices are chosen."""
        return self._node_types

    @node_types.setter
    def node_types(self, node_types: list[str]) -> None:
        self._node_types = list(node_types)

    @property
    @data_field
    def relationships(self) -> list[str]:
        """The edge kinds the chosen node types sit on, or those chosen."""
        return self._relationships

    @relationships.setter
    def relationships(self, relationships: list[str]) -> None:
        self._relationships = list(relationships)

    @property
    @data_field
    def rules(self) -> list[str]:
        """The rules the chosen node types run or fail, or those chosen."""
        return self._rules

    @rules.setter
    def rules(self, rules: list[str]) -> None:
        self._rules = list(rules)

    def clear(self) -> None:
        self.practices = []
        self.node_types = []
        self.relationships = []
        self.rules = []
        self.violations = False
        self.relationships_selected = False

    def select_rules(self, rules: list[str]) -> None:
        self.rules = list(rules)

    def select_violations(self) -> None:
        """Keep nodes that fail one of the selected rules."""
        self.violations = True

    def select_relationships(self, relationships: list[str]) -> None:
        """Keep nodes that sit on one of these edges."""
        self.relationships = list(relationships)
        self.relationships_selected = True

    def select_practices(self, practices: list[str]) -> None:
        self.violations = False
        self.relationships_selected = False
        self.practices = list(practices)
        self.node_types = self._available_node_types()
        self._fill_from_nodes()

    def select_node_types(self, node_types: list[str]) -> None:
        self.violations = False
        self.relationships_selected = False
        self.node_types = list(node_types)
        self._fill_from_nodes()

    def _scope(self) -> list[str]:
        if self.practices:
            return list(self.practices)
        return list(self.graph.practices)

    def _available_node_types(self) -> list[str]:
        found: list[str] = []
        for name in self._scope():
            practice = self.graph.practices.get(name)
            if practice is None:
                continue
            for node_type in practice.node_types:
                if node_type not in found:
                    found.append(node_type)
        return found

    def _available_relationships(self) -> list[str]:
        types = set(self.node_types or self._available_node_types())
        found: list[str] = []
        for name in self._scope():
            practice = self.graph.practices.get(name)
            if practice is None:
                continue
            ordered = sorted(practice.edge_types.values(), key=lambda edge_type: edge_type.order)
            for edge_type in ordered:
                if edge_type.kind in found:
                    continue
                edges = practice.edges.get(edge_type.kind, [])
                if any(edge.parent.type in types or edge.child.type in types for edge in edges):
                    found.append(edge_type.kind)
        return found

    def _available_rules(self) -> list[str]:
        from harness.graph.schema_rules import active_overlay_patterns, qualified_rule_label

        types = set(self.node_types or self._available_node_types())
        patterns = active_overlay_patterns(tuple(self.graph.overlays))
        found: set[str] = set()
        for name in self._scope():
            practice = self.graph.practices.get(name)
            if practice is None:
                continue
            for rule, bound in practice.applicable.items():
                for node_type in bound:
                    if node_type not in types:
                        continue
                    found.add(qualified_rule_label(name, node_type, rule, patterns))
            for type_name, nodes in practice.nodes.items():
                if type_name not in types:
                    continue
                for node in nodes:
                    for slug in node.failed_rules:
                        found.add(qualified_rule_label(name, type_name, slug, patterns))
        return sorted(found)

    def _fill_from_nodes(self) -> None:
        self.relationships = self._available_relationships()
        self.rules = self._available_rules()

    def narrowed_by(self, request: dict) -> Filter:
        """This filter with a request's keys applied: practice(s), type(s), name, rules, relationships, violations, and
        path(s). The practices and node types chosen here hold where the request names none; chosen violations and
        relationships hold over the request's."""
        narrowed = Filter(self.graph)
        narrowed.practices = _listed(request, "practices", "practice") if _names(request, "practices", "practice") else (self._scope() if self.practices else [])
        narrowed.node_types = _listed(request, "types", "type") if _names(request, "types", "type") else list(self.node_types)
        narrowed.name = request.get("name") or ""
        narrowed.paths = _listed(request, "paths", "path")
        narrowed.violations = self.violations or bool(request.get("violations"))
        narrowed.rules = list(self.rules) if self.violations else list(request.get("rules") or [])
        narrowed.relationships = list(self.relationships) if self.relationships_selected else list(request.get("relationships") or [])
        narrowed.relationships_selected = bool(narrowed.relationships)
        return narrowed

    def matches(self, node: Node) -> bool:
        """True when the node is of a chosen practice and type, has the chosen name, fails a chosen rule when only
        violations are wanted, sits on a chosen relationship, and lies under a chosen path."""
        if node.type == "Practice" or node.type == node.name:
            return False
        if self.name and node.name != self.name:
            return False
        if self.node_types and node.type not in self.node_types:
            return False
        if self.practices and node.practice.name not in self.practices:
            return False
        if self.violations and not self._fails_selected_rule(node):
            return False
        if self.relationships and not self._on_relationship(node):
            return False
        return not self.paths or _under_any(node.source.file, self.paths)

    def _fails_selected_rule(self, node: Node) -> bool:
        hits = node.failed_rules
        if not hits:
            return False
        if not self.rules:
            return True
        return any(self._label_hits(node, label, hits) for label in self.rules)

    def _label_hits(self, node: Node, label: str, hits: list[str]) -> bool:
        parts = label.split(".")
        if len(parts) < 3:
            return label in hits
        slug = parts[-1]
        node_type = parts[-2]
        practice = parts[-3]
        if slug not in hits or node.type != node_type:
            return False
        return node.practice.name == practice

    def _on_relationship(self, node: Node) -> bool:
        for kind in self.relationships:
            for edge in node.practice.edges.get(kind, []):
                if edge.parent is node or edge.child is node:
                    return True
        return False


def _names(request: dict, many: str, one: str) -> bool:
    return many in request or one in request


def _listed(request: dict, many: str, one: str) -> list[str]:
    """A request key that takes a list or a single value, such as ``types`` or ``type``."""
    return list(request.get(many) or ([request[one]] if request.get(one) else []))


class Node:
    """children is the list populate writes on this node. Direct edges are the children. Grouped and relationship edges sit under one child named for the kind.

    A loader that parsed the code or document behind a node hands the node that parsed object as ``model``: rules read
    its measurements straight from it. ``data`` holds only what the parsed object does not know, such as the facts a
    model document adds. A graph reloaded from ``graph.json`` has no ``model``; its saved facts are in ``data``.
    """

    graph_facts: tuple[str, ...] = ()
    """The attributes of a parsed object that save with the graph, so a reloaded graph still answers ``get_fact``."""

    def __init__(self, practice: PracticeGraph, type: str, node_id: str, name: str, source: Source) -> None:
        self.practice = practice
        self.type = type
        self.node_id = node_id
        self.name = name
        self.source = source
        self.stage = ""
        self.data: dict = {}
        self.model: Node | None = None
        self.children: list[Node] = []
        self.parent: Node | None = None
        self._rules = None
        self._populated = False

    def set_fact(self, key: str, value) -> None:
        """Record one fact on this node for rules to read; facts save with the graph."""
        self.data[key] = value

    def get_fact(self, key: str, default=None):
        """This node's fact, else the nearest ancestor's: a fact a whole file owns lives once, on the file's top node."""
        node = self
        while node is not None:
            if node._model_has(key):
                return getattr(node.model, key)
            if key in node.data:
                return node.data[key]
            node = node.parent or node.practice.direct_parent(node)
        return default

    def has_fact(self, key: str) -> bool:
        """True when this node itself records the fact."""
        return self._model_has(key) or key in self.data

    @property
    def facts(self) -> dict:
        """Every fact this node records: its parsed object's saved attributes, then ``data``. This is what ``graph.json`` keeps."""
        model = self.model
        found = {} if model is None else {name: getattr(model, name) for name in model.graph_facts if hasattr(model, name)}
        found.update(self.data)
        return found

    def _model_has(self, key: str) -> bool:
        return self.model is not None and key in self.model.graph_facts and hasattr(self.model, key)

    @property
    def fidelity(self) -> str:
        """The fidelity that creates this node, from its practice's schema; empty when the schema gives none."""
        return next(iter(self.fidelities), "")

    @property
    def fidelities(self) -> list[str]:
        """The fidelity that creates this node and every higher fidelity of its practice."""
        from harness.graph.schema_rules import fidelities_for_type

        return fidelities_for_type(self.practice.name, self.type)

    @property
    def rules(self):
        """Schema rules for this node, with violations on each entry."""
        from harness.graph.node_rules import attach_node_rules

        if self._rules is None:
            attach_node_rules(self)
        return self._rules

    @property
    def failed_rules(self) -> list[str]:
        return self.rules.failed_slugs

    @property
    def passing_rules(self) -> list[str]:
        """Rules that apply to this node and did not fail."""
        return self.rules.passing_slugs

    @staticmethod
    def fact(row: Tuple) -> dict | None:
        if len(row) < 7:
            return None
        node_id, name, semantic_type, practice, file, line, end_line = (row + [""] * 7)[:7]
        if not node_id or not semantic_type:
            return None
        practice_name = str(practice).strip()
        from harness.guidance.practice_catalogue import PracticeCatalogue

        if not PracticeCatalogue.has(practice_name):
            return None
        from harness.graph.node_data import decode_node_data

        return {
            "node_id": node_id,
            "name": name,
            "semantic_type": semantic_type,
            "practice": practice_name,
            "file": file,
            "line": int(line or 1),
            "end_line": int(end_line or 1),
            "stage": Node._stage_cell(row),
            "data": decode_node_data(row),
        }

    @classmethod
    def from_fact(cls, practice: PracticeGraph, row: dict) -> Node:
        node = Node(
            practice,
            row["semantic_type"],
            row["node_id"],
            row["name"],
            Source(row["file"], row["line"], row["end_line"], practice.source_root),
        )
        node.stage = str(row.get("stage") or "")
        node.data = dict(row.get("data") or {})
        if row["semantic_type"] in {"Step", "Given", "When", "Then"}:
            node.source.align_to_label(row["name"])
        elif row["semantic_type"] in {"Scenario", "Story", "Background"}:
            node.source.widen_to_call_close()
        elif row["semantic_type"] == "Example":
            node.source.align_to_example_export(practice.source_root, row["name"])
        return node

    @staticmethod
    def _stage_cell(row: Tuple) -> str:
        for cell in row[7:]:
            if cell in {"discovery", "specification", "implementation"}:
                return str(cell)
        return ""

    def populate(self, parent: Node | None = None) -> None:
        if parent is not None:
            parent.children.append(self)
            if self.parent is None or (self._holder(self.parent) and not self._holder(parent)):
                self.parent = parent
        if self._populated:
            return
        self._populated = True
        types = sorted(self.practice.edge_types.values(), key=lambda edge_type: edge_type.order)
        for edge_type in types:
            for edge in self._edges_in_source_order(edge_type.kind):
                if edge.display == "direct":
                    edge.child.populate(self)
                else:
                    holder = self._child_named(edge.kind)
                    if holder is None:
                        holder = self._new_kind_node(edge.kind)
                        holder.parent = self
                        self.children.append(holder)
                    edge.child.populate(holder)

    def _edges_in_source_order(self, kind: str) -> list[Edge]:
        matched = self.practice.edges_from(kind, self)
        ordered = sorted((edge for edge in matched if self._follows_source(edge)), key=self._source_position)
        cursor = 0
        placed: list[Edge] = []
        for edge in matched:
            if self._follows_source(edge):
                placed.append(ordered[cursor])
                cursor += 1
            else:
                placed.append(edge)
        return placed

    def _follows_source(self, edge: Edge) -> bool:
        return edge.child.type in {"Background", "Scenario", "Step", "Story"}

    def _source_position(self, edge: Edge) -> tuple:
        source = edge.child.source
        return (source.file, source.start_line, edge.child.node_id)

    def _holder(self, node: Node) -> bool:
        return node.type == node.name

    def _child_named(self, name: str) -> Node | None:
        for child in self.children:
            if child.name == name:
                return child
        return None

    def serialize(self, seen: set[str] | None = None, via: Node | None = None, stack: set[str] | None = None) -> ExplorerEntry:
        """Write the full child list once, on the home parent.

        A relationship copy is empty. A node already on the path is a stub, so a call back to this step stops.
        """
        seen = set() if seen is None else seen
        stack = set() if stack is None else stack
        if self.node_id in stack:
            return ExplorerEntry(self)
        home = via is None or via is self.parent
        first_home = home and self.node_id not in seen
        children = self.children if first_home else []
        if first_home:
            seen.add(self.node_id)
        path = stack | {self.node_id}
        written = [child.serialize(seen, self, path) for child in children]
        if first_home:
            category = self.rule_category()
            if category is not None:
                written.append(category)
        return ExplorerEntry(self, written)

    def rule_category(self) -> ExplorerEntry | None:
        """Applicable rules as one child category. A violation filter keeps the rules that failed."""
        if self.type == self.name or self.type == "Practice":
            return None
        rows = self.rule_rows()
        if not rows:
            return None
        return RuleCategory(self, rows)

    def rule_rows(self, violations_only: bool | None = None, selected: list[str] | None = None) -> list[RuleEntry]:
        """One rule child: status violating, passing, or prompt, and every stored hit.

        Only violating rows (of the selected rules) come back when ``violations_only`` is set;
        left out, both follow the graph filter.
        """
        graph = self.practice.graph
        if violations_only is None:
            violations_only = bool(graph and graph.filter.violations)
        if selected is None:
            selected = list(graph.filter.rules) if graph else []
        rows: list[RuleEntry] = []
        for slug in self.rules.slugs:
            entry = self.rules.entries.get(slug)
            hits = [RuleHit.from_stored(hit) for hit in getattr(entry, "hits", []) or []]
            if hits:
                status = "violating"
            elif not getattr(entry, "executable", True):
                status = "prompt"
            else:
                status = "passing"
            if violations_only and (status != "violating" or (selected and slug not in selected)):
                continue
            rows.append(RuleEntry(self, slug, status, hits))
        return rows

    def _new_kind_node(self, kind: str) -> Node:
        return Node(self.practice, kind, f"{self.practice.name}:{kind}:{self.node_id}", kind, self.source)


class PracticeGraph:
    """An edge is recorded only when both ends are already registered."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.nodes: dict[str, list[Node]] = {}
        self.edges: dict[str, list[Edge]] = {}
        self.node_types: set[str] = set()
        self.edge_types: dict[str, EdgeType] = {}
        self.by_id: dict[str, Node] = {}
        self.rules_run: list[str] = []
        self.applicable: dict[str, list[str]] = {}
        self.loaded: list[str] = []
        self.source_root = ""
        self.graph: Graph | None = None
        self.root_node = Node(self, "Practice", f"{name}:Practice:.:{name}", name, Source(".", 0, 0))
        # Lookup indexes over self.edges, rebuilt when a kind's list is replaced or grows elsewhere.
        self._edge_pairs: dict[str, tuple[tuple[int, int], set[tuple[int, int]]]] = {}
        self._edges_by_parent: dict[str, tuple[tuple[int, int], dict[int, list[Edge]]]] = {}
        self._direct_parents: tuple[tuple, dict[int, Node]] = ((), {})

    def bind_rule(self, rule: str, types: list[str]) -> None:
        current = self.applicable.setdefault(rule, [])
        for node_type in types:
            if node_type not in current:
                current.append(node_type)

    def rules_for(self, node_type: str) -> list[str]:
        return [rule for rule, types in self.applicable.items() if node_type in types]

    @property
    @data_field
    def node_counts(self) -> dict[str, int]:
        """How many nodes of each type this practice holds."""
        return {type: self.node_count(type) for type in self.node_types}

    @property
    @data_field
    def edge_count(self) -> int:
        return sum(len(edges) for edges in self.edges.values())

    @property
    @data_field(key="node_types")
    def node_type_names(self) -> list[str]:
        """The node types this practice holds, sorted by name."""
        return sorted(self.node_types)

    @property
    @data_field(key="edge_types")
    def edge_type_kinds(self) -> list[str]:
        """The edge kinds this practice holds, in the order the explorer tree shows them."""
        ordered = sorted(self.edge_types.values(), key=lambda edge_type: edge_type.order)
        return [edge_type.kind for edge_type in ordered]

    @property
    @data_field(key="rules")
    def rule_labels(self) -> list[str]:
        """Each rule this practice runs, named ``practice.node.rule`` with the pattern that owns it in front."""
        from harness.graph.schema_rules import active_overlay_patterns, qualified_rule_labels

        patterns = active_overlay_patterns(tuple(self.graph.overlays)) if self.graph is not None else ()
        return qualified_rule_labels(self.name, self.applicable, patterns)

    @property
    @data_field
    def tree(self) -> ExplorerEntry:
        """The explorer tree, from this practice's root."""
        return self.root_node.serialize()

    def apply_nodes(self, tuples: list[Tuple], models: dict[str, Node] | None = None) -> None:
        """Register a node for each record. ``models`` gives, by node id, the parsed object a loader read the node from."""
        from harness.graph.node_rules import attach_node_rules
        from harness.graph.schema_rules import bind_practice_rules

        bind_practice_rules(self)
        models = models or {}
        for row in tuples:
            fact = Node.fact(row)
            if fact is None or fact["node_id"] in self.by_id:
                continue
            self.node_types.add(fact["semantic_type"])
            node = Node.from_fact(self, fact)
            node.model = models.get(fact["node_id"])
            attach_node_rules(node)
            self.nodes.setdefault(fact["semantic_type"], []).append(node)
            self.by_id[fact["node_id"]] = node

    def registered(self, node_id: str) -> Node | None:
        local = self.by_id.get(node_id)
        if local is not None:
            return local
        if self.graph is None:
            return None
        for practice in self.graph.practices.values():
            node = practice.by_id.get(node_id)
            if node is not None:
                return node
        return None

    def apply_edges(self, tuples: list[Tuple]) -> None:
        for row in tuples:
            fact = Edge.fact(row)
            if fact is None:
                continue
            parent = self.registered(fact["parent_id"])
            child = self.registered(fact["child_id"])
            if parent is None or child is None:
                continue
            parent.practice.record(fact, parent, child)
            if parent.practice is not child.practice:
                child.practice.record(fact, child, parent)

    def record(self, fact: dict, parent: Node, child: Node) -> None:
        kind = fact["kind"]
        list_ = self.edges.setdefault(kind, [])
        pairs = self._pairs_of(kind, list_)
        if (id(parent), id(child)) in pairs:
            return
        if kind not in self.edge_types:
            self.edge_types[kind] = EdgeType(kind, fact["order"], fact["display"])
        list_.append(Edge(kind, fact["order"], fact["display"], parent, child))
        pairs.add((id(parent), id(child)))
        self._edge_pairs[kind] = ((id(list_), len(list_)), pairs)

    def edges_from(self, kind: str, parent: Node) -> list[Edge]:
        """Edges of one kind leaving this parent, in recorded order."""
        list_ = self.edges.get(kind, [])
        state = (id(list_), len(list_))
        cached = self._edges_by_parent.get(kind)
        if cached is None or cached[0] != state:
            by_parent: dict[int, list[Edge]] = {}
            for edge in list_:
                by_parent.setdefault(id(edge.parent), []).append(edge)
            cached = (state, by_parent)
            self._edges_by_parent[kind] = cached
        return cached[1].get(id(parent), [])

    def direct_parent(self, child: Node) -> Node | None:
        """The node a direct edge hangs this child under; available before populate sets ``parent``."""
        state = tuple((kind, id(list_), len(list_)) for kind, list_ in self.edges.items())
        if self._direct_parents[0] != state:
            parents: dict[int, Node] = {}
            for list_ in self.edges.values():
                for edge in list_:
                    if edge.display == "direct":
                        parents.setdefault(id(edge.child), edge.parent)
            self._direct_parents = (state, parents)
        return self._direct_parents[1].get(id(child))

    def _pairs_of(self, kind: str, list_: list[Edge]) -> set[tuple[int, int]]:
        state = (id(list_), len(list_))
        cached = self._edge_pairs.get(kind)
        if cached is None or cached[0] != state:
            cached = (state, {(id(edge.parent), id(edge.child)) for edge in list_})
            self._edge_pairs[kind] = cached
        return cached[1]

    def node_count(self, type: str) -> int:
        return len(self.nodes.get(type, []))

    def rebuild_tree(self) -> None:
        """Rebuild the explorer tree from edge facts after late-bound nodes or overlays."""
        for node in self.by_id.values():
            node.children = []
            node.parent = None
            node._populated = False
        self.root_node.populate()

    def apply_rules(self, rule: str, tuples: list[Tuple]) -> None:
        self.rules_run.append(rule)
        for row in tuples:
            slug, node_id, violation = (row + [""] * 3)[:3]
            if not slug or not node_id or not violation:
                continue
            node = self.registered(node_id)
            if node is None:
                continue
            existing = [message for s, message in node.rules.violations if s == slug]
            if violation in existing:
                continue
            node.rules.record_violation(slug, violation)

    def nodes_for_rule(self, rule: str) -> list[Node]:
        found = []
        for nodes in self.nodes.values():
            for node in nodes:
                if rule in node.failed_rules:
                    found.append(node)
        return found



class Inventory:
    """Every loaded practice, with the pattern overlays applied and those available."""

    def __init__(self, practices: dict[str, PracticeGraph], overlays: list[str], available_overlays: list[str]) -> None:
        self._practices = dict(practices)
        self._overlays = list(overlays)
        self._available_overlays = list(available_overlays)

    @property
    @data_field
    def practices(self) -> dict[str, PracticeGraph]:
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


@language_adapter(language="typescript")
@agent_toolset
class Graph:
    """One graph. Builders fill nodes, edges, and rules. The explorer reads the tree."""

    _current: Graph | None = None

    def __init__(self) -> None:
        self._folder: Path | None = None
        self._practice_roots: dict[str, Path] = {}
        self._scope: list[Path] | None = None
        self.practices: dict[str, PracticeGraph] = {}
        self.filter = Filter(self)
        self.overlays: list[str] = []

    @classmethod
    @tool_subject
    def current(cls) -> Graph:
        """The graph this process holds: one per cdd server, loaded and filtered by the calls made to it."""
        if cls._current is None:
            cls._current = cls()
        return cls._current

    def report_progress(self, message: str) -> None:
        """Tell whoever called the running tool which practice, file, node, or rule is in progress."""
        report_progress(message)

    @property
    @data_field
    def folder(self) -> str:
        return "" if self._folder is None else str(self._folder)

    @property
    @data_field(key="overlays")
    def applied_overlays(self) -> list[str]:
        return list(self.overlays)

    def practice(self, name: str) -> PracticeGraph:
        practice = self.practices.setdefault(name, PracticeGraph(name))
        practice.graph = self
        return practice

    @mcp
    @agent_tool
    def load_working_copy(
        self,
        folder: str,
        practices: dict[str, str],
        database: str | None = None,
        overlays: list[str] | None = None,
        force: bool = False,
    ) -> GraphLoaded:
        """Open each practice on its source root and build the explorer tree.

        A saved graph in the folder's ``.context`` is used when it already holds
        every requested practice (extra cached practices are fine), the practice
        source roots match, and those roots plus the rule files are not newer
        than the cache. A forced load always rebuilds. Every rebuild merges into
        the serialized graph so other practices already cached stay put.
        """
        self._folder = Path(database or folder).resolve()
        self._practice_roots = {name: (Path(folder) / root).resolve() for name, root in practices.items()}
        self.overlays = _normalize_overlay_list(list(overlays or []))
        self.report_progress("Checking the saved graph")
        if not force and self._saved_graph_is_current():
            self.report_progress("Loading the saved graph")
            self._load_saved_json()
            return GraphLoaded("Loaded the saved graph.")
        self._scope = None
        self.report_progress("Scanning the folder")
        self._build_working_copy()
        self.report_progress("Saving the graph")
        self.save_json()
        return GraphLoaded("Loaded the working copies.")

    @mcp
    @command(name="load-files")
    @agent_tool
    def load_files(
        self,
        folder: str,
        practices: list[str],
        files: list[str],
        overlays: list[str] | None = None,
    ) -> GraphLoaded:
        """Build each practice from only the given files and run its rules on them.

        ``files`` are files or folders, relative to ``folder`` or absolute; a folder
        stands for the source files under it. Use it for the files being edited:
        it reads them as they are now and never touches the saved graph.
        """
        self._folder = Path(folder).resolve()
        self._practice_roots = {name: self._folder for name in practices}
        self.overlays = _normalize_overlay_list(list(overlays or []))
        self._scope = self._scoped_files(files)
        self.report_progress("Reading the edited files")
        self._build_working_copy()
        return GraphLoaded(f"Loaded {len(self._scope)} edited files.")

    def edited_files(self) -> list[Path] | None:
        """The files a ``load_files`` reads; ``None`` when the whole folder loads."""
        return None if self._scope is None else list(self._scope)

    def scoped(self, found: list[Path]) -> list[Path]:
        """The files of ``found`` this load reads: all of them, or only the edited ones."""
        if self._scope is None:
            return found
        wanted = set(self._scope)
        return [path for path in found if path.resolve() in wanted]

    def scope_folders(self) -> list[Path] | None:
        """Folders holding the edited files, up to the loaded folder; ``None`` when the whole folder loads."""
        if self._scope is None or self._folder is None:
            return None
        folders: set[Path] = set()
        for path in self._scope:
            folders.update(parent for parent in path.parents if parent != self._folder and self._folder in parent.parents)
        return sorted(folders)

    def _scoped_files(self, files: list[str]) -> list[Path]:
        folder = self._folder or Path()
        found: list[Path] = []
        for item in files:
            path = Path(item) if Path(item).is_absolute() else folder / item
            path = path.resolve()
            # The loaded folder itself, such as ".", stands for every source file under it.
            if path != folder.resolve() and folder.resolve() not in path.parents:
                continue
            if path.is_dir():
                found.extend(item.resolve() for item in scanned_files(path))
            elif path.is_file():
                found.append(path)
        return sorted(set(found))

    def write_json(self, path: str) -> str:
        """Write this graph alone to ``path``, without merging into the folder's saved graph."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self._graph_document(), separators=(",", ":")), encoding="utf-8")
        return str(target)

    @mcp
    @agent_tool
    def save_json(self) -> GraphSaved:
        """Write the serialized graph into the loaded folder's ``.context``.

        Practices already on disk that are not part of this load stay in the file.
        """
        folder = self._folder
        if folder is None:
            return GraphSaved("")
        path = self._graph_json_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._merged_graph_document(), separators=(",", ":")), encoding="utf-8")
        return GraphSaved(str(path))

    def _build_working_copy(self) -> None:
        self.practices = {}
        for name, source in self._practice_roots.items():
            practice = self.practice(name)
            practice.source_root = str(source)
            practice.by_id[practice.root_node.node_id] = practice.root_node
        from harness.graph.working_copy import fill_working_copy

        fill_working_copy(self)
        for practice in self.practices.values():
            practice.root_node.populate()

    def _graph_json_path(self) -> Path:
        folder = self._folder or Path()
        return folder / ".context" / _GRAPH_JSON_NAME

    def _graph_document(self) -> dict:
        return {
            "overlays": list(self.overlays),
            "practices": {name: self._practice_document(practice) for name, practice in self.practices.items()},
        }

    def _merged_graph_document(self) -> dict:
        document = self._graph_document()
        existing = self._read_saved_graph() or {}
        saved = existing.get("practices")
        if not isinstance(saved, dict):
            return document
        practices = dict(saved)
        practices.update(document["practices"])
        return {"overlays": list(self.overlays), "practices": practices}

    def _practice_document(self, practice: PracticeGraph) -> dict:
        nodes = [node for group in practice.nodes.values() for node in group]
        edges = [edge for group in practice.edges.values() for edge in group]
        from harness.graph.node_data import encode_node_data

        return {
            "source_root": practice.source_root,
            # Facts about the practice as a whole, such as the Clean Engineering model's members, live on its root.
            "root_facts": encode_node_data(practice.root_node.facts),
            "nodes": [self._node_row(node) for node in nodes],
            "edges": [self._edge_row(edge) for edge in edges],
            "rules": [[slug, node.node_id, message] for node in nodes for slug, message in node.rules.violations],
        }

    def _node_row(self, node: Node) -> list:
        from harness.graph.node_data import encode_node_data

        return [
            node.node_id,
            node.name,
            node.type,
            node.practice.name,
            node.source.file,
            node.source.start_line,
            node.source.end_line,
            node.stage,
            encode_node_data(node.facts),
        ]

    def _edge_row(self, edge: Edge) -> list:
        return [edge.parent.node_id, edge.child.node_id, edge.kind, edge.order, edge.display]

    def _saved_graph_is_current(self) -> bool:
        document = self._read_saved_graph()
        if document is None or not self._saved_graph_matches_request(document):
            return False
        stamp = self._graph_json_path().stat().st_mtime
        if self._rules_changed_since(stamp):
            return False
        return not self._practice_roots_are_dirty(stamp)

    def _saved_graph_matches_request(self, document: dict) -> bool:
        saved = document.get("practices")
        if not isinstance(saved, dict):
            return False
        if not set(self._practice_roots).issubset(set(saved)):
            return False
        for name, source in self._practice_roots.items():
            row = saved.get(name)
            if not isinstance(row, dict):
                return False
            if Path(str(row.get("source_root") or "")).resolve() != Path(source).resolve():
                return False
        return list(document.get("overlays") or []) == list(self.overlays)

    def _read_saved_graph(self) -> dict | None:
        path = self._graph_json_path()
        if not path.is_file():
            return None
        self.report_progress("Reading the saved graph")
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(document, dict):
            return None
        return document

    def _rules_changed_since(self, stamp: float) -> bool:
        practices = _REPO / "cdd_guidance" / "practices"
        if practices.is_dir() and self._rule_file_newer_than(practices, stamp):
            return True
        patterns = _REPO / "cdd_guidance" / "patterns"
        if patterns.is_dir() and self._rule_file_newer_than(patterns, stamp):
            return True
        graph_dir = Path(__file__).resolve().parent
        names = (
            "rules.py",
            "schema_rules.py",
            "node_rules.py",
            "practice_rule.py",
            "practice_rules_registry.py",
            "rule_context.py",
            "graph_rules_collection.py",
        )
        return any(self._file_newer_than(graph_dir / name, stamp) for name in names)

    def _rule_file_newer_than(self, folder: Path, stamp: float) -> bool:
        for dirpath, dirnames, filenames in os.walk(folder):
            dirnames[:] = [name for name in dirnames if name not in SKIPPED_FOLDERS]
            for filename in filenames:
                if not self._is_rule_file(Path(dirpath, filename)):
                    continue
                if Path(dirpath, filename).stat().st_mtime > stamp:
                    return True
        return False

    def _is_rule_file(self, path: Path) -> bool:
        if path.name in _RULE_FILE_NAMES:
            return True
        return path.suffix == ".py" and "rules" in path.parts

    def _practice_roots_are_dirty(self, stamp: float) -> bool:
        roots = list(self._practice_roots.values())
        if not roots:
            folder = self._folder
            if folder is None or not folder.exists():
                return True
            return self._path_is_dirty(folder, stamp)
        return any(self._path_is_dirty(root, stamp) for root in roots)

    def _path_is_dirty(self, path: Path, stamp: float) -> bool:
        if not path.exists():
            return True
        if path.is_file():
            return path.stat().st_mtime > stamp
        return self._contents_newer_than(path, stamp)

    def _contents_newer_than(self, folder: Path, stamp: float) -> bool:
        seen = 0
        for dirpath, dirnames, filenames in os.walk(folder):
            dirnames[:] = [name for name in dirnames if not skips_folder(name)]
            for filename in filenames:
                path = Path(dirpath, filename)
                if path.suffix.lower() not in _DIRTY_SUFFIXES:
                    continue
                seen += 1
                if seen == 1 or seen % 400 == 0:
                    self.report_progress(f"Checking folder dates · {seen}")
                if path.stat().st_mtime > stamp:
                    return True
        return False

    def _file_newer_than(self, path: Path, stamp: float) -> bool:
        return path.is_file() and path.stat().st_mtime > stamp

    def _load_saved_json(self) -> None:
        document = self._read_saved_graph() or {}
        saved = document.get("practices") or {}
        self.practices = {}
        for name in self._practice_roots:
            self._restore_practice_nodes(name, saved.get(name) or {})
        for name in self._practice_roots:
            self._restore_practice_links(name, saved.get(name) or {})
        for practice in self.practices.values():
            practice.root_node.populate()
        from harness.graph.rules import attach_rules

        for practice in self.practices.values():
            attach_rules(practice)
            practice.loaded = ["nodes", "edges", "rules"]

    def _restore_practice_nodes(self, name: str, saved: dict) -> None:
        self.report_progress(f"Loading saved {name} nodes")
        practice = self.practice(name)
        practice.source_root = str(saved.get("source_root") or self._practice_roots[name])
        practice.by_id[practice.root_node.node_id] = practice.root_node
        practice.apply_nodes(list(saved.get("nodes") or []))

    def _restore_practice_links(self, name: str, saved: dict) -> None:
        practice = self.practice(name)
        practice.apply_edges(list(saved.get("edges") or []))
        self._restore_rule_hits(practice, list(saved.get("rules") or []))
        practice.loaded = ["nodes", "edges", "rules"]

    def _restore_rule_hits(self, practice: PracticeGraph, rows: list) -> None:
        grouped: dict[str, list] = {}
        for row in rows:
            if len(row) < 3:
                continue
            grouped.setdefault(str(row[0]), []).append(row)
        for slug, hits in grouped.items():
            practice.apply_rules(slug, hits)

    @mcp
    @agent_tool
    def set_overlays(self, overlays: list[str]) -> AppliedOverlays:
        """Apply pattern overlays, folders holding practices/, and rebuild the explorer tree from the open folder; answer with the graph's inventory."""
        self.overlays = _normalize_overlay_list(list(overlays or []))
        if self._folder is not None and self._practice_roots:
            roots = {name: str(path) for name, path in self._practice_roots.items()}
            self.load_working_copy(str(self._folder), roots, database=str(self._folder), overlays=self.overlays)
        label = ", ".join(Path(item).name for item in self.overlays) if self.overlays else "none"
        return AppliedOverlays(f"Applied pattern overlays: {label}.", self.inventory())

    @mcp
    @agent_tool
    def overlay_of(self, folder: str) -> Overlay:
        """Return the pattern overlay folder holds: folder itself or the overlay root above it, which must hold practices/."""
        root = resolve_overlay_root(folder)
        if not (root / "practices").is_dir():
            raise GraphFailure("overlay_of", f"Not an overlay root (missing practices/): {folder}")
        return Overlay(normalize_overlay(str(root)))

    @mcp
    @agent_tool
    def inventory(self) -> Inventory:
        """Return each loaded practice's node and edge counts, node types, rules, and explorer tree, with the overlays applied and those available."""
        return Inventory(self.practices, list(self.overlays), available_pattern_overlays())

    @mcp
    @agent_tool
    def filter_choices(self, practices: list[str], node_types: list[str]) -> Filter:
        """Return the node types, relationships, and rules a filter offers once practices and node types are chosen.
        The graph's own filter is cleared."""
        self.filter.clear()
        offered = Filter(self)
        if practices:
            offered.select_practices(practices)
        if node_types:
            offered.select_node_types(node_types)
        return offered

    @mcp
    @agent_tool
    def source(self, node_id: str) -> NodeSource | None:
        """Return the source of the node node_id: its file, text, and lines, with every class, operation, and property the loaded graph holds, so calls in it can be opened in place. None for an id with no source, such as a rule's row."""
        node = self._node(node_id)
        if node is None:
            return None
        return NodeSource(node, self._members())

    def _node(self, node_id: str) -> Node | None:
        return next((practice.by_id[node_id] for practice in self.practices.values() if node_id in practice.by_id), None)

    def _members(self) -> list[Member]:
        wanted = _CLASS_KINDS | {"Operation", "Property"}
        return [self._member(node) for practice in self.practices.values() for node in practice.by_id.values() if node.type in wanted]

    def _member(self, node: Node) -> Member:
        return Member(node, "" if node.type in _CLASS_KINDS else str(node.get_fact("owner", "") or ""))

    @mcp
    @agent_tool
    @skill(name="read-graph")
    def return_nodes(self, filter: dict | None = None) -> list[FilteredNode]:
        """Return matching graph nodes as JSON, with ancestors, children, and relationships.

        filter keys: practice(s), type(s), name, rules, relationships;
        violations: true returns only failing nodes with only their failing rule rows;
        paths: source path prefixes (relative to the folder, e.g. src/orders) a node must sit under.
        """
        wanted = self.filter.narrowed_by(filter or {})
        found: list[FilteredNode] = []
        seen: set[int] = set()
        for practice in self.practices.values():
            self._collect_nodes(practice.root_node, [], wanted, found, seen)
        return found

    def _collect_nodes(self, node: Node, ancestors: list[str], wanted: Filter, found: list[FilteredNode], seen: set[int]) -> None:
        if id(node) in seen:
            return
        seen.add(id(node))
        chain = [*ancestors, node.name]
        if wanted.matches(node):
            rules = node.rule_rows(wanted.violations or None, list(wanted.rules) or None)
            found.append(FilteredNode(node, ancestors, rules))
        for child in node.children:
            self._collect_nodes(child, chain, wanted, found, seen)

