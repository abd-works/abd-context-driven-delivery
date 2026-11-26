"""BDD node types: the describe tree a spec is read into, each node bound to the graph."""

from __future__ import annotations

import re
from typing import List, Optional

from harness.graph.model_node import ModelChildren, ModelNode
from harness.graph.graph import Graph

from cdd_guidance.practices.source_code import CallGraph
from cdd_guidance.practices.source_code import CodeBody, WrittenBlock


_EXPECT_PRIVATE = re.compile(r"(?:expect\s*\([^)]*\._\w+|expect\([^)]*\)\.to\([^)]*\._\w+)")
_DIRECT_PRIVATE = re.compile(r"(?:result|output|instance|obj|subject|sut|actual|entity|self\.\w+)\s*\.\s*_\w+")
_PRIVATE_METHOD_CALL = re.compile(r"(?:result|output|instance|obj|subject|sut|entity)\s*\.\s*_\w+\s*\(")
_EXPECT = re.compile(r"\bexpect\s*\(")
_IMPLEMENTATION = re.compile(r"\b(mock|import|require)\b")
# Shared setup a describe or context runs before its observations: `with before.each:`, `beforeEach(`.
_SETUP_HOOK = re.compile(r"\bbefore(?:\.each|\.all|Each|All)\b")


def private_probe_in_text(text: str, start_line: int) -> dict:
    """First line that asserts on, reads, or calls a private member; empty when there is none."""
    for line_number, line in enumerate(text.splitlines(), start=start_line):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//")):
            continue
        if _EXPECT_PRIVATE.search(stripped):
            return {"line": line_number, "kind": "assertion reaches a private member"}
        if _DIRECT_PRIVATE.search(stripped):
            return {"line": line_number, "kind": "probe reads private state"}
        if _PRIVATE_METHOD_CALL.search(stripped):
            return {"line": line_number, "kind": "call reaches a private method"}
    return {}


class BehaviorNode(ModelNode):
    """A describe-tree node read from spec code. Knows its own source lines and loads the facts BDD rules read.

    `written` is how the block was spelled in the language it was read from, and `setup` the code above its first
    child, so a render into the same language can write both back."""

    graph_facts = ("expect_count", "has_implementation", "private_probe")

    def __init__(self, name: str, sequential_order: int = 1, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self.line = 0
        self.end_line = 0
        self.written: Optional[WrittenBlock] = None
        self.setup = CodeBody()

    def load_span_facts(self, span: str) -> None:
        """Fill the facts this node's own lines carry, and what its setup reaches: its lines after its own opening
        line, up to its first child. A line a child holds is the child's fact, so each hit is found on one node."""
        own, first_line = self.own_lines(span)
        self.expect_count = len(_EXPECT.findall(own))
        self.has_implementation = bool(_EXPECT.search(own) or _IMPLEMENTATION.search(own) or _SETUP_HOOK.search(own))
        self.private_probe = private_probe_in_text(own, first_line)

    def own_lines(self, span: str) -> tuple[str, int]:
        """The lines this block holds itself, with the number of the first: a describe's or context's setup."""
        return self._setup(span), (self.line or 1) + 1

    def _setup(self, span: str) -> str:
        first_child = min((child.line for child in self.children_blocks()), default=self.end_line + 1)
        return "\n".join(span.splitlines()[1 : first_child - self.line])

    def children_blocks(self) -> list:
        """The contexts and observations nested straight under this block."""
        return [*getattr(self, "contexts", []), *getattr(self, "observations", [])]


class DescribeBlock(BehaviorNode):
    """A describe or a context: a block that holds contexts and observations, each added through it."""

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.contexts = ModelChildren(self, "contexts")
        # Spec code often puts `it` straight under the outermost describe.
        self.observations = ModelChildren(self, "observations")

    def add_child(self, kind: str, name: str, order: int | None = None) -> "Context | Observation":
        """A new context (kind ``context``) or observation (kind ``it``) named name, added under this block. order is
        its place among this block's children as its file has them; by default it comes after every child it has."""
        order = order or len(self.contexts) + len(self.observations) + 1
        if kind == "it":
            observation = Observation(name, order)
            self.observations.append(observation)
            return observation
        context = Context(name, order)
        self.contexts.append(context)
        return context

    def children_in_order(self) -> "list[Context | Observation]":
        """Its contexts and observations in the order its file has them, which every format writes them in. Children
        built with no place of their own keep the observations above the contexts."""
        return sorted(self.children_blocks(), key=lambda child: (child.sequential_order, isinstance(child, DescribeBlock)))


class Description(DescribeBlock):
    _semantic_type_name = "Description"
    _belongs = {("Context", "Description"), ("Observation", "Description"), ("Description", "Spec")}


class Context(DescribeBlock):
    _semantic_type_name = "Context"
    _belongs = {("Observation", "Context"), ("Context", "Context"), ("Context", "Description")}


class Observation(BehaviorNode):
    _semantic_type_name = "Observation"

    def __init__(self, name: str, sequential_order: int = 1, graph: Graph | None = None) -> None:
        super().__init__(name=name, sequential_order=sequential_order, graph=graph)
        self.call_graph = CallGraph()
        self.surface_lines: List[str] = []
        self.body = CodeBody()

    def own_lines(self, span: str) -> tuple[str, int]:
        """An observation holds every line of its span: it has no child."""
        return span, self.line or 1
