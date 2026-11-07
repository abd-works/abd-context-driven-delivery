"""Draw.io layout scanners: each scanner reads the pages of a `.drawio` file and reports one layout rule."""
from __future__ import annotations

import argparse
import html
import importlib
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from harness.graph.violation import Violation
from harness.installation.destination import data_of

DRAWIO_EXTENSIONS = frozenset({'.drawio', '.xml'})
SKIP_DIR_NAMES = frozenset({'node_modules', '.git', 'dist', 'build', 'coverage', '__pycache__', '.venv', 'venv', 'examples'})
_REPAIR_FIXTURE_NAMES = frozenset({'faultyasset', 'repairedasset'})
_REPAIR_FIXTURE_DIRS = frozenset({'faultyassets', 'repairedassets'})
# A segment counts as horizontal or vertical when it moves less than this many pixels across.
STRAIGHT_TOLERANCE = 1

Point = tuple[float, float]
Segment = tuple[Point, Point]
Box = tuple[float, float, float, float]


class DrawioPage:
    """One diagram page of a scanned file: the class boxes on it and the edges between them."""

    def __init__(self, file_path: Path, name: str, root: ET.Element) -> None:
        self.file_path = file_path
        self.name = name
        self.root = root
        self.boxes: dict[str, Box] = {}
        self.class_names: dict[str, str] = {}
        for cell in root.iter('mxCell'):
            name_in_cell = class_name_in(cell.get('value', '')) if cell.get('vertex') == '1' else None
            box = cell_box(cell)
            if name_in_cell and box:
                self.boxes[cell.get('id')] = box
                self.class_names[cell.get('id')] = name_in_cell
        self.edges = [cell for cell in root.findall('mxCell') if cell.get('edge') == '1']

    def describe(self, edge: ET.Element) -> str:
        """`Source->Target (kind)`, the way every edge message names the edge."""
        source = self.class_names.get(edge.get('source', ''), '?')
        target = self.class_names.get(edge.get('target', ''), '?')
        return f"{source}->{target} ({edge_kind(edge.get('style', ''))})"

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


class DrawioScanner:
    """Scans `.drawio` files page by page. Each subclass names one layout RULE and checks it in `scan_page`."""

    def __init__(self, rule: str | None=None, explicit_paths: Iterable[Path]=(), scan_root: Path | str | None=None) -> None:
        self.rule = rule or getattr(type(self), 'RULE', '')
        # Paths the caller named itself are scanned even inside folders a workspace scan skips.
        self.explicit_paths = frozenset(Path(path).resolve() for path in explicit_paths)
        # The folder a report scans under; without one, the folder the named paths share.
        self.scan_root = Path(scan_root) if scan_root is not None else None

    def is_skipped_path(self, path: Path) -> bool:
        p = Path(path)
        if p.resolve() in self.explicit_paths:
            return False
        if p.stem.lower() in _REPAIR_FIXTURE_NAMES:
            return False
        if any((part.lower() in _REPAIR_FIXTURE_DIRS for part in p.parts)):
            return False
        return any((part in SKIP_DIR_NAMES for part in p.parts))

    def filter_scan_files(self, files: list[Path]) -> list[Path]:
        return [path for path in files if not self.is_skipped_path(path)]

    def scan(self, root: Path, files: list[Path]) -> list[Violation]:
        root = root.resolve()
        violations: list[Violation] = []
        for file_path in self.filter_scan_files(files):
            path = file_path if file_path.is_absolute() else root / file_path
            if not path.is_file():
                continue
            if self.is_skipped_path(path):
                continue
            violations.extend(self.scan_file(root, path))
        return violations

    def scan_file(self, root: Path, file_path: Path) -> list[Violation]:
        del root
        if file_path.suffix.lower() not in DRAWIO_EXTENSIONS:
            return []
        try:
            mxfile = ET.parse(str(file_path)).getroot()
        except (OSError, ET.ParseError) as exc:
            return [Violation(self.rule, f'Could not load drawio file: {exc}', practice='clean_engineering', location=str(file_path))]
        violations = []
        for diagram in mxfile.findall('diagram'):
            page_root = diagram.find('mxGraphModel/root')
            if page_root is None:
                continue
            violations.extend(self.scan_page(DrawioPage(file_path, diagram.get('name') or '(unnamed)', page_root)))
        return violations

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        return []

    def violation(self, page: DrawioPage, message: str) -> Violation:
        """A violation on this page, prefixed with the page name and located at the scanned file."""
        return Violation(self.rule, f'[{page.name}] {message}', practice='clean_engineering', location=str(page.file_path))

    def discover(self) -> dict[str, type[DrawioScanner]]:
        discovered: dict[str, type[DrawioScanner]] = {}
        scanners_dir = Path(__file__).resolve().parent
        for script in sorted(scanners_dir.glob('*_scanner.py')):
            scanner_class = self._scanner_class_in(script)
            if scanner_class is None:
                continue
            slug = getattr(scanner_class, 'RULE', None)
            if not isinstance(slug, str) or not slug.strip():
                slug = script.stem[:-len('_scanner')].replace('_', '-')
            discovered[slug.strip()] = scanner_class
        return discovered

    def _scanner_class_in(self, script: Path) -> type[DrawioScanner] | None:
        module = importlib.import_module(f'{__package__}.{script.stem}')
        for value in vars(module).values():
            if isinstance(value, type) and issubclass(value, DrawioScanner) and value.__module__ == module.__name__:
                return value
        return None

    def run_report(self, paths: list[str]) -> dict[str, Any]:
        files = [Path(path) for path in paths]
        scan_root = self.scan_root or self._shared_folder(files)
        discovered = self.discover()
        violations: list[Violation] = []
        for slug, scanner_class in discovered.items():
            violations.extend(scanner_class(slug, explicit_paths=files).scan(scan_root, files))
        if self.rule:
            violations = [item for item in violations if item.rule == self.rule]
        return {'ok': not violations, 'rules': sorted(discovered), 'violations': data_of(violations)}

    def _shared_folder(self, files: list[Path]) -> Path:
        """The deepest folder that holds every named path, so a report never scans the server's working folder."""
        folders = [path.resolve().parent for path in files]
        shared = folders[0] if folders else Path(__file__).resolve().parent
        while any(shared != folder and shared not in folder.parents for folder in folders):
            shared = shared.parent
        return shared

    def run_main(self, argv: list[str] | None=None) -> int:
        parser = argparse.ArgumentParser(description='Run one Draw.io scanner')
        parser.add_argument('--workspace', type=Path, default=Path.cwd(), help='Project root (default: cwd).')
        args = parser.parse_args(argv)
        workspace = args.workspace.resolve()
        violations = self.scan(workspace, self.collect_drawio_files(workspace))
        for violation in violations:
            print(data_of(violation), file=sys.stderr)
        return 1 if violations else 0

    def collect_drawio_files(self, root: Path) -> list[Path]:
        files: list[Path] = []
        for path in root.rglob('*'):
            if not path.is_file():
                continue
            if path.suffix.lower() not in DRAWIO_EXTENSIONS:
                continue
            if self.is_skipped_path(path):
                continue
            files.append(path)
        return files


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
    match = re.search('<b[^>]*>(.*?)</b>', html.unescape(value), re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    name = re.sub('\\s+', ' ', match.group(1)).strip()
    return name.split(' : ')[0].strip() or None


def cell_box(cell: ET.Element) -> Box | None:
    """(x, y, width, height) from a cell's mxGeometry, or None when the cell has none."""
    geometry = cell.find('mxGeometry')
    if geometry is None:
        return None
    return (float(geometry.get('x', '0')), float(geometry.get('y', '0')), float(geometry.get('width', '0')), float(geometry.get('height', '0')))


def edge_kind(style: str) -> str:
    """The UML relationship an edge style draws."""
    is_orthogonal = 'orthogonalEdgeStyle' in style
    if 'endFill=0' in style and 'endArrow=block' in style:
        return 'inheritance-orthogonal' if is_orthogonal else 'inheritance'
    if 'startFill=1' in style and 'diamondThin' in style:
        return 'composition'
    if 'startFill=0' in style and 'diamondThin' in style:
        return 'aggregation'
    if 'dashed=1' in style and 'endArrow=open' in style:
        return 'dependency-orthogonal' if is_orthogonal else 'dependency'
    if 'endArrow=open' in style:
        return 'association'
    return 'unknown'


def style_number(style: str, key: str) -> float | None:
    """A number set in a Draw.io style string, such as `exitX=0.3`."""
    match = re.search(f'(?:^|;){key}=(-?[0-9.]+)', style)
    return float(match.group(1)) if match else None


def box_center(box: Box) -> Point:
    x, y, width, height = box
    return (x + width / 2, y + height / 2)


def anchor_point(style: str, box: Box, end: str) -> Point:
    """Where one end of an edge meets its box: the exit or entry anchor in the style, else the box centre."""
    x, y, width, height = box
    fraction_x = style_number(style, f'{end}X')
    fraction_y = style_number(style, f'{end}Y')
    if fraction_x is not None and fraction_y is not None:
        return (x + width * fraction_x, y + height * fraction_y)
    return box_center(box)


def segments_cross(first: Segment, second: Segment) -> bool:
    """True when two straight segments cross each other."""
    (a, b), (c, d) = first, second
    return _turns_left(a, c, d) != _turns_left(b, c, d) and _turns_left(a, b, c) != _turns_left(a, b, d)


def segment_hits_box(segment: Segment, box: Box, margin: float) -> bool:
    """True when the segment cuts the box grown by margin on every side, or starts inside it."""
    start = segment[0]
    left, top = box[0] - margin, box[1] - margin
    right, bottom = box[0] + box[2] + margin, box[1] + box[3] + margin
    corners = [(left, top), (right, top), (right, bottom), (left, bottom)]
    if any(segments_cross(segment, (corners[index], corners[(index + 1) % 4])) for index in range(4)):
        return True
    return left <= start[0] <= right and top <= start[1] <= bottom


def _turns_left(a: Point, b: Point, c: Point) -> bool:
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])


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
