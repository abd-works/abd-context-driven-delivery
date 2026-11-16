"""DrawIO channel — the bounded-context map and the aggregate view, drawn and read as Clean Engineering's draw.io diagram.

The drawn map (`ddd.model.drawn.drawn_map`) draws the map as Clean Engineering modules; this channel puts its cells in front
of draw.io's module, whose cell style names its kind. The map is itself the draw.io diagram, so it draws itself;
reading a drawing builds each cell as the cell type its style names, and each cell reads itself into the map.
"""

from __future__ import annotations

import html
from xml.etree import ElementTree as ET

from cdd_guidance.practices.clean_engineering.model.drawio.diagram_node import DrawIOModule
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from cdd_guidance.practices.ddd.model.drawn.drawn_map import AggregateCell, ContextCell, DrawnBoundedContextMap
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap


class DrawIOContextCell(ContextCell, DrawIOModule):
    """A bounded context on the map: a module whose cell style names its kind (`kind=boundedContext;`)."""

    KIND = "boundedContext"


class DrawIOAggregateCell(AggregateCell, DrawIOModule):
    """An aggregate on the map: a module nested in its context's module (`kind=aggregate;`)."""

    KIND = "aggregate"


class DrawIOBoundedContextMap(DrawnBoundedContextMap, DrawIOCleanEngineeringModel):
    """The `drawio` format: the map as a Clean Engineering draw.io diagram. Its contexts and aggregates are drawn as
    its own modules, which it renders as itself."""

    context_cell_type = DrawIOContextCell
    aggregate_cell_type = DrawIOAggregateCell
    module_cell_types = (DrawIOContextCell, DrawIOAggregateCell, DrawIOModule)

    def render(self, canonical: BoundedContextMap | None = None, previous: str | None = None) -> str:
        """The aggregate view when the map's aggregates hold class cards (model fidelity); otherwise the map."""
        del previous
        self.draw(canonical if canonical is not None else self)
        return DrawIOCleanEngineeringModel.render(self, self)

    def _read_title(self, cell: ET.Element) -> None:
        """The map's own name, from the title it was drawn under; a modules view's title names its system instead."""
        super()._read_title(cell)
        if cell.get("id") == "title" and not self.name_from_modules_title(cell):
            self.title = html.unescape(cell.get("value", "")).strip()

    @staticmethod
    def name_from_modules_title(cell: ET.Element) -> bool:
        return html.unescape(cell.get("value", "")).rstrip().endswith("Modules Context")

    def parse(self, text: str) -> "DrawIOBoundedContextMap":
        """Read a drawing into this map, and return it."""
        DrawIOCleanEngineeringModel.parse(self, text)
        return self.read_drawing()
