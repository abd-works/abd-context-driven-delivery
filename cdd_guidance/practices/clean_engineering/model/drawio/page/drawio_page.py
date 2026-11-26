"""A class diagram's page over the framework's draw.io page (harness/drawio), and what one cell of it says: a class
card's title, or an edge's kind, anchors, and route. The Clean Engineering class model and the layout scanners both read
draw.io through these."""

from __future__ import annotations

import html
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from harness.drawio import CellStyle, DrawioCell, DrawioPage
from harness.whiteboard import Box
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Point, Segment, segments_cross

# A segment counts as horizontal or vertical when it moves less than this many pixels across.
STRAIGHT_TOLERANCE = 1
# How much of a class title a scanner's message quotes, so a long title does not swamp the report.
QUOTED_TITLE_CHARS = 80



class ClassDiagramPage:
    """One page of a class diagram, read over the framework's draw.io page (``page``): the class boxes on it, and the
    edges between them with their kinds, anchors, and routes, which are the class diagram's own. The Clean Engineering
    class model reads a diagram, and keeps the positions of the one it replaces, through it, and so does each layout
    scanner."""

    def __init__(self, page: DrawioPage, file_path: Path | None = None) -> None:
        self.page = page
        self.file_path = file_path
        self.name = page.name
        self.cells = [_as_one_cell(cell) for cell in page.cells]
        self.vertices = [cell for cell in self.cells if cell.get('vertex') == '1']
        self.edges = [cell for cell in self.cells if cell.get('edge') == '1']
        self.boxes: dict[str, Box] = {}
        self.class_names: dict[str, str] = {}
        for cell in self.vertices:
            name_in_cell = class_name_in(cell.get('value', ''))
            box = DrawioCell(cell).box
            if name_in_cell and box:
                self.boxes[cell.get('id')] = box
                self.class_names[cell.get('id')] = name_in_cell

    def edges_by_ends(self) -> dict[tuple[str, str], ET.Element]:
        """Each edge that joins two cells, by its source and target cell ids."""
        return {(edge.get('source'), edge.get('target')): edge for edge in self.edges if edge.get('source') and edge.get('target')}

    def kind_of(self, edge: ET.Element) -> str:
        """The UML relationship an edge draws: inheritance, composition, aggregation, dependency, or association."""
        return edge_kind(edge.get('style', ''))

    def describe(self, edge: ET.Element) -> str:
        """`Source->Target (kind)`, the way every edge message names the edge."""
        source = self.class_names.get(edge.get('source', ''), '?')
        target = self.class_names.get(edge.get('target', ''), '?')
        kind = self.kind_of(edge)
        drawn = f"{kind}-orthogonal" if kind in {'inheritance', 'dependency'} and 'orthogonalEdgeStyle' in edge.get('style', '') else kind
        return f"{source}->{target} ({drawn})"

    def segments(self, edge: ET.Element) -> tuple[list[Segment], bool]:
        """The polyline an edge draws, and whether it is a guess.

        Straight edges run anchor to anchor. Orthogonal edges follow their waypoints, turning at right angles; without
        waypoints Draw.io's router picks the route, so the middle-split route returned here is only an approximation."""
        style = edge.get('style', '')
        source_box = self.boxes.get(edge.get('source', ''))
        target_box = self.boxes.get(edge.get('target', ''))
        if source_box is None or target_box is None:
            return ([], False)
        start = anchor_point(style, source_box, 'exit')
        end = anchor_point(style, target_box, 'entry')
        if 'orthogonal' not in style.lower():
            return ([(start, end)], False)
        return self._orthogonal_route(edge, (start, end))

    def _orthogonal_route(self, edge: ET.Element, ends: Segment) -> tuple[list[Segment], bool]:
        """An orthogonal edge's route through its waypoints, or, with none, the middle-split guess at Draw.io's own."""
        start, end = ends
        waypoints = [(float(point.get('x', '0')), float(point.get('y', '0'))) for point in edge.findall('mxGeometry/Array/mxPoint')]
        if waypoints:
            return (self._orthogonal_through([start] + waypoints + [end]), False)
        if abs(end[0] - start[0]) < STRAIGHT_TOLERANCE or abs(end[1] - start[1]) < STRAIGHT_TOLERANCE:
            return ([(start, end)], False)
        middle_x = (start[0] + end[0]) / 2
        return ([(start, (middle_x, start[1])), ((middle_x, start[1]), (middle_x, end[1])), ((middle_x, end[1]), end)], True)

    def _orthogonal_through(self, points: list[Point]) -> list[Segment]:
        """Segments through each point in turn, adding a corner wherever two points are not in line."""
        expanded = [points[0]]
        previous_direction = None
        for following in points[1:]:
            corners, previous_direction = self._orthogonal_step((expanded[-1], following), previous_direction)
            expanded.extend(corners)
        return list(zip(expanded, expanded[1:]))

    def _orthogonal_step(self, leg: Segment, previous_direction: str | None) -> tuple[list[Point], str]:
        """The points after the leg's start that reach its end at right angles, turning away from the previous
        segment's direction."""
        start, end = leg
        if abs(end[0] - start[0]) < STRAIGHT_TOLERANCE or abs(end[1] - start[1]) < STRAIGHT_TOLERANCE:
            return ([end], 'v' if abs(end[0] - start[0]) < STRAIGHT_TOLERANCE else 'h')
        if previous_direction == 'v':
            return ([(start[0], end[1]), end], 'h')
        return ([(end[0], start[1]), end], 'v')



def _as_one_cell(cell: DrawioCell) -> ET.Element:
    """The cell as one mxCell with its id and words on it: a linked cell keeps them on the UserObject round it, so it is
    read as a copy that carries them, and every reader of the page reads both kinds alike."""
    element = cell.element
    if element.get('id') is not None:
        return element
    whole = ET.Element('mxCell', attrib={**element.attrib, 'id': cell.id, 'value': cell.label})
    whole.extend(list(element))
    return whole


def class_title_in(cell_label: str) -> str | None:
    """The raw HTML inside the class cell's `<b>` title, or None for a cell with no title."""
    if not cell_label:
        return None
    match = re.search('<b[^>]*>(.*?)</b>', html.unescape(html.unescape(cell_label)), re.IGNORECASE | re.DOTALL)
    return match.group(1) if match else None


def quoted_title(title: str) -> str:
    """A class title as a message quotes it: its words without HTML tags, cut to QUOTED_TITLE_CHARS."""
    return re.sub(r'<[^>]+>', '', title)[:QUOTED_TITLE_CHARS]


def class_name_in(cell_label: str) -> str | None:
    """The class name in a class cell's title; a stereotype or ` : Base` beside it is not part of the name."""
    if not cell_label:
        return None
    # `<b>` or `<b style=...>`, never the `<br/>` that ends a stereotype line above the name.
    match = re.search(r'<b(?:\s[^>]*)?>(.*?)</b>', html.unescape(cell_label), re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    name = re.sub('\\s+', ' ', match.group(1)).strip()
    return name.split(' : ')[0].strip() or None


def edge_kind(style: str) -> str:
    """The UML relationship an edge style draws; an edge with no UML marks is an association."""
    if 'endFill=0' in style and 'endArrow=block' in style:
        return 'inheritance'
    if 'startFill=1' in style and 'diamondThin' in style:
        return 'composition'
    if 'startFill=0' in style and 'diamondThin' in style:
        return 'aggregation'
    if 'dashed=1' in style and 'endArrow=open' in style:
        return 'dependency'
    return 'association'


def is_inheritance(edge: ET.Element) -> bool:
    return edge_kind(edge.get('style', '')) == 'inheritance'


def anchor_fractions(edge: ET.Element, end: str) -> tuple[float | None, float | None]:
    """The `exit` or `entry` anchor fractions an edge's style sets, or None for each one it leaves to Draw.io."""
    style = edge.get('style', '')
    return (CellStyle(style).number(f'{end}X'), CellStyle(style).number(f'{end}Y'))


def share_inheritance_trunk(first: ET.Element, second: ET.Element) -> bool:
    """True when two inheritance edges end at the same anchor on the same base: subclasses joined into one shared
    line to their base, the UML tree style, which draws as one line and one arrowhead."""
    return (
        is_inheritance(first) and is_inheritance(second)
        and first.get('target') == second.get('target')
        and None not in anchor_fractions(first, 'entry')
        and anchor_fractions(first, 'entry') == anchor_fractions(second, 'entry')
    )


def anchor_point(style: str, box: Box, end: str) -> Point:
    """Where one end of an edge meets its box: the exit or entry anchor in the style, else the box centre."""
    fraction_x = CellStyle(style).number(f'{end}X')
    fraction_y = CellStyle(style).number(f'{end}Y')
    if fraction_x is not None and fraction_y is not None:
        return (box.x + box.w * fraction_x, box.y + box.h * fraction_y)
    return box.center


def segment_hits_box(segment: Segment, box: Box, margin: float) -> bool:
    """True when the segment cuts the box grown by margin on every side, or starts inside it."""
    start = segment[0]
    left, top = box.x - margin, box.y - margin
    right, bottom = box.x + box.w + margin, box.y + box.h + margin
    corners = [(left, top), (right, top), (right, bottom), (left, bottom)]
    if any(segments_cross(segment, (corners[index], corners[(index + 1) % 4])) for index in range(4)):
        return True
    return left <= start[0] <= right and top <= start[1] <= bottom
