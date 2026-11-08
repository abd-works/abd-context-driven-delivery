"""Which DDD building block a class is, read from the stereotypes it carries.

A class says which building block it is with a stereotype — `<<Aggregate Root>>`, `<<Entity>>`, `<<Value Object>>`,
`<<Repository>>`, `<<Domain Service>>`, `<<Domain Event>>`, `<<Specification>>`, `<<Factory>>` — which the Clean
Engineering class model already reads into `OoadClass.stereotypes` in every format. Where code carries no stereotype, a
naming convention the tactics fidelity allows (`CartRepository`, `ShippingCode`) still names the block. A class with
neither is not a building block: a capital letter says nothing about identity or lifecycle.

This is the one table of stereotypes and building-block kinds: the markdown cards, the graph's building blocks, and the
tactical rules all read it.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import without_marks

# Each DDD stereotype, lower-cased, and the building block it names. Order matters: the first one a class carries wins.
KIND_OF_STEREOTYPE = (
    ("aggregate root", "EntityRoot"),
    ("specification", "Specification"),
    ("entity", "Entity"),
    ("value object", "ValueObject"),
    ("repository", "Repository"),
    ("domain event", "DomainEvent"),
    ("domain service", "DomainService"),
    ("service", "DomainService"),
    ("factory", "Factory"),
)
# The kinds of class a building block can be, which the tactical rules check.
BUILDING_BLOCK_KINDS = ("EntityRoot", "Entity", "ValueObject", "Repository", "DomainService", "Factory", "Specification")
# A class marked as another system's is not one of this domain's building blocks.
_SYSTEM = "system"
# The stereotypes DDD gives a class, lower-cased; a class's other stereotypes, such as a dataclass mark, are not DDD's.
_TACTICAL_STEREOTYPES = frozenset({stereotype for stereotype, _kind in KIND_OF_STEREOTYPE} | {_SYSTEM})
_REPOSITORY = "Repository"
_VALUE_OBJECT_SUFFIXES = ("Token", "Code", "Message", "Requirement", "Requirements", "Operation")
_NON_TACTICAL_SUFFIXES = ("Exception", "Error", "Client", "Node", "View", "Screen", "Routes", "Router")
# The naming convention of each building block: the words a class name ends with to say it is that block. This is the
# one convention: inferring a block from a name and checking that a name says its block both read it.
_NAME_ENDINGS = {
    "Repository": (_REPOSITORY,),
    "ValueObject": _VALUE_OBJECT_SUFFIXES,
    "DomainService": ("Service",),
    "Entity": ("Entity",),
    "EntityRoot": ("Root",),
}
_SPECIFICATION = "Specification"


def plain_class_name(name: str) -> str:
    """The class name alone: no bold or code marks, stereotypes, or base classes."""
    plain = without_marks(name.replace("*", "").replace("`", ""))
    return plain.split(" extends ", 1)[0].split(" : ", 1)[0].strip()


def root_kept_by(class_name: str) -> Optional[str]:
    """The class a repository called class_name says it keeps: `Cart` for `CartRepository`; None for any other name."""
    name = plain_class_name(class_name)
    if name.endswith(_REPOSITORY) and name != _REPOSITORY:
        return name[: -len(_REPOSITORY)]
    return None


def kind_named_by(stereotypes: Iterable[str]) -> Optional[str]:
    """The building block a list of stereotypes names; None for none, or for a class marked as another system's."""
    lowered = {item.lower() for item in stereotypes}
    if marks_another_system(lowered):
        return None
    return next((kind for stereotype, kind in KIND_OF_STEREOTYPE if stereotype in lowered), None)


def marks_another_system(stereotypes: Iterable[str]) -> bool:
    """Whether the stereotypes mark a class as another system's, which is none of this domain's building blocks."""
    return _SYSTEM in {item.lower() for item in stereotypes}


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

    @property
    def kept_root_name(self) -> Optional[str]:
        """The class a repository's name says it keeps: `Cart` for `CartRepository`; None for any other name."""
        return root_kept_by(self.name)

    @property
    def building_block_stereotypes(self) -> List[str]:
        """The DDD stereotypes the class carries, else `Repository` when its name says it keeps a root."""
        return self.stereotypes or ([_REPOSITORY] if self.kept_root_name else [])

    def kind(self) -> Optional[str]:
        """The building block its stereotypes name; None for a class with none, or one marked as another system."""
        return kind_named_by(self.oclass.stereotypes)

    def inferred_kind(self, peer_names: Iterable[str]) -> Optional[str]:
        """The building block its stereotypes name, else the one its name follows the convention for."""
        named = self.kind()
        if named is not None:
            return named
        if self.name.endswith(_NAME_ENDINGS[_REPOSITORY]):
            return _REPOSITORY
        if self.name.endswith(_NON_TACTICAL_SUFFIXES):
            return None
        if self.name.endswith(_NAME_ENDINGS["ValueObject"]):
            return "ValueObject"
        return "EntityRoot" if self.repository_name in set(peer_names) else None

    @property
    def repository_name(self) -> str:
        """The name of the repository that would keep this class: `CartRepository` for `Cart`."""
        return f"{self.name}{_REPOSITORY}"

    def name_says(self, kind: str) -> bool:
        """True when the class's name follows the naming convention of the building block kind: a root is also named
        by the repository beside it among the classes its file declares."""
        if kind == _SPECIFICATION:
            return _SPECIFICATION in self.name
        if kind == "EntityRoot" and self.repository_name in set(self.oclass.peer_names):
            return True
        return self.name.endswith(_NAME_ENDINGS.get(kind, ())) if kind in _NAME_ENDINGS else False
