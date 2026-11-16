"""Claude Whiteboard channel — the bounded-context map and the aggregate view, drawn and read as Clean Engineering's
whiteboard, as the drawio channel draws them as Clean Engineering's draw.io diagram.

The drawn map (`ddd.model.drawn_map`) draws the map as Clean Engineering modules; this channel puts its cells in front
of the whiteboard's module: each context a section, each aggregate a module nested in it. Reading a board builds each
module as the cell type its element id names, and each cell reads itself into the map.
"""

from __future__ import annotations

from cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model import (
    WhiteboardCleanEngineeringModel,
    WhiteboardModule,
)
from cdd_guidance.practices.ddd.model.drawn_map import AggregateCell, ContextCell, DrawnBoundedContextMap
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap

_TITLE = "Bounded Context Map"


class WhiteboardContextCell(ContextCell, WhiteboardModule):
    """A bounded context on the map: a section whose id names its role (``context.``)."""

    ROLE = "context"
    TOP_COLOR = "green"


class WhiteboardAggregateCell(AggregateCell, WhiteboardModule):
    """An aggregate on the map: a module nested in its context's section (``aggregate.``)."""

    ROLE = "aggregate"
    NESTED_COLOR = "yellow"


class WhiteboardBoundedContextMap(DrawnBoundedContextMap, WhiteboardCleanEngineeringModel):
    """The ``whiteboard`` format: the map as a Clean Engineering board. Its contexts and aggregates are drawn as its
    own modules, which it renders as itself."""

    context_cell_type = WhiteboardContextCell
    aggregate_cell_type = WhiteboardAggregateCell
    module_cell_types = (WhiteboardContextCell, WhiteboardAggregateCell, WhiteboardModule)

    def __init__(self) -> None:
        super().__init__()
        self.name = _TITLE

    def render(self, canonical: BoundedContextMap | None = None, previous: str | None = None) -> str:
        """The aggregate view when the map's aggregates hold class cards (model fidelity); otherwise the map."""
        self.draw(canonical if canonical is not None else self)
        return WhiteboardCleanEngineeringModel.render(self, self, previous)

    def parse(self, text: str) -> "WhiteboardBoundedContextMap":
        """Read a board into this map, and return it."""
        WhiteboardCleanEngineeringModel.parse(self, text)
        return self.read_drawing()
