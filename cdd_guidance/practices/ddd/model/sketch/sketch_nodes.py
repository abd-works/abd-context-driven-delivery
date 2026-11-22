"""The `domain driven design:` section of a sketch, flattened to indentation, as the map's contexts and aggregates read
and write it: a context is `### Name | owner`, the heading that holds aggregates `#### group` or `#### module/`, and an
entity `##### Name`, each with a fence below. A context and an aggregate read from a sketch are markdown's, so a map
read from a sketch writes as markdown too; a map of any format is written as a sketch through *SketchedContext*."""

from __future__ import annotations

from cdd_guidance.practices.clean_engineering.model import marks_in, without_marks
from cdd_guidance.practices.ddd.model.markdown.class_cards import MarkdownBuildingBlock
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownAggregate, MarkdownBoundedContext
from cdd_guidance.practices.ddd.model.stereotypes import kind_named_by, plain_class_name

SKETCH_INDENT = 2
SKETCH_CONTEXT = "### "
_SKETCH_HOLDER = "#### "
_SKETCH_ENTITY = "##### "
_FENCE = "```"
_SKETCH_NOTE = "note:"
BUILD_ORDER = "build order"
# Lines at entity depth that are aggregate notes, not entities.
_NOT_ENTITIES = ("entry:", _SKETCH_NOTE, BUILD_ORDER, "seam:", "constraint:", "//")


def sketch_level(raw: str) -> int:
    """How deep a flattened sketch line sits: 0 for a context heading, 1 for a holder, 2 for an entity."""
    return (len(raw) - len(raw.lstrip(" "))) // SKETCH_INDENT


def fenced(lines: list[str]) -> list[str]:
    """The lines with text in a sketch fence, then a blank line; nothing when no line has text."""
    kept = [line for line in lines if line.strip()]
    return [_FENCE, *kept, _FENCE, ""] if kept else []


class SketchAggregate(MarkdownAggregate):
    """An aggregate read from a sketch: the entity fences listed under it, read into cards once the section is read."""

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        # The entity fences a sketch lists under this aggregate: each card's heading and the lines of its fence.
        self.sketch_fences: list[tuple[str, list[str]]] = []

    def take_sketch_line(self, raw: str) -> None:
        """One sketch line under this aggregate's entity: its own line, and a line of the fence it is in."""
        if self.sketch_fences:
            self.sketch_fences[-1][1].append(raw)
        self.source_lines.append(raw)

    def load_sketch(self) -> None:
        """Read the sketch's fences into cards, then the root from this aggregate's lines and its root card."""
        self.classes = [card for heading, lines in self.sketch_fences for card in MarkdownBuildingBlock.from_sketch(heading, lines)]
        self.load_root()


class SketchBoundedContext(MarkdownBoundedContext):
    """A bounded context read from a sketch: the holders that group its aggregates or name its module, and each entity
    that opens an aggregate or joins the one its root opened."""

    aggregate_type = SketchAggregate

    def __init__(self, name: str = "", sequential_order: int = 0, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        # The sketch headings an aggregate is already named after, so the next entity under one is named after itself.
        self._used_holders: set[str] = set()

    def read_sketch_lines(self, lines: list[str]) -> None:
        """Read this context's lines of a sketch: the holders that group its aggregates or name its module, each
        entity that opens an aggregate or joins the one its root opened, and the notes and fences under them."""
        aggregate: SketchAggregate | None = None
        group: str | None = None
        for raw in lines:
            stripped = raw.strip()
            level = sketch_level(raw)
            if level == 1:
                aggregate, group = None, self._read_sketch_holder(stripped)
                continue
            if level == 2 and self._is_entity_heading(stripped):
                aggregate = self._open_sketch_entity(stripped.split("//", 1)[0].strip().rstrip(":"), aggregate, group)
                continue
            if aggregate is not None:
                aggregate.take_sketch_line(raw)
                continue
            self._keep_note(stripped, group)
        for item in self.aggregates:
            item.load_sketch()

    def _is_entity_heading(self, stripped: str) -> bool:
        """A sketch line at entity depth names an entity, unless it is an aggregate note."""
        name = stripped.split("//", 1)[0].strip().rstrip(":")
        if not name or name.startswith("- ") or name.lower().startswith(_NOT_ENTITIES):
            return False
        return ":" not in name

    def _read_sketch_holder(self, stripped: str) -> str | None:
        """A holder line: a note, the module the context is built as, or a heading that groups aggregates, which
        is the group in force after it."""
        if stripped.lower().startswith(_SKETCH_NOTE):
            self.notes.append(stripped)
            return None
        if stripped.rstrip(":").strip().endswith("/"):
            self.module_name = stripped.rstrip(":").strip().rstrip("/").strip()
            self.module_notes = []
            return None
        group = without_marks(stripped.rstrip(":"))
        self.group_notes.setdefault(group, [])
        return group

    def _open_sketch_entity(self, name: str, current: SketchAggregate | None, group: str | None) -> SketchAggregate:
        """The aggregate an entity heading belongs to: a member card joins the aggregate its root opened; any other
        entity opens one, named after the heading it sits under the first time, else after itself."""
        marks = marks_in(name)
        if marks and kind_named_by(marks) != "EntityRoot" and current is not None and current.sketch_fences:
            current.sketch_fences.append((name, []))
            return current
        aggregate_name = name
        if marks:
            holder = group or self.module_name
            aggregate_name = holder if holder and holder not in self._used_holders else plain_class_name(name)
            self._used_holders.add(holder)
        aggregate = self.aggregate_type(aggregate_name, len(self.aggregates) + 1)
        aggregate.sketch_fences = [(name, [])] if marks else []
        aggregate.group = group
        self.append_aggregate(aggregate)
        return aggregate


class SketchedAggregate:
    """An aggregate of any format as a sketch writes it: its entity and fence, or each card's heading and fence, its
    arcs on the root."""

    def __init__(self, aggregate: MarkdownAggregate) -> None:
        self._aggregate = aggregate

    @property
    def holder(self) -> str | None:
        """The heading a sketch lists this aggregate under: its own name when its root card is named apart, else
        its group."""
        aggregate = self._aggregate
        root = aggregate.root_card
        return aggregate.name if root is not None and root.name != aggregate.name else aggregate.group

    def lines(self) -> list[str]:
        aggregate = self._aggregate
        if not aggregate.classes:
            root = aggregate.root
            members = [item.name for item in root.operations] + [item.name for item in root.invariant_objects] if root is not None else []
            return [f"{_SKETCH_ENTITY}{aggregate.name}", ""] + fenced(members + aggregate.integration_lines())
        written: list[str] = []
        for card in aggregate.ordered_cards:
            arcs = aggregate.integration_lines() if card is aggregate.root_card else []
            written.extend([f"{_SKETCH_ENTITY}{card.heading}", ""] + fenced(card.sketch_lines() + arcs))
        return written


class SketchedContext:
    """A bounded context of any format as a sketch writes it: its heading, its notes, its module, then each aggregate
    under its holder."""

    def __init__(self, context: MarkdownBoundedContext) -> None:
        self._context = context

    def lines(self) -> list[str]:
        context = self._context
        notes = [note if note.lower().startswith(_SKETCH_NOTE) else f"{_SKETCH_NOTE} {note}" for note in context.notes]
        written = [f"{SKETCH_CONTEXT}{context.name} | {context.owner or ''}", ""] + fenced(notes)
        if context.module_name:
            written.extend([f"{_SKETCH_HOLDER}{context.module_name}/", ""] + fenced(context.module_notes))
        group: str | None = None
        for aggregate in (SketchedAggregate(item) for item in context.aggregates):
            holder = aggregate.holder
            if holder and holder != group:
                written.extend([f"{_SKETCH_HOLDER}{holder}", ""] + fenced(context.group_notes.get(holder, [])))
                group = holder
            written.extend(aggregate.lines())
        return written
