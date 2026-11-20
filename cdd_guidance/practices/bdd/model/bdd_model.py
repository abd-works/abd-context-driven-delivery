"""Canonical BDD describe tree — parse and render a sketch. Code channels live in code_spec_model."""

from __future__ import annotations

import re

from harness.graph.model_node import ModelChildren, ModelNode
from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraph, parse_arrow_line
from cdd_guidance.practices.bdd.model.nodes import Context, Description, Observation, private_probe_in_text
from cdd_guidance.practices.bdd.model.spec_source import has_signature_marker, is_developed
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody


class BddModel(ModelNode):
    _semantic_type_name = "Spec"
    graph_facts = (
        "patches_infrastructure",
        "signature_marker",
        "developed",
        "top_level_describes",
        "private_probe",
        "imported_classes",
    )
    _belongs = {("Description", "Spec")}

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
        self.descriptions = []
        _SketchReader(self).read(text)
        return self

    def add_child(self, kind: str, name: str, order: int | None = None) -> Description:
        """A new outermost describe named name, after the others unless order places it. Every block at the top of a
        spec is a description, whatever kind its file wrote it as, so kind only matches DescribeBlock.add_child."""
        description = Description(name, order or len(self.descriptions) + 1)
        self.descriptions.append(description)
        return description

    def parse_code(self, text: str) -> "BddModel":
        """Read the describe tree out of spec code; each language model knows its own syntax."""
        return self

    def load_source_facts(self, text: str) -> None:
        """Fill the facts the whole spec file owns. Its private probe is one in the lines no describe holds, since each
        describe keeps the probes in its own lines."""
        self.patches_infrastructure = bool(_PATCH_DECORATOR.search(text) or _MOCK_PATCH_IMPORT.search(text))
        self.signature_marker = has_signature_marker(text)
        self.developed = is_developed(text)
        self.top_level_describes = [description.name for description in self.descriptions]
        described = {number for description in self.descriptions for number in range(description.line, description.end_line + 1)}
        outside = "\n".join("" if number in described else line for number, line in enumerate(text.splitlines(), start=1))
        self.private_probe = private_probe_in_text(outside, 1)

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
        return "\n".join([description.name, *self._children_lines(description, "")]) + "\n"

    def _children_lines(self, block: Description | Context, pad: str) -> list[str]:
        """The block's observations and contexts one level under it, in the order its file has them. Each observation
        is a fenced block when it carries a realization, else its line."""
        inner = f"{pad}  "
        lines: list[str] = []
        for child in block.children_in_order():
            if isinstance(child, Context):
                lines.extend([f"{inner}{child.name}", *self._children_lines(child, inner)])
            elif child.surface_lines or child.call_graph:
                lines.extend(self._realized_lines(child, inner))
            else:
                lines.append(f"{inner}it {child.name}")
        return lines

    def _realized_lines(self, observation: Observation, pad: str) -> list[str]:
        """The fenced block of an observation that carries a realization: its surface lines, its call graph, its name."""
        graph_lines = observation.call_graph.block().splitlines() if observation.call_graph else []
        return [
            f"{pad}```",
            *(f"{pad}-> {surface}" for surface in observation.surface_lines),
            *(f"{pad}{graph_line}" for graph_line in graph_lines),
            f"{pad}it {observation.name}",
            f"{pad}```",
        ]

    def node_at(self, path: tuple) -> BddModel | Description | Context | Observation | None:
        """The block at this path of names, the spec itself at the empty path; None when this spec has no such block."""
        found, children = self, list(self.descriptions)
        for name in path:
            found = next((child for child in children if child.name == name), None)
            if found is None:
                return None
            children = list(getattr(found, "contexts", [])) + list(getattr(found, "observations", []))
        return found


_PATCH_DECORATOR = re.compile(r"^\s*@patch\s*\(", re.MULTILINE)
_MOCK_PATCH_IMPORT = re.compile(r"from unittest\.mock import patch")


class _SketchReader:
    """Reads one sketch's indented describe tree. It keeps what a read tracks from line to line: the contexts still
    open, the fenced realization being collected, and surface lines waiting for the observation below them."""

    def __init__(self, spec: BddModel) -> None:
        self.spec = spec
        self._description: Description | None = None
        self._open: list[tuple[int, Context]] = []
        self._fence: list[str] | None = None
        self._pending_surface: list[str] = []

    def read(self, text: str) -> None:
        for raw in text.splitlines():
            self._read_line(raw)

    def _read_line(self, raw: str) -> None:
        stripped = raw.strip()
        if stripped.startswith("```"):
            self._toggle_fence(raw)
            return
        if self._fence is not None:
            self._fence.append(raw)
            return
        if not stripped or stripped.startswith(("//", "#", "Fidelity:")):
            return
        if stripped.startswith("->"):
            self._read_surface(stripped)
            return
        if stripped.startswith("it "):
            self._read_observation(stripped[3:].strip(), self._level(raw))
            return
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
        """Each `it` in the fence takes the call-graph lines above it as its realization, each at its depth under the
        fence's own margin, and the lines indented under it as its surface lines."""
        owner, lines, self._fence = self._owner(), self._fence or [], None
        written = [raw for raw in lines if raw.strip() and not raw.strip().startswith("//")]
        if owner is None or not written:
            return
        margin = min(self._level(raw) for raw in written)
        call_graph, observation, observed_at = CallGraph(), None, 0
        for raw in written:
            stripped, level = raw.strip(), self._level(raw) - margin
            if stripped.startswith("it "):
                observation, observed_at = owner.add_child("it", stripped[3:].strip()), level
                observation.call_graph, call_graph = call_graph, CallGraph()
            elif observation is not None and level > observed_at:
                arrow = parse_arrow_line(stripped)
                observation.surface_lines.append(arrow[1] if arrow else stripped)
            else:
                observation = None
                call_graph.add_line(stripped, level)

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
        observation = owner.add_child("it", name)
        observation.surface_lines, self._pending_surface = self._pending_surface, []

    def _read_block(self, name: str, level: int) -> None:
        """A line at the margin opens a description; an indented line opens a context inside the nearest open block."""
        if level == 0:
            self._description = self.spec.add_child("description", name)
            self._open = []
            return
        if self._description is None:
            return
        self._close_to(level)
        holder = self._open[-1][1] if self._open else self._description
        self._open.append((level, holder.add_child("context", name)))

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
