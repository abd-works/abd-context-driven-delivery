"""Graph. Practice graphs, nodes, edges, and the explorer tree."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Callable, Iterable, Iterator


from harness.agent_tools import agent_tool, agent_toolset
from harness.annotations.annotation import hosted_only
from harness.agent_tools.progress import report_progress
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from harness.installation.data_class import data_field, language_adapter
from harness.installation.files import command, skill
from harness.mcp.mcp_annotations import long_call, mcp
from harness.graph.edge import Display, Edge, EdgeFacts, EdgeIndex, EdgeType
from harness.graph.explorer import ExplorerEntry, FilteredNode, GraphLoaded, GraphSaved, NodeSource, Overlay, PracticeInventory
from harness.graph.file_lines import FileLines, PathKind
from harness.markdown.markdown import MarkdownText
from harness.graph.graph_build import GraphBuild
import harness.graph.graph_app  # noqa: F401 - registers the Graph app with App, so the server health report lists it
from harness.graph.graph_practices import GraphPractices
from harness.graph.graph_reads import GraphReads
from harness.graph.node_filter import Filter, FilterChoices, FilterRequest
from harness.graph.violation_correction import ViolationCorrections
from harness.graph.node_metric import METRIC_TYPE, METRICS_GROUP
from harness.graph.graph_rules_collection import GraphRulesCollection
from harness.graph.load_scope import LoadScope
from harness.graph.location import Location
from harness.graph.pattern_overlays import GraphChecks, GraphOverlay, PatternOverlays
from harness.graph.rule_context import RuleCheckContext
from harness.graph.schema_edges import SchemaEdges
from harness.graph.schema_rules import PracticeSchema
from harness.graph.saved_graph import GRAPH_FILE_NAME, FactValue, NodeFacts, NodeIdentity, PracticeChanges, SavedGraph, SavedGraphFile, SavedNode, SavedPractice

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

    def __init__(self, line: int, operation: str) -> None:
        self.line = line
        self.operation = operation


# The files a slice reads as markdown sections rather than code: a story map's and a scenario file's text.
MARKDOWN_SUFFIXES = frozenset({".md", ".markdown"})
# The fact a node keeps the fidelity it was read at under (``Node.read_at``).
READ_AT_FIDELITY = "read_at_fidelity"


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


def as_code_writes(text: str) -> tuple[str, ...]:
    """text as a line of a file can hold it: as it is, and as code writes it inside a string of the same quotes, each
    quote escaped (``refuses with \\"not paid\\"``). A step is found on its line by any of them."""
    return (text, text.replace('"', '\\"'), text.replace("'", "\\'"))


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
            self._load_calls(raw)
            self._text = self._insert_calls(raw)
        return self._text

    def _load_calls(self, raw: str) -> None:
        self.calls = []
        for index, line in enumerate(raw.splitlines()):
            self._calls_on_line(line, index + 1)

    def _insert_calls(self, raw: str) -> str:
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
        written = as_code_writes(quote)
        hits = [index for index, line in enumerate(lines) if any(form in line for form in written)]
        if not hits:
            return
        chosen = min(hits, key=lambda index: (abs(index + 1 - self.start_line), index))
        self.start_line = chosen + 1
        self.end_line = self._call_end(lines, chosen)
        self._text = None

    def align_to_table_row(self, name: str) -> None:
        """Point this slice at the first row of a markdown table in its file that holds name as one of its cells, with
        or without the underline marks around it; left where it is when no row does."""
        for index, line in enumerate(self._file_lines()):
            cells = [cell.strip().strip("+").strip() for cell in line.strip().strip("|").split("|")] if line.lstrip().startswith("|") else []
            if name in cells:
                self.start_line = self.end_line = index + 1
                self._text = None
                return

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

    def align_to_example_export(self, name: str, files: Iterable[Path]) -> None:
        """Point this slice at the fixture named ``name`` in one of ``files``, the TypeScript files under its root the
        read is scoped to: a fixture function, or an exported constant such as ``export const DONE = {...}``. A story
        test imports both from its examples file, so an example it names belongs there, not at the test that uses it.
        Only the files given are searched, so a read limited to the files being edited never opens any other file."""
        if not self.root or not name:
            return
        root_path = Path(self.root)
        function = re.compile(rf"(?:export\s+)?function\s+{re.escape(name)}\b")
        constant = re.compile(rf"\bexport\s+const\s+{re.escape(name)}\b")
        for path in sorted(files):
            if FileLines(path).kind is not PathKind.FILE:
                continue
            lines = FileLines(path).lines
            for index, line in enumerate(lines):
                if function.search(line) or constant.search(line):
                    end = self._call_end(lines, index) if function.search(line) else self._declaration_end(lines, index)
                    self._point_at(Location(path.relative_to(root_path).as_posix(), index + 1, end))
                    return

    def align_to_declaration(self, declared_in: Path, start_line: int, end_line: int) -> None:
        """Point this slice at lines start_line to end_line of declared_in, a file under its root its reader already
        read, such as the examples module a Python story test imports a fixture from; a file outside the root leaves it
        where it is, since a node names its file from its root."""
        if not self.root:
            return
        try:
            relative = Path(declared_in).resolve().relative_to(Path(self.root).resolve())
        except ValueError:
            return
        self._point_at(Location(relative.as_posix(), start_line, end_line))

    def _point_at(self, location: Location) -> None:
        """Point this slice at the lines location names, in its file under its root."""
        self.file = location.file
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
        if PurePosixPath(self.file or "").suffix.lower() in MARKDOWN_SUFFIXES:
            return self._section_end(lines, start)
        return self._code_call_end(lines, start)

    def _section_end(self, lines: list[str], start: int) -> int:
        """In markdown, where prose's apostrophes and links are no code: the last line of the section a heading on start
        opens, or start's own line for a step or any other line."""
        section = MarkdownText("\n".join(lines)).section_lines(start + 1)
        return section[1] if section is not None else start + 1

    def _code_call_end(self, lines: list[str], start: int) -> int:
        """The line the call or block that opens at start closes on: the first where its parentheses and braces are
        all closed again after one has opened. A Python decorator, such as a shared story's scenario or step, closes
        its call on its own line, so it runs on through the function it decorates."""
        depth = _BracketDepth()
        for index in range(start, len(lines)):
            depth.read(lines[index])
            if depth.opened_call and depth.closed:
                return self._decorated_end(lines, index + 1) if lines[start].lstrip().startswith("@") else index + 1
        return max(self.end_line, start + 1)

    def _decorated_end(self, lines: list[str], after: int) -> int:
        """The last line of the function or class a Python decorator ending on line after (counted from 1) decorates: the
        last line indented under its def. After decorators stacked below, or no def at all, the decorator's own line."""
        found = next((index for index in range(after, len(lines)) if not lines[index].lstrip().startswith("@")), None)
        if found is None or not re.match(r"\s*(async\s+)?(def|class)\b", lines[found]):
            return after
        indent = len(lines[found]) - len(lines[found].lstrip())
        end = found
        for index in range(found + 1, len(lines)):
            if not lines[index].strip():
                continue
            if len(lines[index]) - len(lines[index].lstrip()) <= indent:
                break
            end = index
        return end + 1

    def _read(self) -> str:
        lines = self._file_lines()
        if not lines:
            return ""
        if self._directory():
            return "\n".join(lines)
        return "\n".join(lines[max(0, self.start_line - 1) : self.end_line])

    def _calls_on_line(self, line: str, line_number: int) -> None:
        for found in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?)\s*\(", line):
            name = found.group(1)
            receiver = name.split(".", 1)[0] if "." in name else ""
            method = name.rsplit(".", 1)[-1]
            if method in self._SKIP or receiver in self._SKIP_RECEIVER or self._declares(line, found.start()):
                continue
            self.calls.append(Call(line_number, name))

    def _declares(self, line: str, start: int) -> bool:
        return re.search(r"(?:async|function|def|public|private|protected|static|get|set)\s+$", line[:start]) is not None


class Node:
    """children is the list populate writes on this node. Direct edges are the children. Grouped and relationship edges sit under one child named for the kind.

    A practice's parsed objects (a class, an operation, a scenario, a step) are nodes themselves: a practice reader adds
    the object it parsed to its practice graph, and rules read measurements straight from it. ``data`` holds only the
    facts the reader knows and the object does not, such as which folder a class sits in. A graph reloaded from
    ``graph.json`` holds plain nodes, whose saved facts are all in ``data``.
    """

    graph_facts: tuple[str, ...] = ()
    """The attributes of a parsed object that save with the graph, so a reloaded graph still answers ``get_fact``."""

    def __init__(self, practice: PracticeGuidance, identity: NodeIdentity, source: Source) -> None:
        self.practice = practice
        self.type = identity["type"]
        self.node_id = identity["node_id"]
        self.name = identity["name"]
        self.source = source
        self.stage = ""
        self.data: NodeFacts = {}
        self.children: list[Node] = []
        self.parent: Node | None = None
        self._rules = None
        self.tree = NodeTree(self)

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
    def schema(self) -> PracticeSchema:
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

    def read_at(self, fidelity: str) -> None:
        """Record the fidelity this node was read at, by the fidelity's name (``model``, ``code``), as a fact, so a
        saved graph keeps it. Its practice's reading calls this as it reads, deciding by what the content holds and
        never by the format it is written in: a class whose operations have no bodies is at the model fidelity in code,
        in a model document, or in a drawing. Record it on the node the test applies to, such as a class; its parts
        answer it too."""
        self.set_fact(READ_AT_FIDELITY, fidelity)

    @property
    def fidelity_read_at(self) -> str:
        """The name of the fidelity this node was read at, as its reading recorded it on the node or on the nearest
        node above it, so an operation, a property and a parameter take their class's; empty when no reading recorded
        one. ``node.fidelity`` answers another question: the fidelity that creates the node's type."""
        return str(self.get_fact(READ_AT_FIDELITY, "") or "")

    def is_read_at(self, fidelity: str) -> bool:
        """Whether this node was read at fidelity. A rule of one fidelity opens with it and leaves every other node
        out (``if not node.is_read_at("code"): return []``), since a rule of the code fidelity has nothing to judge on
        a class with no bodies. A node no reading recorded a fidelity for is read at none."""
        return self.fidelity_read_at == fidelity

    @property
    def failed_rules(self) -> list[str]:
        return self.rules.failed_slugs

    def place(self, location: Location) -> None:
        """Put this node at the lines location names, in its file under its practice's source root. A node its
        practice's reader found by a nearby line, such as a story's step, moves onto the lines that declare it."""
        self.source = Source.from_root(self.practice.reading.in_graph.source_root, location)

class NodeTree:
    """One node's place in its practice's explorer tree, which the node makes once and keeps (``node.tree``): it puts
    the node under its parent and the nodes its edges lead to under it, takes it out again for a rebuild, and writes
    the node's entry with the entries below it. The node keeps its ``parent`` and ``children``; this part keeps whether
    the node's own children are placed yet."""

    def __init__(self, node: Node) -> None:
        self._node = node
        self._populated = False

    def populate(self, parent: Node | None = None) -> None:
        """Put the node under parent in the explorer tree, then each node its edges lead to under it, depth first, in
        the order its edges sit. The walk keeps its own stack: a chain of edges, such as operations each invoking the
        next, runs deeper than Python's call stack would let a node populating its children call itself."""
        pending: list[Iterator[tuple[Node, Node | None]]] = [iter([(self._node, parent)])]
        while pending:
            step = next(pending[-1], None)
            if step is None:
                pending.pop()
                continue
            node, holder = step
            if node.tree._placed_under(holder):
                pending.append(node.tree._placements())

    def leave(self) -> None:
        """Take the node out of the explorer tree, so the next populate places it again from its practice's edges."""
        self._node.children = []
        self._node.parent = None
        self._populated = False

    def rebuild(self) -> None:
        """Rebuild the explorer tree under the node, its practice's root, from its practice's edges after late-bound
        nodes or overlays: every node of the practice leaves the tree, then the node places them again."""
        for node in [self._node, *self._node.practice.reading.in_graph.nodes()]:
            node.tree.leave()
        self.populate()

    def serialize(self, seen: set[str] | None = None, via: Node | None = None, stack: set[str] | None = None) -> ExplorerEntry:
        """Write the node's full child list once, on its home parent.

        A relationship copy is empty. A node already on the path is a stub, so a call back to this step stops.
        """
        node = self._node
        seen = set() if seen is None else seen
        stack = set() if stack is None else stack
        if node.node_id in stack:
            return ExplorerEntry(node)
        first_home = (via is None or via is node.parent) and node.node_id not in seen
        if not first_home:
            return ExplorerEntry(node, [])
        seen.add(node.node_id)
        return ExplorerEntry(node, self._written_at_home(seen, stack | {node.node_id}))

    def _placed_under(self, parent: Node | None) -> bool:
        """Join parent's children, taking parent as the node's own unless it has a better one; whether the node's own
        children are still to place, which is true only the first time."""
        node = self._node
        if parent is not None:
            parent.children.append(node)
            if node.parent is None or (self._holder(node.parent) and not self._holder(parent)):
                node.parent = parent
        if self._populated:
            return False
        self._populated = True
        return True

    def _placements(self) -> Iterator[tuple[Node, Node]]:
        """Each node an edge leads to from the node, with the node it goes under: the node for a direct edge, else the
        node named for the edge's kind, made when the first such edge is placed. Edges are placed kind by kind, but for
        the parts its practice lists in source order, which are placed in the order their file writes them. A kind no
        one filters by, the belongsTo back-edge and scopes, is no part of the explorer tree."""
        offered = self._node.practice.reading.in_graph.edge_index.types.values()
        types = sorted((edge_type for edge_type in offered if edge_type.is_offered), key=lambda edge_type: edge_type.order)
        written = self._parts_in_source_order([edge_type.kind for edge_type in types])
        for edge_type in types:
            for edge in self._edges_in_source_order(edge_type.kind):
                if not self._is_written_part(edge):
                    yield edge.child, self._node if edge.display == "direct" else self._holder_for(edge.kind)
                    continue
                # The node's parts of every kind are placed together, where the first of them comes.
                for part in written:
                    yield part.child, self._node
                written = []
        self._place_metrics()

    def _place_metrics(self) -> None:
        """Put the node's metrics, the facts a limit rule of its practice reads on it, under one child of the node
        named for them, each as an entry that says its plain name, its value and its limit. They come after the
        node's relationship kinds; a node with no metric gets no such child."""
        node = self._node
        metrics = node.practice.reading.metrics_of(node)
        if not metrics:
            return
        holder = self._holder_for(METRICS_GROUP)
        for metric in metrics:
            shown = Node(node.practice, NodeIdentity(type=METRIC_TYPE, node_id=f"{holder.node_id}:{metric.name}", name=metric.said), node.source)
            shown.parent = holder
            holder.children.append(shown)
            node.practice.reading.in_graph.hold_group(shown)

    def _parts_in_source_order(self, kinds: list[str]) -> list[Edge]:
        """The direct edges of kinds to the node's parts its practice lists in source order, in the order their file
        writes them, whatever their kind: a describe's states and observations, or a story's background and scenarios,
        read as the file has them, not kind by kind."""
        parts = [edge for kind in kinds for edge in self._node.graph.edges.from_parent(kind, self._node) if self._is_written_part(edge)]
        return sorted(parts, key=self._source_position)

    def _is_written_part(self, edge: Edge) -> bool:
        return edge.display == "direct" and self._follows_source(edge)

    def _holder_for(self, kind: str) -> Node:
        """The child named for kind that grouped and relationship edges of that kind sit under, made the first time."""
        node = self._node
        holder = self._child_named(kind)
        if holder is None:
            holder = Node(node.practice, NodeIdentity(type=kind, node_id=f"{node.practice.key}:{kind}:{node.node_id}", name=kind), node.source)
            holder.parent = node
            node.children.append(holder)
            node.practice.reading.in_graph.hold_group(holder)
        return holder

    def _edges_in_source_order(self, kind: str) -> list[Edge]:
        matched = self._node.graph.edges.from_parent(kind, self._node)
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
        return next((child for child in self._node.children if child.name == name), None)

    def _written_at_home(self, seen: set[str], path: set[str]) -> list[ExplorerEntry]:
        """The entries the node writes under it at its home place: each child, then its rules when the filter shows
        them."""
        node = self._node
        written = [child.tree.serialize(seen, node, path) for child in node.children]
        category = self._rule_category()
        if category is not None:
            written.append(category)
        return written

    def _rule_category(self) -> GraphRulesCollection | None:
        """The rules that apply to the node, as one child of it in the explorer tree; none when the filter shows none."""
        node = self._node
        if node.type == node.name or node.type in ("Practice", METRIC_TYPE):
            return None
        return node.rules if node.rules.shown else None


class Inventory:
    """Every open practice as the explorer's inventory shows it, with the pattern overlays applied and those available,
    read from the graph."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    @property
    @data_field
    def practices(self) -> dict[str, PracticeInventory]:
        return {key: PracticeInventory(practice) for key, practice in self._graph.practices.opened.items()}

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

    @property
    @data_field
    def message(self) -> str:
        applied = self._graph.overlays
        label = ", ".join(Path(item).name for item in applied) if applied else "none"
        return f"Applied pattern overlays: {label}."


@hosted_only
class GraphExplorer:
    """The explorer's queries on the graph, published as the graph's own tools under the toolset name ``graph``: mixed
    into *Graph*, whose practices, nodes, and pattern overlays it reads. Each query takes the filter its call asks for
    (a *FilterRequest*) and makes a *Filter* for it, so no filter stays chosen on the server between calls."""

    practices: GraphPractices
    applied_patterns: PatternOverlays
    node: Callable[[str], "Node | None"]

    @mcp
    @agent_tool
    def practice_names(self) -> list[str]:
        """Return the name of every practice the graph can load, in the order the approach walks them."""
        return list(self.practices.held)

    @mcp
    @agent_tool
    def inventory(self) -> Inventory:
        """Return each loaded practice's node and edge counts, node types, and rules, with the overlays applied and those available; explorer_trees answers the trees."""
        return Inventory(self)

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
    def filter_choices(self, practices: list[str], node_types: list[str], practices_before: list[str] | None = None) -> FilterChoices:
        """Return the node types a filter offers and those it chooses, with the relationships and rules of the chosen
        ones (of every offered one when none is chosen), once practices and node types are chosen. practices_before
        names the practices chosen before a change of practice: then node_types are those chosen before, the ones the
        new practices still hold stay chosen, and every node type of each practice added is chosen."""
        return FilterChoices(self, practices, node_types, practices_before)

    @mcp
    @agent_tool
    def source(self, node_id: str) -> NodeSource | None:
        """Return the source of the node node_id: its file, text, and lines, with every class, operation, and property the loaded graph holds, so calls in it can be opened in place. None for an id with no source, such as a rule's row."""
        node = self.node(node_id)
        if node is None:
            return None
        return NodeSource(node, members=self.source_members())

    @mcp
    @agent_tool
    def correction_prompt(self, node_id: str, rule: str) -> str:
        """Return what Correct on the Graph app's banner sends the chat about rule broken on the node node_id: how to fix it test first, the node, its file and lines, the rule, the code, and what is wrong. Empty when the node does not break rule, or the graph holds no such node."""
        node = self.node(node_id)
        broken = node.rules.entries.get(rule) if node is not None else None
        return broken.correction.prompt if broken is not None and broken.is_failing else ""

    def fix_prompt(self, filter: FilterRequest | None = None, node_id: str = "") -> str:
        """What Fix rule and Fix all send the chat: one correction for each rule broken on each node the filter keeps,
        with only violations kept, and of the node node_id alone when one is named, as Fix this one on a rule of it
        sends. Empty when the filter keeps no broken rule."""
        wanted = Filter(self, {**(filter or {}), "violations": True})
        roots = (practice.reading.in_graph.root for practice in self.practices.opened.values())
        kept = (self.node(found.node_id) for found in wanted.collect(roots) if not node_id or found.node_id == node_id)
        return ViolationCorrections([rule.correction for node in kept if node is not None for rule in wanted.failing_rules(node)]).prompt

    def source_members(self) -> list[NodeSource]:
        """Every class, operation, and property the open practices hold, each with the class it belongs to."""
        declared = list(self.practices.opened.values())
        classes = {node_type for practice in declared for node_type in practice.reading.class_types}
        members = {node_type for practice in declared for node_type in practice.reading.member_types}
        found = (node for practice in declared for node in practice.reading.in_graph.nodes() if node.type in classes | members)
        return [NodeSource(node, owner="" if node.type in classes else str(node.get_fact("owner", "") or "")) for node in found]

    @mcp
    @agent_tool
    @skill(name="read-graph")
    def return_nodes(self, filter: FilterRequest | None = None) -> list[FilteredNode]:
        """Return matching graph nodes as JSON, with ancestors, children, and relationships.

        filter keys: practice(s), type(s), name, rules, relationships;
        violations: true returns only failing nodes with only their failing rule rows;
        paths: source path prefixes (relative to the folder, e.g. src/orders) a node must sit under.
        """
        roots = (practice.reading.in_graph.root for practice in self.practices.opened.values())
        return Filter(self, filter).collect(roots)

    @mcp
    @agent_tool
    def explorer_trees(self, filter: FilterRequest | None = None) -> list[ExplorerEntry]:
        """Return the explorer tree of each practice the filter names, or of every loaded practice when it names none, keeping each practice's root, the nodes the filter matches with their rules, and the nodes on the way to them. Each root comes with the entries below it, closed: each keeps its rules and says how many entries below it were left out (children_left_out), which explorer_branch answers. filter takes the keys return_nodes takes."""
        wanted = Filter(self, filter)
        opened = self.practices.opened
        named = [opened[key] for key in wanted.practices if key in opened] if wanted.practices else list(opened.values())
        return [tree.opened() for practice in named if (tree := practice.reading.in_graph.root.tree.serialize().kept_by(wanted)) is not None]

    @mcp
    @agent_tool
    def explorer_branch(self, node_id: str, filter: FilterRequest | None = None) -> ExplorerEntry | None:
        """Return the node node_id's explorer entry as the filter keeps it, with the entries below it, closed as explorer_trees closes them; None for an id the graph no longer holds. filter takes the keys return_nodes takes, the same filter the tree was read with."""
        node = self.node(node_id)
        if node is None:
            return None
        kept = node.tree.serialize(via=node.parent).kept_by(Filter(self, filter))
        return kept.opened() if kept is not None else ExplorerEntry(node)


class PracticeNodes:
    """One practice's part of the graph that holds it: the root node its explorer tree starts from, the folder its
    source is read from, and its nodes, which it holds itself by id, by type, and the relationship groups its explorer
    tree puts edges under. The graph makes one for each practice it holds, keeps it, and gives it to the practice
    (``practice.reading.in_graph``), so code holding a practice asks it for its nodes
    (``stories.reading.in_graph.nodes("Story")``) instead of handing the practice back to the graph on every call. It holds
    four parts of its own, each made once: its edges, indexed by kind (``edge_index``), the run of its graph rules
    (``rule_run``), what a load does to the nodes it holds (``loading``), and what it takes back from saved records
    (``restore``). Each change to the nodes it holds counts as a change to the graph's build."""

    def __init__(self, graph: Graph, practice: PracticeGuidance) -> None:
        self.graph = graph
        self.practice = practice
        self._source_root: Path | None = None
        self._root: Node | None = None
        self._by_id: dict[str, Node] = {}
        # The nodes by type. A type offered before any node of it is read holds none yet; the types keep the order
        # each was first offered or held, so the explorer lists them the same way in every process.
        self._by_type: dict[str, list[Node]] = {}
        # The relationship groups the explorer tree puts edges under, such as an operation's invokes; no node of the
        # practice, so the practice's nodes and rules leave them out, but an explorer opens them by id.
        self._groups: dict[str, Node] = {}
        self.edge_index = EdgeIndex(graph.build.changed)
        self.rule_run = PracticeRuleRun(self)
        self.loading = PracticeLoading(self)
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

    @property
    def is_open(self) -> bool:
        """Whether the practice is open in the graph, holding its root node."""
        return self._root is not None

    def hold_root(self, root: Node) -> None:
        """Keep root as the practice's root, held by its id but by no type, so no list of nodes holds it."""
        self._root = root
        self._by_id[root.node_id] = root

    ## nodes

    def nodes(self, type: str | None = None) -> list[Node]:
        """Every node the practice holds, or only those of type."""
        if type is not None:
            return list(self._by_type.get(type, []))
        return [node for group in self._by_type.values() for node in group]

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
        files = self.loading.from_root(path.resolve() for path in edited)
        return [node for node in found if node.source.file in files]

    def node(self, node_id: str) -> Node | None:
        """The practice's node called node_id, or the relationship group called node_id one of its nodes holds; none
        when it holds neither."""
        return self._by_id.get(node_id) or self._groups.get(node_id)

    def hold_group(self, group: Node) -> None:
        """Hold group, a relationship group one of the practice's nodes made, so an explorer opens it by its id."""
        self._groups[group.node_id] = group

    def holds(self, node_id: str) -> bool:
        """Whether the practice already holds a node called node_id."""
        return self._by_id.get(node_id) is not None

    @property
    def node_types(self) -> list[str]:
        """The node types the graph offers for the practice, those the practice offers and those it holds a node of, in
        the order each was first offered or held."""
        return list(self._by_type)

    def offer_node_types(self, types: Iterable[str]) -> None:
        """Offer these node types in the explorer's filter, before any node of them is read."""
        for node_type in types:
            self._by_type.setdefault(node_type, [])

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
        node = Node(self.practice, NodeIdentity(type=type, node_id=node_id, name=name or Path(relative).stem), source)
        return self.add(node, node_id, Location(source.file, source.start_line, source.end_line))

    def hold(self, node: Node) -> None:
        """Keep node, one of this practice's, by its type and its id."""
        self.graph.build.changed()
        self._by_type.setdefault(node.type, []).append(node)
        self._by_id[node.node_id] = node

    def release(self, node: Node) -> None:
        """Let go of node when the practice holds it, so another practice can take it; nothing when another node holds
        its id."""
        if self._by_id.get(node.node_id) is not node:
            return
        self.graph.build.changed()
        del self._by_id[node.node_id]
        bucket = self._by_type.get(node.type, [])
        if node in bucket:
            bucket.remove(node)

    def drop(self, dropped: set[int]) -> set[int]:
        """Drop the nodes whose ``id`` is in dropped; answer dropped."""
        if dropped:
            self.graph.build.changed()
            self._by_id = {node_id: node for node_id, node in self._by_id.items() if id(node) not in dropped}
            self._by_type = {kind: [node for node in group if id(node) not in dropped] for kind, group in self._by_type.items()}
        return dropped

    def forget_all(self) -> None:
        """Forget the root, every node, and every relationship group."""
        self.graph.build.changed()
        self._root = None
        self._by_id.clear()
        self._by_type.clear()
        self._groups.clear()

    def put_in_source_order(self) -> None:
        """Hold the nodes of each type in the order their files and lines give them. A refresh holds the nodes it read
        again after those it kept, so without this a rule that reports the first of two nodes, such as the original of
        two duplicate bodies, would report another node after a refresh than after a fresh build."""
        for kind, group in self._by_type.items():
            self._by_type[kind] = sorted(group, key=self._where_it_sits)

    def _where_it_sits(self, node: Node) -> tuple:
        """Where node sits: its file, its lines, then its id, which tells apart two nodes on one line."""
        return (node.source.file or "", node.source.start_line, node.source.end_line, node.node_id)

    def _release_from_its_practice(self, node: Node) -> None:
        """Take node out of the practice that holds it, in whichever graph that is, so this practice can take it."""
        practice = getattr(node, "practice", None)
        part = practice.reading.in_graph if practice is not None else None
        if isinstance(part, PracticeNodes):
            part.release(node)

    def unused_node_id(self, type: str, name: str) -> str:
        """``practice:type:name``, numbered from 2 when the practice already holds a node of that id."""
        base = f"{self.practice.key}:{type}:{name}"
        found, index = base, 2
        while found in self._by_id:
            found = f"{base}:{index}"
            index += 1
        return found


class PracticeLoading:
    """What a load, a refresh, or a restore does to the nodes one practice holds, which its part of the graph makes
    once and keeps (``practice.reading.in_graph.loading``): open the practice on a root with its root node alone, close
    it, and drop the nodes read from files read again."""

    def __init__(self, part: PracticeNodes) -> None:
        self._part = part

    def open(self, root: Path | None) -> None:
        """Read the practice from root, starting from its root node alone."""
        part = self._part
        part.graph.build.changed()
        if root is not None:
            part.source_root_path = root
        if not part.is_open:
            key = part.practice.key
            part.hold_root(Node(part.practice, NodeIdentity(type="Practice", node_id=f"{key}:Practice:.:{key}", name=key), Source(".", 0, 0)))

    def close(self) -> None:
        """Forget every node and edge, so a load reads them again from nothing."""
        self._part.forget_all()
        self._part.edge_index.clear()

    def forget_files(self, files: Iterable[Path]) -> set[int]:
        """Drop every node read from one of files, and every node read from a file under one of them that is no longer
        on disk, so a refresh reads those files again from nothing and holds exactly what is under a refreshed folder
        now: a file deleted or moved out of it leaves no node behind. Answer the ``id`` of each node dropped, whose
        edges every practice then drops."""
        read_from = self.from_root(files)
        root = self._root
        return self._part.drop({
            id(node)
            for node in self._part.nodes()
            if node.source.file in read_from or (root is not None and self._under_any(node.source.file or "", read_from) and not (root / node.source.file).is_file())
        })

    def _under_any(self, file: str, folders: set[str]) -> bool:
        """Whether file, a path from the practice's source root, lies under one of folders, given from the same root."""
        return any(folder == "." or file.startswith(f"{folder}/") for folder in folders)

    def from_root(self, files: Iterable[Path]) -> set[str]:
        """Each of files under the practice's source root, as a path from that root, the way its nodes name their file."""
        root = self._root
        if root is None:
            return set()
        return {file.relative_to(root).as_posix() for file in files if file == root or root in file.parents}

    @property
    def _root(self) -> Path | None:
        """The practice's source root, which its nodes name their files from; the loaded folder when it has none."""
        held_root = self._part.source_root_path
        return held_root.resolve() if held_root is not None else self._part.graph.scope.folder


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
    def checks(self) -> GraphChecks:
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
        context = RuleCheckContext(practice)
        for index, check in enumerate(checks, start=1):
            report_progress(f"{practice.key} · rule {check.slug} · {index}/{len(checks)}")
            for finding in check.check_practice(context):
                finding.node.rules.record(check, finding)
        self._check_each_node(context)

    def renew(self) -> None:
        """Forget every node's rules, its root's among them, so each is made fresh when next read and the next check
        finds each violation again."""
        self._part.graph.build.changed()
        for node in [self._part.root, *self._part.nodes()]:
            node.forget_rules()

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
                for finding in rule.check(context):
                    rule.record(finding)

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
        part.drop({id(node) for node in part.nodes() if node.node_id in dropped})
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
            node = Node(part.practice, kept.record, Source.from_root(part.source_root, kept.location))
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
                graph.edges.record(kept.type, parent, child, kept.facts)
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

    def relate(self, kind: str, parent: Node, child: Node, facts: EdgeFacts | None = None) -> None:
        """Record a relationship edge of kind from parent to child: parent refers to child, which stays where it is. The
        edge keeps facts about the relationship, beside those it kept when it was recorded before."""
        self.record(EdgeType.from_kind(kind, "relationship"), parent, child, facts)

    def group(self, kind: str, parent: Node, child: Node) -> None:
        """Record a grouped edge of kind from parent to child, which the tree shows under a child of parent named for
        kind."""
        self.record(EdgeType.from_kind(kind, "grouped"), parent, child)

    def record(self, edge_type: EdgeType, parent: Node, child: Node, facts: EdgeFacts | None = None) -> None:
        """Record an edge of edge_type from parent to child on the parent's practice, once, keeping facts on it."""
        self._graph.practices.part_of(parent.practice).edge_index.record(edge_type, parent, child, facts)

    def from_parent(self, kind: str, parent: Node) -> list[Edge]:
        """Edges of one kind leaving parent, in recorded order."""
        return self._graph.practices.part_of(parent.practice).edge_index.from_parent(kind, parent)

    def direct_parent(self, child: Node) -> Node | None:
        """The node a direct edge of the child's practice hangs the child under; available before populate sets
        ``parent``."""
        return self._graph.practices.part_of(child.practice).edge_index.direct_parent(child)


@language_adapter(language="typescript")
@agent_toolset
class Graph(GraphExplorer):
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
    model objects (``schema_edges``), and its reads (``reads``). Its MCP operations are the one entry: its own loads and
    saves, and the explorer's queries, which *GraphExplorer* publishes under the same toolset name. The call a tool
    answers stops here: a tool says whether its build runs apart, in a worker process, as it does for a call the cdd
    server answers for a chat."""

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
        self.reads = GraphReads(self)

    def for_call(self, call: ToolCall) -> Graph:
        """The graph call works on: its session's, which the server holds between calls; this graph for a call that
        works in no session."""
        session = call.session
        graph = session.graph if session is not None else None
        return graph if isinstance(graph, Graph) else self

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

    def node(self, node_id: str) -> Node | None:
        """The node called node_id, in whichever practice holds it; none when no practice does."""
        found = (practice.reading.in_graph.node(node_id) for practice in self.practices.held.values())
        return next((node for node in found if node is not None), None)

    ## loading and refreshing: each is one of the graph's reads (``reads``)

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
        with self.reads.changing:
            self.scope = LoadScope(Path(database or folder).resolve())
            self.practices.choose({self.practices.named(key): (Path(folder) / root).resolve() for key, root in practices.items()})
            self.overlays = list(overlays or [])
            return self.reads.load(force, _builds_apart(call))

    @long_call
    @mcp
    @agent_tool
    def load_practice_roots(self, call: ToolCall | None = None) -> GraphLoaded:
        """Open each practice this graph holds on the folder its session names for it (its session root), with the
        overlays the graph applies, and build: the Graph app's whole load, with no folder or practice named by the
        caller. A session's graph holds only the practices its session works on, so a practice turned off is never
        read. A practice no session works in has no root, and one whose folder is not written yet has nothing to read:
        both are left out."""
        return self.reads.practice_roots(_builds_apart(call))

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
        with self.reads.changing:
            root = Path(folder).resolve()
            self.scope = LoadScope.of_paths(root, files)
            self.practices.choose({self.practices.named(key): root for key in practices})
            self.overlays = list(overlays or [])
            return self.reads.edited_files(_builds_apart(call))

    @mcp
    @agent_tool
    def refresh(self, paths: list[str], call: ToolCall | None = None) -> GraphLoaded:
        """Read again exactly the files at paths, the files an action just wrote, into the graph held in memory: drop
        every node read from them, read them as they are now, link them to the other practices' nodes, and run the
        rules again. Every other node stays as it was; nothing watches the files, so a written file is in the graph
        only once refresh is called with it.
        paths: the files written, absolute or from the graph's folder (the session's root); a folder stands for the
        source files under it. A file that is gone is dropped from the graph."""
        return self.reads.refresh(paths, _builds_apart(call))

    @mcp
    @agent_tool
    def save_json(self) -> GraphSaved:
        """Write the serialized graph into the loaded folder's ``.context``.

        Practices already on disk that are not part of this load stay in the file.
        """
        return GraphSaved("" if self.scope.folder is None else str(self.saved_file.save(SavedGraph.from_graph(self))))

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
        return AppliedOverlays(self.reads.apply_overlays(overlays, _builds_apart(call)))


def _builds_apart(call: ToolCall | None) -> bool:
    """Whether a build call asks for runs apart, in a worker process: it does for a call the cdd server answers for a
    chat, so the server keeps answering every other chat while it runs."""
    return call is not None and call.request.answers_a_chat
