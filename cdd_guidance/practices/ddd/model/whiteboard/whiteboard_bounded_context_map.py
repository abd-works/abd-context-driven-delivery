"""Claude Whiteboard channel — the bounded-context map and the aggregate view, drawn and read as Clean Engineering's
whiteboard, as the drawio channel draws them as Clean Engineering's draw.io diagram.

The drawn map (`ddd.model.drawn.drawn_map`) draws the map as Clean Engineering modules; this channel puts its cells in front
of the whiteboard's module: each context a section, each aggregate a module nested in it. Reading a board builds each
module as the cell type its element id names, and each cell reads itself into the map.

The aggregate view nests the same way: each aggregate's classes in a section titled with the aggregate's name, and
each bounded context a larger section round its aggregates' sections, titled with the context's name.
"""

from __future__ import annotations

from harness.whiteboard.whiteboard import Whiteboard

from cdd_guidance.practices.clean_engineering.model.base_class_model import Module
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import module_path_in
from cdd_guidance.practices.clean_engineering.model.whiteboard.whiteboard_class_model import (
    ClassBoard,
    WhiteboardCleanEngineeringModel,
    WhiteboardModule,
)
from cdd_guidance.practices.ddd.model.drawn.drawn_map import MODULES_TITLE_ENDING, AggregateCell, ContextCell, DrawnBoundedContextMap
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap


class WhiteboardContextCell(ContextCell, WhiteboardModule):
    """A bounded context on the map: a section whose id names its role (``context.``)."""

    ROLE = "context"
    TOP_COLOR = "green"


class WhiteboardAggregateCell(AggregateCell, WhiteboardModule):
    """An aggregate on the map: a module nested in its context's section (``aggregate.``)."""

    ROLE = "aggregate"
    NESTED_COLOR = "yellow"


class AggregateViewBoard(ClassBoard):
    """The aggregate view on a board: every aggregate's classes on a page of their own, titled with the aggregate's
    name, and each bounded context a section round its aggregates' pages, titled with the context's name. A class
    model names each aggregate's module by its place, `Revenue | custom · Subscription`, which says both."""

    page_inset = 24
    group_role = "boundedcontext"
    links_across_pages = True

    @property
    def draws_one_page(self) -> bool:
        return False

    def page_groups(self) -> list[tuple[str, list[Module]]]:
        groups: dict[str, list[Module]] = {}
        for module in self.named_modules:
            groups.setdefault(self._context_name(module), []).append(module)
        return list(groups.items())

    def page_title(self, module: Module) -> str:
        return module_path_in(module.name)[-1]

    def _context_name(self, module: Module) -> str:
        """The name of the context that holds the module's aggregate, without its owner; the names of the contexts it
        is nested in come first."""
        return " · ".join(label.partition("|")[0].strip() for label in module_path_in(module.name)[:-1])


class WhiteboardBoundedContextMap(DrawnBoundedContextMap, WhiteboardCleanEngineeringModel):
    """The ``whiteboard`` format: the map as a Clean Engineering board. Its contexts and aggregates are drawn as its
    own modules, which it renders as itself."""

    context_cell_type = WhiteboardContextCell
    aggregate_cell_type = WhiteboardAggregateCell
    module_cell_types = (WhiteboardContextCell, WhiteboardAggregateCell, WhiteboardModule)
    class_board_type = AggregateViewBoard

    def render(self, canonical: BoundedContextMap | None = None, previous: str | None = None) -> str:
        """The aggregate view when the map's aggregates hold class cards (model fidelity); otherwise the map."""
        self.draw(canonical if canonical is not None else self)
        return WhiteboardCleanEngineeringModel.render(self, self, previous)

    def take_board(self, board: Whiteboard) -> "WhiteboardBoundedContextMap":
        """Read the board's modules or classes, and the map's own name from the title it was drawn under; a modules
        view's title names its system instead, and a board of classes is titled for its view, not for the map."""
        super().take_board(board)
        holds_classes = any(module.classes for module in self.modules)
        if not holds_classes and not board.title.rstrip().endswith(MODULES_TITLE_ENDING):
            self.title = board.title.strip()
        return self

    def parse(self, text: str) -> "WhiteboardBoundedContextMap":
        """Read a board into this map, and return it."""
        WhiteboardCleanEngineeringModel.parse(self, text)
        return self.read_drawing()
