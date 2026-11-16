"""Graph. Practice graphs, nodes, edges, and the explorer tree."""

from __future__ import annotations

import os
import re
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterable, Iterator, TypedDict


from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.progress import report_progress
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from harness.installation.data_class import data_field, language_adapter
from harness.installation.files import command, skill
from harness.mcp.mcp_annotations import long_call, mcp
from harness.graph.edge import Display, Edge, EdgeIndex, EdgeType
from harness.graph.explorer import ExplorerEntry, FilteredNode, GraphLoaded, GraphSaved, NodeSource, Overlay, PracticeInventory
from harness.graph.file_lines import FileLines, PathKind
from harness.graph.graph_build import BuildStep, BuildTask, CheckedFiles, GraphBuild
from harness.graph.graph_practices import GraphPractices
from harness.graph.graph_rules_collection import GraphRulesCollection
from harness.graph.load_scope import LoadScope
from harness.graph.location import Location
from harness.graph.pattern_overlays import GraphOverlay, PatternOverlays
from harness.graph.rule_context import RuleCheckContext
from harness.graph.schema_edges import SchemaEdges
from harness.graph.schema_rules import PracticeSchema
from harness.graph.saved_graph import GRAPH_FILE_NAME, FactValue, NodeFacts, PracticeChanges, SavedGraph, SavedGraphFile, SavedNode, SavedPractice

if TYPE_CHECKING:
    from harness.agent_tools.tool_call import ToolCall
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance

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

    def __init__(self, path: str, line_start: int, line_end: int) -> None:
        self.file = path
        self.start_line = line_start
        self.end_line = line_end
        self.root = ""
        self.calls: list[Call] = []
        self._text: str | None = None

    @classmethod
    def from_root(cls, root: str, location: Location) -> Source:
        """The lines location names in its file, a path from root, the folder its practice reads its source from."""
        source = cls(location.file, location.line or 0, location.end_line or 0)
        source.root = root
        return source

    @classmethod
    def whole_file(cls, relative: str, root: str) -> Source:
        """Every line of the file at relative under root; one line when it is empty or not there."""
        path = Path(root, relative) if root else None
        text = path.read_text(encoding="utf-8") if path is not None and path.is_file() else ""
        end = text.count("\n") + (0 if not text or text.endswith("\n") else 1)
        return cls.from_root(root, Location(relative, 1, max(1, end)))

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

    def align_to_example_export(self, root: str, name: str, files: Iterable[Path]) -> None:
        """Point this slice at the fixture named ``name`` in one of ``files``, the TypeScript files under ``root`` the
        read is scoped to: a fixture function, or an exported constant such as ``export const DONE = {...}``. A story
        test imports both from its examples file, so an example it names belongs there, not at the test that uses it.
        Only the files given are searched, so a read limited to the files being edited never opens any other file."""
        if not root or not name:
            return
        root_path = Path(root)
        function = re.compile(rf"(?:export\s+)?function\s+{re.escape(name)}\b")
        constant = re.compile(rf"\bexport\s+const\s+{re.escape(name)}\b")
        for path in sorted(files):
            if FileLines(path).kind is not PathKind.FILE:
                continue
            lines = FileLines(path).lines
            for index, line in enumerate(lines):
                if function.search(line) or constant.search(line):
                    end = self._call_end(lines, index) if function.search(line) else self._declaration_end(lines, index)
                    self._point_at(root, Location(path.relative_to(root_path).as_posix(), index + 1, end))
                    return

    def _point_at(self, root: str, location: Location) -> None:
        """Point this slice at the lines location names, in its file under root."""
        self.file = location.file
        self.root = root
        self.start_line, self.end_line = location.line, location.end_line
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
        """The lines of the file this slice is in, or of every code file in its folder; a build reads each once."""
        full = self._full_path()
        return FileLines(full).lines if full is not None else []

    def _directory(self) -> bool:
        full = self._full_path()
        return full is not None and FileLines(full).kind is PathKind.FOLDER

    def _full_path(self) -> Path | None:
        if not self.root or not self.file or self.file == ".":
            return None
        return Path(self.root, self.file)

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


class FilterRequest(TypedDict, total=False):
    """What a call to ``graph.return_nodes``, ``graph.explorer_trees``, or ``graph.explorer_branch`` asks the filter
    for: practice(s), type(s), a name, rules, relationships, whether only violations, and path(s). A key that takes a
    list also takes one value under its singular name."""

    practices: list[str]
    practice: str
    types: list[str]
    type: str
    name: str
    rules: list[str]
    relationships: list[str]
    violations: bool
    paths: list[str]
    path: str


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

    @property
    @data_field
    def rules(self) -> list[str]:
        """The rules the chosen node types run or fail, or those chosen."""
        return self._rules

    def clear(self) -> None:
        self.practices = []
        self._node_types = []
        self._relationships = []
        self._rules = []
        self.violations = False
        self.relationships_selected = False

    def select_violations(self, rules: list[str]) -> None:
        """Keep nodes that fail one of rules."""
        self._rules = list(rules)
        self.violations = True

    def select_relationships(self, relationships: list[str]) -> None:
        """Keep nodes that sit on one of these edges."""
        self._relationships = list(relationships)
        self.relationships_selected = True

    def select_practices(self, practices: list[str]) -> None:
        self.violations = False
        self.relationships_selected = False
        self.practices = list(practices)
        self._node_types = self._available_node_types()
        self._fill_from_nodes()

    def select_node_types(self, node_types: list[str]) -> None:
        self.violations = False
        self.relationships_selected = False
        self._node_types = list(node_types)
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
        return list(self.graph.practices.opened)

    def _node_types_of(self, key: str) -> list[str]:
        practice = self.graph.practices.opened.get(key)
        return list(practice.reading.in_graph.node_types) if practice is not None else []

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
            practice = self.graph.practices.opened.get(name)
            if practice is None:
                continue
            ordered = sorted(practice.reading.in_graph.edge_index.types.values(), key=lambda edge_type: edge_type.order)
            for edge_type in ordered:
                if edge_type.kind in found or not edge_type.is_offered:
                    continue
                edges = practice.reading.in_graph.edges(edge_type.kind)
                if any(edge.parent.type in types or edge.child.type in types for edge in edges):
                    found.append(edge_type.kind)
        return found

    def _available_rules(self) -> list[str]:
        types = set(self.node_types or self._available_node_types())
        found: set[str] = set()
        for name in self._scope():
            practice = self.graph.practices.opened.get(name)
            if practice is not None:
                found.update(practice.reading.in_graph.rule_run.rule_labels_for(types))
        return sorted(found)

    def _fill_from_nodes(self) -> None:
        self._relationships = self._available_relationships()
        self._rules = self._available_rules()

    def narrowed_by(self, request: FilterRequest) -> Filter:
        """This filter with a request's keys applied: practice(s), type(s), name, rules, relationships, violations, and
        path(s). The practices and node types chosen here hold where the request names none; chosen violations and
        relationships hold over the request's."""
        narrowed = Filter(self.graph)
        practices = self._listed(request, "practices", "practice")
        narrowed.practices = practices if practices is not None else (self._scope() if self.practices else [])
        types = self._listed(request, "types", "type")
        narrowed._node_types = types if types is not None else list(self.node_types)
        narrowed.name = request.get("name") or ""
        narrowed.paths = self._listed(request, "paths", "path") or []
        narrowed.violations = self.violations or bool(request.get("violations"))
        narrowed._rules = list(self.rules) if self.violations else list(request.get("rules") or [])
        narrowed._relationships = list(self.relationships) if self.relationships_selected else list(request.get("relationships") or [])
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
        return not self.paths or self._under_paths(node.source.file) or self._under_paths(self._named_from_folder(node.source))

    def _listed(self, request: FilterRequest, many: str, one: str) -> list[str] | None:
        """A request key that takes a list or a single value, such as ``types`` or ``type``; none when it names neither."""
        if many not in request and one not in request:
            return None
        return list(request.get(many) or ([request[one]] if request.get(one) else []))

    def _named_from_folder(self, source: Source) -> str | None:
        """source's file named from the graph's folder, as a viewer listing the folder names it: a practice that reads from
        a folder of its own, such as Stories from the project's .context, names its files from there; a file above the
        folder is named with `..`, as Session names the paths it filters by."""
        folder = self.graph.folder
        if not folder or not source.root or not source.file:
            return None
        return os.path.relpath(os.path.normpath(Path(source.root, source.file)), folder).replace("\\", "/")

    def _under_paths(self, file: str | None) -> bool:
        """True when ``file`` is one of the chosen paths or sits under one."""
        location = self._posix(file)
        folders = [self._posix(prefix) for prefix in self.paths]
        return any(folder and (location == folder or location.startswith(folder + "/")) for folder in folders)

    def _posix(self, path: str | None) -> str:
        """path with forward slashes and no slash at either end, as a node names its file."""
        return str(path or "").replace("\\", "/").strip("/")

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
            for edge in node.practice.reading.in_graph.edges(kind):
                if edge.parent is node or edge.child is node:
                    return True
        return False

    def collect(self, roots: Iterable[Node]) -> list[FilteredNode]:
        """Every node under roots, the roots included, that this filter matches, each once, with its ancestors' names
        and the rules this filter shows."""
        walk = _FilterWalk(self)
        for root in roots:
            walk.visit(root, [])
        return walk.found


class _FilterWalk:
    """One walk of a filter down the trees it collects from: the nodes it matched so far, and every node it has seen,
    so a node reached twice is collected once."""

    def __init__(self, wanted: Filter) -> None:
        self._wanted = wanted
        self.found: list[FilteredNode] = []
        self._seen: set[int] = set()

    def visit(self, node: Node, ancestors: list[str]) -> None:
        """Collect node, when the filter matches it, and then each node under it."""
        if id(node) in self._seen:
            return
        self._seen.add(id(node))
        wanted = self._wanted
        if wanted.matches(node):
            self.found.append(FilteredNode(node, ancestors, node.rules.chosen(wanted.violations, list(wanted.rules))))
        chain = [*ancestors, node.name]
        for child in node.children:
            self.visit(child, chain)


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
        self.data: NodeFacts = {}
        self.children: list[Node] = []
        self.parent: Node | None = None
        self._rules = None
        self._populated = False

    def set_fact(self, key: str, fact: FactValue) -> None:
        """Record one fact on this node for rules to read; facts save with the graph."""
        self.data[key] = fact
        if self.practice is not None and self.practice.reading.in_graph is not None:
            self.graph.build.changed()

    def set_facts(self, facts: NodeFacts) -> None:
        """Record each of facts on this node, as ``set_fact`` records one."""
        for key, fact in facts.items():
            self.set_fact(key, fact)

    def get_fact(self, key: str, default: FactValue = None) -> FactValue:
        """This node's fact, else the nearest ancestor's: a fact a whole file owns lives once, on the file's top node. A
        node no practice holds yet has only the ancestors its parser gave it."""
        node, visited = self, set()
        while node is not None and id(node) not in visited:
            if node._holds_attribute(key):
                return getattr(node, key)
            if key in node.data:
                return node.data[key]
            visited.add(id(node))
            node = node.parent or (node.graph.edges.direct_parent(node) if node.practice is not None else None)
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
    def facts(self) -> NodeFacts:
        """Every fact this node records: its saved attributes, then ``data``. This is what ``graph.json`` keeps."""
        found = {name: getattr(self, name) for name in self.graph_facts if hasattr(self, name)}
        found.update(self.data)
        return found

    def _holds_attribute(self, key: str) -> bool:
        return key in self.graph_facts and hasattr(self, key)

    @property
    def graph(self) -> Graph:
        """The graph that holds this node: its practice's."""
        return self.practice.reading.graph

    @property
    def schema(self):
        """This node's practice's schema, with its graph's pattern overlays applied."""
        return self.practice.reading.in_graph.rule_run.schema

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
        return self.practice.formats.reading_with(Path(file), self.graph.practices.held.values()) or "graph"

    @property
    def failed_rules(self) -> list[str]:
        return self.rules.failed_slugs

    @property
    def passing_rules(self) -> list[str]:
        """Rules that apply to this node and did not fail."""
        return self.rules.passing_slugs

    def place(self, location: Location) -> None:
        """Put this node at the lines location names, in its file under its practice's source root. A node its
        practice's reader found by a nearby line, such as a story's step, moves onto the lines that declare it."""
        self.source = Source.from_root(self.practice.reading.in_graph.source_root, location)

    def populate(self, parent: Node | None = None) -> None:
        """Put this node under parent in the explorer tree, then each node its edges lead to under it, depth first, in
        the order its edges sit. The walk keeps its own stack: a chain of edges, such as operations each invoking the
        next, runs deeper than Python's call stack would let a node populating its children call itself."""
        pending: list[Iterator[tuple[Node, Node | None]]] = [iter([(self, parent)])]
        while pending:
            step = next(pending[-1], None)
            if step is None:
                pending.pop()
                continue
            node, holder = step
            if node._placed_under(holder):
                pending.append(node._placements())

    def _placed_under(self, parent: Node | None) -> bool:
        """Join parent's children, taking parent as this node's own unless it has a better one; whether this node's
        own children are still to place, which is true only the first time."""
        if parent is not None:
            parent.children.append(self)
            if self.parent is None or (self._holder(self.parent) and not self._holder(parent)):
                self.parent = parent
        if self._populated:
            return False
        self._populated = True
        return True

    def _placements(self) -> Iterator[tuple[Node, Node]]:
        """Each node an edge leads to from this one, with the node it goes under: this one for a direct edge, else the
        node named for the edge's kind, made when the first such edge is placed. A kind no one filters by, the
        belongsTo back-edge and scopes, is no part of the explorer tree."""
        types = sorted((edge_type for edge_type in self.practice.reading.in_graph.edge_index.types.values() if edge_type.is_offered), key=lambda edge_type: edge_type.order)
        for edge_type in types:
            for edge in self._edges_in_source_order(edge_type.kind):
                yield edge.child, self if edge.display == "direct" else self._holder_for(edge.kind)

    def _holder_for(self, kind: str) -> Node:
        """The child named for kind that grouped and relationship edges of that kind sit under, made the first time."""
        holder = self._child_named(kind)
        if holder is None:
            holder = self._new_kind_node(kind)
            holder.parent = self
            self.children.append(holder)
        return holder

    def _edges_in_source_order(self, kind: str) -> list[Edge]:
        matched = self.graph.edges.from_parent(kind, self)
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
        return edge.child.type in edge.child.practice.reading.source_ordered_types

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
        first_home = (via is None or via is self.parent) and self.node_id not in seen
        if not first_home:
            return ExplorerEntry(self, [])
        seen.add(self.node_id)
        return ExplorerEntry(self, self._written_at_home(seen, stack | {self.node_id}))

    def _written_at_home(self, seen: set[str], path: set[str]) -> list[ExplorerEntry]:
        """The entries this node writes under it at its home place: each child, then its rules when the filter shows
        them."""
        written = [child.serialize(seen, self, path) for child in self.children]
        category = self._rule_category()
        if category is not None:
            written.append(category)
        return written

    def _rule_category(self) -> GraphRulesCollection | None:
        """The rules that apply to this node, as one child of it in the explorer tree; none when the filter shows none."""
        if self.type == self.name or self.type == "Practice":
            return None
        return self.rules if self.rules.shown else None

    def _new_kind_node(self, kind: str) -> Node:
        return Node(self.practice, kind, f"{self.practice.key}:{kind}:{self.node_id}", kind, self.source)


class Inventory:
    """Every open practice as the explorer's inventory shows it, with the pattern overlays applied and those available,
    read from the graph."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    @property
    @data_field
    def practices(self) -> dict[str, PracticeInventory]:
        return {key: PracticeInventory(self._graph, practice) for key, practice in self._graph.practices.opened.items()}

    @property
    @data_field
    def overlays(self) -> list[str]:
        return list(self._graph.overlays)

    @property
    @data_field
    def available_overlays(self) -> list[str]:
        return self._graph.applied_patterns.available


class AppliedOverlays(Inventory):
    """The inventory after a change of pattern overlays, with a sentence naming the overlays now applied."""

    def __init__(self, message: str, graph: Graph) -> None:
        super().__init__(graph)
        self._message = message

    @property
    @data_field
    def message(self) -> str:
        return self._message


class GraphExplorer:
    """The explorer's queries on one graph, which the graph makes once and keeps (``graph.explorer``), with the graph's
    own filter, which narrows what ``return_nodes`` and ``explorer_trees`` keep and which rules the tree shows."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.filter = Filter(graph)

    def inventory(self) -> Inventory:
        """Each open practice's node and edge counts, node types, and rules, with the overlays applied and those
        available."""
        return Inventory(self.graph)

    def filter_choices(self, practices: list[str], node_types: list[str], practices_before: list[str] | None) -> Filter:
        """The node types a filter offers and those it chooses once practices and node types are chosen, with the
        relationships and rules of the chosen ones; after a change of practice when practices_before names those chosen
        before. The graph's own filter is cleared."""
        self.filter.clear()
        offered = Filter(self.graph)
        if practices_before is not None:
            offered.select_practices(practices_before)
            offered.select_node_types(node_types)
            offered.change_practices(practices)
            return offered
        offered.select_practices(practices)
        offered.select_node_types(node_types)
        return offered

    def source(self, node_id: str) -> NodeSource | None:
        """The source of the node node_id, with every class, operation, and property the graph holds; none for an id
        with no node."""
        node = self.graph.node(node_id)
        if node is None:
            return None
        return NodeSource(node, members=self.source_members())

    def source_members(self) -> list[NodeSource]:
        """Every class, operation, and property the open practices hold, each with the class it belongs to."""
        declared = list(self.graph.practices.opened.values())
        classes = {node_type for practice in declared for node_type in practice.reading.class_types}
        members = {node_type for practice in declared for node_type in practice.reading.member_types}
        found = (node for practice in declared for node in practice.reading.in_graph.nodes() if node.type in classes | members)
        return [NodeSource(node, owner="" if node.type in classes else str(node.get_fact("owner", "") or "")) for node in found]

    def return_nodes(self, request: FilterRequest) -> list[FilteredNode]:
        """The nodes the graph's filter, narrowed by request, matches, with their ancestors and their rules."""
        roots = (practice.reading.in_graph.root for practice in self.graph.practices.opened.values())
        return self.filter.narrowed_by(request).collect(roots)

    def explorer_trees(self, request: FilterRequest) -> list[ExplorerEntry]:
        """The explorer tree of each practice the narrowed filter names, or of every open practice when it names none,
        keeping each practice's root, the nodes the filter matches, and the nodes on the way to them: each root with the
        entries below it, which are closed."""
        wanted = self.filter.narrowed_by(request)
        opened = self.graph.practices.opened
        named = [opened[key] for key in wanted.practices if key in opened] if wanted.practices else list(opened.values())
        return [tree.opened() for practice in named if (tree := practice.reading.in_graph.root.serialize().kept_by(wanted)) is not None]

    def explorer_branch(self, node_id: str, request: FilterRequest) -> ExplorerEntry | None:
        """The node node_id's entry as the narrowed filter keeps it, with the entries below it, which are closed; none
        for an id the graph no longer holds. The node is written at its home place, under its parent, where its children
        are."""
        node = self.graph.node(node_id)
        if node is None:
            return None
        kept = node.serialize(via=node.parent).kept_by(self.filter.narrowed_by(request))
        return kept.opened() if kept is not None else ExplorerEntry(node)


class PracticeNodes:
    """One practice's part of the graph that holds it: the root node its explorer tree starts from, the folder its
    source is read from, and its nodes by type and by id. The graph makes one for each practice it holds, keeps it, and
    gives it to the practice (``practice.reading.in_graph``), so code holding a practice asks it for its nodes
    (``stories.reading.in_graph.nodes("Story")``) instead of handing the practice back to the graph on every call. It holds
    three parts of its own, each made once: its edges, indexed by kind (``edge_index``), the run of its graph rules
    (``rule_run``), and what it takes back from saved records (``restore``)."""

    def __init__(self, graph: Graph, practice: PracticeGuidance) -> None:
        self.graph = graph
        self.practice = practice
        # The graph's build, which counts each change to what the graph holds.
        self._build = graph.build
        self._source_root: Path | None = None
        self._root: Node | None = None
        self._by_id: dict[str, Node] = {}
        # The nodes by type. A type offered before any node of it is read holds none yet; the types keep the order
        # each was first offered or held, so the explorer lists them the same way in every process.
        self._nodes: dict[str, list[Node]] = {}
        self.edge_index = EdgeIndex(self._build.changed)
        self.rule_run = PracticeRuleRun(self)
        self.restore = PracticeRestore(self)

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
    def root(self) -> Node:
        """The node the practice's explorer tree starts from, which holds the facts about the practice as a whole."""
        if self._root is None:
            raise GraphFailure("root", f"{self.practice.key} is not open in this graph")
        return self._root

    def open(self, root: Path | None) -> None:
        """Read the practice from root, starting from its root node alone."""
        self._build.changed()
        if root is not None:
            self._source_root = Path(root)
        if self._root is None:
            key = self.practice.key
            self._root = Node(self.practice, "Practice", f"{key}:Practice:.:{key}", key, Source(".", 0, 0))
        self._by_id[self._root.node_id] = self._root

    def close(self) -> None:
        """Forget every node and edge, so a load reads them again from nothing."""
        self._build.changed()
        self._root = None
        for store in (self._by_id, self._nodes):
            store.clear()
        self.edge_index.clear()

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
        edited = self.graph.scope.edited_files
        if edited is None:
            return found
        files = self._files_from_root(path.resolve() for path in edited)
        return [node for node in found if node.source.file in files]

    def _files_from_root(self, files: Iterable[Path]) -> set[str]:
        """Each of files under the practice's source root, as a path from that root, the way its nodes name their file."""
        root = self._source_root.resolve() if self._source_root is not None else self.graph.scope.folder
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
    def node_types(self) -> list[str]:
        """The node types the graph offers for the practice, those the practice offers and those it holds a node of, in
        the order each was first offered or held."""
        return list(self._nodes)

    def offer_node_types(self, types: Iterable[str]) -> None:
        """Offer these node types in the explorer's filter, before any node of them is read."""
        for node_type in types:
            self._nodes.setdefault(node_type, [])

    def add(self, node: Node, node_id: str, location: Location) -> Node:
        """Make node one of the practice's nodes, called node_id, at the lines location names in its file; the node the practice already
        calls node_id when there is one. A parsed object leaves the throwaway graph its parser built it in. It keeps the
        parent its parser gave it only when that parent is one of the practice's nodes too, such as an operation's class;
        the tree itself is built from the practice's edges."""
        existing = self._by_id.get(node_id)
        if existing is not None:
            return existing
        self._release_from_its_practice(node)
        node.practice = self.practice
        node.node_id = node_id
        parent = node.parent
        if parent is None or self._by_id.get(getattr(parent, "node_id", "")) is not parent:
            node.parent = None
        node.place(location)
        self.hold(node)
        node.forget_rules()
        return node

    def add_file(self, type: str, relative: str, name: str = "") -> Node:
        """The practice's node of type for the whole file or folder at relative, under its source root, such as a
        pattern's tier file or an aggregate's folder: the one it holds, else one made and added with no parsed object
        behind it. name defaults to the file's stem."""
        node_id = f"{self.practice.key}:{type}:{relative}"
        held = self._by_id.get(node_id)
        if held is not None:
            return held
        source = Source.whole_file(relative, self.source_root)
        node = Node(self.practice, type, node_id, name or Path(relative).stem, source)
        return self.add(node, node_id, Location(source.file, source.start_line, source.end_line))

    def hold(self, node: Node) -> None:
        """Keep node, one of this practice's, by its type and its id."""
        self._build.changed()
        self._nodes.setdefault(node.type, []).append(node)
        self._by_id[node.node_id] = node

    def _release_from_its_practice(self, node: Node) -> None:
        """Take node out of the practice that holds it, in whichever graph that is, so this practice can take it."""
        practice = getattr(node, "practice", None)
        part = practice.reading.in_graph if practice is not None else None
        if isinstance(part, PracticeNodes):
            part.release(node)

    def release(self, node: Node) -> None:
        """Let go of node when the practice holds it, so another practice can take it."""
        if self._by_id.get(node.node_id) is not node:
            return
        self._build.changed()
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

    def forget_files(self, files: Iterable[Path]) -> set[int]:
        """Drop every node read from one of files, so a refresh reads those files again from nothing; answer the ``id``
        of each node dropped, whose edges every practice then drops."""
        read_from = self._files_from_root(files)
        return self.forget({id(node) for node in self._by_id.values() if node is not self._root and node.source.file in read_from})

    def forget(self, dropped: set[int]) -> set[int]:
        """Drop the nodes whose ``id`` is in dropped; answer dropped."""
        if dropped:
            self._build.changed()
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
        self._build.changed()
        for node in self._by_id.values():
            node.forget_rules()

    def rebuild_tree(self) -> None:
        """Rebuild the practice's explorer tree from its edges after late-bound nodes or overlays."""
        for node in self._by_id.values():
            node.leave_tree()
        self.root.populate()

    ## edges

    def edges(self, kind: str | None = None) -> list[Edge]:
        """Every edge recorded on the practice, the practice of each edge's parent, or only those of kind."""
        return self.edge_index.of(kind)



class PracticeRuleRun:
    """The graph rules one practice runs in the graph that holds it, which its part of the graph makes once and keeps
    (``practice.reading.in_graph.rule_run``): the practice's schema with the graph's pattern overlays, made once for each set of
    overlays, which says the node types each rule applies to; the checks it runs, its own and those the overlays add;
    and the run itself, which records each violation on the node it was found on."""

    def __init__(self, part: PracticeNodes) -> None:
        self._part = part
        self._schemas: dict[tuple[GraphOverlay, ...], PracticeSchema] = {}

    @property
    def schema(self) -> PracticeSchema:
        """The practice's schema, with the graph's pattern overlays and the practice's supplements applied."""
        return self.schema_with(self._part.graph.applied_patterns.overlays_for(self._part.practice))

    def schema_with(self, overlays: tuple[GraphOverlay, ...]) -> PracticeSchema:
        """The practice's schema with overlays applied, made the first time and kept here."""
        schema = self._schemas.get(overlays)
        if schema is None:
            schema = self._schemas[overlays] = PracticeSchema(self._part.practice, overlays)
        return schema

    @property
    def checks(self) -> dict:
        """The graph rules the practice checks in this graph, by slug: its own and those the graph's pattern overlays
        add to it."""
        return self._part.graph.applied_patterns.checks_of(self._part.practice)

    @property
    def rule_labels(self) -> list[str]:
        """Each rule the practice runs, named ``practice.node.rule`` with the pattern that owns it in front."""
        schema = self.schema
        return schema.rule_labels(schema.applicable)

    def rule_labels_for(self, types: set[str]) -> set[str]:
        """The labels of the rules the practice's nodes of these types run, and of those a node of them fails."""
        schema = self.schema
        labels = {schema.rule_label(node_type, rule) for rule, rule_types in schema.applicable.items() for node_type in rule_types if node_type in types}
        failing = (node for node_type in types for node in self._part.nodes(node_type))
        labels.update(schema.rule_label(node.type, slug) for node in failing for slug in node.failed_rules)
        return labels

    def check(self) -> None:
        """Run every graph rule the practice checks, over the whole practice, then node by node, and record each
        violation on the node it was found on. A practice names the rules it checks itself (``practice.reading.checks()``),
        with those the graph's pattern overlays add; which of them apply to one node, the node says (``node.rules``)."""
        practice = self._part.practice
        checks = list(practice.reading.checks().values())
        if not checks:
            return
        context = RuleCheckContext(practice, self._part.source_root_path)
        for index, check in enumerate(checks, start=1):
            report_progress(f"{practice.key} · rule {check.slug} · {index}/{len(checks)}")
            for node_id, message in check.check_practice(context):
                node = self._part.graph.node(node_id)
                if node is not None:
                    node.rules.record_violation(check.slug, message)
        self._check_each_node(context)

    def offer_overlay_types(self, overlays: list[GraphOverlay]) -> None:
        """Offer the node and relationship types the overlays' schemas give the practice in the explorer's filter, before
        the rules run."""
        part = self._part
        schema = self.schema
        part.offer_node_types(schema.types)
        for kind in schema.overlay_relationship_kinds - set(part.edge_index.types):
            display = "direct" if any(overlay.display_of(kind) == "direct" for overlay in overlays) else "relationship"
            # A kind no edge was recorded under is listed after the ones the tree shows.
            part.edge_index.offer(EdgeType(kind, EdgeType.from_kind(kind, "relationship").order, display))

    def _check_each_node(self, context: RuleCheckContext) -> None:
        """A node another practice's class covers skips that practice's checks, which already ran on the class."""
        covering = self._covering_classes()
        nodes = self._part.nodes()
        key = self._part.practice.key
        for index, node in enumerate(nodes, start=1):
            report_progress(f"{key} · rules · {index}/{len(nodes)} · {node.type} {node.name}")
            skipped = {slug for slugs, spans in covering for slug in slugs if self._inside(node, spans)}
            for rule in node.rules:
                if not rule.runs or rule.slug in skipped:
                    continue
                for message in rule.check(node, context):
                    node.rules.record_violation(rule.slug, message)

    def _inside(self, node: Node, spans: dict[str, list[tuple[int, int]]]) -> bool:
        """Whether node's lines overlap one of the class spans of its file."""
        file = (node.source.file or "").replace("\\", "/")
        start, end = node.source.start_line, node.source.end_line
        return any(start <= class_end and class_start <= end for class_start, class_end in spans.get(file, ()))

    def _covering_classes(self) -> list[tuple[frozenset[str], dict[str, list[tuple[int, int]]]]]:
        """For each other open practice that checks whole classes: its check slugs, and its classes' line spans by
        file."""
        found = []
        for other in self._part.graph.practices.opened.values():
            class_type = other.reading.class_node_type
            if other is self._part.practice or not class_type:
                continue
            spans: dict[str, list[tuple[int, int]]] = {}
            for node in other.reading.in_graph.nodes(class_type):
                if node.source.file:
                    spans.setdefault(node.source.file.replace("\\", "/"), []).append((node.source.start_line, node.source.end_line))
            found.append((frozenset(other.reading.checks()), spans))
        return found


class PracticeRestore:
    """What one practice takes back from saved records, which its part of the graph makes once and keeps
    (``practice.reading.in_graph.restore``): a saved graph's practice when a graph is opened from it or holds a worker's whole
    answer, or the changes a worker answers for a refresh. Nodes come back first, as plain nodes holding their saved
    facts at the lines they were saved at; the edges and violations come back once every practice's nodes are back,
    since an edge may join another practice's node."""

    def __init__(self, part: PracticeNodes) -> None:
        self._part = part

    def nodes(self, saved: SavedPractice) -> None:
        """Hold the nodes saved keeps for the practice that it does not hold yet, and the facts its root kept about the
        practice as a whole."""
        part = self._part
        if saved.source_root:
            part.source_root_path = Path(saved.source_root)
        part.root.data.update(saved.root_facts)
        for kept in saved.nodes:
            if not part.holds(kept.node_id):
                self._take(kept)

    def changes(self, changes: PracticeChanges) -> None:
        """Drop the edges and nodes changes says the practice no longer holds, and hold each node it names new or
        changed: a node the practice holds already is changed in place, so the edges that join it stay."""
        part = self._part
        if changes.dropped_edges:
            named = set(changes.dropped_edges)
            part.edge_index.drop(lambda edge: (edge.kind, edge.parent.node_id, edge.child.node_id) in named)
        dropped = set(changes.dropped_nodes)
        part.forget({id(node) for node in part.nodes() if node.node_id in dropped})
        for kept in changes.nodes:
            self._take(kept)
        if changes.root_facts is not None:
            part.root.data = dict(changes.root_facts)

    def _take(self, kept: SavedNode) -> None:
        """Hold the node kept describes, as a saved graph or a worker's changes keep it: a plain node holding its saved
        facts at the lines it was saved at, or, when the practice holds a node of that id, that node made what kept says
        in place, so the edges that join it stay."""
        part = self._part
        node = part.node(kept.node_id)
        if node is None:
            node = Node(part.practice, kept.type, kept.node_id, kept.name, Source.from_root(part.source_root, kept.location))
            part.hold(node)
        elif node.type != kept.type:
            part.release(node)
            node.type = kept.type
            part.hold(node)
        node.name = kept.name
        node.source = Source.from_root(part.source_root, kept.location)
        node.stage = kept.stage
        node.data = dict(kept.facts)
        part.graph.build.changed()

    def links(self, saved: SavedPractice | PracticeChanges) -> None:
        """Record each edge saved keeps between nodes the graph holds, as it was saved and no other way: a practice that
        links its nodes to another's records the edge back itself when it wants one, so the graph holds exactly the edges
        the build that saved them held. Then give each node its saved violations in place of those it held."""
        graph = self._part.graph
        for kept in saved.edges:
            parent, child = graph.node(kept.parent), graph.node(kept.child)
            if parent is not None and child is not None:
                graph.edges.record(kept.type, parent, child)
        for node_id, hits in saved.violations_by_node.items():
            node = graph.node(node_id)
            if node is not None:
                node.forget_rules()
                for violation in hits:
                    node.rules.restore(violation)


class GraphEdges:
    """The edges between the nodes of one graph, which the graph makes once and keeps (``graph.edges``). Each edge is
    kept on its parent's practice, and its display says where the explorer tree shows it: a direct edge hangs the
    child under the parent, a grouped edge under a child named for its kind, and a relationship edge lists the child
    there without moving it."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    def link(self, kind: str, parent: Node, child: Node) -> None:
        """Record a direct edge of kind from parent to child: child is one of parent's parts."""
        self.record(EdgeType.from_kind(kind, "direct"), parent, child)

    def relate(self, kind: str, parent: Node, child: Node) -> None:
        """Record a relationship edge of kind from parent to child: parent refers to child, which stays where it is."""
        self.record(EdgeType.from_kind(kind, "relationship"), parent, child)

    def group(self, kind: str, parent: Node, child: Node) -> None:
        """Record a grouped edge of kind from parent to child, which the tree shows under a child of parent named for
        kind."""
        self.record(EdgeType.from_kind(kind, "grouped"), parent, child)

    def record(self, edge_type: EdgeType, parent: Node, child: Node) -> None:
        """Record an edge of edge_type from parent to child on the parent's practice, once."""
        self._graph.practices.part_of(parent.practice).edge_index.record(edge_type, parent, child)

    def from_parent(self, kind: str, parent: Node) -> list[Edge]:
        """Edges of one kind leaving parent, in recorded order."""
        return self._graph.practices.part_of(parent.practice).edge_index.from_parent(kind, parent)

    def direct_parent(self, child: Node) -> Node | None:
        """The node a direct edge of the child's practice hangs the child under; available before populate sets
        ``parent``."""
        return self._graph.practices.part_of(child.practice).edge_index.direct_parent(child)


def _where_it_sits(node: Node) -> tuple:
    """Where node sits: its file, its lines, then its id, which tells apart two nodes on one line."""
    return (node.source.file or "", node.source.start_line, node.source.end_line, node.node_id)


@language_adapter(language="typescript")
@agent_toolset
class Graph:
    """One graph. Builders fill nodes, edges, and rules. The explorer reads the tree.

    The graph holds its practices (``graph.practices``): the PracticeGuidance objects it is given, each of which knows
    this graph, so a node's practice is one of them (``node.practice``). It gives each practice its part of the graph, a
    *PracticeNodes* made once and kept, which holds the practice's nodes, edges, and root
    (``practice.reading.in_graph.nodes("Story")``); the graph aggregates those parts. A session gives its graph the session's own
    practices, the same objects its actions work with; a graph no session holds makes a set of its own from the
    catalogue; a model object made apart from any graph joins one when a graph adopts it. The graph changes only when a
    call asks: ``load_working_copy`` and ``load_files`` read a folder or files, and ``refresh`` reads again exactly the
    files an action wrote. Each of its jobs is a part it makes once and keeps: its practices, the scope of the read it
    last made (``scope``, a *LoadScope* each read makes for itself), its build (``build``), the schema edges between its
    model objects (``schema_edges``), and the explorer's queries (``explorer``). Its MCP operations are the one entry."""

    def __init__(self, practices: Iterable[PracticeGuidance] | None = None) -> None:
        self.build = GraphBuild(self)
        held = list(PRACTICE_CATALOGUE.create_all(fidelity=None) if practices is None else practices)
        for practice in held:
            practice.reading.held_in(self, PracticeNodes(self, practice))
        self.practices = GraphPractices(self, held)
        # The scope of the load or refresh the graph last made: its folder, and the files it was limited to.
        self.scope = LoadScope(None)
        # The saved graph file of the folder last loaded, with that folder.
        self._saved_graph_file: tuple[Path, SavedGraphFile] | None = None
        # The folder a session's graph is saved in, the session's own folder; none for a graph no session holds, such as
        # the graph tool's, which saves in the folder it loads.
        self.kept_in: Path | None = None
        # The pattern overlays this graph applies, each pattern made once.
        self.applied_patterns = PatternOverlays()
        self.schema_edges = SchemaEdges(self)
        self.edges = GraphEdges(self)
        self.explorer = GraphExplorer(self)
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
            # Holding no node yet, the graph stands on none of the working copy until a load reads it.
            self.scope = LoadScope(folder, [])
            self.practices.choose({practice: folder for practice in self.practices.held.values()})
            self.practices.open_chosen()

    def open_saved(self, folder: Path) -> None:
        """Open this graph on folder, then read back the graph saved in its ``.context`` when there is one, each saved
        practice on the source root it was read from, with the violations it was saved with: a session opened again
        shows what was loaded in it before. Its rules run again on the next load or refresh, which a call makes and
        which builds where that call says; opening a session runs no build. A folder with nothing saved opens holding
        no node until a load reads it."""
        self.open(folder)
        with self._changing:
            saved = self.saved_file.read()
            if saved is not None:
                self.overlays = list(saved.overlays)
                self.practices.reopen(saved, folder)
                if saved.holds(self.practices.roots_by_key, self.overlays):
                    self.scope = LoadScope(folder)

    @property
    @data_field
    def folder(self) -> str:
        return "" if self.scope.folder is None else str(self.scope.folder)

    @property
    @data_field
    def overlays(self) -> list[str]:
        """The folders of the pattern overlays this graph applies."""
        return list(self.applied_patterns.paths)

    @overlays.setter
    def overlays(self, overlays: list[str]) -> None:
        """Apply the overlays named, each a folder or a pattern's name: the graph holds the pattern each one is, and
        asks each for the GraphOverlay it owns."""
        self.applied_patterns.apply(list(overlays))

    ## the practices this graph holds, and their nodes and edges

    def practice(self, key: str) -> PracticeGuidance:
        """The practice called key among those this graph holds, opened in this graph on the folder it last loaded the
        first time it is asked for. It is always the same object: the one the graph was given. This is the one lookup
        by key, for a call that names a practice by the key it sent; code that knows the practice's class asks
        ``graph.practices.of``."""
        return self.practices.named(key)

    def node(self, node_id: str) -> Node | None:
        """The node called node_id, in whichever practice holds it; none when no practice does."""
        found = (practice.reading.in_graph.node(node_id) for practice in self.practices.held.values())
        return next((node for node in found if node is not None), None)

    def restored_from(self, saved: SavedGraph) -> None:
        """Hold every practice saved keeps, with the overlays it was saved with: each practice's nodes first, then the
        edges between them, which may cross practices, and the violations on them."""
        self.overlays = list(saved.overlays)
        self.practices.hold(saved, self.scope.folder)

    ## loading and refreshing

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
            self.scope = LoadScope(Path(database or folder).resolve())
            self.practices.choose({self.practices.named(key): (Path(folder) / root).resolve() for key, root in practices.items()})
            self.overlays = list(overlays or [])
            return self.build.load(force, call)

    @long_call
    @mcp
    @agent_tool
    def load_practice_roots(self, call: ToolCall | None = None) -> GraphLoaded:
        """Open each practice this graph holds on the folder its session names for it (its session root), with the
        overlays the graph applies, and build: the Graph app's whole load, with no folder or practice named by the
        caller. A session's graph holds only the practices its session works on, so a practice turned off is never
        read. A practice no session works in has no root, and one whose folder is not written yet has nothing to read:
        both are left out."""
        with self._changing:
            roots = {practice: root for practice in self.practices.held.values() if (root := practice.session_root) is not None and root.is_dir()}
            if not roots:
                return GraphLoaded("No practice root of a session is there to read, so nothing was loaded.")
            self.scope = LoadScope(self.scope.folder)
            self.practices.choose(roots)
            return self.build.load(False, call)

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
            root = Path(folder).resolve()
            self.scope = LoadScope.of_paths(root, files)
            self.practices.choose({self.practices.named(key): root for key in practices})
            self.overlays = list(overlays or [])
            report_progress("Reading the edited files")
            self.practices.open_chosen()
            self.build.run(BuildTask(BuildStep.READ), call)
            return GraphLoaded(f"Loaded {len(self.scope.edited_files or [])} edited files.")

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
            return self.build.refresh(paths, call)

    def hold_whole(self, call: ToolCall | None = None) -> None:
        """Make sure the graph holds the whole working copy across every practice it holds, reading it, or the saved
        graph when that holds it, when it does not yet: a validate judges links across practices, which a graph holding
        only some files cannot."""
        with self._changing:
            if self.scope.over_whole or self.scope.folder is None:
                return
            self.scope = LoadScope(self.scope.folder)
            self.build.load(False, call)

    def refreshed(self, paths: list[str], checked: Path, call: ToolCall | None = None) -> None:
        """Refresh the graph with exactly the files at paths and write the nodes read from them, as they save, at
        checked, as one change: no other call's load or refresh comes between the two, so a call that checks the files
        it names sees the graph its own refresh left, whatever other calls in the session do at the same time. The build
        writes them, in its worker for a chat's call, so the server answering chats never serialises them."""
        with self._changing:
            self.build.refresh(paths, call, CheckedFiles(paths, checked))

    @mcp
    @agent_tool
    def save_json(self) -> GraphSaved:
        """Write the serialized graph into the loaded folder's ``.context``.

        Practices already on disk that are not part of this load stay in the file.
        """
        if self.scope.folder is None:
            return GraphSaved("")
        saved_file = self.saved_file
        return GraphSaved(str(saved_file.write(SavedGraph.from_graph(self).merged_over(saved_file.read()))))

    @property
    def saved_file(self) -> SavedGraphFile:
        """The saved graph file of the loaded folder, made once for each folder the graph loads; a validate that checks
        the session's saved graph reads it here."""
        folder = self.scope.folder or Path()
        path = self.kept_in / GRAPH_FILE_NAME if self.kept_in is not None else None
        held = self._saved_graph_file
        if held is None or held[0] != folder:
            held = self._saved_graph_file = (folder, SavedGraphFile(folder, report_progress, path))
        return held[1]

    @long_call
    @mcp
    @agent_tool
    def set_overlays(self, overlays: list[str], call: ToolCall | None = None) -> AppliedOverlays:
        """Apply pattern overlays, folders holding practices/, and rebuild the explorer tree from the open folder; answer with the graph's inventory."""
        with self._changing:
            self.overlays = list(overlays or [])
            if self.scope.folder is not None and self.practices.chosen:
                self.scope = LoadScope(self.scope.folder)
                self.build.load(False, call)
        label = ", ".join(Path(item).name for item in self.overlays) if self.overlays else "none"
        return AppliedOverlays(f"Applied pattern overlays: {label}.", self)

    @mcp
    @agent_tool
    def overlay_of(self, folder: str) -> Overlay:
        """Return the pattern overlay folder holds: folder itself or the overlay root above it, which must hold practices/."""
        root = self.applied_patterns.root_of(folder)
        if not (root / "practices").is_dir():
            raise GraphFailure("overlay_of", f"Not an overlay root (missing practices/): {folder}")
        return Overlay(str(root))

    ## the explorer's queries

    @mcp
    @agent_tool
    def practice_names(self) -> list[str]:
        """Return the name of every practice the graph can load, in the order the approach walks them."""
        return list(self.practices.held)

    @mcp
    @agent_tool
    def inventory(self) -> Inventory:
        """Return each loaded practice's node and edge counts, node types, and rules, with the overlays applied and those available; explorer_trees answers the trees."""
        return self.explorer.inventory()

    @mcp
    @agent_tool
    def filter_choices(self, practices: list[str], node_types: list[str], practices_before: list[str] | None = None) -> Filter:
        """Return the node types a filter offers and those it chooses, with the relationships and rules of the chosen
        ones (of every offered one when none is chosen), once practices and node types are chosen. practices_before
        names the practices chosen before a change of practice: then node_types are those chosen before, the ones the
        new practices still hold stay chosen, and every node type of each practice added is chosen. The graph's own
        filter is cleared."""
        return self.explorer.filter_choices(practices, node_types, practices_before)

    @mcp
    @agent_tool
    def source(self, node_id: str) -> NodeSource | None:
        """Return the source of the node node_id: its file, text, and lines, with every class, operation, and property the loaded graph holds, so calls in it can be opened in place. None for an id with no source, such as a rule's row."""
        return self.explorer.source(node_id)

    @mcp
    @agent_tool
    @skill(name="read-graph")
    def return_nodes(self, filter: dict | None = None) -> list[FilteredNode]:
        """Return matching graph nodes as JSON, with ancestors, children, and relationships.

        filter keys: practice(s), type(s), name, rules, relationships;
        violations: true returns only failing nodes with only their failing rule rows;
        paths: source path prefixes (relative to the folder, e.g. src/orders) a node must sit under.
        """
        return self.explorer.return_nodes(filter or {})

    @mcp
    @agent_tool
    def explorer_trees(self, filter: dict | None = None) -> list[ExplorerEntry]:
        """Return the explorer tree of each practice the filter names, or of every loaded practice when it names none, keeping each practice's root, the nodes the filter matches with their rules, and the nodes on the way to them. Each root comes with the entries below it, closed: each keeps its rules and says how many entries below it were left out (children_left_out), which explorer_branch answers. filter takes the keys return_nodes takes."""
        return self.explorer.explorer_trees(filter or {})

    @mcp
    @agent_tool
    def explorer_branch(self, node_id: str, filter: dict | None = None) -> ExplorerEntry | None:
        """Return the node node_id's explorer entry as the filter keeps it, with the entries below it, closed as explorer_trees closes them; None for an id the graph no longer holds. filter takes the keys return_nodes takes, the same filter the tree was read with."""
        return self.explorer.explorer_branch(node_id, filter or {})
