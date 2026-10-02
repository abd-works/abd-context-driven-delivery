"""Markdown channel. Each node reads only the next child in the file."""

from __future__ import annotations

from pathlib import Path

from practices.clean_engineering.model.property import Property
from practices.ddd.model.nodes import (
    Aggregate,
    BoundedContext,
    BoundedContextMap,
    DomainEvent,
    DomainService,
    Entity,
    Integration,
    InvariantObject,
)

_EVENT_MAP = "event map"


def _blank(line: str) -> bool:
    return not line.strip()


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

    def stereotypes(self, text: str) -> list[str]:
        found = []
        rest = text
        while "<<" in rest and ">>" in rest:
            found.append(rest.split("<<", 1)[1].split(">>", 1)[0].strip())
            rest = rest.split(">>", 1)[1]
        return found

    def building_block_type(self, text: str) -> type:
        marks = {item.lower() for item in self.stereotypes(text)}
        if "specification" in marks:
            from practices.ddd.model.nodes import Specification
            return Specification
        if "value object" in marks:
            from practices.ddd.model.nodes import ValueObject
            return ValueObject
        if "repository" in marks:
            from practices.ddd.model.nodes import Repository
            return Repository
        if "domain event" in marks:
            return DomainEvent
        if "domain service" in marks or "service" in marks:
            return DomainService
        if "factory" in marks:
            from practices.ddd.model.nodes import Factory
            return Factory
        if "entity" in marks or "aggregate root" in marks:
            return Entity
        return type(self)


class MarkdownIntegration(Integration, MarkdownDomainNode):
    pass


class MarkdownInvariantObject(InvariantObject, MarkdownDomainNode):
    pass


class MarkdownEntity(Entity, MarkdownDomainNode):
    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self._member_lines: list[str] = []
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
        self._body: list[str] = []
        self._body_index = 0

    def load_root(self) -> None:
        self._read_body()
        super().load_root()

    def has_more_integration(self) -> bool:
        return False

    def get_next_integration_from_file(self) -> Integration:
        return MarkdownIntegration()

    def _read_body(self) -> None:
        root_name = self.name
        members: list[str] = []
        emit_names: list[str] = []
        index = 0
        while index < len(self._body):
            raw = self._body[index]
            line = raw.strip()
            if line.lower().startswith("integrations:"):
                index = self._read_integrations(index + 1)
                continue
            if line.lower().startswith("emits:"):
                index += 1
                while index < len(self._body) and self._body[index].strip().startswith("-"):
                    emit_names.append(self.plain_name(self._body[index].strip()[1:]))
                    index += 1
                continue
            if line.lower().startswith("consumes:"):
                index += 1
                while index < len(self._body) and self._body[index].strip().startswith("-"):
                    index += 1
                continue
            if " - " in line and not raw.startswith(" "):
                root_name = self.plain_name(line.split(" - ", 1)[0])
            elif raw.startswith("  ") and line and not line.startswith("-"):
                members.append(line)
            index += 1
        self.root = MarkdownEntity(root_name, 1)
        self.root._member_lines = members
        for event_name in emit_names:
            event = DomainEvent(event_name, len(self.root.properties))
            event.producer = self
            self.root.properties.append(event)


    def _read_integrations(self, index: int) -> int:
        current: MarkdownIntegration | None = None
        while index < len(self._body):
            raw = self._body[index]
            line = raw.strip()
            if not line:
                index += 1
                continue
            if not raw.startswith(" ") and not raw.startswith("\t"):
                break
            if line.startswith("- "):
                current = MarkdownIntegration()
                current.target = self.plain_name(line[2:].split("(by", 1)[0])
                self.integrations.append(current)
            elif current is not None and ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key == "pattern":
                    current.pattern = value
                elif key == "direction":
                    current.direction = value
                elif key == "crosses":
                    current.crosses = value
                elif key == "integration":
                    current.integration = value
                elif key == "context":
                    current.context = value
                elif key == "aggregate":
                    current.aggregate = value
            index += 1
        return index

    def lines(self) -> list[str]:
        written = [f"### {self.name}", ""]
        if self.root is not None:
            written.append(self.root.name)
            for item in self.root.invariant_objects:
                written.append(f"  {item.name}")
            if self.integrations:
                written.append("")
                written.append("Integrations:")
                for item in self.integrations:
                    written.append(f"  - {item.target}")
                    if item.pattern:
                        written.append(f"    pattern: {item.pattern}")
                    if item.direction:
                        written.append(f"    direction: {item.direction}")
                    if item.crosses:
                        written.append(f"    crosses: {item.crosses}")
                    if item.integration:
                        written.append(f"    integration: {item.integration}")
            events = [item for item in self.root.properties if isinstance(item, DomainEvent)]
            if events:
                written.append("")
                written.append("emits:")
                for event in events:
                    written.append(f"  - {event.name}")
        written.append("")
        return written


class MarkdownBoundedContext(BoundedContext, MarkdownDomainNode):
    def lines(self) -> list[str]:
        written = [f"## {self.name} | {self.owner}", ""]
        for context in self.contexts:
            if isinstance(context, MarkdownBoundedContext):
                written.extend(context.lines())
        for aggregate in self.aggregates:
            if isinstance(aggregate, MarkdownAggregate):
                written.extend(aggregate.lines())
        return written


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
        heading = self._lines[start].strip()[3:]
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
        del previous
        source = canonical if canonical is not None else self
        if isinstance(source, MarkdownBoundedContextMap):
            return source.save()
        return type(self)(source).save()

    def save(self) -> str:
        lines = ["# Bounded Context Map", ""]
        for context in self.contexts:
            if isinstance(context, MarkdownBoundedContext):
                lines.extend(context.lines())
        events = _events_in(self)
        if events:
            lines.append("## event map")
            lines.append("")
            for event in events:
                consumers = ", ".join(_consumer_name(item) for item in event.consumers)
                producer = event.producer.name if event.producer is not None else ""
                lines.append(f"- {event.name}: emitted by {producer}; consumed by {consumers}")
            lines.append("")
        return "\n".join(lines)

    def _next_context_at(self) -> int | None:
        index = self._index
        while index < len(self._lines):
            line = self._lines[index].strip()
            if line.startswith("## ") and not line.startswith("### "):
                title = line[3:].split("|", 1)[0].strip().lower()
                if title != _EVENT_MAP:
                    return index
            index += 1
        return None

    def _next_heading_after(self, start: int) -> int:
        index = start + 1
        while index < len(self._lines):
            line = self._lines[index].strip()
            if line.startswith("## ") and not line.startswith("### "):
                return index
            index += 1
        return len(self._lines)

    def _fill_context(self, context: MarkdownBoundedContext, start: int, end: int) -> None:
        index = start
        body = self._lines
        while index < end:
            line = body[index].strip()
            if line.startswith("### "):
                aggregate = MarkdownAggregate(self.plain_name(line[4:]), len(context.aggregates) + 1)
                next_at = index + 1
                while next_at < end and not body[next_at].strip().startswith("### "):
                    next_at += 1
                aggregate._body = body[index + 1:next_at]
                context.append_aggregate(aggregate)
                aggregate.load_root()
                index = next_at
                continue
            index += 1

    def load_bounded_contexts(self) -> None:
        super().load_bounded_contexts()
        self._apply_event_map()

    def _apply_event_map(self) -> None:
        aggregates = {item.name: item for item in _aggregates_in(self)}
        services = {item.name: item for item in _services_in(self)}
        index = 0
        while index < len(self._lines):
            line = self._lines[index].strip()
            if line.startswith("## ") and line[3:].split("|", 1)[0].strip().lower() == _EVENT_MAP:
                index += 1
                while index < len(self._lines) and not self._lines[index].strip().startswith("## "):
                    item = self._lines[index].strip()
                    if item.startswith("- ") and ":" in item:
                        _wire_event(item[2:], aggregates, services)
                    index += 1
                return
            index += 1


def _aggregates_in(bounded_context_map: BoundedContextMap) -> list[Aggregate]:
    found: list[Aggregate] = []

    def take(context: BoundedContext) -> None:
        found.extend(context.aggregates)
        for child in context.contexts:
            take(child)

    for context in bounded_context_map.contexts:
        take(context)
    return found


def _services_in(bounded_context_map: BoundedContextMap) -> list[DomainService]:
    found: list[DomainService] = []
    for aggregate in _aggregates_in(bounded_context_map):
        if aggregate.root is None:
            continue
        for item in aggregate.root.properties:
            if isinstance(item, DomainService):
                found.append(item)
    return found


def _events_in(bounded_context_map: BoundedContextMap) -> list[DomainEvent]:
    found: list[DomainEvent] = []
    for aggregate in _aggregates_in(bounded_context_map):
        if aggregate.root is None:
            continue
        for item in aggregate.root.properties:
            if isinstance(item, DomainEvent):
                found.append(item)
    return found


def _consumer_name(consumer: Aggregate | DomainService) -> str:
    return consumer.name


def _wire_event(text: str, aggregates: dict[str, Aggregate], services: dict[str, DomainService]) -> None:
    # CartCheckedOut: emitted by ShoppingCart; consumed by Inventory, Receipt
    name, rest = text.split(":", 1)
    emitted = ""
    consumed = ""
    if "consumed by" in rest:
        emitted, consumed = rest.split("consumed by", 1)
    else:
        emitted = rest
    producer_name = emitted.replace("emitted by", "").strip(" ;")
    producer = aggregates.get(producer_name)
    if producer is None or producer.root is None:
        return
    event = next((item for item in producer.root.properties if isinstance(item, DomainEvent) and item.name == name.strip()), None)
    if event is None:
        event = DomainEvent(name.strip(), len(producer.root.properties))
        event.producer = producer
        producer.root.properties.append(event)
    event.producer = producer
    event.subject = Property("subject", 0, description="the state of the event")
    for part in consumed.split(","):
        consumer_name = part.strip()
        if not consumer_name:
            continue
        if consumer_name in aggregates:
            event.consumers.append(aggregates[consumer_name])
        elif consumer_name in services:
            event.consumers.append(services[consumer_name])
        else:
            service = DomainService(consumer_name, len(event.consumers) + 1)
            services[consumer_name] = service
            event.consumers.append(service)
