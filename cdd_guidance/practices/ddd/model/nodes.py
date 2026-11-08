"""DDD building blocks — CE subtypes (schema ``is: class|module|property``).

BoundedContext and Aggregate subclass Module; Entity, ValueObject, Repository, and peers
subclass OoadClass; DomainEvent subclasses Property. Graph rule slugs inherit from CE via
``harness.graph.schema_rules`` (same ``is:`` mapping as schema.yaml).
"""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.model_node import ModelChildren, ModelNode
from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import joined_module_path, module_path_in
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.type_refs import pascal_type_names
from cdd_guidance.practices.ddd.model.stereotypes import TacticalClass

# The `# Title` line of a bounded context's `.context/bounded-context.md`: the context's name.
_CONTEXT_TITLE = re.compile(r"^\s*#\s+(.+?)\s*$", re.M)

# A module's path: the labels of the contexts that hold it, then its own name, as Clean Engineering nests modules.
_PATH = "/"
# The context classes with no place gather in.
_DEFAULT_CONTEXT = "Domain"


class DomainNode(ModelNode):
    """A node of the DDD model. Most also subclass a Clean Engineering node, and the DDD practice registers itself on
    this class, so each is a node of the DDD practice's graph."""


class Integration:
    """An arrow from an aggregate to another class: the context, aggregate, and entity it reaches, the identity it holds
    that class by, and its fields. A target that names one class names only its entity."""

    FIELDS = ("pattern", "direction", "crosses", "integration")
    """The fields of an arc, in the order its lines write them under its target."""
    PARTS = ("context", "aggregate", "entity", "held_by")
    """The parts of the arc's target, each kept as its own detail when a class model keeps the arc as a dependency."""

    def __init__(self, context: str = "", aggregate: str = "", entity: str = "", held_by: str = "") -> None:
        self.context = context
        self.aggregate = aggregate
        self.entity = entity
        self.held_by = held_by
        self.direction = ""
        self.crosses = ""
        self.integration = ""
        self.pattern = ""

    @property
    def target_name(self) -> str:
        """The class the arrow points at: the entity when the target names one, else the aggregate."""
        return self.entity or self.aggregate

    def as_dependency(self) -> Relationship:
        """The arc as a class model keeps it on the aggregate's root: a dependency on the class it reaches, labelled by
        its pattern, with each part of its target and each of its other fields as a detail."""
        details = {key: getattr(self, key) for key in (*self.PARTS, *self.FIELDS[1:]) if getattr(self, key)}
        return Relationship(target=self.target_name, kind="dependency", label=self.pattern, details=details)

    @classmethod
    def keeps_one(cls, dependency: Relationship) -> bool:
        """Whether a class model's dependency keeps an arc: it names a part of the arc's target as a detail."""
        return any(dependency.details.get(key) for key in cls.PARTS)

    def read_dependency(self, dependency: Relationship) -> None:
        """Take the parts and fields a class model's dependency keeps for this arc: its pattern is the label, the rest
        details."""
        self.pattern = dependency.label
        for key in (*self.PARTS, *self.FIELDS[1:]):
            setattr(self, key, dependency.details.get(key, ""))


class InvariantObject(DomainNode, Property):
    """A property that changes with its entity. Stereotype is invariant."""

    _semantic_type_name = "InvariantObject"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, kwargs.get("type_hint", ""), kwargs.get("description", ""))
        self.stereotype = "invariant"


class Entity(DomainNode, OoadClass):
    """Identity that stays the same when its values change."""

    _semantic_type_name = "Entity"
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


class ValueObject(DomainNode, OoadClass):
    """No write operations and no setters: a change makes a new value."""

    _semantic_type_name = "ValueObject"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class Repository(DomainNode, OoadClass):
    """A collection. Operations are any of create, read, update, delete, and search."""

    _semantic_type_name = "Repository"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))
        self.accesses = None


class DomainService(DomainNode, OoadClass):
    """No state. An operation here is one no domain object can perform."""

    _semantic_type_name = "DomainService"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class DomainEvent(DomainNode, Property):
    """One producer aggregate, one or many consumers, and a subject property."""

    _semantic_type_name = "DomainEvent"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, kwargs.get("type_hint", ""), kwargs.get("description", ""))
        self.producer = None
        self.consumers = []
        self.subject = Property("subject", 0, description="the state of the event")

    def map_entry(self) -> str:
        """The event as a map's event map lists it: `CartCheckedOut: emitted by ShoppingCart; consumed by Inventory`,
        which `BoundedContextMap.wire_events` reads back."""
        producer = self.producer.name if self.producer is not None else ""
        consumers = ", ".join(item.name for item in self.consumers)
        return f"{self.name}: emitted by {producer}; consumed by {consumers}"


class Specification(DomainNode, OoadClass):
    _semantic_type_name = "Specification"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class Factory(DomainNode, OoadClass):
    _semantic_type_name = "Factory"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))


class Aggregate(DomainNode, Module):
    """Knows its root entity and its integrations. The entity loads invariant objects."""

    _semantic_type_name = "Aggregate"
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

    @property
    def place_labels(self) -> list[str]:
        """Where the aggregate lives: each enclosing context's label, then its own name."""
        return [context.label for context in self.parent.enclosing_contexts] + [self.name]

    @property
    def code_place(self) -> str:
        """The aggregate's place as one module name, as a class model names the module that holds its classes."""
        return joined_module_path(self.place_labels)

    @property
    def module_path(self) -> str:
        """The aggregate as a module nested in its context's module: `Sales | custom/ShoppingCart`."""
        return f"{self.parent.module_path}{_PATH}{self.name}"

    def take_class(self, oclass: OoadClass) -> None:
        """Hold a class read from a class model."""
        self.classes.append(oclass)

    def take_root_from_classes(self) -> None:
        """Once its classes are read, make the one marked <<Aggregate Root>> its root."""
        root = next((item for item in self.classes if isinstance(item, Entity) and TacticalClass(item).kind() == "EntityRoot"), None)
        if root is not None:
            self.take_root(root)

    def write_classes_into(self, module: Module) -> None:
        """Add each of its classes to module, a module of a Clean Engineering format, as that format's own class."""
        for oclass in self.classes:
            written = module.load_class(oclass)
            written.translate_from(oclass)
            module.classes.append(written)


class BoundedContext(DomainNode, Module):
    """A module of aggregates. A nested context is a context whose parent is a context."""

    _semantic_type_name = "BoundedContext"
    _belongs = {
        ("Aggregate", "BoundedContext"),
        ("BoundedContext", "BoundedContext"),
    }
    aggregate_type: type[Aggregate] = Aggregate
    """The aggregates this context opens: each format's context names its own format's aggregate."""

    def __init__(self, name: str = "", sequential_order: int = 0, graph: Graph | None = None, **kwargs) -> None:
        if isinstance(name, Graph):
            graph = name
            name = "bounded context"
        super().__init__(name, sequential_order, graph=graph)
        self.owner = ""
        self.contexts = ModelChildren(self, "contexts")
        self.aggregates = ModelChildren(self, "aggregates")
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
        self.contexts.append(context)

    def append_aggregate(self, aggregate: Aggregate) -> None:
        self.aggregates.append(aggregate)

    def aggregate_named(self, name: str) -> Aggregate:
        """This context's aggregate called name, opened the first time a class names it."""
        found = next((item for item in self.aggregates if item.name == name), None)
        if found is None:
            found = self.aggregate_type(name, len(self.aggregates) + 1)
            self.append_aggregate(found)
        return found

    @property
    def module_path(self) -> str:
        """The context as a module nested in the contexts around it: each enclosing context's label, joined by `/`."""
        return _PATH.join(context.label for context in self.enclosing_contexts)

    @property
    def every_aggregate(self) -> list[Aggregate]:
        """This context's aggregates, then those of every context nested in it."""
        found = list(self.aggregates)
        for child in self.contexts:
            found.extend(child.every_aggregate)
        return found

    @property
    def every_context(self) -> list["BoundedContext"]:
        """This context, then every context nested in it."""
        return [self] + [found for child in self.contexts for found in child.every_context]

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
        """The next context nested in this one, of this context's own format."""
        return type(self)(sequential_order=len(self.contexts) + 1)

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
        return self.aggregate_type(sequential_order=len(self.aggregates) + 1)


class BoundedContextMap:
    """The bounded contexts of a domain, each holding its aggregates and the contexts nested in it. Each format
    subclasses the map and names the context type it reads and writes, which names its own aggregate type; each
    context loads its own children."""

    bounded_context_type: type[BoundedContext] = BoundedContext

    def __init__(self) -> None:
        super().__init__()
        self.contexts: list[BoundedContext] = []

    def load_bounded_contexts(self) -> None:
        while self.has_more_bounded_context():
            self.contexts.append(self.load_next_bounded_context())

    def has_more_bounded_context(self) -> bool:
        return False

    def load_next_bounded_context(self) -> BoundedContext:
        context = self.get_next_bounded_context_from_file()
        context.load_bounded_contexts()
        context.load_aggregates()
        return context

    def get_next_bounded_context_from_file(self) -> BoundedContext:
        return self.bounded_context_type(sequential_order=len(self.contexts) + 1)

    def append_context(self, context: BoundedContext) -> None:
        self.contexts.append(context)

    @property
    def every_aggregate(self) -> list[Aggregate]:
        """Every aggregate on the map, those in nested contexts included."""
        return [aggregate for context in self.contexts for aggregate in context.every_aggregate]

    @property
    def every_context(self) -> list[BoundedContext]:
        """Every context on the map, each before the contexts nested in it."""
        return [found for context in self.contexts for found in context.every_context]

    def aggregate_reached_by(self, integration: Integration) -> Aggregate | None:
        """The aggregate an integration's target names: in the context it names, its entity or its aggregate; with no
        context the map holds, the aggregate called by the name it gives."""
        context_name, aggregate_name, entity_name = integration.context, integration.aggregate, integration.entity
        in_context = [item for item in self.every_aggregate if _same_name(item.parent.name, context_name)]
        if not in_context:
            return next((item for item in self.every_aggregate if _same_name(item.name, aggregate_name or entity_name)), None)
        for name in (entity_name, aggregate_name):
            found = next((item for item in in_context if name and _same_name(item.name, name)), None)
            if found is not None:
                return found
        return None

    @property
    def holds_classes_only(self) -> bool:
        """Whether the text this map read is a plain class model rather than a map: never, for a map of its own
        notation; a markdown map says so when its text names no aggregate."""
        return False

    @property
    def has_class_cards(self) -> bool:
        """Whether the map is a domain model, whose aggregates hold classes, rather than a bounded context map."""
        return any(aggregate.classes for aggregate in self.every_aggregate)

    def context_at(self, labels: list[str]) -> BoundedContext:
        """The context a place's labels name, opened the first time: a nested context sits in the one before it."""
        holder: BoundedContextMap | BoundedContext = self
        for label in labels:
            name, _, owner = label.partition("|")
            context = next((item for item in holder.contexts if item.label == label.strip()), None)
            if context is None:
                context = self.bounded_context_type(name.strip(), len(holder.contexts) + 1)
                context.owner = owner.strip()
                holder.append_context(context)
            holder = context
        return holder

    def aggregate_at(self, path: str) -> Aggregate:
        """The aggregate a module path names, `Sales | custom/ShoppingCart`, opened the first time."""
        labels = path.split(_PATH)
        return self.context_at(labels[:-1]).aggregate_named(labels[-1])

    def wire_events(self, entries: list[str]) -> None:
        """Read each `Event: emitted by Producer; consumed by A, B` entry of an event map onto its producer's root."""
        aggregates = {item.name: item for item in self.every_aggregate}
        services: dict[str, DomainService] = {}
        for entry in entries:
            _wire_event(entry, aggregates, services)

    def write_classes(self, model: CleanEngineeringModel) -> None:
        """Write this map into model, a Clean Engineering model of some format, as that format's own modules and
        classes: one module per aggregate, named by the aggregate's place, holding a class for each of its building
        blocks."""
        modules: list[Module] = []
        for aggregate in self.every_aggregate:
            module = model.load_module(aggregate)
            module.name = aggregate.code_place
            module.sequential_order = len(modules) + 1
            aggregate.write_classes_into(module)
            modules.append(module)
        model.modules = modules

    def read_class_model(self, model: CleanEngineeringModel) -> "BoundedContextMap":
        """Read a class model written as code or drawn as classes into this map, and return it: each class's place
        names its context and aggregate, which takes the class; classes with no place gather around the roots that
        hold them."""
        self.contexts = []
        unplaced: list[tuple[str, OoadClass]] = []
        for module in model.modules:
            for oclass in module.classes:
                if oclass.name.startswith("_"):
                    continue
                place = _place_of(module, oclass)
                if place:
                    self.context_at(place[:-1]).aggregate_named(place[-1]).take_class(oclass)
                else:
                    unplaced.append((module.name or _DEFAULT_CONTEXT, oclass))
        for context_name, aggregate_name, oclass in _grouped(unplaced):
            self.context_at([context_name]).aggregate_named(aggregate_name).take_class(oclass)
        for aggregate in self.every_aggregate:
            aggregate.take_root_from_classes()
        return self


def _same_name(left: str, right: str) -> bool:
    return bool(right) and left.strip().lower() == right.strip().lower()


def _place_of(module: Module, oclass: OoadClass) -> list[str]:
    """Where a class read from a class model lives, its contexts' labels then its aggregate: the module path code names
    for it, else the module a class drawing keeps it in; none for a class with neither."""
    for place in (oclass.module_path, module_path_in(module.name)):
        if len(place) >= 2:
            return list(place)
    return []


def _grouped(unplaced: list[tuple[str, OoadClass]]):
    """Classes with no place: each root, or each class nobody composes, opens an aggregate; the rest join it. A class
    the business keeps in its own repository is an aggregate root."""
    names = {oclass.name: oclass for _context, oclass in unplaced}
    owner: dict[str, str] = {}
    for _context, oclass in unplaced:
        tactical = TacticalClass(oclass)
        for prop in oclass.properties:
            for target in pascal_type_names(prop.type_hint or ""):
                if target in names and target != oclass.name and TacticalClass(names[target]).kind() != "EntityRoot":
                    owner.setdefault(target, oclass.name)
        root = names.get(tactical.kept_root_name)
        if root is not None:
            owner.setdefault(oclass.name, root.name)
            if not TacticalClass(root).stereotypes:
                root.stereotypes = ["Aggregate Root", "Entity", *root.stereotypes]
    for context, oclass in unplaced:
        top = oclass.name
        seen = set()
        while top in owner and top not in seen:
            seen.add(top)
            top = owner[top]
        yield context, top, oclass


def _wire_event(text: str, aggregates: dict[str, Aggregate], services: dict[str, DomainService]) -> None:
    # CartCheckedOut: emitted by ShoppingCart; consumed by Inventory, Receipt
    name, _, rest = text.partition(":")
    emitted, _, consumed = rest.partition("consumed by")
    producer = aggregates.get(emitted.replace("emitted by", "").strip(" ;"))
    if producer is None or producer.root is None:
        return
    event = next((item for item in producer.events if item.name == name.strip()), None)
    if event is None:
        event = DomainEvent(name.strip(), len(producer.root.properties))
        producer.root.properties.append(event)
    event.producer = producer
    event.subject = Property("subject", 0, description="the state of the event")
    for part in consumed.split(","):
        consumer_name = part.strip()
        if consumer_name:
            event.consumers.append(_consumer(consumer_name, aggregates, services, len(event.consumers) + 1))


def _consumer(name: str, aggregates: dict[str, Aggregate], services: dict[str, DomainService], order: int):
    """The aggregate a consumer names, else the domain service it names, made once per map."""
    if name in aggregates:
        return aggregates[name]
    if name not in services:
        services[name] = DomainService(name, order)
    return services[name]
