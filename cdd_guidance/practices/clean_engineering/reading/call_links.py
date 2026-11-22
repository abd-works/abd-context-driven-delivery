"""The edges one read of the code draws between the members and classes it added: each call and read to the member its
receiver names, each class to the class it extends, and each class a model document describes to the class in code
that implements it. Each name is resolved by the file it is written in (*CodeFile*), never to every node of that
name."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harness.graph.schema_conformance import EXEMPT_FACT

from cdd_guidance.practices.clean_engineering.reading.code_file import CodeSpan
from cdd_guidance.practices.clean_engineering.reading.code_read import DESCRIBED_FACT

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.graph_reading import GraphReading

_ABSTRACT_MARK = re.compile(r"@abstractmethod|^\s*(?:public\s+|protected\s+)?abstract\s", re.MULTILINE)
_DOCSTRING = re.compile(r'(?s)\A\s*(?:"""|\'\'\').*?(?:"""|\'\'\')')
# The marker the source view puts after a line for each call on it, `/* call:show */`, which is no code.
_CALL_MARKER = re.compile(r"\s*/\* call:[^*]*\*/")
_NO_BODY = {"", "...", "pass", "raise NotImplementedError", "raise NotImplementedError()"}


class ClassLinks:
    """The edges between the classes the graph holds: each class to the class it extends (``baseClass``), and each
    class in code to the class a model document of its own module describes under its name (``implements``), so the
    design and the code that implements it are two nodes a reader walks between."""

    def __init__(self, reading: "GraphReading") -> None:
        self._graph = reading.graph
        self._in_graph = reading.in_graph
        self._index = reading.code_index

    def link(self) -> None:
        classes = list(self._in_graph.nodes("OoadClass"))
        described = [node for node in classes if node.has_fact(DESCRIBED_FACT)]
        for node in classes:
            for base in node.get_fact("bases") or []:
                extended = self._index.file(node.source.file).class_named(str(base).split("[")[0].split("<")[0].strip())
                if extended is not None and extended is not node:
                    self._graph.edges.relate("baseClass", node, extended)
            if not node.has_fact(DESCRIBED_FACT):
                design = self._design_of(node, described)
                if design is not None:
                    self._graph.edges.relate("implements", node, design)

    def _design_of(self, coded: "Node", described: "list[Node]") -> "Node | None":
        """The class a model document describes under coded's name, from the nearest folder at or above coded's file
        whose document describes one; none when no document above it does."""
        found = [
            (len(folder), node) for node in described
            if node.name == coded.name
            for folder in [self._described_folder(node)]
            if not folder or coded.source.file.startswith(f"{folder}/")
        ]
        return max(found, key=lambda pair: pair[0])[1] if found else None

    def _described_folder(self, design: "Node") -> str:
        """The folder a model document describes, the one holding its `.context`; empty for the source root."""
        parts = design.source.file.split("/")[:-2]
        return "/".join(parts)


class CallLinks:
    """The ``invokes`` edges of the code read: each operation and property to the operations it calls and the
    properties it reads, each found on the class its receiver is: the caller's own class for `self` and `this`, the
    class it extends for `super()`, the type of a field, a parameter, or a local for any other object, and the class
    the file declares or imports for a class named outright. A call whose receiver's class the code does not say is
    joined to nothing. The file the member is written in reads its body (``CodeFile.members_called_in``)."""

    def __init__(self, reading: "GraphReading") -> None:
        self._reading = reading
        self._graph = reading.graph
        self._index = reading.code_index

    def link(self) -> None:
        """Record an ``invokes`` edge from every member the graph holds to each member it calls."""
        in_graph = self._reading.in_graph
        for caller in [*in_graph.nodes("Operation"), *in_graph.nodes("Property")]:
            called = [member for member in self._index.file(caller.source.file).members_called_in(self._span_of(caller)) if member is not caller]
            for member in called:
                self._graph.edges.relate("invokes", caller, member)
            if not called and self._calls_nothing_by_design(caller):
                caller.set_fact(EXEMPT_FACT, ["invokes"])

    def _span_of(self, caller: "Node") -> CodeSpan:
        """The caller's own code, the class that declares it, and the type hint of each of its parameters."""
        text = CodeSpan.code_of(caller.source.text) if caller.source.file else ""
        typed = {edge.child.name: str(edge.child.get_fact("type_hint") or "") for edge in self._graph.edges.from_parent("hasParameter", caller)}
        return CodeSpan(text, self._class_declaring(caller), typed)

    def _class_declaring(self, member: "Node") -> "Node | None":
        owner = member.get_fact("owner")
        return next((node for node in self._index.classes_named(owner) if node.source.file == member.source.file), None) if owner else None

    def _calls_nothing_by_design(self, caller: "Node") -> bool:
        """Whether caller is a member that has nothing to call: an abstract one, whose subclasses do the work, or one
        that takes nothing and answers a value, which is a property in all but name."""
        return self._is_abstract(caller) or not self._graph.edges.from_parent("hasParameter", caller)

    def _is_abstract(self, caller: "Node") -> bool:
        """An abstract member: marked so (`@abstractmethod`, `abstract`), or with no body but `...`, `pass`, or a raise of
        NotImplementedError under its signature and docstring."""
        text = caller.source.text if caller.source.file else ""
        if _ABSTRACT_MARK.search(text) or self._declared_without_body(text):
            return True
        return _DOCSTRING.sub("", self._python_body(text)).strip() in _NO_BODY

    def _declared_without_body(self, text: str) -> bool:
        """A C-family member with no body: its signature ends in `;` and no brace opens a body (an interface's method,
        `draw(scale: number): void;`)."""
        code = _CALL_MARKER.sub("", text).strip()
        return bool(code) and "{" not in code and code.endswith(";")

    def _python_body(self, text: str) -> str:
        """What follows a Python member's signature, the line that ends its `def` with a colon; none for other code."""
        lines = text.splitlines()
        if not any(line.lstrip().startswith(("def ", "async def ")) for line in lines[:4]):
            return ""
        end = next((index for index, line in enumerate(lines) if line.rstrip().endswith(":")), len(lines))
        return "\n".join(lines[end + 1:])
