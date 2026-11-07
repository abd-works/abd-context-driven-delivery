"""Canonical BDD describe tree — parse and render a sketch. Code channels live in code_spec_model."""

from __future__ import annotations

import re

from harness.graph.model_node import ModelChildren, ModelNode
from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.call_graph import (
    CallGraphEntry,
    parse_arrow_line,
    render_call_graph_block,
)
from cdd_guidance.practices.bdd.model.nodes import Context, Description, Observation
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody


class BddModel(ModelNode):
    _semantic_type_name = "Spec"
    graph_facts = ("patches_infrastructure", "signature_marker", "top_level_describes", "code_like_describe_lines", "private_probe")
    _belongs = {("Description", "Spec")}

    @classmethod
    def practice_kind(cls) -> type:
        from cdd_guidance.practices.bdd.bdd import Bdd

        return Bdd

    def __init__(self, graph: Graph | None = None) -> None:
        super().__init__("spec", 0, graph)
        self.preamble = CodeBody()
        self.written = None
        self._descriptions = ModelChildren(self, "descriptions")

    @property
    def descriptions(self) -> list[Description]:
        return self._descriptions

    @descriptions.setter
    def descriptions(self, descriptions: list[Description]) -> None:
        self._descriptions.refill(descriptions)


    def parse(self, text: str) -> "BddModel":
        self.descriptions = _SketchReader().read(text)
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
        # Spec code often puts `it` straight under the outermost describe, so those observations come before its contexts.
        lines = [description.name, *self._observation_lines(description.observations, "")]
        for child in description.contexts:
            lines.extend(self._sketch_context(child, 1))
        return "\n".join(lines) + "\n"

    def _sketch_context(self, node: Context, depth: int) -> list[str]:
        pad = "  " * depth
        lines = [f"{pad}{node.name}", *self._observation_lines(node.observations, pad)]
        for child in node.contexts:
            lines.extend(self._sketch_context(child, depth + 1))
        return lines

    def _observation_lines(self, observations, pad: str) -> list[str]:
        """Each observation one level under its parent: a fenced block when it carries a realization, else its line."""
        lines: list[str] = []
        for observation in observations:
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


class _SketchReader:
    """Reads one sketch's indented describe tree. It keeps what a read tracks from line to line: the contexts still
    open, the fenced realization being collected, and surface lines waiting for the observation below them."""

    def __init__(self) -> None:
        self.descriptions: list[Description] = []
        self._description: Description | None = None
        self._open: list[tuple[int, Context]] = []
        self._fence: list[str] | None = None
        self._pending_surface: list[str] = []

    def read(self, text: str) -> list[Description]:
        for raw in text.splitlines():
            self._read_line(raw)
        return self.descriptions

    def _read_line(self, raw: str) -> None:
        stripped = raw.strip()
        if stripped.startswith("```"):
            self._toggle_fence(raw)
        elif self._fence is not None:
            self._fence.append(raw)
        elif not stripped or stripped.startswith(("//", "#", "Fidelity:")):
            return
        elif stripped.startswith("->"):
            self._read_surface(stripped)
        elif stripped.startswith("it "):
            self._read_observation(stripped[3:].strip(), self._level(raw))
        else:
            self._pending_surface = []
            self._read_block(stripped, self._level(raw))

    def _toggle_fence(self, raw: str) -> None:
        if self._fence is not None:
            self._close_fence()
            return
        # An indented fence belongs to the node one level above it, so a fence one level under the description holds
        # the description's own observations. A fence at the margin belongs to the innermost open context.
        fence_level = self._level(raw)
        if fence_level:
            self._close_to(fence_level)
        self._fence = []

    def _close_fence(self) -> None:
        """Each `it` in the fence takes the call-graph lines above it as its realization."""
        owner, lines, self._fence = self._owner(), self._fence or [], None
        if owner is None:
            return
        call_graph: list[CallGraphEntry] = []
        for raw in lines:
            stripped = raw.strip()
            if not stripped or stripped.startswith("//"):
                continue
            if stripped.startswith("it "):
                observation = Observation(stripped[3:].strip(), len(owner.observations) + 1)
                observation.call_graph, call_graph = call_graph, []
                owner.observations.append(observation)
                continue
            call_graph.append(self._call_graph_entry(raw, stripped))

    def _call_graph_entry(self, raw: str, stripped: str) -> CallGraphEntry:
        """An arrow line keeps its direction; any other line is a call."""
        kind, payload = parse_arrow_line(stripped) or ("call", stripped)
        return CallGraphEntry(depth=self._level(raw), kind=kind, text=payload)

    def _read_surface(self, stripped: str) -> None:
        """A surface line belongs to the observation above it; before any observation it waits for the next one."""
        observation = self._current_observation()
        if observation is None:
            self._pending_surface.append(stripped[2:].strip())
            return
        arrow = parse_arrow_line(stripped)
        observation.surface_lines.append(arrow[1] if arrow else stripped)

    def _read_observation(self, name: str, level: int) -> None:
        # An `it` one level under a context belongs to it; one level under the description belongs to the description.
        self._close_to(level)
        owner = self._owner()
        if owner is None:
            return
        observation = Observation(name, len(owner.observations) + 1)
        observation.surface_lines, self._pending_surface = self._pending_surface, []
        owner.observations.append(observation)

    def _read_block(self, name: str, level: int) -> None:
        """A line at the margin opens a description; an indented line opens a context inside the nearest open block."""
        if level == 0:
            self._description = Description(name, len(self.descriptions) + 1)
            self.descriptions.append(self._description)
            self._open = []
            return
        if self._description is None:
            return
        self._close_to(level)
        siblings = self._open[-1][1].contexts if self._open else self._description.contexts
        context = Context(name, len(siblings) + 1)
        siblings.append(context)
        self._open.append((level, context))

    def _close_to(self, level: int) -> None:
        while self._open and self._open[-1][0] >= level:
            self._open.pop()

    def _owner(self) -> Context | Description | None:
        """The node the next observation belongs to: the innermost open context, else the description itself."""
        return self._open[-1][1] if self._open else self._description

    def _current_observation(self) -> Observation | None:
        owner = self._owner()
        if owner is None or not owner.observations:
            return None
        return owner.observations[-1]

    def _level(self, raw: str) -> int:
        """Two spaces of indent per level."""
        return (len(raw) - len(raw.lstrip(" "))) // 2
