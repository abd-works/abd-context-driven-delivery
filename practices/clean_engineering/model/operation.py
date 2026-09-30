"""Operation and Parameter — behaviour on a class."""

from __future__ import annotations

from typing import List

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
        super().__init__(name, sequential_order)
        self.return_type = return_type
        self.description = description
        self.callees: List[str] = list(callees) if callees is not None else []
        self.parameters: List[Parameter] = []
        self.invariants: List = []
        self._legacy_parameters: List[str] = []
        self.line: int | None = None
        self.line_count = 0
        self.nesting_depth = 0
        self.literals: List[str] = []
        self.param_count = 0
        self.has_calculation = False
        self.has_validation = False
        self.bare_except_lines: List[int] = []
        self.swallowed_except_lines: List[int] = []
        self.assigned_names: List[tuple] = []
        self.loop_target_names: List[tuple] = []
        self.body_fingerprint = ""
        self.constructed_types: List[tuple] = []
        self.public_attr_assigns: List[tuple] = []
        self.is_property = False
        self.returns_private_attr = False
        self.magic_numbers: List[tuple] = []
        self.docstring_parrots_name = False
        for key, value in fields.items():
            setattr(self, key, value)
        if parameters:
            self._take_parameters(parameters)

    def _take_parameters(self, parameters: list) -> None:
        if parameters and isinstance(parameters[0], Parameter):
            self.parameters = [parameter.clone() for parameter in parameters]
            self._legacy_parameters = [parameter.save() for parameter in self.parameters]
            return
        self.legacy_parameters = list(parameters)

    @property
    def legacy_parameters(self) -> List[str]:
        return list(self._legacy_parameters)

    @legacy_parameters.setter
    def legacy_parameters(self, values: List[str]) -> None:
        self._legacy_parameters = list(values)
        self._sync_parameters_from_legacy()

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
        cloned._legacy_parameters = list(self._legacy_parameters)
        for name in (
            "line",
            "line_count",
            "nesting_depth",
            "literals",
            "param_count",
            "has_calculation",
            "has_validation",
            "bare_except_lines",
            "swallowed_except_lines",
            "assigned_names",
            "loop_target_names",
            "body_fingerprint",
            "constructed_types",
            "public_attr_assigns",
            "is_property",
            "returns_private_attr",
            "magic_numbers",
            "docstring_parrots_name",
        ):
            setattr(cloned, name, getattr(self, name))
        return cloned

    def save(self) -> str:
        params = ", ".join(parameter.save() for parameter in self.parameters)
        suffix = f": {self.return_type}" if self.return_type else ""
        prefix = "- " if self.name.startswith("_") else ""
        return f"{prefix}{self.name}({params}){suffix}"

    def render(self) -> str:
        return self.save()

    def _sync_parameters_from_legacy(self) -> None:
        from practices.clean_engineering.model.type_refs import parse_parameter

        self.parameters = []
        for index, raw in enumerate(self._legacy_parameters, start=1):
            name, type_hint = parse_parameter(raw)
            self.parameters.append(Parameter(name or f"arg{index}", index, type_hint=type_hint))

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
        self._legacy_parameters = list(copied._legacy_parameters)
        for name in (
            "line",
            "line_count",
            "nesting_depth",
            "literals",
            "param_count",
            "has_calculation",
            "has_validation",
            "bare_except_lines",
            "swallowed_except_lines",
            "assigned_names",
            "loop_target_names",
            "body_fingerprint",
            "constructed_types",
            "public_attr_assigns",
            "is_property",
            "returns_private_attr",
            "magic_numbers",
            "docstring_parrots_name",
        ):
            setattr(self, name, getattr(copied, name))

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
