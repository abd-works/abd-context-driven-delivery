"""Canonical BDD describe tree — parse and render a sketch. Code channels live in code_spec_model."""

from __future__ import annotations

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
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody


class BddModel(BoundNode):
    _graph_practice = "bdd"
    _semantic_type_name = "Spec"
    _belongs = {("Description", "Spec")}

    def __init__(self, graph: Graph | None = None) -> None:
        super().__init__("spec", 0, graph)
        self.preamble = CodeBody()
        self.written = None
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
        return "\n\n".join(self._sketch_lines(item) for item in canonical.descriptions)

    def _sketch_lines(self, description: Description) -> str:
        lines = [description.name]
        for child in description.contexts:
            lines.extend(self._sketch_context(child, 1))
        return "\n".join(lines) + "\n"

    def _sketch_context(self, node: Context, depth: int) -> list[str]:
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
            lines.extend(self._sketch_context(child, depth + 1))
        return lines

    def setup_at(self, path: tuple) -> CodeBody:
        """The setup read for the describe at this path of names; empty when this spec has none."""
        node = self._node_at(path)
        return getattr(node, "setup", CodeBody()) if node is not None else CodeBody()

    def body_at(self, path: tuple) -> CodeBody:
        """The test body read for the it at this path of names; empty when this spec has none."""
        node = self._node_at(path)
        return getattr(node, "body", CodeBody()) if node is not None else CodeBody()

    def written_at(self, path: tuple):
        """How the block at this path of names was written; None when this spec has no such block."""
        node = self._node_at(path)
        return node.written if node is not None else None

    def _node_at(self, path: tuple):
        found, children = None, list(self.descriptions)
        for name in path:
            found = next((child for child in children if child.name == name), None)
            if found is None:
                return None
            children = list(getattr(found, "contexts", [])) + list(getattr(found, "observations", []))
        return found


_PATCH_DECORATOR = re.compile(r"^\s*@patch\s*\(", re.MULTILINE)
_MOCK_PATCH_IMPORT = re.compile(r"from unittest\.mock import patch")
_MAMBA_DESCRIBE = re.compile(r'^with description\("([^"]+)"\)', re.MULTILINE)


class MarkdownBddModel(BddModel):
    pass


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
