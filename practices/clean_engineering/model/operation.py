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

from harness.graph.bound_node import BoundChildren

from practices.clean_engineering.model.base_class_model import OoadNode
from practices.clean_engineering.model.update_report import ChildCollectionPair


class Parameter(OoadNode):
    _semantic_type_name = "Parameter"

    def __init__(self, name: str, sequential_order: int = 0, type_hint: str = "") -> None:
        super().__init__(name, sequential_order)
        self.type_hint = type_hint

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


class Operation(OoadNode):
    _semantic_type_name = "Operation"

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
        self._parameters = BoundChildren(self, "parameters")
        self.invariants: List = []
        self.line: int | None = None
        self.end_line: int | None = None
        self.line_count: int | None = None
        self.body_fingerprint: str = ""
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
        for key, value in fields.items():
            setattr(self, key, value)
        if parameters:
            self._take_parameters(parameters)

    @property
    def parameters(self) -> List[Parameter]:
        return self._parameters

    @parameters.setter
    def parameters(self, parameters: List[Parameter]) -> None:
        self._refill(self._parameters, parameters)

    def _take_parameters(self, parameters: list) -> None:
        from practices.clean_engineering.model.type_refs import parse_parameter

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

    def save(self) -> str:
        params = ", ".join(parameter.save() for parameter in self.parameters)
        suffix = f": {self.return_type}" if self.return_type else ""
        prefix = "- " if self.name.startswith("_") else ""
        return f"{prefix}{self.name}({params}){suffix}"

    def render(self) -> str:
        return self.save()

    def to_field(self) -> "Operation":
        return self


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

    @classmethod
    def from_field(cls, field: object, sequential_order: int) -> "Operation":
        node = cls(
            name=getattr(field, "name"),
            sequential_order=sequential_order,
            return_type=getattr(field, "return_type", ""),
            description=getattr(field, "description", ""),
            callees=list(getattr(field, "callees", []) or []),
            parameters=list(getattr(field, "parameters", []) or []),
        )
        node.invariants = [item.clone() for item in getattr(field, "invariants", [])]
        return node
