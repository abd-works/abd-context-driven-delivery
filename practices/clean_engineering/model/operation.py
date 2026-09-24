"""Operation and Parameter — behaviour on a Class (canonical OoadNode)."""

from __future__ import annotations

from typing import List

from practices.clean_engineering.model.base_class_model import OoadNode
from practices.clean_engineering.model.field_types import OperationField
from practices.clean_engineering.model.update_report import ChildCollectionPair


class Parameter(OoadNode):
    _semantic_type_name = "Parameter"

    def __init__(self, name: str, sequential_order: int, type_hint: str = "") -> None:
        super().__init__(name, sequential_order)
        self.type_hint = type_hint

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
        sequential_order: int,
        return_type: str = "",
        description: str = "",
        callees: List[str] | None = None,
    ) -> None:
        super().__init__(name, sequential_order)
        self.return_type = return_type
        self.description = description
        self.callees: List[str] = list(callees) if callees is not None else []
        self.parameters: List[Parameter] = []
        self._legacy_parameters: List[str] = []

    @property
    def legacy_parameters(self) -> List[str]:
        return list(self._legacy_parameters)

    @legacy_parameters.setter
    def legacy_parameters(self, values: List[str]) -> None:
        self._legacy_parameters = list(values)

    @classmethod
    def from_field(cls, field: OperationField, sequential_order: int) -> "Operation":
        op = cls(
            name=field.name,
            sequential_order=sequential_order,
            return_type=field.return_type,
            description=field.description,
            callees=list(field.callees),
        )
        op._legacy_parameters = list(field.parameters)
        op._sync_parameters_from_legacy()
        return op

    def _sync_parameters_from_legacy(self) -> None:
        from practices.clean_engineering.model.type_refs import parse_parameter

        self.parameters = []
        for index, raw in enumerate(self._legacy_parameters, start=1):
            name, type_hint = parse_parameter(raw)
            self.parameters.append(
                Parameter(name or f"arg{index}", index, type_hint=type_hint)
            )

    def to_field(self) -> OperationField:
        params = [
            f"{p.name}: {p.type_hint}" if p.type_hint else p.name for p in self.parameters
        ] or list(self._legacy_parameters)
        return OperationField(
            name=self.name,
            parameters=params,
            return_type=self.return_type,
            description=self.description,
            callees=list(self.callees),
        )

    def as_record(self) -> dict:
        return self.to_field().as_record()

    def render(self) -> str:
        return self.to_field().render()

    def update_self(self, source: OoadNode) -> None:
        assert isinstance(source, Operation)
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.return_type = source.return_type
        self.description = source.description
        self.callees = list(source.callees)
        self.legacy_parameters = list(source.legacy_parameters)

    def load_parameter(self, source: Parameter) -> Parameter:
        return Parameter(source.name, source.sequential_order, source.type_hint)

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
