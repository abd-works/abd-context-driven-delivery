"""Relationship on a class. Kind is composition, aggregation, or association."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


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

    def translate_from(self, source: "Relationship"):
        from practices.clean_engineering.model.update_report import UpdateReport

        self.update_self(source)
        return UpdateReport()

    def update_self(self, source: "Relationship") -> None:
        self.target = source.target
        self.kind = source.kind
        self.cardinality = source.cardinality
        self.description = source.description
        self.sequential_order = source.sequential_order

    def clone(self) -> "Relationship":
        return type(self)(
            target=self.target,
            kind=self.kind,
            cardinality=self.cardinality,
            description=self.description,
            sequential_order=self.sequential_order,
        )
