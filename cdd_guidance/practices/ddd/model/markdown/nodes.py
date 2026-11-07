"""Markdown channel. Each node reads only the next child in the file."""

from __future__ import annotations

import re
from pathlib import Path

from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.ddd.model.markdown.class_cards import ClassCard, read_card, split_cards
from cdd_guidance.practices.ddd.model.nodes import (
    Aggregate,
    BoundedContext,
    BoundedContextMap,
    DomainEvent,
    DomainService,
    Entity,
    Integration,
    InvariantObject,
    Repository,
)

_EVENT_MAP = "event map"
_CONTEXT = "## "
_AGGREGATE = "### "
_NOTE = "> "
_MODULE = "**Module:**"
# `*Group*`: the heading a sketch grouped the following aggregates under.
_GROUP = re.compile(r"^\*([^*].*?)\*$")
_INTEGRATION_FIELDS = ("pattern", "direction", "crosses", "integration")
# `integrate:` is the sketch's word for the integration field.
_FIELD_NAMES = {"integrate": "integration", "context": "context", "aggregate": "aggregate"} | {
    field: field for field in _INTEGRATION_FIELDS
}


def looks_like_operation(line: str) -> bool:
    """A single lower-case word under the root names one of its operations; anything else names a member."""
    if not line or " " in line:
        return False
    if line.endswith(":"):
        return False
    return line[0].islower()


def _indent(raw: str) -> int:
    return len(raw) - len(raw.lstrip())


class MarkdownDomainNode:
    def plain_name(self, text: str) -> str:
        name = text.replace("**", "").replace("`", "").strip()
        if "|" in name:
            name = name.split("|", 1)[0]
        return name.strip()

    def owner_from(self, heading: str) -> str:
        if "|" not in heading:
            return ""
        return heading.split("|", 1)[1].strip()


class MarkdownIntegration(Integration, MarkdownDomainNode):
    pass


class MarkdownInvariantObject(InvariantObject, MarkdownDomainNode):
    pass


class MarkdownEntity(Entity, MarkdownDomainNode):
    def __init__(self, name: str = "", sequential_order: int = 0, member_lines: list[str] | None = None, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self._member_lines = list(member_lines or [])
        self._member_index = 0
        self.invariant_object_type = MarkdownInvariantObject

    def has_more_invariant_object(self) -> bool:
        return self._member_index < len(self._member_lines)

    def get_next_invariant_object_from_file(self) -> InvariantObject:
        line = self._member_lines[self._member_index].strip()
        self._member_index += 1
        return MarkdownInvariantObject(self.plain_name(line), len(self.invariant_objects))


class MarkdownAggregate(Aggregate, MarkdownDomainNode):
    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        # The lines under the aggregate's heading; `load_root` reads the root, its cards, and its arcs from them.
        self.source_lines: list[str] = []
        self.cards: list[ClassCard] = []
        # The sketch heading this aggregate was listed under, so the map keeps the sketch's grouping.
        self.group: str | None = None

    def load_root(self) -> None:
        sections, map_lines = split_cards(self.source_lines)
        self.cards.extend(read_card(section) for section in sections)
        self._read_map_lines(map_lines)
        self.take_root_card()
        super().load_root()

    @property
    def root_card(self) -> ClassCard | None:
        return next((card for card in self.cards if card.is_root), None)

    @property
    def repository(self) -> ClassCard | None:
        return next((card for card in self.cards if card.is_repository), None)

    @property
    def member_cards(self) -> list[ClassCard]:
        """The entities and values the root composes."""
        return [card for card in self.cards if not card.is_root and not card.is_repository]

    @property
    def ordered_cards(self) -> list[ClassCard]:
        """Root, then its repository, then members — the same order in every aggregate."""
        roots = [card for card in self.cards if card.is_root]
        repositories = [card for card in self.cards if card.is_repository]
        return roots + repositories + self.member_cards

    def take_root_card(self) -> None:
        """At model fidelity the root is the <<Aggregate Root>> card; its members are the other non-repository cards."""
        root = self.root_card
        if root is None:
            return
        events = self.events
        self.take_root(root.node)
        self.root.properties.extend(event for event in events if event not in self.root.properties)
        self.root.invariant_objects = [
            MarkdownInvariantObject(card.node.name, index) for index, card in enumerate(self.member_cards)
        ]
        for card in self.cards:
            if isinstance(card.node, Repository):
                card.node.accesses = self.root

    def _read_map_lines(self, lines: list[str]) -> None:
        root_name = self.name
        members: list[str] = []
        emitted: list[str] = []
        index = 0
        while index < len(lines):
            raw = lines[index]
            line = raw.strip().lower()
            if line.startswith("integrations:"):
                index = self._read_integrations(lines, index)
                continue
            if line.startswith(("emits events:", "consumes events:")):
                names, index = self._read_event_names(lines, index + 1)
                emitted.extend(names if line.startswith("emits") else [])
                continue
            if " - " in line and not raw.startswith(" "):
                root_name = self.plain_name(raw.split(" - ", 1)[0])
            elif raw.startswith("  ") and line and not line.startswith("-"):
                members.append(raw.split("//", 1)[0].strip())
            index += 1
        self._open_root(root_name, members, emitted)

    def _read_event_names(self, lines: list[str], index: int) -> tuple[list[str], int]:
        names: list[str] = []
        while index < len(lines) and lines[index].strip().startswith("-"):
            names.append(self.plain_name(lines[index].strip()[1:]))
            index += 1
        return names, index

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
        heading_indent = _indent(lines[index])
        current: MarkdownIntegration | None = None
        for index in range(index + 1, len(lines)):
            raw = lines[index]
            line = raw.strip()
            if not line:
                continue
            if _indent(raw) <= heading_indent:
                return index
            if line.startswith("- "):
                current = self._new_integration(line[2:])
            elif current is not None and ":" in line:
                key, value = (part.strip() for part in line.split(":", 1))
                if key.lower() in _FIELD_NAMES:
                    setattr(current, _FIELD_NAMES[key.lower()], value)
        return len(lines)

    def _new_integration(self, target: str) -> MarkdownIntegration:
        integration = MarkdownIntegration()
        integration.target = self.plain_name(target.split("(by", 1)[0])
        integration.context, integration.aggregate, _entity = integration.target_parts
        self.integrations.append(integration)
        return integration

    def lines(self) -> list[str]:
        written = [f"{_AGGREGATE}{self.name}", ""]
        if self.cards:
            for card in self.ordered_cards:
                written.extend(card.lines())
        elif self.root is not None:
            written.append(self.root.name)
            written.extend(f"  {item.name}" for item in self.root.operations)
            written.extend(f"  {item.name}" for item in self.root.invariant_objects)
            written.append("")
        written.extend(self.integration_lines())
        return written

    def integration_lines(self, indent: str = "") -> list[str]:
        """The aggregate's arcs and the events its root emits, under `Integrations:` and `emits events:`."""
        written: list[str] = []
        if self.integrations:
            written.append(f"{indent}Integrations:")
            for item in self.integrations:
                written.append(f"{indent}  - {item.target}")
                written.extend(
                    f"{indent}    {key}: {getattr(item, key)}" for key in _INTEGRATION_FIELDS if getattr(item, key)
                )
            written.append("")
        if self.events:
            written.append(f"{indent}emits events:")
            written.extend(f"{indent}  - {event.name}" for event in self.events)
            written.append("")
        return written


class MarkdownBoundedContext(BoundedContext, MarkdownDomainNode):
    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        # Why the context exists and what it must not do, as the sketch noted it above its aggregates.
        self.notes: list[str] = []
        # The clean-engineering module the context is built as, with the seam and constraint noted on it.
        self.module_name = ""
        self.module_notes: list[str] = []
        # The notes under each heading that groups aggregates, by that heading.
        self.group_notes: dict[str, list[str]] = {}

    def lines(self) -> list[str]:
        written = [f"{_CONTEXT}{self.name} | {self.owner or ''}", ""]
        written.extend(_quoted(self.notes))
        if self.module_name:
            written.append(f"{_MODULE} `{self.module_name}`")
            written.extend(_quoted(self.module_notes))
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
        text = line[len(_NOTE):].strip()
        if group is not None:
            self.group_notes.setdefault(group, []).append(text)
        elif self.module_name:
            self.module_notes.append(text)
        else:
            self.notes.append(text)

    def _group_lines(self, group: str) -> list[str]:
        notes = self.group_notes.get(group, [])
        if not notes:
            return []
        return [f"*{group}*"] + _quoted(notes) + [""]


def _quoted(notes: list[str]) -> list[str]:
    written = [f"{_NOTE}{text.strip()}" for text in notes if text.strip()]
    return written + [""] if written else []


class MarkdownBoundedContextMap(BoundedContextMap, MarkdownDomainNode):
    def __init__(self, source: BoundedContextMap | None = None) -> None:
        super().__init__(source)
        self.bounded_context_type = MarkdownBoundedContext
        self.aggregate_type = MarkdownAggregate

    def load_bounded_context_map_content(self) -> None:
        self._lines = Path(self.path).read_text(encoding="utf-8").splitlines()
        self._index = 0

    def has_more_bounded_context(self) -> bool:
        return self._next_context_at() is not None

    def get_next_bounded_context_from_file(self) -> BoundedContext:
        start = self._next_context_at()
        assert start is not None
        heading = self._lines[start].strip()[len(_CONTEXT):]
        context = MarkdownBoundedContext(self.plain_name(heading), len(self.contexts) + 1)
        context.owner = self.owner_from(heading)
        context._map = self
        end = self._next_heading_after(start)
        self._fill_context(context, start + 1, end)
        self._index = end
        return context

    def parse(self, text: str) -> "MarkdownBoundedContextMap":
        model = type(self)()
        model._lines = text.splitlines()
        model._index = 0
        model.load_bounded_contexts()
        return model

    def render(self, canonical=None, previous: str | None = None) -> str:
        source = canonical if canonical is not None else self
        if isinstance(source, MarkdownBoundedContextMap):
            body = source.save()
        else:
            body = type(self)(source).save()
        if previous and "## domain driven design:" in previous.lower():
            return self._wrap_bounded_context_document(body, previous)
        return body

    def save(self) -> str:
        has_cards = any(isinstance(item, MarkdownAggregate) and item.cards for item in self.every_aggregate)
        lines = ["# Domain Model" if has_cards else "# Bounded Context Map", ""]
        for context in self.contexts:
            if isinstance(context, MarkdownBoundedContext):
                lines.extend(context.lines())
        events = [event for aggregate in self.every_aggregate for event in aggregate.events]
        if events:
            lines.append(f"{_CONTEXT}{_EVENT_MAP}")
            lines.append("")
            for event in events:
                consumers = ", ".join(item.name for item in event.consumers)
                producer = event.producer.name if event.producer is not None else ""
                lines.append(f"- {event.name}: emitted by {producer}; consumed by {consumers}")
            lines.append("")
        return "\n".join(lines)

    def wire_events(self, entries: list[str]) -> None:
        """Read each `Event: emitted by Producer; consumed by A, B` entry of an event map onto its producer's root."""
        aggregates = {item.name: item for item in self.every_aggregate}
        services: dict[str, DomainService] = {}
        for entry in entries:
            _wire_event(entry, aggregates, services)

    def _wrap_bounded_context_document(self, body: str, sketch: str) -> str:
        title, sources = self._sketch_metadata(sketch)
        return "\n".join(
            [
                "---",
                "fidelity: [discovery]",
                "artifact: [bounded-context-map]",
                "format: md",
                "---",
                "",
                f"# Bounded Context Map — {title}",
                "",
                f"**Sources / context:** {sources}",
                "",
                "---",
                "",
                body.removeprefix("# Bounded Context Map\n\n").rstrip(),
                "",
            ]
        )

    def _sketch_metadata(self, text: str) -> tuple[str, str]:
        title = "Product / Feature Name"
        sources = "see engagement sketch"
        sketch_suffix = re.compile(r"\s+sketch\s*$", re.IGNORECASE)
        trailing_separator = re.compile(r"[\s\-–—€”]+$")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                raw = stripped[2:].strip()
                title = sketch_suffix.sub("", raw).strip()
                title = trailing_separator.sub("", title).strip() or title
            if stripped.lower().startswith("source:"):
                sources = stripped.split(":", 1)[1].strip()
        return title, sources

    def _next_context_at(self) -> int | None:
        index = self._index
        while index < len(self._lines):
            line = self._lines[index].strip()
            if line.startswith(_CONTEXT) and not line.startswith(_AGGREGATE):
                title = line[len(_CONTEXT):].split("|", 1)[0].strip().lower()
                if title != _EVENT_MAP:
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

    def _fill_context(self, context: MarkdownBoundedContext, start: int, end: int) -> None:
        index = start
        group: str | None = None
        while index < end:
            line = self._lines[index].strip()
            if line.startswith(_AGGREGATE):
                index = self._read_aggregate(context, index, end, group)
                continue
            group = self._read_context_line(context, line, group)
            index += 1

    def _read_context_line(self, context: MarkdownBoundedContext, line: str, group: str | None) -> str | None:
        """Read a line between aggregates: a note, the module, or a group heading. Returns the group in force."""
        grouped = _GROUP.match(line)
        if grouped:
            return grouped.group(1)
        if line.startswith(_MODULE):
            context.module_name = line[len(_MODULE):].strip().strip("`")
        elif line.startswith(_NOTE):
            context.read_note(line, group)
        return group

    def _read_aggregate(self, context: MarkdownBoundedContext, start: int, end: int, group: str | None) -> int:
        aggregate = MarkdownAggregate(self.plain_name(self._lines[start].strip()[len(_AGGREGATE):]), len(context.aggregates) + 1)
        aggregate.group = group
        after = start + 1
        while after < end and not self._ends_aggregate(self._lines[after].strip()):
            after += 1
        aggregate.source_lines = self._lines[start + 1:after]
        context.append_aggregate(aggregate)
        aggregate.load_root()
        return after

    def _ends_aggregate(self, line: str) -> bool:
        return line.startswith(_AGGREGATE) or _GROUP.match(line) is not None

    def load_bounded_contexts(self) -> None:
        super().load_bounded_contexts()
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
