"""DrawIO channel — the bounded-context map and the aggregate view, drawn and read as Clean Engineering's draw.io diagram.

The drawn map (`ddd.model.drawn.drawn_map`) draws the map as Clean Engineering modules; this channel puts its cells in front
of draw.io's module, whose cell style names its kind. The map is itself the draw.io diagram, so it draws itself;
reading a drawing builds each cell as the cell type its style names, and each cell reads itself into the map.

The aggregate view (model fidelity) is one page of class cards laid out as the model fidelity lays an aggregate out:
each aggregate a container titled with its name, holding its root, whose card carries the repository below the root's
operations, and the entities and values it owns; each bounded context a larger container round its aggregates', titled
with the context's name and owner. The containers lie behind the cards on the page itself, so every card keeps its
place on the page, and reads back by the module its style names, whatever container it is drawn in.
"""

from __future__ import annotations

import html
from typing import Dict, Iterable, List, Tuple
from xml.etree import ElementTree as ET

from harness.drawio import DrawioPage
from harness.whiteboard import Box

from cdd_guidance.practices.clean_engineering.model import Module, module_path_in
from cdd_guidance.practices.clean_engineering.model.diagram.class_layout import CardPlacement, DiagramArrow
from cdd_guidance.practices.clean_engineering.model.diagram.class_view import ClassViewPage, cell_slug
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import DiagramClass
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import flowed
from cdd_guidance.practices.clean_engineering.model.drawio.diagram_node import DrawIOModule
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import (
    ClassDiagramPageWriter,
    ClassDiagramWriter,
    DrawIOCleanEngineeringModel,
)
from cdd_guidance.practices.ddd.model.drawn.drawn_map import MODULES_TITLE_ENDING, AggregateCell, ContextCell, DrawnBoundedContextMap
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap
from harness.guidance.practice_formats import Written

# The room between a container's edge and what it holds, and the room above that for its title.
CONTAINER_INSET = 30
CONTAINER_TITLE_ROOM = 30
# The room between two containers, side by side or one under the other, wide enough for the arrows that run between.
CONTAINER_GAP = 80
# How wide a row of aggregates in a context, or of contexts on the page, runs before the next row starts below it.
CONTAINER_ROW_WIDTH = 2400
# Where the first context's container stands from the page's top-left corner.
PAGE_MARGIN = 40


class DrawIOContextCell(ContextCell, DrawIOModule):
    """A bounded context on the map: a module whose cell style names its kind (`kind=boundedContext;`)."""

    KIND = "boundedContext"


class DrawIOAggregateCell(AggregateCell, DrawIOModule):
    """An aggregate on the map: a module nested in its context's module (`kind=aggregate;`)."""

    KIND = "aggregate"


_CONTAINER_STYLE = "rounded=1;arcSize=2;whiteSpace=wrap;html=1;verticalAlign=top;align=left;spacingLeft=10;spacingTop=4;fontStyle=1;"
# A container's style names its kind as the map's cells do; its colours are none a modules view's cells are drawn in,
# so a reader never takes the aggregate view for a modules view.
CONTEXT_STYLE = f"{_CONTAINER_STYLE}fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;kind={DrawIOContextCell.KIND};"
AGGREGATE_STYLE = f"{_CONTAINER_STYLE}fontSize=12;fillColor=#ffffff;strokeColor=#999999;dashed=1;kind={DrawIOAggregateCell.KIND};"


class _AggregateCards:
    """One aggregate's cards, laid out together by the shared placement, and moved as one to where its container
    stands."""

    def __init__(self, page: ClassViewPage, arrows: List[DiagramArrow]) -> None:
        self.cards = page.cards(arrows)
        CardPlacement(list(self.cards.values()), arrows).place()

    def size(self) -> Tuple[float, float]:
        """The width and height its container fills: its cards, inset from the container's edges, under its title."""
        container = _round(_bounds(card.geometry for card in self.cards.values()))
        return (container.w, container.h)

    def move_to(self, left: float, top: float) -> None:
        """Move the cards so their container's top-left corner stands at (left, top)."""
        container = _round(_bounds(card.geometry for card in self.cards.values()))
        for card in self.cards.values():
            card.geometry = card.geometry.shifted(left - container.x, top - container.y)


class _ContextCards:
    """One bounded context's aggregates, their containers side by side in rows inside the context's container."""

    def __init__(self, aggregates: List[_AggregateCards]) -> None:
        self.aggregates = aggregates
        self._corners = flowed([item.size() for item in aggregates], CONTAINER_ROW_WIDTH, CONTAINER_GAP)

    def size(self) -> Tuple[float, float]:
        """The width and height its container fills: its aggregates' containers, inset from its edges, under its title."""
        right = max(left + item.size()[0] for item, (left, _top) in zip(self.aggregates, self._corners))
        bottom = max(top + item.size()[1] for item, (_left, top) in zip(self.aggregates, self._corners))
        container = _round(Box(0, 0, right, bottom))
        return (container.w, container.h)

    def move_to(self, left: float, top: float) -> None:
        """Move its aggregates so its container's top-left corner stands at (left, top)."""
        for item, (x, y) in zip(self.aggregates, self._corners):
            item.move_to(left + CONTAINER_INSET + x, top + CONTAINER_INSET + CONTAINER_TITLE_ROOM + y)


class AggregateViewPage(ClassDiagramPageWriter):
    """The aggregate view's one page: each aggregate's cards laid out together inside a container titled with the
    aggregate's name, and the aggregates of one bounded context inside a larger container titled with the context's
    name and owner. Arrows between aggregates run in the room between the containers."""

    def laid_out(self, positions: Dict[str, Tuple[float, float]]) -> Tuple[Dict[str, DiagramClass], List[DiagramArrow]]:
        """Every card placed in its aggregate's container and its context's, keeping those a person already placed at
        positions; and the arrows between them, not yet routed."""
        arrows = self._arrows()
        contexts = [
            _ContextCards([_AggregateCards(ClassViewPage(self._writer, module, shows_imports=False), arrows) for module in modules])
            for modules in self._modules_by_context().values()
        ]
        corners = flowed([item.size() for item in contexts], CONTAINER_ROW_WIDTH, CONTAINER_GAP)
        for item, (left, top) in zip(contexts, corners):
            item.move_to(PAGE_MARGIN + left, PAGE_MARGIN + top)
        placed = {cell_id: card for item in contexts for aggregate in item.aggregates for cell_id, card in aggregate.cards.items()}
        cards = {cell_id: placed[cell_id] for cell_id in self._writer.classes_by_cell if cell_id in placed}
        self._keep_placed(cards, positions)
        return cards, arrows

    def enclose(self, root_el: ET.Element, cards: Dict[str, DiagramClass]) -> None:
        """A container round each aggregate's cards, and round each bounded context's aggregates' containers."""
        page = DrawioPage("", root_el)
        for context_labels, modules in self._modules_by_context().items():
            held = [(module, [cards[cell_id].geometry for cell_id in self._cell_ids_of(module) if cell_id in cards]) for module in modules]
            aggregates = [(module, _round(_bounds(boxes))) for module, boxes in held if boxes]
            if not aggregates:
                continue
            label = " · ".join(context_labels)
            page.add(f"context-{cell_slug(label)}", label, CONTEXT_STYLE, _round(_bounds(box for _module, box in aggregates)))
            for module, box in aggregates:
                page.add(f"aggregate-{cell_slug(module.name)}", module_path_in(module.name)[-1], AGGREGATE_STYLE, box)

    def _modules_by_context(self) -> Dict[Tuple[str, ...], List[Module]]:
        """Each aggregate's module, by the labels of the bounded contexts that hold it, in the model's order."""
        grouped: Dict[Tuple[str, ...], List[Module]] = {}
        for module in self._writer.named_modules:
            grouped.setdefault(tuple(module_path_in(module.name)[:-1]), []).append(module)
        return grouped

    def _cell_ids_of(self, module: Module) -> List[str]:
        return [self._writer.cell_ids[id(oclass)] for oclass in module.classes]

    def _keep_placed(self, cards: Dict[str, DiagramClass], positions: Dict[str, Tuple[float, float]]) -> None:
        """Cards a person already placed stay where they left them; new ones stand below them, as laid out."""
        kept = [cell_id for cell_id in cards if cell_id in positions]
        if not kept:
            return
        new = [card for cell_id, card in cards.items() if cell_id not in positions]
        for cell_id in kept:
            cards[cell_id].geometry = cards[cell_id].geometry.moved_to(*positions[cell_id])
        if not new:
            return
        bottom = max(cards[cell_id].geometry.y + cards[cell_id].geometry.h for cell_id in kept)
        top = min(card.geometry.y for card in new)
        for card in new:
            card.geometry = card.geometry.shifted(0, bottom + CONTAINER_GAP - top)


def _bounds(boxes: Iterable[Box]) -> Box:
    """The smallest box round every one of boxes."""
    boxes = list(boxes)
    left = min(box.x for box in boxes)
    top = min(box.y for box in boxes)
    return Box(left, top, max(box.x + box.w for box in boxes) - left, max(box.y + box.h for box in boxes) - top)


def _round(box: Box) -> Box:
    """The container drawn round box: inset from it on every side, with room for its title above."""
    return Box(
        box.x - CONTAINER_INSET, box.y - CONTAINER_INSET - CONTAINER_TITLE_ROOM,
        box.w + 2 * CONTAINER_INSET, box.h + 2 * CONTAINER_INSET + CONTAINER_TITLE_ROOM,
    )


class AggregateViewDiagram(ClassDiagramWriter):
    """The aggregate view drawn in draw.io: every aggregate on one page, so each bounded context's container holds
    every aggregate it has, however many classes the model holds."""

    @property
    def on_one_page(self) -> bool:
        return True

    @property
    def page_type(self) -> type:
        return AggregateViewPage


class DrawIOBoundedContextMap(DrawnBoundedContextMap, DrawIOCleanEngineeringModel):
    """The `drawio` format: the map as a Clean Engineering draw.io diagram. Its contexts and aggregates are drawn as
    its own modules, which it renders as itself; at model fidelity, its aggregate view (*AggregateViewDiagram*)."""

    context_cell_type = DrawIOContextCell
    aggregate_cell_type = DrawIOAggregateCell
    module_cell_types = (DrawIOContextCell, DrawIOAggregateCell, DrawIOModule)
    class_diagram_type = AggregateViewDiagram

    def render(self, canonical: BoundedContextMap, written: Written = Written()) -> str:
        """The aggregate view when the map's aggregates hold class cards (model fidelity); otherwise the map. The cards a
        person placed on previous, the drawing this one replaces, stay where they are."""
        self.draw(canonical)
        return DrawIOCleanEngineeringModel.render(self, self, written)

    def _read_title(self, cell: ET.Element) -> None:
        """The map's own name, from the title it was drawn under; a modules view's title names its system instead."""
        super()._read_title(cell)
        if cell.get("id") == "title" and not self._names_the_modules_title(cell):
            self.title = html.unescape(cell.get("value", "")).strip()

    def _names_the_modules_title(self, cell: ET.Element) -> bool:
        return html.unescape(cell.get("value", "")).rstrip().endswith(MODULES_TITLE_ENDING)

    def parse(self, text: str, file: str = "") -> "DrawIOBoundedContextMap":
        """Read a drawing into this map, and return it."""
        DrawIOCleanEngineeringModel.parse(self, text)
        return self.read_drawing()
