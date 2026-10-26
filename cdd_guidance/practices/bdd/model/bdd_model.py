"""Canonical BDD describe tree — parse a sketch or spec code, render python or typescript."""

from __future__ import annotations

import ast
import re

from harness.graph.bound_node import BoundChildren, BoundNode
from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.call_graph import (
    CallGraphEntry,
    parse_arrow_line,
    parse_call_graph_block,
    render_call_graph_block,
)
from cdd_guidance.practices.bdd.model.nodes import Context, Description, Observation


class BddModel(BoundNode):
    _graph_practice = "bdd"
    _semantic_type_name = "Spec"
    _belongs = {("Description", "Spec")}

    def __init__(self, graph: Graph | None = None) -> None:
        super().__init__("spec", 0, graph)
        self._descriptions = BoundChildren(self, "descriptions")
        if graph is not None:
            self._copy_descriptions_on_graph()

    @property
    def descriptions(self) -> list[Description]:
        return self._descriptions

    @descriptions.setter
    def descriptions(self, descriptions: list[Description]) -> None:
        self._refill(self._descriptions, descriptions)

    def _copy_descriptions_on_graph(self) -> None:
        others = [node for node in self._copies_on_graph("Spec") if node.descriptions]
        if not others:
            return
        for description in others[0].descriptions:
            self.descriptions.append(description.clone())

    def parse(self, text: str) -> "BddModel":
        self.descriptions = _parse_sketch(text)
        return self

    def parse_code(self, text: str) -> "BddModel":
        """Read the describe tree out of spec code; each language model knows its own syntax."""
        return self

    def load_source_facts(self, text: str) -> None:
        """Fill the facts the whole spec file owns."""
        from cdd_guidance.practices.bdd.model.nodes import private_probe_in_text
        from cdd_guidance.practices.bdd.model.spec_source import code_like_describe_lines, has_signature_marker

        self.patches_infrastructure = bool(_PATCH_DECORATOR.search(text) or _MOCK_PATCH_IMPORT.search(text))
        self.signature_marker = has_signature_marker(text)
        self.top_level_describes = _MAMBA_DESCRIBE.findall(text)
        self.code_like_describe_lines = code_like_describe_lines(text)
        self.private_probe = private_probe_in_text(text, 1)

    def behavior_nodes(self) -> list:
        """Every description, context, and observation under this spec, parents first."""
        found: list = []
        pending = list(self.descriptions)
        while pending:
            node = pending.pop(0)
            found.append(node)
            pending.extend(getattr(node, "contexts", []))
            pending.extend(getattr(node, "observations", []))
        return found

    def render(self, canonical: "BddModel", previous: str | None = None) -> str:
        return "\n\n".join(_render_python(item) for item in canonical.descriptions)


class PythonBddModel(BddModel):
    def render(self, canonical: BddModel, previous: str | None = None) -> str:
        return "\n\n".join(_render_python(item) for item in canonical.descriptions)

    def parse_code(self, text: str) -> "BddModel":
        """Mamba specs: `with description(...)`, `with context(...)`, `with it(...)` blocks."""
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return self
        self.descriptions = [
            node for node in (_mamba_node(item, None, order) for order, item in enumerate(tree.body, 1)) if node is not None
        ]
        return self


class TypeScriptBddModel(BddModel):
    def render(self, canonical: BddModel, previous: str | None = None) -> str:
        return "\n\n".join(_render_typescript(item) for item in canonical.descriptions)

    def parse_code(self, text: str) -> "BddModel":
        """Vitest / Jest specs: `describe(...)`, `it(...)`, `test(...)` blocks found by bracket matching."""
        blocks = sorted(_script_blocks(text), key=lambda block: block[1])
        self.descriptions = _nest_script_blocks(blocks)
        return self


_PATCH_DECORATOR = re.compile(r"^\s*@patch\s*\(", re.MULTILINE)
_MOCK_PATCH_IMPORT = re.compile(r"from unittest\.mock import patch")
_MAMBA_DESCRIBE = re.compile(r'^with description\("([^"]+)"\)', re.MULTILINE)
_MAMBA_BLOCKS = {"description": "description", "describe": "description", "context": "context", "it": "it", "_it": "it"}
_SCRIPT_BLOCK = re.compile(r"\b(describe|context|it|test)\s*\(\s*(['\"`])((?:\\.|(?!\2).)*)\2")


def _mamba_node(item: ast.stmt, parent, order: int):
    """One `with <block>("name"):` statement as a Description, Context, or Observation (None otherwise)."""
    if not isinstance(item, ast.With) or not item.items:
        return None
    call = item.items[0].context_expr
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.args):
        return None
    kind = _MAMBA_BLOCKS.get(call.func.id)
    name = call.args[0].value if isinstance(call.args[0], ast.Constant) else ""
    if kind is None or not isinstance(name, str):
        return None
    node = _behavior_node(kind, parent, name, order, item.lineno, item.end_lineno or item.lineno)
    for child_order, child in enumerate(item.body, 1):
        _mamba_node(child, node, child_order)
    return node


def _behavior_node(kind: str, parent, name: str, order: int, line: int, end_line: int):
    if kind == "description" and parent is None:
        node = Description(name, order)
    elif kind == "it":
        node = Observation(name, order)
    else:
        node = Context(name, order)
    node.line, node.end_line = line, end_line
    if parent is not None:
        (parent.observations if isinstance(node, Observation) else parent.contexts).append(node)
    return node


def _script_blocks(text: str) -> list[tuple[str, int, int, str]]:
    """(kind, start line, end line, name) for every describe/it/test call whose body closes."""
    blocks = []
    for match in _SCRIPT_BLOCK.finditer(text):
        close = _closing_paren(text, text.index("(", match.start()))
        if close is None:
            continue
        start = text.count("\n", 0, match.start()) + 1
        blocks.append((match.group(1), start, text.count("\n", 0, close) + 1, match.group(3)))
    return blocks


def _closing_paren(text: str, open_index: int) -> int | None:
    depth = 0
    for index in range(open_index, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return index
    return None


def _nest_script_blocks(blocks: list[tuple[str, int, int, str]]) -> list:
    roots: list = []
    open_nodes: list = []
    for order, (kind, start, end, name) in enumerate(blocks, 1):
        while open_nodes and open_nodes[-1].end_line < start:
            open_nodes.pop()
        parent = open_nodes[-1] if open_nodes else None
        mapped = "it" if kind in {"it", "test"} else ("description" if kind == "describe" and parent is None else "context")
        node = _behavior_node(mapped, parent, name, order, start, end)
        if parent is None:
            roots.append(node)
        if not isinstance(node, Observation):
            open_nodes.append(node)
    return [node for node in roots if isinstance(node, Description)]


class MarkdownBddModel(BddModel):
    def render(self, canonical: BddModel, previous: str | None = None) -> str:
        return "\n\n".join(_render_sketch(item) for item in canonical.descriptions)


def _parse_sketch(text: str) -> list[Description]:
    descriptions: list[Description] = []
    description: Description | None = None
    stack: list[tuple[int, Context]] = []
    fence_lines: list[str] = []
    in_fence = False
    pending_surface: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("```"):
            if in_fence:
                _apply_fence_block(fence_lines, stack)
                fence_lines = []
                in_fence = False
            else:
                in_fence = True
            continue
        if in_fence:
            fence_lines.append(raw)
            continue
        if not stripped or stripped.startswith(("//", "#", "Fidelity:")):
            continue
        if stripped.startswith("->"):
            if _current_observation(stack) is None:
                pending_surface.append(stripped[2:].strip())
            else:
                _append_surface_line(stripped, stack)
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        level = indent // 2
        if stripped.startswith("it "):
            if not stack:
                continue
            observation = Observation(stripped[3:].strip(), len(stack[-1][1].observations) + 1)
            if pending_surface:
                observation.surface_lines = list(pending_surface)
                pending_surface = []
            stack[-1][1].observations.append(observation)
            continue
        pending_surface = []
        if level == 0:
            description = Description(stripped, len(descriptions) + 1)
            descriptions.append(description)
            stack = []
            continue
        if description is None:
            continue
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1].contexts if stack else description.contexts
        context = Context(stripped, len(parent) + 1)
        parent.append(context)
        stack.append((level, context))
    return descriptions


def _current_observation(stack: list[tuple[int, Context]]) -> Observation | None:
    if not stack:
        return None
    observations = stack[-1][1].observations
    return observations[-1] if observations else None


def _append_surface_line(stripped: str, stack: list[tuple[int, Context]]) -> None:
    observation = _current_observation(stack)
    if observation is None:
        return
    arrow = parse_arrow_line(stripped)
    payload = arrow[1] if arrow else stripped
    observation.surface_lines.append(payload)


def _apply_fence_block(lines: list[str], stack: list[tuple[int, Context]]) -> None:
    if not stack:
        return
    pending_surface: list[str] = []
    pending_graph: list[CallGraphEntry] = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if stripped.startswith("it "):
            observation = Observation(stripped[3:].strip(), len(stack[-1][1].observations) + 1)
            if pending_surface:
                observation.surface_lines = list(pending_surface)
                pending_surface = []
            if pending_graph:
                observation.call_graph = list(pending_graph)
                pending_graph = []
            stack[-1][1].observations.append(observation)
            continue
        arrow = parse_arrow_line(stripped)
        if arrow is not None:
            kind, payload = arrow
            depth = (len(raw) - len(raw.lstrip(" "))) // 2
            pending_graph.append(CallGraphEntry(depth=depth, kind=kind, text=payload))
            continue
        depth = (len(raw) - len(raw.lstrip(" "))) // 2
        pending_graph.append(CallGraphEntry(depth=depth, kind="call", text=stripped))


def _render_python(description: Description) -> str:
    lines = [
        "from mamba import description, context, it",
        "from expects import expect",
        "",
        f'with description("{_escape(description.name)}"):',
    ]
    if not description.contexts:
        lines.append("    pass")
    for child in description.contexts:
        lines.extend(_python_context(child, 1))
    return "\n".join(lines) + "\n"


def _python_context(node: Context, depth: int) -> list[str]:
    pad = "    " * depth
    lines = [f'{pad}with context("{_escape(node.name)}"):']
    body = False
    for observation in node.observations:
        body = True
        lines.append(f'{pad}    with it("{_escape(observation.name)}"):')
        lines.append(f"{pad}        # BDD: SIGNATURE")
    for child in node.contexts:
        body = True
        lines.extend(_python_context(child, depth + 1))
    if not body:
        lines.append(f"{pad}    pass")
    return lines


def _render_typescript(description: Description) -> str:
    lines = [
        'import { describe, it } from "vitest";',
        "",
        f'describe("{_escape(description.name)}", () => {{',
    ]
    if not description.contexts:
        lines.append("  // BDD: SIGNATURE")
    for child in description.contexts:
        lines.extend(_typescript_context(child, 1))
    lines.append("});")
    return "\n".join(lines) + "\n"


def _typescript_context(node: Context, depth: int) -> list[str]:
    pad = "  " * depth
    lines = [f'{pad}describe("{_escape(node.name)}", () => {{']
    for observation in node.observations:
        lines.append(f'{pad}  it("{_escape(observation.name)}", () => {{')
        lines.append(f"{pad}    // BDD: SIGNATURE")
        lines.append(f"{pad}  }});")
    for child in node.contexts:
        lines.extend(_typescript_context(child, depth + 1))
    if not node.observations and not node.contexts:
        lines.append(f"{pad}  // BDD: SIGNATURE")
    lines.append(f"{pad}}});")
    return lines


def _render_sketch(description: Description) -> str:
    lines = [description.name]
    for child in description.contexts:
        lines.extend(_sketch_context(child, 1))
    return "\n".join(lines) + "\n"


def _sketch_context(node: Context, depth: int) -> list[str]:
    pad = "  " * depth
    lines = [f"{pad}{node.name}"]
    for observation in node.observations:
        if observation.surface_lines or observation.call_graph:
            lines.append(f"{pad}  ```")
            for surface in observation.surface_lines:
                lines.append(f"{pad}  -> {surface}")
            if observation.call_graph:
                for graph_line in render_call_graph_block(observation.call_graph).splitlines():
                    lines.append(f"{pad}  {graph_line}")
            lines.append(f"{pad}  it {observation.name}")
            lines.append(f"{pad}  ```")
        else:
            lines.append(f"{pad}  it {observation.name}")
    for child in node.contexts:
        lines.extend(_sketch_context(child, depth + 1))
    return lines


def _escape(name: str) -> str:
    return name.replace("\\", "\\\\").replace('"', '\\"')
