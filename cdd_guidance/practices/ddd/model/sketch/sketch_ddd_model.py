"""Sketch channel — the `domain driven design:` section of a sketch, read into and written from the bounded-context map.

The map reads the section's own lines: where each context starts, the prose sections it skips, and the event map.
Each context reads and writes its own lines, and each aggregate and card its own fence."""

from __future__ import annotations

from cdd_guidance.actions.sketch.sketch_outline import SketchOutline
from harness.guidance.guidance import SketchLens
from cdd_guidance.practices.ddd.model.markdown.nodes import (
    BUILD_ORDER,
    SKETCH_CONTEXT,
    SKETCH_INDENT,
    MarkdownAggregate,
    MarkdownBoundedContext,
    fenced,
    sketch_level,
)
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap

_SECTION = "## domain driven design:"
# The headings that open the DDD section of a sketch; the DDD practice declares them from here.
_LENS = SketchLens(("ddd:", "domain driven design:"))
_EVENT_MAP = "event_map:"
_EVENT_HEADINGS = {"event_map:", "event map:", "event_map", "event map"}
_PROSE_HEADINGS = (
    "false cognates to carry forward",
    "false cognates",
    "open questions",
    "settled",
)
_META_PREFIXES = ("fidelity:", "partition:")


def _is_context_heading(stripped: str) -> bool:
    if "|" not in stripped:
        return False
    lower = stripped.lower()
    return not any(lower.startswith(prefix) for prefix in _META_PREFIXES)


def _is_prose_heading(stripped: str) -> bool:
    lower = stripped.rstrip(":").strip().lower()
    if lower in _PROSE_HEADINGS or lower.startswith("false cognates"):
        return True
    return lower.startswith(BUILD_ORDER)


class SketchDddModel(BoundedContextMap):
    """The `sketch` format: the map as the DDD section of a sketch. Its contexts and aggregates read and write their
    own sketch lines."""

    lens = _LENS
    """The section of a sketch DDD writes, opened by its `ddd:` or `domain driven design:` heading."""
    bounded_context_type = MarkdownBoundedContext
    aggregate_type = MarkdownAggregate

    def parse(self, text: str) -> "SketchDddModel":
        """Read the ddd section of a sketch, flattened to indentation, into this map, and return it: each context the
        section opens reads the lines under it, and the event map is wired once every aggregate has its root."""
        self.contexts = []
        sections: list[tuple[MarkdownBoundedContext, list[str]]] = []
        events: list[str] = []
        lines: list[str] | None = None
        in_events = False
        in_meta = True
        for raw in SketchOutline(text, SKETCH_INDENT).body_for(self.lens).splitlines():
            stripped = raw.strip()
            lowered = stripped.lower()
            if not stripped or stripped.startswith(("#", "---")):
                continue
            if lowered.startswith(f"{BUILD_ORDER}:"):
                lines = None
                continue
            if lowered in _EVENT_HEADINGS:
                in_events = True
                continue
            if in_events and stripped.startswith("- ") and ":" in stripped:
                events.append(stripped[2:].split("//", 1)[0].strip())
                continue
            in_events = False
            if in_meta and lowered.startswith(_META_PREFIXES):
                continue
            if sketch_level(raw) > 0:
                if lines is not None:
                    lines.append(raw)
            elif _is_context_heading(stripped):
                in_meta = False
                lines = []
                sections.append((self._open_context(stripped), lines))
            elif _is_prose_heading(stripped):
                lines = None
        for context, context_lines in sections:
            context.read_sketch_lines(context_lines)
        self.wire_events(events)
        return self

    def render(self, canonical: BoundedContextMap | None = None, previous: str | None = None) -> str:
        del previous
        model = canonical or self
        written = [_SECTION, ""]
        for context in model.contexts:
            written.extend(context.sketch_lines())
        entries = [
            f"- {event.name}: emitted by {aggregate.name}; consumed by {', '.join(item.name for item in event.consumers)}"
            for aggregate in model.every_aggregate
            for event in aggregate.events
        ]
        if entries:
            written.extend([f"{SKETCH_CONTEXT}{_EVENT_MAP}", ""] + fenced(entries))
        return "\n".join(written)

    def _open_context(self, stripped: str) -> MarkdownBoundedContext:
        name, _, owner = stripped.rstrip(":").partition("|")
        context = self.bounded_context_type(name.strip(), len(self.contexts) + 1)
        context.owner = owner.strip()
        self.append_context(context)
        return context
