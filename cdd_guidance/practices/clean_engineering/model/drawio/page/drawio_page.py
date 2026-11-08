"""A draw.io file's diagram pages, and what one cell says: a class card's title and box, or an edge's kind, anchors,
and route. The Clean Engineering class model and the layout scanners both read draw.io through these."""

from __future__ import annotations

import html
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from cdd_guidance.practices.clean_engineering.model.drawio.diagram.geometry import Geometry, Point, Segment, segments_cross

# A segment counts as horizontal or vertical when it moves less than this many pixels across.
STRAIGHT_TOLERANCE = 1



class DrawioPage:
    """One diagram page of a draw.io file: its cells, the class boxes on it, and the edges between them. Every reader of
    draw.io reads its cells through a page: the Clean Engineering class model when it parses a diagram or keeps the
    positions of the one it replaces, and each layout scanner."""

    def __init__(self, file_path: Path | None, name: str, root: ET.Element) -> None:
        self.file_path = file_path
        self.name = name
        self.cells = list(root.iter('mxCell'))
        self.vertices = [cell for cell in self.cells if cell.get('vertex') == '1']
        self.edges = [cell for cell in self.cells if cell.get('edge') == '1']
        self.boxes: dict[str, Geometry] = {}
        self.class_names: dict[str, str] = {}
        for cell in self.vertices:
            name_in_cell = class_name_in(cell.get('value', ''))
            box = cell_box(cell)
            if name_in_cell and box:
                self.boxes[cell.get('id')] = box
                self.class_names[cell.get('id')] = name_in_cell

    @classmethod
    def pages_in(cls, mxfile: ET.Element, file_path: Path | None = None) -> list[DrawioPage]:
        """Each diagram page of a draw.io file that holds a graph model, in file order."""
        pages = []
        for diagram in mxfile.findall('diagram'):
            page_root = diagram.find('mxGraphModel/root')
            if page_root is not None:
                pages.append(cls(file_path, diagram.get('name') or '', page_root))
        return pages

    @classmethod
    def whole(cls, text: str) -> DrawioPage | None:
        """Every cell of a draw.io document read as one page; none for text that is not XML."""
        try:
            return cls(None, '', ET.fromstring(text))
        except ET.ParseError:
            return None

    def cell(self, cell_id: str) -> ET.Element | None:
        """The cell called cell_id on this page; none when the page has no such cell."""
        return next((cell for cell in self.cells if cell.get('id') == cell_id), None)

    def positions(self) -> dict[str, tuple[float, float]]:
        """Where each vertex sits, by cell id."""
        found: dict[str, tuple[float, float]] = {}
        for cell in self.vertices:
            geometry = cell.find('mxGeometry')
            if geometry is None or not cell.get('id'):
                continue
            try:
                found[cell.get('id')] = (float(geometry.get('x')), float(geometry.get('y')))
            except (TypeError, ValueError):
                continue
        return found

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
        waypoints = [(float(point.get('x', '0')), float(point.get('y', '0'))) for point in edge.findall('mxGeometry/Array/mxPoint')]
        if waypoints:
            return (_orthogonal_through([start] + waypoints + [end]), False)
        if abs(end[0] - start[0]) < STRAIGHT_TOLERANCE or abs(end[1] - start[1]) < STRAIGHT_TOLERANCE:
            return ([(start, end)], False)
        middle_x = (start[0] + end[0]) / 2
        return ([(start, (middle_x, start[1])), ((middle_x, start[1]), (middle_x, end[1])), ((middle_x, end[1]), end)], True)



def class_title_in(value: str) -> str | None:
    """The raw HTML inside the class cell's `<b>` title, or None for a cell with no title."""
    if not value:
        return None
    match = re.search('<b[^>]*>(.*?)</b>', html.unescape(html.unescape(value)), re.IGNORECASE | re.DOTALL)
    return match.group(1) if match else None


def class_name_in(value: str) -> str | None:
    """The class name in a class cell's title; a stereotype or ` : Base` beside it is not part of the name."""
    if not value:
        return None
    # `<b>` or `<b style=...>`, never the `<br/>` that ends a stereotype line above the name.
    match = re.search(r'<b(?:\s[^>]*)?>(.*?)</b>', html.unescape(value), re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    name = re.sub('\\s+', ' ', match.group(1)).strip()
    return name.split(' : ')[0].strip() or None


def cell_box(cell: ET.Element) -> Geometry | None:
    """The box a cell's mxGeometry places it in, or None when the cell has none."""
    geometry = cell.find('mxGeometry')
    if geometry is None:
        return None
    return Geometry(float(geometry.get('x', '0')), float(geometry.get('y', '0')), float(geometry.get('width', '0')), float(geometry.get('height', '0')))


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
    return (style_number(style, f'{end}X'), style_number(style, f'{end}Y'))


def share_inheritance_trunk(first: ET.Element, second: ET.Element) -> bool:
    """True when two inheritance edges end at the same anchor on the same base: subclasses joined into one shared
    line to their base, the UML tree style, which draws as one line and one arrowhead."""
    return (
        is_inheritance(first) and is_inheritance(second)
        and first.get('target') == second.get('target')
        and None not in anchor_fractions(first, 'entry')
        and anchor_fractions(first, 'entry') == anchor_fractions(second, 'entry')
    )


def style_number(style: str, key: str) -> float | None:
    """A number set in a Draw.io style string, such as `exitX=0.3`."""
    match = re.search(f'(?:^|;){key}=(-?[0-9.]+)', style)
    return float(match.group(1)) if match else None


def anchor_point(style: str, box: Geometry, end: str) -> Point:
    """Where one end of an edge meets its box: the exit or entry anchor in the style, else the box centre."""
    x, y, width, height = box
    fraction_x = style_number(style, f'{end}X')
    fraction_y = style_number(style, f'{end}Y')
    if fraction_x is not None and fraction_y is not None:
        return (x + width * fraction_x, y + height * fraction_y)
    return box.center


def segment_hits_box(segment: Segment, box: Geometry, margin: float) -> bool:
    """True when the segment cuts the box grown by margin on every side, or starts inside it."""
    start = segment[0]
    left, top = box[0] - margin, box[1] - margin
    right, bottom = box[0] + box[2] + margin, box[1] + box[3] + margin
    corners = [(left, top), (right, top), (right, bottom), (left, bottom)]
    if any(segments_cross(segment, (corners[index], corners[(index + 1) % 4])) for index in range(4)):
        return True
    return left <= start[0] <= right and top <= start[1] <= bottom


def _orthogonal_through(points: list[Point]) -> list[Segment]:
    """Segments through each point in turn, adding a corner wherever two points are not in line."""
    expanded = [points[0]]
    previous_direction = None
    for following in points[1:]:
        corners, previous_direction = _orthogonal_step(expanded[-1], following, previous_direction)
        expanded.extend(corners)
    return list(zip(expanded, expanded[1:]))


def _orthogonal_step(start: Point, end: Point, previous_direction: str | None) -> tuple[list[Point], str]:
    """The points after start that reach end at right angles, turning away from the previous segment's direction."""
    if abs(end[0] - start[0]) < STRAIGHT_TOLERANCE or abs(end[1] - start[1]) < STRAIGHT_TOLERANCE:
        return ([end], 'v' if abs(end[0] - start[0]) < STRAIGHT_TOLERANCE else 'h')
    if previous_direction == 'v':
        return ([(start[0], end[1]), end], 'h')
    return ([(end[0], start[1]), end], 'v')
