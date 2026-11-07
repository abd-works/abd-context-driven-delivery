"""DDD building blocks — CE subtypes (schema ``is: class|module|property``).

BoundedContext and Aggregate subclass Module; Entity, ValueObject, Repository, and peers
subclass OoadClass; DomainEvent subclasses Property. Graph rule slugs inherit from CE via
``harness.graph.schema_rules`` (same ``is:`` mapping as schema.yaml).
"""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.bound_node import BoundChildren
from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.base_class_model import Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.operation import Operation
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


class InvariantObject(Property):
    """A property that changes with its entity. Stereotype is invariant."""

    _semantic_type_name = "InvariantObject"
    _graph_practice = "ddd"

    def __init__(self, name: str = "", sequential_order: int = 0, source: "InvariantObject | None" = None, **kwargs) -> None:
        if source is not None:
            super().__init__(source.name, source.sequential_order, source.type_hint, source.description)
            self.access = source.access
        else:
            super().__init__(name, sequential_order, kwargs.get("type_hint", ""), kwargs.get("description", ""))
        self.stereotype = "invariant"


_DERIVE_PREFIX = re.compile(r"^derive\w*", re.IGNORECASE)
_ONLY_DELEGATES = re.compile(r"return\s+\w+\.\w+\s*\(")
_LOAD_NAMES = frozenset({"load", "get", "find", "fetch"})
# A load with no identity is fine when it returns the one record its store holds; it is wrong when it finds the
# identity in ambient state (the session, the request, a cookie, the signed-in user, the browser).
_AMBIENT_STATE = re.compile(
    r"(?<![A-Za-z])(?:[Ss]ession|[Cc]urrent|[Rr]eq(?:uest)?|[Cc]ookies?|[Aa]uth|[Ll]ogged|[Cc]tx|[Cc]ontext"
    r"|localStorage|sessionStorage|window|process\.env)(?![a-z])"
)


class TacticalBuildingBlock(OoadClass):
    """A class-shaped DDD building block. Loads the tactical facts DDD rules read from its graph node.

    The block is the parsed class seen through DDD, so it also carries that class's own facts.
    """

    graph_facts = OoadClass.graph_facts + (
        "peer_private_operations",
        "public_derive_operations",
        "delegating_operations",
        "identity_free_loads",
        "tactical_stereotype",
    )

    def load_tactical_facts(self, parsed: OoadClass, file_text: str) -> None:
        """Fill the facts this building block owns, from the class its language parser read and the file around it.

        Each operation's body is the one the parser already read; only the class declaration's stereotype marks,
        which sit above the class, come from the file text."""
        from cdd_guidance.practices.ddd.model.stereotypes import declares_tactical_stereotype

        for name in OoadClass.graph_facts:
            if hasattr(parsed, name):
                setattr(self, name, getattr(parsed, name))
        operations = parsed.own_operations()
        public = [op for op in operations if op.name and not op.name.startswith("_")]
        self.peer_private_operations = [op.name for op in operations if op.peer_private_access]
        self.public_derive_operations = [op.name for op in public if _DERIVE_PREFIX.match(op.name)]
        self.delegating_operations = [op.name for op in public if _ONLY_DELEGATES.search(op.body.text)]
        self.identity_free_loads = [
            op.name
            for op in operations
            if op.name.lower() in _LOAD_NAMES and not op.parameters and _AMBIENT_STATE.search(op.body.text)
        ]
        self.tactical_stereotype = declares_tactical_stereotype(
            file_text, parsed.name, self.tactical_kind(), set(parsed.peer_names)
        )

    def tactical_kind(self) -> str:
        return "EntityRoot" if getattr(self, "is_root", False) else self._semantic_type_name


class Entity(TacticalBuildingBlock):
    """Identity that stays the same when its values change."""

    _semantic_type_name = "Entity"
    _graph_practice = "ddd"
    _belongs = {("InvariantObject", "Entity")}

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


class ValueObject(TacticalBuildingBlock):
    """No write operations and no setters. create, clone, and mix return a new instance."""

    _semantic_type_name = "ValueObject"
    _graph_practice = "ddd"

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


class Repository(TacticalBuildingBlock):
    """A collection. Operations are any of create, read, update, delete, and search."""

    _semantic_type_name = "Repository"
    _graph_practice = "ddd"

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


class DomainService(TacticalBuildingBlock):
    """No state. An operation here is one no domain object can perform."""

    _semantic_type_name = "DomainService"
    _graph_practice = "ddd"

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
    _graph_practice = "ddd"

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


class Specification(TacticalBuildingBlock):
    _semantic_type_name = "Specification"
    _graph_practice = "ddd"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class Factory(TacticalBuildingBlock):
    _semantic_type_name = "Factory"
    _graph_practice = "ddd"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


# Which building block a class card's stereotypes make it, first match first; a card with none is a plain class.
_BLOCK_TYPES: tuple[tuple[str, type[OoadClass]], ...] = (
    ("specification", Specification),
    ("value object", ValueObject),
    ("repository", Repository),
    ("domain service", DomainService),
    ("service", DomainService),
    ("factory", Factory),
    ("entity", Entity),
    ("aggregate root", Entity),
)


def building_block_type(stereotypes: list[str]) -> type[OoadClass]:
    """The class a card with these stereotypes is read into."""
    marks = {item.lower() for item in stereotypes}
    return next((block for mark, block in _BLOCK_TYPES if mark in marks), OoadClass)


class Aggregate(Module):
    """Knows its root entity and its integrations. The entity loads invariant objects."""

    _semantic_type_name = "Aggregate"
    _graph_practice = "ddd"
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


class BoundedContext(Module):
    """A module of aggregates. A nested context is a context whose parent is a context."""

    _semantic_type_name = "BoundedContext"
    _graph_practice = "ddd"
    _belongs = {
        ("Aggregate", "BoundedContext"),
        ("BoundedContext", "BoundedContext"),
    }

    def __init__(self, name: str = "", sequential_order: int = 0, source: "BoundedContext | None" = None, graph: Graph | None = None, **kwargs) -> None:
        if isinstance(name, Graph):
            graph = name
            name = "bounded context"
        if source is not None:
            super().__init__(source.name, source.sequential_order, graph=graph)
            self.owner = source.owner
        else:
            super().__init__(name, sequential_order, graph=graph)
            self.owner = ""
        self.contexts = BoundChildren(self, "contexts")
        self.aggregates = BoundChildren(self, "aggregates")
        self._map: BoundedContextMap | None = None
        self.context_file_lines = 1
        if graph is None:
            return
        others = [
            node
            for node in self._copies_on_graph("BoundedContext")
            if node.aggregates or node.contexts
        ]
        if not others:
            return
        for child in others[0].contexts:
            self.append_context(BoundedContext(child.name, child.sequential_order))
        for aggregate in others[0].aggregates:
            self.append_aggregate(aggregate.clone())

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

    def append_context(self, context: BoundedContext) -> None:
        context._map = self
        self.contexts.append(context)

    @property
    def every_aggregate(self) -> list[Aggregate]:
        """Every aggregate on the map, those in nested contexts included."""
        return [aggregate for context in self.contexts for aggregate in context.every_aggregate]
