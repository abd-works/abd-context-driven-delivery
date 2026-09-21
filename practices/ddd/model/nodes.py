"""DDD node types — specialise CE Module and OoadClass."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from practices.clean_engineering.model.base_class_model import Module, OoadClass
from practices.clean_engineering.model.update_report import ChildCollectionPair

from .stereotypes import ddd_class_kind, plain_class_name

if TYPE_CHECKING:
    from practices.clean_engineering.model.operation import Operation
    from practices.clean_engineering.model.property import Property

IdentityMember = Union["Property", "Operation"]


class BoundedContext(Module):
    """Language boundary — owns Aggregates, not classes directly."""

    _semantic_type_name = "BoundedContext"

    def __init__(self, name: str, sequential_order: int, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self.aggregates: List[Aggregate] = []

    def update_self(self, source) -> None:
        assert isinstance(source, Module)
        super().update_self(source)

    def load_aggregate(self, source: "Aggregate") -> "Aggregate":
        return Aggregate(source.name, source.sequential_order)

    def child_collections(self, source) -> List[ChildCollectionPair]:
        assert isinstance(source, Module)
        if isinstance(source, BoundedContext):
            return [
                ChildCollectionPair(
                    self_children=self.aggregates,
                    source_children=source.aggregates,
                    load=self.load_aggregate,
                )
            ]
        return super().child_collections(source)


class Aggregate(Module):
    """Consistency cluster — owns domain classes; exposes one EntityRoot."""

    _semantic_type_name = "Aggregate"

    def __init__(self, name: str, sequential_order: int, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self.root: EntityRoot | None = None

    def load_class(self, source: OoadClass) -> OoadClass:
        return ddd_class_for(source)

    def child_collections(self, source) -> List[ChildCollectionPair]:
        return super().child_collections(source)


class Entity(OoadClass):
    _semantic_type_name = "Entity"

    def __init__(self, name: str, sequential_order: int, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self.identity: List[IdentityMember] = []

    def update_self(self, source) -> None:
        assert isinstance(source, OoadClass)
        super().update_self(source)
        if isinstance(source, Entity):
            self.identity = list(source.identity)


class EntityRoot(Entity):
    _semantic_type_name = "EntityRoot"

    def __init__(self, name: str, sequential_order: int, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self.aggregate: Aggregate | None = None

    def update_self(self, source) -> None:
        assert isinstance(source, OoadClass)
        super().update_self(source)
        if isinstance(source, EntityRoot):
            self.aggregate = source.aggregate


class ValueObject(OoadClass):
    _semantic_type_name = "ValueObject"


class Repository(OoadClass):
    _semantic_type_name = "Repository"

    def __init__(self, name: str, sequential_order: int, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self.accesses: EntityRoot | None = None

    def update_self(self, source) -> None:
        assert isinstance(source, OoadClass)
        super().update_self(source)
        if isinstance(source, Repository):
            self.accesses = source.accesses


class DomainEvent(OoadClass):
    _semantic_type_name = "DomainEvent"


class DomainService(OoadClass):
    _semantic_type_name = "DomainService"


_DDD_CLASS_BY_KIND = {
    "EntityRoot": EntityRoot,
    "Entity": Entity,
    "ValueObject": ValueObject,
    "Repository": Repository,
    "DomainEvent": DomainEvent,
    "DomainService": DomainService,
}


def ddd_class_for(source: OoadClass) -> OoadClass:
    """Map a CE OoadClass to the matching DDD stereotype when tags are present."""
    if isinstance(
        source,
        (EntityRoot, Entity, ValueObject, Repository, DomainEvent, DomainService),
    ):
        kind = source._semantic_type_name
    else:
        kind = ddd_class_kind(source.name)
    if kind is None:
        return OoadClass(
            name=plain_class_name(source.name),
            sequential_order=source.sequential_order,
            intent=source.intent,
        )
    cls = _DDD_CLASS_BY_KIND[kind]
    node = cls(
        name=plain_class_name(source.name),
        sequential_order=source.sequential_order,
        intent=source.intent,
    )
    if isinstance(source, Repository) and source.accesses is not None:
        node.accesses = source.accesses
    if isinstance(source, EntityRoot) and source.aggregate is not None:
        node.aggregate = source.aggregate
    if isinstance(source, Entity) and source.identity:
        node.identity = list(source.identity)
    return node
