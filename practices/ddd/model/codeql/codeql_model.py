"""CodeQL graph types for DDD — wrap live DDD types."""

from __future__ import annotations

from practices.clean_engineering.model.base_class_model import OoadClass as SourceClass
from practices.ddd.model.nodes import (
    Aggregate as SourceAggregate,
    BoundedContext as SourceBoundedContext,
    DomainEvent as SourceDomainEvent,
    DomainService as SourceDomainService,
    Entity as SourceEntity,
    EntityRoot as SourceEntityRoot,
    Repository as SourceRepository,
    ValueObject as SourceValueObject,
    ddd_class_for,
)
from practices.ddd.model.stereotypes import plain_class_name

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


class EntityRoot(_Members, SourceEntityRoot, Node):
    practice = "ddd"
    _semantic_type_name = "EntityRoot"


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


_BY_KIND = {
    "EntityRoot": EntityRoot,
    "Entity": Entity,
    "ValueObject": ValueObject,
    "Repository": Repository,
    "DomainEvent": DomainEvent,
    "DomainService": DomainService,
}


def ddd_graph_class_for(source: SourceClass) -> SourceClass:
    base = ddd_class_for(source)
    kind = base._semantic_type_name
    if kind == "OoadClass":
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
    if isinstance(base, SourceRepository) and base.accesses is not None:
        node.accesses = base.accesses
    if isinstance(base, SourceEntityRoot) and base.aggregate is not None:
        node.aggregate = base.aggregate
    if isinstance(base, SourceEntity) and base.identity:
        node.identity = list(base.identity)
    return node
