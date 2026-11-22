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
        context.take_words_from(was)
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
        """The aggregate's own words, its root's and its cards' (``MarkdownAggregate.take_words_from``), then the
        integrations the replaced file writes to the targets its arrows still reach."""
        self._aggregate.take_words_from(self._was)
        self._aggregate.integrations = self._integrations()

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
