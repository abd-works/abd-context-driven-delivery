"""DDD building blocks — CE subtypes (schema ``is: class|module|property``).

BoundedContext and Aggregate subclass Module; Entity, ValueObject, Repository, and peers
subclass OoadClass; DomainEvent subclasses Property. Graph rule slugs inherit from CE via
``harness.graph.schema_rules`` (same ``is:`` mapping as schema.yaml).
"""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.model_node import ModelChildren
from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.base_class_model import Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.property import Property

# The `# Title` line of a bounded context's `.context/bounded-context.md`: the context's name.
_CONTEXT_TITLE = re.compile(r"^\s*#\s+(.+?)\s*$", re.M)

_PATTERNS = (
    "Shared Kernel",
    "Customer/Supplier",
    "Conformist",
    "Anticorruption Layer",
    "Open Host / Published Language",
    "Separate Ways",
)


# `→ Context · Aggregate · Entity`: the segments of an integration's target.
_TARGET_SEGMENT = re.compile(r"[·•]")
_ARROWS = ("→", "->")
# `Product (by ProductId)`: the identity an integration holds its target by.
_HELD_BY = "(by"


class Integration:
    """An arrow from an aggregate to another class."""

    FIELDS = ("pattern", "direction", "crosses", "integration")
    """The fields of an arc, in the order its lines write them under its target."""

    def __init__(self) -> None:
        self.context = ""
        self.aggregate = ""
        self.target = ""
        self.direction = ""
        self.crosses = ""
        self.integration = ""
        self.pattern = ""

    @property
    def target_parts(self) -> tuple[str, str, str]:
        """The target's context, aggregate, and entity; a target that names one class names only the entity."""
        text = self.target.split(_HELD_BY, 1)[0].strip()
        for arrow in _ARROWS:
            text = text.removeprefix(arrow).strip()
        parts = [part.strip() for part in _TARGET_SEGMENT.split(text) if part.strip()]
        if len(parts) == 1:
            return "", "", parts[0]
        padded = parts + ["", "", ""]
        return padded[0], padded[1], padded[2]

    @property
    def target_name(self) -> str:
        """The class the arrow points at: the entity when the target names one, else the aggregate."""
        _context, aggregate, entity = self.target_parts
        return entity or aggregate or self.aggregate

    def lines(self) -> list[str]:
        """The arc as an aggregate writes it under `Integrations:`: `- target`, then each field it has, indented."""
        return [f"- {self.target}"] + [f"  {key}: {getattr(self, key)}" for key in self.FIELDS if getattr(self, key)]


class InvariantObject(Property):
    """A property that changes with its entity. Stereotype is invariant."""

    _semantic_type_name = "InvariantObject"
    _practice_key = "ddd"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, kwargs.get("type_hint", ""), kwargs.get("description", ""))
        self.stereotype = "invariant"


class Entity(OoadClass):
    """Identity that stays the same when its values change."""

    _semantic_type_name = "Entity"
    _practice_key = "ddd"
    _belongs = {("InvariantObject", "Entity")}

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
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
    _practice_key = "ddd"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
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
    _practice_key = "ddd"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))
        self.accesses = None


class DomainService(OoadClass):
    """No state. An operation here is one no domain object can perform."""

    _semantic_type_name = "DomainService"
    _practice_key = "ddd"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class DomainEvent(Property):
    """One producer aggregate, one or many consumers, and a subject property."""

    _semantic_type_name = "DomainEvent"
    _practice_key = "ddd"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, kwargs.get("type_hint", ""), kwargs.get("description", ""))
        self.producer = None
        self.consumers = []
        self.subject = Property("subject", 0, description="the state of the event")


class Specification(OoadClass):
    _semantic_type_name = "Specification"
    _practice_key = "ddd"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class Factory(OoadClass):
    _semantic_type_name = "Factory"
    _practice_key = "ddd"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class Aggregate(Module):
    """Knows its root entity and its integrations. The entity loads invariant objects."""

    _semantic_type_name = "Aggregate"
    _practice_key = "ddd"
    _belongs = {
        ("Entity", "Aggregate"),
        ("ValueObject", "Aggregate"),
        ("Repository", "Aggregate"),
        ("DomainService", "Aggregate"),
        ("DomainEvent", "Aggregate"),
        ("Factory", "Aggregate"),
        ("Specification", "Aggregate"),
        ("OoadClass", "Aggregate"),
    }

    def __init__(self, name: str = "", sequential_order: int = 0, graph: Graph | None = None, **kwargs) -> None:
        super().__init__(name, sequential_order, graph=graph)
        self.root = None
        self.integrations = []

    def load_root(self) -> None:
        # The entity records this aggregate and loads its own invariant objects.
        if self.root is None:
            return
        self.take_root(self.root)
        self.root.load_invariant_objects()

    def take_root(self, entity: Entity) -> None:
        """Make the entity this aggregate's root, its only way in."""
        self.root = entity
        entity.is_root = True
        entity.aggregate = self

    @property
    def events(self) -> list[DomainEvent]:
        """The domain events the root emits."""
        if self.root is None:
            return []
        return [item for item in self.root.properties if isinstance(item, DomainEvent)]

    @property
    def members(self) -> list:
        """What the root holds: the invariant objects its lines name."""
        return list(self.root.invariant_objects) if self.root is not None else []


class BoundedContext(Module):
    """A module of aggregates. A nested context is a context whose parent is a context."""

    _semantic_type_name = "BoundedContext"
    _practice_key = "ddd"
    _belongs = {
        ("Aggregate", "BoundedContext"),
        ("BoundedContext", "BoundedContext"),
    }

    def __init__(self, name: str = "", sequential_order: int = 0, graph: Graph | None = None, **kwargs) -> None:
        if isinstance(name, Graph):
            graph = name
            name = "bounded context"
        super().__init__(name, sequential_order, graph=graph)
        self.owner = ""
        self.contexts = ModelChildren(self, "contexts")
        self.aggregates = ModelChildren(self, "aggregates")
        self._map: BoundedContextMap | None = None
        self.context_file_lines = 1

    @property
    def label(self) -> str:
        """The context's name, with its owner after `|` when it has one: `Customer | custom`."""
        return f"{self.name} | {self.owner}" if self.owner else self.name

    def load_context_folder(self, folder: Path) -> None:
        """Read the folder that holds this context in code: its name is the title of `.context/bounded-context.md`,
        else the folder's own name, and it owns the facts every code folder carries."""
        text = (folder / ".context" / "bounded-context.md").read_text(encoding="utf-8")
        title = _CONTEXT_TITLE.search(text)
        self.name = title.group(1).strip() if title else folder.name
        self.context_file_lines = max(1, text.count("\n") if text.endswith("\n") else text.count("\n") + 1)
        self.load_folder_facts(folder)

    def append_context(self, context: "BoundedContext") -> None:
        context._map = self._map
        self.contexts.append(context)

    def append_aggregate(self, aggregate: Aggregate) -> None:
        self.aggregates.append(aggregate)

    @property
    def every_aggregate(self) -> list[Aggregate]:
        """This context's aggregates, then those of every context nested in it."""
        found = list(self.aggregates)
        for child in self.contexts:
            found.extend(child.every_aggregate)
        return found

    @property
    def enclosing_contexts(self) -> list["BoundedContext"]:
        """The contexts this one is nested in, outermost first, ending with this context."""
        parent = self.parent
        outer = parent.enclosing_contexts if isinstance(parent, BoundedContext) else []
        return outer + [self]

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

    def __init__(self) -> None:
        self.path = ""
        self.contexts: list[BoundedContext] = []
        self.bounded_context_type = BoundedContext
        self.aggregate_type = Aggregate
        self._lines: list[str] = []
        self._index = 0

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

    def append_context(self, context: BoundedContext) -> None:
        context._map = self
        self.contexts.append(context)

    @property
    def every_aggregate(self) -> list[Aggregate]:
        """Every aggregate on the map, those in nested contexts included."""
        return [aggregate for context in self.contexts for aggregate in context.every_aggregate]

    @property
    def holds_classes_only(self) -> bool:
        """Whether the text this map read is a plain class model rather than a map: never, for a map of its own
        notation; a markdown map says so when its text names no aggregate."""
        return False
