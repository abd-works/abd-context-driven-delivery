"""DrawIO channel — the bounded-context map and the aggregate view, drawn and read by Clean Engineering's draw.io diagram.

A bounded context and an aggregate are modules, so the map is Clean Engineering's modules view: each context a module,
each aggregate a module nested in its context's, listing its members, and each integration a dependency arrow named by
its pattern. At model fidelity the building blocks are classes, so the aggregate view is Clean Engineering's class view:
the map writes each card into the diagram as one of its classes, kept in the module of its context and aggregate.
"""

from __future__ import annotations

from cdd_guidance.practices.clean_engineering.model.drawio.diagram_node import DrawIOModule
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from cdd_guidance.practices.ddd.model.markdown.nodes import (
    MarkdownAggregate,
    MarkdownBoundedContext,
    MarkdownIntegration,
)
from cdd_guidance.practices.ddd.model.nodes import Aggregate, BoundedContext, BoundedContextMap

_TITLE = "Bounded Context Map"


class DrawIOContextCell(DrawIOModule):
    """A bounded context on the map: a module whose purpose line says it is one."""

    PURPOSE = "bounded context"

    def __init__(self, context: BoundedContext) -> None:
        super().__init__(context.module_path, context.sequential_order, description=self.PURPOSE)


class DrawIOAggregateCell(DrawIOModule):
    """An aggregate on the map: a module nested in its context's module, listing the members it draws, ten at most,
    so a drawing never cuts a list short and reads its `...` back as a member."""

    PURPOSE = "aggregate"
    seam_bullets = 10

    def __init__(self, aggregate: Aggregate) -> None:
        super().__init__(
            aggregate.module_path,
            aggregate.sequential_order,
            description=self.PURPOSE,
            seam_terms=aggregate.drawn_members[: self.seam_bullets],
        )


class DrawIOBoundedContextMap(BoundedContextMap):
    """The `drawio` format: a map written and read through the Clean Engineering draw.io diagram it holds, which is
    the map's drawing."""

    bounded_context_type = MarkdownBoundedContext
    aggregate_type = MarkdownAggregate

    def __init__(self) -> None:
        super().__init__()
        self.diagram = DrawIOCleanEngineeringModel(_TITLE)
        # How a module drawn with each cell's purpose line reads back.
        self._readers = {DrawIOContextCell.PURPOSE: self._read_context, DrawIOAggregateCell.PURPOSE: self._read_aggregate}

    def render(self, canonical: BoundedContextMap | None = None, previous: str | None = None) -> str:
        """The aggregate view when the map's aggregates hold class cards (model fidelity); otherwise the map."""
        del previous
        source = canonical if canonical is not None else self
        if source.has_class_cards:
            source.write_classes(self.diagram)
        else:
            self.diagram.modules = self._cells(source)
        return self.diagram.render(self.diagram)

    def _cells(self, source: BoundedContextMap) -> list[DrawIOModule]:
        """A cell for each context and aggregate on the map, each context before what it holds, in the map's order;
        each integration a dependency of its aggregate's cell on the cell of the aggregate it reaches."""
        cells: dict[object, DrawIOModule] = {}
        for context in source.every_context:
            cells[context] = DrawIOContextCell(context)
            for aggregate in context.aggregates:
                cells[aggregate] = DrawIOAggregateCell(aggregate)
        for aggregate in source.every_aggregate:
            for integration in aggregate.integrations:
                target = source.aggregate_reached_by(integration)
                if target is not None and target is not aggregate:
                    cells[aggregate].dependencies.append(target.module_path)
                    cells[aggregate].dependency_labels[target.module_path] = integration.pattern
        return list(cells.values())

    def parse(self, text: str) -> "DrawIOBoundedContextMap":
        """Read a drawing into this map, and return it: the class view's classes are the cards of the aggregates
        their modules name; the modules view's modules are the contexts and aggregates."""
        self.diagram.parse(text)
        if any(module.classes for module in self.diagram.modules):
            return self.read_class_model(self.diagram)
        self.contexts = []
        for module in self.diagram.modules:
            self._readers.get(module.description, self._read_nothing)(module)
        for module in self.diagram.modules:
            if module.description == DrawIOAggregateCell.PURPOSE:
                self._read_integrations(module)
        return self

    def _read_context(self, module: DrawIOModule) -> None:
        self.context_at(module.name.split("/"))

    def _read_aggregate(self, module: DrawIOModule) -> None:
        self.aggregate_at(module.name).take_drawn_root(module.seam_terms)

    def _read_nothing(self, module: DrawIOModule) -> None:
        """A module drawn with no cell's purpose line is not on the map."""

    def _read_integrations(self, module: DrawIOModule) -> None:
        source = self.aggregate_at(module.name)
        for dependency in module.external_deps():
            target = self.aggregate_at(dependency)
            integration = MarkdownIntegration()
            integration.context = target.parent.name
            integration.aggregate = target.name
            integration.target = f"{integration.context} · {integration.aggregate}"
            integration.pattern = module.dependency_labels.get(dependency, "")
            source.integrations.append(integration)
