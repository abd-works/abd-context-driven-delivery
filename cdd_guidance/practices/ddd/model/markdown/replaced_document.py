"""The markdown document a render writes over, which keeps the words a drawing does not hold.

A drawn bounded-context map or domain model holds the contexts, the aggregates, their members and classes, and an arrow
for each integration and each call to another aggregate. It holds none of the document's prose: the sentence under a
heading, a note, an invariant, the fields of an integration, the events, a call inside an aggregate. The Render action
hands the markdown adapter the file as it is before the render (`RenderedFile.previous`), and the adapter asks that
file, read as the map it was, to give those words to everything still on the map under the same name. What the drawing
does hold is the drawing's: a context, a class, a member or an arrow removed from it stays removed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap, Integration

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.model import Operation
    from cdd_guidance.practices.ddd.model.markdown.class_cards import ClassCard
    from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownAggregate, MarkdownBoundedContext


class ReplacedDocument:
    """The markdown file a render replaces, read as the map it was, and the map a drawing was read into, which takes
    the replaced file's words."""

    def __init__(self, replaced: BoundedContextMap, read: BoundedContextMap) -> None:
        self._replaced = replaced
        self._read = read

    def give_its_words(self) -> None:
        """Give the map read from the drawing what the replaced file writes round its title, and each context still on
        it the words of the context of the same name."""
        read, replaced = self._read, self._replaced
        read.title = read.title or replaced.title
        read.opening = read.opening or list(replaced.opening)
        read.description = read.description or list(replaced.description)
        was_named = {context.name: context for context in replaced.every_context}
        for context in read.every_context:
            if context.name in was_named:
                self._give_context(was_named[context.name], context)

    def _give_context(self, was: MarkdownBoundedContext, context: MarkdownBoundedContext) -> None:
        """The context's sentence, notes, module, and group notes, then each of its aggregates' words."""
        context.description = context.description or was.description
        context.notes = context.notes or list(was.notes)
        context.module_name = context.module_name or was.module_name
        context.module_notes = context.module_notes or list(was.module_notes)
        context.group_notes = context.group_notes or dict(was.group_notes)
        was_named = {aggregate.name: aggregate for aggregate in was.aggregates}
        for aggregate in context.aggregates:
            if aggregate.name in was_named:
                _ReplacedAggregate(self, was_named[aggregate.name], aggregate).give_its_words()

    def same_target(self, was: Integration, drawn: Integration) -> bool:
        """Whether an integration the replaced file writes is the one an arrow of the drawing was read as: both reach
        the same aggregate, and the same class of it when the arrow names one."""
        reached, arrow_reaches = self._replaced.aggregate_reached_by(was), self._read.aggregate_reached_by(drawn)
        if reached is None or arrow_reaches is None:
            return False
        same_aggregate = (reached.parent.name, reached.name) == (arrow_reaches.parent.name, arrow_reaches.name)
        return same_aggregate and (not drawn.entity or not was.entity or drawn.entity == was.entity)

    def draws_no_arrow(self, was: Integration) -> bool:
        """Whether an integration the replaced file writes reaches no aggregate on the map, so no drawing shows it."""
        return self._replaced.aggregate_reached_by(was) is None


class _ReplacedAggregate:
    """One aggregate of the replaced file and the aggregate of the same name read from the drawing."""

    def __init__(self, document: ReplacedDocument, was: MarkdownAggregate, aggregate: MarkdownAggregate) -> None:
        self._document = document
        self._was = was
        self._aggregate = aggregate

    def give_its_words(self) -> None:
        was, aggregate = self._was, self._aggregate
        aggregate.description = aggregate.description or was.description
        aggregate.group = aggregate.group or was.group
        aggregate.consumed_events = aggregate.consumed_events or list(was.consumed_events)
        aggregate.integrations = self._integrations()
        self._give_root()
        was_named = {card.name: card for card in was.classes}
        local = {card.name for card in aggregate.classes}
        for card in aggregate.classes:
            if card.name in was_named:
                _ReplacedCard(was_named[card.name], card, local).give_its_words()

    def _integrations(self) -> list[Integration]:
        """Each arrow read from the drawing as the integrations the replaced file writes to the same target, with every
        field, under the pattern the arrow is labelled with now; an arrow the file has no integration for as it was
        read; then the file's integrations no drawing shows an arrow for."""
        kept: list[Integration] = []
        for drawn in self._aggregate.integrations:
            written = [item for item in self._was.integrations if self._document.same_target(item, drawn) and item not in kept]
            for item in written[:1]:
                item.pattern = drawn.pattern or item.pattern
            kept.extend(written or [drawn])
        return kept + [item for item in self._was.integrations if self._document.draws_no_arrow(item)]

    def _give_root(self) -> None:
        """A root listed under its aggregate, as the bounded-context map writes it, takes what the file says the root
        is, its operations, the events it emits, and each member's line as the file writes it."""
        was_root, root = self._was.root, self._aggregate.root
        if was_root is None or root is None or self._aggregate.classes:
            return
        root.intent = root.intent or was_root.intent
        root.operations = root.operations or list(was_root.operations)
        if not self._aggregate.events:
            root.properties.extend(self._was.events)
        written = {self._drawn_name(member.name): member.name for member in was_root.invariant_objects}
        for member in root.invariant_objects:
            member.name = written.get(self._drawn_name(member.name), member.name)

    def _drawn_name(self, line: str) -> str:
        """A member's name as a drawing lists it: without what its line says after ` - `."""
        return line.split(" - ", 1)[0].strip().lower()


class _ReplacedCard:
    """One class card of the replaced file and the card of the same name read from the drawing, in an aggregate whose
    classes are local."""

    def __init__(self, was: ClassCard, card: ClassCard, local: set[str]) -> None:
        self._was = was
        self._card = card
        self._local = local

    def give_its_words(self) -> None:
        """The card's invariants and intent, where the file writes its repository, each property's note and the
        relationship a drawing shows no arrow for, and each operation's note and calls."""
        was, card = self._was, self._card
        card.invariants = card.invariants or list(was.invariants)
        card.intent = card.intent or was.intent
        card.drawn_in_root = was.drawn_in_root
        was_properties = {item.name: item for item in was.plain_properties}
        for prop in card.plain_properties:
            written = was_properties.get(prop.name)
            if written is not None:
                prop.description = prop.description or written.description
                if written.type_hint == prop.type_hint and not prop.stereotype:
                    prop.stereotype = written.stereotype
        was_operations = {item.name: item for item in was.operations}
        for operation in card.operations:
            if operation.name in was_operations:
                self._give_operation(was_operations[operation.name], operation)

    def _give_operation(self, was: Operation, operation: Operation) -> None:
        """The operation's note, and its calls as the file writes them: every call inside the aggregate, which no arrow
        shows, each call to another aggregate whose arrow is still drawn, then each arrow the file has no call for."""
        operation.description = operation.description or was.description
        arrows = {self._called_class(callee) for callee in operation.callees}
        kept = [callee for callee in was.callees if self._is_local(callee) or self._called_class(callee) in arrows]
        written = {self._called_class(callee) for callee in kept}
        operation.callees = kept + [callee for callee in operation.callees if self._called_class(callee) not in written]

    def _is_local(self, callee: str) -> bool:
        named = self._called_class(callee)
        return not named or named in self._local

    def _called_class(self, callee: str) -> str:
        """The class a call names before its operation: `BookRepository` of `BookRepository.load(bookId)`; none for a
        call that names only an operation."""
        named = callee.strip().partition(".")[0].partition("(")[0].strip()
        return named if named[:1].isupper() else ""
