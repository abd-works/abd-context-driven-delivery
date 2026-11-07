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


def operation_source_span(operation: "Operation") -> tuple[int, int] | None:
    """1-based inclusive source lines for this operation when the model recorded them."""
    start = operation.line
    if not start:
        return None
    end = operation.end_line
    if end is not None and end >= start:
        return start, end
    if operation.line_count and operation.line_count > 0:
        return start, start + operation.line_count - 1
    return None

from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody
from harness.graph.model_node import ModelChildren

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass, OoadNode
from cdd_guidance.practices.clean_engineering.model.operation_metrics import (
    MIN_DELEGATION_LINES,
    PythonFunctionBody,
    SourceText,
)
from cdd_guidance.practices.clean_engineering.model.translation import ChildCollectionPair


class Parameter(OoadNode):
    _semantic_type_name = "Parameter"
    graph_facts = ("type_hint", "operation_name", "property_setter")

    def __init__(self, name: str, sequential_order: int = 0, type_hint: str = "") -> None:
        super().__init__(name, sequential_order)
        self.type_hint = type_hint
        self.operation_name = ""
        self.property_setter = False

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

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        return []

    def load_operation_facts(self, operation: "Operation") -> None:
        """Fill the facts this parameter owns about the operation that declares it."""
        self.operation_name = operation.name
        self.property_setter = operation.is_property and len(operation.parameters) == 1


class Operation(OoadNode):
    _semantic_type_name = "Operation"
    graph_facts = (
        "line_count",
        "max_control_flow_depth",
        "has_bare_catch",
        "swallows_exceptions",
        "unnamed_literal_numbers",
        "is_static",
        "is_classmethod",
        "is_property",
        "body_fingerprint",
        "callees",
        "peer_private_access",
        "private_reach",
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
        self.constructed_types: list[tuple[str, int]] = []
        self.is_property = False
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
        self.private_reach = False
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

    @property
    def owner(self) -> str:
        """The name of the class that declares this operation; ``_module`` for a module function; empty before a class holds it."""
        return self.parent.name if isinstance(self.parent, OoadClass) else ""

    @property
    def parameters(self) -> List[Parameter]:
        return self._parameters

    @parameters.setter
    def parameters(self, parameters: List[Parameter]) -> None:
        self._refill(self._parameters, parameters)

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
        cloned.is_static = self.is_static
        cloned.is_classmethod = self.is_classmethod
        cloned.max_control_flow_depth = self.max_control_flow_depth
        cloned.has_bare_catch = self.has_bare_catch
        cloned.swallows_exceptions = self.swallows_exceptions
        cloned.unnamed_literal_numbers = list(self.unnamed_literal_numbers)
        cloned.narrative_comment_lines = self.narrative_comment_lines
        cloned.peer_private_access = self.peer_private_access
        return cloned

    def load_span_facts(self, source_span: str) -> None:
        """Fill the facts this operation's own source span carries, beyond what the parser measured."""
        if not self.body_fingerprint:
            self.body_fingerprint = _span_fingerprint(source_span)
        self.io_and_domain_callees = self._delegates_io_and_domain()
        span = SourceText(source_span)
        self.private_reach = span.private_reach()
        self.io_and_domain = span.mixes_io_and_domain()
        self.raises_on_empty = span.raises_on_empty()
        self.exception_without_message = span.exception_without_message()
        self.generic_exception_message = span.generic_exception_message()
        self.mutates_without_record = span.mutates_without_record()
        self.prose_comment = span.has_prose_comment()
        bullets = span.markdown_bullet_lines()
        self.bold_interaction_lines = bullets.get("bold_interaction_lines", [])
        self.bold_invariant_lines = bullets.get("bold_invariant_lines", [])

    def load_brace_body_facts(self, body: str) -> None:
        """Fill the facts the rules measure on a brace-language method body (inside its `{` … `}`)."""
        measured = SourceText(body)
        self.max_control_flow_depth = measured.control_flow_depth()
        self.has_bare_catch = measured.has_bare_catch()
        self.swallows_exceptions = measured.swallows_exceptions()
        self.unnamed_literal_numbers = measured.unnamed_numbers()
        self.peer_private_access = measured.reaches_peer_private(frozenset(p.name for p in self.parameters if p.name))

    def load_python_function_facts(self, node) -> None:
        """Fill the facts the rules measure on a Python function, from its syntax tree."""
        measured = PythonFunctionBody(node)
        self.max_control_flow_depth = measured.control_flow_depth()
        self.has_bare_catch, self.swallows_exceptions = measured.except_flags()
        self.unnamed_literal_numbers = measured.unnamed_numbers()
        self.narrative_comment_lines = 0
        self.peer_private_access = measured.reaches_peer_private()
        self.packed_parameters = measured.packed_parameters()

    def _delegates_io_and_domain(self) -> bool:
        """A long operation that calls both I/O and domain calculations does two jobs, even when it only delegates."""
        if (self.line_count or 0) < MIN_DELEGATION_LINES:
            return False
        return SourceText("\n".join(f"{callee}(" for callee in self.callees if callee)).calls_io_and_domain()

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
        self.is_static = copied.is_static
        self.is_classmethod = copied.is_classmethod
        self.max_control_flow_depth = copied.max_control_flow_depth
        self.has_bare_catch = copied.has_bare_catch
        self.swallows_exceptions = copied.swallows_exceptions
        self.unnamed_literal_numbers = list(copied.unnamed_literal_numbers)
        self.narrative_comment_lines = copied.narrative_comment_lines
        self.peer_private_access = copied.peer_private_access

    def load_parameters(self) -> None:
        while self.has_more_parameter():
            self.parameters.append(self.load_next_parameter())

    def has_more_parameter(self) -> bool:
        return False

    def load_next_parameter(self) -> Parameter:
        return self.get_next_parameter_from_file()

    def get_next_parameter_from_file(self) -> Parameter:
        raise NotImplementedError(f"{type(self).__name__} must implement get_next_parameter_from_file")

    def load_parameter(self, source: Parameter) -> Parameter:
        return type(self.parameters[0])(source.name, source.sequential_order, source.type_hint) if self.parameters else Parameter(
            source.name, source.sequential_order, source.type_hint
        )

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        assert isinstance(source, Operation)
        if source.parameters:
            return [
                ChildCollectionPair(
                    self_children=self.parameters,
                    source_children=source.parameters,
                    load=self.load_parameter,
                )
            ]
        return []


def _span_fingerprint(source_span: str) -> str:
    normalized = re.sub(r"\s+", " ", source_span.strip())
    return hashlib.sha256(normalized.encode()).hexdigest()[:24] if normalized else ""
