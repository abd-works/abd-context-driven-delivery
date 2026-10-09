"""CodeQLGraph. One toolset: databases, working copies, and practice graphs."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import threading
import time
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
_RUN_QUERIES_FLAGS = ("--threads=0", "--ram=8192", "--warnings=hide", "-v")
_CODEQL_SUBPROCESS_TIMEOUT_SECONDS = int(os.environ.get("CODEQL_SUBPROCESS_TIMEOUT_SECONDS", "600"))
_SKIP_SOURCE_DIRS = ("node_modules", ".git", "dist", "__pycache__", ".venv", ".codeql", "coverage")
_DB_STORE_BY_LANGUAGE = {"python": "db-python", "javascript": "db-javascript", "typescript": "db-javascript"}


def _dbscheme_mismatch(detail: str) -> bool:
    text = detail.lower()
    return "no upgrade path" in text and "dbscheme" in text


def _codeql_detail(*parts: str | None) -> str:
    return "\n".join(part for part in parts if part)


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


def _make_writable(function, path, exc) -> None:
    if _file_in_use(exc):
        raise exc
    try:
        os.chmod(path, stat.S_IWRITE)
    except OSError:
        pass
    function(path)


_WINDOWS_FILE_IN_USE = 32
_REMOVE_TREE_ATTEMPTS = 12
_REMOVE_TREE_DELAY_SECONDS = 0.3


def _file_in_use(error: BaseException) -> bool:
    if os.name != "nt":
        return False
    winerror = getattr(error, "winerror", None)
    return winerror == _WINDOWS_FILE_IN_USE


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


def _remove_tree_with_cache_recovery(path: Path, *, ignore_errors: bool = False) -> None:
    try:
        _remove_tree_once(path, ignore_errors=ignore_errors)
    except OSError as error:
        cache = missing_cache(error)
        if cache is None:
            raise
        _remove_tree_once(cache)
        _remove_tree_once(path, ignore_errors=ignore_errors)


def remove_tree(
    path: Path,
    *,
    ignore_errors: bool = False,
    lock_roots: tuple[Path | str, ...] = (),
) -> None:
    """Delete a database directory. A path Windows cannot see drops the CodeQL cache and retries."""
    from harness.mcp.codeql_server import release_codeql_database_locks

    last: BaseException | None = None
    for attempt in range(_REMOVE_TREE_ATTEMPTS):
        try:
            _remove_tree_with_cache_recovery(path, ignore_errors=ignore_errors)
            return
        except OSError as error:
            last = error
            if not _file_in_use(error):
                if ignore_errors:
                    return
                raise
            if attempt + 1 >= _REMOVE_TREE_ATTEMPTS:
                break
            if lock_roots:
                release_codeql_database_locks(*lock_roots, settle_seconds=1.0 if os.name == "nt" else 0.5)
            else:
                time.sleep(_REMOVE_TREE_DELAY_SECONDS)
    if ignore_errors:
        return
    if last is not None:
        raise last


def copy_tree(
    source: Path,
    destination: Path,
    *,
    lock_roots: tuple[Path | str, ...] = (),
) -> None:
    remove_tree(destination, lock_roots=lock_roots)
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

        Every copy still lists invokes, invokedBy, observes, demonstrates, and demonstratedThrough. A node already on the path is a stub, so a call back to this step stops.
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
            children = [child for child in self.children if child.type == child.name and child.name in {"invokes", "invokedBy", "observes", "demonstrates", "demonstratedThrough", "uses", "usedBy"}]
        path = stack | {self.node_id}
        written = [child.serialize(seen, self, path) for child in children]
        if first_home:
            category = self.rule_category()
            if category is not None:
                written.append(category)
        return {
            "type": self.type,
            "name": self.name,
            "node_id": self.node_id,
            "children": written,
        }

    def rule_category(self) -> dict | None:
        """Applicable rules as one child category. A violation filter keeps the rules that failed."""
        if self.type == self.name or self.type == "Practice":
            return None
        rows = self.rule_rows()
        if not rows:
            return None
        return {
            "type": "rules",
            "name": "rules",
            "node_id": f"{self.node_id}:rules",
            "children": rows,
        }

    def rule_rows(self) -> list[dict]:
        graph = self.practice.graph
        violations_only = bool(graph and graph.filter.violations)
        selected = list(graph.filter.rules) if graph else []
        failed: dict[str, str] = {}
        for hit in self.rules:
            failed.setdefault(hit.rule, hit.violation)
        rows: list[dict] = []
        for rule in self.practice.rules_for(self.type):
            violating = rule in failed
            if violations_only and (not violating or (selected and rule not in selected)):
                continue
            rows.append(
                {
                    "type": "Rule",
                    "name": rule,
                    "node_id": f"{self.node_id}:rules:{rule}",
                    "status": "violating" if violating else "passing",
                    "violation": failed.get(rule, ""),
                    "children": [],
                }
            )
        return rows

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
        self._query_rows: list[dict] = []
        self._progress: list[dict] = []
        self._on_progress = None
        self.use_query_server = False
        self._target_dbscheme_by_language: dict[str, Path | None] = {}
        self.filter = CodeQLFilter(self)
        super().__init__()

    def watch_progress(self, listener) -> None:
        """listener receives each progress event while a load or query is running."""
        self._on_progress = listener

    def _report(self, step: str, message: str, **extra: object) -> None:
        event = {"step": step, "message": message, **extra}
        self._progress.append(event)
        listener = self._on_progress
        if listener is None:
            return
        listener(event)

    @property
    def folder(self) -> str:
        """Directory that holds the .codeql master and working-copy databases.

        This is the repo root unless a subset directory was passed.
        """
        return "" if self._folder is None else str(self._folder)

    @property
    def master_stale(self) -> dict:
        """Whether the master is older than the working copy or the code. Each comparison includes those dates."""
        rows = self._artifact_rows()
        return {
            "older_than_worktree": self._older_than(rows, "master", "worktree"),
            "older_than_code": self._older_than(rows, "master", "code"),
        }

    @property
    def worktree_stale(self) -> dict:
        """Whether the working copy is older than the code or the master. Each comparison includes those dates."""
        rows = self._artifact_rows()
        return {
            "older_than_code": self._older_than(rows, "worktree", "code"),
            "older_than_master": self._older_than(rows, "worktree", "master"),
        }

    @property
    def graph_cache_stale(self) -> dict:
        """Whether the saved graph is older than the working copy, the master, or the code. Each comparison includes those dates."""
        rows = self._artifact_rows()
        cache_ns = self._graph_cache_ns()
        compared = [{**row, "graph_cache": cache_ns} for row in rows]
        return {
            "older_than_worktree": self._older_than(compared, "graph_cache", "worktree"),
            "older_than_master": self._older_than(compared, "graph_cache", "master"),
            "older_than_code": self._older_than(compared, "graph_cache", "code"),
        }

    @property
    def dates(self) -> dict:
        """Dates of the master, working copy, graph cache, and code."""
        return {
            "graph_cache": self._iso_time(self._graph_cache_ns()),
            "practices": [
                {
                    "practice": row["practice"],
                    "master": self._iso_time(row["master"]),
                    "worktree": self._iso_time(row["worktree"]),
                    "code": self._iso_time(row["code"]),
                }
                for row in self._artifact_rows()
            ],
        }

    @mcp
    @agent_tool
    def staleness(self, folder: str | None = None, practices: dict[str, str] | None = None, database: str | None = None) -> str:
        """Report master, working copy, and graph cache staleness, with the dates compared.

        folder and practices bind the graph when the caller has not already created a database.
        """
        return json.dumps(self.staleness_report(folder, practices, database), indent=2)

    def staleness_report(self, folder: str | None = None, practices: dict[str, str] | None = None, database: str | None = None) -> dict:
        """master_stale, worktree_stale, graph_cache_stale, and dates."""
        if folder and practices is not None:
            self._bind(folder, practices, database)
        return {
            "master_stale": self.master_stale,
            "worktree_stale": self.worktree_stale,
            "graph_cache_stale": self.graph_cache_stale,
            "dates": self.dates,
        }

    @mcp
    @agent_tool
    def serialize_graph_cache(self, folder: str | None = None, practices: dict[str, str] | None = None, database: str | None = None) -> str:
        """Write the loaded graph to the knowledge-graph cache.

        folder and practices bind the graph when the caller has not already created a database.
        """
        if folder and practices is not None:
            self._bind(folder, practices, database)
        self._require_practices()
        if not self._query_rows:
            raise QueryFailure("serialize_graph_cache", "Load a graph before serializing the cache.")
        self._save_graph()
        return f"Serialized the graph cache to {self._snapshot_path()}"

    @mcp
    @agent_tool
    def create_database(self, folder: str, practices: dict[str, str], database: str | None = None) -> str:
        """Delete each master and working copy, extract the source into a new master, and copy that master to the working copy.

        folder is the repo. Databases are stored there unless database is set.
        database stores a subset's databases so a test does not overwrite the repo database.
        practices maps each practice name to that practice's source root.
        """
        self._bind(folder, practices, database)
        self._report("create", f"Creating databases in {self._folder}")
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

        The working copy is rebuilt only when it is missing or the practice source or CodeQL queries are newer than the stamp. When the query packs match the saved graph, that graph is loaded instead of querying.
        """
        self._require_practices()
        self._report("reload", "Checking which working copies are older than the code")
        stale = [name for name in self._practice_roots if not self._working_copy_current(name)]
        if stale:
            self._report("reload", f"Rebuilding working copies for {', '.join(stale)}")
        else:
            self._report("reload", "Working copies match the code")
        self._rewrite_working_copies(stale)
        if not stale and self._saved_graph_current():
            self._restore_saved_graph()
            return "Working copies are current. Loaded the saved knowledge graph."
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
        """Populate the graph from the saved graph, or from query results on each working copy.

        folder is the repo. database stores a subset's databases so a test does not overwrite the repo database.
        A newer query pack re-runs the queries and saves the graph again. This does not create a database.
        """
        self._progress.clear()
        self._bind(folder, practices, database)
        self._report("load", f"Opening {folder}")
        stale = [name for name in self._practice_roots if not self._working_copy_current(name)]
        if stale:
            names = ", ".join(stale)
            if any(not self._database_ready(self._working_copy(name)) for name in stale):
                self._report("load", f"No working copy for {names}. Extracting source.")
            else:
                self._report("load", f"Working copy outdated for {names}. Rebuilding.")
            self._rewrite_working_copies(stale)
            for name in stale:
                self._write_stamp(name)
        if self._saved_graph_current():
            self._report("load", "Saved graph matches the query packs")
            self._restore_saved_graph()
            return "Loaded the saved knowledge graph."
        self._report("load", "Saved graph is stale. Querying the working copies.")
        self._load_all(reuse=not self._queries_newer_than_graph())
        return "Loaded the working copies."

    @mcp
    @agent_tool
    def return_nodes(self, filter: dict | None = None) -> str:
        """Return matching graph nodes as JSON, with ancestors, children, and relationships."""
        self._require_practices()
        if not self.practices:
            self._load_saved_or_query()
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
        """Evaluate the queries that are not already cached.

        Cached results are decoded. The rest run together on the warm query server, or in one database run-queries process if that server is down.
        reuse keeps a saved result even when the query pack is newer.
        """
        if not queries:
            return {}
        cached, missing = self._partition_cached(queries, database, reuse=reuse)
        if cached:
            self._report("cache", f"Using {len(cached)} saved query results. Running {len(missing)}.")
        produced: dict[str, Path] = {}
        if missing:
            produced = self._run_missing(missing, database)
        located: list[tuple[str, Path]] = []
        for query in queries:
            key = str(Path(query).resolve())
            if key in produced:
                located.append((query, produced[key]))
            elif key in cached:
                located.append((query, cached[key]))
            else:
                located.append((query, self._bqrs_for(database, Path(query))))
        self._report("decode", f"Decoding {len(located)} query results")
        return self._decode_located(located)

    def _run_codeql(
        self,
        args: list[str],
        *,
        label: str,
        timeout: int | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        limit = _CODEQL_SUBPROCESS_TIMEOUT_SECONDS if timeout is None else timeout
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)
        self._report("codeql", label)
        try:
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
        except OSError as error:
            self._report("error", f"Could not start CodeQL: {error}")
            raise QueryFailure(label, f"Could not start CodeQL\n{error}") from error
        stdout_parts: list[str] = []
        stderr_parts: list[str] = []

        def drain(stream, parts: list[str]) -> None:
            if stream is None:
                return
            for line in stream:
                parts.append(line)
                text = line.strip()
                if text:
                    self._report("codeql", text)

        threads = [
            threading.Thread(target=drain, args=(process.stdout, stdout_parts), daemon=True),
            threading.Thread(target=drain, args=(process.stderr, stderr_parts), daemon=True),
        ]
        for thread in threads:
            thread.start()
        try:
            if limit <= 0:
                process.wait()
            else:
                process.wait(timeout=limit)
        except subprocess.TimeoutExpired as error:
            process.kill()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            for thread in threads:
                thread.join(timeout=1)
            detail = self._with_crash_dump(_codeql_detail("".join(stderr_parts), "".join(stdout_parts)) or f"no output before timeout after {limit}s")
            self._report("error", f"CodeQL timed out after {limit}s during {label}")
            raise QueryFailure(label, f"CodeQL subprocess timed out after {limit}s\n{detail}") from error
        for thread in threads:
            thread.join(timeout=5)
        return subprocess.CompletedProcess(args, process.returncode or 0, "".join(stdout_parts), "".join(stderr_parts))

    def _partition_cached(self, queries: list[str], database: Path, *, reuse: bool) -> tuple[dict[str, Path], list[str]]:
        """Saved bqrs newer than their query pack are reused. One walk of the results directory."""
        index = self._bqrs_index(database)
        pack_mtime: dict[Path, int] = {}
        cached: dict[str, Path] = {}
        missing: list[str] = []
        for query in queries:
            path = Path(query)
            pack = self._pack_root(path)
            if pack not in pack_mtime:
                pack_mtime[pack] = self._latest_mtime(pack)
            hit = index.get(path.stem)
            fresh = hit is not None and (reuse or hit.stat().st_mtime_ns >= pack_mtime[pack])
            if fresh and hit is not None:
                cached[str(path.resolve())] = hit
            else:
                missing.append(query)
        return cached, missing

    def _bqrs_index(self, database: Path) -> dict[str, Path]:
        results = database / "results"
        found: dict[str, Path] = {}
        if not results.is_dir():
            return found
        for path in results.rglob("*.bqrs"):
            previous = found.get(path.stem)
            if previous is None or path.stat().st_mtime_ns >= previous.stat().st_mtime_ns:
                found[path.stem] = path
        return found

    def _run_missing(self, queries: list[str], database: Path, *, retried_for_dbscheme: bool = False) -> dict[str, Path]:
        total = len(queries)
        self._report("queries", f"Running {total} queries together", total=total)
        if not self.use_query_server:
            self._execute_queries(queries, database, retried_for_dbscheme=retried_for_dbscheme)
            return {}
        try:
            from harness.mcp.codeql_query_daemon import QueryServerClient

            self._report("queries", "Connecting to the query server")
            client = QueryServerClient().ensure_query_server(_REPO)
            self._report("queries", f"Query server on port {client.port}, {total} queries, threads across cores")
            produced = client.run_queries(queries, database, lambda line: self._report("query", line))
            resolved = {str(Path(query).resolve()) for query in queries}
            return {key: path for key, path in produced.items() if key in resolved}
        except QueryFailure as error:
            if not retried_for_dbscheme and _dbscheme_mismatch(error.detail):
                self._report("queries", "CodeQL database scheme is outdated. Rebuilding and retrying queries.")
                self._rebuild_working_copies_for_database(database)
                return self._run_missing(queries, database, retried_for_dbscheme=True)
            raise
        except Exception as error:
            detail = str(error)
            if not retried_for_dbscheme and _dbscheme_mismatch(detail):
                self._report("queries", "CodeQL database scheme is outdated. Rebuilding and retrying queries.")
                self._rebuild_working_copies_for_database(database)
                return self._run_missing(queries, database, retried_for_dbscheme=True)
            self._report("error", detail)
            raise QueryFailure("query server", detail) from error

    def _execute_queries(self, queries: list[str], database: Path, *, retried_for_dbscheme: bool = False) -> None:
        if not queries:
            return
        paths = [str(Path(query).resolve()) for query in queries]
        total = len(paths)
        for index, query in enumerate(paths, start=1):
            self._report("query", f"{index}/{total} {Path(query).name}", index=index, total=total, query=query)
        run = self._run_codeql(
            [
                self._executable,
                "database",
                "run-queries",
                *_RUN_QUERIES_FLAGS,
                str(database),
                "--",
                *paths,
            ],
            label="database run-queries",
            timeout=0,
        )
        if run.returncode != 0:
            detail = self._with_crash_dump(_codeql_detail(run.stderr, run.stdout) or "database run-queries failed")
            if not retried_for_dbscheme and _dbscheme_mismatch(detail):
                self._report("queries", "CodeQL database scheme is outdated. Rebuilding and retrying queries.")
                self._rebuild_working_copies_for_database(database)
                self._execute_queries(queries, database, retried_for_dbscheme=True)
                return
            self._report("error", detail)
            raise QueryFailure("database run-queries", detail)

    def _with_crash_dump(self, detail: str) -> str:
        from harness.mcp.codeql_server import codeql_process_report, crash_logs

        logs = crash_logs([Path.cwd(), _REPO], time.time() - 7200)
        others = codeql_process_report()
        text = detail
        if logs and logs not in text:
            text = f"{text}\n{logs}"
        if others and others not in text:
            text = f"{text}\n{others}"
        return text

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
        except Exception as error:
            self.practices = previous
            self._report("error", f"{type(error).__name__}: {error}")
            raise
        self._report("save", "Writing the graph cache")
        self._save_graph()

    def _load_saved_or_query(self) -> None:
        if self._saved_graph_current():
            self._restore_saved_graph()
            return
        self._load_all(reuse=not self._queries_newer_than_graph())

    def _replace_practices(self, reuse: bool = False) -> None:
        grouped = self._open_practices()
        batches = [self._query_batch(names, reuse) for names in grouped.values()]
        self._query_rows = [self._batch_record(batch) for batch in batches]
        self._apply_batches(batches)

    def _open_practices(self) -> dict[tuple[str, str], list[str]]:
        self.practices = {}
        groups: dict[tuple[str, str], list[str]] = {}
        for name, source in self._practice_roots.items():
            practice = self.practice(name)
            practice.graph = self
            practice.source_root = str(source)
            practice.database = self._working_copy(name)
            practice.by_id[practice.root_node.node_id] = practice.root_node
            groups.setdefault((str(source), self._languages[name]), []).append(name)
        return groups

    def _query_batch(self, names: list[str], reuse: bool) -> dict:
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
        return {"nodes": node_queries, "edges": edge_queries, "rules": rule_queries, "rows": rows}

    def _batch_record(self, batch: dict) -> dict:
        rows = batch["rows"]
        return {
            "nodes": [[name, query, rows.get(query, [])] for name, query in batch["nodes"]],
            "edges": [[name, query, rows.get(query, [])] for name, query in batch["edges"]],
            "rules": [[name, query, rows.get(query, [])] for name, query in batch["rules"]],
        }

    def _apply_batches(self, batches: list[dict]) -> None:
        for batch in batches:
            self._apply_kind(batch["nodes"], batch["rows"], "nodes")
        for batch in batches:
            self._apply_kind(batch["edges"], batch["rows"], "edges")
        for practice in self.practices.values():
            practice.root_node.populate()
        for batch in batches:
            self._apply_kind(batch["rules"], batch["rows"], "rules")

    def _apply_kind(self, queries: list[tuple[str, str]], rows: dict[str, list[Tuple]], kind: str) -> None:
        seen: set[str] = set()
        total = len(queries)
        for index, (name, query) in enumerate(queries, start=1):
            self._report(
                "apply",
                f"{kind} {index}/{total} {name} {Path(query).name}",
                index=index,
                total=total,
                practice=name,
                query=query,
                kind=kind,
            )
            practice = self.practice(name)
            tuples = rows.get(query, [])
            if kind == "nodes":
                practice.apply_nodes(tuples)
            elif kind == "edges":
                practice.apply_edges(tuples)
            else:
                practice.bind_rule(Path(query).stem, self._rule_node_types(Path(query).read_text(encoding="utf-8")))
                practice.apply_rules(Path(query).stem, tuples)
            if name not in seen:
                practice.loaded.append(kind)
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

    def _lock_release_roots(self) -> tuple[Path | str, ...]:
        roots: list[Path | str] = [_REPO]
        if self._folder is not None:
            roots.append(self._folder)
        return tuple(roots)

    def _delete_databases(self) -> None:
        from harness.mcp.codeql_server import release_codeql_database_locks

        lock_roots = self._lock_release_roots()
        release_codeql_database_locks(*lock_roots, settle_seconds=1.0 if os.name == "nt" else 0.5)
        snapshot = self._snapshot_path()
        if snapshot.is_file():
            snapshot.unlink()
        for name in self._practice_roots:
            for path in (self._master(name), self._working_copy(name), self._stamp_path(name)):
                if path.is_dir() or path.is_file():
                    remove_tree(path, lock_roots=lock_roots)

    def _snapshot_path(self) -> Path:
        folder = self._folder or Path()
        return folder / ".codeql" / "knowledge-graph.json"

    def _read_snapshot(self) -> dict | None:
        path = self._snapshot_path()
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def _saved_graph_current(self) -> bool:
        """The saved graph matches the query packs. A newer query file means the graph is rebuilt."""
        saved = self._read_snapshot()
        if saved is None or not saved.get("batches"):
            return False
        recorded = saved.get("queries_ns") or {}
        if set(recorded) != set(self._practice_roots):
            return False
        for name in self._practice_roots:
            if recorded.get(name) != self._watched_stamp(name)["queries_ns"]:
                return False
        return True

    def _queries_newer_than_graph(self) -> bool:
        saved = self._read_snapshot()
        if saved is None:
            return False
        return not self._saved_graph_current()

    def _save_graph(self) -> None:
        if self._folder is None or not self._query_rows:
            return
        path = self._snapshot_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "queries_ns": {name: self._watched_stamp(name)["queries_ns"] for name in self._practice_roots},
            "batches": self._query_rows,
        }
        path.write_text(json.dumps(payload), encoding="utf-8")

    def _restore_saved_graph(self) -> None:
        self._report("restore", "Reading the saved graph")
        saved = self._read_snapshot() or {}
        self._query_rows = list(saved.get("batches") or [])
        self._open_practices()
        self._apply_batches(self._batches_from_disk(self._query_rows))

    def _batches_from_disk(self, records: list[dict]) -> list[dict]:
        batches = []
        for record in records:
            rows: dict[str, list[Tuple]] = {}
            listed = record["nodes"] + record["edges"] + record["rules"]
            for _name, query, tuples in listed:
                rows[query] = tuples
            batches.append(
                {
                    "nodes": [(name, query) for name, query, _tuples in record["nodes"]],
                    "edges": [(name, query) for name, query, _tuples in record["edges"]],
                    "rules": [(name, query) for name, query, _tuples in record["rules"]],
                    "rows": rows,
                }
            )
        return batches

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
        if not self._database_dbscheme_current(name):
            return False
        path = self._stamp_path(name)
        if not path.is_file():
            return False
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            self._report("error", f"Working copy stamp for {name} is not valid JSON: {error}")
            return False
        current = self._watched_stamp(name)
        return saved.get("source_ns") == current["source_ns"] and saved.get("queries_ns") == current["queries_ns"]

    def _practices_with_stale_dbscheme(self) -> list[str]:
        stale: list[str] = []
        for name in self._practice_roots:
            working = self._working_copy(name)
            if not self._database_ready(working):
                continue
            if not self._database_dbscheme_current(name):
                stale.append(name)
        return stale

    def _rebuild_working_copies_for_database(self, database: Path) -> None:
        from harness.mcp.codeql_server import release_codeql_database_locks

        lock_roots = self._lock_release_roots()
        release_codeql_database_locks(*lock_roots, settle_seconds=1.0 if os.name == "nt" else 0.5)
        names = self._practice_names_for_database(database)
        touched = names if names else list(self._practice_roots)
        self._rewrite_working_copies(touched)
        for name in touched:
            self._write_stamp(name)

    def _practice_names_for_database(self, database: Path) -> list[str]:
        resolved = Path(database).resolve()
        return [name for name in self._practice_roots if self._working_copy(name).resolve() == resolved]

    def _database_dbscheme_current(self, name: str) -> bool:
        target = self._target_dbscheme(name)
        if target is None:
            return True
        stored = self._stored_dbscheme(self._working_copy(name), self._languages[name])
        if stored is None or not stored.is_file():
            return False
        return stored.read_bytes() == target.read_bytes()

    def _stored_dbscheme(self, database: Path, language: str) -> Path | None:
        store = _DB_STORE_BY_LANGUAGE.get(language)
        if store is None:
            return None
        folder = database / store
        if not folder.is_dir():
            return None
        matches = list(folder.glob("*.dbscheme"))
        if not matches:
            return None
        return matches[0]

    def _target_dbscheme(self, practice: str) -> Path | None:
        language = self._languages[practice]
        if language in self._target_dbscheme_by_language:
            return self._target_dbscheme_by_language[language]
        sample = self.query_files(practice, "nodes")
        if not sample:
            sample = self.query_files(practice, "rules")
        if not sample:
            self._target_dbscheme_by_language[language] = None
            return None
        run = subprocess.run(
            [
                self._executable,
                "resolve",
                "library-path",
                f"--query={sample[0]}",
                "--format=json",
                f"--search-path={_REPO / 'practices'}",
            ],
            cwd=str(_REPO),
            capture_output=True,
            text=True,
            check=False,
        )
        if run.returncode != 0 or not run.stdout.strip():
            self._target_dbscheme_by_language[language] = None
            return None
        try:
            payload = json.loads(run.stdout)
            path = Path(payload["dbscheme"])
        except (json.JSONDecodeError, KeyError, TypeError):
            self._target_dbscheme_by_language[language] = None
            return None
        self._target_dbscheme_by_language[language] = path
        return path

    def _write_stamp(self, name: str) -> None:
        path = self._stamp_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._watched_stamp(name), indent=2), encoding="utf-8")

    def _watched_stamp(self, name: str) -> dict[str, int | str]:
        language = self._languages[name]
        pack = query_pack(name, language)
        source_ns = self._latest_mtime(self._practice_roots[name])
        queries_ns = self._latest_mtime(pack)
        target = self._target_dbscheme(name)
        dbscheme_digest = ""
        if target is not None and target.is_file():
            dbscheme_digest = hashlib.sha256(target.read_bytes()).hexdigest()
        return {
            "source_ns": source_ns,
            "queries_ns": queries_ns,
            "source": self._iso_time(source_ns),
            "queries": self._iso_time(queries_ns),
            "dbscheme_digest": dbscheme_digest,
        }

    def _latest_mtime(self, path: Path) -> int:
        if path.is_file():
            return path.stat().st_mtime_ns
        if not path.is_dir():
            return 0
        latest = 0
        skip = set(_SKIP_SOURCE_DIRS)
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames[:] = [name for name in dirnames if name not in skip]
            for filename in filenames:
                latest = max(latest, (Path(dirpath) / filename).stat().st_mtime_ns)
        return latest

    def _iso_time(self, mtime_ns: int) -> str:
        if mtime_ns <= 0:
            return ""
        return datetime.fromtimestamp(mtime_ns / 1_000_000_000, timezone.utc).isoformat()

    def _artifact_rows(self) -> list[dict]:
        rows = []
        for name in self._practice_roots:
            rows.append(
                {
                    "practice": name,
                    "master": self._database_mtime(self._master(name)),
                    "worktree": self._database_mtime(self._working_copy(name)),
                    "code": self._latest_mtime(self._practice_roots[name]),
                }
            )
        return rows

    def _database_mtime(self, database: Path) -> int:
        marker = database / "codeql-database.yml"
        if marker.is_file():
            return marker.stat().st_mtime_ns
        return 0

    def _graph_cache_ns(self) -> int:
        path = self._snapshot_path()
        if path.is_file():
            return path.stat().st_mtime_ns
        return 0

    def _older_than(self, rows: list[dict], left: str, right: str) -> dict:
        """The comparison with the greatest gap. A missing left side is older than a right side that exists."""
        chosen: dict | None = None
        chosen_older = False
        chosen_gap = 0
        for row in rows:
            left_ns = int(row[left])
            right_ns = int(row[right])
            older = right_ns > 0 and left_ns < right_ns
            gap = right_ns - left_ns
            if chosen is None or (older and not chosen_older) or (older == chosen_older and gap > chosen_gap):
                chosen = row
                chosen_older = older
                chosen_gap = gap
        if chosen is None:
            return {"older": False, "practice": "", "dates": {left: "", right: ""}}
        return {
            "older": chosen_older,
            "practice": chosen["practice"],
            "dates": {left: self._iso_time(int(chosen[left])), right: self._iso_time(int(chosen[right]))},
        }

    def _rewrite_working_copies(self, names: list[str]) -> None:
        """Extract each distinct source once, then copy that database to the other practices."""
        from harness.mcp.codeql_server import release_codeql_database_locks

        lock_roots = self._lock_release_roots()
        release_codeql_database_locks(*lock_roots, settle_seconds=1.0 if os.name == "nt" else 0.5)
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
        self._report("decode", Path(query).name, query=query)
        return query, self._decode_bqrs(bqrs)

    def _decode_bqrs(self, bqrs: Path) -> list[Tuple]:
        decode = self._run_codeql(
            [self._executable, "bqrs", "decode", str(bqrs), "--format=json"],
            label=f"bqrs decode {bqrs}",
        )
        if decode.returncode != 0 or not decode.stdout.strip():
            detail = decode.stderr or decode.stdout or "bqrs decode failed"
            self._report("error", f"Could not decode {bqrs.name}: {detail}")
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
        skip = set(_SKIP_SOURCE_DIRS)
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
        if database.exists() and not self._database_ready(database):
            remove_tree(database, lock_roots=self._lock_release_roots())
        self._report("extract", f"Extracting {language} source into {database.name}")
        extractor = "python" if language == "python" else "javascript"
        run = self._run_codeql(
            [
                self._executable,
                "database",
                "create",
                str(database),
                f"--language={extractor}",
                f"--source-root={source}",
                "--overwrite",
            ],
            label=f"database create {database}",
            extra_env={
                "LGTM_INDEX_EXCLUDE": "\n".join(str(source / name) for name in _SKIP_SOURCE_DIRS),
            },
        )
        if run.returncode != 0:
            detail = _codeql_detail(run.stderr, run.stdout) or "database create failed"
            self._report("error", detail)
            raise QueryFailure(str(database), detail)

    def _copy_database(self, source: Path, destination: Path) -> None:
        copy_tree(source, destination, lock_roots=self._lock_release_roots())

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
                    "rules": node.rule_rows(),
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
