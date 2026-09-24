"""Legacy field rows for format channels — tree nodes are Property and Operation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from practices.clean_engineering.model.update_report import UpdateReport

@dataclass
class PropertyField:
    name: str
    type_hint: str = ""
    description: str = ""
    sequential_order: int = 0

    def as_record(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "typeHint": self.type_hint,
            "description": self.description,
        }

    def update_self(self, source: "PropertyField") -> None:
        self.name = source.name
        self.type_hint = source.type_hint
        self.description = source.description
        self.sequential_order = source.sequential_order

    def translate_from(self, source: "PropertyField") -> UpdateReport:
        self.update_self(source)
        return UpdateReport()

    def render(self) -> str:
        if self.type_hint:
            return f"{self.name}: {self.type_hint}"
        return self.name


@dataclass
class OperationField:
    name: str
    parameters: List[str] = field(default_factory=list)
    return_type: str = ""
    description: str = ""
    line: int | None = None
    line_count: int = 0
    nesting_depth: int = 0
    callees: List[str] = field(default_factory=list)
    literals: List[str] = field(default_factory=list)
    param_count: int = 0
    has_calculation: bool = False
    has_validation: bool = False
    bare_except_lines: List[int] = field(default_factory=list)
    swallowed_except_lines: List[int] = field(default_factory=list)
    assigned_names: List[tuple[str, int]] = field(default_factory=list)
    loop_target_names: List[tuple[str, int]] = field(default_factory=list)
    body_fingerprint: str = ""
    constructed_types: List[tuple[str, int]] = field(default_factory=list)
    public_attr_assigns: List[tuple[str, int]] = field(default_factory=list)
    is_property: bool = False
    returns_private_attr: bool = False
    magic_numbers: List[tuple[float, int]] = field(default_factory=list)
    docstring_parrots_name: bool = False
    sequential_order: int = 0

    def as_record(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "parameters": list(self.parameters),
            "returnType": self.return_type,
            "description": self.description,
        }

    def update_self(self, source: "OperationField") -> None:
        self.name = source.name
        self.parameters = list(source.parameters)
        self.return_type = source.return_type
        self.description = source.description
        self.line = source.line
        self.line_count = source.line_count
        self.nesting_depth = source.nesting_depth
        self.callees = list(source.callees)
        self.literals = list(source.literals)
        self.param_count = source.param_count
        self.has_calculation = source.has_calculation
        self.has_validation = source.has_validation
        self.bare_except_lines = list(source.bare_except_lines)
        self.swallowed_except_lines = list(source.swallowed_except_lines)
        self.assigned_names = list(source.assigned_names)
        self.loop_target_names = list(source.loop_target_names)
        self.body_fingerprint = source.body_fingerprint
        self.constructed_types = list(source.constructed_types)
        self.public_attr_assigns = list(source.public_attr_assigns)
        self.is_property = source.is_property
        self.returns_private_attr = source.returns_private_attr
        self.magic_numbers = list(source.magic_numbers)
        self.docstring_parrots_name = source.docstring_parrots_name
        self.sequential_order = source.sequential_order

    def translate_from(self, source: "OperationField") -> UpdateReport:
        self.update_self(source)
        return UpdateReport()

    def render(self) -> str:
        params = ", ".join(self.parameters)
        suffix = f": {self.return_type}" if self.return_type else ""
        prefix = "- " if self.name.startswith("_") else ""
        return f"{prefix}{self.name}({params}){suffix}"


@dataclass
class Relationship:
    target: str
    kind: str = ""
    cardinality: str = ""
    description: str = ""
    sequential_order: int = 0

    @property
    def name(self) -> str:
        return self.target

    def as_record(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "kind": self.kind,
            "cardinality": self.cardinality,
            "description": self.description,
        }

    def update_self(self, source: "Relationship") -> None:
        self.target = source.target
        self.kind = source.kind
        self.cardinality = source.cardinality
        self.description = source.description
        self.sequential_order = source.sequential_order

    def translate_from(self, source: "Relationship") -> UpdateReport:
        self.update_self(source)
        return UpdateReport()
