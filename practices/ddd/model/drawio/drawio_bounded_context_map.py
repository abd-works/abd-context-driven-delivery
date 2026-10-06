"""DrawIO channel — bounded-context map from markdown."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from practices.ddd.model.markdown.nodes import MarkdownAggregate, MarkdownBoundedContextMap
from practices.ddd.model.nodes import Aggregate, BoundedContext, BoundedContextMap, Integration

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
_CONTEXT_WIDTH = 190
_CONTEXT_GAP = 80
_CONTEXT_INSET = 8
_AGG_GAP = 10
_SIDE_MIN_GAP = 120
_AGG_TITLE_FONT = 10
_BULLET_FONT = 10
_AGG_TITLE_BLOCK = 14
_BULLET_LINE = 11
_AGG_TOP_PAD = 4
_AGG_BOTTOM_PAD = 10
_BULLET_UL_TOP = 2
_CONTEXT_HEADER = 36
_CONTEXT_COL_GAP = 160
_PAGE_MARGIN = 100
_MAX_MEMBERS = 10
_ARROW_SPLIT = re.compile(r"[\u00b7\u2022]")


@dataclass
class _EdgePlan:
    src_id: str
    tgt_id: str
    label: str


@dataclass
class _IntegrationLink:
    src_context: str
    src_aggregate: str
    tgt_context: str
    tgt_aggregate: str = ""
    tgt_entity: str = ""


class DrawIOBoundedContextMap(MarkdownBoundedContextMap):
    def render(self, canonical=None, previous: str | None = None) -> str:
        source = canonical if canonical is not None else self
        markdown = MarkdownBoundedContextMap()
        body = markdown.render(source, previous)
        parsed = markdown.parse(body)
        return self._write_diagram(parsed)

    def _write_diagram(self, model: BoundedContextMap) -> str:
        writer = _DiagramWriter()
        contexts = [item for item in model.contexts if isinstance(item, BoundedContext)]
        outgoing, links = _integration_graph(contexts)
        hub = _hub_context(contexts, outgoing)
        positions = _layout_context_positions(contexts, links, hub)
        aggregate_orders = _aggregate_render_orders(contexts, links, hub, positions)
        for context in contexts:
            abs_x, abs_y = positions[context.name]
            writer.add_context(
                context,
                abs_x,
                abs_y,
                aggregate_order=aggregate_orders.get(context.name),
            )
        writer.draw_integration_edges()
        return writer.finish(title="Bounded Context Map")


@dataclass
class _CellRecord:
    cell_id: str
    parent_id: str
    x: float
    y: float
    width: float
    height: float


class _DiagramWriter:
    def __init__(self) -> None:
        self._next_id = 2
        self._mxfile = ET.Element("mxfile", attrib={"host": "CleanEngineering.diagram.drawio"})
        diagram = ET.SubElement(
            self._mxfile,
            "diagram",
            attrib={"name": "Bounded Context Map", "id": "bounded-context-map"},
        )
        self._graph = ET.SubElement(
            diagram,
            "mxGraphModel",
            attrib={
                "dx": "1200",
                "dy": "900",
                "grid": "1",
                "gridSize": "10",
                "guides": "1",
                "page": "1",
                "pageScale": "1",
                "pageWidth": "2400",
                "pageHeight": "1600",
            },
        )
        self._root = ET.SubElement(self._graph, "root")
        ET.SubElement(self._root, "mxCell", attrib={"id": "0"})
        ET.SubElement(self._root, "mxCell", attrib={"id": "1", "parent": "0"})
        self._cells: Dict[str, _CellRecord] = {}
        self._context_ids: Dict[str, str] = {}
        self._aggregate_ids: Dict[Tuple[str, str], str] = {}
        self._pending_integrations: List[Tuple[str, str, Integration]] = []

    def add_context(
        self,
        context: BoundedContext,
        abs_x: int,
        abs_y: int,
        aggregate_order: Optional[List[str]] = None,
    ) -> int:
        aggregates = _ordered_aggregates(context, aggregate_order)
        agg_width = _CONTEXT_WIDTH - 2 * _CONTEXT_INSET
        agg_y = _CONTEXT_HEADER + _CONTEXT_INSET
        for aggregate in aggregates:
            bullets = _bullet_members(aggregate)
            agg_y += _aggregate_height(len(bullets)) + _AGG_GAP
        context_height = agg_y + _CONTEXT_INSET
        context_id = self._vertex(
            _context_label(context),
            abs_x,
            abs_y,
            _CONTEXT_WIDTH,
            context_height,
            _CONTEXT_STYLE,
            "1",
            html=True,
        )
        self._context_ids[context.name] = context_id
        agg_y = _CONTEXT_HEADER + _CONTEXT_INSET
        for aggregate in aggregates:
            bullets = _bullet_members(aggregate)
            agg_height = _aggregate_height(len(bullets))
            agg_id = self._vertex(
                _aggregate_label(aggregate, bullets),
                _CONTEXT_INSET,
                agg_y,
                agg_width,
                agg_height,
                _AGGREGATE_STYLE,
                context_id,
                html=True,
            )
            self._aggregate_ids[(context.name, aggregate.name)] = agg_id
            self._collect_edges(context.name, aggregate)
            agg_y += agg_height + _AGG_GAP
        return context_height

    def draw_integration_edges(self) -> None:
        placements = self._absolute_placements()
        plans: List[_EdgePlan] = []
        for context_name, aggregate_name, integration in self._pending_integrations:
            src_id = self._aggregate_ids.get((context_name, aggregate_name))
            if src_id is None:
                continue
            tgt_id = _resolve_target_aggregate(
                self._aggregate_ids,
                integration,
                self._context_ids,
            )
            if tgt_id is None or tgt_id == src_id:
                continue
            if src_id not in placements or tgt_id not in placements:
                continue
            plans.append(
                _EdgePlan(
                    src_id=src_id,
                    tgt_id=tgt_id,
                    label=integration.pattern or "",
                )
            )
        routes = _plan_straight_routes(placements, plans)
        for route in routes:
            self._add_straight_edge(route)

    def _add_straight_edge(self, route: dict) -> None:
        cell_id = str(self._next_id)
        self._next_id += 1
        style = (
            f"{_INTEGRATION_EDGE_STYLE}"
            f"exitX={route['exit_x']};exitY={route['exit_y']};exitDx=0;exitDy=0;"
            f"entryX={route['entry_x']};entryY={route['entry_y']};entryDx=0;entryDy=0;"
        )
        cell = ET.SubElement(self._root, "mxCell")
        cell.set("id", cell_id)
        cell.set("value", _escape(route["label"]))
        cell.set("style", style)
        cell.set("edge", "1")
        cell.set("source", route["src_id"])
        cell.set("target", route["tgt_id"])
        cell.set("parent", "1")
        geo = ET.SubElement(cell, "mxGeometry")
        geo.set("relative", "1")
        geo.set("as", "geometry")

    def _collect_edges(self, context_name: str, aggregate: Aggregate) -> None:
        if not isinstance(aggregate, MarkdownAggregate):
            return
        for integration in aggregate.integrations:
            self._pending_integrations.append((context_name, aggregate.name, integration))

    def _absolute_placements(self) -> Dict[str, Tuple[float, float, float, float]]:
        placements: Dict[str, Tuple[float, float, float, float]] = {}
        for cell_id, record in self._cells.items():
            placements[cell_id] = _absolute_bounds(self._cells, cell_id)
        return placements

    def _vertex(
        self,
        label: str,
        x: int,
        y: int,
        width: int,
        height: int,
        style: str,
        parent: str,
        *,
        html: bool = False,
    ) -> str:
        cell_id = str(self._next_id)
        self._next_id += 1
        value = label if html else _escape(label)
        cell = ET.SubElement(
            self._root,
            "mxCell",
            attrib={
                "id": cell_id,
                "value": value,
                "style": style,
                "vertex": "1",
                "parent": parent,
            },
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            attrib={
                "x": str(x),
                "y": str(y),
                "width": str(width),
                "height": str(height),
                "as": "geometry",
            },
        )
        self._cells[cell_id] = _CellRecord(cell_id, parent, float(x), float(y), float(width), float(height))
        return cell_id

    def finish(self, title: str) -> str:
        self._mxfile.find("diagram").set("name", title)
        page_width, page_height = _page_size(self._cells)
        self._graph.set("pageWidth", str(page_width))
        self._graph.set("pageHeight", str(page_height))
        body = ET.tostring(self._mxfile, encoding="unicode")
        return "<?xml version='1.0' encoding='utf-8'?>\n" + body


def _document_ordered_aggregates(context: BoundedContext) -> List[Aggregate]:
    aggregates = [item for item in context.aggregates if isinstance(item, Aggregate)]
    return sorted(aggregates, key=lambda aggregate: float(aggregate.sequential_order or 0))


def _ordered_aggregates(
    context: BoundedContext,
    aggregate_order: Optional[List[str]],
) -> List[Aggregate]:
    aggregates = _document_ordered_aggregates(context)
    if not aggregate_order:
        return aggregates
    by_name = {aggregate.name: aggregate for aggregate in aggregates}
    ordered = [by_name[name] for name in aggregate_order if name in by_name]
    seen = {aggregate.name for aggregate in ordered}
    ordered.extend(aggregate for aggregate in aggregates if aggregate.name not in seen)
    return ordered


def _layout_context_positions(
    contexts: List[BoundedContext],
    links: List[_IntegrationLink],
    hub: str,
) -> Dict[str, Tuple[int, int]]:
    if not contexts:
        return {}
    if len(contexts) == 1:
        return {contexts[0].name: (_CONTEXT_GAP, _CONTEXT_GAP)}
    by_name = {context.name: context for context in contexts}
    hub_context = by_name[hub]
    left_x = _CONTEXT_GAP
    hub_x = left_x + _CONTEXT_WIDTH + _CONTEXT_COL_GAP
    right_x = hub_x + _CONTEXT_WIDTH + _CONTEXT_COL_GAP
    peripheral_names = [name for name in by_name if name != hub]
    if not peripheral_names:
        return {hub: (hub_x, _CONTEXT_GAP)}
    rel_anchors = _peripheral_relative_anchors(hub_context, links, hub)
    left_names, right_names = _split_sides_by_height(peripheral_names, rel_anchors)
    positions: Dict[str, Tuple[int, int]] = {}
    estimate_y = _estimate_hub_y(by_name, peripheral_names, rel_anchors)
    positions.update(_place_side_column(left_names, by_name, rel_anchors, estimate_y, left_x))
    positions.update(_place_side_column(right_names, by_name, rel_anchors, estimate_y, right_x))
    hub_y = _centered_hub_y(positions, peripheral_names, by_name, hub_context)
    positions.update(_place_side_column(left_names, by_name, rel_anchors, float(hub_y), left_x))
    positions.update(_place_side_column(right_names, by_name, rel_anchors, float(hub_y), right_x))
    hub_y = _centered_hub_y(positions, peripheral_names, by_name, hub_context)
    positions[hub] = (hub_x, hub_y)
    return positions


def _integration_graph(
    contexts: List[BoundedContext],
) -> Tuple[Dict[str, set[str]], List[_IntegrationLink]]:
    names = {context.name for context in contexts}
    outgoing: Dict[str, set[str]] = {name: set() for name in names}
    links: List[_IntegrationLink] = []
    for context in contexts:
        for aggregate in context.aggregates:
            if not isinstance(aggregate, MarkdownAggregate):
                continue
            for integration in aggregate.integrations:
                target_context = _integration_context_name(integration, contexts)
                if target_context and target_context in names and target_context != context.name:
                    outgoing[context.name].add(target_context)
                    _, aggregate_name, entity_name = _parse_integration_target(integration.target)
                    if integration.aggregate:
                        aggregate_name = integration.aggregate
                    links.append(
                        _IntegrationLink(
                            src_context=context.name,
                            src_aggregate=aggregate.name,
                            tgt_context=target_context,
                            tgt_aggregate=aggregate_name,
                            tgt_entity=entity_name,
                        )
                    )
    return outgoing, links


def _hub_context(contexts: List[BoundedContext], outgoing: Dict[str, set[str]]) -> str:
    incoming: Dict[str, int] = {context.name: 0 for context in contexts}
    for targets in outgoing.values():
        for target in targets:
            incoming[target] = incoming.get(target, 0) + 1

    def score(name: str) -> Tuple[int, int, int]:
        context = next(item for item in contexts if item.name == name)
        return (len(outgoing[name]), incoming.get(name, 0), -(context.sequential_order or 0))

    return max((context.name for context in contexts), key=score)


def _aggregate_center_offsets(context: BoundedContext) -> Dict[str, float]:
    offsets: Dict[str, float] = {}
    y = float(_CONTEXT_HEADER + _CONTEXT_INSET)
    for aggregate in _document_ordered_aggregates(context):
        bullets = _bullet_members(aggregate)
        height = float(_aggregate_height(len(bullets)))
        offsets[aggregate.name] = y + height / 2.0
        y += height + _AGG_GAP
    return offsets


def _peripheral_relative_anchors(
    hub_context: BoundedContext,
    links: List[_IntegrationLink],
    hub_name: str,
) -> Dict[str, float]:
    centers = _aggregate_center_offsets(hub_context)
    anchors: Dict[str, List[float]] = {}
    for link in links:
        if link.src_context != hub_name:
            continue
        anchor = centers.get(link.src_aggregate, float(_CONTEXT_HEADER))
        anchors.setdefault(link.tgt_context, []).append(anchor)
    return {name: sum(values) / len(values) for name, values in anchors.items()}


def _split_sides_by_height(
    peripheral_names: List[str],
    rel_anchors: Dict[str, float],
) -> Tuple[List[str], List[str]]:
    ordered = sorted(peripheral_names, key=lambda name: rel_anchors.get(name, 0.0))
    midpoint = (len(ordered) + 1) // 2
    return ordered[:midpoint], ordered[midpoint:]


def _aggregate_render_orders(
    contexts: List[BoundedContext],
    links: List[_IntegrationLink],
    hub: str,
    positions: Dict[str, Tuple[int, int]],
) -> Dict[str, List[str]]:
    by_name = {context.name: context for context in contexts}
    orders: Dict[str, List[str]] = {}
    hub_context = by_name[hub]
    hub_aggregates = [item for item in hub_context.aggregates if isinstance(item, Aggregate)]
    peripheral_centers = {
        name: positions[name][1] + _context_height(by_name[name]) / 2.0
        for name in positions
        if name != hub
    }
    hub_scores: Dict[str, List[float]] = {}
    for link in links:
        if link.src_context != hub:
            continue
        center = peripheral_centers.get(link.tgt_context)
        if center is not None:
            hub_scores.setdefault(link.src_aggregate, []).append(center)

    def hub_sort_key(aggregate: Aggregate) -> tuple[float, float]:
        scores = hub_scores.get(aggregate.name, [])
        hub_rank = sum(scores) / len(scores) if scores else 999.0
        return (hub_rank, float(aggregate.sequential_order or 0))

    orders[hub] = [aggregate.name for aggregate in sorted(hub_aggregates, key=hub_sort_key)]
    hub_rank = {name: index for index, name in enumerate(orders[hub])}

    for context in contexts:
        if context.name == hub:
            continue
        aggregates = [item for item in context.aggregates if isinstance(item, Aggregate)]
        target_ranks: Dict[str, float] = {}
        for link in links:
            if link.src_context != hub or link.tgt_context != context.name:
                continue
            target_name = _link_target_name(link, aggregates)
            if target_name is None:
                continue
            rank = float(hub_rank.get(link.src_aggregate, 999))
            prior = target_ranks.get(target_name, 999.0)
            target_ranks[target_name] = min(prior, rank)

        def peripheral_sort_key(aggregate: Aggregate) -> tuple[float, float]:
            hub_rank = target_ranks.get(aggregate.name, 999.0)
            return (hub_rank, float(aggregate.sequential_order or 0))

        orders[context.name] = [
            aggregate.name for aggregate in sorted(aggregates, key=peripheral_sort_key)
        ]
    return orders


def _link_target_name(link: _IntegrationLink, aggregates: List[Aggregate]) -> Optional[str]:
    candidates = [link.tgt_aggregate, link.tgt_entity]
    aggregate_names = {aggregate.name.lower() for aggregate in aggregates}
    for candidate in candidates:
        if candidate and candidate.lower() in aggregate_names:
            return next(
                aggregate.name for aggregate in aggregates if aggregate.name.lower() == candidate.lower()
            )
    if link.tgt_entity:
        for aggregate in aggregates:
            if _names_match(aggregate.name, link.tgt_entity):
                return aggregate.name
    if link.tgt_aggregate:
        for aggregate in aggregates:
            if _names_match(aggregate.name, link.tgt_aggregate):
                return aggregate.name
    return None


def _place_side_column(
    names: List[str],
    by_name: Dict[str, BoundedContext],
    rel_anchors: Dict[str, float],
    hub_y: float,
    x: int,
) -> Dict[str, Tuple[int, int]]:
    if not names:
        return {}
    positions: Dict[str, Tuple[int, int]] = {}
    ordered = sorted(names, key=lambda name: rel_anchors.get(name, 0.0))
    ideal_tops: List[float] = []
    for name in ordered:
        height = float(_context_height(by_name[name]))
        relative = rel_anchors.get(name, height / 2.0)
        ideal_tops.append(hub_y + relative - height / 2.0)
    y_cursor = max(float(_CONTEXT_GAP), min(ideal_tops))
    for index, name in enumerate(ordered):
        height = float(_context_height(by_name[name]))
        y = max(ideal_tops[index], y_cursor)
        positions[name] = (x, int(y))
        y_cursor = y + height + _SIDE_MIN_GAP
    return positions


def _estimate_hub_y(
    by_name: Dict[str, BoundedContext],
    peripheral_names: List[str],
    rel_anchors: Dict[str, float],
) -> float:
    if not rel_anchors:
        return float(_CONTEXT_GAP)
    anchor_span = max(rel_anchors.values()) - min(rel_anchors.values())
    peripheral_span = sum(_context_height(by_name[name]) + _SIDE_MIN_GAP for name in peripheral_names)
    return float(_CONTEXT_GAP) + max(anchor_span, float(peripheral_span)) / 4.0


def _centered_hub_y(
    positions: Dict[str, Tuple[int, int]],
    peripheral_names: List[str],
    by_name: Dict[str, BoundedContext],
    hub_context: BoundedContext,
) -> int:
    tops = [positions[name][1] for name in peripheral_names]
    bottoms = [positions[name][1] + _context_height(by_name[name]) for name in peripheral_names]
    side_top = min(tops)
    side_bottom = max(bottoms)
    hub_height = _context_height(hub_context)
    centered = int((side_top + side_bottom) / 2 - hub_height / 2)
    return max(_CONTEXT_GAP, centered)


def _context_height(context: BoundedContext) -> int:
    agg_y = _CONTEXT_HEADER + _CONTEXT_INSET
    for aggregate in _document_ordered_aggregates(context):
        bullets = _bullet_members(aggregate)
        agg_y += _aggregate_height(len(bullets)) + _AGG_GAP
    return agg_y + _CONTEXT_INSET


def _integration_context_name(integration: Integration, contexts: List[BoundedContext]) -> str:
    if integration.context:
        matched = _match_context(integration.context, contexts)
        return matched.name if matched else ""
    context_name, _, _ = _parse_integration_target(integration.target)
    if not context_name:
        return ""
    matched = _match_context(context_name, contexts)
    return matched.name if matched else ""


def _parse_integration_target(target: str) -> Tuple[str, str, str]:
    text = target.strip()
    if text.startswith("\u2192"):
        text = text[1:].strip()
    elif text.startswith("->"):
        text = text[2:].strip()
    parts = [part.strip() for part in _ARROW_SPLIT.split(text) if part.strip()]
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    if len(parts) == 2:
        return parts[0], parts[1], ""
    if len(parts) == 1:
        return "", "", parts[0]
    return "", "", ""


def _match_context(name: str, contexts: List[BoundedContext]) -> Optional[BoundedContext]:
    key = name.strip().lower()
    for context in contexts:
        plain = context.name.split("|", 1)[0].strip().lower()
        if plain == key or context.name.lower() == key:
            return context
        if plain.startswith(key) or key.startswith(plain):
            return context
    return None


def _resolve_target_aggregate(
    aggregate_ids: Dict[Tuple[str, str], str],
    integration: Integration,
    context_ids: Dict[str, str],
) -> Optional[str]:
    context_name = integration.context
    aggregate_name = integration.aggregate
    entity_name = ""
    if not context_name and not aggregate_name:
        context_name, aggregate_name, entity_name = _parse_integration_target(integration.target)
    elif not entity_name:
        _, _, entity_name = _parse_integration_target(integration.target)
    if not entity_name and integration.target and not context_name:
        entity_name = integration.target
    if context_name:
        matched_context = None
        for name in context_ids:
            if _names_match(context_name, name):
                matched_context = name
                break
        if matched_context is None:
            return _resolve_global_aggregate(aggregate_ids, aggregate_name or entity_name)
        return _resolve_aggregate_in_context(
            matched_context,
            aggregate_ids,
            aggregate_name,
            entity_name,
        )
    return _resolve_global_aggregate(aggregate_ids, aggregate_name or entity_name)


def _resolve_global_aggregate(
    aggregate_ids: Dict[Tuple[str, str], str],
    name: str,
) -> Optional[str]:
    if not name:
        return None
    key = name.strip().lower()
    for (_context_name, aggregate_name), cell_id in aggregate_ids.items():
        if aggregate_name.lower() == key:
            return cell_id
    return None


def _resolve_aggregate_in_context(
    context_name: str,
    aggregate_ids: Dict[Tuple[str, str], str],
    aggregate_name: str,
    entity_name: str,
) -> Optional[str]:
    for candidate in (entity_name, aggregate_name):
        if not candidate:
            continue
        for (ctx, agg), cell_id in aggregate_ids.items():
            if ctx == context_name and _names_match(agg, candidate):
                return cell_id
    return None


def _names_match(left: str, right: str) -> bool:
    return left.strip().lower() == right.strip().lower()


def _absolute_bounds(cells: Dict[str, _CellRecord], cell_id: str) -> Tuple[float, float, float, float]:
    record = cells[cell_id]
    x, y = record.x, record.y
    parent_id = record.parent_id
    while parent_id not in {"", "0", "1"} and parent_id in cells:
        parent = cells[parent_id]
        x += parent.x
        y += parent.y
        parent_id = parent.parent_id
    return (x, y, record.width, record.height)


def _box_center_y(box: Tuple[float, float, float, float]) -> float:
    _, y, _, height = box
    return y + height / 2.0


def _anchor_fractions(count: int) -> List[float]:
    if count <= 1:
        return [0.5]
    return [round(0.15 + 0.7 * index / (count - 1), 3) for index in range(count)]


def _plan_straight_routes(
    placements: Dict[str, Tuple[float, float, float, float]],
    plans: List[_EdgePlan],
) -> List[dict]:
    if not plans:
        return []
    sorted_plans = sorted(
        plans,
        key=lambda plan: (
            _box_center_y(placements[plan.tgt_id]) + _box_center_y(placements[plan.src_id])
        )
        / 2.0,
    )
    source_groups: Dict[str, List[_EdgePlan]] = {}
    target_groups: Dict[str, List[_EdgePlan]] = {}
    for plan in sorted_plans:
        source_groups.setdefault(plan.src_id, []).append(plan)
        target_groups.setdefault(plan.tgt_id, []).append(plan)
    for group in source_groups.values():
        group.sort(key=lambda plan: _box_center_y(placements[plan.tgt_id]))
    for group in target_groups.values():
        group.sort(key=lambda plan: _box_center_y(placements[plan.src_id]))
    source_fracs: Dict[Tuple[str, str], float] = {}
    target_fracs: Dict[Tuple[str, str], float] = {}
    for group in source_groups.values():
        for frac, plan in zip(_anchor_fractions(len(group)), group):
            source_fracs[(plan.src_id, plan.tgt_id)] = frac
    for group in target_groups.values():
        for frac, plan in zip(_anchor_fractions(len(group)), group):
            target_fracs[(plan.src_id, plan.tgt_id)] = frac
    routes: List[dict] = []
    for plan in sorted_plans:
        source = placements[plan.src_id]
        target = placements[plan.tgt_id]
        if source[0] >= target[0]:
            exit_x, entry_x = 0.0, 1.0
        else:
            exit_x, entry_x = 1.0, 0.0
        routes.append(
            {
                "src_id": plan.src_id,
                "tgt_id": plan.tgt_id,
                "label": plan.label,
                "exit_x": exit_x,
                "exit_y": source_fracs[(plan.src_id, plan.tgt_id)],
                "entry_x": entry_x,
                "entry_y": target_fracs[(plan.src_id, plan.tgt_id)],
            }
        )
    return routes


def _page_size(cells: Dict[str, _CellRecord]) -> Tuple[int, int]:
    max_x = 0.0
    max_y = 0.0
    for cell_id in cells:
        x, y, width, height = _absolute_bounds(cells, cell_id)
        max_x = max(max_x, x + width)
        max_y = max(max_y, y + height)
    return (int(max_x + _PAGE_MARGIN), int(max_y + _PAGE_MARGIN))


def _aggregate_height(bullet_count: int) -> int:
    base = _AGG_TITLE_BLOCK + _AGG_TOP_PAD + _AGG_BOTTOM_PAD
    if bullet_count <= 0:
        return base
    return base + _BULLET_UL_TOP + bullet_count * _BULLET_LINE


def _bullet_members(aggregate: Aggregate) -> list[str]:
    members = _member_labels(aggregate)
    if members and _plain_entity_name(members[0]).lower() == aggregate.name.lower():
        return [_plain_entity_name(member) for member in members[1:]]
    return [_plain_entity_name(member) for member in members]


def _context_label(context: BoundedContext) -> str:
    name = _escape(context.name)
    wrap = "word-wrap:break-word;overflow-wrap:break-word;"
    if not context.owner:
        return (
            f'<div style="font-size:{_CONTEXT_TITLE_FONT}px;line-height:1.15;'
            f'font-weight:bold;text-align:center;{wrap}">{name}</div>'
        )
    owner = _escape(context.owner)
    return (
        f'<div style="font-size:{_CONTEXT_TITLE_FONT}px;line-height:1.15;text-align:center;{wrap}">'
        f'<div style="font-weight:bold;">{name}</div>'
        f'<div style="font-size:{_CONTEXT_OWNER_FONT}px;opacity:0.9;">{owner}</div>'
        f"</div>"
    )


def _aggregate_label(aggregate: Aggregate, bullets: list[str]) -> str:
    title = _escape(aggregate.name)
    title_style = (
        f"margin:0;font-size:{_AGG_TITLE_FONT}px;line-height:1.1;font-weight:bold;"
        f"word-wrap:break-word;overflow-wrap:break-word;"
    )
    if not bullets:
        return f'<p style="{title_style}">{title}</p>'
    items = "".join(
        f'<li style="margin:0;padding:0;line-height:1.1;">{_escape(name)}</li>'
        for name in bullets
    )
    return (
        f'<p style="{title_style}">{title}</p>'
        f'<ul style="margin:{_BULLET_UL_TOP}px 0 0 8px;padding:0;font-size:{_BULLET_FONT}px;'
        f'line-height:1.1;list-style-position:outside;">'
        f"{items}</ul>"
    )


def _member_labels(aggregate: Aggregate) -> list[str]:
    if not isinstance(aggregate, MarkdownAggregate) or aggregate.root is None:
        return [aggregate.name]
    labels: list[str] = []
    root_line = aggregate.root.name.strip()
    root_name = root_line.split(" - ", 1)[0].strip()
    if root_line:
        labels.append(root_line)
    seen = {root_name.lower()}
    for item in aggregate.root.invariant_objects:
        name = item.name.strip()
        if not name or name.lower().startswith("note:"):
            continue
        plain = name.split("//", 1)[0].strip()
        if not plain or plain.lower() in seen:
            continue
        if _looks_like_prose(plain) or _looks_like_operation(plain):
            continue
        seen.add(plain.lower())
        labels.append(plain)
        if len(labels) >= _MAX_MEMBERS:
            break
    return labels or [aggregate.name]


def _plain_entity_name(label: str) -> str:
    return label.split(" - ", 1)[0].strip()


def _looks_like_operation(line: str) -> bool:
    if not line or " " in line:
        return False
    if line.endswith(":"):
        return False
    return line[0].islower()


def _looks_like_prose(line: str) -> bool:
    text = line.strip()
    if not text:
        return True
    if text.lower().startswith("note:"):
        return True
    if ". " in text or text.endswith("."):
        return True
    if text[0].islower():
        return True
    return False


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
