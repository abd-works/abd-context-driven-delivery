"""Legacy field rows for format channels — tree nodes are Property and Operation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PropertyField:
    name: str
    type_hint: str = ""
    description: str = ""


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


@dataclass
class Relationship:
    target: str
    kind: str = ""
    cardinality: str = ""
    description: str = ""
