"""Graph. Practice graphs, nodes, edges, and the explorer tree."""

from __future__ import annotations

import re
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterable, Iterator


from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.progress import report_progress
from harness.guidance.practice_catalogue import PracticeCatalogue, UnknownPractice
from harness.installation.data_class import data_field, language_adapter
from harness.installation.files import command, skill
from harness.mcp.mcp_server import long_call, mcp
from harness.graph.edge import Display, Edge, EdgeType
from harness.graph.graph_build import BuildOrder, BuildStep, WorkerBuild
from harness.graph.explorer import ExplorerEntry, FilteredNode, GraphLoaded, GraphSaved, NodeSource, Overlay, PracticeInventory
from harness.graph.graph_rules_collection import GraphRulesCollection
from harness.graph.pattern_overlays import GraphOverlay, PatternOverlays
from harness.graph.rule_context import RuleCheckContext
from harness.graph.schema_edges import SchemaEdges
from harness.graph.schema_rules import PracticeSchema
from harness.graph.saved_graph import SavedGraph, SavedGraphFile, SavedPractice
from harness.graph.skipped_folders import SKIPPED_FOLDERS, scanned_files

if TYPE_CHECKING:
    from harness.agent_tools.tool_call import ToolCall
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance

# A refresh reads files a practice keeps in `.context` (model documents, bounded contexts, story maps); every other
# skipped folder, such as a session's reports in `.sessions`, holds nothing a practice reads.
_REFRESH_SKIPPED_FOLDERS = SKIPPED_FOLDERS - {".context"}

class GraphFailure(Exception):
    def __init__(self, query: str, detail: str) -> None:
        super().__init__(f"{query}\n{detail}")
        self.query = query
        self.detail = detail


class Call:
    """A call found in source. operation is the callee text Monaco marks."""

    def __init__(self, line: int, order: int, operation: str) -> None:
        self.line = line
        self.order = order
        self.operation = operation


class _BracketDepth:
    """How deep a run of source lines is inside parentheses, braces, and brackets, and the string it is inside, if any,
    read one line after another; brackets inside a string do not count."""

    _QUOTES = "\"'`"
    _OPENING = {"(": ("parens", 1), ")": ("parens", -1), "{": ("braces", 1), "}": ("braces", -1)}

    def __init__(self) -> None:
        self.parens = 0
        self.braces = 0
        self.brackets = 0
        self.quote = ""
        self.opened_call = False

    @property
    def closed(self) -> bool:
        return self.parens <= 0 and self.braces <= 0

    def read(self, line: str) -> None:
        self.brackets += line.count("[") - line.count("]")
        index = 0
        while index < len(line):
            index += self._read_character(line, index)

    def _read_character(self, line: str, index: int) -> int:
        """Read the character at index and answer how many characters it took: two for an escape inside a string."""
        char = line[index]
        if self.quote:
            if char == "\\":
                return 2
            self.quote = "" if char == self.quote else self.quote
        elif char in self._QUOTES:
            self.quote = char
        elif char in self._OPENING:
            name, step = self._OPENING[char]
            setattr(self, name, getattr(self, name) + step)
            self.opened_call = self.opened_call or char == "("
        return 1


class Source:
    """Source text Monaco displays: file, start and end line, and text with each call marked."""

    _SKIP = {"if", "for", "while", "function", "def", "switch", "catch", "constructor"}
    _SKIP_RECEIVER = {"console", "Math", "JSON", "Object", "Promise", "Array", "expect", "vi"}

    def __init__(self, path: str, line_start: int, line_end: int, root: str = "") -> None:
        self.file = path
        self.start_line = line_start
        self.end_line = line_end
        self.root = root
        self.calls: list[Call] = []
        self._text: str | None = None

    @classmethod
    def whole_file(cls, relative: str, root: str) -> Source:
        """Every line of the file at relative under root; one line when it is empty or not there."""
        path = Path(root, relative) if root else None
        text = path.read_text(encoding="utf-8") if path is not None and path.is_file() else ""
        end = text.count("\n") + (0 if not text or text.endswith("\n") else 1)
        return cls(relative, 1, max(1, end), root)

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
            lines = path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines):
                if function.search(line) or constant.search(line):
                    end = self._call_end(lines, index) if function.search(line) else self._declaration_end(lines, index)
                    self._point_at(path.relative_to(root_path).as_posix(), root, index + 1, end)
                    return

    def _point_at(self, file: str, root: str, start_line: int, end_line: int) -> None:
        self.file = file
        self.root = root
        self.start_line = start_line
        self.end_line = end_line
        self._text = None

    def _declaration_end(self, lines: list[str], start: int) -> int:
        """The line a declaration ends on: the first from start where its braces, brackets and parentheses are all
        closed, so a multi-line object or list is read whole."""
        depth = _BracketDepth()
        for index in range(start, len(lines)):
            depth.read(lines[index])
            if depth.closed and depth.brackets <= 0 and not depth.quote:
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
        """The line the call or block that opens at start closes on: the first where its parentheses and braces are
        all closed again after one has opened."""
        depth = _BracketDepth()
        for index in range(start, len(lines)):
            depth.read(lines[index])
            if depth.opened_call and depth.closed:
                return index + 1
        return max(self.end_line, start + 1)

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
    def offered_node_types(self) -> list[str]:
        """Every node type the chosen practices hold, or every loaded practice's when none is chosen."""
        return self._available_node_types()

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

    def change_practices(self, practices: list[str]) -> None:
        """Choose practices in place of those chosen, so a person who narrowed the node types keeps that choice: the
        chosen node types the new practices still hold stay chosen, and every node type of each practice added is
        chosen. A change from or to every practice chooses every node type the new choice holds."""
        before, kept = list(self.practices), set(self.node_types)
        self.select_practices(practices)
        if not before or not practices:
            return
        added = {node_type for key in practices if key not in before for node_type in self._node_types_of(key)}
        self.select_node_types([node_type for node_type in self.node_types if node_type in kept | added])

    def _scope(self) -> list[str]:
        if self.practices:
            return list(self.practices)
        return list(self.graph.practices)

    def _node_types_of(self, key: str) -> list[str]:
        practice = self.graph.practices.get(key)
        return list(practice.in_graph.node_types) if practice is not None else []

    def _available_node_types(self) -> list[str]:
        found: list[str] = []
        for name in self._scope():
            for node_type in self._node_types_of(name):
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
            ordered = sorted(practice.in_graph.edge_types.values(), key=lambda edge_type: edge_type.order)
            for edge_type in ordered:
                if edge_type.kind in found or not edge_type.is_offered:
                    continue
                edges = practice.in_graph.edges(edge_type.kind)
                if any(edge.parent.type in types or edge.child.type in types for edge in edges):
                    found.append(edge_type.kind)
        return found

    def _available_rules(self) -> list[str]:
        types = set(self.node_types or self._available_node_types())
        found: set[str] = set()
        for name in self._scope():
            practice = self.graph.practices.get(name)
            if practice is not None:
                found.update(practice.in_graph.rule_labels_for(types))
        return sorted(found)

    def _fill_from_nodes(self) -> None:
        self.relationships = self._available_relationships()
        self.rules = self._available_rules()

    def narrowed_by(self, request: dict) -> Filter:
        """This filter with a request's keys applied: practice(s), type(s), name, rules, relationships, violations, and
        path(s). The practices and node types chosen here hold where the request names none; chosen violations and
        relationships hold over the request's."""
        narrowed = Filter(self.graph)
        practices = self._listed(request, "practices", "practice")
        narrowed.practices = practices if practices is not None else (self._scope() if self.practices else [])
        types = self._listed(request, "types", "type")
        narrowed.node_types = types if types is not None else list(self.node_types)
        narrowed.name = request.get("name") or ""
        narrowed.paths = self._listed(request, "paths", "path") or []
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
        if self.practices and node.practice.key not in self.practices:
            return False
        if self.violations and not self._fails_selected_rule(node):
            return False
        if self.relationships and not self._on_relationship(node):
            return False
        return not self.paths or self._under_paths(node.source.file)

    def _listed(self, request: dict, many: str, one: str) -> list[str] | None:
        """A request key that takes a list or a single value, such as ``types`` or ``type``; none when it names neither."""
        if many not in request and one not in request:
            return None
        return list(request.get(many) or ([request[one]] if request.get(one) else []))

    def _under_paths(self, file: str | None) -> bool:
        """True when ``file`` is one of the chosen paths or sits under one."""
        location = (file or "").replace("\\", "/").strip("/")
        folders = [str(prefix).replace("\\", "/").strip("/") for prefix in self.paths]
        return any(folder and (location == folder or location.startswith(folder + "/")) for folder in folders)

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
        return node.practice.key == practice

    def _on_relationship(self, node: Node) -> bool:
        for kind in self.relationships:
            for edge in node.practice.in_graph.edges(kind):
                if edge.parent is node or edge.child is node:
                    return True
        return False


class Node:
    """children is the list populate writes on this node. Direct edges are the children. Grouped and relationship edges sit under one child named for the kind.

    A practice's parsed objects (a class, an operation, a scenario, a step) are nodes themselves: a practice reader adds
    the object it parsed to its practice graph, and rules read measurements straight from it. ``data`` holds only the
    facts the reader knows and the object does not, such as which folder a class sits in. A graph reloaded from
    ``graph.json`` holds plain nodes, whose saved facts are all in ``data``.
    """

    graph_facts: tuple[str, ...] = ()
    """The attributes of a parsed object that save with the graph, so a reloaded graph still answers ``get_fact``."""

    def __init__(self, practice: PracticeGuidance, type: str, node_id: str, name: str, source: Source) -> None:
        self.practice = practice
        self.type = type
        self.node_id = node_id
        self.name = name
        self.source = source
        self.stage = ""
        self.data: dict = {}
        self.children: list[Node] = []
        self.parent: Node | None = None
        self._rules = None
        self._populated = False

    def set_fact(self, key: str, value) -> None:
        """Record one fact on this node for rules to read; facts save with the graph."""
        self.data[key] = value

    def get_fact(self, key: str, default=None):
        """This node's fact, else the nearest ancestor's: a fact a whole file owns lives once, on the file's top node. A
        node no practice holds yet has only the ancestors its parser gave it."""
        node, visited = self, set()
        while node is not None and id(node) not in visited:
            if node._holds_attribute(key):
                return getattr(node, key)
            if key in node.data:
                return node.data[key]
            visited.add(id(node))
            node = node.parent or (node.graph.direct_parent(node) if node.practice is not None else None)
        return default

    def merge_fact(self, key: str, values: list) -> None:
        """Add values to a list fact this node keeps, each once, sorted: on its parsed object's own field when the
        object saves that fact, else among the facts the node keeps itself."""
        merged = sorted(set(self.get_fact(key) or []) | set(values))
        if key in self.graph_facts:
            setattr(self, key, merged)
        else:
            self.set_fact(key, merged)

    def has_fact(self, key: str) -> bool:
        """True when this node itself records the fact."""
        return self._holds_attribute(key) or key in self.data

    @property
    def facts(self) -> dict:
        """Every fact this node records: its saved attributes, then ``data``. This is what ``graph.json`` keeps."""
        found = {name: getattr(self, name) for name in self.graph_facts if hasattr(self, name)}
        found.update(self.data)
        return found

    def _holds_attribute(self, key: str) -> bool:
        return key in self.graph_facts and hasattr(self, key)

    @property
    def graph(self) -> Graph:
        """The graph that holds this node: its practice's."""
        return self.practice.graph

    @property
    def schema(self):
        """This node's practice's schema, with its graph's pattern overlays applied."""
        return self.practice.in_graph.schema

    @property
    def fidelity(self) -> FidelityGuidance | None:
        """The fidelity of this node's practice that creates it, with its rules, templates, and actions; none when the
        practice's schema gives none."""
        return next(iter(self.fidelities), None)

    @property
    def fidelities(self) -> list[FidelityGuidance]:
        """The fidelity of this node's practice that creates it, then every higher fidelity of that practice."""
        names = self.schema.fidelities_for(self.type)
        return [fidelity for fidelity in self.practice.fidelities if fidelity.name in names]

    def rule_checks(self) -> dict:
        """The checks this node's rules can run, by slug: its practice's own, and those of the practice it extends and
        of each pattern overlay its graph applies."""
        return dict(self.practice.checks())

    def applying_rule_types(self) -> set[str]:
        """The node types whose checks apply to this node: its own, and the type of the extended practice it is
        anchored to, such as a Clean Engineering class for a DDD entity."""
        types = {self.type}
        anchor = self.schema.anchor_type(self.type)
        if anchor:
            types.add(anchor)
        return types

    @property
    def rules(self) -> GraphRulesCollection:
        """The rules that apply to this node, from its practice and every fidelity of it, the practice it extends, and
        each pattern overlay its graph applies; each holds the violations found here and whether its check runs here."""
        if self._rules is None:
            self._rules = GraphRulesCollection.from_node(self)
        return self._rules

    def forget_rules(self) -> None:
        """Make this node's rules fresh when next read, with no violation found yet."""
        self._rules = None

    def leave_tree(self) -> None:
        """Take this node out of the explorer tree, so the next populate places it again from its practice's edges."""
        self.children = []
        self.parent = None
        self._populated = False

    @property
    def file_language(self) -> str | None:
        """The format the node's file is written in (``python``, ``typescript``, ``drawio``, ...), as the format of its
        practice, else of another practice the graph holds, that reads the file's extension says; ``graph`` for a node
        read from no file of its own such as a module, or from a file no format reads; none for any other node without
        a file."""
        file = self.source.file or ""
        if file in {"", "."}:
            return "graph" if self.type in {"Module", "Package"} else None
        return self.practice.format_reading_with(Path(file), self.graph.every_practice.values()) or "graph"

    @property
    def failed_rules(self) -> list[str]:
        return self.rules.failed_slugs

    @property
    def passing_rules(self) -> list[str]:
        """Rules that apply to this node and did not fail."""
        return self.rules.passing_slugs

    def place(self, file: str, start_line: int, end_line: int) -> None:
        """Put this node at its lines in file, under its practice's source root. A node its practice's reader found by
        a nearby line, such as a story's step, moves onto the lines that declare it."""
        self.source = Source(file, start_line, end_line, self.practice.in_graph.source_root)
        self.practice.align_node(self)

    def populate(self, parent: Node | None = None) -> None:
        if parent is not None:
            parent.children.append(self)
            if self.parent is None or (self._holder(self.parent) and not self._holder(parent)):
                self.parent = parent
        if self._populated:
            return
        self._populated = True
        # A kind no one filters by, the belongsTo back-edge and scopes, is no part of the explorer tree.
        types = sorted((edge_type for edge_type in self.practice.in_graph.edge_types.values() if edge_type.is_offered), key=lambda edge_type: edge_type.order)
        for edge_type in types:
            for edge in self._edges_in_source_order(edge_type.kind):
                edge.child.populate(self if edge.display == "direct" else self._holder_for(edge.kind))

    def _holder_for(self, kind: str) -> Node:
        """The child named for kind that grouped and relationship edges of that kind sit under, made the first time."""
        holder = self._child_named(kind)
        if holder is None:
            holder = self._new_kind_node(kind)
            holder.parent = self
            self.children.append(holder)
        return holder

    def _edges_in_source_order(self, kind: str) -> list[Edge]:
        matched = self.graph.edges_from(kind, self)
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
        return edge.child.type in edge.child.practice.source_ordered_types

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

    def rule_category(self) -> GraphRulesCollection | None:
        """The rules that apply to this node, as one child of it in the explorer tree; none when the filter shows none."""
        if self.type == self.name or self.type == "Practice":
            return None
        return self.rules if self.rules.shown else None

    def _new_kind_node(self, kind: str) -> Node:
        return Node(self.practice, kind, f"{self.practice.key}:{kind}:{self.node_id}", kind, self.source)


class Inventory:
    """Every loaded practice as the explorer's inventory shows it, with the pattern overlays applied and those available."""

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


class PracticeNodes:
    """One practice's part of the graph that holds it: the root node its explorer tree starts from, the folder its
    source is read from, its nodes by type and by id, and its edges by kind. The graph makes one for each practice it
    holds, keeps it, and gives it to the practice (``practice.in_graph``), so code holding a practice asks it for its
    nodes (``stories.in_graph.nodes("Story")``) instead of handing the practice back to the graph on every call."""

    def __init__(self, graph: Graph, practice: PracticeGuidance) -> None:
        self.graph = graph
        self.practice = practice
        self._source_root: Path | None = None
        self._root: Node | None = None
        self._by_id: dict[str, Node] = {}
        self._nodes: dict[str, list[Node]] = {}
        self._node_types: set[str] = set()
        self._edges: dict[str, list[Edge]] = {}
        self._edge_types: dict[str, EdgeType] = {}
        # Lookup indexes over the edges, rebuilt when a kind's list is replaced or grows elsewhere.
        self._edge_pairs: dict[str, tuple[tuple[int, int], set[tuple[int, int]]]] = {}
        self._edges_by_parent: dict[str, tuple[tuple[int, int], dict[int, list[Edge]]]] = {}
        self._direct_parents: tuple[tuple, dict[int, Node]] | None = None
        # The practice's schema for each set of overlays, made the first time it is asked for.
        self._schemas: dict[tuple[GraphOverlay, ...], PracticeSchema] = {}

    ## where the practice is read from, and its root

    @property
    def source_root_path(self) -> Path | None:
        """The folder the graph reads the practice's source from; none before a load chooses one."""
        return self._source_root

    @source_root_path.setter
    def source_root_path(self, root: Path | None) -> None:
        self._source_root = None if root is None else Path(root)

    @property
    def source_root(self) -> str:
        """The folder the graph reads the practice's source from, as text; empty before a load."""
        return "" if self._source_root is None else str(self._source_root)

    @property
    def is_open(self) -> bool:
        return self._root is not None

    @property
    def root(self) -> Node:
        """The node the practice's explorer tree starts from, which holds the facts about the practice as a whole."""
        if self._root is None:
            raise GraphFailure("root", f"{self.practice.key} is not open in this graph")
        return self._root

    def open(self, root: Path | None) -> None:
        """Read the practice from root, starting from its root node alone."""
        if root is not None:
            self._source_root = Path(root)
        if self._root is None:
            key = self.practice.key
            self._root = Node(self.practice, "Practice", f"{key}:Practice:.:{key}", key, Source(".", 0, 0))
        self._by_id[self._root.node_id] = self._root

    def close(self) -> None:
        """Forget every node and edge, so a load reads them again from nothing."""
        self._root = None
        for store in (self._by_id, self._nodes, self._node_types, self._edges, self._edge_types):
            store.clear()
        self.forget_edge_indexes()

    ## nodes

    def nodes(self, type: str | None = None) -> list[Node]:
        """Every node the practice holds, or only those of type."""
        if type is not None:
            return list(self._nodes.get(type, []))
        return [node for group in self._nodes.values() for node in group]

    def nodes_read_now(self, type: str | None = None) -> list[Node]:
        """The nodes of type that the load or refresh in progress read: every one on a load of the whole folder, and
        only those read from its files on a load of edited files or a refresh. The others were held from before. In a
        worker process, or in a graph opened from its saved graph, they are plain nodes holding only their saved facts,
        never the objects the practice parsed. A practice that builds its own nodes from another practice's builds them
        from these, so it sees the same parsed objects whichever process built the graph, and keeps the nodes it built
        before from the others."""
        found = self.nodes(type)
        edited = self.graph.edited_files()
        if edited is None:
            return found
        files = self.files_from_root(path.resolve() for path in edited)
        return [node for node in found if node.source.file in files]

    def files_from_root(self, files: Iterable[Path]) -> set[str]:
        """Each of files under the practice's source root, as a path from that root, the way its nodes name their file."""
        root = self._source_root.resolve() if self._source_root is not None else self.graph.loaded_folder
        if root is None:
            return set()
        return {file.relative_to(root).as_posix() for file in files if file == root or root in file.parents}

    def node(self, node_id: str) -> Node | None:
        """The practice's node called node_id; none when it holds none."""
        return self._by_id.get(node_id)

    def holds(self, node_id: str) -> bool:
        """Whether the practice already holds a node called node_id."""
        return node_id in self._by_id

    @property
    def node_types(self) -> set[str]:
        """The node types the graph offers for the practice: those it holds a node of, and those the practice offers."""
        return set(self._node_types)

    def offer_node_types(self, types: Iterable[str]) -> None:
        """Offer these node types in the explorer's filter, before any node of them is read."""
        self._node_types.update(types)

    def add(self, node: Node, node_id: str, file: str, start_line: int, end_line: int) -> Node:
        """Make node one of the practice's nodes, called node_id, at its lines in file; the node the practice already
        calls node_id when there is one. A parsed object leaves the throwaway graph its parser built it in. It keeps the
        parent its parser gave it only when that parent is one of the practice's nodes too, such as an operation's class;
        the tree itself is built from the practice's edges."""
        existing = self._by_id.get(node_id)
        if existing is not None:
            return existing
        _release(node)
        node.practice = self.practice
        node.node_id = node_id
        parent = node.parent
        if parent is None or self._by_id.get(getattr(parent, "node_id", "")) is not parent:
            node.parent = None
        node.place(file, start_line, end_line)
        self.hold(node)
        node.forget_rules()
        return node

    def add_named(self, type: str, node_id: str, name: str, source: Source) -> Node:
        """A node of the practice with no parsed object behind it, such as a story's example or a pattern's file, made
        and added."""
        node = Node(self.practice, type, node_id, name, source)
        return self.add(node, node_id, source.file, source.start_line, source.end_line)

    def hold(self, node: Node) -> None:
        """Keep node, one of this practice's, by its type and its id."""
        self._node_types.add(node.type)
        self._nodes.setdefault(node.type, []).append(node)
        self._by_id[node.node_id] = node

    def release(self, node: Node) -> None:
        """Let go of node when the practice holds it, so another practice can take it."""
        if self._by_id.get(node.node_id) is not node:
            return
        del self._by_id[node.node_id]
        bucket = self._nodes.get(node.type, [])
        if node in bucket:
            bucket.remove(node)

    def unused_node_id(self, type: str, name: str) -> str:
        """``practice:type:name``, numbered from 2 when the practice already holds a node of that id."""
        base = f"{self.practice.key}:{type}:{name}"
        index = 2
        found = base
        while found in self._by_id:
            found = f"{base}:{index}"
            index += 1
        return found

    def forget_files(self, files: set[str]) -> set[int]:
        """Drop every node read from one of files, each a path from the source root, so a refresh reads those files
        again from nothing; answer the ``id`` of each node dropped, whose edges every practice then drops."""
        dropped = {id(node) for node in self._by_id.values() if node is not self._root and node.source.file in files}
        if dropped:
            self._by_id = {node_id: node for node_id, node in self._by_id.items() if id(node) not in dropped}
            self._nodes = {kind: [node for node in group if id(node) not in dropped] for kind, group in self._nodes.items()}
        return dropped

    def put_in_source_order(self) -> None:
        """Hold the nodes of each type in the order their files and lines give them. A refresh holds the nodes it read
        again after those it kept, so without this a rule that reports the first of two nodes, such as the original of
        two duplicate bodies, would report another node after a refresh than after a fresh build."""
        for kind, group in self._nodes.items():
            self._nodes[kind] = sorted(group, key=_where_it_sits)

    def renew_rules(self) -> None:
        """Forget every node's rules, so each is made fresh when next read and the next check finds each violation again."""
        for node in self._by_id.values():
            node.forget_rules()

    ## edges

    def edges(self, kind: str | None = None) -> list[Edge]:
        """Every edge recorded on the practice, the practice of each edge's parent, or only those of kind."""
        if kind is not None:
            return list(self._edges.get(kind, []))
        return [edge for group in self._edges.values() for edge in group]

    @property
    def edge_types(self) -> dict[str, EdgeType]:
        """The kinds of edge the practice holds, each with where its group sits in the explorer tree."""
        return dict(self._edge_types)

    def offer_edge_type(self, edge_type: EdgeType) -> None:
        """Offer a kind of edge in the explorer's filter, before any edge of it is recorded."""
        self._edge_types[edge_type.kind] = edge_type

    def record(self, edge_type: EdgeType, parent: Node, child: Node) -> None:
        """Record an edge of edge_type from parent, one of this practice's nodes, to child, once; the first edge of a
        kind sets where its kind sits."""
        kind = edge_type.kind
        edges = self._edges.setdefault(kind, [])
        pairs = self._pairs_of(kind, edges)
        if (id(parent), id(child)) in pairs:
            return
        self._edge_types.setdefault(kind, edge_type)
        edges.append(Edge(kind, edge_type.order, edge_type.display, parent, child))
        pairs.add((id(parent), id(child)))
        self._edge_pairs[kind] = ((id(edges), len(edges)), pairs)

    def drop_edges(self, dropped: Callable[[Edge], bool]) -> list[Edge]:
        """Drop each edge that dropped says to; answer the edges dropped."""
        removed: list[Edge] = []
        for kind, edges in list(self._edges.items()):
            self._edges[kind] = [edge for edge in edges if not dropped(edge)]
            removed.extend(edge for edge in edges if dropped(edge))
        self.forget_edge_indexes()
        return removed

    def edges_from(self, kind: str, parent: Node) -> list[Edge]:
        """Edges of one kind leaving parent, in recorded order."""
        edges = self._edges.get(kind, [])
        state = (id(edges), len(edges))
        cached = self._edges_by_parent.get(kind)
        if cached is None or cached[0] != state:
            by_parent: dict[int, list[Edge]] = {}
            for edge in edges:
                by_parent.setdefault(id(edge.parent), []).append(edge)
            cached = (state, by_parent)
            self._edges_by_parent[kind] = cached
        return cached[1].get(id(parent), [])

    def direct_parent(self, child: Node) -> Node | None:
        """The node a direct edge of the practice hangs child under; available before populate sets ``parent``."""
        state = tuple((kind, id(edges), len(edges)) for kind, edges in self._edges.items())
        cached = self._direct_parents
        if cached is None or cached[0] != state:
            parents: dict[int, Node] = {}
            for edge in (edge for edges in self._edges.values() for edge in edges if edge.display == "direct"):
                parents.setdefault(id(edge.child), edge.parent)
            cached = self._direct_parents = (state, parents)
        return cached[1].get(id(child))

    def _pairs_of(self, kind: str, edges: list[Edge]) -> set[tuple[int, int]]:
        state = (id(edges), len(edges))
        cached = self._edge_pairs.get(kind)
        if cached is None or cached[0] != state:
            cached = (state, {(id(edge.parent), id(edge.child)) for edge in edges})
            self._edge_pairs[kind] = cached
        return cached[1]

    def forget_edge_indexes(self) -> None:
        self._edge_pairs = {}
        self._edges_by_parent = {}
        self._direct_parents = None

    def rebuild_tree(self) -> None:
        """Rebuild the practice's explorer tree from its edges after late-bound nodes or overlays."""
        for node in self._by_id.values():
            node.leave_tree()
        self.root.populate()

    ## schema and rules

    @property
    def schema(self) -> PracticeSchema:
        """The practice's schema, with the graph's pattern overlays applied."""
        return self.schema_with(tuple(self.graph.pattern_overlays))

    def schema_with(self, overlays: tuple[GraphOverlay, ...]) -> PracticeSchema:
        """The practice's schema with overlays applied, made the first time and kept here."""
        schema = self._schemas.get(overlays)
        if schema is None:
            schema = self._schemas[overlays] = PracticeSchema(self.practice, overlays)
        return schema

    @property
    def checks(self) -> dict:
        """The graph rules the practice checks in this graph, by slug: its own and those the graph's pattern overlays
        add to it."""
        return self.graph.applied_patterns.checks_of(self.practice)

    @property
    def rule_labels(self) -> list[str]:
        """Each rule the practice runs, named ``practice.node.rule`` with the pattern that owns it in front."""
        schema = self.schema
        return schema.rule_labels(schema.applicable)

    def rule_labels_for(self, types: set[str]) -> set[str]:
        """The labels of the rules the practice's nodes of these types run, and of those a node of them fails."""
        schema = self.schema
        labels = {schema.rule_label(node_type, rule) for rule, rule_types in schema.applicable.items() for node_type in rule_types if node_type in types}
        failing = (node for node_type in types for node in self.nodes(node_type))
        labels.update(schema.rule_label(node.type, slug) for node in failing for slug in node.failed_rules)
        return labels

    def check(self) -> None:
        """Run every graph rule the practice checks, over the whole practice, then node by node, and record each
        violation on the node it was found on. A practice names the rules it checks itself (``practice.checks()``),
        with those the graph's pattern overlays add; which of them apply to one node, the node says (``node.rules``)."""
        checks = list(self.practice.checks().values())
        if not checks:
            return
        context = RuleCheckContext(self.practice, self._source_root)
        key = self.practice.key
        for index, check in enumerate(checks, start=1):
            self.graph.report_progress(f"{key} · rule {check.slug} · {index}/{len(checks)}")
            for node_id, message in check.check_practice(context):
                node = self.graph.node(node_id)
                if node is not None:
                    node.rules.record_violation(check.slug, message)
        self._check_each_node(context)

    def _check_each_node(self, context: RuleCheckContext) -> None:
        """A node another practice's class covers skips that practice's checks, which already ran on the class."""
        covering = self._covering_classes()
        nodes = self.nodes()
        key = self.practice.key
        for index, node in enumerate(nodes, start=1):
            self.graph.report_progress(f"{key} · rules · {index}/{len(nodes)} · {node.type} {node.name}")
            skipped = {slug for slugs, spans in covering for slug in slugs if _inside(node, spans)}
            for rule in node.rules:
                if not rule.runs or rule.slug in skipped:
                    continue
                for message in rule.check(node, context):
                    node.rules.record_violation(rule.slug, message)

    def _covering_classes(self) -> list[tuple[frozenset[str], dict[str, list[tuple[int, int]]]]]:
        """For each other loaded practice that checks whole classes: its check slugs, and its classes' line spans by
        file."""
        found = []
        for other in self.graph.practices.values():
            class_type = other.class_node_type
            if other is self.practice or not class_type:
                continue
            spans: dict[str, list[tuple[int, int]]] = {}
            for node in other.in_graph.nodes(class_type):
                if node.source.file:
                    spans.setdefault(node.source.file.replace("\\", "/"), []).append((node.source.start_line, node.source.end_line))
            found.append((frozenset(other.checks()), spans))
        return found

    def restore(self, saved: SavedPractice) -> None:
        """Read back the nodes a saved graph kept for the practice, as plain nodes holding their saved facts, at the
        lines they were saved at, and the facts its root kept about the practice as a whole."""
        if saved.source_root:
            self._source_root = Path(saved.source_root)
        self.root.data.update(saved.root_facts)
        for kept in saved.nodes:
            if self.holds(kept.node_id):
                continue
            node = Node(self.practice, kept.type, kept.node_id, kept.name, Source(kept.file, kept.line, kept.end_line, self.source_root))
            node.stage = kept.stage
            node.data = dict(kept.facts)
            self.hold(node)


def _where_it_sits(node: Node) -> tuple:
    """Where node sits: its file, its lines, then its id, which tells apart two nodes on one line."""
    return (node.source.file or "", node.source.start_line, node.source.end_line, node.node_id)


def _inside(node: Node, spans: dict[str, list[tuple[int, int]]]) -> bool:
    """Whether node's lines overlap one of the class spans of its file."""
    file = (node.source.file or "").replace("\\", "/")
    start, end = node.source.start_line, node.source.end_line
    return any(start <= class_end and class_start <= end for class_start, class_end in spans.get(file, ()))


def _release(node: Node) -> None:
    """Take node out of the practice that holds it, in whichever graph that is, so another practice can take it."""
    part = getattr(getattr(node, "practice", None), "in_graph", None)
    if isinstance(part, PracticeNodes):
        part.release(node)


@language_adapter(language="typescript")
@agent_toolset
class Graph:
    """One graph. Builders fill nodes, edges, and rules. The explorer reads the tree.

    The graph holds its practices: the PracticeGuidance objects it is given, each of which knows this graph, so a node's
    practice is one of them (``node.practice``). It gives each practice its part of the graph, a *PracticeNodes* made
    once and kept, which holds the practice's nodes, edges, and root (``practice.in_graph.nodes("Story")``); the graph
    aggregates those parts. A session gives its graph the
    session's own practices, the same objects its actions work with; a graph no session holds makes a set of its own from the
    catalogue; a model object made apart from any graph joins one when a graph adopts it. The graph changes only when a call asks:
    ``load_working_copy`` and ``load_files`` read a folder or files, and ``refresh`` reads again exactly the files an
    action wrote."""

    def __init__(self, practices: Iterable[PracticeGuidance] | None = None) -> None:
        self._folder: Path | None = None
        self._scope: list[Path] | None = None
        # Every practice this graph holds, by key, whether a load reads it or not.
        self._held: dict[str, PracticeGuidance] = {}
        for practice in PracticeCatalogue.create_all(fidelity=None) if practices is None else practices:
            practice.graph = self
            practice.in_graph = PracticeNodes(self, practice)
            self._held[practice.key] = practice
        # The practices the last load reads, by key, in the order it opened them.
        self.practices: dict[str, PracticeGuidance] = {}
        # The practices a load call names, each read from the source root its part keeps.
        self._chosen: list[PracticeGuidance] = []
        # The saved graph file of the folder last loaded, with that folder.
        self._saved_graph_file: tuple[Path, SavedGraphFile] | None = None
        self.filter = Filter(self)
        # The pattern overlays this graph applies, each pattern made once.
        self.applied_patterns = PatternOverlays()
        self._schema_edges = SchemaEdges(self)
        self.syncs_schema_edges = True
        self._schema_sync_holds = 0
        self._syncing_schema = False
        # A load, a refresh, and a write each run alone: calls in one session can arrive at once.
        self._changing = threading.RLock()

    def for_call(self, call: ToolCall) -> Graph:
        """The graph call works on: its session's, which the server holds between calls; this graph for a call that
        works in no session."""
        session = call.session
        graph = getattr(session, "graph", None) if session is not None else None
        return graph if isinstance(graph, Graph) else self

    def open(self, folder: Path) -> None:
        """Open this graph on folder with every practice it holds rooted there, holding no node yet."""
        with self._changing:
            self._folder = folder
            self._scope = None
            self._choose_roots({key: folder for key in self._held})
            self._open_chosen_roots()

    def open_saved(self, folder: Path) -> None:
        """Open this graph on folder, then read back the graph saved in its ``.context`` when there is one, each saved
        practice on the source root it was read from, with the violations it was saved with: a session opened again
        shows what was loaded in it before. Its rules run again on the next load or refresh, which a call makes and
        which builds where that call says; opening a session runs no build. A folder with nothing saved opens holding
        no node until a load reads it."""
        self.open(folder)
        with self._changing:
            saved = self.saved_file.read()
            if saved is None:
                return
            self.overlays = list(saved.overlays)
            kept = {key: practice for key, practice in saved.practices.items() if key in self._held}
            self._choose_roots({key: Path(practice.source_root) if practice.source_root else folder for key, practice in kept.items()})
            self._hold(saved.of_practices(list(kept)))

    def report_progress(self, message: str) -> None:
        """Tell whoever called the running tool which practice, file, node, or rule is in progress."""
        report_progress(message)

    @property
    @data_field
    def folder(self) -> str:
        return "" if self._folder is None else str(self._folder)

    @property
    def loaded_folder(self) -> Path | None:
        """The folder the graph last loaded, where practices and overlays read from; none before a load."""
        return self._folder

    @property
    @data_field(key="overlays")
    def applied_overlays(self) -> list[str]:
        return list(self.overlays)

    @property
    def overlays(self) -> list[str]:
        """The folders of the pattern overlays this graph applies."""
        return list(self.applied_patterns.paths)

    @overlays.setter
    def overlays(self, overlays: list[str]) -> None:
        """Apply the overlays named, each a folder or a pattern's name: the graph holds the pattern each one is, and
        asks each for the GraphOverlay it owns."""
        self.applied_patterns.apply(list(overlays))

    @property
    def pattern_overlays(self) -> list[GraphOverlay]:
        """What each pattern this graph applies gives it: its nodes and its rules."""
        return self.applied_patterns.graph_overlays

    @property
    def every_graph_overlay(self) -> list[GraphOverlay]:
        """The overlay of every registered pattern, applied or not, whose schemas name relationships between the
        practices' types."""
        return self.applied_patterns.every_graph_overlay

    ## the practices this graph holds, and their nodes and edges

    @property
    def every_practice(self) -> dict[str, PracticeGuidance]:
        """Every practice this graph holds, by key, whether a load reads it or not."""
        return dict(self._held)

    def practice(self, key: str) -> PracticeGuidance:
        """The practice called key among those this graph holds, opened in this graph on the folder it last loaded the
        first time it is asked for. It is always the same object: the one the graph was given. This is the one lookup
        by key, for a call that names a practice by the key it sent; code that knows the practice's class asks
        ``practice_of``."""
        practice = self._held.get(key)
        if practice is None:
            raise UnknownPractice(key, tuple(self._held))
        return self._opened(practice)

    def practice_of(self, kind: type) -> PracticeGuidance:
        """The practice of class kind among those this graph holds, such as its Stories for ``Stories``, opened like
        ``practice``. Code that knows the practice's class asks for it by that class, never by its key."""
        practice = next((held for held in self._held.values() if type(held) is kind), None)
        if practice is None:
            raise UnknownPractice(kind.__name__, tuple(self._held))
        return self._opened(practice)

    def loaded(self, kind: type) -> PracticeGuidance | None:
        """The practice of class kind when the last load reads it; none when it reads no such practice. A practice that
        links its nodes to another's, or checks them against another's, asks this, so it opens nothing."""
        return next((practice for practice in self.practices.values() if type(practice) is kind), None)

    def _opened(self, practice: PracticeGuidance) -> PracticeGuidance:
        """practice, opened in this graph on the folder it last loaded the first time it is asked for."""
        if practice.key not in self.practices:
            self._open_practice(practice, practice.in_graph.source_root_path or self._folder)
        return practice

    def _open_practice(self, practice: PracticeGuidance, root: Path | None) -> None:
        """Read practice in this graph from root, starting from its root node alone."""
        self.practices[practice.key] = practice
        practice.in_graph.open(root)

    def _close_practices(self) -> None:
        """Forget every practice's nodes and edges, so a load reads them again from nothing."""
        self.practices = {}
        for practice in self._held.values():
            practice.in_graph.close()

    def node(self, node_id: str) -> Node | None:
        """The node called node_id, in whichever practice holds it; none when no practice does."""
        return next((found for found in (practice.in_graph.node(node_id) for practice in self._held.values()) if found is not None), None)

    def link(self, kind: str, parent: Node, child: Node, display: Display = "direct") -> None:
        """Record an edge of kind from parent to child, in the place its kind takes in the tree."""
        self.record(EdgeType.from_kind(kind, display), parent, child)

    def record(self, edge_type: EdgeType, parent: Node, child: Node) -> None:
        """Record an edge of edge_type from parent to child on the parent's practice, once."""
        parent.practice.in_graph.record(edge_type, parent, child)

    def edges_from(self, kind: str, parent: Node) -> list[Edge]:
        """Edges of one kind leaving this parent, in recorded order."""
        return parent.practice.in_graph.edges_from(kind, parent)

    def direct_parent(self, child: Node) -> Node | None:
        """The node a direct edge of the child's practice hangs the child under; available before populate sets
        ``parent``."""
        return child.practice.in_graph.direct_parent(child)

    def _restore_links(self, saved: SavedPractice) -> None:
        """Read back the edges and violations a saved graph kept for a practice, once every practice's nodes are back.
        An edge's parent and a violation's node are most often the practice's own, so it looks there first. Each edge
        is recorded as it was saved and no other way: a practice that links its nodes to another's records the edge
        back itself when it wants one, so the graph read back holds exactly the edges the build that saved it held."""
        own = self._held[saved.name].in_graph
        for kept in saved.edges:
            parent = own.node(kept.parent) or self.node(kept.parent)
            child = own.node(kept.child) or self.node(kept.child)
            if parent is not None and child is not None:
                self.record(EdgeType(kept.kind, kept.order, kept.display), parent, child)
        for violation in saved.violations:
            node = own.node(violation.node_id) or self.node(violation.node_id)
            if node is not None:
                node.rules.restore(violation)

    def restored_from(self, saved: SavedGraph) -> None:
        """Hold every practice saved keeps, with the overlays it was saved with: each practice's nodes first, then the
        edges between them, which may cross practices, and the violations on them."""
        self.overlays = list(saved.overlays)
        self._hold(saved)

    def _hold(self, saved: SavedGraph) -> None:
        """Hold exactly the practices saved keeps, of those this graph holds, each on the source root it was saved
        with: their nodes, then the edges between them and the violations on them, then each practice's tree."""
        self._close_practices()
        kept = {key: practice for key, practice in saved.practices.items() if key in self._held}
        for key, practice in kept.items():
            self.report_progress(f"Loading saved {key} nodes")
            root = Path(practice.source_root) if practice.source_root else self._folder
            self._open_practice(self._held[key], root)
            self._held[key].in_graph.restore(practice)
        for practice in kept.values():
            self._restore_links(practice)
        for practice in self.practices.values():
            practice.in_graph.root.populate()

    @long_call
    @mcp
    @agent_tool
    def load_working_copy(
        self,
        folder: str,
        practices: dict[str, str],
        database: str | None = None,
        overlays: list[str] | None = None,
        force: bool = False,
        call: ToolCall | None = None,
    ) -> GraphLoaded:
        """Open each practice on its source root and build the explorer tree.

        A saved graph in the folder's ``.context`` is used when it already holds
        every requested practice (extra cached practices are fine), each on the
        same source root, with the same overlays. Nothing watches the files: a
        file changed since is read again only by ``refresh`` with that file, or
        by a forced load, which always rebuilds. Every rebuild merges into the
        serialized graph so other practices already cached stay put.
        """
        with self._changing:
            self._folder = Path(database or folder).resolve()
            self._choose_roots({name: (Path(folder) / root).resolve() for name, root in practices.items()})
            self.overlays = list(overlays or [])
            self.report_progress("Checking the saved graph")
            saved = None if force else self.saved_file.holding(self._roots_by_key(), self.overlays)
            if saved is not None:
                self.report_progress("Loading the saved graph")
                self._load_saved(saved, call)
                return GraphLoaded("Loaded the saved graph.")
            self._scope = None
            self.report_progress("Scanning the folder")
            self._open_chosen_roots()
            self._build(BuildStep.READ, None, call, saves=True)
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
        call: ToolCall | None = None,
    ) -> GraphLoaded:
        """Build each practice from only the given files and run its rules on them.

        ``files`` are files or folders, relative to ``folder`` or absolute; a folder
        stands for the source files under it. Use it for the files being edited:
        it reads them as they are now and never touches the saved graph.
        """
        with self._changing:
            self._folder = Path(folder).resolve()
            self._choose_roots({name: self._folder for name in practices})
            self.overlays = list(overlays or [])
            self._scope = self._scoped_files(files)
            self.report_progress("Reading the edited files")
            self._open_chosen_roots()
            self._build(BuildStep.READ, None, call)
            return GraphLoaded(f"Loaded {len(self._scope)} edited files.")

    @mcp
    @agent_tool
    def refresh(self, paths: list[str], call: ToolCall | None = None) -> GraphLoaded:
        """Read again exactly the files at paths, the files an action just wrote, into the graph held in memory: drop
        every node read from them, read them as they are now, link them to the other practices' nodes, and run the
        rules again. Every other node stays as it was; nothing watches the files, so a written file is in the graph
        only once refresh is called with it.
        paths: the files written, absolute or from the graph's folder (the session's root); a folder stands for the
        source files under it. A file that is gone is dropped from the graph."""
        with self._changing:
            return self._refresh(paths, call)

    def refreshed(self, paths: list[str], call: ToolCall | None = None) -> SavedGraph:
        """Refresh the graph with exactly the files at paths and answer the nodes read from them, as they save, as one
        change: no other call's load or refresh comes between the two, so a call that checks the files it names sees
        the graph its own refresh left, whole, whatever other calls in the session do at the same time."""
        with self._changing:
            self._refresh(paths, call)
            return SavedGraph.from_graph(self, paths)

    def _refresh(self, paths: list[str], call: ToolCall | None) -> GraphLoaded:
        if self._folder is None or not self._chosen:
            return GraphLoaded("No graph is open, so nothing was refreshed.")
        files = self._refreshed_files(paths)
        if not files:
            return GraphLoaded("None of those files is in the graph's folder, so nothing was refreshed.")
        self.report_progress(f"Refreshing {len(files)} files")
        kept = self._scope
        self._scope = files
        try:
            self._build(BuildStep.REFRESH, None, call)
        finally:
            self._scope = kept
        return GraphLoaded(f"Refreshed {len(files)} files.")

    def _refreshed_files(self, paths: list[str]) -> list[Path]:
        """Each path a refresh names that lies in the graph's folder, outside the folders no practice reads; a folder
        stands for the source files under it, and a file that is gone is kept so its nodes drop."""
        folder = (self._folder or Path()).resolve()
        found: set[Path] = set()
        for item in paths or []:
            path = Path(item) if Path(item).is_absolute() else folder / item
            path = path.resolve()
            if path != folder and folder not in path.parents:
                continue
            if any(part in _REFRESH_SKIPPED_FOLDERS for part in path.relative_to(folder).parts):
                continue
            if path.is_dir():
                found.update(file.resolve() for file in scanned_files(path))
            else:
                found.add(path)
        return sorted(found)

    def _forget(self, files: list[Path]) -> None:
        """Drop the nodes read from files in every practice, and every edge that joins one of them."""
        dropped: set[int] = set()
        for practice in self.practices.values():
            dropped |= practice.in_graph.forget_files(practice.in_graph.files_from_root(files))
        for practice in self.practices.values():
            practice.in_graph.drop_edges(lambda edge: id(edge.parent) in dropped or id(edge.child) in dropped)

    def _build(self, step: BuildStep, state: SavedGraph | None, call: ToolCall | None, saves: bool = False) -> None:
        """Carry step out, from state when one is given, else from what the graph holds now, and save the graph after
        when saves is set. A call the cdd server answers for a chat (``call.answers_a_chat``) has a worker process carry
        it out, and this graph then holds what the worker built: a build is minutes of CPU-bound Python, and in the
        server's interpreter it would keep the server from answering every other chat. The graph changes only once the
        worker answers, so a build that fails leaves it holding what it held. Any other call, or none, builds here."""
        if call is not None and call.answers_a_chat:
            WorkerBuild(self.report_progress).carry_out(lambda: self._order(step, state, saves), self._hold)
            return
        if state is not None:
            self._hold(state)
        self._carry_out(step)
        if saves:
            self.report_progress("Saving the graph")
            self.save_json()

    def _order(self, step: BuildStep, state: SavedGraph | None, saves: bool) -> BuildOrder:
        """step as a worker carries it out: from state when one is given, else from what the graph holds now."""
        before = state if state is not None else SavedGraph.from_graph(self)
        return BuildOrder(step, self.folder, self._roots_as_text(), self.overlays, self._scope_as_text(), before, self._registering_modules(), saves)

    def carry_out(self, order: BuildOrder) -> SavedGraph:
        """Carry order out on this graph, as a worker process does for a graph the cdd server holds, save it when the
        order says, and answer the graph as it is then. The worker saves it, so the server never serialises the graph
        it built a second time."""
        with self._changing:
            self._folder = Path(order.folder) if order.folder else None
            self._scope = None if order.scope is None else [Path(path) for path in order.scope]
            self._choose_roots({key: Path(root) for key, root in order.roots.items()})
            self.overlays = order.overlays
            self.syncs_schema_edges = False
            self._hold(order.state)
            self._carry_out(order.step)
            if order.saves:
                self.report_progress("Saving the graph")
                self.save_json()
            return SavedGraph.from_graph(self)

    def _carry_out(self, step: BuildStep) -> None:
        """Run step on what this graph holds, in this process. A read fills the open practices from the working copy;
        a refresh first drops the nodes read from the files in scope, and every rule's findings, since a rule over a
        whole practice can change its finding on a node no file in scope holds. Both run every rule and rebuild each
        practice's tree. A working copy's edges are the ones its practices read; its parsed objects never add schema
        edges of their own. A check only runs the rules on what the graph holds."""
        if step is BuildStep.CHECK:
            for practice in self.practices.values():
                practice.in_graph.check()
            return
        self.syncs_schema_edges = False
        if step is BuildStep.REFRESH:
            files = list(self._scope or [])
            self._forget(files)
            self._scope = [path for path in files if path.is_file()]
            for practice in self.practices.values():
                practice.in_graph.renew_rules()
        self._read_working_copy()
        for practice in self.practices.values():
            practice.in_graph.rebuild_tree()

    def _roots_as_text(self) -> dict[str, str]:
        return {practice.key: str(practice.in_graph.source_root_path) for practice in self._chosen if practice.in_graph.source_root_path is not None}

    def _scope_as_text(self) -> list[str] | None:
        return None if self._scope is None else [str(path) for path in self._scope]

    def _registering_modules(self) -> list[str]:
        """The modules that define the practices this graph holds and the patterns it applies; importing them registers
        them with their catalogues, so a worker process holds the same classes."""
        held = [*self._held.values(), *self.applied_patterns.patterns]
        return sorted({type(item).__module__ for item in held})

    def _read_working_copy(self) -> None:
        """Read every open practice from the loaded folder, each after the practices it reads while it reads its own;
        link them once all are read; add the applied overlays' nodes; then run every practice's rules."""
        if self._folder is None:
            return
        practices = self._in_reading_order()
        for practice in practices:
            practice.in_graph.offer_node_types(practice.node_types)
            practice.read_working_copy()
        for practice in practices:
            practice.link_to_other_practices()
        for overlay in self.pattern_overlays:
            overlay.read(self)
        self._offer_overlay_types()
        for practice in self.practices.values():
            practice.in_graph.put_in_source_order()
        for practice in self.practices.values():
            practice.in_graph.check()

    def _in_reading_order(self) -> list[PracticeGuidance]:
        """The open practices, each after the practices it reads while it reads its own."""
        ordered: list[PracticeGuidance] = []

        def place(practice: PracticeGuidance) -> None:
            if practice in ordered:
                return
            for earlier in practice.reads_after:
                if earlier in self.practices:
                    place(self.practices[earlier])
            ordered.append(practice)

        for practice in list(self.practices.values()):
            place(practice)
        return ordered

    def _offer_overlay_types(self) -> None:
        """Offer the overlay schemas' node and relationship types in the filter lists before rules run."""
        overlays = self.pattern_overlays
        if not overlays:
            return
        for practice in self.practices.values():
            part = practice.in_graph
            schema = part.schema
            part.offer_node_types(schema.types)
            for kind in schema.overlay_relationship_kinds - set(part.edge_types):
                display = "direct" if any(overlay.display_of(kind) == "direct" for overlay in overlays) else "relationship"
                # A kind no edge was recorded under is listed after the ones the tree shows.
                part.offer_edge_type(EdgeType(kind, EdgeType.from_kind(kind, "relationship").order, display))

    def source_files(self, root: Path, suffixes: set[str]) -> list[Path]:
        """The files with these suffixes under root; only the edited ones when the graph loads a file scope."""
        edited = self.edited_files()
        if edited is None:
            return scanned_files(root, suffixes)
        return [path for path in edited if path.suffix.lower() in suffixes]

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

    def saved(self, files: list[str] | None = None) -> SavedGraph:
        """This graph as it saves, taken while no load, refresh, or write changes it; with files, only the nodes read
        from them, each a file or folder from a practice's source root, and the edges between them."""
        with self._changing:
            return SavedGraph.from_graph(self, files)

    @mcp
    @agent_tool
    def save_json(self) -> GraphSaved:
        """Write the serialized graph into the loaded folder's ``.context``.

        Practices already on disk that are not part of this load stay in the file.
        """
        if self._folder is None:
            return GraphSaved("")
        saved_file = self.saved_file
        return GraphSaved(str(saved_file.write(SavedGraph.from_graph(self).merged_over(saved_file.read()))))

    @property
    def saved_file(self) -> SavedGraphFile:
        """The saved graph file of the loaded folder, made once for each folder the graph loads; a validate that checks
        the session's saved graph reads it here."""
        folder = self._folder or Path()
        held = self._saved_graph_file
        if held is None or held[0] != folder:
            held = self._saved_graph_file = (folder, SavedGraphFile(folder, self.report_progress))
        return held[1]

    def _choose_roots(self, roots: dict[str, Path]) -> None:
        """Read each practice a call names, by key, from its root; the next load reads only those."""
        chosen = {self.practice(name): Path(root) for name, root in roots.items()}
        for practice in self._held.values():
            practice.in_graph.source_root_path = chosen.get(practice)
        self._chosen = list(chosen)

    def _roots_by_key(self) -> dict[str, Path]:
        return {practice.key: practice.in_graph.source_root_path for practice in self._chosen}

    def _open_chosen_roots(self) -> None:
        """Forget every node and open each chosen practice on its root, holding its root node alone."""
        self._close_practices()
        for practice in self._chosen:
            self._open_practice(practice, practice.in_graph.source_root_path)

    def _load_saved(self, saved: SavedGraph, call: ToolCall | None) -> None:
        """Read the requested practices back from the saved graph, which holds each on its chosen root, then run their
        rules on what was read, where call says to build."""
        self._build(BuildStep.CHECK, saved.of_practices([practice.key for practice in self._chosen]), call)

    def sync_schema_edges(self) -> None:
        """Record the schema relationship edges between the model objects on this graph, unless a working copy loaded
        it (its practices record their own edges) or a batch of links is still being made."""
        if not self.syncs_schema_edges or self._schema_sync_holds or self._syncing_schema:
            return
        self._syncing_schema = True
        try:
            self._schema_edges.sync()
        finally:
            self._syncing_schema = False

    @contextmanager
    def schema_sync_held(self) -> Iterator[None]:
        """Hold schema-edge rebuilds until a batch of links is finished, then rebuild once. Each link would otherwise
        rebuild every schema edge, which on a story map is quadratic in the nodes already attached."""
        self._schema_sync_holds += 1
        try:
            yield
        finally:
            self._schema_sync_holds -= 1
            self.sync_schema_edges()

    @long_call
    @mcp
    @agent_tool
    def set_overlays(self, overlays: list[str], call: ToolCall | None = None) -> AppliedOverlays:
        """Apply pattern overlays, folders holding practices/, and rebuild the explorer tree from the open folder; answer with the graph's inventory."""
        self.overlays = list(overlays or [])
        if self._folder is not None and self._chosen:
            roots = {name: str(path) for name, path in self._roots_by_key().items()}
            self.load_working_copy(str(self._folder), roots, database=str(self._folder), overlays=self.overlays, call=call)
        label = ", ".join(Path(item).name for item in self.overlays) if self.overlays else "none"
        return AppliedOverlays(f"Applied pattern overlays: {label}.", self.inventory())

    @mcp
    @agent_tool
    def overlay_of(self, folder: str) -> Overlay:
        """Return the pattern overlay folder holds: folder itself or the overlay root above it, which must hold practices/."""
        root = self.applied_patterns.root_of(folder)
        if not (root / "practices").is_dir():
            raise GraphFailure("overlay_of", f"Not an overlay root (missing practices/): {folder}")
        return Overlay(str(root))

    @mcp
    @agent_tool
    def practice_names(self) -> list[str]:
        """Return the name of every practice the graph can load, in the order the approach walks them."""
        return list(self._held)

    @mcp
    @agent_tool
    def inventory(self) -> Inventory:
        """Return each loaded practice's node and edge counts, node types, rules, and explorer tree, with the overlays applied and those available."""
        loaded = {key: PracticeInventory(self, practice) for key, practice in self.practices.items()}
        return Inventory(loaded, list(self.overlays), self.applied_patterns.available)

    @mcp
    @agent_tool
    def filter_choices(self, practices: list[str], node_types: list[str], practices_before: list[str] | None = None) -> Filter:
        """Return the node types a filter offers and those it chooses, with the relationships and rules of the chosen
        ones (of every offered one when none is chosen), once practices and node types are chosen. practices_before
        names the practices chosen before a change of practice: then node_types are those chosen before, the ones the
        new practices still hold stay chosen, and every node type of each practice added is chosen. The graph's own
        filter is cleared."""
        self.filter.clear()
        offered = Filter(self)
        if practices_before is not None:
            offered.practices = list(practices_before)
            offered.node_types = list(node_types)
            offered.change_practices(practices)
            return offered
        offered.select_practices(practices)
        offered.select_node_types(node_types)
        return offered

    @mcp
    @agent_tool
    def source(self, node_id: str) -> NodeSource | None:
        """Return the source of the node node_id: its file, text, and lines, with every class, operation, and property the loaded graph holds, so calls in it can be opened in place. None for an id with no source, such as a rule's row."""
        node = self.node(node_id)
        if node is None:
            return None
        return NodeSource(node, members=self._source_members())

    def _source_members(self) -> list[NodeSource]:
        """Every class, operation, and property the loaded practices hold, each with the class it belongs to."""
        declared = list(self.practices.values())
        classes = {node_type for practice in declared for node_type in practice.class_types}
        members = {node_type for practice in declared for node_type in practice.member_types}
        found = (node for practice in declared for node in practice.in_graph.nodes() if node.type in classes | members)
        return [NodeSource(node, owner="" if node.type in classes else str(node.get_fact("owner", "") or "")) for node in found]

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
            self._collect_nodes(practice.in_graph.root, [], wanted, found, seen)
        return found

    def _collect_nodes(self, node: Node, ancestors: list[str], wanted: Filter, found: list[FilteredNode], seen: set[int]) -> None:
        if id(node) in seen:
            return
        seen.add(id(node))
        chain = [*ancestors, node.name]
        if wanted.matches(node):
            rules = node.rules.chosen(wanted.violations, list(wanted.rules))
            found.append(FilteredNode(node, ancestors, rules))
        for child in node.children:
            self._collect_nodes(child, chain, wanted, found, seen)

    @mcp
    @agent_tool
    def explorer_trees(self, filter: dict | None = None) -> list[ExplorerEntry]:
        """Return the explorer tree of each practice the filter names, or of every loaded practice when it names none, keeping each practice's root, the nodes the filter matches with their rules, and the nodes on the way to them. filter takes the keys return_nodes takes."""
        wanted = self.filter.narrowed_by(filter or {})
        named = [self.practices[key] for key in wanted.practices if key in self.practices] if wanted.practices else list(self.practices.values())
        return [tree for practice in named if (tree := practice.in_graph.root.serialize().kept_by(wanted)) is not None]

