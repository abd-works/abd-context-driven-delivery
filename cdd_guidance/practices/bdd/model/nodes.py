"""BDD node types: the describe tree a spec is read into, each node bound to the graph."""

from __future__ import annotations

import re
from typing import List, Optional, TypedDict

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
_MEMBER_CALL = re.compile(r"\.([\w$]+)\s*\(")
# A member read that is not a call: `ticketOn(page, OTHER).isLocked`, `stage.actions`.
_MEMBER_READ = re.compile(r"\.([\w$]+)\b(?!\s*\()")
_BARE_CALL = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")
# A tool called by its name, `<toolset>.<operation>`: `call("ticket.move_next", ticket="pet-visits")`.
_TOOL_NAMED = re.compile(r"""\b(\w+)\(\s*["']([a-z][a-z-]*)\.([a-zA-Z_]+)["']""")
_QUOTED = re.compile(r"""(['"`])(?:\\.|(?!\1).)*\1""")
_SPEC_STATE = re.compile(r"\bself\.(\w+)")
# A member reached through a name: `cart.total`, `order.pay(`.
_RECEIVED = re.compile(r"(?<![.\w$])([A-Za-z_$][\w$]*)\s*\.\s*([\w$]+)")
# A variable given a new object, `cart = Cart()` or `order = new Order(cart)`, or declared as one, `let cart: Cart`.
_BUILT = re.compile(r"(?<![.\w$])([A-Za-z_$][\w$]*)\s*(?::\s*[\w$.]+\s*)?=\s*(?:new\s+)?([A-Z][\w$]*)\s*\(")
_DECLARED = re.compile(r"\b(?:let|const|var)\s+([A-Za-z_$][\w$]*)\s*:\s*([A-Z][\w$]*)")


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


class Reach(TypedDict):
    """What a block's lines reach: every member name it calls or reads, in order; the names it only reads; each
    tool it calls by its name, as the call carrying it, the toolset, and the operation; the variables each member name
    is reached through; and the class each variable the lines build or declare is."""

    names: list[str]
    reads: list[str]
    tools: list[list[str]]
    receivers: dict[str, list[str]]
    builds: dict[str, str]


def reach_of(text: str) -> Reach:
    """What a block's lines reach, in the order they name it: every member name it calls or reads, which of those it
    only reads, and each tool it calls by its name (``call("ticket.move_next", ...)``) as the call carrying it, the
    toolset, and the operation. A mamba spec keeps its fixtures on `self`, so `self.project` is the spec's own state."""
    tools = [[match.group(1), match.group(2), match.group(3)] for match in _TOOL_NAMED.finditer(text)]
    code = _SPEC_STATE.sub(r"\1", _QUOTED.sub('""', text))
    calls = _MEMBER_CALL.findall(code) + _BARE_CALL.findall(code)
    found = [(match.start(1), match.group(1)) for pattern in (_MEMBER_CALL, _MEMBER_READ, _BARE_CALL) for match in pattern.finditer(code)]
    receivers: dict[str, list[str]] = {}
    for receiver, name in _RECEIVED.findall(code):
        if receiver not in receivers.setdefault(name, []):
            receivers[name].append(receiver)
    return {
        "names": list(dict.fromkeys(name for _start, name in sorted(found))),
        "reads": sorted(set(_MEMBER_READ.findall(code)) - set(calls)),
        "tools": tools,
        "receivers": receivers,
        "builds": dict(_DECLARED.findall(code) + _BUILT.findall(code)),
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
    graph_facts = (*BehaviorNode.graph_facts, "reach")

    def __init__(self, name: str, sequential_order: int = 1, graph: Graph | None = None) -> None:
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
