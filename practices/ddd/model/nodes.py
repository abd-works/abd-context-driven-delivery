"""DDD building blocks. Each node loads only its own children."""

from __future__ import annotations

from pathlib import Path

from practices.clean_engineering.model.base_class_model import Module, OoadClass
from practices.clean_engineering.model.operation import Operation
from practices.clean_engineering.model.property import Property

_PATTERNS = (
    "Shared Kernel",
    "Customer/Supplier",
    "Conformist",
    "Anticorruption Layer",
    "Open Host / Published Language",
    "Separate Ways",
)


class UnsupportedBoundedContextFile(Exception):
    """No channel can read the given bounded-context file."""

    def __init__(self, path: str) -> None:
        super().__init__(f"No bounded-context channel reads {path}")
        self.path = path


class Integration:
    """An arrow from an aggregate to another class."""

    def __init__(self, source: "Integration | None" = None) -> None:
        self.context = ""
        self.aggregate = ""
        self.target = ""
        self.direction = ""
        self.crosses = ""
        self.integration = ""
        self.pattern = ""
        if source is not None:
            self.context = source.context
            self.aggregate = source.aggregate
            self.target = source.target
            self.direction = source.direction
            self.crosses = source.crosses
            self.integration = source.integration
            self.pattern = source.pattern


class InvariantObject(Property):
    """A property that changes with its entity. Stereotype is invariant."""

    _semantic_type_name = "InvariantObject"

    def __init__(self, name: str = "", sequential_order: int = 0, source: "InvariantObject | None" = None, **kwargs) -> None:
        if source is not None:
            super().__init__(source.name, source.sequential_order, source.type_hint, source.description)
            self.access = source.access
        else:
            super().__init__(name, sequential_order, kwargs.get("type_hint", ""), kwargs.get("description", ""))
        self.stereotype = "invariant"


class Entity(OoadClass):
    """Identity that stays the same when its values change."""

    _semantic_type_name = "Entity"

    def __init__(self, name: str = "", sequential_order: int = 0, source: "Entity | None" = None, **kwargs) -> None:
        if source is not None:
            super().__init__(source.name, source.sequential_order, intent=source.intent)
            self.identity = list(source.identity)
            self.is_root = source.is_root
            self.aggregate = source.aggregate
            self.invariant_objects = [
                InvariantObject(source=item) for item in source.invariant_objects
            ]
        else:
            super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))
            self.identity = []
            self.is_root = False
            self.aggregate = None
            self.invariant_objects = []
        self.invariant_object_type = InvariantObject

    def load_invariant_objects(self) -> None:
        while self.has_more_invariant_object():
            self.invariant_objects.append(self.load_next_invariant_object())

    def has_more_invariant_object(self) -> bool:
        return False

    def load_next_invariant_object(self) -> InvariantObject:
        found = self.get_next_invariant_object_from_file()
        return found

    def get_next_invariant_object_from_file(self) -> InvariantObject:
        return self.invariant_object_type(sequential_order=len(self.invariant_objects))


class ValueObject(OoadClass):
    """No write operations and no setters. create, clone, and mix return a new instance."""

    _semantic_type_name = "ValueObject"

    def __init__(self, name: str = "", sequential_order: int = 0, source: "ValueObject | None" = None, **kwargs) -> None:
        if source is not None:
            super().__init__(source.name, source.sequential_order, intent=source.intent)
        else:
            super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))

    def create(self) -> "ValueObject":
        return type(self)(self.name, self.sequential_order, intent=self.intent)

    def clone(self) -> "ValueObject":
        return type(self)(self.name, self.sequential_order, intent=self.intent)

    def mix(self, other: "ValueObject") -> "ValueObject":
        return type(self)(self.name, self.sequential_order, intent=other.intent or self.intent)


class Repository(OoadClass):
    """A collection. Operations are any of create, read, update, delete, and search."""

    _semantic_type_name = "Repository"

    def __init__(self, name: str = "", sequential_order: int = 0, source: "Repository | None" = None, **kwargs) -> None:
        if source is not None:
            super().__init__(
                source.name,
                source.sequential_order,
                intent=source.intent,
                operations=list(source.operations),
            )
            self.accesses = source.accesses
        else:
            super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))
            self.accesses = None


class DomainService(OoadClass):
    """No state. An operation here is one no domain object can perform."""

    _semantic_type_name = "DomainService"

    def __init__(self, name: str = "", sequential_order: int = 0, source: "DomainService | None" = None, **kwargs) -> None:
        if source is not None:
            super().__init__(
                source.name,
                source.sequential_order,
                intent=source.intent,
                operations=list(source.operations),
            )
        else:
            super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class DomainEvent(Property):
    """One producer aggregate, one or many consumers, and a subject property."""

    _semantic_type_name = "DomainEvent"

    def __init__(self, name: str = "", sequential_order: int = 0, source: "DomainEvent | None" = None, **kwargs) -> None:
        if source is not None:
            super().__init__(source.name, source.sequential_order, source.type_hint, source.description)
            self.access = source.access
            self.producer = source.producer
            self.consumers = list(source.consumers)
            self.subject = Property(
                source.subject.name,
                source.subject.sequential_order,
                source.subject.type_hint,
                source.subject.description,
            )
        else:
            super().__init__(
                name,
                sequential_order,
                kwargs.get("type_hint", ""),
                kwargs.get("description", ""),
            )
            self.producer = None
            self.consumers = []
            self.subject = Property("subject", 0, description="the state of the event")


class Specification(OoadClass):
    _semantic_type_name = "Specification"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class Factory(OoadClass):
    _semantic_type_name = "Factory"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class Aggregate(Module):
    """Knows its root entity and its integrations. The entity loads invariant objects."""

    _semantic_type_name = "Aggregate"

    def __init__(self, name: str = "", sequential_order: int = 0, source: "Aggregate | None" = None, **kwargs) -> None:
        if source is not None:
            super().__init__(source.name, source.sequential_order)
            self.root = None
            self.integrations = [Integration(item) for item in source.integrations]
        else:
            super().__init__(name, sequential_order)
            self.root = None
            self.integrations = []
        self._lines: list[str] = []
        self._index = 0

    def load_root(self) -> None:
        # The entity records this aggregate and loads its own invariant objects.
        if self.root is None:
            return
        self.root.is_root = True
        self.root.aggregate = self
        self.root.load_invariant_objects()


class BoundedContext(Module):
    """A module of aggregates. A nested context is a context whose parent is a context."""

    _semantic_type_name = "BoundedContext"

    def __init__(self, name: str = "", sequential_order: int = 0, source: "BoundedContext | None" = None, **kwargs) -> None:
        if source is not None:
            super().__init__(source.name, source.sequential_order)
            self.owner = source.owner
        else:
            super().__init__(name, sequential_order)
            self.owner = ""
        self.contexts: list[BoundedContext] = []
        self.aggregates: list[Aggregate] = []
        self._map: BoundedContextMap | None = None

    def append_context(self, context: "BoundedContext") -> None:
        context._map = self._map
        self.contexts.append(context)

    def append_aggregate(self, aggregate: Aggregate) -> None:
        self.aggregates.append(aggregate)

    def load_bounded_contexts(self) -> None:
        while self.has_more_bounded_context():
            self.append_context(self.load_next_bounded_context())

    def has_more_bounded_context(self) -> bool:
        return False

    def load_next_bounded_context(self) -> "BoundedContext":
        child = self.get_next_bounded_context_from_file()
        child.load_bounded_contexts()
        child.load_aggregates()
        return child

    def get_next_bounded_context_from_file(self) -> "BoundedContext":
        context_type = BoundedContext
        if self._map is not None:
            context_type = self._map.bounded_context_type
        return context_type(sequential_order=len(self.contexts) + 1)

    def load_aggregates(self) -> None:
        while self.has_more_aggregate():
            self.append_aggregate(self.load_next_aggregate())

    def has_more_aggregate(self) -> bool:
        return False

    def load_next_aggregate(self) -> Aggregate:
        aggregate = self.get_next_aggregate_from_file()
        aggregate.load_root()
        return aggregate

    def get_next_aggregate_from_file(self) -> Aggregate:
        aggregate_type = Aggregate
        if self._map is not None:
            aggregate_type = self._map.aggregate_type
        return aggregate_type(sequential_order=len(self.aggregates) + 1)


class BoundedContextMap:
    """Reads a path into bounded contexts. Each context loads its own children."""

    def __init__(self, source: "BoundedContextMap | None" = None) -> None:
        self.path = ""
        self.contexts: list[BoundedContext] = []
        self.bounded_context_type = BoundedContext
        self.aggregate_type = Aggregate
        self._lines: list[str] = []
        self._index = 0
        if source is not None:
            self.path = source.path
            for context in source.contexts:
                copied = self.bounded_context_type(source=context)
                copied._map = self
                self.contexts.append(copied)

    def load(self, path: str) -> "BoundedContextMap":
        self.path = path
        self.load_bounded_context_map_content()
        self.load_bounded_contexts()
        return self

    def save(self) -> str:
        return ""

    def load_bounded_context_map_content(self) -> None:
        return None

    def load_bounded_contexts(self) -> None:
        while self.has_more_bounded_context():
            self.contexts.append(self.load_next_bounded_context())

    def has_more_bounded_context(self) -> bool:
        return False

    def load_next_bounded_context(self) -> BoundedContext:
        context = self.get_next_bounded_context_from_file()
        context._map = self
        context.load_bounded_contexts()
        context.load_aggregates()
        return context

    def get_next_bounded_context_from_file(self) -> BoundedContext:
        return self.bounded_context_type(sequential_order=len(self.contexts) + 1)


class DDDModelFactory:
    @staticmethod
    def load(path: str) -> BoundedContextMap:
        # The file type selects the channel. That map loads itself.
        chosen = _channel_for(path)
        return chosen().load(path)


def _channel_for(path: str) -> type[BoundedContextMap]:
    from practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap

    location = Path(path)
    if location.suffix.lower() in {".md", ".markdown"}:
        return MarkdownBoundedContextMap
    raise UnsupportedBoundedContextFile(path)
