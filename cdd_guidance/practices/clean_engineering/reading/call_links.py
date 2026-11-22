"""The edges one read of the code draws between the members and classes it added: each call and read to the member its
receiver names, each class to the class it extends, and each class a model document describes to the class in code
that implements it. Each name is resolved by the file it is written in (*CodeFile*), never to every node of that
name."""

from __future__ import annotations

import re
from collections import Counter
from typing import TYPE_CHECKING

from harness.graph.schema_conformance import EXEMPT_FACT

from cdd_guidance.practices.clean_engineering.reading.code_file import (
    CREATED_IN_THE_CONSTRUCTOR,
    CREATED_ON_EACH_CALL,
    HELD_AS_A_FIELD,
    JOINED_BY_A_GUESS,
    JOINED_FACT,
    REACHED_FACT,
    THROUGH_FACT,
)
from cdd_guidance.practices.clean_engineering.reading.receiver_causes import UNRESOLVED_CALLS_FACTS
from cdd_guidance.practices.clean_engineering.reading.code_read import DESCRIBED_FACT

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.graph_reading import GraphReading

_ABSTRACT_MARK = re.compile(r"@abstractmethod|^\s*(?:public\s+|protected\s+)?abstract\s", re.MULTILINE)
_DOCSTRING = re.compile(r'(?s)\A\s*(?:"""|\'\'\').*?(?:"""|\'\'\')')
# The marker the source view puts after a line for each call on it, `/* call:show */`, which is no code.
_CALL_MARKER = re.compile(r"\s*/\* call:[^*]*\*/")
_NO_BODY = {"", "...", "pass", "raise NotImplementedError", "raise NotImplementedError()"}
# The relationships a class has with the class a field of its holds, each its own kind of edge, as the schema names them.
_FIELD_RELATIONSHIPS = ("composition", "aggregation", "association")


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


class FieldLinks:
    """The relationship each class of the code has with the class each of its fields holds, private or public, typed by
    its hint or by what its constructor or initializer assigns it: a part the class builds itself is a composition
    (``composition``), many members it is handed an aggregation (``aggregation``), and one collaborator it is handed an
    association (``association``). The class depends on each, held as a field. A relationship a person wrote on a
    property stands, and a class a model document describes keeps only those. Made after the calls are linked, since
    whether a class builds a part is what its dependency on the part keeps."""

    def __init__(self, reading: "GraphReading") -> None:
        self._graph = reading.graph
        self._in_graph = reading.in_graph
        self._answers = reading.code_index.answers

    def link(self) -> None:
        for holder in self._in_graph.nodes("OoadClass"):
            if not holder.has_fact(DESCRIBED_FACT):
                for name in holder.get_fact("held_fields") or {}:
                    self._link_field(holder, name)

    def _link_field(self, holder: "Node", name: str) -> None:
        held = self._answers.held_in(holder, name)
        part = held.class_held if held is not None else None
        if part is None or part is holder:
            return
        self._graph.edges.relate("dependsOn", holder, part, {REACHED_FACT: [HELD_AS_A_FIELD], THROUGH_FACT: [name]})
        if not any(self._related(kind, holder, part) for kind in _FIELD_RELATIONSHIPS):
            self._graph.edges.relate(self._kind_of(holder, part, held.is_many), holder, part)

    def _related(self, kind: str, holder: "Node", part: "Node") -> bool:
        return any(edge.child is part for edge in self._graph.edges.from_parent(kind, holder))

    def _kind_of(self, holder: "Node", part: "Node", many: bool) -> str:
        """Composition when the holder's own code builds the part, aggregation when it is handed many, else
        association."""
        dependency = next((edge for edge in self._graph.edges.from_parent("dependsOn", holder) if edge.child is part), None)
        reached = set(dependency.facts.get(REACHED_FACT, [])) if dependency is not None else set()
        if reached & {CREATED_ON_EACH_CALL, CREATED_IN_THE_CONSTRUCTOR}:
            return "composition"
        return "aggregation" if many else "association"


class CallLinks:
    """The ``invokes`` edges of the code read: each operation and property to the operations it calls and the
    properties it reads, each found on the class its receiver is: the caller's own class for `self` and `this`, the
    class it extends for `super()`, the type of a field, a parameter, or a local for any other object, and the class
    the file declares or imports for a class named outright. A receiver of no known class reaches the one member of
    the name the file's reach declares, and that edge keeps that it was joined by a guess (``joined``). A call no class
    can be told for is joined to nothing, and counted on its class by why (``unresolved_calls_on_outside_objects``,
    ``unresolved_calls_on_untyped_values``, ``unresolved_calls_otherwise``). Each class depends on each other class its
    members create, call, read, or name as a value (``dependsOn``), and the edge keeps how it reaches that class
    (``reached``) and the members that do (``through``). The file the member is written in reads its body
    (``CodeFile.reach_of``)."""

    def __init__(self, reading: "GraphReading") -> None:
        self._reading = reading
        self._graph = reading.graph
        self._index = reading.code_index

    def link(self) -> None:
        """Record an ``invokes`` edge from every member the graph holds to each member it calls, and a ``dependsOn``
        edge from its class to each other class it reaches, and count on each class, by cause, the calls it could not
        join."""
        in_graph = self._reading.in_graph
        unjoined: dict[int, Counter] = {id(node): Counter() for node in in_graph.nodes("OoadClass")}
        for caller in [*in_graph.nodes("Operation"), *in_graph.nodes("Property")]:
            reach = self._index.file(caller.source.file).reach_of(self._index.span_of(caller))
            called = [member for member in dict.fromkeys(reach.members) if member is not caller]
            for member in called:
                guessed = {JOINED_FACT: [JOINED_BY_A_GUESS]} if reach.joined_only_by_a_guess(member) else None
                self._graph.edges.relate("invokes", caller, member, guessed)
            if not called and self._calls_nothing_by_design(caller):
                caller.set_fact(EXEMPT_FACT, ["invokes"])
            owner = self._index.class_declaring(caller)
            if owner is not None:
                self._depend(owner, caller, reach.classes)
                unjoined.setdefault(id(owner), Counter()).update(reach.unresolved_calls)
        for node in in_graph.nodes("OoadClass"):
            counted = unjoined.get(id(node), Counter())
            for cause, fact in UNRESOLVED_CALLS_FACTS.items():
                node.set_fact(fact, counted[cause])

    def _depend(self, owner: "Node", caller: "Node", reached: "list[tuple[Node, str]]") -> None:
        """Record that owner depends on each other class caller reaches, with how it reaches it and through caller."""
        for other, how in reached:
            if other is not owner:
                self._graph.edges.relate("dependsOn", owner, other, {REACHED_FACT: [how], THROUGH_FACT: [caller.name]})

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
