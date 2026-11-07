"""DrawIO channel — the bounded-context map and the aggregate view, drawn and read by Clean Engineering's draw.io diagram.

A bounded context and an aggregate are modules, so the map is Clean Engineering's modules view: each context a module,
each aggregate a module nested in its context's, listing its members, and each integration a dependency arrow named by
its pattern. At model fidelity the building blocks are classes, so the aggregate view is Clean Engineering's class view
of the map's class model: each card a class with its stereotypes, kept in the module of its context and aggregate.
"""

from __future__ import annotations

from cdd_guidance.practices.clean_engineering.model.drawio.diagram_node import DrawIOModule
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from cdd_guidance.practices.ddd.model.markdown.nodes import (
    MarkdownAggregate,
    MarkdownBoundedContextMap,
    MarkdownIntegration,
)
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap

# The purpose line of each module on the map, which says whether the module is a bounded context or an aggregate.
CONTEXT_PURPOSE = "bounded context"
AGGREGATE_PURPOSE = "aggregate"
_TITLE = "Bounded Context Map"


class DrawIOBoundedContextMap(MarkdownBoundedContextMap):
    """The `drawio` format: a map written and read through the Clean Engineering draw.io diagram it holds."""

    def __init__(self) -> None:
        super().__init__()
        self.diagram = DrawIOCleanEngineeringModel(_TITLE)

    @property
    def holds_classes_only(self) -> bool:
        """A drawing is always a map."""
        return False

    def render(self, canonical: BoundedContextMap | None = None, previous: str | None = None) -> str:
        """The aggregate view when the map's aggregates hold class cards (model fidelity); otherwise the map."""
        del previous
        source = canonical if canonical is not None else self
        self.diagram.modules = []
        if source.has_class_cards:
            return self.diagram.render(source.class_model())
        self.diagram.modules = self._cells(source)
        return self.diagram.render(self.diagram)

    def _cells(self, source: BoundedContextMap) -> list[DrawIOModule]:
        """A module for each context and aggregate on the map, each context before what it holds, in the map's order;
        each integration a dependency of its aggregate's module on the module of the aggregate it reaches."""
        cells: dict[object, DrawIOModule] = {}
        for context in source.every_context:
            cells[context] = DrawIOModule(context.module_path, context.sequential_order, description=CONTEXT_PURPOSE)
            for aggregate in context.aggregates:
                cells[aggregate] = DrawIOAggregateCell(
                    aggregate.module_path,
                    aggregate.sequential_order,
                    description=AGGREGATE_PURPOSE,
                    seam_terms=aggregate.drawn_members,
                )
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
            self._read_module(module)
        for module in self.diagram.modules:
            self._read_integrations(module)
        return self

    def _read_module(self, module: DrawIOModule) -> None:
        labels = module.name.split("/")
        if module.description == CONTEXT_PURPOSE:
            self._context_at(labels)
        elif module.description == AGGREGATE_PURPOSE:
            self._context_at(labels[:-1]).aggregate_named(labels[-1]).take_drawn_root(module.seam_terms)

    def _read_integrations(self, module: DrawIOModule) -> None:
        if module.description != AGGREGATE_PURPOSE:
            return
        source = self._aggregate_at(module.name)
        for dependency in module.external_deps():
            target = self._aggregate_at(dependency)
            integration = MarkdownIntegration()
            integration.context = target.parent.name
            integration.aggregate = target.name
            integration.target = f"{integration.context} · {integration.aggregate}"
            integration.pattern = module.dependency_labels.get(dependency, "")
            source.integrations.append(integration)

    def _aggregate_at(self, path: str) -> MarkdownAggregate:
        labels = path.split("/")
        return self._context_at(labels[:-1]).aggregate_named(labels[-1])


class DrawIOAggregateCell(DrawIOModule):
    """An aggregate on the map: a module nested in its context's module, listing every member the aggregate draws."""

    seam_bullets = 10

