"""The bounded-context map as a drawing of Clean Engineering modules, shared by every drawn format (draw.io, whiteboard).

A bounded context and an aggregate are modules, so a drawn map is Clean Engineering's modules view: each context a
module, each aggregate a module nested in its context's, listing its members, and each integration a dependency arrow
named by its pattern. At model fidelity the building blocks are classes, so the drawing is Clean Engineering's class
view. Each format's cell classes put these parts in front of that format's own module class; reading a drawing builds
each cell as the cell type the format names for it, and each cell reads itself into the map.
"""

from __future__ import annotations

from cdd_guidance.practices.clean_engineering.model.base_class_model import Module
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContext, MarkdownIntegration
from cdd_guidance.practices.ddd.model.nodes import Aggregate, BoundedContext, BoundedContextMap

# What a drawn map is called on the page it is drawn on.
_TITLE = "Bounded Context Map"


class MapCell:
    """A module on a drawn map that reads itself back into the map: a context or an aggregate."""

    def read_into(self, drawn: BoundedContextMap) -> None:
        raise NotImplementedError(f"{type(self).__name__} must read itself into the map")

    def read_integrations_into(self, drawn: BoundedContextMap) -> None:
        """The arcs this cell's arrows draw, once every cell is on the map; a context draws none of its own."""


class ContextCell(MapCell):
    """A bounded context on a drawn map: a module named by the labels of the contexts that hold it."""

    PURPOSE = "bounded context"

    @classmethod
    def drawing(cls, context: BoundedContext) -> "ContextCell":
        cell = cls(context.module_path, context.sequential_order)
        cell.description = cls.PURPOSE
        return cell

    def read_into(self, drawn: BoundedContextMap) -> None:
        drawn.context_at(self.name.split("/"))


class AggregateCell(MapCell):
    """An aggregate on a drawn map: a module nested in its context's module, listing the members it draws, ten at most,
    so a drawing never cuts a list short and reads its `...` back as a member."""

    PURPOSE = "aggregate"
    seam_bullets = 10

    @classmethod
    def drawing(cls, aggregate: Aggregate) -> "AggregateCell":
        cell = cls(aggregate.module_path, aggregate.sequential_order)
        cell.description = cls.PURPOSE
        cell.seam_terms = aggregate.drawn_members[: cls.seam_bullets]
        return cell

    def depend_on_aggregate(self, target: Aggregate, pattern: str) -> None:
        """An arrow to the aggregate an integration reaches, named by the integration's pattern; one arrow per aggregate,
        named by the first integration, when several of its members are reached."""
        if target.module_path in self.dependencies:
            return
        self.dependencies.append(target.module_path)
        self.dependency_labels[target.module_path] = pattern

    def read_into(self, drawn: BoundedContextMap) -> None:
        drawn.aggregate_at(self.name).take_drawn_root(self.seam_terms)

    def read_integrations_into(self, drawn: BoundedContextMap) -> None:
        source = drawn.aggregate_at(self.name)
        for dependency in self.external_deps():
            integration = MarkdownIntegration.from_aggregate(drawn.aggregate_at(dependency))
            integration.pattern = self.dependency_labels.get(dependency, "")
            source.integrations.append(integration)


class DrawnBoundedContextMap(BoundedContextMap):
    """A map drawn as a Clean Engineering model of some drawn format: its contexts and aggregates are its own modules.
    Each format names its context and aggregate cell types and renders and parses the drawing itself."""

    bounded_context_type = MarkdownBoundedContext
    context_cell_type: type[ContextCell] = ContextCell
    aggregate_cell_type: type[AggregateCell] = AggregateCell

    def __init__(self) -> None:
        super().__init__()
        self.name = _TITLE

    @property
    def modules_title(self) -> str:
        """The drawing's title: the map's own name, as its heading gives it, else the modules view's."""
        return self.title or super().modules_title

    def draw(self, source: BoundedContextMap) -> None:
        """Make source this drawing's modules: the aggregate view when its aggregates hold class cards (model
        fidelity); otherwise the map. The drawing takes the map's own name."""
        self.title = source.title
        if source.has_class_cards:
            source.write_classes(self)
        else:
            self.modules = self._cells(source)

    def _cells(self, source: BoundedContextMap) -> list[Module]:
        """A cell for each context and aggregate on the map, each context before what it holds, in the map's order;
        each integration a dependency of its aggregate's cell on the cell of the aggregate it reaches."""
        contexts = {context: self.context_cell_type.drawing(context) for context in source.every_context}
        aggregates = {aggregate: self.aggregate_cell_type.drawing(aggregate) for aggregate in source.every_aggregate}
        for aggregate, cell in aggregates.items():
            self._draw_integrations(source, aggregate, cell)
        return [cell for context in source.every_context for cell in [contexts[context], *(aggregates[item] for item in context.aggregates)]]

    def _draw_integrations(self, source: BoundedContextMap, aggregate: Aggregate, cell: AggregateCell) -> None:
        for integration in aggregate.integrations:
            target = source.aggregate_reached_by(integration)
            if target is not None and target is not aggregate:
                cell.depend_on_aggregate(target, integration.pattern)

    def read_drawing(self) -> "DrawnBoundedContextMap":
        """Read the modules the drawing parsed into this map, and return it: the class view's classes are the cards of
        the aggregates their modules name; each cell of the modules view reads itself in, then each draws its
        integrations."""
        if any(module.classes for module in self.modules):
            return self.read_class_model(self)
        self.contexts = []
        cells = [module for module in self.modules if isinstance(module, MapCell)]
        for cell in cells:
            cell.read_into(self)
        for cell in cells:
            cell.read_integrations_into(self)
        return self
