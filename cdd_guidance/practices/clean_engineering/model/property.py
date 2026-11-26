"""Property — typed field on a class."""

from __future__ import annotations

import re
from typing import List

from cdd_guidance.practices.clean_engineering.model.ooad_node import OoadNode
from cdd_guidance.practices.clean_engineering.model.field_types import RELATIONSHIP_STRENGTH, Relationship
from cdd_guidance.practices.clean_engineering.model.type_refs import domain_type_names, name_with_type


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

    def take_words_from(self, earlier: "InvariantHolder") -> None:
        """Keep the calls and the `//` lines it has, and take earlier's where it has none, as a render from a drawing
        that writes neither gives a member back what its document held."""
        if not self.callees:
            self.callees = list(earlier.callees)
        if not self.invariants:
            self.invariants = [item.clone() for item in earlier.invariants]
            self.description = earlier.description

    def invariant_lines(self) -> List[str]:
        if self.invariants:
            return [item.text for item in self.invariants]
        return [line.strip() for line in (self.description or "").splitlines() if line.strip()]


# `identity: Identity`, or `nickname?: string` for an optional field, as a model line writes a property.
_SIGNATURE = re.compile(r"^(\w+)\??\s*:\s*(.+)$")
# A model line with the relationship it may write first: `<< composition >> lines: Line`.
_MARKED_SIGNATURE = re.compile(r"^(?:<<\s*(composition|aggregation|association)\s*>>\s*)?(.*)$", re.I)
_CARDINALITY = re.compile(r"^(?:\d+\.\.\*|\d+\.\.\d+|\*|\d+)$")
_ORIGIN = re.compile(r"^from\s+([A-Z][\w ]*)$")
# The kinds of arrow a field's relationship can be; any other kind reads as an association.
_ARROW_KINDS = frozenset({"composition", "aggregation", "association", "relative"})
_STEREOTYPE_NOTE = re.compile(r"^<<\s*(composition|aggregation|association)\s*>>$", re.I)


class Property(InvariantHolder, OoadNode):
    _semantic_type_name = "Property"
    graph_facts = ("owner", "value_type")

    def __init__(self, name: str, sequential_order: int = 0, type_hint: str = "") -> None:
        super().__init__(name, sequential_order)
        self.type_hint = type_hint
        # What it says about itself: its invariant lines joined, or a note a format reads.
        self.description = ""
        self.access = "both"
        # The class that declares it, once kept (keep_owner).
        self._declared_by = ""
        self.stereotype = ""
        self.cardinality = ""
        self.origin = ""
        self.relationship: Relationship | None = None
        self.invariants: List[Invariant] = []
        # A derived property can ask collaborators for its value, written under it as `-> Sessions.saved`.
        self.callees: List[str] = []
        # The line its parser read it from, and whether it is a static field, which the class's instances do not hold.
        self.line: int | None = None
        self.is_static = False
        # The relationship arrow it stands for when its type names a domain class, a part it makes once.
        self.arrow = FieldArrow(self)

    @classmethod
    def from_signature(cls, text: str) -> "Property | None":
        """The property a typed model line such as `identity: Identity` writes; none for a line that is no typed
        property. A line may write its relationship first, as `<< composition >> lines: Line`. Every format that
        writes members as such lines reads them here."""
        marked = _MARKED_SIGNATURE.match(text.strip())
        match = _SIGNATURE.match(marked.group(2))
        if match is None:
            return None
        found = cls(match.group(1), type_hint=match.group(2).strip())
        found.stereotype = (marked.group(1) or "").lower()
        return found

    def marked_signature(self) -> str:
        """The property as a model line writes it with the relationship written on it: `<< composition >> lines: Line`."""
        return f"<< {self.stereotype} >> {self.save()}" if self.stereotype else self.save()

    @property
    def value_type(self) -> str:
        """The type a reader of this property gets: its declared type."""
        return self.type_hint

    @property
    def owner(self) -> str:
        """The name of the class that declares this property; empty before a class holds it."""
        parent = self.parent
        return parent.name if isinstance(parent, OoadNode) and parent.declares(self) else self._declared_by

    def keep_owner(self) -> None:
        """Keep the class that declares this property as its owner from now on: a graph's tree may hang it under a group
        of its class's members, and its owner, which saves with the graph, stays the class."""
        self._declared_by = self.owner

    def clone(self) -> "Property":
        cloned = type(self)(self.name, self.sequential_order, self.type_hint)
        cloned.description = self.description
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
        self.arrow.derive()

    def notes(self) -> List[str]:
        """Notes written back under the field, in file order: origin, cardinality, then invariants."""
        lines: List[str] = []
        if self.origin:
            lines.append(f"from {self.origin}")
        if self.cardinality:
            lines.append(self.cardinality)
        lines.extend(self.invariant_lines())
        return lines

    def save(self) -> str:
        return name_with_type(self.name, self.type_hint)

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


class FieldArrow:
    """The relationship arrow a property stands for, which the property makes once and keeps (``prop.arrow``): an arrow
    exists only when the field's type names a domain class, marked by its stereotype, cardinality, and origin, which an
    arrow drawn to that type, or a note under the field, gives it."""

    def __init__(self, field: Property) -> None:
        self._field = field

    def take(self, relationship: Relationship) -> None:
        """Become the arrow a relationship drawn to the field's type is: its kind, cardinality, and origin."""
        field = self._field
        if relationship.kind:
            field.stereotype = relationship.kind
        if relationship.cardinality:
            field.cardinality = relationship.cardinality
        if relationship.description and not field.origin:
            field.origin = relationship.description
        self.derive()

    def take_kind(self, kind: str) -> None:
        """Become the arrow of kind drawn to the field's type, unless a stronger kind already marks it."""
        field = self._field
        drawn = (kind or "association").lower()
        current = (field.stereotype or "").lower()
        if RELATIONSHIP_STRENGTH.get(drawn, 0) >= RELATIONSHIP_STRENGTH.get(current, 0):
            field.stereotype = drawn
        self.derive()

    def _is_unmarked_collection(self) -> bool:
        """True for a list with no stereotype written on it, which stands for no arrow of its own."""
        field = self._field
        return not field.stereotype and (field.type_hint or " ")[0].islower()

    def derive(self) -> None:
        """Give the field its relationship, which exists only when the field's type names a domain class. A field with
        no stereotype is an association and stays unmarked: the stereotype is what a person wrote or drew, and a format
        writes it back, so one put there here would come back as a mark nobody wrote."""
        field = self._field
        targets = domain_type_names(field.type_hint)
        if not targets or self._is_unmarked_collection():
            # An unmarked list is derived from relationships drawn elsewhere, so it adds no arrow of its own.
            field.relationship = None
            return
        kind = (field.stereotype or "association").lower()
        if kind not in _ARROW_KINDS:
            kind = "association"
        if field.stereotype:
            field.stereotype = kind
        field.relationship = Relationship(target=targets[0], kind=kind, cardinality=field.cardinality, description=field.origin)
