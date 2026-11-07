"""Which DDD building block a class is, read from the stereotypes it carries.

A class says which building block it is with a stereotype — `<<Aggregate Root>>`, `<<Entity>>`, `<<Value Object>>`,
`<<Repository>>`, `<<Domain Service>>`, `<<Domain Event>>`, `<<Specification>>` — which the Clean Engineering class model
already reads into `OoadClass.stereotypes` in every format. Where code carries no stereotype, a naming convention the
tactics fidelity allows (`CartRepository`, `ShippingCode`) still names the block. A class with neither is not a
building block: a capital letter says nothing about identity or lifecycle.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import without_marks

# Each DDD stereotype, lower-cased, and the building block it names. Order matters: the first one a class carries wins.
_KIND_OF_STEREOTYPE = (
    ("aggregate root", "EntityRoot"),
    ("specification", "Specification"),
    ("entity", "Entity"),
    ("value object", "ValueObject"),
    ("repository", "Repository"),
    ("domain event", "DomainEvent"),
    ("domain service", "DomainService"),
    ("service", "DomainService"),
)
# The stereotypes DDD gives a class, lower-cased; a class's other stereotypes, such as a dataclass mark, are not DDD's.
_TACTICAL_STEREOTYPES = frozenset({stereotype for stereotype, _kind in _KIND_OF_STEREOTYPE} | {"factory", "system"})
_VALUE_OBJECT_SUFFIXES = ("Token", "Code", "Message", "Requirement", "Requirements", "Operation")
_NON_TACTICAL_SUFFIXES = ("Exception", "Error", "Client", "Node", "View", "Screen", "Routes", "Router")
_TAGGED_KINDS = frozenset({"Entity", "EntityRoot", "ValueObject", "Repository", "DomainService", "Specification"})


def plain_class_name(name: str) -> str:
    """The class name alone: no bold or code marks, stereotypes, or base classes."""
    plain = without_marks(name.replace("*", "").replace("`", ""))
    return plain.split(" extends ", 1)[0].split(" : ", 1)[0].strip()


class TacticalClass:
    """A class as DDD reads it: the class Clean Engineering read, held, with the building block its stereotypes or its
    name make it."""

    def __init__(self, oclass: OoadClass) -> None:
        self.oclass = oclass

    @property
    def name(self) -> str:
        return plain_class_name(self.oclass.name)

    @property
    def stereotypes(self) -> List[str]:
        """The class's stereotypes that are DDD building blocks, as written."""
        return [item for item in self.oclass.stereotypes if item.lower() in _TACTICAL_STEREOTYPES]

    def kind(self) -> Optional[str]:
        """The building block its stereotypes name; None for a class with none, or one marked as another system."""
        lowered = {item.lower() for item in self.oclass.stereotypes}
        if "system" in lowered:
            return None
        return next((kind for stereotype, kind in _KIND_OF_STEREOTYPE if stereotype in lowered), None)

    def inferred_kind(self, peer_names: Iterable[str]) -> Optional[str]:
        """The building block its stereotypes name, else the one its name follows the convention for."""
        named = self.kind()
        if named is not None:
            return named
        if self.name.endswith("Repository"):
            return "Repository"
        if self.name.endswith(_NON_TACTICAL_SUFFIXES):
            return None
        if self.name.endswith(_VALUE_OBJECT_SUFFIXES):
            return "ValueObject"
        return "EntityRoot" if f"{self.name}Repository" in set(peer_names) else None

    def declares_stereotype(self, graph_kind: str) -> bool:
        """True when the class carries a DDD stereotype, or its name itself says the building block it is, among the
        classes its file declares."""
        if self.stereotypes:
            return True
        names = set(self.oclass.peer_names)
        kind = self.inferred_kind(names) or graph_kind
        return self._name_says(kind if kind in _TAGGED_KINDS else graph_kind, names)

    def _name_says(self, kind: str, names: set[str]) -> bool:
        if kind == "Repository":
            return self.name.endswith("Repository")
        if kind == "DomainService":
            return self.name.endswith("Service")
        if kind == "Specification":
            return "Specification" in self.name
        if kind == "ValueObject":
            return self.name.endswith(("Token", "Code", "Message", "Value"))
        if kind == "EntityRoot":
            return self.name.endswith("Root") or f"{self.name}Repository" in names
        if kind == "Entity":
            return self.name.endswith("Entity")
        return False
