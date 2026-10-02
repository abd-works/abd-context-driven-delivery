"""Knowledge-graph channel for the DDD model."""

from __future__ import annotations

from harness.knowledge_graph.model.knowledge_graph_node import KnowledgeGraphNode
from practices.ddd.model.nodes import (
    Aggregate,
    BoundedContext,
    BoundedContextMap,
    DomainEvent,
    DomainService,
    Entity,
    Repository,
    Specification,
    ValueObject,
)


class KnowledgeGraphDomainDrivenDesignModel(BoundedContextMap, KnowledgeGraphNode):
    boundedContextType = None

    def __init__(self, source=None) -> None:
        BoundedContextMap.__init__(self, source)

    def save(self) -> str:
        return ""

    def load(self, path) -> "KnowledgeGraphDomainDrivenDesignModel":
        return self

    def parse(self, text: str) -> "KnowledgeGraphDomainDrivenDesignModel":
        return self

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return (canonical or self).save()


class KnowledgeGraphBoundedContext(BoundedContext, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        BoundedContext.__init__(self, source=source)


class KnowledgeGraphAggregate(Aggregate, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Aggregate.__init__(self, source=source)


class KnowledgeGraphEntity(Entity, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Entity.__init__(self, source=source)


class KnowledgeGraphEntityRoot(Entity, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Entity.__init__(self, source=source)


class KnowledgeGraphValueObject(ValueObject, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        ValueObject.__init__(self, source.name, source.sequential_order)


class KnowledgeGraphRepository(Repository, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Repository.__init__(self, source.name, source.sequential_order)


class KnowledgeGraphDomainEvent(DomainEvent, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        DomainEvent.__init__(self, source=source)


class KnowledgeGraphDomainService(DomainService, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        DomainService.__init__(self, source=source)


class KnowledgeGraphSpecification(Specification, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Specification.__init__(self, source.name, source.sequential_order)


KnowledgeGraphDomainDrivenDesignModel.boundedContextType = KnowledgeGraphBoundedContext
KnowledgeGraphDomainDrivenDesignModel.bounded_context_type = KnowledgeGraphBoundedContext
KnowledgeGraphDomainDrivenDesignModel.aggregate_type = KnowledgeGraphAggregate
