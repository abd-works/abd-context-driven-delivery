"""Markdown channel. Each node reads only the next child in the file."""

from __future__ import annotations

import re

from cdd_guidance.practices.sketch_document.discovery_document import DiscoveryDocument
from cdd_guidance.practices.clean_engineering.model.base_class_model import Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.type_refs import pascal_type_names
from cdd_guidance.practices.ddd.model.markdown.class_cards import (
    CARD,
    ClassCard,
    MarkdownDomainNode,
    MarkdownEntity,
)
from cdd_guidance.practices.ddd.model.nodes import (
    Aggregate,
    BoundedContext,
    BoundedContextMap,
    DomainEvent,
    Integration,
)
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import marks_in, without_marks
from cdd_guidance.practices.ddd.model.stereotypes import kind_named_by, plain_class_name

_EVENT_MAP = "event map"
_CONTEXT = "## "
_AGGREGATE = "### "
_NOTE = "> "
_MODULE = "**Module:**"
_INTEGRATIONS = "Integrations:"
# `*Group*`: the heading a sketch grouped the following aggregates under.
_GROUP = re.compile(r"^\*([^*].*?)\*$")
# `integrate:` is the sketch's word for the integration field.
_FIELD_NAMES = {"integrate": "integration", "context": "context", "aggregate": "aggregate"} | {
    field: field for field in Integration.FIELDS
}
# Lines that end a card's section and return to the aggregate's own lines: its arcs, its events, the next aggregate.
_LEAVES_CARD = ("integrations:", "emits events:", "consumes events:", "### ")
# The `domain driven design:` section of a sketch, flattened to indentation: a context is `### Name | owner`, the
# heading that holds aggregates `#### group` or `#### module/`, and an entity `##### Name`, each with a fence below.
SKETCH_INDENT = 2
SKETCH_CONTEXT = "### "
_SKETCH_HOLDER = "#### "
_SKETCH_ENTITY = "##### "
_FENCE = "```"
_SKETCH_NOTE = "note:"
BUILD_ORDER = "build order"
# Lines at entity depth that are aggregate notes, not entities.
_NOT_ENTITIES = ("entry:", _SKETCH_NOTE, BUILD_ORDER, "seam:", "constraint:", "//")


def looks_like_operation(line: str) -> bool:
    """A single lower-case word under the root names one of its operations; anything else names a member."""
    if not line or " " in line:
        return False
    if line.endswith(":"):
        return False
    return line[0].islower()


def _indent(raw: str) -> int:
    return len(raw) - len(raw.lstrip())


def _ends_aggregate(line: str) -> bool:
    """An aggregate's section ends at the next aggregate heading or group heading."""
    return line.startswith(_AGGREGATE) or _GROUP.match(line) is not None


def sketch_level(raw: str) -> int:
    """How deep a flattened sketch line sits: 0 for a context heading, 1 for a holder, 2 for an entity."""
    return (len(raw) - len(raw.lstrip(" "))) // SKETCH_INDENT


def _is_entity_heading(stripped: str) -> bool:
    name = stripped.split("//", 1)[0].strip().rstrip(":")
    if not name or name.startswith("- "):
        return False
    if name.lower().startswith(_NOT_ENTITIES):
        return False
    return ":" not in name


def _is_module_heading(stripped: str) -> bool:
    return stripped.rstrip(":").strip().endswith("/")


def fenced(lines: list[str]) -> list[str]:
    """The lines with text in a sketch fence, then a blank line; nothing when no line has text."""
    kept = [line for line in lines if line.strip()]
    return [_FENCE, *kept, _FENCE, ""] if kept else []


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
        """An arc to the class text names; the context and aggregate its target names are its own."""
        integration = MarkdownIntegration()
        integration.target = integration.plain_name(text.split("(by", 1)[0])
        integration.context, integration.aggregate, _entity = integration.target_parts
        return integration

    @staticmethod
    def kept_by(dependency: Relationship) -> "MarkdownIntegration | None":
        """The arc a class model's dependency keeps, when it keeps one: a dependency that names the arc's target."""
        target = dependency.details.get(Integration.TARGET)
        if not target:
            return None
        integration = MarkdownIntegration.targeting(target)
        integration.read_dependency(dependency)
        return integration

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
        # The sketch heading this aggregate was listed under, so the map keeps the sketch's grouping.
        self.group: str | None = None
        # The entity fences a sketch lists under this aggregate: each card's heading and the lines of its fence.
        self.sketch_fences: list[tuple[str, list[str]]] = []

    def take_sketch_line(self, raw: str) -> None:
        """One sketch line under this aggregate's entity: its own line, and a line of the fence it is in."""
        if self.sketch_fences:
            self.sketch_fences[-1][1].append(raw)
        self.source_lines.append(raw)

    def load_sketch(self) -> None:
        """Read the sketch's fences into cards, then the root from this aggregate's lines and its root card."""
        self.classes = [card for heading, lines in self.sketch_fences for card in ClassCard.from_sketch(heading, lines)]
        self.load_root()

    @property
    def sketch_holder(self) -> str | None:
        """The heading a sketch lists this aggregate under: its own name when its root card is named apart, else
        its group."""
        root = self.root_card
        return self.name if root is not None and root.name != self.name else self.group

    def sketch_lines(self) -> list[str]:
        """The aggregate in a sketch: its entity and fence, or each card's heading and fence, its arcs on the root."""
        if not self.classes:
            members = [item.name for item in self.root.operations] + [item.name for item in self.root.invariant_objects] if self.root is not None else []
            return [f"{_SKETCH_ENTITY}{self.name}", ""] + fenced(members + self.integration_lines())
        written: list[str] = []
        for card in self.ordered_cards:
            arcs = self.integration_lines() if card is self.root_card else []
            written.extend([f"{_SKETCH_ENTITY}{card.heading}", ""] + fenced(card.sketch_lines() + arcs))
        return written

    def load_root(self) -> None:
        sections, map_lines = self._split_cards()
        self.classes.extend(ClassCard.read(section) for section in sections)
        self._read_map_lines(map_lines)
        self.take_root_card()
        super().load_root()

    @property
    def root_card(self) -> ClassCard | None:
        return next((card for card in self.classes if card.is_root), None)

    @property
    def repository(self) -> ClassCard | None:
        return next((card for card in self.classes if card.is_repository), None)

    @property
    def member_cards(self) -> list[ClassCard]:
        """The entities and values the root composes."""
        return [card for card in self.classes if not card.is_root and not card.is_repository]

    @property
    def ordered_cards(self) -> list[ClassCard]:
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
            if name and name.lower() not in seen and not _looks_like_prose(name) and not looks_like_operation(name):
                seen.add(name.lower())
                drawn.append(name)
        return drawn

    def take_drawn_root(self, members: list[str]) -> None:
        """The root a map drawing shows: the aggregate's own entity, holding the members listed under it."""
        self._open_root(self.name, members, [])
        super().load_root()

    def take_root_card(self) -> None:
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
        self.classes.append(ClassCard.from_code(oclass))
        arcs = (MarkdownIntegration.kept_by(dependency) for dependency in oclass.dependencies)
        self.integrations.extend(arc for arc in arcs if arc is not None)

    def take_root_from_classes(self) -> None:
        """Once its cards are read from a class model: the relationships their types name, and the root card, else a
        root named after the aggregate."""
        self.infer_relationships()
        self.take_root_card()
        if self.root is None:
            self.root = MarkdownEntity(self.name, 1)

    def write_classes_into(self, module: Module) -> None:
        """Write the aggregate into module as code holds it: each card a class kept in the aggregate's place, and the
        root alone when it has no cards."""
        for card in self.ordered_cards:
            card.write_into(module, self.place_labels)
        if not module.classes and self.root is not None:
            self.root.write_into(module, self.place_labels)
        self._depend_across(module)

    def _depend_across(self, module: Module) -> None:
        """Each class depends on the class of another aggregate its operations call, named by the calling operation,
        and the root on each class an integration reaches, the arc kept whole as that dependency."""
        local = {card.name for card in self.classes} | {self.name}
        for oclass in module.classes:
            for operation in oclass.operations:
                for callee in operation.callees:
                    target, dot, _called = callee.strip().partition(".")
                    if dot and target[:1].isupper() and target not in local:
                        oclass.depend_on(target, operation.name)
        if module.classes:
            module.classes[0].dependencies.extend(item.as_dependency() for item in self.integrations if item.target_name)

    def infer_relationships(self) -> None:
        """Code holds `identity: Identity`, not `<< composition >>`: a member the aggregate holds is composed, and a
        repository's collection of the root is an aggregation."""
        members = {card.name for card in self.member_cards}
        roots = {card.name for card in self.classes if card.is_root}
        for card in self.classes:
            for prop in card.plain_properties:
                if prop.stereotype:
                    continue
                named = pascal_type_names(prop.type_hint or "")
                if card.is_repository and any(part in roots for part in named) and prop.type_hint.strip() not in roots:
                    prop.stereotype = "aggregation"
                elif named and named[0] in members:
                    prop.stereotype = "composition"

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
        root_name = self.name
        members: list[str] = []
        emitted: list[str] = []
        index = 0
        while index < len(lines):
            raw = lines[index]
            line = raw.strip().lower()
            if line.startswith(_INTEGRATIONS.lower()):
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
        end = index + 1
        while end < len(lines) and (not lines[end].strip() or _indent(lines[end]) > heading_indent):
            end += 1
        self.integrations.extend(MarkdownIntegration.read_arcs(lines[index + 1:end]))
        return end

    def lines(self) -> list[str]:
        written = [f"{_AGGREGATE}{self.name}", ""]
        if self.classes:
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
            written.append(f"{indent}{_INTEGRATIONS}")
            written.extend(f"{indent}  {line}" for item in self.integrations for line in item.lines())
            written.append("")
        if self.events:
            written.append(f"{indent}emits events:")
            written.extend(f"{indent}  - {event.name}" for event in self.events)
            written.append("")
        return written


class MarkdownBoundedContext(BoundedContext, MarkdownDomainNode):
    aggregate_type = MarkdownAggregate

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        # Why the context exists and what it must not do, as the sketch noted it above its aggregates.
        self.notes: list[str] = []
        # The clean-engineering module the context is built as, with the seam and constraint noted on it.
        self.module_name = ""
        self.module_notes: list[str] = []
        # The notes under each heading that groups aggregates, by that heading.
        self.group_notes: dict[str, list[str]] = {}

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
        """Read a line between aggregates: a note, the module, or a group heading. Returns the group in force."""
        grouped = _GROUP.match(line)
        if grouped:
            return grouped.group(1)
        if line.startswith(_MODULE):
            self.module_name = line[len(_MODULE):].strip().strip("`")
        elif line.startswith(_NOTE):
            self.read_note(line, group)
        return group

    def _read_aggregate(self, lines: list[str], start: int, group: str | None) -> int:
        aggregate = self.aggregate_type(self.plain_name(lines[start].strip()[len(_AGGREGATE):]), len(self.aggregates) + 1)
        aggregate.group = group
        after = start + 1
        while after < len(lines) and not _ends_aggregate(lines[after].strip()):
            after += 1
        aggregate.source_lines = lines[start + 1:after]
        self.append_aggregate(aggregate)
        aggregate.load_root()
        return after

    def read_sketch_lines(self, lines: list[str]) -> None:
        """Read this context's lines of a sketch: the holders that group its aggregates or name its module, each
        entity that opens an aggregate or joins the one its root opened, and the notes and fences under them."""
        aggregate: MarkdownAggregate | None = None
        group: str | None = None
        used_holders: set[str] = set()
        for raw in lines:
            stripped = raw.strip()
            level = sketch_level(raw)
            if level == 1:
                aggregate, group = None, self._read_sketch_holder(stripped)
            elif level == 2 and _is_entity_heading(stripped):
                aggregate = self._open_sketch_entity(stripped.split("//", 1)[0].strip().rstrip(":"), aggregate, group, used_holders)
            elif aggregate is not None:
                aggregate.take_sketch_line(raw)
            elif group:
                self.group_notes[group].append(stripped)
            elif self.module_name:
                self.module_notes.append(stripped)
            else:
                self.notes.append(stripped)
        for item in self.aggregates:
            item.load_sketch()

    def sketch_lines(self) -> list[str]:
        """The context in a sketch: its heading, its notes, its module, then each aggregate under its holder."""
        notes = [note if note.lower().startswith(_SKETCH_NOTE) else f"{_SKETCH_NOTE} {note}" for note in self.notes]
        written = [f"{SKETCH_CONTEXT}{self.name} | {self.owner or ''}", ""] + fenced(notes)
        if self.module_name:
            written.extend([f"{_SKETCH_HOLDER}{self.module_name}/", ""] + fenced(self.module_notes))
        group: str | None = None
        for aggregate in self.aggregates:
            holder = aggregate.sketch_holder
            if holder and holder != group:
                written.extend([f"{_SKETCH_HOLDER}{holder}", ""] + fenced(self.group_notes.get(holder, [])))
                group = holder
            written.extend(aggregate.sketch_lines())
        return written

    def _read_sketch_holder(self, stripped: str) -> str | None:
        """A holder line: a note, the module the context is built as, or a heading that groups aggregates, which
        is the group in force after it."""
        if stripped.lower().startswith(_SKETCH_NOTE):
            self.notes.append(stripped)
            return None
        if _is_module_heading(stripped):
            self.module_name = stripped.rstrip(":").strip().rstrip("/").strip()
            self.module_notes = []
            return None
        group = without_marks(stripped.rstrip(":"))
        self.group_notes.setdefault(group, [])
        return group

    def _open_sketch_entity(self, name: str, current: MarkdownAggregate | None, group: str | None, used_holders: set[str]) -> MarkdownAggregate:
        """The aggregate an entity heading belongs to: a member card joins the aggregate its root opened; any other
        entity opens one, named after the heading it sits under the first time, else after itself."""
        marks = marks_in(name)
        if marks and kind_named_by(marks) != "EntityRoot" and current is not None and current.sketch_fences:
            current.sketch_fences.append((name, []))
            return current
        aggregate_name = name
        if marks:
            holder = group or self.module_name
            aggregate_name = holder if holder and holder not in used_holders else plain_class_name(name)
            used_holders.add(holder)
        aggregate = self.aggregate_type(aggregate_name, len(self.aggregates) + 1)
        aggregate.sketch_fences = [(name, [])] if marks else []
        aggregate.group = group
        self.append_aggregate(aggregate)
        return aggregate

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
    """The `markdown` format: `## Context | owner` headings, `### Aggregate` sections under them, then the event map."""

    bounded_context_type = MarkdownBoundedContext

    def __init__(self) -> None:
        super().__init__()
        # The lines of the text being parsed, and the line the next context is looked for from.
        self._lines: list[str] = []
        self._index = 0

    def has_more_bounded_context(self) -> bool:
        return self._next_context_at() is not None

    def get_next_bounded_context_from_file(self) -> BoundedContext:
        start = self._next_context_at()
        assert start is not None
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
        self.load_bounded_contexts()
        return self

    @property
    def holds_classes_only(self) -> bool:
        """A markdown text that names no aggregate is a plain class model, which Clean Engineering's markdown reads."""
        return not self.every_aggregate

    def render(self, canonical: BoundedContextMap | None = None, previous: str | None = None) -> str:
        """canonical (this map when none is given) as markdown; under the header of the sketch it came from when the
        previous text is a sketch."""
        body = self._text(canonical or self)
        if previous and "## domain driven design:" in previous.lower():
            return self._wrap_bounded_context_document(body, previous)
        return body

    def save(self) -> str:
        return self._text(self)

    def _text(self, source: BoundedContextMap) -> str:
        """source as markdown: each context's own lines, then the event map."""
        lines = ["# Domain Model" if source.has_class_cards else "# Bounded Context Map", ""]
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


def _looks_like_prose(line: str) -> bool:
    """A note or a sentence, not a member's name."""
    text = line.strip()
    if not text or text.lower().startswith("note:"):
        return True
    return ". " in text or text.endswith(".") or text[0].islower()
