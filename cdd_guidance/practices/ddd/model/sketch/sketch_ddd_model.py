"""Sketch channel — the `domain driven design:` section of a sketch, read into and written from the bounded-context map.

The map reads the section's own lines: where each context starts, the prose sections it skips, and the event map.
Each context reads and writes its own lines, and each aggregate and card its own fence."""

from __future__ import annotations

from cdd_guidance.practices.sketch_document.sketch_outline import SketchOutline
from harness.guidance.guidance import SketchLens
from cdd_guidance.practices.ddd.model.sketch.sketch_nodes import (
    BUILD_ORDER,
    SKETCH_CONTEXT,
    SKETCH_INDENT,
    SketchBoundedContext,
    SketchedContext,
    fenced,
    sketch_level,
)
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap
from harness.guidance.practice_formats import Written

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


class SketchDddModel(BoundedContextMap):
    """The `sketch` format: the map as the DDD section of a sketch. Its contexts and aggregates read and write their
    own sketch lines."""

    lens = _LENS
    """The section of a sketch DDD writes, opened by its `ddd:` or `domain driven design:` heading."""
    bounded_context_type = SketchBoundedContext


    def parse(self, text: str, file: str = "") -> "SketchDddModel":
        """Read the ddd section of a sketch, flattened to indentation, into this map, and return it: each context the
        section opens reads the lines under it, and the event map is wired once every aggregate has its root."""
        self.contexts = []
        section = _SectionReading(self)
        for raw in SketchOutline(text, SKETCH_INDENT).body_for(self.lens).splitlines():
            section.read_line(raw)
        for context, context_lines in section.contexts:
            context.read_sketch_lines(context_lines)
        self.wire_events(section.events)
        return self

    def render(self, canonical: BoundedContextMap, written: Written = Written()) -> str:
        """canonical as the ddd section of a sketch; a sketch keeps no previous text."""
        lines = [_SECTION, ""]
        for context in canonical.contexts:
            lines.extend(SketchedContext(context).lines())
        entries = [f"- {event.map_entry()}" for aggregate in canonical.every_aggregate for event in aggregate.events]
        if entries:
            lines.extend([f"{SKETCH_CONTEXT}{_EVENT_MAP}", ""] + fenced(entries))
        return "\n".join(lines)


    def open_context(self, stripped: str) -> SketchBoundedContext:
        """The context a `Name | owner` heading opens, added to the map."""
        name, _, owner = stripped.rstrip(":").partition("|")
        context = self.bounded_context_type(name.strip(), len(self.contexts) + 1)
        context.owner = owner.strip()
        self.append_context(context)
        return context


class _SectionReading:
    """One read of the DDD section of a sketch, line by line: the lines under each context heading, which the context
    reads once every heading is found, and the entries of the event map. Build order, meta lines before the first
    context, and prose sections are skipped."""

    def __init__(self, sketch: SketchDddModel) -> None:
        self._sketch = sketch
        self.contexts: list[tuple[SketchBoundedContext, list[str]]] = []
        self.events: list[str] = []
        # The lines of the context being read; none while a section is being skipped.
        self._lines: list[str] | None = None
        self._in_events = False
        self._in_meta = True

    def read_line(self, raw: str) -> None:
        stripped = raw.strip()
        lowered = stripped.lower()
        if not stripped or stripped.startswith(("#", "---")):
            return
        if lowered.startswith(f"{BUILD_ORDER}:"):
            self._lines = None
        elif lowered in _EVENT_HEADINGS:
            self._in_events = True
        elif self._in_events and stripped.startswith("- ") and ":" in stripped:
            self.events.append(stripped[2:].split("//", 1)[0].strip())
        else:
            self._in_events = False
            self._read_outline_line(raw, stripped)

    def _read_outline_line(self, raw: str, stripped: str) -> None:
        """A line that is neither build order nor the event map: a meta line, a line under a context, a context heading,
        or a prose heading."""
        if self._in_meta and stripped.lower().startswith(_META_PREFIXES):
            return
        if sketch_level(raw) > 0:
            if self._lines is not None:
                self._lines.append(raw)
        elif self._is_context_heading(stripped):
            self._in_meta = False
            self._lines = []
            self.contexts.append((self._sketch.open_context(stripped), self._lines))
        elif self._is_prose_heading(stripped):
            self._lines = None

    def _is_context_heading(self, stripped: str) -> bool:
        return "|" in stripped and not stripped.lower().startswith(_META_PREFIXES)

    def _is_prose_heading(self, stripped: str) -> bool:
        lower = stripped.rstrip(":").strip().lower()
        return lower in _PROSE_HEADINGS or lower.startswith("false cognates") or lower.startswith(BUILD_ORDER)
