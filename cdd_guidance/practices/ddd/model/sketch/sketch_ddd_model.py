"""Sketch channel — indent bounded-context map from a DDD sketch."""

from __future__ import annotations

from cdd_guidance.actions.sketch.sketch_outline import SketchLens, SketchOutline
from cdd_guidance.practices.ddd.model.markdown.class_cards import card_from_sketch, plain_class_name, stereotypes_in
from cdd_guidance.practices.ddd.model.markdown.nodes import (
    MarkdownAggregate,
    MarkdownBoundedContext,
    MarkdownBoundedContextMap,
    _aggregates_in,
    _services_in,
    _wire_event,
)

_NESTING_INDENT = 2
_EVENT_HEADINGS = {"event_map:", "event map:", "event_map", "event map"}
_PROSE_HEADINGS = (
    "false cognates to carry forward",
    "false cognates",
    "open questions",
    "settled",
)
_META_PREFIXES = ("fidelity:", "partition:")


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
    return lower.startswith("build order")


def _is_entity_heading(stripped: str) -> bool:
    name = stripped.split("//", 1)[0].strip().rstrip(":")
    if not name or name.startswith("- "):
        return False
    lower = name.lower()
    if lower.startswith(("entry:", "note:", "build order", "seam:", "constraint:", "//")):
        return False
    if name.endswith(":"):
        return False
    if ":" in name:
        return False
    return True


def _is_module_heading(stripped: str) -> bool:
    return stripped.rstrip(":").strip().endswith("/")


class SketchDddModel(MarkdownBoundedContextMap):
    def parse(self, text: str) -> "SketchDddModel":
        model = type(self)()
        body = SketchOutline(text, _NESTING_INDENT).body_for(SketchLens.domain_driven_design)
        context: MarkdownBoundedContext | None = None
        aggregate: MarkdownAggregate | None = None
        current_group: str | None = None
        event_lines: list[str] = []
        in_events = False
        skip_section = False
        in_meta = True
        used_holders: set[str] = set()
        for raw in body.splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith(("#", "---")):
                continue
            lowered = stripped.lower()
            if lowered.startswith("build order:"):
                skip_section = True
                context = None
                aggregate = None
                continue
            if lowered in _EVENT_HEADINGS:
                in_events = True
                skip_section = False
                continue
            if in_events:
                if stripped.startswith("- ") and ":" in stripped:
                    event_lines.append(stripped[2:].split("//", 1)[0].strip())
                    continue
                in_events = False
            level = _level(raw)
            if in_meta and any(lowered.startswith(prefix) for prefix in _META_PREFIXES):
                continue
            if level <= 0 and _is_context_heading(stripped):
                in_meta = False
                skip_section = False
                name, _, vendor = stripped.rstrip(":").partition("|")
                context = MarkdownBoundedContext(name.strip(), len(model.contexts) + 1)
                context.owner = vendor.strip()
                context._map = model
                context._preamble = []
                context._module_name = ""
                context._module_body = []
                context._group_preambles = {}
                model.contexts.append(context)
                aggregate = None
                current_group = None
                continue
            if level <= 0 and _is_prose_heading(stripped):
                skip_section = True
                context = None
                aggregate = None
                current_group = None
                continue
            if skip_section or context is None:
                continue
            if level <= 0:
                continue
            if level == 1:
                aggregate = None
                if lowered.startswith("note:"):
                    context._preamble.append(stripped)
                    current_group = None
                    continue
                if _is_module_heading(stripped):
                    context._module_name = stripped.rstrip(":").strip().rstrip("/").strip()
                    context._module_body = []
                    current_group = None
                    continue
                name = stripped.rstrip(":")
                if "<<" in name:
                    name = name.split("<<", 1)[0].strip()
                current_group = name
                context._group_preambles.setdefault(current_group, [])
                continue
            if level == 2 and _is_entity_heading(stripped):
                name = stripped.split("//", 1)[0].strip().rstrip(":")
                marks = [item.lower() for item in stereotypes_in(name)]
                if marks and "aggregate root" not in marks and aggregate is not None and aggregate._sketch_cards:
                    # A member card at model fidelity joins the aggregate its root opened.
                    aggregate._sketch_cards.append((name, []))
                    continue
                if marks:
                    holder = current_group or context._module_name
                    aggregate_name = holder if holder and holder not in used_holders else plain_class_name(name)
                    used_holders.add(holder)
                    aggregate = MarkdownAggregate(aggregate_name, len(context.aggregates) + 1)
                    aggregate._sketch_cards = [(name, [])]
                else:
                    aggregate = MarkdownAggregate(name, len(context.aggregates) + 1)
                    aggregate._sketch_cards = []
                aggregate._group = current_group
                context.append_aggregate(aggregate)
                continue
            if aggregate is not None:
                if aggregate._sketch_cards:
                    aggregate._sketch_cards[-1][1].append(raw)
                aggregate._body.append(raw)
                continue
            if current_group:
                context._group_preambles[current_group].append(raw)
                continue
            if context._module_name:
                context._module_body.append(raw)
                continue
            context._preamble.append(raw)
        for item in model.contexts:
            for child in item.aggregates:
                if isinstance(child, MarkdownAggregate):
                    _take_sketch_cards(child)
                    child.load_root()
        aggregates = {row.name: row for row in _aggregates_in(model)}
        services = {row.name: row for row in _services_in(model)}
        for line in event_lines:
            _wire_event(line, aggregates, services)
        return model

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return _as_sketch(canonical or self)


def _take_sketch_cards(aggregate: MarkdownAggregate) -> None:
    # Model-fidelity entity fences become `####` class cards after the aggregate's map lines.
    found = getattr(aggregate, "_sketch_cards", [])
    if not found:
        return
    written: list[str] = []
    for heading, lines in found:
        for card in card_from_sketch(heading, lines, aggregate.building_block_type):
            written.extend(card.lines())
    aggregate._body = list(aggregate._body) + written


def _as_sketch(model: MarkdownBoundedContextMap) -> str:
    lines: list[str] = []
    for context in model.contexts:
        heading = context.name
        if context.owner:
            heading = f"{context.name} | {context.owner}"
        lines.append(heading)
        for aggregate in context.aggregates:
            lines.append(f"  {aggregate.name}:")
            if isinstance(aggregate, MarkdownAggregate) and aggregate._body:
                lines.extend(aggregate._body)
        lines.append("")
    return "\n".join(lines)
