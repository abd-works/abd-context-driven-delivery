"""Property — typed field on a Class (canonical OoadNode)."""

from __future__ import annotations

from typing import List

from practices.clean_engineering.model.base_class_model import OoadNode
from practices.clean_engineering.model.field_types import PropertyField
from practices.clean_engineering.model.update_report import ChildCollectionPair


class Property(OoadNode):
    _semantic_type_name = "Property"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        type_hint: str = "",
        description: str = "",
    ) -> None:
        super().__init__(name, sequential_order)
        self.type_hint = type_hint
        self.description = description

    @classmethod
    def from_field(cls, field: PropertyField, sequential_order: int) -> "Property":
        return cls(
            name=field.name,
            sequential_order=sequential_order,
            type_hint=field.type_hint,
            description=field.description,
        )

    def to_field(self) -> PropertyField:
        return PropertyField(
            name=self.name,
            type_hint=self.type_hint,
            description=self.description,
        )

    def as_record(self) -> dict:
        return {
            "name": self.name,
            "typeHint": self.type_hint,
            "description": self.description,
        }

    def render(self) -> str:
        return self.to_field().render()

    def update_self(self, source: OoadNode) -> None:
        assert isinstance(source, Property)
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.type_hint = source.type_hint
        self.description = source.description

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        return []
