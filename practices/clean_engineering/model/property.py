"""Property — typed field on a class."""

from __future__ import annotations

import re
from typing import List

from practices.clean_engineering.model.base_class_model import OoadNode
from practices.clean_engineering.model.field_types import Relationship
from practices.clean_engineering.model.type_refs import domain_type_names
from practices.clean_engineering.model.update_report import ChildCollectionPair


class Invariant(OoadNode):
    """One rule that must stay true, in file order, on a property or an operation."""

    _semantic_type_name = "Invariant"

    def __init__(self, text: str, sequential_order: int = 0) -> None:
        super().__init__(text, sequential_order)
        self.text = text

    def clone(self) -> "Invariant":
        return type(self)(self.text, self.sequential_order)

    def update_self(self, source: OoadNode) -> None:
        assert isinstance(source, Invariant)
        self.name = source.text
        self.text = source.text
        self.sequential_order = source.sequential_order

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        return []


def append_invariant(owner: object, text: str) -> None:
    """Append one // line. Description stays the same lines joined, for channels that still read it."""
    cleaned = text.strip()
    if not cleaned:
        return
    invariants = getattr(owner, "invariants")
    invariants.append(Invariant(cleaned, len(invariants) + 1))
    owner.description = "\n".join(item.text for item in invariants)


_CARDINALITY = re.compile(r"^(?:\d+\.\.\*|\d+\.\.\d+|\*|\d+)$")
_ORIGIN = re.compile(r"^from\s+([A-Z][\w ]*)$")
_STEREOTYPE_NOTE = re.compile(r"^<<\s*(composition|aggregation|association)\s*>>$", re.I)


def take_property_note(prop: "Property", text: str) -> None:
    """A // line under a field is the stereotype, the cardinality, where it comes from, or an invariant."""
    cleaned = text.strip()
    if not cleaned:
        return
    stereotype = _STEREOTYPE_NOTE.match(cleaned)
    if stereotype:
        prop.stereotype = stereotype.group(1).lower()
    elif _CARDINALITY.match(cleaned):
        prop.cardinality = cleaned
    else:
        origin = _ORIGIN.match(cleaned)
        if origin:
            prop.origin = origin.group(1).strip()
        else:
            append_invariant(prop, cleaned)
    bind_property_relationship(prop)


def property_notes(prop: "Property") -> List[str]:
    """Notes written back under the field, in file order: origin, cardinality, then invariants."""
    lines: List[str] = []
    if getattr(prop, "origin", ""):
        lines.append(f"from {prop.origin}")
    if getattr(prop, "cardinality", ""):
        lines.append(prop.cardinality)
    lines.extend(invariant_lines(prop))
    return lines


def bind_property_relationship(prop: "Property") -> None:
    """A relationship exists only when the field's type names a domain class."""
    targets = domain_type_names(prop.type_hint)
    if not targets:
        prop.relationship = None
        return
    kind = (prop.stereotype or "association").lower()
    if kind not in {"composition", "aggregation", "association"}:
        kind = "association"
    prop.stereotype = kind
    prop.relationship = Relationship(
        target=targets[0],
        kind=kind,
        cardinality=prop.cardinality,
        description=prop.origin,
    )


def invariant_lines(owner: object) -> List[str]:
    invariants = getattr(owner, "invariants", None) or []
    if invariants:
        return [item.text for item in invariants]
    return [line.strip() for line in (getattr(owner, "description", "") or "").splitlines() if line.strip()]


class Property(OoadNode):
    _semantic_type_name = "Property"

    def __init__(
        self,
        name: str,
        sequential_order: int = 0,
        type_hint: str = "",
        description: str = "",
    ) -> None:
        super().__init__(name, sequential_order)
        self.type_hint = type_hint
        self.description = description
        self.access = "both"
        self.stereotype = ""
        self.cardinality = ""
        self.origin = ""
        self.relationship: Relationship | None = None
        self.invariants: List[Invariant] = []

    def clone(self) -> "Property":
        cloned = type(self)(self.name, self.sequential_order, self.type_hint, self.description)
        cloned.access = self.access
        cloned.stereotype = self.stereotype
        cloned.cardinality = self.cardinality
        cloned.origin = self.origin
        cloned.relationship = self.relationship.clone() if self.relationship is not None else None
        cloned.invariants = [item.clone() for item in self.invariants]
        return cloned

    def save(self) -> str:
        if self.type_hint:
            return f"{self.name}: {self.type_hint}"
        return self.name

    def render(self) -> str:
        return self.save()

    def as_record(self) -> dict:
        return {
            "name": self.name,
            "typeHint": self.type_hint,
            "description": self.description,
        }

    def update_self(self, source: OoadNode) -> None:
        assert isinstance(source, Property)
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.type_hint = source.type_hint
        self.description = source.description
        self.access = getattr(source, "access", "both")
        self.stereotype = getattr(source, "stereotype", "") or ""
        self.cardinality = getattr(source, "cardinality", "") or ""
        self.origin = getattr(source, "origin", "") or ""
        source_relationship = getattr(source, "relationship", None)
        self.relationship = source_relationship.clone() if source_relationship is not None else None
        self.invariants = [item.clone() for item in getattr(source, "invariants", [])]

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        return []

    @classmethod
    def from_field(cls, field: object, sequential_order: int) -> "Property":
        loaded = cls(
            name=getattr(field, "name"),
            sequential_order=sequential_order,
            type_hint=getattr(field, "type_hint", ""),
            description=getattr(field, "description", ""),
        )
        loaded.stereotype = getattr(field, "stereotype", "") or ""
        loaded.cardinality = getattr(field, "cardinality", "") or ""
        loaded.origin = getattr(field, "origin", "") or ""
        source_relationship = getattr(field, "relationship", None)
        loaded.relationship = source_relationship.clone() if source_relationship is not None else None
        if loaded.relationship is None:
            bind_property_relationship(loaded)
        loaded.invariants = [item.clone() for item in getattr(field, "invariants", [])]
        return loaded

    def to_field(self) -> "Property":
        return self
