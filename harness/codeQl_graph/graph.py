"""CodeQLGraph. One toolset: databases, working copies, and practice graphs."""

from __future__ import annotations

import errno
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.agent_tools import agent_tool, agent_toolset
from harness.mcp.mcp_server import mcp

Display = str
Tuple = list[str]
_RUN_QUERIES_FLAGS = ("--threads=0", "--quiet", "--ram=8192")


def query_pack(practice: str, language: str) -> Path:
    return _REPO / "practices" / practice / "model" / language / "codeql"


def windows_path(path: Path) -> str:
    """Absolute path. On Windows the \\\\?\\ form addresses CodeQL cache names past MAX_PATH."""
    text = os.path.abspath(path)
    if os.name != "nt" or text.startswith("\\\\?\\"):
        return text
    if text.startswith("\\\\"):
        return "\\\\?\\UNC\\" + text[2:]
    return "\\\\?\\" + text


def _make_writable(function, path, _exc) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def _cache_root(path: Path) -> Path | None:
    parts = Path(str(path).removeprefix("\\\\?\\")).parts
    for index, part in enumerate(parts):
        if part == "cache" and index >= 1 and parts[index - 1] == "default":
            return Path(*parts[: index + 1])
    return None


def missing_cache(error: BaseException) -> Path | None:
    """The CodeQL cache directory named in a Windows path-not-found error."""
    if not isinstance(error, OSError):
        return None
    unreachable = getattr(error, "winerror", None) == 3 or error.errno == errno.ENOENT
    if not unreachable or not error.filename:
        return None
    return _cache_root(Path(error.filename))


def _remove_tree_once(path: Path, *, ignore_errors: bool = False) -> None:
    target = windows_path(path)
    if not os.path.exists(target):
        return
    if not os.path.isdir(target):
        os.remove(target)
        return
    shutil.rmtree(target, ignore_errors=ignore_errors, onexc=_make_writable)


def remove_tree(path: Path, *, ignore_errors: bool = False) -> None:
    """Delete a database directory. A path Windows cannot see drops the CodeQL cache and retries."""
    try:
        _remove_tree_once(path, ignore_errors=ignore_errors)
    except OSError as error:
        cache = missing_cache(error)
        if cache is None:
            if ignore_errors:
                return
            raise
        _remove_tree_once(cache)
        _remove_tree_once(path, ignore_errors=ignore_errors)


def copy_tree(source: Path, destination: Path) -> None:
    remove_tree(destination)
    try:
        shutil.copytree(windows_path(source), windows_path(destination))
    except OSError as error:
        cache = missing_cache(error)
        if cache is None:
            raise
        _remove_tree_once(cache)
        remove_tree(destination)
        shutil.copytree(windows_path(source), windows_path(destination))


class QueryFailure(Exception):
    def __init__(self, query: str, detail: str) -> None:
        super().__init__(f"{query}\n{detail}")
        self.query = query
        self.detail = detail


class EdgeType:
    def __init__(self, kind: str, order: int, display: Display) -> None:
        self.kind = kind
        self.order = order
        self.display = display


class Edge:
    def __init__(self, kind: str, order: int, display: Display, parent: CodeQLNode, child: CodeQLNode) -> None:
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


class SourceFold:
    """A Monaco fold. start and end are 1-based lines. kind is call, class, or block."""

    def __init__(self, start: int, end: int, kind: str, glyph: int = 0, member: bool = False, listed: bool = False) -> None:
        self.start = start
        self.end = end
        self.kind = kind
        self.glyph = glyph or start
        self.member = member
        self.listed = listed


class Source:
    """Source text Monaco displays: file, startLine, endLine, text, and folds."""

    _SKIP = {"if", "for", "while", "function", "def", "switch", "catch", "constructor"}
    _SKIP_RECEIVER = {"console", "Math", "JSON", "Object", "Promise", "Array", "expect", "vi"}
    _EXPAND_DEPTH = 5
    _CLASS_DECL = re.compile(r"^\s*(export\s+)?(abstract\s+)?class\s+")

    def __init__(self, path: str, line_start: int, line_end: int, root: str = "") -> None:
        self.file = path
        self.start_line = line_start
        self.end_line = line_end
        self.root = root
        self.calls: list[Call] = []
        self.folds: list[SourceFold] = []
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
            self.load_folds()
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

    def load_folds(self) -> None:
        self.folds = [
            SourceFold(call.line, call.line, "call" if "." in call.operation else "class")
            for call in self.calls
        ]
        self.folds.extend(self._block_folds(self._text or ""))

    def expand(self, nodes: list[CodeQLNode]) -> None:
        """Inline called operations and the classes they name. Folds cover the call, the class, and each block."""
        text, folds = self._inline(self.text, nodes, 1, set())
        self._text = text
        self.folds = folds

    def _inline(self, text: str, nodes: list[CodeQLNode], depth: int, stack: set[str]) -> tuple[str, list[SourceFold]]:
        operations = {node.name: node for node in nodes if node.type == "Operation"}
        classes = {node.name: node for node in nodes if node.type == "OoadClass"}
        output: list[str] = []
        folds: list[SourceFold] = []
        frames: list[tuple[int, int, bool]] = []
        brace = 0
        for line in text.splitlines() or [""]:
            output.append(line)
            brace, frames = self._open_frames(line, brace, len(output), frames)
            if depth < self._EXPAND_DEPTH:
                self._inline_line(line, output, folds, operations, classes, nodes, depth, stack)
            brace, frames, folds = self._close_frames(brace, frames, folds, len(output))
        return "\n".join(output), folds

    def _open_frames(self, line: str, brace: int, source_line: int, frames: list[tuple[int, int, bool]]) -> tuple[int, list[tuple[int, int, bool]]]:
        before = brace
        brace = self._brace_depth(line, brace)
        if self._CLASS_DECL.match(line):
            return brace, frames
        member = self._member_head(line)
        opened = before
        while opened < brace:
            opened += 1
            frames.append((source_line, opened, member and opened == before + 1))
        return brace, frames

    def _close_frames(self, brace: int, frames: list[tuple[int, int, bool]], folds: list[SourceFold], length: int) -> tuple[int, list[tuple[int, int, bool]], list[SourceFold]]:
        while frames and brace < frames[-1][1]:
            at, _, member = frames.pop()
            if length > at:
                folds.append(SourceFold(at + 1, length, "block", glyph=at, member=member))
        return brace, frames, folds

    def _inline_line(self, line: str, output: list[str], folds: list[SourceFold], operations: dict[str, CodeQLNode], classes: dict[str, CodeQLNode], nodes: list[CodeQLNode], depth: int, stack: set[str]) -> None:
        call_line = len(output)
        for name in self._called_names(line):
            callee = operations.get(name)
            if callee is None or callee.node_id in stack:
                continue
            self._append_operation(output, folds, callee, line, nodes, depth, stack, classes)
        if len(output) > call_line:
            folds.append(SourceFold(call_line, len(output), "call"))

    def _append_operation(self, output: list[str], folds: list[SourceFold], callee: CodeQLNode, line: str, nodes: list[CodeQLNode], depth: int, stack: set[str], classes: dict[str, CodeQLNode]) -> None:
        pad = f"{self._indent(line)}    "
        output.append(f"{pad}{callee.name}")
        nested_text, nested_folds = self._inline(callee.source.text, nodes, depth + 1, stack | {callee.node_id})
        body_start = len(output)
        for nested_line in nested_text.splitlines():
            output.append(f"{pad}    {nested_line}" if nested_line else f"{pad}    ")
        if len(output) > body_start:
            folds.append(SourceFold(body_start, len(output), "call"))
        for fold in nested_folds:
            folds.append(SourceFold(body_start + fold.start, body_start + fold.end, fold.kind, member=fold.member, listed=fold.listed))
        for named in self._mentioned_classes(callee.source.text, classes, stack):
            self._append_class(output, folds, named, pad)

    def _append_class(self, output: list[str], folds: list[SourceFold], node: CodeQLNode, pad: str) -> None:
        output.append(f"{pad}{node.name}")
        start = len(output)
        class_pad = f"{pad}    "
        for class_line in node.source.text.splitlines():
            output.append(f"{class_pad}{class_line}" if class_line else class_pad)
        if len(output) > start:
            folds.append(SourceFold(start, len(output), "class", listed=True))

    def _block_folds(self, text: str) -> list[SourceFold]:
        folds: list[SourceFold] = []
        frames: list[tuple[int, int, bool]] = []
        brace = 0
        for index, line in enumerate(text.splitlines(), start=1):
            brace, frames = self._open_frames(line, brace, index, frames)
            brace, frames, folds = self._close_frames(brace, frames, folds, index)
        return folds

    def _brace_depth(self, line: str, depth: int) -> int:
        quote = ""
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
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            index += 1
        return depth

    def _member_head(self, line: str) -> bool:
        trimmed = line.strip()
        if re.match(r"^(if|for|while|switch|catch|else|try|do|return|throw)\b", trimmed):
            return False
        return "{" in trimmed

    def _indent(self, line: str) -> str:
        return line[: len(line) - len(line.lstrip())]

    def _called_names(self, line: str) -> list[str]:
        names = []
        for found in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?)\s*\(", line):
            name = found.group(1).rsplit(".", 1)[-1]
            receiver = found.group(1).split(".", 1)[0] if "." in found.group(1) else ""
            if name in self._SKIP or receiver in self._SKIP_RECEIVER or name in names:
                continue
            names.append(name)
        return names

    def _mentioned_classes(self, text: str, classes: dict[str, CodeQLNode], stack: set[str]) -> list[CodeQLNode]:
        found = []
        for name, node in classes.items():
            if node.node_id in stack or node in found:
                continue
            if re.search(rf"\b{name}\b", text):
                found.append(node)
        return found

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

    def _file_lines(self) -> list[str]:
        full = self._full_path()
        if full is None:
            return []
        return full.read_text(encoding="utf-8").splitlines()

    def _full_path(self) -> Path | None:
        if not self.root or not self.file or self.file == ".":
            return None
        full = Path(self.root, self.file)
        return full if full.is_file() else None

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


class RuleResult:
    """A rule query row attached to the node it checked."""

    def __init__(self, rule: str, violation: str) -> None:
        self.rule = rule
        self.violation = violation


class CodeQLFilter:
    """Narrows a loaded graph. A practice choice reads that practice's node queries, and a node-type choice sets the relationships and rules."""

    def __init__(self, graph: CodeQLGraph) -> None:
        self.graph = graph
        self.practices: list[str] = []
        self.node_types: list[str] = []
        self.relationships: list[str] = []
        self.rules: list[str] = []
        self.violations = False
        self.relationships_selected = False

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
        for practice in self._scope():
            for query in self.graph.query_files(practice, "nodes"):
                semantic = self._semantic_type(Path(query).read_text(encoding="utf-8"))
                if semantic and semantic not in found:
                    found.append(semantic)
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
        found: list[str] = []
        for name in self._scope():
            practice = self.graph.practices.get(name)
            if practice is None:
                continue
            for type_name, nodes in practice.nodes.items():
                if type_name not in types:
                    continue
                for node in nodes:
                    for hit in node.rules:
                        if hit.rule not in found:
                            found.append(hit.rule)
        return found

    def _fill_from_nodes(self) -> None:
        self.relationships = self._available_relationships()
        self.rules = self._available_rules()

    def _semantic_type(self, text: str) -> str:
        stripped = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
        stripped = re.sub(r"//.*?$", " ", stripped, flags=re.M)
        columns = self._select_columns(stripped)
        if len(columns) < 3:
            return ""
        match = re.fullmatch(r'"([^"]*)"', columns[2].strip())
        return match.group(1) if match else ""

    def _select_columns(self, text: str) -> list[str]:
        match = re.search(r"\bselect\b", text)
        if match is None:
            return []
        columns: list[str] = []
        current: list[str] = []
        depth = 0
        quote = ""
        for char in text[match.end() :]:
            if quote:
                current.append(char)
                if char == quote:
                    quote = ""
                continue
            if char in "\"'":
                quote = char
                current.append(char)
                continue
            if char == "(":
                depth += 1
            elif char == ")" and depth:
                depth -= 1
            elif char == "," and depth == 0:
                columns.append("".join(current).strip())
                current = []
                continue
            current.append(char)
        if current:
            columns.append("".join(current).strip())
        return columns


class CodeQLNode:
    """children is the list populate writes on this node. Direct edges are the children. Grouped and relationship edges sit under one child named for the kind."""

    def __init__(self, practice: CodeQLPracticeGraph, type: str, node_id: str, name: str, source: Source) -> None:
        self.practice = practice
        self.type = type
        self.node_id = node_id
        self.name = name
        self.source = source
        self.stage = ""
        self.children: list[CodeQLNode] = []
        self.parent: CodeQLNode | None = None
        self.rules: list[RuleResult] = []
        self._populated = False

    @property
    def failed_rules(self) -> list[str]:
        found: list[str] = []
        for hit in self.rules:
            if hit.rule not in found:
                found.append(hit.rule)
        return found

    @property
    def passing_rules(self) -> list[str]:
        """Rules that apply to this node and did not fail."""
        failed = set(self.failed_rules)
        return [rule for rule in self.practice.rules_for(self.type) if rule not in failed]

    @staticmethod
    def fact(row: Tuple) -> dict | None:
        node_id, name, semantic_type, practice, file, line, end_line = (row + [""] * 7)[:7]
        if not node_id or not semantic_type:
            return None
        return {
            "node_id": node_id,
            "name": name,
            "semantic_type": semantic_type,
            "practice": practice,
            "file": file,
            "line": int(line or 1),
            "end_line": int(end_line or 1),
            "stage": CodeQLNode._stage_cell(row),
        }

    @classmethod
    def from_fact(cls, practice: CodeQLPracticeGraph, row: dict) -> CodeQLNode:
        node = CodeQLNode(
            practice,
            row["semantic_type"],
            row["node_id"],
            row["name"],
            Source(row["file"], row["line"], row["end_line"], practice.source_root),
        )
        node.stage = str(row.get("stage") or "")
        if row["semantic_type"] == "Step":
            node.source.align_to_label(row["name"])
        return node

    @staticmethod
    def _stage_cell(row: Tuple) -> str:
        for cell in row[7:]:
            if cell in {"discovery", "specification", "implementation"}:
                return str(cell)
        return ""

    def populate(self, parent: CodeQLNode | None = None) -> None:
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
        matched = [edge for edge in self.practice.edges.get(kind, []) if edge.parent is self]
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

    def _holder(self, node: CodeQLNode) -> bool:
        return node.type == node.name

    def _child_named(self, name: str) -> CodeQLNode | None:
        for child in self.children:
            if child.name == name:
                return child
        return None

    def serialize(self, seen: set[str] | None = None, via: CodeQLNode | None = None, stack: set[str] | None = None) -> dict:
        """Write the full child list once, on the home parent.

        Every copy still lists invokes, observes, and demonstrates. A node already on the path is a stub, so a call back to this step stops.
        """
        seen = set() if seen is None else seen
        stack = set() if stack is None else stack
        if self.node_id in stack:
            return {"type": self.type, "name": self.name, "node_id": self.node_id, "children": []}
        home = via is None or via is self.parent
        first_home = home and self.node_id not in seen
        if first_home:
            seen.add(self.node_id)
            children = self.children
        else:
            children = [child for child in self.children if child.type == child.name and child.name in {"invokes", "observes", "demonstrates"}]
        path = stack | {self.node_id}
        return {
            "type": self.type,
            "name": self.name,
            "node_id": self.node_id,
            "children": [child.serialize(seen, self, path) for child in children],
        }

    def _new_kind_node(self, kind: str) -> CodeQLNode:
        return CodeQLNode(self.practice, kind, f"{self.practice.name}:{kind}:{self.node_id}", kind, self.source)


class CodeQLPracticeGraph:
    """An edge is recorded only when both ends are already registered."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.nodes: dict[str, list[CodeQLNode]] = {}
        self.edges: dict[str, list[Edge]] = {}
        self.node_types: set[str] = set()
        self.edge_types: dict[str, EdgeType] = {}
        self.by_id: dict[str, CodeQLNode] = {}
        self.rules_run: list[str] = []
        self.applicable: dict[str, list[str]] = {}
        self.loaded: list[str] = []
        self.source_root = ""
        self.database = Path()
        self.graph: CodeQLGraph | None = None
        self.root_node = CodeQLNode(self, "Practice", f"{name}:Practice:.:{name}", name, Source(".", 0, 0))

    def bind_rule(self, rule: str, types: list[str]) -> None:
        current = self.applicable.setdefault(rule, [])
        for node_type in types:
            if node_type not in current:
                current.append(node_type)

    def rules_for(self, node_type: str) -> list[str]:
        return [rule for rule, types in self.applicable.items() if node_type in types]

    @property
    def edge_count(self) -> int:
        return sum(len(edges) for edges in self.edges.values())

    @property
    def edge_type_kinds(self) -> list[str]:
        ordered = sorted(self.edge_types.values(), key=lambda edge_type: edge_type.order)
        return [edge_type.kind for edge_type in ordered]

    def load_nodes(self, queries: list[str]) -> None:
        assert self.graph is not None
        rows = self.graph.run_queries(queries, self.database)
        for query in queries:
            self.apply_nodes(rows.get(query, []))

    def apply_nodes(self, tuples: list[Tuple]) -> None:
        for row in tuples:
            fact = CodeQLNode.fact(row)
            if fact is None or fact["node_id"] in self.by_id:
                continue
            self.node_types.add(fact["semantic_type"])
            node = CodeQLNode.from_fact(self, fact)
            self.nodes.setdefault(fact["semantic_type"], []).append(node)
            self.by_id[fact["node_id"]] = node

    def registered(self, node_id: str) -> CodeQLNode | None:
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

    def load_edges(self, queries: list[str]) -> None:
        assert self.graph is not None
        rows = self.graph.run_queries(queries, self.database)
        for query in queries:
            self.apply_edges(rows.get(query, []))

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

    def record(self, fact: dict, parent: CodeQLNode, child: CodeQLNode) -> None:
        list_ = self.edges.setdefault(fact["kind"], [])
        if any(edge.parent is parent and edge.child is child for edge in list_):
            return
        if fact["kind"] not in self.edge_types:
            self.edge_types[fact["kind"]] = EdgeType(fact["kind"], fact["order"], fact["display"])
        list_.append(Edge(fact["kind"], fact["order"], fact["display"], parent, child))

    def node_count(self, type: str) -> int:
        return len(self.nodes.get(type, []))

    def apply_rules(self, rule: str, tuples: list[Tuple]) -> None:
        self.rules_run.append(rule)
        for row in tuples:
            slug, node_id, violation = (row + [""] * 3)[:3]
            if not slug or not node_id or not violation:
                continue
            node = self.registered(node_id)
            if node is None:
                continue
            if any(hit.rule == slug and hit.violation == violation for hit in node.rules):
                continue
            node.rules.append(RuleResult(slug, violation))

    def nodes_for_rule(self, rule: str) -> list[CodeQLNode]:
        found = []
        for nodes in self.nodes.values():
            for node in nodes:
                if any(hit.rule == rule for hit in node.rules):
                    found.append(node)
        return found


@agent_toolset
class CodeQLGraph:
    """Read CodeQL databases into practice graphs. Databases live on the working copy."""

    def __init__(self) -> None:
        """Open an empty graph. create_database points it at a repo and its practice roots."""
        self._folder: Path | None = None
        self._practice_roots: dict[str, Path] = {}
        self._languages: dict[str, str] = {}
        self._executable = shutil.which("codeql") or "codeql"
        self.practices: dict[str, CodeQLPracticeGraph] = {}
        self.filter = CodeQLFilter(self)
        super().__init__()

    @property
    def folder(self) -> str:
        """Directory that holds the .codeql master and working-copy databases.

        This is the repo root unless a subset directory was passed.
        """
        return "" if self._folder is None else str(self._folder)

    @mcp
    @agent_tool
    def create_database(self, folder: str, practices: dict[str, str], database: str | None = None) -> str:
        """Delete each master and working copy, extract the source into a new master, and copy that master to the working copy.

        folder is the repo. Databases are stored there unless database is set.
        database stores a subset's databases so a test does not overwrite the repo database.
        practices maps each practice name to that practice's source root.
        """
        self._bind(folder, practices, database)
        self._delete_databases()
        self._ensure_masters()
        for name in self._practice_roots:
            working = self._working_copy(name)
            if not self._database_ready(working):
                self._copy_database(self._master(name), working)
        names = ", ".join(self._practice_roots)
        return f"Created databases for {names} in {self._folder}"

    @mcp
    @agent_tool
    def reload_working_copy(self) -> str:
        """Populate the graph from each working copy.

        The working copy is rebuilt only when it is missing or the practice source or CodeQL queries are newer than the stamp. Queries always read the working copy.
        """
        self._require_practices()
        stale = [name for name in self._practice_roots if not self._working_copy_current(name)]
        self._rewrite_working_copies(stale)
        self._load_all(reuse=not stale)
        for name in stale:
            self._write_stamp(name)
            self._copy_database(self._working_copy(name), self._master(name))
        if not stale:
            return "Working copies are current. Queried the working copies."
        names = ", ".join(stale)
        return f"Rebuilt working copies for {names} and queried them."

    @mcp
    @agent_tool
    def update_working_copy(self, paths: list[str]) -> str:
        """Update the working copy from these files and populate the graph from it."""
        self._require_practices()
        touched = self._practices_for_paths(paths)
        self._rewrite_working_copies(touched)
        self._load_all()
        for name in touched:
            self._write_stamp(name)
        names = ", ".join(touched) if touched else "no practices"
        return f"Updated the working copy for {names}."

    def load_working_copy(self, folder: str, practices: dict[str, str], database: str | None = None) -> str:
        """Populate the graph from query results already stored on each working copy.

        folder is the repo. database stores a subset's databases so a test does not overwrite the repo database.
        This does not create a database or write into the working copy.
        """
        self._bind(folder, practices, database)
        missing = [name for name in self._practice_roots if not self._database_ready(self._working_copy(name))]
        if missing:
            names = ", ".join(missing)
            raise QueryFailure("load_working_copy", f"No working copy for {names}.")
        self._load_all(reuse=True)
        return "Loaded the working copies."

    @mcp
    @agent_tool
    def return_nodes(self, filter: dict | None = None) -> str:
        """Return matching graph nodes as JSON, with ancestors, children, and relationships."""
        self._require_practices()
        if not self.practices:
            self._load_all()
        wanted = dict(filter or {})
        if "practice" not in wanted and "practices" not in wanted and self.filter.practices:
            wanted["practices"] = self.filter._scope()
        if "type" not in wanted and "types" not in wanted and self.filter.node_types:
            wanted["types"] = self.filter.node_types
        if self.filter.violations:
            wanted["violations"] = True
            wanted["rules"] = list(self.filter.rules)
        if self.filter.relationships_selected:
            wanted["relationships"] = list(self.filter.relationships)
        found: list[dict] = []
        seen: set[int] = set()
        for practice in self.practices.values():
            self._collect_nodes(practice.root_node, [], wanted, found, seen)
        return json.dumps(found, indent=2)

    def practice(self, name: str) -> CodeQLPracticeGraph:
        return self.practices.setdefault(name, CodeQLPracticeGraph(name))

    def query_files(self, practice: str, kind: str) -> list[str]:
        folder = query_pack(practice, self._languages[practice]) / kind
        if not folder.is_dir():
            return []
        return [str(path) for path in sorted(folder.glob("*.ql"))]

    def run_query(self, ql_path: str, database: Path) -> list[Tuple]:
        return self.run_queries([ql_path], database).get(ql_path, [])

    def run_queries(self, queries: list[str], database: Path, *, reuse: bool = False) -> dict[str, list[Tuple]]:
        """Evaluate every query in one CodeQL process. The JVM compiles the pack once.

        reuse decodes bqrs already stored on the working copy and does not write.
        """
        if not queries:
            return {}
        missing = list(queries)
        if reuse:
            missing = []
            for query in queries:
                try:
                    self._bqrs_for(database, Path(query))
                except QueryFailure:
                    missing.append(query)
            if not missing:
                return self._decode_located([(query, self._bqrs_for(database, Path(query))) for query in queries])
        self._execute_queries(missing, database)
        located = [(query, self._bqrs_for(database, Path(query))) for query in queries]
        return self._decode_located(located)

    def _execute_queries(self, queries: list[str], database: Path) -> None:
        if not queries:
            return
        paths = [str(Path(query).resolve()) for query in queries]
        run = subprocess.run(
            [
                self._executable,
                "database",
                "run-queries",
                *_RUN_QUERIES_FLAGS,
                str(database),
                "--",
                *paths,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if run.returncode != 0:
            detail = run.stderr or run.stdout or "database run-queries failed"
            raise QueryFailure("database run-queries", detail)

    def _decode_located(self, located: list[tuple[str, Path]]) -> dict[str, list[Tuple]]:
        decoded: dict[str, list[Tuple]] = {}
        with ThreadPoolExecutor(max_workers=8) as pool:
            for query, tuples in pool.map(self._decode_query, located):
                decoded[query] = tuples
        return decoded

    def inventory(self) -> dict[str, dict]:
        """Node and edge counts for each loaded practice, taken from the graph."""
        report: dict[str, dict] = {}
        for name, practice in self.practices.items():
            report[name] = {
                "node_counts": {type: practice.node_count(type) for type in practice.node_types},
                "edge_count": practice.edge_count,
                "node_types": sorted(practice.node_types),
                "edge_types": list(practice.edge_type_kinds),
                "rules": list(practice.rules_run),
                "tree": practice.root_node.serialize(),
            }
        return report

    def write_actual(self, out_dir: str) -> None:
        destination = Path(out_dir)
        destination.mkdir(parents=True, exist_ok=True)
        dump: dict[str, object] = {}
        for name, practice in self.practices.items():
            payload = {
                "node_types": sorted(practice.node_types),
                "edge_types": practice.edge_type_kinds,
                "node_counts": {type: practice.node_count(type) for type in practice.node_types},
                "edge_count": practice.edge_count,
                "tree": practice.root_node.serialize(),
            }
            dump[name] = payload
            (destination / f"{name}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (destination / "knowledge-graph.json").write_text(json.dumps(dump, indent=2), encoding="utf-8")

    def _bind(self, folder: str, practices: dict[str, str], database: str | None) -> None:
        self._folder = Path(database or folder).resolve()
        self._practice_roots = {name: Path(root).resolve() for name, root in practices.items()}
        self._languages = {name: self._detect_language(root) for name, root in self._practice_roots.items()}

    def _require_practices(self) -> None:
        if not self._practice_roots:
            raise QueryFailure("create_database", "Call create_database with a folder and practice roots first.")

    def _load_all(self, reuse: bool = False) -> None:
        previous = self.practices
        try:
            self._replace_practices(reuse)
        except Exception:
            self.practices = previous
            raise

    def _replace_practices(self, reuse: bool = False) -> None:
        self.practices = {}
        groups: dict[tuple[str, str], list[str]] = {}
        for name, source in self._practice_roots.items():
            practice = self.practice(name)
            practice.graph = self
            practice.source_root = str(source)
            practice.database = self._working_copy(name)
            practice.by_id[practice.root_node.node_id] = practice.root_node
            groups.setdefault((str(source), self._languages[name]), []).append(name)
        batches: list[tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]], dict[str, list[Tuple]]]] = []
        for names in groups.values():
            node_queries: list[tuple[str, str]] = []
            edge_queries: list[tuple[str, str]] = []
            rule_queries: list[tuple[str, str]] = []
            for name in names:
                node_queries.extend((name, query) for query in self.query_files(name, "nodes"))
                edge_queries.extend((name, query) for query in self.query_files(name, "edges"))
                rule_queries.extend((name, query) for query in self.query_files(name, "rules"))
            rows = self.run_queries(
                [query for _, query in node_queries + edge_queries + rule_queries],
                self._working_copy(names[0]),
                reuse=reuse,
            )
            batches.append((node_queries, edge_queries, rule_queries, rows))
        for node_queries, _, _, rows in batches:
            seen: set[str] = set()
            for name, query in node_queries:
                self.practice(name).apply_nodes(rows.get(query, []))
                if name not in seen:
                    self.practice(name).loaded.append("nodes")
                    seen.add(name)
        for _, edge_queries, _, rows in batches:
            seen = set()
            for name, query in edge_queries:
                self.practice(name).apply_edges(rows.get(query, []))
                if name not in seen:
                    self.practice(name).loaded.append("edges")
                    seen.add(name)
        for practice in self.practices.values():
            practice.root_node.populate()
        for _, _, rule_queries, rows in batches:
            seen = set()
            for name, query in rule_queries:
                practice = self.practice(name)
                practice.bind_rule(Path(query).stem, self._rule_node_types(Path(query).read_text(encoding="utf-8")))
                practice.apply_rules(Path(query).stem, rows.get(query, []))
                if name not in seen:
                    self.practice(name).loaded.append("rules")
                    seen.add(name)

    def _rule_node_types(self, text: str) -> list[str]:
        found: list[str] = []
        named = {
            "operationId": "Operation",
            "parameterId": "Parameter",
            "classId": "OoadClass",
            "namedClassId": "OoadClass",
            "moduleId": "Module",
            "propertyId": "Property",
            "packageId": "Package",
        }
        for token, node_type in named.items():
            if token in text and node_type not in found:
                found.append(node_type)
        for node_type in re.findall(r'nodeId\("[^"]+",\s*"([^"]+)"', text):
            if node_type not in found:
                found.append(node_type)
        return found

    def _source_key(self, name: str) -> tuple[str, str]:
        return (str(self._practice_roots[name]), self._languages[name])

    def _delete_databases(self) -> None:
        for name in self._practice_roots:
            for path in (self._master(name), self._working_copy(name), self._stamp_path(name)):
                if path.is_dir() or path.is_file():
                    remove_tree(path)

    def _ensure_masters(self) -> None:
        built: dict[tuple[str, str], Path] = {}
        for name in self._practice_roots:
            key = self._source_key(name)
            master = self._master(name)
            if key not in built:
                if not self._database_ready(master):
                    self._create_database_at(master, self._practice_roots[name], self._languages[name])
                built[key] = master
            elif not self._database_ready(master):
                self._copy_database(built[key], master)

    def _stamp_path(self, name: str) -> Path:
        working = self._working_copy(name)
        return working.with_name(working.name + ".stamp.json")

    def _working_copy_current(self, name: str) -> bool:
        if not self._database_ready(self._working_copy(name)):
            return False
        path = self._stamp_path(name)
        if not path.is_file():
            return False
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return False
        current = self._watched_stamp(name)
        return saved.get("source_ns") == current["source_ns"] and saved.get("queries_ns") == current["queries_ns"]

    def _write_stamp(self, name: str) -> None:
        path = self._stamp_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._watched_stamp(name), indent=2), encoding="utf-8")

    def _watched_stamp(self, name: str) -> dict[str, int | str]:
        language = self._languages[name]
        pack = query_pack(name, language)
        source_ns = self._latest_mtime(self._practice_roots[name])
        queries_ns = self._latest_mtime(pack)
        return {
            "source_ns": source_ns,
            "queries_ns": queries_ns,
            "source": self._iso_time(source_ns),
            "queries": self._iso_time(queries_ns),
        }

    def _latest_mtime(self, path: Path) -> int:
        if path.is_file():
            return path.stat().st_mtime_ns
        if not path.is_dir():
            return 0
        latest = 0
        skip = {"node_modules", ".git", "dist", "__pycache__", ".venv", ".codeql", "coverage"}
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames[:] = [name for name in dirnames if name not in skip]
            for filename in filenames:
                latest = max(latest, (Path(dirpath) / filename).stat().st_mtime_ns)
        return latest

    def _iso_time(self, mtime_ns: int) -> str:
        if mtime_ns <= 0:
            return ""
        return datetime.fromtimestamp(mtime_ns / 1_000_000_000, timezone.utc).isoformat()

    def _rewrite_working_copies(self, names: list[str]) -> None:
        """Extract each distinct source once, then copy that database to the other practices."""
        built: dict[tuple[str, str], Path] = {}
        for name in names:
            key = self._source_key(name)
            working = self._working_copy(name)
            if key not in built:
                self._create_database_at(working, self._practice_roots[name], self._languages[name])
                built[key] = working
            else:
                self._copy_database(built[key], working)

    def _decode_query(self, item: tuple[str, Path]) -> tuple[str, list[Tuple]]:
        query, bqrs = item
        return query, self._decode_bqrs(bqrs)

    def _decode_bqrs(self, bqrs: Path) -> list[Tuple]:
        decode = subprocess.run(
            [self._executable, "bqrs", "decode", str(bqrs), "--format=json"],
            check=False,
            capture_output=True,
            text=True,
        )
        if decode.returncode != 0 or not decode.stdout.strip():
            detail = decode.stderr or decode.stdout or "bqrs decode failed"
            raise QueryFailure(str(bqrs), detail)
        payload = json.loads(decode.stdout)
        tuples = payload.get("#select", {}).get("tuples") or []
        return [[self._cell(value) for value in row] for row in tuples]

    def _bqrs_for(self, database: Path, query: Path) -> Path:
        pack_root = self._pack_root(query)
        name = self._pack_name(pack_root)
        relative = query.resolve().relative_to(pack_root.resolve()).with_suffix(".bqrs")
        direct = database / "results" / Path(*name.split("/")) / relative
        if direct.is_file():
            return direct
        results = database / "results"
        matches = list(results.rglob(f"{query.stem}.bqrs")) if results.is_dir() else []
        if not matches:
            raise QueryFailure(str(query), f"no bqrs for {query.stem} under {results}")
        return max(matches, key=lambda path: path.stat().st_mtime)

    def _pack_root(self, query: Path) -> Path:
        for parent in (query.resolve(), *query.resolve().parents):
            if (parent / "qlpack.yml").is_file():
                return parent
        return query.resolve().parent

    def _pack_name(self, pack_root: Path) -> str:
        for line in (pack_root / "qlpack.yml").read_text(encoding="utf-8").splitlines():
            if line.startswith("name:"):
                return line.split(":", 1)[1].strip()
        return "cdd/codeql-graph"

    def _master(self, practice: str) -> Path:
        assert self._folder is not None
        return self._folder / ".codeql" / practice / f"{self._languages[practice]}-master"

    def _working_copy(self, practice: str) -> Path:
        assert self._folder is not None
        return self._folder / ".codeql" / practice / f"{self._languages[practice]}-working-copy"

    def _database_ready(self, database: Path) -> bool:
        return (database / "codeql-database.yml").is_file()

    def _detect_language(self, source: Path) -> str:
        skip = {"node_modules", ".git", "dist", "__pycache__", ".venv", ".codeql", "coverage"}
        counts = {"python": 0, "javascript": 0, "typescript": 0}
        for dirpath, dirnames, filenames in os.walk(source):
            dirnames[:] = [name for name in dirnames if name not in skip]
            for name in filenames:
                suffix = Path(name).suffix.lower()
                if name.endswith(".d.ts"):
                    continue
                if suffix in {".ts", ".tsx"}:
                    counts["typescript"] += 1
                elif suffix in {".js", ".jsx"}:
                    counts["javascript"] += 1
                elif suffix == ".py":
                    counts["python"] += 1
        return max(counts, key=counts.get)

    def _create_database_at(self, database: Path, source: Path, language: str) -> None:
        database.parent.mkdir(parents=True, exist_ok=True)
        extractor = "python" if language == "python" else "javascript"
        try:
            subprocess.run(
                [
                    self._executable,
                    "database",
                    "create",
                    str(database),
                    f"--language={extractor}",
                    f"--source-root={source}",
                    "--overwrite",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            detail = error.stderr or str(error)
            raise QueryFailure(str(database), detail) from error

    def _copy_database(self, source: Path, destination: Path) -> None:
        copy_tree(source, destination)

    def _practices_for_paths(self, paths: list[str]) -> list[str]:
        touched: list[str] = []
        for raw in paths:
            path = Path(raw)
            if not path.is_absolute() and self._folder is not None:
                path = self._folder / path
            resolved = path.resolve()
            for name, root in self._practice_roots.items():
                if name in touched:
                    continue
                if resolved == root or root in resolved.parents:
                    touched.append(name)
        return touched

    def _collect_nodes(self, node: CodeQLNode, ancestors: list[str], wanted: dict, found: list[dict], seen: set[int]) -> None:
        if id(node) in seen:
            return
        seen.add(id(node))
        chain = [*ancestors, node.name]
        if self._node_matches(node, wanted):
            found.append(
                {
                    "practice": node.practice.name,
                    "type": node.type,
                    "name": node.name,
                    "node_id": node.node_id,
                    "ancestors": ancestors,
                    "children": [child.name for child in node.children],
                }
            )
        for child in node.children:
            self._collect_nodes(child, chain, wanted, found, seen)

    def _node_matches(self, node: CodeQLNode, wanted: dict) -> bool:
        if node.type == "Practice" or node.type == node.name:
            return False
        if wanted.get("name") and node.name != wanted["name"]:
            return False
        types = wanted.get("types") or ([wanted["type"]] if wanted.get("type") else [])
        if types and node.type not in types:
            return False
        practices = wanted.get("practices") or ([wanted["practice"]] if wanted.get("practice") else [])
        if practices and node.practice.name not in practices:
            return False
        if wanted.get("violations") and not self._fails_selected_rule(node, wanted.get("rules") or []):
            return False
        relationships = wanted.get("relationships") or []
        if relationships and not self._on_relationship(node, relationships):
            return False
        return True

    def _fails_selected_rule(self, node: CodeQLNode, rules: list[str]) -> bool:
        hits = node.failed_rules
        if not hits:
            return False
        if not rules:
            return True
        return any(rule in rules for rule in hits)

    def _on_relationship(self, node: CodeQLNode, kinds: list[str]) -> bool:
        for kind in kinds:
            for edge in node.practice.edges.get(kind, []):
                if edge.parent is node or edge.child is node:
                    return True
        return False

    def _cell(self, value: object) -> str:
        if value is None:
            return ""
        if isinstance(value, dict) and "label" in value:
            return str(value["label"])
        return str(value)
