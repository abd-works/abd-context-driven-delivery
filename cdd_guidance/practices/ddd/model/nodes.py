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
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.ddd.model.stereotypes import TacticalClass

# The `# Title` line of a bounded context's `.context/bounded-context.md`: the context's name.
_CONTEXT_TITLE = re.compile(r"^\s*#\s+(.+?)\s*$", re.M)

# `→ Context · Aggregate · Entity`: the segments of an integration's target.
_TARGET_SEGMENT = re.compile(r"[·•]")
_ARROWS = ("→", "->")
# `Product (by ProductId)`: the identity an integration holds its target by.
_HELD_BY = "(by"
# Where a class lives, as code and class drawings keep it: the labels of the contexts that hold its aggregate, then the
# aggregate's name, `Customer | custom · Customer Profile`.
_PLACE = " · "
# A module's path: the labels of the contexts that hold it, then its own name, as Clean Engineering nests modules.
_PATH = "/"
# The context classes with no place gather in.
_DEFAULT_CONTEXT = "Domain"
# The words between the names in a type hint: `list[CartLine]`, `Map<Id, Cart>`.
_TYPE_SEPARATORS = re.compile(r"[\[\]<>|,\s]+")


class DomainNode(ModelNode):
    """A node of the DDD model. Most also subclass a Clean Engineering node, and the DDD practice registers itself on
    this class, so each is a node of the DDD practice's graph."""


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
    def code_place(self) -> str:
        """Where the aggregate lives, as code keeps it: each enclosing context's label, then its own name."""
        return _PLACE.join([context.label for context in self.parent.enclosing_contexts] + [self.name])

    @property
    def module_path(self) -> str:
        """The aggregate as a module nested in its context's module: `Sales | custom/ShoppingCart`."""
        return f"{self.parent.module_path}{_PATH}{self.name}"

    def take_class(self, oclass: OoadClass, intent: str) -> None:
        """Hold a class read from a class model, with the intent its place left."""
        oclass.intent = intent
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

    def aggregate_named(self, name: str) -> Aggregate:
        """This context's aggregate called name, opened the first time a class names it."""
        found = next((item for item in self.aggregates if item.name == name), None)
        if found is None:
            found = self._aggregate_type(name, len(self.aggregates) + 1)
            self.append_aggregate(found)
        return found

    @property
    def module_path(self) -> str:
        """The context as a module nested in the contexts around it: each enclosing context's label, joined by `/`."""
        return _PATH.join(context.label for context in self.enclosing_contexts)

    @property
    def _aggregate_type(self) -> type:
        return self._map.aggregate_type if self._map is not None else Aggregate

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
        return self._aggregate_type(sequential_order=len(self.aggregates) + 1)


class BoundedContextMap:
    """The bounded contexts of a domain, each holding its aggregates and the contexts nested in it. Each format
    subclasses the map and names the context and aggregate types it reads and writes; each context loads its own
    children."""

    bounded_context_type: type[BoundedContext] = BoundedContext
    aggregate_type: type[Aggregate] = Aggregate

    def __init__(self) -> None:
        self.contexts: list[BoundedContext] = []

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
    def every_context(self) -> list[BoundedContext]:
        """Every context on the map, each before the contexts nested in it."""
        return [found for context in self.contexts for found in context.every_context]

    def aggregate_reached_by(self, integration: Integration) -> Aggregate | None:
        """The aggregate an integration's target names: in the context it names, its entity or its aggregate; with no
        context the map holds, the aggregate called by the name it gives."""
        context_name, aggregate_name, entity_name = integration.target_parts
        if integration.context or integration.aggregate:
            context_name, aggregate_name = integration.context, integration.aggregate
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
        unplaced: list[tuple[str, OoadClass, str]] = []
        for module in model.modules:
            for oclass in module.classes:
                if oclass.name.startswith("_"):
                    continue
                place, intent = _place_of(module, oclass)
                if place:
                    self.context_at(place[:-1]).aggregate_named(place[-1]).take_class(oclass, intent)
                else:
                    unplaced.append((module.name or _DEFAULT_CONTEXT, oclass, intent))
        for context_name, aggregate_name, oclass, intent in _grouped(unplaced):
            self.context_at([context_name]).aggregate_named(aggregate_name).take_class(oclass, intent)
        for aggregate in self.every_aggregate:
            aggregate.take_root_from_classes()
        return self


def _same_name(left: str, right: str) -> bool:
    return bool(right) and left.strip().lower() == right.strip().lower()


def _place_in(text: str) -> list[str]:
    """The context labels and the aggregate name a place names: `Customer | custom · Customer Profile`."""
    return [part.strip() for part in text.split(_PLACE.strip()) if part.strip()]


def _place_of(module: Module, oclass: OoadClass) -> tuple[list[str], str]:
    """Where a class read from a class model lives, and the intent left after its place: code keeps the place as the
    first line of the class's intent, a class drawing as the class's module; none for a class with neither."""
    first, _, rest = (oclass.intent or "").partition("\n")
    place = _place_in(first)
    if len(place) < 2:
        place, rest = _place_in(module.name), oclass.intent or ""
    return (place, rest.strip()) if len(place) >= 2 else ([], rest.strip())


def _grouped(unplaced: list[tuple[str, OoadClass, str]]):
    """Classes with no place: each root, or each class nobody composes, opens an aggregate; the rest join it. A class
    the business keeps in its own repository is an aggregate root."""
    names = {oclass.name: oclass for _context, oclass, _intent in unplaced}
    owner: dict[str, str] = {}
    for _context, oclass, _intent in unplaced:
        tactical = TacticalClass(oclass)
        for prop in oclass.properties:
            for target in _TYPE_SEPARATORS.split(prop.type_hint or ""):
                if target in names and target != oclass.name and TacticalClass(names[target]).kind() != "EntityRoot":
                    owner.setdefault(target, oclass.name)
        root = names.get(tactical.kept_root_name)
        if root is not None:
            owner.setdefault(oclass.name, root.name)
            if not TacticalClass(root).stereotypes:
                root.stereotypes = ["Aggregate Root", "Entity", *root.stereotypes]
    for context, oclass, intent in unplaced:
        top = oclass.name
        seen = set()
        while top in owner and top not in seen:
            seen.add(top)
            top = owner[top]
        yield context, top, oclass, intent


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
