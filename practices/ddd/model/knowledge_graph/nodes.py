"""Knowledge-graph channel for the DDD model."""

from __future__ import annotations

from pathlib import Path

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
        BoundedContextMap.__init__(self)
        self.bounded_context_type = KnowledgeGraphBoundedContext
        self.aggregate_type = KnowledgeGraphAggregate
        if source is None:
            return
        self.path = source.path
        for context in source.contexts:
            copied = KnowledgeGraphBoundedContext(source=context)
            copied._map = self
            self.contexts.append(copied)

    def save(self) -> str:
        if self.path and Path(self.path).is_file():
            return Path(self.path).read_text(encoding="utf-8")
        return _write_map(self)

    def load(self, path) -> "KnowledgeGraphDomainDrivenDesignModel":
        from practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap

        target = Path(path)
        if target.is_dir():
            for name in ("bounded-context-map.kg", "bounded-context-map.md"):
                candidate = target / name
                if candidate.is_file():
                    target = candidate
                    break
        if not target.is_file():
            return self
        parsed = MarkdownBoundedContextMap().parse(target.read_text(encoding="utf-8"))
        return type(self)(parsed)

    def parse(self, text: str) -> "KnowledgeGraphDomainDrivenDesignModel":
        from practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap

        return type(self)(MarkdownBoundedContextMap().parse(text))

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return (canonical or self).save()


class KnowledgeGraphBoundedContext(BoundedContext, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        BoundedContext.__init__(self, source=source)
        for aggregate in source.aggregates:
            self.append_aggregate(KnowledgeGraphAggregate(source=aggregate))
        for child in source.contexts:
            self.append_context(KnowledgeGraphBoundedContext(child))


class KnowledgeGraphAggregate(Aggregate, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Aggregate.__init__(self, source=source)
        if source.root is None:
            return
        self.root = KnowledgeGraphEntity(source=source.root)
        self.root.aggregate = self
        self.root.is_root = True
        self.root.properties = []
        for item in source.root.properties:
            if isinstance(item, DomainEvent):
                event = KnowledgeGraphDomainEvent(source=item)
                event.producer = self
                self.root.properties.append(event)
            else:
                self.root.properties.append(item)


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


def _write_map(model) -> str:
    lines = ["# Bounded Context Map", ""]
    for context in model.contexts:
        lines.append(f"## {context.name} | {context.owner}")
        lines.append("")
        for aggregate in context.aggregates:
            lines.append(f"### {aggregate.name}")
            lines.append("")
            if aggregate.root is not None:
                lines.append(aggregate.root.name)
                for item in aggregate.root.invariant_objects:
                    lines.append(f"  {item.name}")
            lines.append("")
    return "\n".join(lines)


KnowledgeGraphDomainDrivenDesignModel.boundedContextType = KnowledgeGraphBoundedContext
KnowledgeGraphDomainDrivenDesignModel.bounded_context_type = KnowledgeGraphBoundedContext
KnowledgeGraphDomainDrivenDesignModel.aggregate_type = KnowledgeGraphAggregate
