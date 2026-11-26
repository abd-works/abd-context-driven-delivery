"""Markdown channel: `## Context | owner` sections, `### Aggregate` sections under them, then the event map.

The map reads into and writes from the base nodes every format shares. *ContextSection* reads and writes a context's
section, and *AggregateSection* an aggregate's, so a map read from any format writes as markdown."""

from __future__ import annotations

import re

from cdd_guidance.practices.sketch_document.discovery_document import DiscoveryDocument
from cdd_guidance.practices.ddd.model.aggregate_lines import AggregateLines
from cdd_guidance.practices.ddd.model.building_blocks import owner_from, plain_name
from cdd_guidance.practices.ddd.model.markdown.class_cards import CARD, CardSection
from cdd_guidance.practices.ddd.model.nodes import Aggregate, BoundedContext, BoundedContextMap
from cdd_guidance.practices.ddd.model.markdown.replaced_document import ReplacedDocument
from harness.guidance.practice_formats import Written

_EVENT_MAP = "event map"
# The `##` sections a map holds that are no context: the event map, and the template's explanation of the map's format.
_NOT_CONTEXTS = (_EVENT_MAP, "map format")
# The map's own heading, which names it.
_TITLE = "# "
_CONTEXT = "## "
_AGGREGATE = "### "
_NOTE = "> "
_MODULE = "**Module:**"
# `*Group*`: the heading a sketch grouped the following aggregates under.
_GROUP = re.compile(r"^\*([^*].*?)\*$")
# Lines that end a card's section and return to the aggregate's own lines: its arcs, its events, the next aggregate.
_LEAVES_CARD = ("integrations:", "emits events:", "consumes events:", "### ")


class AggregateSection:
    """An aggregate's `###` section: what it keeps true, then its `####` cards at model fidelity or its root line and
    members at bounded-context fidelity, then its arcs and events."""

    def __init__(self, aggregate: Aggregate) -> None:
        self._aggregate = aggregate

    def read(self, lines: list[str]) -> None:
        """Read the lines under the aggregate's heading: each `####` card section, then its own lines."""
        sections, own_lines = self._split_cards(lines)
        self._aggregate.classes.extend(card for section in sections for card in CardSection.read(section))
        AggregateLines(self._aggregate).read(own_lines)

    def _split_cards(self, lines: list[str]) -> tuple[list[list[str]], list[str]]:
        """Separate this aggregate's `####` card sections from its own lines: its root line, integrations, events."""
        cards: list[list[str]] = []
        rest: list[str] = []
        current: list[str] | None = None
        for raw in lines:
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

    def lines(self) -> list[str]:
        aggregate = self._aggregate
        written = [f"{_AGGREGATE}{aggregate.name}", ""]
        if aggregate.description:
            written.extend([*aggregate.description.split("\n"), ""])
        if aggregate.classes:
            for card in aggregate.ordered_cards:
                written.extend(CardSection(card).lines())
        elif aggregate.root is not None:
            root = aggregate.root
            written.append(f"{root.name} - {root.intent}" if root.intent else root.name)
            written.extend(f"  {item.name}" for item in root.operations)
            written.extend(f"  {item.name}" for item in root.invariant_objects)
            written.append("")
        written.extend(AggregateLines(aggregate).integration_lines())
        return written


class ContextSection:
    """A context's `## Context | owner` section: what it is, its `> ` notes, its module, the `*Group*` headings that
    group its aggregates with their notes, and each aggregate's section."""

    def __init__(self, context: BoundedContext) -> None:
        self._context = context

    def read(self, lines: list[str]) -> None:
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
        context = self._context
        grouped = _GROUP.match(line)
        if grouped:
            return grouped.group(1)
        if line.startswith(_MODULE):
            context.module_name = line[len(_MODULE):].strip().strip("`")
        elif line.startswith(_NOTE):
            context.keep_note(line[len(_NOTE):].strip(), group)
        elif line.strip("-"):
            context.description = f"{context.description}\n{line}".strip()
        return group

    def _read_aggregate(self, lines: list[str], start: int, group: str | None) -> int:
        """The aggregate whose heading is at start, reading its own section; returns the line after the section."""
        context = self._context
        aggregate = context.aggregate_type(plain_name(lines[start].strip()[len(_AGGREGATE):]), len(context.aggregates) + 1)
        aggregate.group = group
        after = self._aggregate_end(lines, start)
        context.append_aggregate(aggregate)
        AggregateSection(aggregate).read(lines[start + 1:after])
        return after

    def _aggregate_end(self, lines: list[str], start: int) -> int:
        """An aggregate's section ends at the next aggregate heading or group heading."""
        after = start + 1
        while after < len(lines) and not (lines[after].strip().startswith(_AGGREGATE) or _GROUP.match(lines[after].strip())):
            after += 1
        return after

    def lines(self) -> list[str]:
        context = self._context
        written = [f"{_CONTEXT}{context.name} | {context.owner or ''}", ""]
        if context.description:
            written.extend([*context.description.split("\n"), ""])
        written.extend(_quoted(context.notes))
        if context.module_name:
            written.append(f"{_MODULE} `{context.module_name}`")
            written.extend(_quoted(context.module_notes))
            written.append("")
        for nested in context.contexts:
            written.extend(ContextSection(nested).lines())
        last_group: str | None = None
        for aggregate in context.aggregates:
            if aggregate.group and aggregate.group != last_group:
                last_group = aggregate.group
                written.extend(self._group_lines(aggregate.group))
            written.extend(AggregateSection(aggregate).lines())
        return written

    def _group_lines(self, group: str) -> list[str]:
        notes = self._context.group_notes.get(group, [])
        if not notes:
            return []
        return [f"*{group}*"] + _quoted(notes) + [""]


def _quoted(notes: list[str]) -> list[str]:
    written = [f"{_NOTE}{text.strip()}" for text in notes if text.strip()]
    return written + [""] if written else []


class MarkdownBoundedContextMap(BoundedContextMap):
    """The `markdown` format: `## Context | owner` headings, `### Aggregate` sections under them, then the event map."""

    def __init__(self) -> None:
        super().__init__()
        # The lines of the text being parsed, and the line the next context is looked for from.
        self._lines: list[str] = []
        self._index = 0

    def _read_context_at(self, start: int) -> BoundedContext:
        """The context whose `## Context | owner` heading is at start, holding the lines up to the next heading."""
        heading = self._lines[start].strip()[len(_CONTEXT):]
        context = self.bounded_context_type(plain_name(heading), len(self.contexts) + 1)
        context.owner = owner_from(heading)
        end = self._next_heading_after(start)
        ContextSection(context).read(self._lines[start + 1:end])
        self._index = end
        return context

    def parse(self, text: str, file: str = "") -> "MarkdownBoundedContextMap":
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

    def render(self, canonical: BoundedContextMap, written: Written = Written()) -> str:
        """canonical as markdown; under the header of the sketch it came from when the previous text is a sketch. A map
        read from a drawing first takes, from the markdown file it is written over, the words a drawing does not
        hold."""
        source = canonical
        previous = written.previous
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
            lines.extend(ContextSection(context).lines())
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
