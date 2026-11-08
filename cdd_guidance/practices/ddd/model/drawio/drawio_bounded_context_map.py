"""DrawIO channel — the bounded-context map and the aggregate view, drawn and read as Clean Engineering's draw.io diagram.

A bounded context and an aggregate are modules, so the map is Clean Engineering's modules view: each context a module,
each aggregate a module nested in its context's, listing its members, and each integration a dependency arrow named by
its pattern. At model fidelity the building blocks are classes, so the aggregate view is Clean Engineering's class view:
the map writes each card into its own modules as one of its classes, kept in the module of its context and aggregate.
The map is itself the draw.io diagram, so it draws itself; reading a drawing builds each cell as the cell type its
style names, and each cell reads itself into the map.
"""

from __future__ import annotations

from cdd_guidance.practices.clean_engineering.model.drawio.diagram_node import DrawIOModule
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContext, MarkdownIntegration
from cdd_guidance.practices.ddd.model.nodes import Aggregate, BoundedContext, BoundedContextMap

_TITLE = "Bounded Context Map"


class DrawIOMapCell(DrawIOModule):
    """A module on the map that reads itself back into the map: a context or an aggregate."""

    def read_into(self, drawn: "DrawIOBoundedContextMap") -> None:
        raise NotImplementedError(f"{type(self).__name__} must read itself into the map")

    def read_integrations_into(self, drawn: "DrawIOBoundedContextMap") -> None:
        """The arcs this cell's arrows draw, once every cell is on the map; a context draws none of its own."""


class DrawIOContextCell(DrawIOMapCell):
    """A bounded context on the map: a module whose purpose line says it is one."""

    KIND = "boundedContext"
    PURPOSE = "bounded context"

    @classmethod
    def drawing(cls, context: BoundedContext) -> "DrawIOContextCell":
        return cls(context.module_path, context.sequential_order, description=cls.PURPOSE)

    def read_into(self, drawn: "DrawIOBoundedContextMap") -> None:
        drawn.context_at(self.name.split("/"))


class DrawIOAggregateCell(DrawIOMapCell):
    """An aggregate on the map: a module nested in its context's module, listing the members it draws, ten at most,
    so a drawing never cuts a list short and reads its `...` back as a member."""

    KIND = "aggregate"
    PURPOSE = "aggregate"
    seam_bullets = 10

    @classmethod
    def drawing(cls, aggregate: Aggregate) -> "DrawIOAggregateCell":
        return cls(
            aggregate.module_path,
            aggregate.sequential_order,
            description=cls.PURPOSE,
            seam_terms=aggregate.drawn_members[: cls.seam_bullets],
        )

    def depend_on_aggregate(self, target: Aggregate, pattern: str) -> None:
        """An arrow to the aggregate an integration reaches, named by the integration's pattern."""
        self.dependencies.append(target.module_path)
        self.dependency_labels[target.module_path] = pattern

    def read_into(self, drawn: "DrawIOBoundedContextMap") -> None:
        drawn.aggregate_at(self.name).take_drawn_root(self.seam_terms)

    def read_integrations_into(self, drawn: "DrawIOBoundedContextMap") -> None:
        source = drawn.aggregate_at(self.name)
        for dependency in self.external_deps():
            target = drawn.aggregate_at(dependency)
            integration = MarkdownIntegration()
            integration.context = target.parent.name
            integration.aggregate = target.name
            integration.target = f"{integration.context} · {integration.aggregate}"
            integration.pattern = self.dependency_labels.get(dependency, "")
            source.integrations.append(integration)


class DrawIOBoundedContextMap(BoundedContextMap, DrawIOCleanEngineeringModel):
    """The `drawio` format: the map as a Clean Engineering draw.io diagram. Its contexts and aggregates are drawn as
    its own modules, which it renders as itself."""

    bounded_context_type = MarkdownBoundedContext
    module_cell_types = (DrawIOContextCell, DrawIOAggregateCell, DrawIOModule)

    def __init__(self) -> None:
        super().__init__()
        self.name = _TITLE

    def render(self, canonical: BoundedContextMap | None = None, previous: str | None = None) -> str:
        """The aggregate view when the map's aggregates hold class cards (model fidelity); otherwise the map."""
        del previous
        source = canonical if canonical is not None else self
        if source.has_class_cards:
            source.write_classes(self)
        else:
            self.modules = self._cells(source)
        return DrawIOCleanEngineeringModel.render(self, self)

    def _cells(self, source: BoundedContextMap) -> list[DrawIOModule]:
        """A cell for each context and aggregate on the map, each context before what it holds, in the map's order;
        each integration a dependency of its aggregate's cell on the cell of the aggregate it reaches."""
        contexts = {context: DrawIOContextCell.drawing(context) for context in source.every_context}
        aggregates = {aggregate: DrawIOAggregateCell.drawing(aggregate) for aggregate in source.every_aggregate}
        for aggregate, cell in aggregates.items():
            for integration in aggregate.integrations:
                target = source.aggregate_reached_by(integration)
                if target is not None and target is not aggregate:
                    cell.depend_on_aggregate(target, integration.pattern)
        return [cell for context in source.every_context for cell in [contexts[context], *(aggregates[item] for item in context.aggregates)]]

    def parse(self, text: str) -> "DrawIOBoundedContextMap":
        """Read a drawing into this map, and return it: the class view's classes are the cards of the aggregates
        their modules name; each cell of the modules view reads itself in, then each draws its integrations."""
        DrawIOCleanEngineeringModel.parse(self, text)
        if any(module.classes for module in self.modules):
            return self.read_class_model(self)
        self.contexts = []
        cells = [module for module in self.modules if isinstance(module, DrawIOMapCell)]
        for cell in cells:
            cell.read_into(self)
        for cell in cells:
            cell.read_integrations_into(self)
        return self
