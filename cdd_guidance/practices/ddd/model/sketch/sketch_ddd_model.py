"""Sketch channel — the `domain driven design:` section of a sketch, read into and written from the bounded-context map."""

from __future__ import annotations

from cdd_guidance.actions.sketch.sketch_outline import SketchLens, SketchOutline
from cdd_guidance.practices.ddd.model.markdown.class_cards import card_from_sketch
from cdd_guidance.practices.ddd.model.markdown.nodes import (
    MarkdownAggregate,
    MarkdownBoundedContext,
    MarkdownBoundedContextMap,
)
from cdd_guidance.practices.ddd.model.stereotypes import plain_class_name, stereotypes_in, without_stereotypes

_NESTING_INDENT = 2
_SECTION = "## domain driven design:"
_CONTEXT = "### "
_HOLDER = "#### "
_ENTITY = "##### "
_FENCE = "```"
_EVENT_MAP = "event_map:"
_EVENT_HEADINGS = {"event_map:", "event map:", "event_map", "event map"}
_BUILD_ORDER = "build order"
_NOTE = "note:"
_PROSE_HEADINGS = (
    "false cognates to carry forward",
    "false cognates",
    "open questions",
    "settled",
)
_META_PREFIXES = ("fidelity:", "partition:")
# Lines at entity depth that are aggregate notes, not entities.
_NOT_ENTITIES = ("entry:", _NOTE, _BUILD_ORDER, "seam:", "constraint:", "//")


def _level(raw: str) -> int:
    return (len(raw) - len(raw.lstrip(" "))) // _NESTING_INDENT


def _is_context_heading(stripped: str) -> bool:
    if "|" not in stripped:
        return False
    lower = stripped.lower()
    return not any(lower.startswith(prefix) for prefix in _META_PREFIXES)


def _is_prose_heading(stripped: str) -> bool:
    lower = stripped.rstrip(":").strip().lower()
    if lower in _PROSE_HEADINGS or lower.startswith("false cognates"):
        return True
    return lower.startswith(_BUILD_ORDER)


def _is_entity_heading(stripped: str) -> bool:
    name = stripped.split("//", 1)[0].strip().rstrip(":")
    if not name or name.startswith("- "):
        return False
    if name.lower().startswith(_NOT_ENTITIES):
        return False
    return ":" not in name


def _is_module_heading(stripped: str) -> bool:
    return stripped.rstrip(":").strip().endswith("/")


class SketchDddModel(MarkdownBoundedContextMap):
    def parse(self, text: str) -> "SketchDddModel":
        model = type(self)()
        _SketchReader(model).read(SketchOutline(text, _NESTING_INDENT).body_for(SketchLens.of("ddd")))
        return model

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return _SketchWriter(canonical or self).text()


class _SketchReader:
    """Reads the ddd section of a sketch, flattened to indentation, one line at a time into a bounded-context map."""

    def __init__(self, model: MarkdownBoundedContextMap) -> None:
        self.model = model
        self.context: MarkdownBoundedContext | None = None
        self.aggregate: MarkdownAggregate | None = None
        self.group: str | None = None
        self.event_entries: list[str] = []
        self.in_events = False
        self.skipping = False
        self.in_meta = True
        self.used_holders: set[str] = set()
        # Each aggregate's entity fences, by aggregate: the heading and the lines of each class card it opens.
        self.fences: dict[int, list[tuple[str, list[str]]]] = {}

    def read(self, body: str) -> None:
        for raw in body.splitlines():
            self._read_line(raw)
        for aggregate in self.model.every_aggregate:
            fences = self.fences.get(id(aggregate), [])
            aggregate.cards = [card for heading, lines in fences for card in card_from_sketch(heading, lines)]
            aggregate.load_root()
        self.model.wire_events(self.event_entries)

    def _read_line(self, raw: str) -> None:
        stripped = raw.strip()
        if not stripped or stripped.startswith(("#", "---")) or self._reads_section_marker(stripped):
            return
        if self.in_events and stripped.startswith("- ") and ":" in stripped:
            self.event_entries.append(stripped[2:].split("//", 1)[0].strip())
            return
        self.in_events = False
        level = _level(raw)
        if self.in_meta and stripped.lower().startswith(_META_PREFIXES):
            return
        if level <= 0:
            self._read_top(stripped)
        elif self.skipping or self.context is None:
            return
        elif level == 1:
            self._read_holder(stripped)
        elif level == 2 and _is_entity_heading(stripped):
            self._open_entity(stripped.split("//", 1)[0].strip().rstrip(":"))
        else:
            self._read_detail(raw)

    def _reads_section_marker(self, stripped: str) -> bool:
        lowered = stripped.lower()
        if lowered.startswith(f"{_BUILD_ORDER}:"):
            self.skipping = True
            self.context = None
            self.aggregate = None
            return True
        if lowered in _EVENT_HEADINGS:
            self.in_events = True
            self.skipping = False
            return True
        return False

    def _read_top(self, stripped: str) -> None:
        if _is_context_heading(stripped):
            self._open_context(stripped)
        elif _is_prose_heading(stripped):
            self.skipping = True
            self.context = None
            self.aggregate = None
            self.group = None

    def _open_context(self, stripped: str) -> None:
        self.in_meta = False
        self.skipping = False
        name, _, owner = stripped.rstrip(":").partition("|")
        self.context = MarkdownBoundedContext(name.strip(), len(self.model.contexts) + 1)
        self.context.owner = owner.strip()
        self.model.append_context(self.context)
        self.aggregate = None
        self.group = None

    def _read_holder(self, stripped: str) -> None:
        self.aggregate = None
        self.group = None
        if stripped.lower().startswith(_NOTE):
            self.context.notes.append(stripped)
        elif _is_module_heading(stripped):
            self.context.module_name = stripped.rstrip(":").strip().rstrip("/").strip()
            self.context.module_notes = []
        else:
            self.group = without_stereotypes(stripped.rstrip(":"))
            self.context.group_notes.setdefault(self.group, [])

    def _open_entity(self, name: str) -> None:
        marks = [item.lower() for item in stereotypes_in(name)]
        fences = self.fences.get(id(self.aggregate), []) if self.aggregate is not None else []
        if marks and "aggregate root" not in marks and fences:
            # A member card at model fidelity joins the aggregate its root opened.
            fences.append((name, []))
            return
        self.aggregate = MarkdownAggregate(self._aggregate_name(name, marks), len(self.context.aggregates) + 1)
        self.fences[id(self.aggregate)] = [(name, [])] if marks else []
        self.aggregate.group = self.group
        self.context.append_aggregate(self.aggregate)

    def _aggregate_name(self, name: str, marks: list[str]) -> str:
        """A class card is named after the heading it sits under, the first time; a plain entity after itself."""
        if not marks:
            return name
        holder = self.group or self.context.module_name
        named = holder if holder and holder not in self.used_holders else plain_class_name(name)
        self.used_holders.add(holder)
        return named

    def _read_detail(self, raw: str) -> None:
        if self.aggregate is not None:
            fences = self.fences[id(self.aggregate)]
            if fences:
                fences[-1][1].append(raw)
            self.aggregate.source_lines.append(raw)
        elif self.group:
            self.context.group_notes[self.group].append(raw.strip())
        elif self.context.module_name:
            self.context.module_notes.append(raw.strip())
        else:
            self.context.notes.append(raw.strip())


class _SketchWriter:
    """Writes a bounded-context map as the `domain driven design:` section of a sketch."""

    def __init__(self, model: MarkdownBoundedContextMap) -> None:
        self.model = model
        self.written: list[str] = [_SECTION, ""]

    def text(self) -> str:
        for context in self.model.contexts:
            self._write_context(context)
        self._write_event_map()
        return "\n".join(self.written)

    def _write_context(self, context: MarkdownBoundedContext) -> None:
        self.written.extend([f"{_CONTEXT}{context.name} | {context.owner or ''}", ""])
        self._fence([note if note.lower().startswith(_NOTE) else f"{_NOTE} {note}" for note in context.notes])
        if context.module_name:
            self.written.extend([f"{_HOLDER}{context.module_name}/", ""])
            self._fence(context.module_notes)
        group: str | None = None
        for aggregate in context.aggregates:
            group = self._write_holder(context, aggregate, group)
            self._write_aggregate(aggregate)

    def _write_holder(self, context: MarkdownBoundedContext, aggregate: MarkdownAggregate, group: str | None) -> str | None:
        """Open the heading the aggregate sits under: its group, or its own name when its root card is named apart."""
        root = aggregate.root_card
        holder = aggregate.name if root is not None and root.node.name != aggregate.name else aggregate.group
        if not holder or holder == group:
            return group
        self.written.extend([f"{_HOLDER}{holder}", ""])
        self._fence(context.group_notes.get(holder, []))
        return holder

    def _write_aggregate(self, aggregate: MarkdownAggregate) -> None:
        if not aggregate.cards:
            self.written.extend([f"{_ENTITY}{aggregate.name}", ""])
            self._fence(self._map_lines(aggregate) + aggregate.integration_lines())
            return
        for card in aggregate.ordered_cards:
            arcs = aggregate.integration_lines() if card is aggregate.root_card else []
            self.written.extend([f"{_ENTITY}{card.heading}", ""])
            self._fence(card.sketch_lines() + arcs)

    def _map_lines(self, aggregate: MarkdownAggregate) -> list[str]:
        if aggregate.root is None:
            return []
        return [item.name for item in aggregate.root.operations] + [item.name for item in aggregate.root.invariant_objects]

    def _write_event_map(self) -> None:
        entries = [
            f"- {event.name}: emitted by {aggregate.name}; consumed by {', '.join(item.name for item in event.consumers)}"
            for aggregate in self.model.every_aggregate
            for event in aggregate.events
        ]
        if entries:
            self.written.extend([f"{_CONTEXT}{_EVENT_MAP}", ""])
            self._fence(entries)

    def _fence(self, lines: list[str]) -> None:
        kept = [line for line in lines if line.strip()]
        if kept:
            self.written.extend([_FENCE, *kept, _FENCE, ""])
