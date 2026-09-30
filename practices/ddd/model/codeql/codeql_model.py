"""CodeQL graph types for DDD — wrap live DDD types."""

from __future__ import annotations

from practices.clean_engineering.model.base_class_model import OoadClass as SourceClass
from practices.ddd.model.nodes import (
    Aggregate as SourceAggregate,
    BoundedContext as SourceBoundedContext,
    DomainEvent as SourceDomainEvent,
    DomainService as SourceDomainService,
    Entity as SourceEntity,
    Repository as SourceRepository,
    Specification as SourceSpecification,
    ValueObject as SourceValueObject,
)
from practices.ddd.model.stereotypes import ddd_class_kind, plain_class_name

from practices.clean_engineering.model.codeql.codeql_model import OoadClass, _Members
from harness.knowledge_graph.model.graph_node import Node


class BoundedContext(SourceBoundedContext, Node):
    practice = "ddd"
    _semantic_type_name = "BoundedContext"

    def load_aggregate(self, source: SourceAggregate) -> "Aggregate":
        return Aggregate(source.name, source.sequential_order)


class Aggregate(SourceAggregate, Node):
    practice = "ddd"
    _semantic_type_name = "Aggregate"

    def load_class(self, source: SourceClass) -> SourceClass:
        return ddd_graph_class_for(source)


class Entity(_Members, SourceEntity, Node):
    practice = "ddd"
    _semantic_type_name = "Entity"


class EntityRoot(_Members, SourceEntity, Node):
    practice = "ddd"
    _semantic_type_name = "EntityRoot"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self.is_root = True


class ValueObject(_Members, SourceValueObject, Node):
    practice = "ddd"
    _semantic_type_name = "ValueObject"


class Repository(_Members, SourceRepository, Node):
    practice = "ddd"
    _semantic_type_name = "Repository"


class DomainEvent(_Members, SourceDomainEvent, Node):
    practice = "ddd"
    _semantic_type_name = "DomainEvent"


class DomainService(_Members, SourceDomainService, Node):
    practice = "ddd"
    _semantic_type_name = "DomainService"


class Specification(_Members, SourceSpecification, Node):
    practice = "ddd"
    _semantic_type_name = "Specification"


_BY_KIND = {
    "EntityRoot": EntityRoot,
    "Entity": Entity,
    "ValueObject": ValueObject,
    "Repository": Repository,
    "DomainEvent": DomainEvent,
    "DomainService": DomainService,
    "Specification": Specification,
}


def ddd_graph_class_for(source: SourceClass) -> SourceClass:
    kind = ddd_class_kind(source.name)
    if isinstance(source, SourceEntity) and source.is_root:
        kind = "EntityRoot"
    elif isinstance(source, (SourceEntity, SourceValueObject, SourceRepository, SourceDomainEvent, SourceDomainService, SourceSpecification)):
        kind = source._semantic_type_name
    if kind in (None, "OoadClass"):
        return OoadClass(
            plain_class_name(source.name),
            source.sequential_order,
            intent=source.intent,
        )
    graph_cls = _BY_KIND[kind]
    node = graph_cls(
        plain_class_name(source.name),
        source.sequential_order,
        intent=source.intent,
    )
    if kind == "EntityRoot":
        node.is_root = True
    if isinstance(source, SourceRepository) and source.accesses is not None:
        node.accesses = source.accesses
    if isinstance(source, SourceEntity) and source.aggregate is not None:
        node.aggregate = source.aggregate
    if isinstance(source, SourceEntity) and source.identity:
        node.identity = list(source.identity)
    return node
