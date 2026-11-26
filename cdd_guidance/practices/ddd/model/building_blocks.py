"""DDD's building blocks — Clean Engineering subtypes (schema ``is: class|property``).

Entity, ValueObject, Repository, and their peers subclass *OoadClass* through *DomainClass*; DomainEvent and
InvariantObject subclass *Property*. A building block is also a card every DDD format reads and writes: the class with
its stereotypes, its members, and the invariants it lists. Each format writes the card in its own notation (a markdown
`####` section, a sketch fence, a class drawing), so the card's fields and what it does live here, on the block itself.
"""

from __future__ import annotations

from harness.graph.model_node import ModelNode

from cdd_guidance.practices.clean_engineering.model import Module, OoadClass
from cdd_guidance.practices.clean_engineering.model import Operation
from cdd_guidance.practices.clean_engineering.model import Property
from cdd_guidance.practices.clean_engineering.model import marks_in
from cdd_guidance.practices.ddd.model.stereotypes import TacticalClass, kind_named_by, plain_class_name

# The order a card writes the stereotypes it knows, before any other.
_ORDER = ("Aggregate Root", "Entity", "Value Object", "Repository")


def plain_name(text: str) -> str:
    """A name as a DDD document writes it: without bold or code marks, and before a `|`, which names an owner."""
    name = text.replace("**", "").replace("`", "").strip()
    return name.split("|", 1)[0].strip()


def member_name(text: str) -> str:
    """A member line's name: every word it holds, the choices after a `|` included, since only a heading's `|` names
    an owner."""
    return text.replace("**", "").replace("`", "").strip()


def owner_from(heading: str) -> str:
    """The owner a context heading names after its `|`; none for a heading with no `|`."""
    return heading.split("|", 1)[1].strip() if "|" in heading else ""


def ordered_stereotypes(found: list[str]) -> list[str]:
    """The stereotypes a card writes: those it knows in their order, then the rest as found."""
    known = [item for item in _ORDER if any(item.lower() == mark.lower() for mark in found)]
    return known + [item for item in found if item.lower() not in {mark.lower() for mark in known}]


def called_class(callee: str) -> str:
    """The class a call names before its operation: `BookRepository` of `BookRepository.load(bookId)`; none for a call
    that names only an operation."""
    named = callee.strip().partition(".")[0].partition("(")[0].strip()
    return named if named[:1].isupper() else ""


class DomainNode(ModelNode):
    """A node of the DDD model. Most also subclass a Clean Engineering node, and the DDD practice registers itself on
    this class, so each is a node of the DDD practice's graph."""


class InvariantObject(DomainNode, Property):
    """A property that changes with its entity. Stereotype is invariant."""

    _semantic_type_name = "InvariantObject"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, kwargs.get("type_hint", ""))
        self.description = kwargs.get("description", "")
        self.stereotype = "invariant"


class DomainClass(DomainNode, OoadClass):
    """A class of the DDD model: a Clean Engineering class that is one of the domain's building blocks, made with its
    name, its order, and its intent. It holds its *TacticalClass*, the one reading of which building block its
    stereotypes make it, and it is the card every format writes for it: its stereotypes, its members, the invariants
    it lists, and whether the document writes its repository inside its root's card. A class whose stereotypes name
    no building block is a plain *DomainClass*."""

    # Whether its aggregate made it the root, which a card marked <<Aggregate Root>> is already.
    _made_root = False

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, intent=kwargs.get("intent", ""))
        self.tactical = TacticalClass(self)
        self.invariants: list[str] = []
        # A repository the document writes inside its root's card, under a `**Name** «Repository»` line, rather than
        # under a `####` heading of its own. Every drawing draws a repository inside its root's card either way.
        self.written_in_root = False

    @staticmethod
    def named(name: str, stereotypes: list[str]) -> "DomainClass":
        """An empty card of the building block its stereotypes name; a plain class for none."""
        marks = ordered_stereotypes(stereotypes)
        card = _BLOCK_OF_KIND.get(kind_named_by(marks), DomainClass)(name, 0)
        card.stereotypes = marks
        return card

    @staticmethod
    def from_heading(heading: str) -> "DomainClass":
        """An empty card for `Name <<Stereotype>> …`."""
        return DomainClass.named(plain_class_name(heading), marks_in(heading))

    @staticmethod
    def from_code(oclass: OoadClass) -> "DomainClass":
        """The card a class read from code or a class drawing is: the building block its DDD stereotypes, or its name,
        make it, holding the class's own members, without its constructor, and its intent."""
        card = DomainClass.named(oclass.name, TacticalClass(oclass).building_block_stereotypes)
        card.sequential_order = oclass.sequential_order
        card.intent = oclass.intent
        card.properties = list(oclass.properties)
        card.operations = [item for item in oclass.operations if not item.is_constructor and item.name != oclass.name]
        return card

    @property
    def is_root(self) -> bool:
        """True when the card is marked <<Aggregate Root>>, or its aggregate made it its root."""
        return self._made_root or self.tactical.kind() == "EntityRoot"

    @is_root.setter
    def is_root(self, value: bool) -> None:
        self._made_root = value

    @property
    def is_repository(self) -> bool:
        return self.tactical.kind() == "Repository"

    @property
    def heading(self) -> str:
        """The card's name and its stereotypes: `Cart <<Aggregate Root>> <<Entity>>`."""
        return f"{self.name} {' '.join(f'<<{item}>>' for item in self.stereotypes)}".rstrip()

    @property
    def plain_properties(self) -> list[Property]:
        """What the class holds — not the events or invariant objects DDD hangs on the same list."""
        return [
            item for item in self.properties
            if isinstance(item, Property) and not isinstance(item, (DomainEvent, InvariantObject))
        ]

    def take_words_from(self, earlier: "DomainClass", drawn_in: dict[str, str]) -> None:
        """Keep the invariants, intent, and member words it has, and take earlier's where it has none, as a card read
        from a drawing takes what the document it is written onto held: where that document writes its repository,
        each property's note and the relationship a drawing shows no arrow for, and each operation's note and calls.
        drawn_in names the card each class of the document is drawn inside, by the class's name, for each class drawn
        inside another's card, as each repository is drawn inside its root's."""
        self.invariants = self.invariants or list(earlier.invariants)
        self.intent = self.intent or earlier.intent
        self.written_in_root = earlier.written_in_root
        written_properties = {item.name: item for item in earlier.plain_properties}
        for prop in self.plain_properties:
            written = written_properties.get(prop.name)
            if written is not None:
                prop.description = prop.description or written.description
                if written.type_hint == prop.type_hint and not prop.stereotype:
                    prop.stereotype = written.stereotype
        written_operations = {item.name: item for item in earlier.operations}
        for operation in self.operations:
            if operation.name in written_operations:
                self._take_operation_words(written_operations[operation.name], operation, drawn_in)

    def _take_operation_words(self, earlier: Operation, operation: Operation, drawn_in: dict[str, str]) -> None:
        """The operation's note, and its calls as the document writes them: every call inside the card's aggregate,
        which no arrow shows, each call to another aggregate whose arrow still reaches the card the called class is
        drawn in, then each arrow the document has no call for."""
        operation.description = operation.description or earlier.description
        arrows = {called_class(callee) for callee in operation.callees}
        local = {card.name for card in self.parent.classes} if self.parent is not None else {self.name}

        def card_of(callee: str) -> str:
            return drawn_in.get(called_class(callee), called_class(callee))

        kept = [callee for callee in earlier.callees if called_class(callee) in local | {""} or card_of(callee) in arrows]
        written = {card_of(callee) for callee in kept}
        operation.callees = kept + [callee for callee in operation.callees if called_class(callee) not in written]

    def write_into(self, module: Module, place: list[str]) -> OoadClass:
        """Add this card to module, a module of a Clean Engineering format, as that format's own class: its
        stereotypes, its intent, its members, with the relationships their types name, and the place of its aggregate
        as its module path."""
        written = module.load_class(self)
        written.update_self(self)
        written.sequential_order = len(module.classes) + 1
        written.module_path = list(place)
        written.properties = [written.load_property(item) for item in self.plain_properties]
        written.operations = [written.load_operation(item) for item in self.operations]
        for prop in written.properties:
            prop.arrow.derive()
        module.classes.append(written)
        return written


class Entity(DomainClass):
    """Identity that stays the same when its values change. An entity a document names as an aggregate's root, with the
    member lines under it, reads those lines as its invariant objects."""

    _semantic_type_name = "Entity"
    _belongs = {("InvariantObject", "Entity")}

    def __init__(self, name: str = "", sequential_order: int = 0, member_lines: list[str] | None = None, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self.identity = []
        self.is_root = False
        self.aggregate = None
        self.invariant_objects = []
        self._member_lines = list(member_lines or [])

    def load_invariant_objects(self) -> None:
        """Read each member line under the root as one of its invariant objects, once."""
        for line in self._member_lines:
            self.invariant_objects.append(InvariantObject(member_name(line), len(self.invariant_objects)))
        self._member_lines = []


class ValueObject(DomainClass):
    """No write operations and no setters: a change makes a new value."""

    _semantic_type_name = "ValueObject"


class Repository(DomainClass):
    """A collection. Operations are any of create, read, update, delete, and search."""

    _semantic_type_name = "Repository"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self.accesses = None


class DomainService(DomainClass):
    """No state. An operation here is one no domain object can perform."""

    _semantic_type_name = "DomainService"


class DomainEvent(DomainNode, Property):
    """One producer aggregate, one or many consumers, and a subject property."""

    _semantic_type_name = "DomainEvent"

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, kwargs.get("type_hint", ""))
        self.description = kwargs.get("description", "")
        self.producer = None
        self.consumers = []
        self.subject = self._blank_subject()

    def _blank_subject(self) -> Property:
        """The subject property an event starts with: the state of the event, with no fields read yet."""
        subject = Property("subject", 0)
        subject.description = "the state of the event"
        return subject

    def emitted_by(self, producer) -> None:
        """Become the event producer, an aggregate, emits, starting again from a blank subject."""
        self.producer = producer
        self.subject = self._blank_subject()

    def map_entry(self) -> str:
        """The event as a map's event map lists it: `CartCheckedOut: emitted by ShoppingCart; consumed by Inventory`,
        which `BoundedContextMap.wire_events` reads back."""
        producer = self.producer.name if self.producer is not None else ""
        consumers = ", ".join(item.name for item in self.consumers)
        return f"{self.name}: emitted by {producer}; consumed by {consumers}"


class Specification(DomainClass):
    _semantic_type_name = "Specification"


class Factory(DomainClass):
    _semantic_type_name = "Factory"


# The class of each building block a card's stereotypes name (`stereotypes.KIND_OF_STEREOTYPE`); a card that names none
# is a plain DomainClass.
_BLOCK_OF_KIND: dict[str | None, type[DomainClass]] = {
    "EntityRoot": Entity,
    "Entity": Entity,
    "ValueObject": ValueObject,
    "Repository": Repository,
    "DomainService": DomainService,
    "Specification": Specification,
    "Factory": Factory,
}
