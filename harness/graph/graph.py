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
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp

Display = str
Tuple = list[str]
_GRAPH_PRACTICE_NAMES = frozenset({"clean_engineering", "stories", "ddd", "bdd", "ux"})
_GRAPH_JSON_NAME = "graph.json"
_CACHE_SKIP_DIRS = {
    ".codeql",
    ".git",
    "node_modules",
    "__pycache__",
    ".sessions",
    "retired",
    ".context",
    ".venv",
    "dist",
    "build",
    "coverage",
    ".next",
    "out",
    "playwright-report",
    "test-results",
}
_RULE_FILE_NAMES = ("rules.py", "schema.yaml")

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


class GraphFailure(Exception):
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

    def expand(self, nodes: list[Node]) -> None:
        """Inline called operations and the classes they name. Folds cover the call, the class, and each block."""
        text, folds = self._inline(self.text, nodes, 1, set())
        self._text = text
        self.folds = folds

    def _inline(self, text: str, nodes: list[Node], depth: int, stack: set[str]) -> tuple[str, list[SourceFold]]:
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

    def _inline_line(self, line: str, output: list[str], folds: list[SourceFold], operations: dict[str, Node], classes: dict[str, Node], nodes: list[Node], depth: int, stack: set[str]) -> None:
        call_line = len(output)
        for name in self._called_names(line):
            callee = operations.get(name)
            if callee is None or callee.node_id in stack:
                continue
            self._append_operation(output, folds, callee, line, nodes, depth, stack, classes)
        if len(output) > call_line:
            folds.append(SourceFold(call_line, len(output), "call"))

    def _append_operation(self, output: list[str], folds: list[SourceFold], callee: Node, line: str, nodes: list[Node], depth: int, stack: set[str], classes: dict[str, Node]) -> None:
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

    def _append_class(self, output: list[str], folds: list[SourceFold], node: Node, pad: str) -> None:
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

    def _mentioned_classes(self, text: str, classes: dict[str, Node], stack: set[str]) -> list[Node]:
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
        """Point this slice at an exported fixture function by name under ``root``."""
        if not root or not name:
            return
        root_path = Path(root)
        if not root_path.is_dir():
            return
        pattern = re.compile(rf"(?:export\s+)?function\s+{re.escape(name)}\b")
        for path in sorted(root_path.rglob("*.ts")):
            if any(part in {"node_modules", "dist", "build"} for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            for index, line in enumerate(lines, start=1):
                if not pattern.search(line):
                    continue
                self.file = path.relative_to(root_path).as_posix()
                self.root = root
                self.start_line = index
                self.end_line = self._call_end(lines, index - 1)
                self._text = None
                return

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


class RuleResult:
    """A rule query row attached to the node it checked."""

    def __init__(self, rule: str, violation: str) -> None:
        self.rule = rule
        self.violation = violation


class Filter:
    """Narrows a loaded graph. A practice choice reads that practice's node queries, and a node-type choice sets the relationships and rules."""

    def __init__(self, graph: Graph) -> None:
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

class Node:
    """children is the list populate writes on this node. Direct edges are the children. Grouped and relationship edges sit under one child named for the kind."""

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

    @property
    def rules(self):
        """Schema rules for this node, with violations on each entry."""
        from harness.graph.node_rules import attach_node_rules

        if self._rules is None:
            attach_node_rules(self)
        return self._rules

    @property
    def failed_rules(self) -> list[str]:
        return self.rules.failed_slugs()

    @property
    def passing_rules(self) -> list[str]:
        """Rules that apply to this node and did not fail."""
        return self.rules.passing_slugs()

    @staticmethod
    def fact(row: Tuple) -> dict | None:
        if len(row) < 7:
            return None
        node_id, name, semantic_type, practice, file, line, end_line = (row + [""] * 7)[:7]
        if not node_id or not semantic_type:
            return None
        practice_name = str(practice).strip()
        if practice_name not in _GRAPH_PRACTICE_NAMES:
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

    def _holder(self, node: Node) -> bool:
        return node.type == node.name

    def _child_named(self, name: str) -> Node | None:
        for child in self.children:
            if child.name == name:
                return child
        return None

    def serialize(self, seen: set[str] | None = None, via: Node | None = None, stack: set[str] | None = None) -> dict:
        """Write the full child list once, on the home parent.

        A relationship copy is empty. A node already on the path is a stub, so a call back to this step stops.
        """
        seen = set() if seen is None else seen
        stack = set() if stack is None else stack
        if self.node_id in stack:
            return {"type": self.type, "name": self.name, "node_id": self.node_id, "children": []}
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
        """One rule child: status violating, passing, or prompt, and every stored hit."""
        graph = self.practice.graph
        violations_only = bool(graph and graph.filter.violations)
        selected = list(graph.filter.rules) if graph else []
        rows: list[dict] = []
        for slug in self.rules.slugs():
            entry = self.rules.entries.get(slug)
            hits = [dict(hit) for hit in getattr(entry, "hits", []) or []]
            if hits:
                status = "violating"
            elif not getattr(entry, "executable", True):
                status = "prompt"
            else:
                status = "passing"
            if violations_only and (status != "violating" or (selected and slug not in selected)):
                continue
            rows.append(
                {
                    "type": "Rule",
                    "name": slug,
                    "node_id": f"{self.node_id}:rules:{slug}",
                    "status": status,
                    "violations": hits,
                    "children": [],
                }
            )
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

    def load_nodes(self, tuples: list[Tuple]) -> None:
        self.apply_nodes(tuples)

    def apply_nodes(self, tuples: list[Tuple]) -> None:
        from harness.graph.node_rules import attach_node_rules
        from harness.graph.schema_rules import bind_practice_rules

        bind_practice_rules(self)
        for row in tuples:
            fact = Node.fact(row)
            if fact is None or fact["node_id"] in self.by_id:
                continue
            self.node_types.add(fact["semantic_type"])
            node = Node.from_fact(self, fact)
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

    def load_edges(self, tuples: list[Tuple]) -> None:
        self.apply_edges(tuples)

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
        list_ = self.edges.setdefault(fact["kind"], [])
        if any(edge.parent is parent and edge.child is child for edge in list_):
            return
        if fact["kind"] not in self.edge_types:
            self.edge_types[fact["kind"]] = EdgeType(fact["kind"], fact["order"], fact["display"])
        list_.append(Edge(fact["kind"], fact["order"], fact["display"], parent, child))

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
            existing = [message for s, message in node.rules.violations() if s == slug]
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



@agent_toolset
class Graph:
    """One graph. Builders fill nodes, edges, and rules. The explorer reads the tree."""

    def __init__(self) -> None:
        self._folder: Path | None = None
        self._practice_roots: dict[str, Path] = {}
        self.practices: dict[str, PracticeGraph] = {}
        self.filter = Filter(self)
        self.overlays: list[str] = []
        self._progress = None

    def watch_progress(self, callback) -> None:
        """The app host reports load progress through this callback."""
        self._progress = callback

    def report_progress(self, message: str, step: str = "load") -> None:
        """Tell the explorer which practice, file, node, or rule is in progress."""
        if self._progress is None:
            return
        self._progress({"step": step, "message": message})

    @property
    def folder(self) -> str:
        return "" if self._folder is None else str(self._folder)

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
    ) -> str:
        """Open each practice on its source root and build the explorer tree.

        A saved graph in the folder's ``.context`` is used when the folder, its
        contents, and the rule files are not newer than that file. A forced load
        always rebuilds. Every rebuild writes the serialized graph.
        """
        self._folder = Path(database or folder).resolve()
        self._practice_roots = {name: Path(root).resolve() for name, root in practices.items()}
        self.overlays = _normalize_overlay_list(list(overlays or []))
        self.report_progress("Checking the saved graph")
        if not force and self._saved_graph_is_current():
            self.report_progress("Loading the saved graph")
            self._load_saved_json()
            return "Loaded the saved graph."
        self.report_progress("Scanning the folder")
        self._build_working_copy()
        self.report_progress("Saving the graph")
        self.save_json()
        return "Loaded the working copies."

    @mcp
    @agent_tool
    def save_json(self) -> str:
        """Write the serialized graph into the loaded folder's ``.context``."""
        folder = self._folder
        if folder is None:
            return ""
        path = self._graph_json_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._graph_document(), separators=(",", ":")), encoding="utf-8")
        return str(path)

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

    def _practice_document(self, practice: PracticeGraph) -> dict:
        nodes = [node for group in practice.nodes.values() for node in group]
        edges = [edge for group in practice.edges.values() for edge in group]
        return {
            "source_root": practice.source_root,
            "nodes": [self._node_row(node) for node in nodes],
            "edges": [self._edge_row(edge) for edge in edges],
            "rules": [[slug, node.node_id, message] for node in nodes for slug, message in node.rules.violations()],
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
            encode_node_data(node.data),
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
        return not self._folder_is_dirty(stamp)

    def _saved_graph_matches_request(self, document: dict) -> bool:
        saved = document.get("practices")
        if not isinstance(saved, dict):
            return False
        if set(saved) != set(self._practice_roots):
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
            dirnames[:] = [name for name in dirnames if name not in _CACHE_SKIP_DIRS]
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

    def _folder_is_dirty(self, stamp: float) -> bool:
        folder = self._folder
        if folder is None or not folder.exists():
            return True
        if folder.is_file():
            return folder.stat().st_mtime > stamp
        return self._contents_newer_than(folder, stamp)

    def _contents_newer_than(self, folder: Path, stamp: float) -> bool:
        seen = 0
        for dirpath, dirnames, filenames in os.walk(folder):
            dirnames[:] = [name for name in dirnames if name not in _CACHE_SKIP_DIRS]
            for filename in filenames:
                seen += 1
                if seen == 1 or seen % 400 == 0:
                    self.report_progress(f"Checking folder dates · {seen}")
                if Path(dirpath, filename).stat().st_mtime > stamp:
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

    def _restore_practice_nodes(self, name: str, saved: dict) -> None:
        self.report_progress(f"Loading saved {name} nodes")
        practice = self.practice(name)
        practice.source_root = str(saved.get("source_root") or self._practice_roots[name])
        practice.by_id[practice.root_node.node_id] = practice.root_node
        practice.load_nodes(list(saved.get("nodes") or []))

    def _restore_practice_links(self, name: str, saved: dict) -> None:
        practice = self.practice(name)
        practice.load_edges(list(saved.get("edges") or []))
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

    def set_overlays(self, overlays: list[str]) -> str:
        """Apply pattern overlays and rebuild the explorer tree from the open folder."""
        self.overlays = _normalize_overlay_list(list(overlays or []))
        if self._folder is not None and self._practice_roots:
            roots = {name: str(path) for name, path in self._practice_roots.items()}
            self.load_working_copy(str(self._folder), roots, database=str(self._folder), overlays=self.overlays)
        label = ", ".join(Path(item).name for item in self.overlays) if self.overlays else "none"
        return f"Applied pattern overlays: {label}."

    def inventory(self) -> dict[str, dict]:
        """Node and edge counts for each loaded practice, taken from the graph."""
        from harness.graph.schema_rules import active_overlay_patterns, qualified_rule_labels

        patterns = active_overlay_patterns(tuple(self.overlays))
        report: dict[str, dict] = {}
        for name, practice in self.practices.items():
            report[name] = {
                "node_counts": {type: practice.node_count(type) for type in practice.node_types},
                "edge_count": practice.edge_count,
                "node_types": sorted(practice.node_types),
                "edge_types": list(practice.edge_type_kinds),
                "rules": qualified_rule_labels(name, practice.applicable, patterns),
                "tree": practice.root_node.serialize(),
            }
        return report

    @mcp
    @agent_tool
    @skill(name="read-graph")
    def return_nodes(self, filter: dict | None = None) -> str:
        """Return matching graph nodes as JSON, with ancestors, children, and relationships."""
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

    def _collect_nodes(self, node: Node, ancestors: list[str], wanted: dict, found: list[dict], seen: set[int]) -> None:
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

    def _node_matches(self, node: Node, wanted: dict) -> bool:
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

    def _fails_selected_rule(self, node: Node, rules: list[str]) -> bool:
        hits = node.failed_rules
        if not hits:
            return False
        if not rules:
            return True
        return any(self._label_hits(node, label, hits) for label in rules)

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

    def _on_relationship(self, node: Node, kinds: list[str]) -> bool:
        for kind in kinds:
            for edge in node.practice.edges.get(kind, []):
                if edge.parent is node or edge.child is node:
                    return True
        return False

