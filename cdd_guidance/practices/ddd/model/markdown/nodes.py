"""Markdown channel. Each node reads only the next child in the file."""

from __future__ import annotations

import re

from cdd_guidance.practices.sketch_document.discovery_document import DiscoveryDocument
from cdd_guidance.practices.clean_engineering.model import Module, OoadClass
from cdd_guidance.practices.clean_engineering.model import Relationship
from cdd_guidance.practices.clean_engineering.model import Operation
from cdd_guidance.practices.clean_engineering.model import Property
from cdd_guidance.practices.clean_engineering.model import pascal_type_names
from cdd_guidance.practices.ddd.model.markdown.class_cards import (
    CARD,
    MarkdownBuildingBlock,
    MarkdownDomainNode,
    MarkdownEntity,
)
from cdd_guidance.practices.ddd.model.nodes import (
    Aggregate,
    BoundedContext,
    BoundedContextMap,
    DomainEvent,
    Integration,
    TARGET_SEGMENT,
)
from cdd_guidance.practices.ddd.model.markdown.replaced_document import ReplacedDocument

_EVENT_MAP = "event map"
# The `##` sections a map holds that are no context: the event map, and the template's explanation of the map's format.
_NOT_CONTEXTS = (_EVENT_MAP, "map format")
# The map's own heading, which names it.
_TITLE = "# "
_CONTEXT = "## "
_AGGREGATE = "### "
_NOTE = "> "
_MODULE = "**Module:**"
_INTEGRATIONS = "Integrations:"
# `*Group*`: the heading a sketch grouped the following aggregates under.
_GROUP = re.compile(r"^\*([^*].*?)\*$")
_ARROWS = ("→", "->")
_HELD_BY = "(by"
# `integrate:` is the sketch's word for the integration field.
_FIELD_NAMES = {"integrate": "integration", "context": "context", "aggregate": "aggregate", "entity": "entity"} | {
    field: field for field in Integration.FIELDS
}
# Lines that end a card's section and return to the aggregate's own lines: its arcs, its events, the next aggregate.
_LEAVES_CARD = ("integrations:", "emits events:", "consumes events:", "### ")


def looks_like_operation(line: str) -> bool:
    """A single lower-case word under the root names one of its operations; anything else names a member."""
    if not line or " " in line:
        return False
    if line.endswith(":"):
        return False
    return line[0].islower()


class MarkdownIntegration(Integration, MarkdownDomainNode):
    """An arc as markdown writes it: a `- target` line, then a `key: value` line for each field."""

    @staticmethod
    def read_arcs(lines: list[str]) -> list["MarkdownIntegration"]:
        """The arcs the lines write: each `- target` line opens one, and the `key: value` lines under it fill it."""
        arcs: list[MarkdownIntegration] = []
        for line in (raw.strip() for raw in lines):
            if line.startswith("- "):
                arcs.append(MarkdownIntegration.targeting(line[2:]))
            elif arcs and ":" in line:
                arcs[-1].read_field(line)
        return arcs

    @staticmethod
    def targeting(text: str) -> "MarkdownIntegration":
        """An arc to the target text names: `→ Context · Aggregate · Entity (by Identity)`, or one class alone."""
        integration = MarkdownIntegration()
        named, _, held_by = text.partition(_HELD_BY)
        named = integration.plain_name(named)
        for arrow in _ARROWS:
            named = named.removeprefix(arrow).strip()
        parts = [part.strip() for part in TARGET_SEGMENT.split(named) if part.strip()]
        if len(parts) == 1:
            parts = ["", "", parts[0]]
        integration.context, integration.aggregate, integration.entity = (parts + ["", "", ""])[:3]
        integration.held_by = held_by.rstrip(")").strip()
        return integration

    @staticmethod
    def kept_by(dependency: Relationship) -> "MarkdownIntegration | None":
        """The arc a class model's dependency keeps, when it keeps one."""
        integration = MarkdownIntegration()
        if not integration.keeps_one(dependency):
            return None
        integration.read_dependency(dependency)
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
        if key.lower() in _FIELD_NAMES:
            setattr(self, _FIELD_NAMES[key.lower()], value)


class MarkdownAggregate(Aggregate, MarkdownDomainNode):
    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        # The lines under the aggregate's heading; `load_root` reads the root, its cards, and its arcs from them.
        self.source_lines: list[str] = []
        # The arrows a class drawing shows from one of its cards with no detail kept on them: the card and the arrow.
        self._drawn_arrows: list[tuple[MarkdownBuildingBlock, Relationship]] = []

    def load_root(self) -> None:
        sections, map_lines = self._split_cards()
        self.classes.extend(card for section in sections for card in MarkdownBuildingBlock.read(section))
        self._read_map_lines(map_lines)
        self._take_root_card()
        super().load_root()

    @property
    def root_card(self) -> MarkdownBuildingBlock | None:
        return next((card for card in self.classes if card.is_root), None)

    @property
    def repository(self) -> MarkdownBuildingBlock | None:
        return next((card for card in self.classes if card.is_repository), None)

    @property
    def member_cards(self) -> list[MarkdownBuildingBlock]:
        """The entities and values the root composes."""
        return [card for card in self.classes if not card.is_root and not card.is_repository]

    @property
    def ordered_cards(self) -> list[MarkdownBuildingBlock]:
        """Root, then its repository, then members — the same order in every aggregate."""
        roots = [card for card in self.classes if card.is_root]
        repositories = [card for card in self.classes if card.is_repository]
        return roots + repositories + self.member_cards

    @property
    def members(self) -> list:
        """What the root holds: the member cards at model fidelity, else the invariant objects its lines name."""
        return self.member_cards if self.classes else super().members

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

    def take_drawn_root(self, members: list[str]) -> None:
        """The root a map drawing shows: the aggregate's own entity, holding the members listed under it."""
        self._open_root(self.name, members, [])
        super().load_root()

    def _take_root_card(self) -> None:
        """At model fidelity the root is the <<Aggregate Root>> card; each repository card collects that root."""
        root = self.root_card
        if root is None:
            return
        events = self.events
        self.take_root(root)
        self.root.properties.extend(event for event in events if event not in self.root.properties)
        for card in self.classes:
            if card.is_repository:
                card.accesses = self.root

    def take_class(self, oclass: OoadClass) -> None:
        """Hold a class read from a class model as the card of the building block it is, and the arcs it keeps as
        dependencies as this aggregate's integrations."""
        card = MarkdownBuildingBlock.from_code(oclass)
        self.classes.append(card)
        arcs = (MarkdownIntegration.kept_by(dependency) for dependency in oclass.dependencies)
        self.integrations.extend(arc for arc in arcs if arc is not None)
        self._drawn_arrows.extend((card, item) for item in oclass.dependencies if item.label and not item.details)

    def read_arrows_across(self, homes: dict[str, Aggregate]) -> None:
        """Each labelled arrow from one of its cards to a class of another aggregate, read as what it was drawn from: a
        call, when an operation of the card names the arrow, made by that operation to the class; otherwise an
        integration to the class, whose pattern is the arrow's label."""
        for card, arrow in self._drawn_arrows:
            target = homes.get(arrow.target)
            if target is None or target is self:
                continue
            caller = next((item for item in card.operations if item.name == arrow.label), None)
            if caller is None:
                self._integrate_with(target, arrow)
            elif arrow.target not in (callee.partition(".")[0].strip() for callee in caller.callees):
                caller.callees.append(arrow.target)

    def _integrate_with(self, target: Aggregate, arrow: Relationship) -> None:
        reaches = (target.parent.name, target.name, arrow.target)
        if any((item.context, item.aggregate, item.entity) == reaches for item in self.integrations):
            return
        integration = MarkdownIntegration.from_aggregate(target)
        integration.entity, integration.pattern = arrow.target, arrow.label
        self.integrations.append(integration)

    def take_root_from_classes(self) -> None:
        """Once its cards are read from a class model: the relationships their types name, and the root card, else a
        root named after the aggregate."""
        self._infer_relationships()
        self._take_root_card()
        if self.root is None:
            self.root = MarkdownEntity(self.name, 1)

    def write_classes_into(self, module: Module) -> None:
        """Write the aggregate into module as code holds it: each card a class kept in the aggregate's place, and the
        root alone when it has no cards."""
        written = {id(card): card.write_into(module, self.place_labels) for card in self.ordered_cards}
        self._fold_into_root(module, written)
        if not module.classes and self.root is not None:
            self.root.write_into(module, self.place_labels)
        self._depend_across(module)

    def _fold_into_root(self, module: Module, written: dict[int, OoadClass]) -> None:
        """Draw each repository written inside its root's card inside the root's class, in place of a class of its own."""
        root = self.root_card
        if root is None:
            return
        for card in self.classes:
            if card.drawn_in_root and id(card) in written:
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
            target = callee.strip().partition(".")[0].partition("(")[0].strip()
            if target[:1].isupper() and target not in local:
                oclass.arrows.depend_on(target, operation.name)

    def _infer_relationships(self) -> None:
        """Code holds `identity: Identity`, not `<< composition >>`: a member the aggregate holds is composed, and a
        repository's collection of the root is an aggregation."""
        for card in self.classes:
            for prop in card.plain_properties:
                prop.stereotype = prop.stereotype or self._relationship_named_by(card, prop)

    def _relationship_named_by(self, card: MarkdownBuildingBlock, prop: Property) -> str:
        """The relationship a property's type names: an aggregation for a repository's collection of the root, a
        composition for a member the aggregate holds; none otherwise."""
        named = pascal_type_names(prop.type_hint or "")
        roots = {item.name for item in self.classes if item.is_root}
        if card.is_repository and any(part in roots for part in named) and prop.type_hint.strip() not in roots:
            return "aggregation"
        if named and named[0] in {item.name for item in self.member_cards}:
            return "composition"
        return prop.stereotype

    def _split_cards(self) -> tuple[list[list[str]], list[str]]:
        """Separate this aggregate's `####` card sections from its own lines: its root line, integrations, events."""
        cards: list[list[str]] = []
        rest: list[str] = []
        current: list[str] | None = None
        for raw in self.source_lines:
            line = raw.strip()
            if line.startswith(CARD):
                current = [raw]
                cards.append(current)
                continue
            if current is not None and not raw.startswith((" ", "\t")) and line.lower().startswith(_LEAVES_CARD):
                current = None
            if current is None:
                rest.append(raw)
            else:
                current.append(raw)
        return cards, rest

    def _read_map_lines(self, lines: list[str]) -> None:
        """Read the aggregate's own lines: the rule it keeps true, its root line with what the root is, the members
        under it, its integrations, and its events. An aggregate drawn as class cards has no root line, so each of its
        own lines says what it keeps true."""
        root_line = ""
        described: list[str] = []
        members: list[str] = []
        emitted: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index].strip().lower()
            if line.startswith(_INTEGRATIONS.lower()):
                index = self._read_integrations(lines, index)
            elif line.startswith(("emits events:", "consumes events:")):
                index = self._read_events(lines, index, emitted)
            else:
                root_line = self._read_own_line(lines[index], members, described) or root_line
                index += 1
        root_name, _, root_says = root_line.partition(" - ")
        self.description = "\n".join(described)
        self._open_root(self.plain_name(root_name) or self.name, members, emitted)
        self.root.intent = root_says.strip()

    def _read_own_line(self, raw: str, members: list[str], described: list[str]) -> str:
        """Read one line that is neither an integration nor an event: a member under the root, or a line that says
        what the aggregate keeps true. Answers the line when it is the root's own, `Root - what it is`."""
        line = raw.strip()
        if " - " in line and not raw.startswith(" ") and not self.classes:
            return raw
        if raw.startswith("  ") and line and not line.startswith("-"):
            members.append(raw.split("//", 1)[0].strip())
        elif self._says_what_it_keeps_true(raw):
            described.append(line)
        return ""

    def _says_what_it_keeps_true(self, raw: str) -> bool:
        """A line of the aggregate's own, at the margin, with words on it: neither a rule that parts sections nor the
        root named alone."""
        line = raw.strip()
        return bool(line) and not raw.startswith((" ", "\t")) and bool(line.strip("-")) and self.plain_name(line) != self.name

    def _read_events(self, lines: list[str], index: int, emitted: list[str]) -> int:
        """The `- Event` lines under an `emits events:` or `consumes events:` line; those it emits go to emitted.
        Returns the line after them."""
        emits = lines[index].strip().lower().startswith("emits")
        index += 1
        while index < len(lines) and lines[index].strip().startswith("-"):
            (emitted if emits else self.consumed_events).append(self.plain_name(lines[index].strip()[1:]))
            index += 1
        return index

    def _open_root(self, name: str, members: list[str], emitted: list[str]) -> None:
        operations = [member for member in members if looks_like_operation(member)]
        self.root = MarkdownEntity(name, 1, member_lines=[member for member in members if member and member not in operations])
        for operation in operations:
            self.root.operations.append(Operation(operation, len(self.root.operations) + 1))
        for event_name in emitted:
            event = DomainEvent(event_name, len(self.root.properties))
            event.producer = self
            self.root.properties.append(event)

    def _read_integrations(self, lines: list[str], index: int) -> int:
        # The arcs are the lines indented under `Integrations:`; the first line back at its indent ends them.
        heading_indent = self._indent(lines[index])
        end = index + 1
        while end < len(lines) and (not lines[end].strip() or self._indent(lines[end]) > heading_indent):
            end += 1
        self.integrations.extend(MarkdownIntegration.read_arcs(lines[index + 1:end]))
        return end

    def _indent(self, raw: str) -> int:
        return len(raw) - len(raw.lstrip())

    def lines(self) -> list[str]:
        written = [f"{_AGGREGATE}{self.name}", ""]
        if self.description:
            written.extend([*self.description.split("\n"), ""])
        if self.classes:
            for card in self.ordered_cards:
                written.extend(card.lines())
        elif self.root is not None:
            written.append(f"{self.root.name} - {self.root.intent}" if self.root.intent else self.root.name)
            written.extend(f"  {item.name}" for item in self.root.operations)
            written.extend(f"  {item.name}" for item in self.root.invariant_objects)
            written.append("")
        written.extend(self.integration_lines())
        return written

    def integration_lines(self, indent: str = "") -> list[str]:
        """The aggregate's arcs, the events its root emits, and the events it reacts to, under `Integrations:`,
        `emits events:`, and `consumes events:`."""
        written: list[str] = []
        if self.integrations:
            written.append(f"{indent}{_INTEGRATIONS}")
            written.extend(f"{indent}  {line}" for item in self.integrations for line in item.lines())
            written.append("")
        if self.events:
            written.append(f"{indent}emits events:")
            written.extend(f"{indent}  - {event.name}" for event in self.events)
        if self.consumed_events:
            written.append(f"{indent}consumes events:")
            written.extend(f"{indent}  - {name}" for name in self.consumed_events)
        if self.events or self.consumed_events:
            written.append("")
        return written


class MarkdownBoundedContext(BoundedContext, MarkdownDomainNode):
    aggregate_type = MarkdownAggregate

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)

    def read_lines(self, lines: list[str]) -> None:
        """Read this context's own lines: its notes, its module, the headings that group its aggregates, and each
        aggregate, which reads its own section."""
        index = 0
        group: str | None = None
        while index < len(lines):
            line = lines[index].strip()
            if line.startswith(_AGGREGATE):
                index = self._read_aggregate(lines, index, group)
                continue
            group = self._read_context_line(line, group)
            index += 1

    def _read_context_line(self, line: str, group: str | None) -> str | None:
        """Read a line above the context's aggregates: a note, the module, a group heading, or a line that says what
        the context is. Returns the group in force."""
        grouped = _GROUP.match(line)
        if grouped:
            return grouped.group(1)
        if line.startswith(_MODULE):
            self.module_name = line[len(_MODULE):].strip().strip("`")
        elif line.startswith(_NOTE):
            self.read_note(line, group)
        elif line.strip("-"):
            self.description = f"{self.description}\n{line}".strip()
        return group

    def _read_aggregate(self, lines: list[str], start: int, group: str | None) -> int:
        """The aggregate whose heading is at start, reading its own section; returns the line after the section."""
        aggregate = self.aggregate_type(self.plain_name(lines[start].strip()[len(_AGGREGATE):]), len(self.aggregates) + 1)
        aggregate.group = group
        after = self._aggregate_end(lines, start)
        aggregate.source_lines = lines[start + 1:after]
        self.append_aggregate(aggregate)
        aggregate.load_root()
        return after

    def _aggregate_end(self, lines: list[str], start: int) -> int:
        """An aggregate's section ends at the next aggregate heading or group heading."""
        after = start + 1
        while after < len(lines) and not (lines[after].strip().startswith(_AGGREGATE) or _GROUP.match(lines[after].strip())):
            after += 1
        return after

    def lines(self) -> list[str]:
        written = [f"{_CONTEXT}{self.name} | {self.owner or ''}", ""]
        if self.description:
            written.extend([*self.description.split("\n"), ""])
        written.extend(self._quoted(self.notes))
        if self.module_name:
            written.append(f"{_MODULE} `{self.module_name}`")
            written.extend(self._quoted(self.module_notes))
            written.append("")
        for context in self.contexts:
            if isinstance(context, MarkdownBoundedContext):
                written.extend(context.lines())
        last_group: str | None = None
        for aggregate in self.aggregates:
            if not isinstance(aggregate, MarkdownAggregate):
                continue
            if aggregate.group and aggregate.group != last_group:
                last_group = aggregate.group
                written.extend(self._group_lines(aggregate.group))
            written.extend(aggregate.lines())
        return written

    def read_note(self, line: str, group: str | None) -> None:
        """A `> note` line goes to the group it sits under, else the module, else the context."""
        self._keep_note(line[len(_NOTE):].strip(), group)

    def _keep_note(self, text: str, group: str | None) -> None:
        """A note goes to the group it sits under, else the module, else the context."""
        if group:
            self.group_notes.setdefault(group, []).append(text)
        elif self.module_name:
            self.module_notes.append(text)
        else:
            self.notes.append(text)

    def _quoted(self, notes: list[str]) -> list[str]:
        written = [f"{_NOTE}{text.strip()}" for text in notes if text.strip()]
        return written + [""] if written else []

    def _group_lines(self, group: str) -> list[str]:
        notes = self.group_notes.get(group, [])
        if not notes:
            return []
        return [f"*{group}*"] + self._quoted(notes) + [""]


class MarkdownBoundedContextMap(BoundedContextMap, MarkdownDomainNode):
    """The `markdown` format: `## Context | owner` headings, `### Aggregate` sections under them, then the event map."""

    bounded_context_type = MarkdownBoundedContext

    def __init__(self) -> None:
        super().__init__()
        # The lines of the text being parsed, and the line the next context is looked for from.
        self._lines: list[str] = []
        self._index = 0

    def _read_context_at(self, start: int) -> MarkdownBoundedContext:
        """The context whose `## Context | owner` heading is at start, holding the lines up to the next heading."""
        heading = self._lines[start].strip()[len(_CONTEXT):]
        context = MarkdownBoundedContext(self.plain_name(heading), len(self.contexts) + 1)
        context.owner = self.owner_from(heading)
        end = self._next_heading_after(start)
        context.read_lines(self._lines[start + 1:end])
        self._index = end
        return context

    def parse(self, text: str) -> "MarkdownBoundedContextMap":
        """Read the text's contexts into this map, and return it."""
        self.contexts = []
        self._lines = text.splitlines()
        self._index = 0
        self._read_title()
        self._read_contexts()
        return self

    def _read_title(self) -> None:
        """The map's own name from its `# ` heading, the lines above it, and the lines between it and the first `## `
        heading, which say what the map is of; none of them for a text with no title."""
        title_at = next((index for index, line in enumerate(self._lines) if line.strip().startswith(_TITLE)), None)
        self.title, self.opening, self.description = "", [], []
        if title_at is None:
            return
        self.title = self._lines[title_at].strip()[len(_TITLE):].strip()
        below = self._lines[title_at + 1:]
        first_heading = next((index for index, line in enumerate(below) if line.strip().startswith(_CONTEXT)), len(below))
        self.opening = self._without_blank_ends(self._lines[:title_at])
        self.description = self._without_blank_ends(below[:first_heading])

    def _without_blank_ends(self, lines: list[str]) -> list[str]:
        return "\n".join(lines).strip("\n").splitlines() if any(line.strip() for line in lines) else []

    @property
    def holds_classes_only(self) -> bool:
        """A markdown text that names no aggregate is a plain class model, which Clean Engineering's markdown reads."""
        return not self.every_aggregate

    def render(self, canonical: BoundedContextMap | None = None, previous: str | None = None) -> str:
        """canonical (this map when none is given) as markdown; under the header of the sketch it came from when the
        previous text is a sketch. A map read from a drawing first takes, from the markdown file it is written over,
        the words a drawing does not hold."""
        source = canonical or self
        from_sketch = bool(previous) and "## domain driven design:" in previous.lower()
        if previous and not from_sketch and not source.holds_document_words:
            ReplacedDocument(MarkdownBoundedContextMap().parse(previous), source).give_its_words()
        body = self._text(source)
        return self._wrap_bounded_context_document(body, previous) if from_sketch else body

    def save(self) -> str:
        return self._text(self)

    def _text(self, source: BoundedContextMap) -> str:
        """source as markdown: what it writes round its title, each context's own lines, then the event map."""
        heading = source.title or ("Domain Model" if source.has_class_cards else "Bounded Context Map")
        lines = [*source.opening, ""] if source.opening else []
        lines.extend([f"{_TITLE}{heading}", ""])
        if source.description:
            lines.extend([*source.description, ""])
        for context in source.contexts:
            if isinstance(context, MarkdownBoundedContext):
                lines.extend(context.lines())
        events = [event for aggregate in source.every_aggregate for event in aggregate.events]
        if events:
            lines.append(f"{_CONTEXT}{_EVENT_MAP}")
            lines.append("")
            lines.extend(f"- {event.map_entry()}" for event in events)
            lines.append("")
        return "\n".join(lines)

    def _wrap_bounded_context_document(self, body: str, sketch: str) -> str:
        document = DiscoveryDocument("bounded-context-map", "Bounded Context Map", sketch)
        return "\n".join(document.lines(body.removeprefix("# Bounded Context Map\n\n")))

    def _next_context_at(self) -> int | None:
        index = self._index
        while index < len(self._lines):
            line = self._lines[index].strip()
            if line.startswith(_CONTEXT) and not line.startswith(_AGGREGATE):
                title = line[len(_CONTEXT):].split("|", 1)[0].strip().lower()
                if title not in _NOT_CONTEXTS:
                    return index
            index += 1
        return None

    def _next_heading_after(self, start: int) -> int:
        index = start + 1
        while index < len(self._lines):
            line = self._lines[index].strip()
            if line.startswith(_CONTEXT) and not line.startswith(_AGGREGATE):
                return index
            index += 1
        return len(self._lines)

    def _read_contexts(self) -> None:
        """Read each context heading after the last one read, then wire the event map onto the aggregates."""
        start = self._next_context_at()
        while start is not None:
            self.contexts.append(self._read_context_at(start))
            start = self._next_context_at()
        self.wire_events(self._event_map_entries())

    def _event_map_entries(self) -> list[str]:
        entries: list[str] = []
        in_event_map = False
        for raw in self._lines:
            line = raw.strip()
            if line.startswith(_CONTEXT):
                in_event_map = line[len(_CONTEXT):].split("|", 1)[0].strip().lower() == _EVENT_MAP
            elif in_event_map and line.startswith("- ") and ":" in line:
                entries.append(line[2:])
        return entries
