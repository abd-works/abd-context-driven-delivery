"""Operation and Parameter — behaviour on a class."""

from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.source_code import CodeBody
from harness.graph.model_node import ModelChildren

from cdd_guidance.practices.clean_engineering.model.ooad_node import OoadNode
from cdd_guidance.practices.clean_engineering.model.property import InvariantHolder
from cdd_guidance.practices.clean_engineering.model.source_facts import CONSTRUCTOR_NAMES, OperationSourceFacts
from cdd_guidance.practices.source_code import split_top_level
from cdd_guidance.practices.clean_engineering.model.type_refs import name_with_type, parse_parameter

# `save(cart: Cart, note: str = ""): Receipt` as a model line writes an operation.
_SIGNATURE = re.compile(r"^(_?\w+)\s*\((.*)\)\s*(?::\s*(.+))?$")


# A doc comment that opens a body, and a line that stands for a body nobody has written yet.
_DOC_COMMENT = re.compile(r"""^\s*(?:\"{3}[\s\S]*?\"{3}|'{3}[\s\S]*?'{3}|/\*[\s\S]*?\*/)""")
_NOT_WRITTEN_YET = re.compile(r"""^(?:pass|\.\.\.|raise NotImplementedError(?:\(.*\))?|throw new Error\(['"]not implemented['"]\);?)$""")


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
        return name_with_type(self.name, self.type_hint)

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
    def has_body(self) -> bool:
        """Whether its body holds a statement that does something. A body that is empty, only ``pass`` or an
        ellipsis, only a doc comment, or only the line that fails until it is written (``raise NotImplementedError``,
        ``throw new Error('not implemented')``) is no body: an operation declared so far and not yet written."""
        written = _DOC_COMMENT.sub("", self.body.text)
        statements = [line.strip() for line in written.splitlines() if line.strip() and not line.strip().startswith(("#", "//"))]
        return any(not _NOT_WRITTEN_YET.match(statement) for statement in statements)

    @property
    def body_text(self) -> str:
        """The statements of its body. They save with the graph, so a rule that compares bodies reads the same text from
        an operation read now and from one read back from a saved graph."""
        return self.body.text
    graph_facts = (
        "line_count",
        "is_static",
        "is_private",
        "is_classmethod",
        "is_property",
        "is_setter",
        "published_as_tool",
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

    def __init__(self, name: str, sequential_order: int = 0, return_type: str = "") -> None:
        super().__init__(name, sequential_order)
        self.return_type = return_type
        # What it says about itself: its doc comment, or its invariant lines joined.
        self.description = ""
        # The operations its body calls, as written.
        self.callees: List[str] = []
        self._parameters = ModelChildren(self, "parameters")
        self.invariants: List = []
        # The class that declares it, once kept (keep_owner).
        self._declared_by = ""
        self._start_modifiers()
        self._start_source()
        self._start_measures()

    def _start_modifiers(self) -> None:
        """The kind of operation it is, a plain instance operation until its parser reads otherwise."""
        self._is_property = False
        # A property's setter, such as Python's `@total.setter`; a getter is `is_property`.
        self.is_setter = False
        self.is_static = False
        # Declared private with the language's own keyword, such as TypeScript's `private`; a name starting with `_`
        # says the same in every language.
        self.is_private = False
        self.is_classmethod = False
        # Published as an MCP tool, such as Python's `@mcp` or `@agent_tool`: its parameters are the tool's published
        # argument schema, which the tool's callers fill by name.
        self.published_as_tool = False
        # A JavaScript constructor function: a capitalised `function` that assigns `this.` fields and its file calls
        # with `new`. Like a constructor, it builds its object and has no record to return.
        self.is_constructor_function = False

    def _start_source(self) -> None:
        """Where it sits in its file and what its body says, empty until its parser reads the file."""
        self.line: int | None = None
        self.end_line: int | None = None
        self.line_count: int | None = None
        self.body_fingerprint: str = ""
        self.body = CodeBody()
        # What its source says, as its parser reads it: its body, its fingerprint, and the lines it spans.
        self.source_facts = OperationSourceFacts(self)
        self.constructed_types: list[tuple[str, int]] = []

    def _start_measures(self) -> None:
        """The measures the rules read from what it says about its body, each at its clean value until it is read. The
        measures taken of a written body belong to an operation read from code (CodeOperation)."""
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

    def attach(self, child: OoadNode, kind: str) -> None:
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

    def take_parameters(self, parameters: list) -> None:
        """Take its parameters as written, each a `name: Type` line or a parameter to copy."""
        taken: List[Parameter] = []
        for index, item in enumerate(parameters, start=1):
            if isinstance(item, Parameter):
                taken.append(item.clone())
                continue
            name, type_hint = parse_parameter(str(item))
            taken.append(Parameter(name or f"arg{index}", index, type_hint=type_hint))
        self.parameters = taken

    def clone(self) -> "Operation":
        cloned = type(self)(self.name, self.sequential_order)
        cloned._copy_from(self)
        return cloned

    def _copy_from(self, source: "Operation") -> None:
        """Become a copy of source that shares none of its lists or members."""
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.return_type = source.return_type
        self.description = source.description
        self.callees = list(source.callees)
        self.parameters = [parameter.clone() for parameter in source.parameters]
        self.invariants = [item.clone() for item in source.invariants]
        self._copy_source_from(source)
        self._copy_measures_from(source)

    def _copy_source_from(self, source: "Operation") -> None:
        """Copy where source sits in its file, its body, and its kind."""
        self.line = source.line
        self.end_line = source.end_line
        self.line_count = source.line_count
        self.body_fingerprint = source.body_fingerprint
        self.body = source.body
        self.constructed_types = list(source.constructed_types)
        self.is_property = source.is_property
        self.is_setter = source.is_setter
        self.is_static = source.is_static
        self.is_private = source.is_private
        self.is_classmethod = source.is_classmethod
        self.published_as_tool = source.published_as_tool
        self.is_constructor_function = source.is_constructor_function

    def _copy_measures_from(self, source: "Operation") -> None:
        """Copy the measures the parser took of source."""
        self.peer_private_access = source.peer_private_access

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

    def save(self) -> str:
        params = ", ".join(parameter.save() for parameter in self.parameters)
        suffix = f": {self.return_type}" if self.return_type else ""
        prefix = "- " if self.name.startswith("_") else ""
        return f"{prefix}{self.name}({params}){suffix}"

    def as_record(self) -> dict:
        return {
            "name": self.name,
            "parameters": [parameter.save() for parameter in self.parameters],
            "returnType": self.return_type,
            "description": self.description,
        }

    def update_self(self, source: OoadNode) -> None:
        assert isinstance(source, Operation)
        self._copy_from(source)

    def _load_parameter(self, source: Parameter) -> Parameter:
        return type(self.parameters[0])(source.name, source.sequential_order, source.type_hint) if self.parameters else Parameter(
            source.name, source.sequential_order, source.type_hint
        )

    def reconcile_children(self, source: OoadNode) -> None:
        assert isinstance(source, Operation)
        if source.parameters:
            self._parameters.reconcile(source.parameters, self._load_parameter)

