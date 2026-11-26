"""DDD's map — the bounded contexts and aggregates (schema ``is: module``), and the arcs between aggregates.

BoundedContext and Aggregate subclass Module; the building blocks an aggregate holds are in ``building_blocks``. Every
format reads into these nodes and writes from them: an aggregate holds its building blocks as the cards they are, and
answers which is its root and its repository, whichever format it was read from. Graph rule slugs inherit from CE via
``harness.graph.schema_rules`` (same ``is:`` mapping as schema.yaml).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

from harness.graph.model_node import ModelChildren
from harness.graph.graph import Graph
from harness.markdown.markdown import heading_anchor

from cdd_guidance.practices.clean_engineering.model import CleanEngineeringModel, Module, OoadClass
from cdd_guidance.practices.clean_engineering.model import joined_module_path, module_path_in
from cdd_guidance.practices.clean_engineering.model import Operation
from cdd_guidance.practices.clean_engineering.model import Relationship
from cdd_guidance.practices.clean_engineering.model import Property
from cdd_guidance.practices.clean_engineering.model import pascal_type_names
from cdd_guidance.practices.ddd.model.building_blocks import (
    DomainClass,
    DomainEvent,
    DomainNode,
    DomainService,
    Entity,
    called_class,
    plain_name,
)
from cdd_guidance.practices.ddd.model.stereotypes import TacticalClass
from harness.guidance.practice_formats import FormatAdapter

# The `# Title` line of a bounded context's `.context/bounded-context.md`: the context's name.
_CONTEXT_TITLE = re.compile(r"^\s*#\s+(.+?)\s*$", re.M)
# A `Local → Remote` line of a bounded context's file: a context mapping, each side naming an aggregate.
_CONTEXT_ARROW = re.compile(r"^[\s\-*>]*(.+?)\s*→\s*(.+?)\s*$")
# An aggregate a bounded context's file names as a link to its heading in the domain model: a list entry that is one
# link, `- [Cart](../../.context/domain-model.md#cart)`.
_AGGREGATE_LINK = re.compile(r"^\s*[-*]\s*\[([^\]]+)\]\(([^)\s#]+)#([^)\s]+)\)\s*$")
# The line a bounded context's file writes above the aggregates it names.
_AGGREGATES_LABEL = "Aggregates:"
# `Context · Aggregate · Entity`: the parts of a target as DDD's notations write it, the outermost first.
TARGET_SEGMENT = re.compile(r"[·•]")

# A module's path: the labels of the contexts that hold it, then its own name, as Clean Engineering nests modules.
_PATH = "/"
# The context classes with no place gather in.
_DEFAULT_CONTEXT = "Domain"
# How an arc's target line starts across contexts, and how it names the identity it holds its target by.
_ARROWS = ("→", "->")
_HELD_BY = "(by"
# The words an arc's `key: value` lines use for its fields; `integrate:` is the sketch's word for the integration field.
_FIELD_NAMES = {"integrate": "integration", "context": "context", "aggregate": "aggregate", "entity": "entity"}


def looks_like_operation(line: str) -> bool:
    """A single lower-case word under the root names one of its operations; anything else names a member."""
    if not line or " " in line or line.endswith(":"):
        return False
    return line[0].islower()


def _drawn_name(line: str) -> str:
    """A member's name as a drawing lists it: without what its line says after ` - `."""
    return line.split(" - ", 1)[0].strip().lower()


class Integration:
    """An arrow from an aggregate to another class: the context, aggregate, and entity it reaches, the identity it holds
    that class by, and its fields. A target that names one class names only its entity. Every text format writes an
    arc the same way, a `- target` line, then a `key: value` line for each field, so the arc reads and writes those
    lines itself."""

    FIELDS = ("pattern", "direction", "crosses", "integration", "sync")
    """The fields of an arc, in the order its lines write them under its target."""
    PARTS = ("context", "aggregate", "entity", "held_by")
    """The parts of the arc's target, each kept as its own detail when a class model keeps the arc as a dependency."""

    def __init__(self) -> None:
        self.context = ""
        self.aggregate = ""
        self.entity = ""
        self.held_by = ""
        self.direction = ""
        self.crosses = ""
        self.integration = ""
        self.pattern = ""
        # Who owns what crosses, what makes it cross, and how stale it may be, as a domain model writes it.
        self.sync = ""

    @classmethod
    def from_aggregate(cls, target: "Aggregate") -> "Integration":
        """An arc to target, named by its context and its own name."""
        integration = cls()
        integration.context, integration.aggregate = target.parent.name, target.name
        return integration

    @classmethod
    def read_arcs(cls, lines: list[str]) -> list["Integration"]:
        """The arcs the lines write: each `- target` line opens one, and the `key: value` lines under it fill it."""
        arcs: list[Integration] = []
        for line in (raw.strip() for raw in lines):
            if line.startswith("- "):
                arcs.append(cls.targeting(line[2:]))
            elif arcs and ":" in line:
                arcs[-1].read_field(line)
        return arcs

    @classmethod
    def targeting(cls, text: str) -> "Integration":
        """An arc to the target text names: `→ Context · Aggregate · Entity (by Identity)`, or one class alone."""
        integration = cls()
        named, _, held_by = text.partition(_HELD_BY)
        named = plain_name(named)
        for arrow in _ARROWS:
            named = named.removeprefix(arrow).strip()
        parts = [part.strip() for part in TARGET_SEGMENT.split(named) if part.strip()]
        if len(parts) == 1:
            parts = ["", "", parts[0]]
        integration.context, integration.aggregate, integration.entity = (parts + ["", "", ""])[:3]
        integration.held_by = held_by.rstrip(")").strip()
        return integration

    @classmethod
    def kept_by(cls, dependency: Relationship) -> "Integration | None":
        """The arc a class model's dependency keeps, when its details name a part of the arc's target: its pattern is
        the label, the rest details."""
        if not any(dependency.details.get(key) for key in cls.PARTS):
            return None
        integration = cls()
        integration.pattern = dependency.label
        for key in (*cls.PARTS, *cls.FIELDS[1:]):
            setattr(integration, key, dependency.details.get(key, ""))
        return integration

    @property
    def target(self) -> str:
        """The target as the arc's line writes it: `→ Context · Aggregate · Entity` across contexts, the class alone
        when it names one, then the identity it is held by."""
        named = " · ".join(part for part in (self.context, self.aggregate, self.entity) if part)
        written = f"{_ARROWS[0]} {named}" if self.context or self.aggregate else named
        return f"{written} {_HELD_BY} {self.held_by})" if self.held_by else written

    def lines(self) -> list[str]:
        """The arc as an aggregate writes it under `Integrations:`: `- target`, then each field it has, indented."""
        return [f"- {self.target}"] + [f"  {key}: {getattr(self, key)}" for key in self.FIELDS if getattr(self, key)]

    def read_field(self, line: str) -> None:
        """One `key: value` line under the arc's target, for a field the arc has."""
        key, value = (part.strip() for part in line.split(":", 1))
        field = _FIELD_NAMES.get(key.lower()) or (key.lower() if key.lower() in self.FIELDS else "")
        if field:
            setattr(self, field, value)

    @property
    def target_name(self) -> str:
        """The class the arrow points at: the entity when the target names one, else the aggregate."""
        return self.entity or self.aggregate

    def as_dependency(self) -> Relationship:
        """The arc as a class model keeps it on the aggregate's root: a dependency on the class it reaches, labelled by
        its pattern, with each part of its target and each of its other fields as a detail."""
        details = {key: getattr(self, key) for key in (*self.PARTS, *self.FIELDS[1:]) if getattr(self, key)}
        return Relationship(target=self.target_name, kind="dependency", label=self.pattern, details=details)


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
        # The heading a sketch or a document groups this aggregate under, so every format keeps the grouping.
        self.group: str | None = None
        # The events the aggregate reacts to, which another aggregate's root emits.
        self.consumed_events: list[str] = []
        # The arrows a class drawing shows from one of its cards with no detail kept on them: the card and the arrow.
        self._drawn_arrows: list[tuple[DomainClass, Relationship]] = []

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

    def open_root(self, name: str, members: list[str], emitted: list[str]) -> None:
        """The root a document's or a drawing's lines name: an entity called name, holding the members listed under
        it, the single lower-case words among them its operations, and emitting the events named."""
        operations = [member for member in members if looks_like_operation(member)]
        self.root = Entity(name, 1, member_lines=[member for member in members if member and member not in operations])
        for operation in operations:
            self.root.operations.append(Operation(operation, len(self.root.operations) + 1))
        for event_name in emitted:
            event = DomainEvent(event_name, len(self.root.properties))
            event.producer = self
            self.root.properties.append(event)

    def take_drawn_root(self, members: list[str]) -> None:
        """The root a map drawing shows: the aggregate's own entity, holding the members listed under it."""
        self.open_root(self.name, members, [])
        self.load_root()

    def take_root_card(self) -> None:
        """At model fidelity the root is the <<Aggregate Root>> card, keeping the events the aggregate's lines named;
        each repository card collects that root."""
        root = self.root_card
        if root is None:
            return
        events = self.events
        self.take_root(root)
        self.root.properties.extend(event for event in events if event not in self.root.properties)
        for card in self.classes:
            if card.is_repository:
                card.accesses = self.root

    @property
    def root_card(self) -> DomainClass | None:
        """The card marked <<Aggregate Root>>, or made the aggregate's root; none at bounded-context fidelity."""
        return next((card for card in self.classes if card.is_root), None)

    @property
    def repository(self) -> DomainClass | None:
        """The card of the repository that keeps the root."""
        return next((card for card in self.classes if card.is_repository), None)

    @property
    def member_cards(self) -> list[DomainClass]:
        """The entities and values the root composes."""
        return [card for card in self.classes if not card.is_root and not card.is_repository]

    @property
    def ordered_cards(self) -> list[DomainClass]:
        """Root, then its repository, then members — the same order in every format."""
        roots = [card for card in self.classes if card.is_root]
        repositories = [card for card in self.classes if card.is_repository]
        return roots + repositories + self.member_cards

    @property
    def events(self) -> list[DomainEvent]:
        """The domain events the root emits."""
        if self.root is None:
            return []
        return [item for item in self.root.properties if isinstance(item, DomainEvent)]

    @property
    def members(self) -> list:
        """What the root holds: the member cards at model fidelity, else the invariant objects its lines name."""
        if self.classes:
            return self.member_cards
        return list(self.root.invariant_objects) if self.root is not None else []

    @property
    def drawn_members(self) -> list[str]:
        """The members the map lists under the aggregate: what the root holds, without the root itself, prose, or
        operations."""
        if self.root is None:
            return []
        names = [item.name.split("//", 1)[0].split(" - ", 1)[0].strip() for item in self.members]
        seen = {self.root.name.split(" - ", 1)[0].strip().lower(), self.name.lower()}
        drawn: list[str] = []
        for name in names:
            if name and name.lower() not in seen and not self._looks_like_prose(name) and not looks_like_operation(name):
                seen.add(name.lower())
                drawn.append(name)
        return drawn

    def _looks_like_prose(self, line: str) -> bool:
        """A note or a sentence, not a member's name."""
        text = line.strip()
        if not text or text.lower().startswith("note:"):
            return True
        return ". " in text or text.endswith(".") or text[0].islower()

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

    def take_words_from(self, earlier: "Aggregate", drawn_in: dict[str, str]) -> None:
        """Keep the sentence, group, and consumed events it has, and take earlier's where it has none, as an aggregate
        read from a drawing takes what the document it is written onto held; what a root listed under it, as the
        bounded-context map writes it, says it is; and each card's words, card by card, given the card each class of
        the document is drawn inside (drawn_in)."""
        self.description = self.description or earlier.description
        self.group = self.group or earlier.group
        self.consumed_events = self.consumed_events or list(earlier.consumed_events)
        self._take_root_words_from(earlier)
        was_named = {card.name: card for card in earlier.classes}
        for card in self.classes:
            if card.name in was_named:
                card.take_words_from(was_named[card.name], drawn_in)

    def _take_root_words_from(self, earlier: "Aggregate") -> None:
        """A root listed under this aggregate, as the bounded-context map writes it, takes what earlier says the root
        is, its operations, the events it emits, and each member's line as earlier writes it."""
        was_root, root = earlier.root, self.root
        if was_root is None or root is None or self.classes:
            return
        root.intent = root.intent or was_root.intent
        root.operations = root.operations or list(was_root.operations)
        if not self.events:
            root.properties.extend(earlier.events)
        written = {_drawn_name(member.name): member.name for member in was_root.invariant_objects}
        for member in root.invariant_objects:
            member.name = written.get(_drawn_name(member.name), member.name)

    def take_class(self, oclass: OoadClass) -> None:
        """Hold a class read from a class model as the card of the building block it is, and the arcs it keeps as
        dependencies as this aggregate's integrations."""
        card = DomainClass.from_code(oclass)
        self.classes.append(card)
        arcs = (Integration.kept_by(dependency) for dependency in oclass.dependencies)
        self.integrations.extend(arc for arc in arcs if arc is not None)
        self._drawn_arrows.extend((card, item) for item in oclass.dependencies if item.label and not item.details)

    def read_arrows_across(self, homes: dict[str, "Aggregate"]) -> None:
        """Once every aggregate holds its classes, read each labelled arrow from one of its cards to a class of another
        aggregate, given the aggregate each class is in, as what it was drawn from: a call, when an operation of the
        card names the arrow, made by that operation to the class; otherwise an integration to the class, whose
        pattern is the arrow's label."""
        for card, arrow in self._drawn_arrows:
            target = homes.get(arrow.target)
            if target is None or target is self:
                continue
            caller = next((item for item in card.operations if item.name == arrow.label), None)
            if caller is None:
                self._integrate_with(target, arrow)
            elif arrow.target not in (callee.partition(".")[0].strip() for callee in caller.callees):
                caller.callees.append(arrow.target)

    def _integrate_with(self, target: "Aggregate", arrow: Relationship) -> None:
        reaches = (target.parent.name, target.name, arrow.target)
        if any((item.context, item.aggregate, item.entity) == reaches for item in self.integrations):
            return
        integration = Integration.from_aggregate(target)
        integration.entity, integration.pattern = arrow.target, arrow.label
        self.integrations.append(integration)

    def take_root_from_classes(self) -> None:
        """Once its cards are read from a class model: the relationships their types name, and the root card, else a
        root named after the aggregate."""
        self._infer_relationships()
        self.take_root_card()
        if self.root is None:
            self.root = Entity(self.name, 1)

    def write_classes_into(self, module: Module, draws_repository_in_root: bool = False) -> None:
        """Write the aggregate into module as code holds it: each card a class kept in the aggregate's place, and the
        root alone when it has no cards. A drawing draws the repository inside its root's card, as the model fidelity
        lays an aggregate out; code keeps it a class of its own."""
        written = {id(card): card.write_into(module, self.place_labels) for card in self.ordered_cards}
        if draws_repository_in_root:
            self._fold_into_root(module, written)
        if not module.classes and self.root is not None:
            self.root.write_into(module, self.place_labels)
        self._depend_across(module)

    def _fold_into_root(self, module: Module, written: dict[int, OoadClass]) -> None:
        """Draw each repository inside the root's class, below the root's operations, in place of a class of its own,
        however the document writes it."""
        root = self.root_card
        if root is None or root.is_repository:
            return
        for card in self.classes:
            if card.is_repository and id(card) in written:
                module.classes.remove(written[id(card)])
                written[id(root)].fold(written[id(card)])

    def _depend_across(self, module: Module) -> None:
        """Each class depends on the class of another aggregate its operations call, named by the calling operation,
        and the root on each class an integration reaches, the arc kept whole as that dependency."""
        local = {card.name for card in self.classes} | {self.name}
        for oclass in module.classes:
            for operation in oclass.operations:
                self._depend_on_callees(oclass, operation, local)
        if module.classes:
            module.classes[0].dependencies.extend(item.as_dependency() for item in self.integrations if item.target_name)

    def _depend_on_callees(self, oclass: OoadClass, operation: Operation, local: set[str]) -> None:
        """oclass depends on the class of another aggregate each of the operation's calls names, by the operation."""
        for callee in operation.callees:
            target = called_class(callee)
            if target and target not in local:
                oclass.arrows.depend_on(target, operation.name)

    def _infer_relationships(self) -> None:
        """Code holds `identity: Identity`, not `<< composition >>`: a member the aggregate holds is composed, and a
        repository's collection of the root is an aggregation."""
        for card in self.classes:
            for prop in card.plain_properties:
                prop.stereotype = prop.stereotype or self._relationship_named_by(card, prop)

    def _relationship_named_by(self, card: DomainClass, prop: Property) -> str:
        """The relationship a property's type names: an aggregation for a repository's collection of the root, a
        composition for a member the aggregate holds; none otherwise."""
        named = pascal_type_names(prop.type_hint or "")
        roots = {item.name for item in self.classes if item.is_root}
        if card.is_repository and any(part in roots for part in named) and prop.type_hint.strip() not in roots:
            return "aggregation"
        if named and named[0] in {item.name for item in self.member_cards}:
            return "composition"
        return prop.stereotype


class ContextMapping(DomainNode):
    """How one bounded context maps to another: a `Local → Remote` line its `.context/bounded-context.md` lists, on
    the line it sits on (its sequential order). Each side names an aggregate, alone or after the context that holds it
    (`Sales · cart`); the two sides are saved with the graph, so a reader of a graph opened from its save has them."""

    _semantic_type_name = "ContextMapping"
    graph_facts = ("local", "remote", "pattern")

    def __init__(self, local: str = "", remote: str = "", line: int = 0, pattern: str = "") -> None:
        super().__init__(f"{local} → {remote}", line)
        self.local = local
        self.remote = remote
        # The integration pattern the mapping follows, when the document that lists it names one.
        self.pattern = pattern

    @property
    def aggregate_names(self) -> dict[str, str]:
        """The aggregate each side names, by its side (`local`, `remote`): the last part of what the side writes."""
        return {side: TARGET_SEGMENT.split(written)[-1].strip() for side, written in (("local", self.local), ("remote", self.remote))}


class AggregateLink(NamedTuple):
    """An aggregate as a bounded context's file names it: the words of the link, the domain model it opens, written
    from the context's file, the anchor of the aggregate's heading there, and the line of the file the link is on."""

    name: str
    file: str
    anchor: str
    line: int


class ContextFile:
    """A bounded context's own file, `.context/bounded-context.md`, whose folder is the context in code. Its `# Title`
    names the context; under `Aggregates:` it names each aggregate as a link to that aggregate's heading in the domain
    model, which the Files app opens in place, as a story opens its scenarios; and each `Local → Remote` line is a
    context mapping. It never changes once made: the file naming a context's aggregates is a new one (``naming``)."""

    def __init__(self, text: str = "") -> None:
        self.text = text
        self._lines = text.splitlines()

    @property
    def title(self) -> str:
        """The context's name as the file's `# Title` gives it; empty for a file with no title."""
        found = _CONTEXT_TITLE.search(self.text)
        return found.group(1).strip() if found else ""

    @property
    def line_count(self) -> int:
        return max(1, len(self._lines))

    @property
    def mappings(self) -> list[ContextMapping]:
        """Each `Local → Remote` line of the file, as the mapping it lists."""
        found = ((index, _CONTEXT_ARROW.match(line.strip())) for index, line in enumerate(self._lines, start=1))
        return [ContextMapping(match.group(1).strip(), match.group(2).strip(), index) for index, match in found if match is not None]

    @property
    def aggregate_links(self) -> list[AggregateLink]:
        """Each aggregate the file names as a link to a heading. A link in a sentence, or to a whole file, names none."""
        found = ((index, _AGGREGATE_LINK.match(line)) for index, line in enumerate(self._lines, start=1))
        return [AggregateLink(*match.groups(), index) for index, match in found if match is not None]

    def naming(self, context: "BoundedContext", domain_model: str) -> "ContextFile":
        """The file naming each of context's aggregates as a link to its heading in domain_model, the domain model's
        path as written from this file: every other line the file holds is kept, and an aggregate it named in plain
        words or by an earlier link is named once, by the new link. A file with no text is written new, with the
        context's title and what the domain model says the context is."""
        links = [_AGGREGATES_LABEL, *(f"- [{aggregate.name}]({domain_model}#{heading_anchor(aggregate.name)})" for aggregate in context.aggregates)]
        if not self.text.strip():
            opening = [f"# {context.name}", "", *([context.description, ""] if context.description else [])]
            return ContextFile("\n".join([*opening, *links]) + "\n")
        named = {aggregate.name for aggregate in context.aggregates}
        kept = [line for line in self._lines if not self._names_an_aggregate(line, named)]
        at = self._aggregates_at(named)
        above = "\n".join(kept[:at]).rstrip("\n").splitlines()
        below = "\n".join(kept[at:]).strip("\n").splitlines()
        return ContextFile("\n".join([*above, "", *links, *(["", *below] if below else [])]) + "\n")

    def _names_an_aggregate(self, line: str, named: set[str]) -> bool:
        """Whether line is one the aggregates' links replace: their label, a link to an aggregate's heading, or a list
        entry that is the name of one of the context's aggregates."""
        written = line.strip()
        return written == _AGGREGATES_LABEL or _AGGREGATE_LINK.match(line) is not None or (written[:1] in ("-", "*") and written[1:].strip() in named)

    def _aggregates_at(self, named: set[str]) -> int:
        """How many of the lines kept come before the aggregates: those above where the file named them before, else
        those above its first context mapping, else all of them."""
        replaced = [self._names_an_aggregate(line, named) for line in self._lines]
        if any(replaced):
            return replaced.index(True)
        return next((index for index, line in enumerate(self._lines) if _CONTEXT_ARROW.match(line.strip())), len(self._lines))


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
        self.mappings: list[ContextMapping] = []
        # The aggregates the context's own file names as links to their headings in the domain model.
        self.aggregate_links: list[AggregateLink] = []
        # Why the context exists and what it must not do, as a sketch or a document notes it above its aggregates.
        self.notes: list[str] = []
        # The Clean Engineering module the context is built as, with the seam and constraint noted on it.
        self.module_name = ""
        self.module_notes: list[str] = []
        # The notes under each heading that groups aggregates, by that heading.
        self.group_notes: dict[str, list[str]] = {}

    @property
    def label(self) -> str:
        """The context's name, with its owner after `|` when it has one: `Customer | custom`."""
        return f"{self.name} | {self.owner}" if self.owner else self.name

    def load_context_folder(self, folder: Path) -> None:
        """Read the folder that holds this context in code: its name is the title of `.context/bounded-context.md`,
        else the folder's own name, its context mappings are the `Local → Remote` lines that file lists, and it owns
        the facts every code folder carries."""
        file = ContextFile((folder / ".context" / "bounded-context.md").read_text(encoding="utf-8"))
        self.name = file.title or folder.name
        self.context_file_lines = file.line_count
        self.mappings = file.mappings
        self.aggregate_links = file.aggregate_links
        self.source_facts.load_folder(folder)

    def context_file(self, domain_model: str, previous: str = "") -> str:
        """The text of this context's own file, naming each of its aggregates as a link to its heading in
        domain_model, the domain model's path as written from that file; previous is the file as it is now, whose
        other lines are kept."""
        return ContextFile(previous).naming(self, domain_model).text

    def take_words_from(self, earlier: "BoundedContext") -> None:
        """Keep the sentence, notes, module, and group notes it has, and take earlier's where it has none, as a context
        read from a drawing takes what the document it is written onto held."""
        self.description = self.description or earlier.description
        self.notes = self.notes or list(earlier.notes)
        self.module_name = self.module_name or earlier.module_name
        self.module_notes = self.module_notes or list(earlier.module_notes)
        self.group_notes = self.group_notes or dict(earlier.group_notes)

    def keep_note(self, text: str, group: str | None) -> None:
        """A note goes to the group it sits under, else the module, else the context."""
        if group:
            self.group_notes.setdefault(group, []).append(text)
        elif self.module_name:
            self.module_notes.append(text)
        else:
            self.notes.append(text)

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


class BoundedContextMap(FormatAdapter):
    """The bounded contexts of a domain, each holding its aggregates and the contexts nested in it. Each format
    subclasses the map and names the context type it reads and writes, which names its own aggregate type; each
    context loads its own children."""

    bounded_context_type: type[BoundedContext] = BoundedContext

    def __init__(self) -> None:
        super().__init__()
        self.contexts: list[BoundedContext] = []
        # The map's own name, as its `# ` heading gives it; none for a map that names itself no title.
        self.title = ""
        # What a document writes round its title: the lines above it, such as front matter, and the lines between it
        # and the first bounded context, which say what the map is of.
        self.opening: list[str] = []
        self.description: list[str] = []

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

    @property
    def holds_document_words(self) -> bool:
        """Whether the format this map was read from holds a document's words: the sentence under a heading, a note,
        an invariant, an integration's fields, the events. A drawing holds none of them."""
        return True

    def aggregate_reached_by(self, integration: Integration) -> Aggregate | None:
        """The aggregate an integration's target names: in the context it names, its entity or its aggregate; with no
        context the map holds, the aggregate called by the name it gives."""
        context_name, aggregate_name, entity_name = integration.context, integration.aggregate, integration.entity
        in_context = [item for item in self.every_aggregate if self._same_name(item.parent.name, context_name)]
        if not in_context:
            return next((item for item in self.every_aggregate if self._same_name(item.name, aggregate_name or entity_name)), None)
        named = (item for name in (entity_name, aggregate_name) if name for item in in_context if self._same_name(item.name, name))
        return next(named, None)

    def _same_name(self, left: str, right: str) -> bool:
        return bool(right) and left.strip().lower() == right.strip().lower()

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
        wiring = _EventWiring(self.every_aggregate)
        for entry in entries:
            wiring.wire(entry)

    def write_classes(self, model: CleanEngineeringModel, draws_repository_in_root: bool = False) -> None:
        """Write this map into model, a Clean Engineering model of some format, as that format's own modules and
        classes: one module per aggregate, named by the aggregate's place, holding a class for each of its building
        blocks; a drawing draws each repository inside its root's class instead."""
        modules: list[Module] = []
        for aggregate in self.every_aggregate:
            module = model.load_module(aggregate)
            module.name = aggregate.code_place
            module.sequential_order = len(modules) + 1
            aggregate.write_classes_into(module, draws_repository_in_root)
            modules.append(module)
        model.modules = modules

    def read_class_model(self, model: CleanEngineeringModel) -> "BoundedContextMap":
        """Read a class model written as code or drawn as classes into this map, and return it: each class's place
        names its context and aggregate, which takes the class; classes with no place gather around the roots that
        hold them."""
        self.contexts = []
        unplaced = _UnplacedClasses(self._place_classes(model))
        for context_name, aggregate_name, oclass in unplaced.grouped():
            self.context_at([context_name]).aggregate_named(aggregate_name).take_class(oclass)
        for aggregate in self.every_aggregate:
            aggregate.take_root_from_classes()
        homes = {oclass.name: aggregate for aggregate in self.every_aggregate for oclass in aggregate.classes}
        for aggregate in self.every_aggregate:
            aggregate.read_arrows_across(homes)
        return self

    def _place_classes(self, model: CleanEngineeringModel) -> list[tuple[str, OoadClass]]:
        """Give each public class of model whose place names an aggregate to that aggregate; answer the rest, each with
        the name of the context its module gives it."""
        unplaced: list[tuple[str, OoadClass]] = []
        drawn = ((module, item) for module in model.modules for oclass in module.classes for item in (oclass, *oclass.folded))
        public = ((module, oclass) for module, oclass in drawn if not oclass.name.startswith("_"))
        for module, oclass in public:
            place = self._place_of(module, oclass)
            if place:
                self.context_at(place[:-1]).aggregate_named(place[-1]).take_class(oclass)
            else:
                unplaced.append((module.name or _DEFAULT_CONTEXT, oclass))
        return unplaced

    def _place_of(self, module: Module, oclass: OoadClass) -> list[str]:
        """Where a class read from a class model lives, its contexts' labels then its aggregate: the module path code
        names for it, else the module a class drawing keeps it in; none for a class with neither."""
        return next((list(place) for place in (oclass.module_path, module_path_in(module.name)) if len(place) >= 2), [])


class _UnplacedClasses:
    """Classes read from a class model with no place: each root, or each class nobody composes, opens an aggregate; the
    rest join the aggregate of the class that holds them. A class the business keeps in its own repository is an
    aggregate root."""

    def __init__(self, classes: list[tuple[str, OoadClass]]) -> None:
        self._classes = classes
        # Each class read once as DDD reads it, by the name a property's type or a repository's name gives it.
        self._tactical = {oclass.name: TacticalClass(oclass) for _context, oclass in classes}
        # The class that holds each held class, by the held class's name.
        self._holder: dict[str, str] = {}

    def grouped(self) -> Iterator[tuple[str, str, OoadClass]]:
        """Each class with its context and the name of the aggregate it joins: the class at the top of its holders."""
        for _context, oclass in self._classes:
            self._hold_composed_members(oclass)
            self._join_kept_root(oclass)
        for context, oclass in self._classes:
            yield context, self._top_holder(oclass.name), oclass

    def _hold_composed_members(self, oclass: OoadClass) -> None:
        """oclass holds each other class its properties' types name, unless that class is a root of its own."""
        for prop in oclass.properties:
            for target in pascal_type_names(prop.type_hint or ""):
                if self._is_member(target, oclass):
                    self._holder.setdefault(target, oclass.name)

    def _is_member(self, target: str, oclass: OoadClass) -> bool:
        found = self._tactical.get(target)
        return found is not None and target != oclass.name and found.kind() != "EntityRoot"

    def _join_kept_root(self, oclass: OoadClass) -> None:
        """A repository joins the root it keeps, which becomes an aggregate root when nothing marks it yet."""
        root = self._tactical.get(self._tactical[oclass.name].kept_root_name)
        if root is None:
            return
        self._holder.setdefault(oclass.name, root.oclass.name)
        if not root.stereotypes:
            root.oclass.stereotypes = ["Aggregate Root", "Entity", *root.oclass.stereotypes]

    def _top_holder(self, name: str) -> str:
        top, seen = name, set()
        while top in self._holder and top not in seen:
            seen.add(top)
            top = self._holder[top]
        return top


class _EventWiring:
    """Reads the entries of an event map onto the roots of the aggregates that emit them: it holds the map's aggregates
    by name, and the domain services consumers name, each made once per map."""

    def __init__(self, aggregates: list[Aggregate]) -> None:
        self._aggregates = {item.name: item for item in aggregates}
        self._services: dict[str, DomainService] = {}

    def wire(self, entry: str) -> None:
        """One `CartCheckedOut: emitted by ShoppingCart; consumed by Inventory, Receipt` entry."""
        name, _, rest = entry.partition(":")
        emitted, _, consumed = rest.partition("consumed by")
        producer = self._aggregates.get(emitted.replace("emitted by", "").strip(" ;"))
        if producer is None or producer.root is None:
            return
        event = self._event_of(producer, name.strip())
        for consumer_name in (part.strip() for part in consumed.split(",")):
            if consumer_name:
                event.consumers.append(self._consumer(consumer_name, len(event.consumers) + 1))

    def _event_of(self, producer: Aggregate, name: str) -> DomainEvent:
        """The event called name on the producer's root, added the first time, emitted by the producer."""
        event = next((item for item in producer.events if item.name == name), None)
        if event is None:
            event = DomainEvent(name, len(producer.root.properties))
            producer.root.properties.append(event)
        event.emitted_by(producer)
        return event

    def _consumer(self, name: str, order: int) -> Aggregate | DomainService:
        """The aggregate a consumer names, else the domain service it names, made once per map."""
        if name in self._aggregates:
            return self._aggregates[name]
        if name not in self._services:
            self._services[name] = DomainService(name, order)
        return self._services[name]
