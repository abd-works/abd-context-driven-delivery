"""Operation and Parameter — behaviour on a class."""

from __future__ import annotations

import hashlib
import re
from typing import List


def operation_body_fingerprint(body: str) -> str:
    """Stable hash of normalized method body text (shared by Python AST and C-family parse)."""
    normalized = re.sub(r"\s+", " ", body.strip())
    if len(normalized) < 40:
        return ""
    return hashlib.sha256(normalized.encode()).hexdigest()[:24]


from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody
from harness.graph.model_node import ModelChildren

from cdd_guidance.practices.clean_engineering.model.ooad_node import OoadNode
from cdd_guidance.practices.clean_engineering.model.operation_metrics import (
    MIN_DELEGATION_LINES,
    SourceText,
    names_call_io_and_domain,
)
from cdd_guidance.practices.clean_engineering.model.property import InvariantHolder
from cdd_guidance.practices.clean_engineering.model.type_refs import split_top_level

# `save(cart: Cart, note: str = ""): Receipt` as a model line writes an operation.
_SIGNATURE = re.compile(r"^(_?\w+)\s*\((.*)\)\s*(?::\s*(.+))?$")


# The names a constructor goes by: Python's and the C-family languages'.
CONSTRUCTOR_NAMES = frozenset({"__init__", "constructor"})


class Parameter(OoadNode):
    _semantic_type_name = "Parameter"
    graph_facts = ("type_hint", "operation_name", "property_setter", "in_typed_language")

    def __init__(self, name: str, sequential_order: int = 0, type_hint: str = "") -> None:
        super().__init__(name, sequential_order)
        self.type_hint = type_hint
        # The operation that declares it, which it keeps after the graph places it in its explorer tree.
        self.operation: Operation | None = None

    @property
    def operation_name(self) -> str:
        """The name of the operation that declares this parameter; empty before one holds it."""
        return self.operation.name if self.operation is not None else ""

    @property
    def in_typed_language(self) -> bool:
        """True when the operation that declares it is written in a language with a syntax for a parameter's type;
        plain JavaScript has none. A parameter no code operation holds, such as one read from a model document, is
        judged as typed."""
        return self.operation is None or self.operation.declares_types

    @property
    def property_setter(self) -> bool:
        """True for the one parameter of a property's setter."""
        operation = self.operation
        if operation is None or len(operation.parameters) != 1:
            return False
        return operation.is_setter or operation.is_property

    def clone(self) -> "Parameter":
        return type(self)(self.name, self.sequential_order, self.type_hint)

    def save(self) -> str:
        if self.type_hint:
            return f"{self.name}: {self.type_hint}"
        return self.name

    def __str__(self) -> str:
        return self.save()

    def as_record(self) -> dict:
        return {"name": self.name, "typeHint": self.type_hint}

    def update_self(self, source: OoadNode) -> None:
        assert isinstance(source, Parameter)
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.type_hint = source.type_hint


class Operation(InvariantHolder, OoadNode):
    _semantic_type_name = "Operation"
    # Whether the language the operation is written in has a syntax for a parameter's type. Plain JavaScript's
    # operation says it has none; every other language, and a model document, has one.
    declares_types = True

    @property
    def is_constructor(self) -> bool:
        """True for the operation that builds its class: `__init__` or `constructor`."""
        return self.name in CONSTRUCTOR_NAMES

    @property
    def body_text(self) -> str:
        """The statements of its body. They save with the graph, so a rule that compares bodies reads the same text from
        an operation read now and from one read back from a saved graph."""
        return self.body.text
    graph_facts = (
        "line_count",
        "max_control_flow_depth",
        "has_bare_catch",
        "swallows_exceptions",
        "unnamed_literal_numbers",
        "is_static",
        "is_classmethod",
        "is_property",
        "is_setter",
        "body_fingerprint",
        "callees",
        "peer_private_access",
        "io_and_domain",
        "io_and_domain_callees",
        "raises_on_empty",
        "exception_without_message",
        "generic_exception_message",
        "mutates_without_record",
        "prose_comment",
        "bold_interaction_lines",
        "bold_invariant_lines",
        "owner",
        "packed_parameters",
        "return_type",
        "value_type",
        "body_text",
    )

    def __init__(
        self,
        name: str,
        sequential_order: int = 0,
        return_type: str = "",
        description: str = "",
        callees: List[str] | None = None,
        parameters: List[str] | None = None,
        **fields: object,
    ) -> None:
        graph = fields.pop("graph", None)
        super().__init__(name, sequential_order, graph)
        self.return_type = return_type
        self.description = description
        self.callees: List[str] = list(callees) if callees is not None else []
        self._parameters = ModelChildren(self, "parameters")
        self.invariants: List = []
        self.line: int | None = None
        self.end_line: int | None = None
        self.line_count: int | None = None
        self.body_fingerprint: str = ""
        self.body = CodeBody()
        # The source this operation spans in its file, kept once its parser reads the file.
        self.span = SourceText("")
        self.constructed_types: list[tuple[str, int]] = []
        self._is_property = False
        # The class that declares it, once kept (keep_owner).
        self._declared_by = ""
        # A property's setter, such as Python's `@total.setter`; a getter is `is_property`.
        self.is_setter = False
        self.is_static = False
        self.is_classmethod = False
        self.max_control_flow_depth: int = 0
        self.has_bare_catch: bool = False
        self.swallows_exceptions: bool = False
        self.unnamed_literal_numbers: list[str] = []
        self.narrative_comment_lines: int = 0
        self.peer_private_access: bool = False
        # Each parameter that packs several values, with how many; only Python's parse measures it.
        self.packed_parameters: dict[str, int] = {}
        self.io_and_domain = False
        self.io_and_domain_callees = False
        self.raises_on_empty = False
        self.exception_without_message = ""
        self.generic_exception_message = False
        self.mutates_without_record = False
        self.prose_comment = False
        self.bold_interaction_lines: list[int] = []
        self.bold_invariant_lines: list[int] = []
        for key, value in fields.items():
            setattr(self, key, value)
        if parameters:
            self._take_parameters(parameters)

    @classmethod
    def from_signature(cls, text: str) -> "Operation | None":
        """The operation a model line such as `save(cart: Cart, note: str = ""): Receipt` writes, each parameter with
        its type and without its default; none for a line that is no operation. Every format that writes members as
        such lines reads them here."""
        match = _SIGNATURE.match(text.strip())
        if match is None:
            return None
        operation = cls(match.group(1), return_type=(match.group(3) or "").strip())
        for order, part in enumerate(split_top_level(match.group(2) or ""), start=1):
            name, _, hint = part.partition(":")
            operation.parameters.append(Parameter(name.strip(), order, hint.split("=")[0].strip()))
        return operation

    @property
    def is_property(self) -> bool:
        """True for a getter, such as Python's `@property` or TypeScript's `get total()`: the operation its class's
        instances show as a property. A getter's graph node is that property, so its kind reads `Property`."""
        return self._is_property

    @is_property.setter
    def is_property(self, value: bool) -> None:
        self._is_property = bool(value)
        self.type = "Property" if self._is_property else self._semantic_type_name

    @property
    def value_type(self) -> str:
        """The type a reader of this operation gets back: its return type, which is a getter's property type."""
        return self.return_type

    def attach(self, child, kind: str) -> None:
        """A parameter it takes keeps it as the operation that declares it."""
        super().attach(child, kind)
        if isinstance(child, Parameter):
            child.operation = self

    @property
    def owner(self) -> str:
        """The name of the class that declares this operation; ``_module`` for a module function; empty before a class holds it."""
        parent = self.parent
        return parent.name if isinstance(parent, OoadNode) and parent.declares(self) else self._declared_by

    def keep_owner(self) -> None:
        """Keep the class that declares this operation as its owner from now on: a graph's tree may hang it under a group
        of its class's members, and its owner, which saves with the graph, stays the class."""
        self._declared_by = self.owner

    @property
    def parameters(self) -> List[Parameter]:
        return self._parameters

    @parameters.setter
    def parameters(self, parameters: List[Parameter]) -> None:
        self._parameters.refill(parameters)

    def _take_parameters(self, parameters: list) -> None:
        from cdd_guidance.practices.clean_engineering.model.type_refs import parse_parameter

        taken: List[Parameter] = []
        for index, item in enumerate(parameters, start=1):
            if isinstance(item, Parameter):
                taken.append(item.clone())
                continue
            name, type_hint = parse_parameter(str(item))
            taken.append(Parameter(name or f"arg{index}", index, type_hint=type_hint))
        self.parameters = taken

    def clone(self) -> "Operation":
        cloned = type(self)(
            self.name,
            self.sequential_order,
            return_type=self.return_type,
            description=self.description,
            callees=list(self.callees),
        )
        cloned.parameters = [parameter.clone() for parameter in self.parameters]
        cloned.invariants = [item.clone() for item in self.invariants]
        cloned.line = self.line
        cloned.end_line = self.end_line
        cloned.line_count = self.line_count
        cloned.body_fingerprint = self.body_fingerprint
        cloned.body = self.body
        cloned.constructed_types = list(self.constructed_types)
        cloned.is_property = self.is_property
        cloned.is_setter = self.is_setter
        cloned.is_static = self.is_static
        cloned.is_classmethod = self.is_classmethod
        cloned.max_control_flow_depth = self.max_control_flow_depth
        cloned.has_bare_catch = self.has_bare_catch
        cloned.swallows_exceptions = self.swallows_exceptions
        cloned.unnamed_literal_numbers = list(self.unnamed_literal_numbers)
        cloned.narrative_comment_lines = self.narrative_comment_lines
        cloned.peer_private_access = self.peer_private_access
        return cloned

    @property
    def source_lines(self) -> tuple[int, int]:
        """The first and last line of its file this operation spans: its line through its end line, or as many lines
        as its body counts; its line alone when its parser recorded no end."""
        start = self.line or 1
        if self.end_line is not None and self.end_line >= start:
            return start, self.end_line
        if self.line_count and self.line_count > 0:
            return start, start + self.line_count - 1
        return start, start

    def take_lines(self, lines: List[str]) -> None:
        """Keep the lines of its file this operation spans."""
        start, end = self.source_lines
        self.span = SourceText("\n".join(lines[start - 1 : end]))

    def load_span_facts(self) -> None:
        """Fill the facts this operation's own source span carries, beyond what the parser measured."""
        span = self.span
        if not self.body_fingerprint:
            self.body_fingerprint = _span_fingerprint(span.text)
        self.io_and_domain_callees = self._delegates_io_and_domain()
        self.io_and_domain = span.mixes_io_and_domain()
        self.raises_on_empty = span.raises_on_empty()
        self.exception_without_message = span.exception_without_message()
        self.generic_exception_message = span.generic_exception_message()
        # A constructor sets up the object it builds and cannot return a record, so it is not a state change to report.
        self.mutates_without_record = not self.is_constructor and span.mutates_without_record()
        self.prose_comment = span.has_prose_comment()
        bullets = span.markdown_bullet_lines()
        self.bold_interaction_lines = bullets.get("bold_interaction_lines", [])
        self.bold_invariant_lines = bullets.get("bold_invariant_lines", [])

    def load_brace_body_facts(self, body: str, class_name: str) -> None:
        """Fill the facts the rules measure on a brace-language method body (inside its `{` … `}`), declared by the
        class named class_name (empty for a module function)."""
        measured = SourceText(body)
        parameter_names = frozenset(p.name for p in self.parameters if p.name)
        self.max_control_flow_depth = measured.control_flow_depth()
        self.has_bare_catch = measured.has_bare_catch()
        self.swallows_exceptions = measured.swallows_exceptions()
        self.unnamed_literal_numbers = measured.unnamed_numbers()
        self.peer_private_access = measured.reaches_peer_private(class_name, self._parameters_typed_as(class_name))
        if self.is_constructor:
            self.constructed_types = measured.built_collaborators(parameter_names, self.line or 1)

    def _parameters_typed_as(self, class_name: str) -> frozenset[str]:
        """The parameters whose declared type names the class: ``other: Money``."""
        if not class_name:
            return frozenset()
        typed = re.compile(rf"\b{re.escape(class_name)}\b")
        return frozenset(parameter.name for parameter in self.parameters if parameter.name and typed.search(parameter.type_hint or ""))

    def _delegates_io_and_domain(self) -> bool:
        """A long operation that calls both I/O and domain calculations does two jobs, even when it only delegates."""
        if (self.line_count or 0) < MIN_DELEGATION_LINES:
            return False
        return names_call_io_and_domain(self.callees)

    def save(self) -> str:
        params = ", ".join(parameter.save() for parameter in self.parameters)
        suffix = f": {self.return_type}" if self.return_type else ""
        prefix = "- " if self.name.startswith("_") else ""
        return f"{prefix}{self.name}({params}){suffix}"

    def render(self) -> str:
        return self.save()

    def as_record(self) -> dict:
        return {
            "name": self.name,
            "parameters": [parameter.save() for parameter in self.parameters],
            "returnType": self.return_type,
            "description": self.description,
        }

    def update_self(self, source: OoadNode) -> None:
        assert isinstance(source, Operation)
        copied = source.clone()
        self.name = copied.name
        self.sequential_order = copied.sequential_order
        self.return_type = copied.return_type
        self.description = copied.description
        self.callees = list(copied.callees)
        self.parameters = copied.parameters
        self.invariants = copied.invariants
        self.line = copied.line
        self.end_line = copied.end_line
        self.line_count = copied.line_count
        self.body_fingerprint = copied.body_fingerprint
        self.body = copied.body
        self.constructed_types = list(copied.constructed_types)
        self.is_property = copied.is_property
        self.is_setter = copied.is_setter
        self.is_static = copied.is_static
        self.is_classmethod = copied.is_classmethod
        self.max_control_flow_depth = copied.max_control_flow_depth
        self.has_bare_catch = copied.has_bare_catch
        self.swallows_exceptions = copied.swallows_exceptions
        self.unnamed_literal_numbers = list(copied.unnamed_literal_numbers)
        self.narrative_comment_lines = copied.narrative_comment_lines
        self.peer_private_access = copied.peer_private_access

    def load_parameter(self, source: Parameter) -> Parameter:
        return type(self.parameters[0])(source.name, source.sequential_order, source.type_hint) if self.parameters else Parameter(
            source.name, source.sequential_order, source.type_hint
        )

    def reconcile_children(self, source: OoadNode) -> None:
        assert isinstance(source, Operation)
        if source.parameters:
            self._parameters.reconcile(source.parameters, self.load_parameter)


def _span_fingerprint(source_span: str) -> str:
    normalized = re.sub(r"\s+", " ", source_span.strip())
    return hashlib.sha256(normalized.encode()).hexdigest()[:24] if normalized else ""
