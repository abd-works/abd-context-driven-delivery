"""Graph. Practice graphs, nodes, edges, and the explorer tree."""

from __future__ import annotations

import re
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.progress import report_progress
from harness.installation.destination import data_field, language_adapter
from harness.installation.files import command, skill
from harness.mcp.mcp_server import mcp
from harness.graph.explorer import ExplorerEntry, FilteredNode, GraphLoaded, GraphSaved, NodeSource, Overlay
from harness.graph.graph_practice import GraphPractices
from harness.graph.graph_rules_collection import GraphRulesCollection
from harness.graph.pattern_overlays import PatternOverlays
from harness.graph.saved_graph import SavedGraph, SavedGraphFile, SavedPractice
from harness.graph.skipped_folders import scanned_files

Display = str
# File endings and the channel a file with that ending is written in; any other file is read as part of the graph.
_FILE_LANGUAGES = (((".ts", ".tsx"), "typescript"), ((".js", ".jsx", ".mjs"), "javascript"), (".py", "python"), ((".drawio", ".xml"), "drawio"))
# A practice whose source root holds more source files than this opens without reading them, so a session on a large
# repository starts at once.
_LOAD_FILE_BUDGET = 40
_BUDGETED_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx"}

def _under_any(file: str | None, prefixes: list[str]) -> bool:
    """True when ``file`` is one of the prefixes or sits under one."""
    location = (file or "").replace("\\", "/").strip("/")
    for prefix in prefixes:
        folder = str(prefix).replace("\\", "/").strip("/")
        if folder and (location == folder or location.startswith(folder + "/")):
            return True
    return False


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


class Call:
    """A call found in source. operation is the callee text Monaco marks."""

    def __init__(self, line: int, order: int, operation: str) -> None:
        self.line = line
        self.order = order
        self.operation = operation


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
        types = set(self.node_types or self._available_node_types())
        found: set[str] = set()
        for name in self._scope():
            practice = self.graph.practices.get(name)
            if practice is not None:
                found.update(practice.rule_labels_for(types))
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


def _within_load_budget(folder: Path) -> bool:
    """Whether folder holds no more source files than the load budget; a folder not yet there holds none."""
    if not folder.is_dir():
        return True
    count = 0
    for item in folder.rglob("*"):
        if item.suffix.lower() not in _BUDGETED_SUFFIXES:
            continue
        count += 1
        if count > _LOAD_FILE_BUDGET:
            return False
    return True


def _names(request: dict, many: str, one: str) -> bool:
    return many in request or one in request


def _listed(request: dict, many: str, one: str) -> list[str]:
    """A request key that takes a list or a single value, such as ``types`` or ``type``."""
    return list(request.get(many) or ([request[one]] if request.get(one) else []))


class Node:
    """children is the list populate writes on this node. Direct edges are the children. Grouped and relationship edges sit under one child named for the kind.

    A practice's parsed objects (a class, an operation, a scenario, a step) are nodes themselves: a practice reader adds
    the object it parsed to its practice graph, and rules read measurements straight from it. ``data`` holds only the
    facts the reader knows and the object does not, such as which folder a class sits in. A graph reloaded from
    ``graph.json`` holds plain nodes, whose saved facts are all in ``data``.
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
        self.children: list[Node] = []
        self.parent: Node | None = None
        self._rules = None
        self._populated = False

    def set_fact(self, key: str, value) -> None:
        """Record one fact on this node for rules to read; facts save with the graph."""
        self.data[key] = value

    def get_fact(self, key: str, default=None):
        """This node's fact, else the nearest ancestor's: a fact a whole file owns lives once, on the file's top node."""
        node, visited = self, set()
        while node is not None and id(node) not in visited:
            if node._holds_attribute(key):
                return getattr(node, key)
            if key in node.data:
                return node.data[key]
            visited.add(id(node))
            node = node.parent or node.practice.direct_parent(node)
        return default

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
    def fidelity(self) -> str:
        """The fidelity that creates this node, from its practice's schema; empty when the schema gives none."""
        return next(iter(self.fidelities), "")

    @property
    def fidelities(self) -> list[str]:
        """The fidelity that creates this node and every higher fidelity of its practice."""
        return self.practice.schema.fidelities_for(self.type)

    @property
    def rules(self) -> GraphRulesCollection:
        """Schema rules for this node, with violations on each entry."""
        if self._rules is None:
            self._rules = GraphRulesCollection.from_node(self)
        return self._rules

    @property
    def file_language(self) -> str | None:
        """The channel the node's file is written in (``python``, ``typescript``, ``drawio``, ...), ``graph`` for a node
        read from no file of its own such as a module; none for any other node without a file."""
        file = (self.source.file or "").lower()
        if file in {"", "."}:
            return "graph" if self.type in {"Module", "Package"} else None
        return next((language for suffixes, language in _FILE_LANGUAGES if file.endswith(suffixes)), "graph")

    @property
    def failed_rules(self) -> list[str]:
        return self.rules.failed_slugs

    @property
    def passing_rules(self) -> list[str]:
        """Rules that apply to this node and did not fail."""
        return self.rules.passing_slugs

    def release(self) -> None:
        """Leave the practice this node is registered in, so another practice can take it."""
        practice = getattr(self, "practice", None)
        if practice is None or practice.by_id.get(self.node_id) is not self:
            return
        del practice.by_id[self.node_id]
        bucket = practice.nodes.get(self.type, [])
        if self in bucket:
            bucket.remove(self)

    def place(self, file: str, start_line: int, end_line: int) -> None:
        """Put this node at its lines in file, under its practice's source root. A node its practice's reader found by
        a nearby line, such as a story's step, moves onto the lines that declare it."""
        self.source = Source(file, start_line, end_line, self.practice.source_root)
        GraphPractices.named(self.practice.name).align(self)

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
        return edge.child.type in GraphPractices.named(edge.child.practice.name).source_ordered_types

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
        self.applicable: dict[str, list[str]] = {}
        self.loaded: list[str] = []
        self.source_root = ""
        self.graph: Graph | None = None
        self.root_node = Node(self, "Practice", f"{name}:Practice:.:{name}", name, Source(".", 0, 0))
        # Lookup indexes over self.edges, rebuilt when a kind's list is replaced or grows elsewhere.
        self._edge_pairs: dict[str, tuple[tuple[int, int], set[tuple[int, int]]]] = {}
        self._edges_by_parent: dict[str, tuple[tuple[int, int], dict[int, list[Edge]]]] = {}
        self._direct_parents: tuple[tuple, dict[int, Node]] = ((), {})

    def apply_rule(self, rule: str, types: list[str]) -> None:
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
        return self.schema.rule_labels(self.applicable)

    def rule_labels_for(self, types: set[str]) -> set[str]:
        """The labels of the rules nodes of these types run here, and of those a node of them fails."""
        labels = {self.schema.rule_label(node_type, rule) for rule, rule_types in self.applicable.items() for node_type in rule_types if node_type in types}
        failing = (node for node_type in types for node in self.nodes.get(node_type, []))
        labels.update(self.schema.rule_label(node.type, slug) for node in failing for slug in node.failed_rules)
        return labels

    @property
    def schema(self):
        """This practice's schema, with the graph's pattern overlays applied."""
        from harness.graph.schema_rules import PracticeSchema

        return PracticeSchema.load(self.name, self.graph.overlay_patterns if self.graph is not None else ())

    @property
    @data_field
    def tree(self) -> ExplorerEntry:
        """The explorer tree, from this practice's root."""
        return self.root_node.serialize()

    def add(self, node: Node, node_id: str, file: str, start_line: int, end_line: int) -> Node:
        """Make node one of this practice's nodes, called node_id, at its lines in file; the node already called
        node_id when there is one. A parsed object leaves the throwaway graph its parser built it in. It keeps the
        parent its parser gave it only when that parent is a node of this practice too, such as an operation's class;
        the tree itself is built from this practice's edges."""
        existing = self.by_id.get(node_id)
        if existing is not None:
            return existing
        node.release()
        node.practice = self
        node.node_id = node_id
        if not self._holds(node.parent):
            node.parent = None
        node.place(file, start_line, end_line)
        return self._register(node)

    def unused_node_id(self, type: str, name: str) -> str:
        """``practice:type:name``, numbered from 2 when this practice already holds a node of that id."""
        base = f"{self.name}:{type}:{name}"
        index = 2
        found = base
        while found in self.by_id:
            found = f"{base}:{index}"
            index += 1
        return found

    def _holds(self, node: Node | None) -> bool:
        return node is not None and self.by_id.get(getattr(node, "node_id", "")) is node

    def add_named(self, type: str, node_id: str, name: str, source: Source) -> Node:
        """A node with no parsed object behind it, such as a story's example or a pattern's file, made and added."""
        node = Node(self, type, node_id, name, source)
        return self.add(node, node_id, source.file, source.start_line, source.end_line)

    def _register(self, node: Node) -> Node:
        self.schema.apply_to(self)
        self.node_types.add(node.type)
        node._rules = GraphRulesCollection.from_node(node)
        self.nodes.setdefault(node.type, []).append(node)
        self.by_id[node.node_id] = node
        return node

    def restore(self, saved: SavedPractice) -> None:
        """Read back the nodes a saved graph kept for this practice, as plain nodes holding their saved facts, at the
        lines they were saved at, and the facts its root kept about the practice as a whole."""
        self.source_root = saved.source_root or self.source_root
        self.by_id[self.root_node.node_id] = self.root_node
        self.root_node.data.update(saved.root_facts)
        for kept in saved.nodes:
            if kept.node_id in self.by_id:
                continue
            node = Node(self, kept.type, kept.node_id, kept.name, Source(kept.file, kept.line, kept.end_line, self.source_root))
            node.stage = kept.stage
            node.data = dict(kept.facts)
            self._register(node)

    def restore_links(self, saved: SavedPractice) -> None:
        """Read back the edges and violations a saved graph kept for this practice, once every practice's nodes are back."""
        for kept in saved.edges:
            parent = self.registered(kept.parent)
            child = self.registered(kept.child)
            if parent is not None and child is not None:
                parent.practice.record(kept.fact, parent, child)
                if parent.practice is not child.practice:
                    child.practice.record(kept.fact, child, parent)
        for violation in saved.violations:
            node = self.registered(violation.node_id)
            if node is not None:
                node.rules.restore(violation)

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

    def link(self, kind: str, parent: Node, child: Node, display: Display = "direct") -> None:
        """Record an edge of kind from parent to child on this practice, in the place its kind takes in the tree."""
        self.record({"kind": kind, "order": edge_order(kind, display), "display": display}, parent, child)

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
            for edge in (edge for list_ in self.edges.values() for edge in list_ if edge.display == "direct"):
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
    """One graph. Builders fill nodes, edges, and rules. The explorer reads the tree.

    Each project's cdd runtime holds one graph, the toolset its graph tools run on, so the calls one chat makes load
    and filter its project's graph and never another's."""

    def __init__(self) -> None:
        self._folder: Path | None = None
        self._practice_roots: dict[str, Path] = {}
        self._scope: list[Path] | None = None
        self.practices: dict[str, PracticeGraph] = {}
        self.filter = Filter(self)
        self.overlays: list[str] = []
        self.syncs_schema_edges = True
        self._schema_sync_holds = 0
        self._syncing_schema = False

    @classmethod
    def of_practice(cls, folder: Path | str, name: str, source_root: Path | str) -> Graph:
        """The graph of the practice called name, whose files are under source_root, with its saved graph in folder's
        ``.context``. A source root with more source files than the load budget is opened without reading them: the
        graph names the practice and its root, which is all an action's log line needs, so a large repository opens at
        once."""
        graph = cls()
        root = Path(source_root)
        if _within_load_budget(root):
            graph.load_working_copy(str(folder), {name: str(root)})
        else:
            graph._open_unread(Path(folder), name, root)
        return graph

    def _open_unread(self, folder: Path, name: str, source_root: Path) -> None:
        self._folder = folder
        self._practice_roots = {name: source_root}
        self.practice(name).source_root = str(source_root)

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
    def overlay_patterns(self) -> tuple[str, ...]:
        """The pattern folder names, such as ``lern_domain_driven``, of the overlays this graph applies."""
        return PatternOverlays(self.overlays).patterns

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
        self.overlays = PatternOverlays(list(overlays or [])).paths
        self.report_progress("Checking the saved graph")
        saved = None if force else self._saved_file().current_for(self._practice_roots, self.overlays)
        if saved is not None:
            self.report_progress("Loading the saved graph")
            self._load_saved(saved)
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
        self.overlays = PatternOverlays(list(overlays or [])).paths
        self._scope = self._scoped_files(files)
        self.report_progress("Reading the edited files")
        self._build_working_copy()
        return GraphLoaded(f"Loaded {len(self._scope)} edited files.")

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

    def write_json(self, path: str) -> str:
        """Write this graph alone to ``path``, without merging into the folder's saved graph."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(SavedGraph.from_graph(self).text, encoding="utf-8")
        return str(target)

    @mcp
    @agent_tool
    def save_json(self) -> GraphSaved:
        """Write the serialized graph into the loaded folder's ``.context``.

        Practices already on disk that are not part of this load stay in the file.
        """
        if self._folder is None:
            return GraphSaved("")
        saved_file = self._saved_file()
        return GraphSaved(str(saved_file.write(SavedGraph.from_graph(self).merged_over(saved_file.read()))))

    def _saved_file(self) -> SavedGraphFile:
        return SavedGraphFile(self._folder or Path(), self.report_progress)

    def _build_working_copy(self) -> None:
        # A working copy's edges are the ones its practices read; its parsed objects never add schema edges of their own.
        self.syncs_schema_edges = False
        self.practices = {}
        for name, source in self._practice_roots.items():
            practice = self.practice(name)
            practice.source_root = str(source)
            practice.by_id[practice.root_node.node_id] = practice.root_node
        from harness.graph.working_copy import WorkingCopy

        WorkingCopy(self).fill()
        for practice in self.practices.values():
            practice.rebuild_tree()

    def _load_saved(self, saved: SavedGraph) -> None:
        """Read the requested practices back from the saved graph, then run their rules on what was read."""
        self.practices = {}
        for name in self._practice_roots:
            self.report_progress(f"Loading saved {name} nodes")
            practice = self.practice(name)
            practice.source_root = str(self._practice_roots[name])
            practice.restore(saved.practices[name])
        for name in self._practice_roots:
            self.practice(name).restore_links(saved.practices[name])
        from harness.graph.rules import PracticeChecks

        for practice in self.practices.values():
            practice.root_node.populate()
            PracticeChecks(practice).run()
            practice.loaded = ["nodes", "edges", "rules"]

    def sync_schema_edges(self) -> None:
        """Record the schema relationship edges between the model objects on this graph, unless a working copy loaded
        it (its practices record their own edges) or a batch of links is still being made."""
        if not self.syncs_schema_edges or self._schema_sync_holds or self._syncing_schema:
            return
        from harness.graph.schema_edges import SchemaEdges

        self._syncing_schema = True
        try:
            SchemaEdges(self).sync()
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

    @mcp
    @agent_tool
    def set_overlays(self, overlays: list[str]) -> AppliedOverlays:
        """Apply pattern overlays, folders holding practices/, and rebuild the explorer tree from the open folder; answer with the graph's inventory."""
        self.overlays = PatternOverlays(list(overlays or [])).paths
        if self._folder is not None and self._practice_roots:
            roots = {name: str(path) for name, path in self._practice_roots.items()}
            self.load_working_copy(str(self._folder), roots, database=str(self._folder), overlays=self.overlays)
        label = ", ".join(Path(item).name for item in self.overlays) if self.overlays else "none"
        return AppliedOverlays(f"Applied pattern overlays: {label}.", self.inventory())

    @mcp
    @agent_tool
    def overlay_of(self, folder: str) -> Overlay:
        """Return the pattern overlay folder holds: folder itself or the overlay root above it, which must hold practices/."""
        root = PatternOverlays().root_of(folder)
        if not (root / "practices").is_dir():
            raise GraphFailure("overlay_of", f"Not an overlay root (missing practices/): {folder}")
        return Overlay(str(root))

    @mcp
    @agent_tool
    def practice_names(self) -> list[str]:
        """Return the name of every practice the graph can load, in the order the approach walks them."""
        from harness.guidance.practice_catalogue import PracticeCatalogue

        return list(PracticeCatalogue.keys())

    @mcp
    @agent_tool
    def inventory(self) -> Inventory:
        """Return each loaded practice's node and edge counts, node types, rules, and explorer tree, with the overlays applied and those available."""
        return Inventory(self.practices, list(self.overlays), PatternOverlays().available)

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
        return NodeSource(node, members=self._members())

    def _node(self, node_id: str) -> Node | None:
        return next((practice.by_id[node_id] for practice in self.practices.values() if node_id in practice.by_id), None)

    def _members(self) -> list[NodeSource]:
        """Every class, operation, and property the loaded practices hold, each with the class it belongs to."""
        declared = [GraphPractices.named(name) for name in self.practices]
        classes = {node_type for practice in declared for node_type in practice.class_types}
        members = {node_type for practice in declared for node_type in practice.member_types}
        found = (node for practice in self.practices.values() for node in practice.by_id.values() if node.type in classes | members)
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
            self._collect_nodes(practice.root_node, [], wanted, found, seen)
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

