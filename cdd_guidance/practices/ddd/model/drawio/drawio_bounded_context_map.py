"""DrawIO channel — the bounded-context map drawn as context swimlanes holding their aggregates, and read back."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape, unescape
from typing import Dict, List, Optional, Tuple

from cdd_guidance.practices.ddd.model.drawio.drawio_aggregate_model import (
    AGGREGATE_VIEW_PAGE,
    DrawIOAggregateModel,
    has_class_cards,
)
from cdd_guidance.practices.ddd.model.drawio.drawn_diagram import DrawnCell, DrawnDiagram
from cdd_guidance.practices.ddd.model.markdown.nodes import (
    MarkdownAggregate,
    MarkdownBoundedContext,
    MarkdownBoundedContextMap,
    MarkdownEntity,
    MarkdownIntegration,
    MarkdownInvariantObject,
    looks_like_operation,
)
from cdd_guidance.practices.ddd.model.nodes import Aggregate, BoundedContext, BoundedContextMap, Integration

_CONTEXT_STYLE = (
    "swimlane;startSize=36;rounded=1;fillColor=#1a3a6e;swimlaneFillColor=#16325f;"
    "strokeColor=#0e2547;fontColor=#ffffff;fontSize=11;fontStyle=1;html=1;strokeWidth=2;"
    "collapsible=0;container=1;horizontal=1;whiteSpace=wrap;"
)
_CONTEXT_TITLE_FONT = 11
_CONTEXT_OWNER_FONT = 10
_AGGREGATE_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#4a86c8;strokeColor=#1a3a6e;"
    "fontColor=#ffffff;fontSize=10;align=left;verticalAlign=top;spacingLeft=6;spacingTop=4;"
    "spacingBottom=8;strokeWidth=2;"
)
_INTEGRATION_EDGE_STYLE = (
    "endArrow=classic;html=1;strokeWidth=2;fontSize=10;strokeColor=#1a3a6e;rounded=0;"
)
_PAGE_ID = "bounded-context-map"
_TITLE = "Bounded Context Map"
# The page's starting canvas; `finish` sizes the page to what was drawn.
_STARTING_PAGE = {"dx": "1200", "dy": "900", "pageWidth": "2400", "pageHeight": "1600"}
_CONTEXT_WIDTH = 190
_CONTEXT_GAP = 80
_CONTEXT_INSET = 8
_AGGREGATE_WIDTH = _CONTEXT_WIDTH - 2 * _CONTEXT_INSET
_AGGREGATE_GAP = 10
_SIDE_MIN_GAP = 120
_AGGREGATE_TITLE_FONT = 10
_BULLET_FONT = 10
_AGGREGATE_TITLE_BLOCK = 14
_BULLET_LINE = 11
_AGGREGATE_TOP_PAD = 4
_AGGREGATE_BOTTOM_PAD = 10
_BULLET_LIST_TOP = 2
_CONTEXT_HEADER = 36
_CONTEXT_COLUMN_GAP = 160
_PAGE_MARGIN = 100
_MAX_MEMBERS = 10
# Sort key for an aggregate no arc from the hub reaches: after every ranked one.
_NO_RANK = 999.0
# Arrows leave and enter a box between 15% and 85% of its height, spread evenly.
_ANCHOR_MARGIN = 0.15
_ANCHOR_SPAN = 0.7
# Cells "0" and "1" are draw.io's root and page layer, not boxes.
_PAGE_LAYERS = {"", "0", "1"}


@dataclass
class _EdgePlan:
    source_id: str
    target_id: str
    label: str


@dataclass
class _Route:
    plan: _EdgePlan
    exit_x: float
    exit_y: float
    entry_x: float
    entry_y: float


@dataclass
class _IntegrationLink:
    source_context: str
    source_aggregate: str
    target_context: str
    target_aggregate: str = ""
    target_entity: str = ""


@dataclass
class _CellRecord:
    cell_id: str
    parent_id: str
    x: float
    y: float
    width: float
    height: float


class DrawIOBoundedContextMap(MarkdownBoundedContextMap):
    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        source = canonical if canonical is not None else self
        if has_class_cards(source):
            # Model fidelity: the aggregate view, not the context map.
            return DrawIOAggregateModel().render(source)
        return self._write_diagram(source)

    def parse(self, text: str) -> "DrawIOBoundedContextMap":
        model = type(self)()
        diagram = DrawnDiagram(text)
        reader = DrawIOAggregateModel() if diagram.page_id == AGGREGATE_VIEW_PAGE else _ContextMapReader()
        for context in reader.contexts_in(diagram):
            model.append_context(context)
        return model

    def _write_diagram(self, model: BoundedContextMap) -> str:
        layout = ContextLayout([item for item in model.contexts if isinstance(item, BoundedContext)])
        writer = _DiagramWriter()
        for context in layout.contexts:
            x, y = layout.positions[context.name]
            writer.add_context(context, x, y, layout.aggregate_orders.get(context.name))
        writer.draw_integration_edges()
        return writer.finish(title=_TITLE)


class _ContextMapReader:
    """Reads the context map back: each swimlane a context, each box in it an aggregate, each arrow an integration."""

    def contexts_in(self, diagram: DrawnDiagram) -> List[MarkdownBoundedContext]:
        contexts: Dict[str, MarkdownBoundedContext] = {}
        aggregates: Dict[str, MarkdownAggregate] = {}
        for swimlane in diagram.boxes_in():
            context = self._context(swimlane, len(contexts) + 1)
            contexts[swimlane.cell_id] = context
            for box in diagram.boxes_in(swimlane.cell_id):
                aggregates[box.cell_id] = self._aggregate(context, box)
        for arrow in diagram.arrows:
            self._integrate(arrow, aggregates)
        return list(contexts.values())

    def _context(self, swimlane: DrawnCell, order: int) -> MarkdownBoundedContext:
        texts = swimlane.texts + [""]
        context = MarkdownBoundedContext(texts[0], order)
        context.owner = texts[1]
        return context

    def _aggregate(self, context: MarkdownBoundedContext, box: DrawnCell) -> MarkdownAggregate:
        title, *members = box.texts
        aggregate = MarkdownAggregate(title, len(context.aggregates) + 1)
        context.append_aggregate(aggregate)
        root = MarkdownEntity(title, 1)
        root.invariant_objects = [MarkdownInvariantObject(name, index) for index, name in enumerate(members)]
        aggregate.take_root(root)
        return aggregate

    def _integrate(self, arrow: DrawnCell, aggregates: Dict[str, MarkdownAggregate]) -> None:
        source = aggregates.get(arrow.source_id)
        target = aggregates.get(arrow.target_id)
        if source is None or target is None:
            return
        integration = MarkdownIntegration()
        integration.context = target.parent.name
        integration.aggregate = target.name
        integration.target = f"{integration.context} · {integration.aggregate}"
        integration.pattern = unescape(arrow.value)
        source.integrations.append(integration)


class ContextLayout:
    """Where each context and aggregate goes: the most connected context in the middle, the others beside it,
    each level with the hub aggregates that reach it."""

    def __init__(self, contexts: List[BoundedContext]) -> None:
        self.contexts = contexts
        self.by_name = {context.name: context for context in contexts}
        self.links = [link for link in (self._link(*arc) for arc in self._arcs()) if link is not None]
        self.hub = self._hub() if contexts else ""
        self.positions = self._positions()
        self.aggregate_orders = self._aggregate_orders() if contexts else {}

    def _arcs(self):
        for context in self.contexts:
            for aggregate in context.aggregates:
                yield from ((context, aggregate, integration) for integration in aggregate.integrations)

    def _link(self, context: BoundedContext, aggregate: Aggregate, integration: Integration) -> Optional[_IntegrationLink]:
        target_context = self._target_context(integration)
        if not target_context or target_context == context.name:
            return None
        _context, aggregate_name, entity_name = integration.target_parts
        return _IntegrationLink(
            context.name, aggregate.name, target_context, integration.aggregate or aggregate_name, entity_name
        )

    def _target_context(self, integration: Integration) -> str:
        name = integration.context or integration.target_parts[0]
        matched = self._context_named(name) if name else None
        return matched.name if matched else ""

    def _context_named(self, name: str) -> Optional[BoundedContext]:
        """The context whose name starts the other's: `Catalog` names `Catalog | bespoke`."""
        key = name.strip().lower()
        for context in self.contexts:
            plain = context.name.split("|", 1)[0].strip().lower()
            if plain.startswith(key) or key.startswith(plain) or context.name.lower() == key:
                return context
        return None

    def _hub(self) -> str:
        outgoing = {name: {link.target_context for link in self.links if link.source_context == name} for name in self.by_name}
        incoming = {name: sum(1 for targets in outgoing.values() if name in targets) for name in self.by_name}

        def score(context: BoundedContext) -> Tuple[int, int, int]:
            return (len(outgoing[context.name]), incoming[context.name], -(context.sequential_order or 0))

        return max(self.contexts, key=score).name

    @property
    def _hub_x(self) -> int:
        return _CONTEXT_GAP + _CONTEXT_WIDTH + _CONTEXT_COLUMN_GAP

    @property
    def _peripheral_names(self) -> List[str]:
        return [name for name in self.by_name if name != self.hub]

    def _hub_links(self) -> List[_IntegrationLink]:
        return [link for link in self.links if link.source_context == self.hub]

    def _positions(self) -> Dict[str, Tuple[int, int]]:
        if len(self.contexts) <= 1:
            return {context.name: (_CONTEXT_GAP, _CONTEXT_GAP) for context in self.contexts}
        anchors = self._peripheral_anchors()
        ordered = sorted(self._peripheral_names, key=lambda name: anchors.get(name, 0.0))
        midpoint = (len(ordered) + 1) // 2
        left, right = ordered[:midpoint], ordered[midpoint:]
        positions = self._place_sides(left, right, anchors, self._estimated_hub_y(anchors))
        positions = self._place_sides(left, right, anchors, float(self._centred_hub_y(positions)))
        positions[self.hub] = (self._hub_x, self._centred_hub_y(positions))
        return positions

    def _peripheral_anchors(self) -> Dict[str, float]:
        """How far down the hub each peripheral context's arcs leave it, on average."""
        centres = _aggregate_centre_offsets(self.by_name[self.hub])
        anchors: Dict[str, List[float]] = {}
        for link in self._hub_links():
            anchors.setdefault(link.target_context, []).append(centres.get(link.source_aggregate, float(_CONTEXT_HEADER)))
        return {name: sum(values) / len(values) for name, values in anchors.items()}

    def _place_sides(self, left: List[str], right: List[str], anchors: Dict[str, float], hub_y: float) -> Dict[str, Tuple[int, int]]:
        right_x = self._hub_x + _CONTEXT_WIDTH + _CONTEXT_COLUMN_GAP
        positions = self._place_column(left, anchors, hub_y, _CONTEXT_GAP)
        positions.update(self._place_column(right, anchors, hub_y, right_x))
        return positions

    def _place_column(self, names: List[str], anchors: Dict[str, float], hub_y: float, x: int) -> Dict[str, Tuple[int, int]]:
        if not names:
            return {}
        ordered = sorted(names, key=lambda name: anchors.get(name, 0.0))
        heights = [float(_context_height(self.by_name[name])) for name in ordered]
        ideal_tops = [hub_y + anchors.get(name, height / 2.0) - height / 2.0 for name, height in zip(ordered, heights)]
        positions: Dict[str, Tuple[int, int]] = {}
        cursor = max(float(_CONTEXT_GAP), min(ideal_tops))
        for name, height, ideal in zip(ordered, heights, ideal_tops):
            top = max(ideal, cursor)
            positions[name] = (x, int(top))
            cursor = top + height + _SIDE_MIN_GAP
        return positions

    def _estimated_hub_y(self, anchors: Dict[str, float]) -> float:
        if not anchors:
            return float(_CONTEXT_GAP)
        anchor_span = max(anchors.values()) - min(anchors.values())
        peripheral_span = sum(_context_height(self.by_name[name]) + _SIDE_MIN_GAP for name in self._peripheral_names)
        return float(_CONTEXT_GAP) + max(anchor_span, float(peripheral_span)) / 4.0

    def _centred_hub_y(self, positions: Dict[str, Tuple[int, int]]) -> int:
        names = self._peripheral_names
        side_top = min(positions[name][1] for name in names)
        side_bottom = max(positions[name][1] + _context_height(self.by_name[name]) for name in names)
        centred = int((side_top + side_bottom) / 2 - _context_height(self.by_name[self.hub]) / 2)
        return max(_CONTEXT_GAP, centred)

    def _aggregate_orders(self) -> Dict[str, List[str]]:
        orders = {self.hub: self._hub_order()}
        hub_rank = {name: index for index, name in enumerate(orders[self.hub])}
        for context in self.contexts:
            if context.name != self.hub:
                orders[context.name] = self._peripheral_order(context, hub_rank)
        return orders

    def _hub_order(self) -> List[str]:
        """Hub aggregates top to bottom in the order of the contexts their arcs reach."""
        centres = {
            name: y + _context_height(self.by_name[name]) / 2.0 for name, (_x, y) in self.positions.items() if name != self.hub
        }
        reached: Dict[str, List[float]] = {}
        for link in self._hub_links():
            if link.target_context in centres:
                reached.setdefault(link.source_aggregate, []).append(centres[link.target_context])

        def rank(aggregate: Aggregate) -> Tuple[float, float]:
            found = reached.get(aggregate.name, [])
            return (sum(found) / len(found) if found else _NO_RANK, float(aggregate.sequential_order or 0))

        return [aggregate.name for aggregate in sorted(self.by_name[self.hub].aggregates, key=rank)]

    def _peripheral_order(self, context: BoundedContext, hub_rank: Dict[str, int]) -> List[str]:
        """A peripheral context's aggregates in the order of the hub aggregates that reach them."""
        aggregates = list(context.aggregates)
        ranks: Dict[str, float] = {}
        for link in self._hub_links():
            target = _link_target_name(link, aggregates) if link.target_context == context.name else None
            if target is not None:
                ranks[target] = min(ranks.get(target, _NO_RANK), float(hub_rank.get(link.source_aggregate, _NO_RANK)))
        return [
            aggregate.name
            for aggregate in sorted(aggregates, key=lambda item: (ranks.get(item.name, _NO_RANK), float(item.sequential_order or 0)))
        ]


class _DiagramWriter:
    def __init__(self) -> None:
        self._next_id = 2
        self._mxfile = ET.Element("mxfile", attrib={"host": "CleanEngineering.diagram.drawio"})
        diagram = ET.SubElement(self._mxfile, "diagram", attrib={"name": _TITLE, "id": _PAGE_ID})
        self._graph = ET.SubElement(
            diagram,
            "mxGraphModel",
            attrib={"grid": "1", "gridSize": "10", "guides": "1", "page": "1", "pageScale": "1", **_STARTING_PAGE},
        )
        self._root = ET.SubElement(self._graph, "root")
        ET.SubElement(self._root, "mxCell", attrib={"id": "0"})
        ET.SubElement(self._root, "mxCell", attrib={"id": "1", "parent": "0"})
        self._cells: Dict[str, _CellRecord] = {}
        self._context_ids: Dict[str, str] = {}
        self._aggregate_ids: Dict[Tuple[str, str], str] = {}
        self._pending_integrations: List[Tuple[str, str, Integration]] = []

    def add_context(self, context: BoundedContext, x: int, y: int, aggregate_order: Optional[List[str]] = None) -> None:
        box = (x, y, _CONTEXT_WIDTH, _context_height(context))
        context_id = self._vertex(_context_label(context), box, _CONTEXT_STYLE, "1")
        self._context_ids[context.name] = context_id
        top = _CONTEXT_HEADER + _CONTEXT_INSET
        for aggregate in _ordered_aggregates(context, aggregate_order):
            top += self._add_aggregate(context.name, aggregate, context_id, top) + _AGGREGATE_GAP

    def _add_aggregate(self, context_name: str, aggregate: Aggregate, context_id: str, top: int) -> int:
        bullets = _bullet_members(aggregate)
        height = _aggregate_height(len(bullets))
        box = (_CONTEXT_INSET, top, _AGGREGATE_WIDTH, height)
        self._aggregate_ids[(context_name, aggregate.name)] = self._vertex(
            _aggregate_label(aggregate, bullets), box, _AGGREGATE_STYLE, context_id
        )
        self._pending_integrations.extend((context_name, aggregate.name, item) for item in aggregate.integrations)
        return height

    def draw_integration_edges(self) -> None:
        placements = {cell_id: self._absolute_box(cell_id) for cell_id in self._cells}
        plans = [self._edge_plan(*pending) for pending in self._pending_integrations]
        drawable = [plan for plan in plans if plan is not None and {plan.source_id, plan.target_id} <= placements.keys()]
        for route in _StraightRoutes(placements, drawable).routes():
            self._add_straight_edge(route)

    def _edge_plan(self, context_name: str, aggregate_name: str, integration: Integration) -> Optional[_EdgePlan]:
        source_id = self._aggregate_ids.get((context_name, aggregate_name))
        target_id = self._target_cell(integration)
        if source_id is None or target_id is None or target_id == source_id:
            return None
        return _EdgePlan(source_id, target_id, integration.pattern or "")

    def _target_cell(self, integration: Integration) -> Optional[str]:
        context_name, aggregate_name, entity_name = integration.target_parts
        if integration.context or integration.aggregate:
            context_name, aggregate_name = integration.context, integration.aggregate
        matched = next((name for name in self._context_ids if _same_name(context_name, name)), None)
        if matched is None:
            return self._cell_named(aggregate_name or entity_name)
        return self._cell_in_context(matched, aggregate_name, entity_name)

    def _cell_named(self, name: str) -> Optional[str]:
        if not name:
            return None
        return next((cell for (_context, aggregate), cell in self._aggregate_ids.items() if _same_name(aggregate, name)), None)

    def _cell_in_context(self, context_name: str, aggregate_name: str, entity_name: str) -> Optional[str]:
        for candidate in (item for item in (entity_name, aggregate_name) if item):
            for (context, aggregate), cell_id in self._aggregate_ids.items():
                if context == context_name and _same_name(aggregate, candidate):
                    return cell_id
        return None

    def _add_straight_edge(self, route: _Route) -> None:
        cell_id = str(self._next_id)
        self._next_id += 1
        style = (
            f"{_INTEGRATION_EDGE_STYLE}"
            f"exitX={route.exit_x};exitY={route.exit_y};exitDx=0;exitDy=0;"
            f"entryX={route.entry_x};entryY={route.entry_y};entryDx=0;entryDy=0;"
        )
        attributes = {"id": cell_id, "value": escape(route.plan.label), "style": style, "edge": "1"}
        cell = ET.SubElement(
            self._root,
            "mxCell",
            attrib={**attributes, "source": route.plan.source_id, "target": route.plan.target_id, "parent": "1"},
        )
        ET.SubElement(cell, "mxGeometry", attrib={"relative": "1", "as": "geometry"})

    def _vertex(self, label: str, box: Tuple[int, int, int, int], style: str, parent: str) -> str:
        cell_id = str(self._next_id)
        self._next_id += 1
        cell = ET.SubElement(
            self._root,
            "mxCell",
            attrib={"id": cell_id, "value": label, "style": style, "vertex": "1", "parent": parent},
        )
        x, y, width, height = box
        geometry = {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"}
        ET.SubElement(cell, "mxGeometry", attrib=geometry)
        self._cells[cell_id] = _CellRecord(cell_id, parent, float(x), float(y), float(width), float(height))
        return cell_id

    def _absolute_box(self, cell_id: str) -> Tuple[float, float, float, float]:
        record = self._cells[cell_id]
        x, y = record.x, record.y
        parent_id = record.parent_id
        while parent_id not in _PAGE_LAYERS and parent_id in self._cells:
            parent = self._cells[parent_id]
            x += parent.x
            y += parent.y
            parent_id = parent.parent_id
        return (x, y, record.width, record.height)

    def finish(self, title: str) -> str:
        self._mxfile.find("diagram").set("name", title)
        boxes = [self._absolute_box(cell_id) for cell_id in self._cells]
        self._graph.set("pageWidth", str(int(max((x + width for x, _y, width, _h in boxes), default=0.0) + _PAGE_MARGIN)))
        self._graph.set("pageHeight", str(int(max((y + height for _x, y, _w, height in boxes), default=0.0) + _PAGE_MARGIN)))
        body = ET.tostring(self._mxfile, encoding="unicode")
        return "<?xml version='1.0' encoding='utf-8'?>\n" + body


class _StraightRoutes:
    """Straight arrows between aggregate boxes, their ends spread down each box in the order of the far ends."""

    def __init__(self, placements: Dict[str, Tuple[float, float, float, float]], plans: List[_EdgePlan]) -> None:
        self.placements = placements
        self.plans = sorted(plans, key=lambda plan: (self._centre_y(plan.target_id) + self._centre_y(plan.source_id)) / 2.0)

    def routes(self) -> List[_Route]:
        exits = self._spread(lambda plan: plan.source_id, lambda plan: plan.target_id)
        entries = self._spread(lambda plan: plan.target_id, lambda plan: plan.source_id)
        return [self._route(plan, exits[id(plan)], entries[id(plan)]) for plan in self.plans]

    def _spread(self, near_end, far_end) -> Dict[int, float]:
        """Where each arrow meets its near box, as a fraction of that box's height."""
        groups: Dict[str, List[_EdgePlan]] = {}
        for plan in self.plans:
            groups.setdefault(near_end(plan), []).append(plan)
        fractions: Dict[int, float] = {}
        for group in groups.values():
            group.sort(key=lambda plan: self._centre_y(far_end(plan)))
            fractions.update((id(plan), fraction) for fraction, plan in zip(_anchor_fractions(len(group)), group))
        return fractions

    def _route(self, plan: _EdgePlan, exit_y: float, entry_y: float) -> _Route:
        leftward = self.placements[plan.source_id][0] >= self.placements[plan.target_id][0]
        exit_x, entry_x = (0.0, 1.0) if leftward else (1.0, 0.0)
        return _Route(plan, exit_x, exit_y, entry_x, entry_y)

    def _centre_y(self, cell_id: str) -> float:
        _x, y, _width, height = self.placements[cell_id]
        return y + height / 2.0


def _anchor_fractions(count: int) -> List[float]:
    if count <= 1:
        return [0.5]
    return [round(_ANCHOR_MARGIN + _ANCHOR_SPAN * index / (count - 1), 3) for index in range(count)]


def _ordered_aggregates(context: BoundedContext, aggregate_order: Optional[List[str]]) -> List[Aggregate]:
    aggregates = sorted(context.aggregates, key=lambda aggregate: float(aggregate.sequential_order or 0))
    if not aggregate_order:
        return aggregates
    by_name = {aggregate.name: aggregate for aggregate in aggregates}
    ordered = [by_name[name] for name in aggregate_order if name in by_name]
    placed = {aggregate.name for aggregate in ordered}
    return ordered + [aggregate for aggregate in aggregates if aggregate.name not in placed]


def _aggregate_centre_offsets(context: BoundedContext) -> Dict[str, float]:
    offsets: Dict[str, float] = {}
    top = float(_CONTEXT_HEADER + _CONTEXT_INSET)
    for aggregate in _ordered_aggregates(context, None):
        height = float(_aggregate_height(len(_bullet_members(aggregate))))
        offsets[aggregate.name] = top + height / 2.0
        top += height + _AGGREGATE_GAP
    return offsets


def _context_height(context: BoundedContext) -> int:
    heights = [_aggregate_height(len(_bullet_members(aggregate))) + _AGGREGATE_GAP for aggregate in context.aggregates]
    return _CONTEXT_HEADER + _CONTEXT_INSET + sum(heights) + _CONTEXT_INSET


def _link_target_name(link: _IntegrationLink, aggregates: List[Aggregate]) -> Optional[str]:
    for candidate in (link.target_aggregate, link.target_entity):
        found = next((aggregate.name for aggregate in aggregates if candidate and _same_name(aggregate.name, candidate)), None)
        if found is not None:
            return found
    return None


def _same_name(left: str, right: str) -> bool:
    return left.strip().lower() == right.strip().lower()


def _aggregate_height(bullet_count: int) -> int:
    base = _AGGREGATE_TITLE_BLOCK + _AGGREGATE_TOP_PAD + _AGGREGATE_BOTTOM_PAD
    if bullet_count <= 0:
        return base
    return base + _BULLET_LIST_TOP + bullet_count * _BULLET_LINE


def _bullet_members(aggregate: Aggregate) -> list[str]:
    members = [_plain_entity_name(member) for member in _member_labels(aggregate)]
    if members and members[0].lower() == aggregate.name.lower():
        return members[1:]
    return members


def _context_label(context: BoundedContext) -> str:
    name = escape(context.name)
    wrap = "word-wrap:break-word;overflow-wrap:break-word;"
    if not context.owner:
        return (
            f'<div style="font-size:{_CONTEXT_TITLE_FONT}px;line-height:1.15;'
            f'font-weight:bold;text-align:center;{wrap}">{name}</div>'
        )
    owner = escape(context.owner)
    return (
        f'<div style="font-size:{_CONTEXT_TITLE_FONT}px;line-height:1.15;text-align:center;{wrap}">'
        f'<div style="font-weight:bold;">{name}</div>'
        f'<div style="font-size:{_CONTEXT_OWNER_FONT}px;opacity:0.9;">{owner}</div>'
        f"</div>"
    )


def _aggregate_label(aggregate: Aggregate, bullets: list[str]) -> str:
    title = escape(aggregate.name)
    title_style = (
        f"margin:0;font-size:{_AGGREGATE_TITLE_FONT}px;line-height:1.1;font-weight:bold;"
        f"word-wrap:break-word;overflow-wrap:break-word;"
    )
    if not bullets:
        return f'<p style="{title_style}">{title}</p>'
    items = "".join(f'<li style="margin:0;padding:0;line-height:1.1;">{escape(name)}</li>' for name in bullets)
    return (
        f'<p style="{title_style}">{title}</p>'
        f'<ul style="margin:{_BULLET_LIST_TOP}px 0 0 8px;padding:0;font-size:{_BULLET_FONT}px;'
        f'line-height:1.1;list-style-position:outside;">'
        f"{items}</ul>"
    )


def _member_labels(aggregate: Aggregate) -> list[str]:
    """The root, then up to ten of the members it holds; prose and operations are not drawn."""
    if aggregate.root is None:
        return [aggregate.name]
    root_line = aggregate.root.name.strip()
    labels = [root_line] if root_line else []
    seen = {_plain_entity_name(root_line).lower()}
    for name in _drawable_members(aggregate):
        if name.lower() not in seen and len(labels) < _MAX_MEMBERS:
            seen.add(name.lower())
            labels.append(name)
    return labels or [aggregate.name]


def _drawable_members(aggregate: Aggregate) -> list[str]:
    names = [item.name.split("//", 1)[0].strip() for item in aggregate.root.invariant_objects]
    return [name for name in names if name and not _looks_like_prose(name) and not looks_like_operation(name)]


def _plain_entity_name(label: str) -> str:
    return label.split(" - ", 1)[0].strip()


def _looks_like_prose(line: str) -> bool:
    text = line.strip()
    if not text or text.lower().startswith("note:"):
        return True
    return ". " in text or text.endswith(".") or text[0].islower()
