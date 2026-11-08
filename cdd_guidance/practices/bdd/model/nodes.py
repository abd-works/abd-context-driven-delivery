"""BDD node types: the describe tree a spec is read into, each node bound to the graph."""

from __future__ import annotations

import re
from typing import List, Optional

from harness.graph.model_node import ModelChildren, ModelNode
from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraph
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, WrittenBlock


_EXPECT_PRIVATE = re.compile(r"(?:expect\s*\([^)]*\._\w+|expect\([^)]*\)\.to\([^)]*\._\w+)")
_DIRECT_PRIVATE = re.compile(r"(?:result|output|instance|obj|subject|sut|actual|entity|self\.\w+)\s*\.\s*_\w+")
_PRIVATE_METHOD_CALL = re.compile(r"(?:result|output|instance|obj|subject|sut|entity)\s*\.\s*_\w+\s*\(")
_EXPECT = re.compile(r"\bexpect\s*\(")
_IMPLEMENTATION = re.compile(r"\b(mock|import|require)\b")
# Shared setup a describe or context runs before its observations: `with before.each:`, `beforeEach(`.
_SETUP_HOOK = re.compile(r"\bbefore(?:\.each|\.all|Each|All)\b")
_MEMBER_CALL = re.compile(r"\.([\w$]+)\s*\(")
# A member read that is not a call: `ticketOn(page, OTHER).isLocked`, `stage.actions`.
_MEMBER_READ = re.compile(r"\.([\w$]+)\b(?!\s*\()")
_BARE_CALL = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")
# A tool called by its name, `<toolset>.<operation>`: `call("ticket.move_next", ticket="pet-visits")`.
_TOOL_NAMED = re.compile(r"""\b(\w+)\(\s*["']([a-z][a-z-]*)\.([a-zA-Z_]+)["']""")
_QUOTED = re.compile(r"""(['"`])(?:\\.|(?!\1).)*\1""")
_SPEC_STATE = re.compile(r"\bself\.(\w+)")


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


def reach_of(text: str) -> dict:
    """What a block's lines reach, in the order they name it: every member name it calls or reads, which of those it
    only reads, and each tool it calls by its name (``call("ticket.move_next", ...)``) as the call carrying it, the
    toolset, and the operation. A mamba spec keeps its fixtures on `self`, so `self.project` is the spec's own state."""
    tools = [[match.group(1), match.group(2), match.group(3)] for match in _TOOL_NAMED.finditer(text)]
    code = _SPEC_STATE.sub(r"\1", _QUOTED.sub('""', text))
    calls = _MEMBER_CALL.findall(code) + _BARE_CALL.findall(code)
    found = [(match.start(1), match.group(1)) for pattern in (_MEMBER_CALL, _MEMBER_READ, _BARE_CALL) for match in pattern.finditer(code)]
    return {
        "names": list(dict.fromkeys(name for _start, name in sorted(found))),
        "reads": sorted(set(_MEMBER_READ.findall(code)) - set(calls)),
        "tools": tools,
    }


class BehaviorNode(ModelNode):
    """A describe-tree node read from spec code. Knows its own source lines and loads the facts BDD rules read.

    `written` is how the block was spelled in the language it was read from, and `setup` the code above its first
    child, so a render into the same language can write both back."""

    graph_facts = ("expect_count", "has_implementation", "private_probe", "setup_reach")

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
        self.setup_reach = reach_of(self._setup(span))

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
        its place among this block's children as its file has them; by default it comes after the others of its kind."""
        if kind == "it":
            observation = Observation(name, order or len(self.observations) + 1)
            self.observations.append(observation)
            return observation
        context = Context(name, order or len(self.contexts) + 1)
        self.contexts.append(context)
        return context


class Description(DescribeBlock):
    _semantic_type_name = "Description"
    _belongs = {("Context", "Description"), ("Observation", "Description"), ("Description", "Spec")}


class Context(DescribeBlock):
    _semantic_type_name = "Context"
    _belongs = {("Observation", "Context"), ("Context", "Context"), ("Context", "Description")}


class Observation(BehaviorNode):
    _semantic_type_name = "Observation"
    graph_facts = (*BehaviorNode.graph_facts, "reach")

    def __init__(self, name: str, sequential_order: int = 1, graph=None) -> None:
        super().__init__(name=name, sequential_order=sequential_order, graph=graph)
        self.call_graph = CallGraph()
        self.surface_lines: List[str] = []
        self.body = CodeBody()

    def load_span_facts(self, span: str) -> None:
        """An observation also keeps what its whole span reaches, which its realization starts from."""
        super().load_span_facts(span)
        self.reach = reach_of(span)

    def own_lines(self, span: str) -> tuple[str, int]:
        """An observation holds every line of its span: it has no child."""
        return span, self.line or 1
