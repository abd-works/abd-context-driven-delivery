"""BDD node types — specialise the Stories StoryNode base."""

from __future__ import annotations

import re
from typing import List

from harness.graph.bound_node import BoundChildren

from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraphEntry
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, WrittenBlock
from cdd_guidance.practices.stories.model.story_model import StoryNode


_EXPECT_PRIVATE = re.compile(r"(?:expect\s*\([^)]*\._\w+|expect\([^)]*\)\.to\([^)]*\._\w+)")
_DIRECT_PRIVATE = re.compile(r"(?:result|output|instance|obj|subject|sut|actual|entity|self\.\w+)\s*\.\s*_\w+")
_PRIVATE_METHOD_CALL = re.compile(r"(?:result|output|instance|obj|subject|sut|entity)\s*\.\s*_\w+\s*\(")
_EXPECT = re.compile(r"\bexpect\s*\(")
_IMPLEMENTATION = re.compile(r"\b(mock|import|require)\b")


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


class BehaviorNode(StoryNode):
    """A describe-tree node read from spec code. Knows its own source lines and loads the facts BDD rules read."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.line = 0
        self.end_line = 0

    def load_span_facts(self, span: str) -> None:
        """Fill the facts this node's own source lines carry."""
        self.expect_count = len(_EXPECT.findall(span))
        self.has_implementation = bool(_EXPECT.search(span) or _IMPLEMENTATION.search(span))
        self.private_probe = private_probe_in_text(span, self.line or 1)


class Description(BehaviorNode):
    _semantic_type_name = "Description"
    _graph_practice = "bdd"
    _belongs = {("Context", "Description"), ("Observation", "Description"), ("Description", "Spec")}

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.contexts = BoundChildren(self, "contexts")
        # Spec code often puts `it` straight under the outermost describe.
        self.observations = BoundChildren(self, "observations")

    def clone(self) -> "Description":
        cloned = type(self)(self.name, self.sequential_order)
        cloned.take_code_from(self)
        for context in self.contexts:
            cloned.contexts.append(context.clone())
        for observation in self.observations:
            cloned.observations.append(observation.clone())
        return cloned

    def load_context(self, source: "Context") -> "Context":
        return source.clone()


class Context(BehaviorNode):
    _semantic_type_name = "Context"
    _graph_practice = "bdd"
    _belongs = {("Observation", "Context"), ("Context", "Context"), ("Context", "Description")}

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.observations = BoundChildren(self, "observations")
        self.contexts = BoundChildren(self, "contexts")

    def clone(self) -> "Context":
        cloned = type(self)(self.name, self.sequential_order)
        cloned.take_code_from(self)
        for observation in self.observations:
            cloned.observations.append(observation.clone())
        for context in self.contexts:
            cloned.contexts.append(context.clone())
        return cloned

    def load_observation(self, source: "Observation") -> "Observation":
        return source.clone()

    def load_context(self, source: "Context") -> "Context":
        return source.clone()


class Observation(BehaviorNode):
    _semantic_type_name = "Observation"
    _graph_practice = "bdd"

    def __init__(self, name: str, sequential_order: int = 1, graph=None) -> None:
        super().__init__(name=name, sequential_order=sequential_order, graph=graph)
        self.call_graph: List[CallGraphEntry] = []
        self.surface_lines: List[str] = []
        self.body = CodeBody()

    def clone(self) -> "Observation":
        cloned = type(self)(self.name, self.sequential_order)
        cloned.take_code_from(self)
        cloned.call_graph = list(self.call_graph)
        cloned.surface_lines = list(self.surface_lines)
        return cloned
