"""A relationship from one class to another. On a property its kind is composition, aggregation, or association, with a
cardinality of 0..1, 0..*, 1, or 1..*. A class's dependency has the kind dependency and a label that names the
interaction, such as `runs` or `reads sections with`, drawn as `Repo ---<<runs>>--> Git`."""

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
    label: str = ""

    @property
    def name(self) -> str:
        return self.target

    def as_record(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "kind": self.kind,
            "cardinality": self.cardinality,
            "description": self.description,
            "label": self.label,
        }

    def translate_from(self, source: "Relationship"):
        from cdd_guidance.practices.clean_engineering.model.update_report import UpdateReport

        self.update_self(source)
        return UpdateReport()

    def update_self(self, source: "Relationship") -> None:
        self.target = source.target
        self.kind = source.kind
        self.cardinality = source.cardinality
        self.description = source.description
        self.sequential_order = source.sequential_order
        self.label = source.label

    def clone(self) -> "Relationship":
        return type(self)(
            target=self.target,
            kind=self.kind,
            cardinality=self.cardinality,
            description=self.description,
            sequential_order=self.sequential_order,
            label=self.label,
        )
