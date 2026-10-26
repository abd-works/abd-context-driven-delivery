"""DrawIO aggregate view — the model fidelity's picture of the core domain.

Bounded contexts and aggregates are containers. Each aggregate holds its root card, which carries the root's
repository below its domain operations, and the members the root composes. Arrows run only where one aggregate
needs another. Golden example: pml-web `src/.context/bounded-context-key-entities-with-operations.drawio`.
"""

from __future__ import annotations

import re
from html import escape
from typing import Dict, List, Optional, Tuple

from cdd_guidance.practices.ddd.model.markdown.class_cards import ClassCard, plain_properties

_CONTEXT_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;dashed=1;dashPattern=8 8;"
    "strokeColor=#666666;strokeWidth=1;fontColor=#333333;arcSize=5;"
)
_AGGREGATE_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#CCCCCC;dashed=1;dashPattern=8 8;"
    "strokeColor=#666666;strokeWidth=1;fontColor=#333333;arcSize=8;"
)
_TITLE_STYLE = "text;html=1;fontStyle=1;fontSize=17;fontFamily=Helvetica;align=left;verticalAlign=middle;"
_CARD_STYLE = (
    "verticalAlign=top;align=left;overflow=fill;fontSize=12;fontFamily=Helvetica;html=1;whiteSpace=wrap;"
    "fillColor=#f5f5f5;fontColor=#333333;strokeColor=#666666;strokeWidth=3;"
)
_COMPOSITION_STYLE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=none;html=1;startArrow=diamondThin;startFill=1;startSize=14;"
)
_DEPENDENCY_STYLE = "edgeStyle=orthogonalEdgeStyle;rounded=1;endArrow=open;endSize=12;html=1;"
_STEREOTYPE_LINE = '<p style="margin:0px;margin-top:2px;text-align:center;font-size:10px;"><i>«{}»</i></p>'
_NAME_LINE = '<p style="margin:0px;text-align:center;"><b>{}</b></p>'
_REPOSITORY_NAME_LINE = '<p style="margin:0px;text-align:center;font-size:10px;"><b>{}</b></p>'
_MEMBERS_LINE = '<p style="margin:0px;margin-left:4px;font-size:10px;">{}</p>'
_RULE = '<hr size="1"/>'

_PAD = 40
_TITLE = 50
_GAP = 40
_ROOT_WIDTH = 300
_MEMBER_WIDTH = 240
_LINE = 14
_CARD_HEAD = 36
_AGGREGATES_PER_ROW = 3
_CALL = re.compile(r"^([A-Z]\w*?)(?:Repository)?\.")


class _Cell:
    def __init__(self, cell_id: str, value: str, style: str, box: Tuple[float, float, float, float]) -> None:
        self.cell_id = cell_id
        self.value = value
        self.style = style
        self.box = box

    def xml(self) -> str:
        x, y, width, height = self.box
        return (
            f'<mxCell id="{self.cell_id}" value="{escape(self.value)}" style="{self.style}" parent="1" vertex="1">'
            f'<mxGeometry x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" as="geometry"/></mxCell>'
        )


class DrawIOAggregateModel:
    """Writes the aggregate view for a bounded-context map whose aggregates carry class cards."""

    def __init__(self) -> None:
        self._cells: List[_Cell] = []
        self._edges: List[str] = []
        self._card_ids: Dict[str, str] = {}
        self._root_ids: Dict[str, str] = {}
        self._next = 0

    def render(self, model) -> str:
        columns = [0.0, 0.0]
        widths = [0.0, 0.0]
        placed = []
        for context in model.contexts:
            layout = self._layout_context(context)
            column = 0 if columns[0] <= columns[1] else 1
            placed.append((context, layout, column, columns[column]))
            columns[column] += layout[1] + _GAP
            widths[column] = max(widths[column], layout[0])
        for context, layout, column, top in placed:
            left = _PAD + (0 if column == 0 else widths[0] + _GAP * 2)
            self._draw_context(context, layout, left, _PAD + top)
        for context, _layout, _column, _top in placed:
            for aggregate in _aggregates(context):
                self._draw_edges(aggregate)
        return self._document(model)

    def _layout_context(self, context) -> Tuple[float, float, list]:
        rows: list = []
        for index, aggregate in enumerate(_aggregates(context)):
            if index % _AGGREGATES_PER_ROW == 0:
                rows.append([])
            rows[-1].append((aggregate, _aggregate_size(aggregate)))
        width = max((sum(size[0] for _, size in row) + _GAP * (len(row) - 1) for row in rows), default=_ROOT_WIDTH)
        height = sum(max(size[1] for _, size in row) for row in rows) + _GAP * max(len(rows) - 1, 0)
        return width + _PAD * 2, height + _TITLE + _PAD, rows

    def _draw_context(self, context, layout, left: float, top: float) -> None:
        width, height, rows = layout
        self._add(f"ctx-{_slug(context.name)}", "", _CONTEXT_STYLE, (left, top, width, height))
        self._add(f"t-ctx-{_slug(context.name)}", context.name, _TITLE_STYLE, (left + 20, top + 10, 300, 30))
        y = top + _TITLE
        for row in rows:
            x = left + _PAD
            for aggregate, size in row:
                self._draw_aggregate(aggregate, x, y, size)
                x += size[0] + _GAP
            y += max(size[1] for _, size in row) + _GAP

    def _draw_aggregate(self, aggregate, left: float, top: float, size: Tuple[float, float]) -> None:
        self._add(f"agg-{_slug(aggregate.name)}", "", _AGGREGATE_STYLE, (left, top, size[0], size[1]))
        self._add(f"t-agg-{_slug(aggregate.name)}", aggregate.name, _TITLE_STYLE, (left + 20, top + 8, 260, 30))
        root, repository, members = _split(aggregate)
        y = top + _TITLE
        if root is not None:
            height = _card_height(root, repository)
            cell = self._add(f"card-{_slug(root.node.name)}", _card_html(root, repository), _CARD_STYLE,
                             (left + _PAD, y, _ROOT_WIDTH, height))
            self._card_ids[root.node.name] = cell
            self._root_ids[root.node.name] = cell
            self._root_ids[aggregate.name] = cell
        x = left + _PAD + (_ROOT_WIDTH + _GAP if root is not None else 0)
        for member in members:
            height = _card_height(member, None)
            cell = self._add(f"card-{_slug(aggregate.name)}-{_slug(member.node.name)}", _card_html(member, None),
                             _CARD_STYLE, (x, y, _MEMBER_WIDTH, height))
            self._card_ids.setdefault(member.node.name, cell)
            y += height + _GAP

    def _draw_edges(self, aggregate) -> None:
        root, repository, members = _split(aggregate)
        if root is None:
            return
        local = {card.node.name for card in members} | {root.node.name}
        composed = set()
        for card in [root] + members:
            for prop in card.node.properties:
                target = _type_name(getattr(prop, "type_hint", ""))
                if getattr(prop, "stereotype", "") == "composition" and target in local and target != card.node.name:
                    self._edge(card.node.name, target, _COMPOSITION_STYLE, self._card_ids)
                    composed.add(target)
        for member in members:
            if member.node.name not in composed:
                self._edge(root.node.name, member.node.name, _COMPOSITION_STYLE, self._card_ids)
        for card in [root] + members:
            for target in _dependencies(card, local):
                self._edge(card.node.name, target, _DEPENDENCY_STYLE, self._root_ids, source_ids=self._card_ids)
        for integration in aggregate.integrations:
            target = _integration_root(integration)
            if target:
                self._edge(root.node.name, target, _DEPENDENCY_STYLE, self._root_ids, source_ids=self._card_ids)

    def _edge(self, source: str, target: str, style: str, targets: Dict[str, str],
              source_ids: Optional[Dict[str, str]] = None) -> None:
        source_id = (source_ids or self._card_ids).get(source)
        target_id = targets.get(target)
        if not source_id or not target_id or source_id == target_id:
            return
        edge_id = f"e-{source_id}-{target_id}"
        if any(f'id="{edge_id}"' in item for item in self._edges):
            return
        self._edges.append(
            f'<mxCell id="{edge_id}" value="" style="{style}" parent="1" source="{source_id}" target="{target_id}" '
            f'edge="1"><mxGeometry relative="1" as="geometry"/></mxCell>'
        )

    def _add(self, cell_id: str, value: str, style: str, box) -> str:
        self._cells.append(_Cell(cell_id, value, style, box))
        return cell_id

    def _document(self, model) -> str:
        width = max((cell.box[0] + cell.box[2] for cell in self._cells), default=800) + _PAD
        height = max((cell.box[1] + cell.box[3] for cell in self._cells), default=600) + _PAD
        cells = "".join(cell.xml() for cell in self._cells) + "".join(self._edges)
        title = escape(getattr(model, "title", "") or "Aggregates + operations")
        return (
            '<mxfile host="cdd">'
            f'<diagram name="{title}" id="page-aggregates">'
            f'<mxGraphModel grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
            f'pageScale="1" pageWidth="{int(width)}" pageHeight="{int(height)}" math="0" shadow="0">'
            f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{cells}</root>'
            "</mxGraphModel></diagram></mxfile>"
        )


def has_class_cards(model) -> bool:
    return any(getattr(aggregate, "cards", None) for context in model.contexts for aggregate in _aggregates(context))


def _aggregates(context) -> list:
    found = list(context.aggregates)
    for child in context.contexts:
        found.extend(_aggregates(child))
    return found


def _split(aggregate) -> Tuple[Optional[ClassCard], Optional[ClassCard], List[ClassCard]]:
    cards = list(getattr(aggregate, "cards", []) or [])
    root = next((card for card in cards if card.is_root), None)
    repository = next((card for card in cards if card.is_repository), None)
    members = [card for card in cards if card is not root and card is not repository]
    return root, repository, members


def _aggregate_size(aggregate) -> Tuple[float, float]:
    root, repository, members = _split(aggregate)
    root_height = _card_height(root, repository) if root is not None else 0
    members_height = sum(_card_height(card, None) + _GAP for card in members) - (_GAP if members else 0)
    width = _PAD * 2 + (_ROOT_WIDTH if root is not None else 0) + ((_GAP + _MEMBER_WIDTH) if members else 0)
    return width, _TITLE + max(root_height, members_height) + _PAD


def _card_height(card: ClassCard, repository: Optional[ClassCard]) -> float:
    lines = len(card.stereotypes) + max(len(_properties(card)), 1) + max(len(card.node.operations), 1)
    height = _CARD_HEAD + lines * _LINE
    if repository is not None:
        height += _CARD_HEAD + max(len(repository.node.operations), 1) * _LINE
    return height


def _card_html(card: ClassCard, repository: Optional[ClassCard]) -> str:
    parts = [_STEREOTYPE_LINE.format(escape(item)) for item in card.stereotypes]
    parts.append(_NAME_LINE.format(escape(card.node.name)))
    parts.append(_RULE)
    parts.append(_MEMBERS_LINE.format("<br/>".join(escape(_property_text(prop)) for prop in _properties(card))))
    parts.append(_RULE)
    parts.append(_MEMBERS_LINE.format("<br/>".join(escape(_operation_text(item)) for item in card.node.operations)))
    if repository is not None:
        parts.append(_RULE)
        parts.append(_STEREOTYPE_LINE.format("Repository"))
        parts.append(_REPOSITORY_NAME_LINE.format(escape(repository.node.name)))
        parts.append(_RULE)
        parts.append(_MEMBERS_LINE.format(
            "<br/>".join(escape(_operation_text(item)) for item in repository.node.operations)
        ))
    return "".join(parts)


def _properties(card: ClassCard) -> list:
    return plain_properties(card.node)


def _property_text(prop) -> str:
    typed = f": {prop.type_hint}" if prop.type_hint else ""
    return f"+ {prop.name}{typed}"


def _operation_text(operation) -> str:
    names = ", ".join(item.name for item in operation.parameters)
    return f"+ {operation.name}({names})"


def _type_name(type_hint: str) -> str:
    return re.split(r"[\[\]<>|\s]", (type_hint or "").strip())[0] if type_hint else ""


def _dependencies(card: ClassCard, local: set[str]) -> List[str]:
    found: List[str] = []
    for operation in card.node.operations:
        for callee in operation.callees:
            match = _CALL.match(callee.strip())
            if match and match.group(1) not in local:
                found.append(match.group(1))
    for prop in card.node.properties:
        target = _type_name(getattr(prop, "type_hint", ""))
        if getattr(prop, "stereotype", "") == "association" and target and target[0].isupper() and target not in local:
            found.append(target)
    return found


def _integration_root(integration) -> str:
    target = (integration.target or "").replace("→", "").replace("->", "")
    parts = [part.strip() for part in re.split(r"[·•]", target) if part.strip()]
    if not parts:
        return ""
    return parts[-1].split("(", 1)[0].strip()


def _slug(name: str) -> str:
    return re.sub(r"[^0-9a-z]+", "-", name.lower()).strip("-") or "x"
