"""Property — typed field on a class."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadNode
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.type_refs import domain_type_names
from cdd_guidance.practices.clean_engineering.model.translation import ChildCollectionPair

if TYPE_CHECKING:
    from harness.graph.graph import Graph


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


class InvariantHolder:
    """A member that carries `//` invariant lines: a property or an operation. The description stays the same lines
    joined, for formats that still read it."""

    invariants: List[Invariant]
    description: str

    def add_invariant(self, text: str) -> None:
        """Append one `//` line."""
        cleaned = text.strip()
        if not cleaned:
            return
        self.invariants.append(Invariant(cleaned, len(self.invariants) + 1))
        self.description = "\n".join(item.text for item in self.invariants)

    def invariant_lines(self) -> List[str]:
        if self.invariants:
            return [item.text for item in self.invariants]
        return [line.strip() for line in (self.description or "").splitlines() if line.strip()]


_CARDINALITY = re.compile(r"^(?:\d+\.\.\*|\d+\.\.\d+|\*|\d+)$")
_ORIGIN = re.compile(r"^from\s+([A-Z][\w ]*)$")
_STEREOTYPE_NOTE = re.compile(r"^<<\s*(composition|aggregation|association)\s*>>$", re.I)


class Property(InvariantHolder, OoadNode):
    _semantic_type_name = "Property"

    def __init__(
        self,
        name: str,
        sequential_order: int = 0,
        type_hint: str = "",
        description: str = "",
        graph: Optional["Graph"] = None,
    ) -> None:
        super().__init__(name, sequential_order, graph)
        self.type_hint = type_hint
        self.description = description
        self.access = "both"
        self.stereotype = ""
        self.cardinality = ""
        self.origin = ""
        self.relationship: Relationship | None = None
        self.invariants: List[Invariant] = []
        # A derived property can ask collaborators for its value, written under it as `-> Sessions.saved`.
        self.callees: List[str] = []

    def clone(self) -> "Property":
        cloned = type(self)(self.name, self.sequential_order, self.type_hint, self.description)
        cloned.access = self.access
        cloned.stereotype = self.stereotype
        cloned.cardinality = self.cardinality
        cloned.origin = self.origin
        cloned.relationship = self.relationship.clone() if self.relationship is not None else None
        cloned.invariants = [item.clone() for item in self.invariants]
        cloned.callees = list(self.callees)
        return cloned

    def take_note(self, text: str) -> None:
        """A `//` line under the field is its stereotype, its cardinality, where it comes from, or an invariant."""
        cleaned = text.strip()
        if not cleaned:
            return
        stereotype = _STEREOTYPE_NOTE.match(cleaned)
        if stereotype:
            self.stereotype = stereotype.group(1).lower()
        elif _CARDINALITY.match(cleaned):
            self.cardinality = cleaned
        else:
            origin = _ORIGIN.match(cleaned)
            if origin:
                self.origin = origin.group(1).strip()
            else:
                self.add_invariant(cleaned)
        self.derive_relationship()

    def take_relationship(self, relationship: Relationship) -> None:
        """Become the field a relationship drawn to its type stands for: its kind, cardinality, and origin."""
        if relationship.kind:
            self.stereotype = relationship.kind
        if relationship.cardinality:
            self.cardinality = relationship.cardinality
        if relationship.description and not self.origin:
            self.origin = relationship.description
        self.derive_relationship()

    def notes(self) -> List[str]:
        """Notes written back under the field, in file order: origin, cardinality, then invariants."""
        lines: List[str] = []
        if self.origin:
            lines.append(f"from {self.origin}")
        if self.cardinality:
            lines.append(self.cardinality)
        lines.extend(self.invariant_lines())
        return lines

    def derive_relationship(self) -> None:
        """A relationship exists only when the field's type names a domain class."""
        targets = domain_type_names(self.type_hint)
        is_unmarked_collection = not self.stereotype and (self.type_hint or " ")[0].islower()
        if not targets or is_unmarked_collection:
            # An unmarked list is derived from relationships drawn elsewhere, so it adds no arrow of its own.
            self.relationship = None
            return
        kind = (self.stereotype or "association").lower()
        if kind not in {"composition", "aggregation", "association", "relative"}:
            kind = "association"
        self.stereotype = kind
        self.relationship = Relationship(
            target=targets[0],
            kind=kind,
            cardinality=self.cardinality,
            description=self.origin,
        )

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
        self.callees = list(getattr(source, "callees", []))

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        return []
