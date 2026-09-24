"""Draw.io layout scanners — self-contained; no Scan kit."""
from __future__ import annotations

import argparse
import html
import importlib.util
import re
import sys
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
DRAWIO_EXTENSIONS = frozenset({'.drawio', '.xml'})
SKIP_DIR_NAMES = frozenset({'node_modules', '.git', 'dist', 'build', 'coverage', '__pycache__', '.venv', 'venv', 'examples'})
_REPAIR_FIXTURE_NAMES = frozenset({'faultyasset', 'repairedasset'})
_REPAIR_FIXTURE_DIRS = frozenset({'faultyassets', 'repairedassets'})

class DrawioViolation:

    def __init__(self, rule: str, message: str, *, location: str='', line: int | None=None, severity: str='error') -> None:
        self.rule = rule
        self.message = message
        self.location = location
        self.line = line
        self.severity = severity

    def to_dict(self) -> dict[str, Any]:
        return {'rule': self.rule, 'violation_message': self.message, 'severity': self.severity, 'line_number': self.line, 'location': self.location}

class DrawioScanner:
    """Scanners that read `.drawio` mxfile pages via ``drawio_tools``."""
    _explicit_paths: frozenset[Path] = frozenset()

    def __init__(self, rule: str | None=None) -> None:
        self.rule = rule or getattr(type(self), 'RULE', type(self).__name__)
        self.workspace_root: Path | str | None = None

    @contextmanager
    def explicitly_requested(self, paths: Iterable[Path]) -> Iterator[None]:
        previous = DrawioScanner._explicit_paths
        DrawioScanner._explicit_paths = frozenset((Path(path).resolve() for path in paths))
        try:
            yield
        finally:
            DrawioScanner._explicit_paths = previous

    def is_skipped_path(self, path: Path) -> bool:
        p = Path(path)
        if DrawioScanner._explicit_paths and p.resolve() in DrawioScanner._explicit_paths:
            return False
        if p.stem.lower() in _REPAIR_FIXTURE_NAMES:
            return False
        if any((part.lower() in _REPAIR_FIXTURE_DIRS for part in p.parts)):
            return False
        return any((part in SKIP_DIR_NAMES for part in p.parts))

    def filter_scan_files(self, files: list[Path]) -> list[Path]:
        return [path for path in files if not self.is_skipped_path(path)]

    def scan(self, root: Path, files: list[Path]) -> list[DrawioViolation]:
        root = root.resolve()
        violations: list[DrawioViolation] = []
        for file_path in self.filter_scan_files(files):
            path = file_path if file_path.is_absolute() else root / file_path
            if not path.is_file():
                continue
            if self.is_skipped_path(path):
                continue
            violations.extend(self.scan_file(root, path))
        return violations

    def scan_file(self, root: Path, file_path: Path) -> list[DrawioViolation]:
        del root
        if file_path.suffix.lower() not in DRAWIO_EXTENSIONS:
            return []
        try:
            _, mxfile = self._load_drawio(str(file_path))
        except Exception as exc:
            return [self.violation(f'Could not load drawio file: {exc}', location=str(file_path))]
        violations = []
        for diagram in mxfile.findall('diagram'):
            page_name = diagram.get('name') or '(unnamed)'
            _, page_root = self._get_page(mxfile, page_name)
            if page_root is None:
                continue
            self._scan_file_path = file_path
            self._scan_page_name = page_name
            violations.extend(self.scan_page(page_root))
        return violations

    def scan_page(self, page_root) -> list:
        return []

    def violation(self, message: str, *, location: str='', line: int | None=None, severity: str='error') -> DrawioViolation:
        return DrawioViolation(self.rule, message, location=location, line=line, severity=severity)

    def discover(self) -> dict[str, type[DrawioScanner]]:
        discovered: dict[str, type[DrawioScanner]] = {}
        scanners_dir = Path(__file__).resolve().parent
        for script in sorted(scanners_dir.glob('*_scanner.py')):
            scanner_class = self._load_scanner_class(script)
            if scanner_class is None:
                continue
            slug = getattr(scanner_class, 'RULE', None)
            if not isinstance(slug, str) or not slug.strip():
                stem = script.stem
                if stem.endswith('_scanner'):
                    stem = stem[:-len('_scanner')]
                slug = stem.replace('_', '-')
            discovered[slug.strip()] = scanner_class
        return discovered

    def _load_scanner_class(self, script: Path) -> type[DrawioScanner] | None:
        parent = str(script.parent)
        sys.path.insert(0, parent)
        previous_alias = sys.modules.get('_drawio_base')
        sys.modules['_drawio_base'] = sys.modules[type(self).__module__]
        try:
            spec = importlib.util.spec_from_file_location(script.stem, script)
            if spec is None or spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for value in vars(module).values():
                if isinstance(value, type) and issubclass(value, DrawioScanner) and (value is not DrawioScanner) and (value.__module__ == module.__name__):
                    return value
            return None
        finally:
            if previous_alias is None:
                sys.modules.pop('_drawio_base', None)
            else:
                sys.modules['_drawio_base'] = previous_alias
            if parent in sys.path:
                sys.path.remove(parent)

    def run_report(self, paths: list[str]) -> dict[str, Any]:
        scan_root = Path(self.workspace_root) if self.workspace_root is not None else Path.cwd()
        files = [Path(path) for path in paths]
        discovered = self.discover()
        with self.explicitly_requested(files):
            violations: list[DrawioViolation] = []
            for slug, scanner_class in discovered.items():
                violations.extend(scanner_class(slug).scan(scan_root, files))
        result = {'ok': len(violations) == 0, 'rules': sorted(discovered), 'violations': [item.to_dict() for item in violations]}
        if self.rule is not None:
            result['violations'] = [item for item in result['violations'] if item['rule'] == self.rule]
            result['ok'] = len(result['violations']) == 0
        return result

    def run_main(self, argv: list[str] | None=None) -> int:
        parser = argparse.ArgumentParser(description='Run one Draw.io scanner')
        parser.add_argument('--workspace', type=Path, default=Path.cwd(), help='Project root (default: cwd).')
        args = parser.parse_args(argv)
        workspace = args.workspace.resolve()
        files = self.collect_drawio_files(workspace)
        scanner = type(self)(getattr(type(self), 'RULE', type(self).__name__))
        violations = scanner.scan(workspace, files)
        if not violations:
            return 0
        for violation in violations:
            print(violation.to_dict(), file=sys.stderr)
        return 1

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

    def _escape(self, text):
        return html.escape(str(text), quote=True)

    def _unescape(self, text):
        return html.unescape(str(text))

    def _load_drawio(self, path):
        """Load a DrawIO file. Returns (tree, root_element)."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f'File not found: {path}')
        tree = ET.parse(str(path))
        return (tree, tree.getroot())

    def _save_drawio(self, path, root_element):
        """Write an mxfile element tree to disk."""
        path = Path(path)
        tree = ET.ElementTree(root_element)
        ET.indent(tree, space='  ')
        tree.write(str(path), encoding='unicode', xml_declaration=False)

    def _create_empty_mxfile(self):
        """Create a new empty mxfile element."""
        return ET.fromstring('<mxfile host="drawio_tools.py"></mxfile>')

    def _get_page(self, mxfile, page_name=None):
        """Get a diagram page by name. Returns (diagram_element, root_cell_parent).
    If page_name is None, returns the first page."""
        diagrams = mxfile.findall('diagram')
        if page_name:
            for d in diagrams:
                if d.get('name') == page_name:
                    model = d.find('mxGraphModel')
                    root = model.find('root') if model is not None else None
                    return (d, root)
            return (None, None)
        if diagrams:
            d = diagrams[0]
            model = d.find('mxGraphModel')
            root = model.find('root') if model is not None else None
            return (d, root)
        return (None, None)

    def _add_page(self, mxfile, _rest):
        page_name, page_width, page_height = _rest
        'Add a new diagram page to the mxfile. Returns (diagram, root).'
        diagram = ET.SubElement(mxfile, 'diagram')
        diagram.set('id', f"page_{page_name.replace(' ', '_').lower()}")
        diagram.set('name', page_name)
        model = ET.SubElement(diagram, 'mxGraphModel')
        model.set('dx', '1200')
        model.set('dy', '800')
        model.set('grid', '1')
        model.set('gridSize', '10')
        model.set('guides', '1')
        model.set('tooltips', '1')
        model.set('connect', '1')
        model.set('arrows', '1')
        model.set('fold', '1')
        model.set('page', '1')
        model.set('pageScale', '1')
        model.set('pageWidth', str(page_width))
        model.set('pageHeight', str(page_height))
        model.set('math', '0')
        model.set('shadow', '0')
        root = ET.SubElement(model, 'root')
        cell0 = ET.SubElement(root, 'mxCell')
        cell0.set('id', '0')
        cell1 = ET.SubElement(root, 'mxCell')
        cell1.set('id', '1')
        cell1.set('parent', '0')
        return (diagram, root)

    def _next_id(self, root):
        """Find the next available integer cell id."""
        max_id = 1
        for cell in root.iter('mxCell'):
            try:
                max_id = max(max_id, int(cell.get('id', '0')))
            except ValueError:
                pass
        return max_id + 1

    def _extract_class_name(self, value):
        """Extract class name from the HTML value of a class cell.
    The name is in the <b> tag. Stereotype (if any) is in a separate <i> tag."""
        if not value:
            return None
        match = re.search('<b[^>]*>(.*?)</b>', self._unescape(value), re.IGNORECASE | re.DOTALL)
        if match:
            name = re.sub('\\s+', ' ', match.group(1)).strip()
            if ' : ' in name:
                name = name.split(' : ')[0].strip()
            return name or None
        return None

    def _find_cell_by_name(self, root, class_name):
        """Find a class mxCell by its displayed name."""
        for cell in root.findall('mxCell'):
            value = cell.get('value', '')
            extracted = self._extract_class_name(value)
            if extracted == class_name:
                return cell
        return None

    def _find_cell_by_id(self, root, cell_id):
        """Find an mxCell by its id attribute."""
        for cell in root.findall('mxCell'):
            if cell.get('id') == str(cell_id):
                return cell
        return None

    def _get_all_classes(self, root):
        """Return list of (cell_id, class_name, x, y, w, h) for all class cells."""
        classes = []
        for cell in root.iter('mxCell'):
            if cell.get('vertex') != '1':
                continue
            name = self._extract_class_name(cell.get('value', ''))
            if not name:
                continue
            geo = self._get_geometry(cell)
            if geo:
                classes.append((cell.get('id'), name, *geo))
        return classes

    def _get_all_edges(self, root):
        """Return list of (cell_id, edge_type, source_id, target_id) for all edges."""
        edges = []
        for cell in root.findall('mxCell'):
            if cell.get('edge') != '1':
                continue
            style = cell.get('style', '')
            source = cell.get('source', '')
            target = cell.get('target', '')
            edge_type = self._classify_edge(style)
            edges.append((cell.get('id'), edge_type, source, target))
        return edges

    def _rect_clear_gap(self, a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
        """Exterior gap between two axis-aligned boxes (0 if they touch/overlap)."""
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        dx = max(0.0, max(ax - (bx + bw), bx - (ax + aw)))
        dy = max(0.0, max(ay - (by + bh), by - (ay + ah)))
        x_overlap = not (ax + aw < bx or bx + bw < ax)
        y_overlap = not (ay + ah < by or by + bh < ay)
        if x_overlap and y_overlap:
            return 0.0
        if x_overlap:
            return dy
        if y_overlap:
            return dx
        return (dx ** 2 + dy ** 2) ** 0.5

    def _edge_waypoint_count(self, edge_cell) -> int:
        geo = edge_cell.find('mxGeometry')
        if geo is None:
            return 0
        arr = geo.find('Array')
        if arr is None:
            return 0
        return len(list(arr))

    def _check_prefer_short_routes(self, root) -> list[tuple[str, str]]:
        """Return (edge_desc, reason) for edges that are unnecessarily long/doglegged."""
        self._id_to_geo, self._id_to_name = self._vertex_geo_and_names(root)
        violations: list[tuple[str, str]] = []
        for cell in root.iter('mxCell'):
            violations.extend(self._short_route_hits(cell))
        return violations

    def _vertex_geo_and_names(self, root):
        id_to_geo: dict[str, tuple[float, float, float, float]] = {}
        id_to_name: dict[str, str] = {}
        for cell in root.iter('mxCell'):
            if cell.get('vertex') != '1':
                continue
            geo = self._get_geometry(cell)
            if not geo:
                continue
            cid = cell.get('id') or ''
            if not cid:
                continue
            id_to_geo[cid] = geo
            id_to_name[cid] = self._extract_class_name(cell.get('value', '')) or cid
        return (id_to_geo, id_to_name)

    def _short_route_hits(self, cell) -> list[tuple[str, str]]:
        if cell.get('edge') != '1':
            return []
        src = cell.get('source', '')
        tgt = cell.get('target', '')
        id_to_geo = self._id_to_geo
        if src not in id_to_geo or tgt not in id_to_geo:
            return []
        sn = self._id_to_name.get(src, src)
        tn = self._id_to_name.get(tgt, tgt)
        desc = f'{sn} → {tn}'
        nwp = self._edge_waypoint_count(cell)
        gap = self._rect_clear_gap(id_to_geo[src], id_to_geo[tgt])
        hits: list[tuple[str, str]] = []
        if nwp > SHORT_ROUTE_MAX_WAYPOINTS and gap <= SHORT_ROUTE_MAX_BOX_GAP:
            hits.append((desc, f'{nwp} waypoints across a {gap:.0f}px gap (max {SHORT_ROUTE_MAX_WAYPOINTS}) — prefer a short orthogonal route'))
        if gap > SHORT_ROUTE_MAX_BOX_GAP:
            hits.append((desc, f'endpoint gap {gap:.0f}px (max {SHORT_ROUTE_MAX_BOX_GAP}) — place related classes closer'))
        return hits

    def _classify_edge(self, style):
        """Determine edge type from style string."""
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

    def _get_geometry(self, cell):
        """Return (x, y, width, height) from a cell's mxGeometry, or None."""
        geo = cell.find('mxGeometry')
        if geo is None:
            return None
        return (float(geo.get('x', '0')), float(geo.get('y', '0')), float(geo.get('width', '0')), float(geo.get('height', '0')))

    def _set_geometry(self, cell, _rest):
        x, y, w, h = _rest
        "Update position and/or size on a cell's mxGeometry."
        geo = cell.find('mxGeometry')
        if geo is None:
            geo = ET.SubElement(cell, 'mxGeometry')
            geo.set('as', 'geometry')
        if x is not None:
            geo.set('x', str(int(x)))
        if y is not None:
            geo.set('y', str(int(y)))
        if w is not None:
            geo.set('width', str(int(w)))
        if h is not None:
            geo.set('height', str(int(h)))

    def _check_overlaps(self, classes):
        """Return list of overlapping pairs: [(name_a, name_b), ...]."""
        overlaps = []
        for i, (_, name_a, xa, ya, wa, ha) in enumerate(classes):
            for j, (_, name_b, xb, yb, wb, hb) in enumerate(classes):
                if j <= i:
                    continue
                if xa < xb + wb and xa + wa > xb and (ya < yb + hb) and (ya + ha > yb):
                    overlaps.append((name_a, name_b))
        return overlaps

    def _rect_center(self, rect):
        """Return center point of a rectangle."""
        x, y, w, h = rect
        return (x + w / 2, y + h / 2)

    def _line_intersects_rect(self, segment, rect):
        """Check if line segment passes through rectangle.

    Uses margin to detect near-misses (edges that visually touch).
    """
        start_x, start_y, end_x, end_y = segment
        left, top, width, height, margin = rect
        if margin is None:
            margin = 5
        left -= margin
        top -= margin
        width += 2 * margin
        height += 2 * margin
        self._ccw_third = (end_x, end_y)
        if self._rect_sides_cross_segment((start_x, start_y), (left, top, width, height)):
            return True
        if left <= start_x <= left + width and top <= start_y <= top + height:
            return True
        return False

    def _rect_sides_cross_segment(self, start, rect) -> bool:
        start_x, start_y = start
        left, top, width, height = rect
        corners = [(left, top), (left + width, top), (left + width, top + height), (left, top + height)]
        sides = [(corners[0], corners[1]), (corners[1], corners[2]), (corners[2], corners[3]), (corners[3], corners[0])]
        end_x, end_y = self._ccw_third
        for first, second in sides:
            if self._segments_cross_2d((start_x, start_y, end_x, end_y), (first[0], first[1], second[0], second[1])):
                return True
        return False

    def _ccw_2d(self, first, second) -> bool:
        ax, ay = first
        bx, by = second
        cx, cy = self._ccw_third
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)

    def _segments_cross_2d(self, first, second) -> bool:
        ax, ay, bx, by = first
        cx, cy, dx, dy = second
        self._ccw_third = (dx, dy)
        first_turn = self._ccw_2d((ax, ay), (cx, cy)) != self._ccw_2d((bx, by), (cx, cy))
        self._ccw_third = (cx, cy)
        second_turn = self._ccw_2d((ax, ay), (bx, by))
        self._ccw_third = (dx, dy)
        return first_turn and second_turn != self._ccw_2d((ax, ay), (bx, by))

    def _orthogonal_crosses_rect(self, src_geo, tgt_geo):
        """Approximate check: does an orthogonal edge between two classes cross a third?

    Orthogonal edges go horizontal then vertical (or vice versa). We check both
    possible L-shaped paths and report a crossing if BOTH paths hit the obstacle.
    """
        rx, ry, rw, rh = self._obstacle_rect
        margin = self._hit_margin
        scx, scy = self._rect_center(src_geo)
        tcx, tcy = self._rect_center(tgt_geo)
        path_a_crosses = self._line_intersects_rect((scx, scy, tcx, scy), (rx, ry, rw, rh, margin)) or self._line_intersects_rect((tcx, scy, tcx, tcy), (rx, ry, rw, rh, margin))
        path_b_crosses = self._line_intersects_rect((scx, scy, scx, tcy), (rx, ry, rw, rh, margin)) or self._line_intersects_rect((scx, tcy, tcx, tcy), (rx, ry, rw, rh, margin))
        return path_a_crosses and path_b_crosses

    def _check_edge_crossings(self, root):
        """Check if any edge passes through a class it is not connected to.
    Returns list of (edge_desc, crossed_class_name) tuples."""
        classes = self._get_all_classes(root)
        edges = self._get_all_edges(root)
        self._scan_classes = classes
        self._id_to_name = {cid: name for cid, name, *_ in classes}
        self._id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}
        crossings = []
        for _eid, etype, src_id, tgt_id in edges:
            self._edge_type = etype
            self._edge_src_id = src_id
            self._edge_tgt_id = tgt_id
            crossings.extend(self._crossings_for_edge())
        return crossings

    def _crossings_for_edge(self):
        src_id, tgt_id = self._edge_src_id, self._edge_tgt_id
        src_geo = self._id_to_geo.get(src_id)
        tgt_geo = self._id_to_geo.get(tgt_id)
        if src_geo is None or tgt_geo is None:
            return []
        src_name = self._id_to_name.get(src_id, '?')
        tgt_name = self._id_to_name.get(tgt_id, '?')
        etype = self._edge_type
        is_straight = etype in ('inheritance', 'dependency', 'association-straight', 'composition-straight', 'aggregation-straight')
        desc = f'{src_name}->{tgt_name} ({etype})'
        hits = []
        for cid, cname, cx, cy, cw, ch in self._scan_classes:
            if cid in (src_id, tgt_id):
                continue
            self._obstacle_box = (cx, cy, cw, ch)
            if self._edge_hits_class(is_straight, (src_geo, tgt_geo)):
                hits.append((desc, cname))
        return hits

    def _edge_hits_class(self, is_straight, geos) -> bool:
        src_geo, tgt_geo = geos
        cx, cy, cw, ch = self._obstacle_box
        if is_straight:
            scx, scy = self._rect_center(src_geo)
            tcx, tcy = self._rect_center(tgt_geo)
            return self._line_intersects_rect((scx, scy, tcx, tcy), (cx, cy, cw, ch, None))
        self._obstacle_rect = (cx, cy, cw, ch)
        self._hit_margin = None
        return self._orthogonal_crosses_rect(src_geo, tgt_geo)

    def _check_shared_anchors(self, root):
        """Detect edges that share the same anchor point on the same class.

    Groups edges by the (class_id, exit/entry_x, exit/entry_y) anchor.  When
    explicit anchors are set in the style, those are used; otherwise the
    default center anchor is assumed.  Reports a conflict only when two or
    more edges share the *exact same* anchor coordinates on the same class.
    """
        classes = self._get_all_classes(root)
        self._id_to_name = {cid: name for cid, name, *_ in classes}
        self._id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}
        self._anchor_map = {}
        for cell in root.findall('mxCell'):
            self._record_edge_anchors(cell)
        return self._anchor_conflicts()

    def _record_edge_anchors(self, cell) -> None:
        if cell.get('edge') != '1':
            return
        style = cell.get('style', '')
        src_id = cell.get('source', '')
        tgt_id = cell.get('target', '')
        src_name = self._id_to_name.get(src_id, '?')
        tgt_name = self._id_to_name.get(tgt_id, '?')
        etype = self._classify_edge(style)
        desc = f'{src_name}->{tgt_name} ({etype})'
        ex = self._parse_style_float(style, 'exitX')
        ey = self._parse_style_float(style, 'exitY')
        src_anchor = (round(ex, 2) if ex is not None else 'def', round(ey, 2) if ey is not None else 'def')
        nx = self._parse_style_float(style, 'entryX')
        ny = self._parse_style_float(style, 'entryY')
        tgt_anchor = (round(nx, 2) if nx is not None else 'def', round(ny, 2) if ny is not None else 'def')
        self._anchor_map.setdefault((src_id, 'exit', src_anchor), []).append(desc)
        self._anchor_map.setdefault((tgt_id, 'entry', tgt_anchor), []).append(desc)

    def _anchor_conflicts(self):
        conflicts = []
        for (cid, end, anchor), descs in self._anchor_map.items():
            if len(descs) <= 1:
                continue
            cls_name = self._id_to_name.get(cid, '?')
            anchor_label = f'{end}({anchor[0]},{anchor[1]})'
            conflicts.append((cls_name, anchor_label, descs))
        return conflicts

    def _parse_style_float(self, style, key):
        """Extract a float value from a Draw.io style string, e.g. 'exitX=0.3'."""
        m = re.search(f'{key}=([0-9.]+)', style)
        return float(m.group(1)) if m else None

    def _edge_anchor_point(self, style, _rest):
        cell_geo, end = _rest
        'Compute the absolute (x, y) anchor point for one end of an edge.\n\n    Reads exitX/exitY or entryX/entryY from the style.  Falls back to the\n    centre of the class box when no explicit anchor is set.\n    '
        x, y, w, h = cell_geo
        ax = self._parse_style_float(style, f'{end}X')
        ay = self._parse_style_float(style, f'{end}Y')
        if ax is not None and ay is not None:
            return (x + w * ax, y + h * ay)
        return self._rect_center((x, y, w, h))

    def _compute_edge_segments(self, edge_cell, id_to_geo):
        """Compute the polyline segments of an edge.

    For straight edges: one segment from source anchor to target anchor.
    For orthogonal edges with explicit waypoints: follow those waypoints.
    For orthogonal edges without waypoints: approximate using both possible
    L-shaped routes (H-V and V-H) and return the one less likely to cross.

    Returns a list of ((x1,y1),(x2,y2)) segments, and a boolean
    ``is_approximate`` indicating whether the route is a best-guess.
    Callers that need is_approximate can call _compute_edge_segments_ex.
    """
        segs, _ = self._compute_edge_segments_ex(edge_cell, id_to_geo)
        return segs

    def _compute_edge_segments_ex(self, edge_cell, id_to_geo):
        """Like _compute_edge_segments but also returns is_approximate flag."""
        style = edge_cell.get('style', '')
        src_id = edge_cell.get('source', '')
        tgt_id = edge_cell.get('target', '')
        src_geo = id_to_geo.get(src_id)
        tgt_geo = id_to_geo.get(tgt_id)
        if src_geo is None or tgt_geo is None:
            return ([], False)
        p1 = self._edge_anchor_point(style, (src_geo, 'exit'))
        p2 = self._edge_anchor_point(style, (tgt_geo, 'entry'))
        is_orthogonal = 'orthogonal' in style.lower() or 'edgestyle=orthogonal' in style.lower()
        if not is_orthogonal:
            return ([(p1, p2)], False)
        geo = edge_cell.find('mxGeometry')
        waypoints = []
        if geo is not None:
            arr = geo.find('Array')
            if arr is not None:
                for pt in arr.findall('mxPoint'):
                    px = float(pt.get('x', '0'))
                    py = float(pt.get('y', '0'))
                    waypoints.append((px, py))

        def _expand_orthogonal_seg(pa, _rest):
            pb, prev_dir = _rest
            'Return list of points (excluding ``pa``) representing the H-V or\n        V-H expansion of segment ``pa→pb`` (or a single point if it is\n        already axis-aligned). ``prev_dir`` is the direction of the\n        previous segment ("h", "v" or None).\n        '
            ax, ay = pa
            bx, by = pb
            if abs(bx - ax) < 1 or abs(by - ay) < 1:
                return ([(bx, by)], 'v' if abs(bx - ax) < 1 else 'h')
            if prev_dir == 'v':
                corner = (ax, by)
                return ([corner, (bx, by)], 'h')
            corner = (bx, ay)
            return ([corner, (bx, by)], 'v')
        if waypoints:
            points = [p1] + waypoints + [p2]
            expanded = [points[0]]
            prev_dir = None
            for i in range(len(points) - 1):
                next_pts, prev_dir = _expand_orthogonal_seg(expanded[-1], (points[i + 1], prev_dir))
                expanded.extend(next_pts)
            return ([(expanded[i], expanded[i + 1]) for i in range(len(expanded) - 1)], False)
        x1, y1 = p1
        x2, y2 = p2
        if abs(x2 - x1) < 1 or abs(y2 - y1) < 1:
            return ([(p1, p2)], False)
        mid_x = (x1 + x2) / 2
        return ([(p1, (mid_x, y1)), ((mid_x, y1), (mid_x, y2)), ((mid_x, y2), p2)], True)

    def _segments_overlap_1d(self, a_start, _rest):
        a_end, b_start, b_end, threshold = _rest
        'Check whether two 1D intervals overlap by more than *threshold* pixels.'
        lo_a, hi_a = (min(a_start, a_end), max(a_start, a_end))
        lo_b, hi_b = (min(b_start, b_end), max(b_start, b_end))
        overlap = min(hi_a, hi_b) - max(lo_a, lo_b)
        return overlap > threshold

    def _edge_segments_overlap(self, seg_a, _rest):
        seg_b, proximity = _rest
        'Check whether two line segments visually overlap (run parallel and\n    close together for a shared span).  Works for axis-aligned segments\n    produced by orthogonal routing.\n    '
        (ax1, ay1), (ax2, ay2) = seg_a
        (bx1, by1), (bx2, by2) = seg_b
        a_horiz = abs(ay2 - ay1) < 2
        a_vert = abs(ax2 - ax1) < 2
        b_horiz = abs(by2 - by1) < 2
        b_vert = abs(bx2 - bx1) < 2
        if a_horiz and b_horiz:
            if abs(ay1 - by1) < proximity:
                if self._segments_overlap_1d(ax1, (ax2, bx1, bx2, None)):
                    return True
        if a_vert and b_vert:
            if abs(ax1 - bx1) < proximity:
                if self._segments_overlap_1d(ay1, (ay2, by1, by2, None)):
                    return True
        return False

    def _check_edge_on_edge_overlaps(self, root):
        """Detect pairs of edges whose route segments visually overlap.

    Returns list of (edge_a_desc, edge_b_desc, detail) tuples.
    """
        classes = self._get_all_classes(root)
        self._id_to_name = {cid: name for cid, name, *_ in classes}
        self._id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}
        edge_info = [self._edge_segment_info(cell) for cell in root.findall('mxCell') if cell.get('edge') == '1']
        overlaps = []
        for i, (desc_a, segs_a) in enumerate(edge_info):
            overlaps.extend(self._overlaps_against_later_edges(desc_a, (segs_a, edge_info[i + 1:])))
        return overlaps

    def _edge_segment_info(self, cell):
        src_id = cell.get('source', '')
        tgt_id = cell.get('target', '')
        src_name = self._id_to_name.get(src_id, '?')
        tgt_name = self._id_to_name.get(tgt_id, '?')
        etype = self._classify_edge(cell.get('style', ''))
        desc = f'{src_name}->{tgt_name} ({etype})'
        segs = self._compute_edge_segments(cell, self._id_to_geo)
        return (desc, segs)

    def _overlaps_against_later_edges(self, desc_a, later):
        segs_a, later_edges = later
        overlaps = []
        for desc_b, segs_b in later_edges:
            detail = self._first_segment_overlap(segs_a, segs_b)
            if detail:
                overlaps.append((desc_a, desc_b, detail))
        return overlaps

    def _first_segment_overlap(self, segs_a, segs_b):
        for sa in segs_a:
            for sb in segs_b:
                if self._edge_segments_overlap(sa, (sb, None)):
                    return f'segments {self._fmt_seg(sa)} and {self._fmt_seg(sb)} overlap'
        return None

    def _fmt_seg(self, seg):
        (x1, y1), (x2, y2) = seg
        return f'({x1:.0f},{y1:.0f})->({x2:.0f},{y2:.0f})'

    def _check_edges_crossing_classes(self, root):
        """Check edges whose route segments pass through a class box they are
    not connected to.

    For straight edges and orthogonal edges with explicit waypoints the
    route is known exactly.  For orthogonal edges WITHOUT waypoints the
    route is approximated — Draw.io's auto-router may find a better path.
    Approximate crossings are tagged ``(approx)`` in the description so
    the agent can decide whether to fix or ignore them.

    Returns list of (edge_desc, crossed_class_name) tuples.
    """
        classes = self._get_all_classes(root)
        self._scan_classes = classes
        self._id_to_name = {cid: name for cid, name, *_ in classes}
        self._id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}
        crossings = []
        for cell in root.findall('mxCell'):
            crossings.extend(self._class_hits_for_edge_cell(cell))
        return crossings

    def _class_hits_for_edge_cell(self, cell):
        if cell.get('edge') != '1':
            return []
        src_id = cell.get('source', '')
        tgt_id = cell.get('target', '')
        src_name = self._id_to_name.get(src_id, '?')
        tgt_name = self._id_to_name.get(tgt_id, '?')
        etype = self._classify_edge(cell.get('style', ''))
        segs, is_approx = self._compute_edge_segments_ex(cell, self._id_to_geo)
        suffix = ' (approx)' if is_approx else ''
        desc = f'{src_name}->{tgt_name} ({etype}){suffix}'
        hits = []
        for cid, cname, cx, cy, cw, ch in self._scan_classes:
            if cid in (src_id, tgt_id):
                continue
            if self._any_seg_hits_rect(segs, (cx, cy, cw, ch)):
                hits.append((desc, cname))
        return hits

    def _any_seg_hits_rect(self, segs, rect) -> bool:
        cx, cy, cw, ch = rect
        for (x1, y1), (x2, y2) in segs:
            if self._line_intersects_rect((x1, y1, x2, y2), (cx, cy, cw, ch, 3)):
                return True
        return False

    def _validate_layout(self, root):
        """Validate diagram against class_diagram rules. Returns list of (rule, message) violations."""
        violations = []
        classes = self._get_all_classes(root)
        self._id_to_name = {cid: name for cid, name, *_ in classes}
        self._name_to_geo = {name: (x, y, w, h) for cid, name, x, y, w, h in classes}
        for name_a, name_b in self._check_overlaps(classes):
            violations.append(('class_overlap', f'{name_a} overlaps {name_b}'))
        for edge_desc, crossed in self._check_edges_crossing_classes(root):
            violations.append(('edge_crosses_class', f'Edge {edge_desc} crosses through {crossed}'))
        for desc_a, desc_b, detail in self._check_edge_on_edge_overlaps(root):
            violations.append(('edge_on_edge_overlap', f'{desc_a} overlaps {desc_b} — {detail}'))
        for cls_name, side, descs in self._check_shared_anchors(root):
            violations.append(('shared_anchor', f"{cls_name} {side}: {len(descs)} edges share default anchor — {', '.join(descs)}"))
        violations.extend(self._inheritance_flow_violations(self._get_all_edges(root)))
        return violations

    def _inheritance_flow_violations(self, edges):
        violations = []
        for _eid, etype, src_id, tgt_id in edges:
            if etype not in ('inheritance', 'inheritance-orthogonal'):
                continue
            src_name = self._id_to_name.get(src_id)
            tgt_name = self._id_to_name.get(tgt_id)
            if src_name is None or tgt_name is None:
                continue
            src_geo = self._name_to_geo.get(src_name)
            tgt_geo = self._name_to_geo.get(tgt_name)
            if src_geo is None or tgt_geo is None:
                continue
            _, child_y, _, _ = src_geo
            _, parent_y, _, _ = tgt_geo
            if child_y <= parent_y:
                violations.append(('hierarchy_flow', f'Inheritance: {src_name} (y={child_y}) should be below parent {tgt_name} (y={parent_y}); base at top, children below'))
        return violations

    def _audit_diagram(self, path, page_name=None):
        """Run all layout checks on one or all pages.  Returns a dict:
    {page_name: {"pass": bool, "violations": [(rule, msg), ...]}}
    Designed to be called from CLI or by the agent after every render.
    """
        _, mxfile = self._load_drawio(path)
        pages = []
        if page_name:
            pages = [(page_name,)]
        else:
            for d in mxfile.findall('diagram'):
                pages.append((d.get('name'),))
        results = {}
        for pname, in pages:
            _, root = self._get_page(mxfile, pname)
            if root is None:
                results[pname] = {'pass': False, 'violations': [('page_missing', f"Page '{pname}' not found")]}
                continue
            v = self._validate_layout(root)
            results[pname] = {'pass': len(v) == 0, 'violations': v}
        return results

    def _audit_diagram_report(self, path, page_name=None):
        """Human-readable audit report. Returns the text string."""
        results = self._audit_diagram(path, page_name)
        lines = []
        all_pass = True
        for pname, info in results.items():
            status = 'PASS' if info['pass'] else 'FAIL'
            if not info['pass']:
                all_pass = False
            lines.append(f'\n=== Page: {pname} — {status} ===')
            if info['violations']:
                for rule, msg in info['violations']:
                    lines.append(f'  [{rule}] {msg}')
            else:
                lines.append('  No issues found.')
        summary = 'ALL PAGES PASS' if all_pass else 'VIOLATIONS FOUND'
        lines.insert(0, f'Audit: {summary}')
        return '\n'.join(lines)

    def _calc_cell_height(self, props_count, _rest):
        ops_count, inv_count = _rest
        'Compute cell height from content line counts.'
        sections = 2
        if inv_count > 0:
            sections = 3
        content_lines = props_count + ops_count + inv_count
        return max(CELL_MIN_HEIGHT, 30 + content_lines * LINE_HEIGHT + sections * SECTION_PAD)

    def _build_class_html(self, name, _rest):
        base, properties, operations, invariants, stereotype = _rest
        'Build the HTML value string for a UML class cell.'
        properties = properties or []
        operations = operations or []
        invariants = invariants or []
        base_label = f' : {self._escape(base)}' if base else ''
        stereotype_html = f'<i style="font-size:9px;color:#888;">{self._escape(stereotype)}</i><br/>' if stereotype else ''
        props_html = self._member_lines_html(properties)
        ops_html = self._member_lines_html(operations)
        label = f'<p style="margin:0px;margin-top:4px;text-align:center;">{stereotype_html}<b>{self._escape(name)}{base_label}</b></p><hr size="1"/><p style="margin:0px;margin-left:4px;font-size:10px;">{props_html}</p><hr size="1"/><p style="margin:0px;margin-left:4px;font-size:10px;">{ops_html}</p>'
        return label + self._invariants_html(invariants)

    def _member_lines_html(self, items):
        html = ''.join((f'+ {self._escape(p)}<br/>' for p in items))
        return html or '<br/>'

    def _invariants_html(self, invariants):
        if not invariants:
            return ''
        inv_html = ''
        for inv in invariants:
            short = inv[:80] + '...' if len(inv) > 80 else inv
            inv_html += f'<i>{self._escape(short)}</i><br/>'
        return f'<hr size="1"/><p style="margin:0px;margin-left:4px;font-size:9px;color:#666;">{inv_html}</p>'

    def _parse_class_html(self, value):
        """Extract (name, base, properties, operations, invariants) from class cell HTML."""
        text = self._unescape(value)
        name = None
        base = None
        match = re.search('<b>([^<]+)</b>', text)
        if match:
            raw = match.group(1).strip()
            if ' : ' in raw:
                name, base = raw.split(' : ', 1)
                name = name.strip()
                base = base.strip()
            else:
                name = raw
        sections = re.split('<hr size="1"\\s*/?>', text)
        properties = []
        operations = []
        invariants = []

        def extract_items(section_html):
            items = []
            for line in re.findall('\\+\\s*([^<]+)', section_html):
                line = line.strip()
                if line:
                    items.append(line)
            return items

        def extract_invariants(section_html):
            items = []
            for line in re.findall('<i>([^<]+)</i>', section_html):
                line = line.strip()
                if line:
                    items.append(line)
            return items
        if len(sections) >= 3:
            properties = extract_items(sections[1])
            operations = extract_items(sections[2])
        if len(sections) >= 4:
            invariants = extract_invariants(sections[3])
        return (name, base, properties, operations, invariants)

    def _create_class_cell(self, root, name):
        """Create and append a class mxCell to root. Returns the cell element.

    If imported_from is set, the class is rendered with dashed border and the
    source module name shown as a stereotype.
    """
        properties = self._cell_properties or []
        operations = self._cell_operations or []
        invariants = self._cell_invariants or []
        imported_from = self._from_module
        cell_id = str(self._next_id(root))
        stereotype = f'«from: {imported_from}»' if imported_from else None
        label = self._build_class_html(name, (self._cell_base, properties, operations, invariants, stereotype))
        height = self._imported_or_local_height((properties, operations, invariants))
        return self._append_vertex_cell(root, (cell_id, label, height))

    def _imported_or_local_height(self, counts):
        properties, operations, invariants = counts
        height = self._calc_cell_height(len(properties), (len(operations), len(invariants)))
        if self._from_module:
            height += LINE_HEIGHT
        return height

    def _append_vertex_cell(self, root, cell):
        cell_id, label, height = cell
        style = CLASS_STYLE_IMPORT if self._from_module else CLASS_STYLE
        cell = ET.SubElement(root, 'mxCell')
        cell.set('id', cell_id)
        cell.set('value', label)
        cell.set('style', style)
        cell.set('vertex', '1')
        cell.set('parent', '1')
        geo = ET.SubElement(cell, 'mxGeometry')
        geo.set('x', str(int(self._cell_x)))
        geo.set('y', str(int(self._cell_y)))
        geo.set('width', str(CELL_WIDTH))
        geo.set('height', str(int(height)))
        geo.set('as', 'geometry')
        return cell

    def _update_class_cell(self, cell, _rest):
        name, base, properties, operations, invariants = _rest
        "Update an existing class cell's content. Recalculates height."
        old_name, old_base, old_props, old_ops, old_invs = self._parse_class_html(self._unescape(cell.get('value', '')))
        new_name = name if name is not None else old_name
        new_base = base if base is not None else old_base
        new_props = properties if properties is not None else old_props
        new_ops = operations if operations is not None else old_ops
        new_invs = invariants if invariants is not None else old_invs
        label = self._build_class_html(new_name, (new_base, new_props, new_ops, new_invs, None))
        cell.set('value', label)
        height = self._calc_cell_height(len(new_props), (len(new_ops), len(new_invs)))
        self._set_geometry(cell, (None, None, None, height))

    def _create_edge(self, root) -> ET.Element:
        """Create and append an edge mxCell. Returns the cell element.

    Anchor points (0.0–1.0) control where the edge leaves/arrives on the
    class box.  0,0 = top-left; 1,1 = bottom-right; 0.5,0 = top-center.
    When multiple edges share a side, callers MUST supply distinct anchors.
    """
        if self._edge_kind not in EDGE_STYLES:
            raise ValueError(f'Unknown edge type: {self._edge_kind}. Use: {list(EDGE_STYLES.keys())}')
        cell = ET.SubElement(root, 'mxCell')
        cell.set('id', str(self._next_id(root)))
        cell.set('value', self._edge_label or '')
        cell.set('style', self._scanner_edge_style())
        cell.set('edge', '1')
        cell.set('parent', '1')
        cell.set('source', str(self._edge_src_id))
        cell.set('target', str(self._edge_tgt_id))
        geo = ET.SubElement(cell, 'mxGeometry')
        geo.set('relative', '1')
        geo.set('as', 'geometry')
        return cell

    def _scanner_edge_style(self) -> str:
        style = EDGE_STYLES[self._edge_kind]
        parts = self._scanner_anchor_parts()
        if parts:
            style = style.rstrip(';') + ';' + ';'.join(parts) + ';'
        return style

    def _scanner_anchor_parts(self) -> list:
        parts = []
        if self._exit_x is not None:
            parts.append(f'exitX={self._exit_x}')
        if self._exit_y is not None:
            parts.append(f'exitY={self._exit_y}')
        if self._entry_x is not None:
            parts.append(f'entryX={self._entry_x}')
        if self._entry_y is not None:
            parts.append(f'entryY={self._entry_y}')
        if not parts:
            return parts
        if self._exit_x is not None or self._exit_y is not None:
            parts.extend(['exitDx=0', 'exitDy=0'])
        if self._entry_x is not None or self._entry_y is not None:
            parts.extend(['entryDx=0', 'entryDy=0'])
        return parts

    def _add_edge_waypoints(self, edge_cell, points):
        """Attach ``<Array as="points">`` waypoints to an edge's geometry.

    ``points`` is a sequence of ``(x, y)`` tuples in absolute page coordinates.
    Existing waypoints on the edge are replaced.

    Draw.io's orthogonal router honours these waypoints, so callers can use them
    to dog-leg an edge around an intervening class.
    """
        if not points:
            return
        geo = edge_cell.find('mxGeometry')
        if geo is None:
            geo = ET.SubElement(edge_cell, 'mxGeometry')
            geo.set('relative', '1')
            geo.set('as', 'geometry')
        for existing in geo.findall('Array'):
            geo.remove(existing)
        arr = ET.SubElement(geo, 'Array')
        arr.set('as', 'points')
        for x, y in points:
            pt = ET.SubElement(arr, 'mxPoint')
            pt.set('x', str(int(round(x))))
            pt.set('y', str(int(round(y))))

    def _set_edge_anchors(self, cell, _rest):
        exit_x, exit_y, entry_x, entry_y = _rest
        'Set or update exit/entry anchor points on an existing edge cell.'
        style = cell.get('style', '')
        for key in ('exitX', 'exitY', 'entryX', 'entryY', 'exitDx', 'exitDy', 'entryDx', 'entryDy'):
            style = re.sub(f'{key}=[^;]*;?', '', style)
        style = style.rstrip(';') + ';'
        parts = self._anchor_style_parts((exit_x, exit_y, entry_x, entry_y))
        if parts:
            style += ';'.join(parts) + ';'
        cell.set('style', style)

    def _anchor_style_parts(self, anchors):
        exit_x, exit_y, entry_x, entry_y = anchors
        parts = []
        if exit_x is not None:
            parts.append(f'exitX={exit_x}')
        if exit_y is not None:
            parts.append(f'exitY={exit_y}')
        if exit_x is not None or exit_y is not None:
            parts.append('exitDx=0')
            parts.append('exitDy=0')
        if entry_x is not None:
            parts.append(f'entryX={entry_x}')
        if entry_y is not None:
            parts.append(f'entryY={entry_y}')
        if entry_x is not None or entry_y is not None:
            parts.append('entryDx=0')
            parts.append('entryDy=0')
        return parts

    def _delete_cell(self, root, cell):
        """Remove a cell from root."""
        root.remove(cell)

    def _delete_class_and_edges(self, root, class_name):
        """Remove a class cell and all edges connected to it."""
        cell = self._find_cell_by_name(root, class_name)
        if cell is None:
            return False
        cell_id = cell.get('id')
        edges_to_remove = []
        for edge in root.findall('mxCell'):
            if edge.get('edge') != '1':
                continue
            if edge.get('source') == cell_id or edge.get('target') == cell_id:
                edges_to_remove.append(edge)
        for e in edges_to_remove:
            root.remove(e)
        root.remove(cell)
        return True

    def _delete_edge_between(self, root, _rest):
        source_name, target_name = _rest
        'Remove edge(s) between two named classes. Returns count removed.'
        source_cell = self._find_cell_by_name(root, source_name)
        target_cell = self._find_cell_by_name(root, target_name)
        if source_cell is None or target_cell is None:
            return 0
        source_id = source_cell.get('id')
        target_id = target_cell.get('id')
        to_remove = []
        for edge in root.findall('mxCell'):
            if edge.get('edge') != '1':
                continue
            s, t = (edge.get('source', ''), edge.get('target', ''))
            if s == source_id and t == target_id or (s == target_id and t == source_id):
                to_remove.append(edge)
        for e in to_remove:
            root.remove(e)
        return len(to_remove)

    def _read_classes_from_page(self, root):
        """Read all class data from a DrawIO page root. Returns list of concept dicts."""
        concepts = []
        for cell in root.findall('mxCell'):
            if cell.get('vertex') != '1':
                continue
            value = cell.get('value', '')
            name = self._extract_class_name(value)
            if not name:
                continue
            full_name, base, props, ops, invs = self._parse_class_html(value)
            concepts.append({'name': full_name or name, 'base': base, 'properties': props, 'operations': ops, 'invariants': invs})
        return concepts

    def _concept_to_md(self, concept):
        """Render a single concept dict to domain-model.md format."""
        name = concept['name']
        base = concept.get('base')
        header = f'**{name}**' + (f' : {base}' if base else '')
        lines = [header]
        for p in concept.get('properties', []):
            lines.append(f'- {p}')
        ops = concept.get('operations', [])
        if ops:
            lines.append('- Operations:')
            for o in ops:
                lines.append(f'  - {o}')
        for inv in concept.get('invariants', []):
            lines.append(f'- Invariant: {inv}')
        return '\n'.join(lines)

    def _parse_model_sections(self, md_text):
        """Parse domain-model.md into sections by foundational model name."""
        self._section_state = {
            'sections': {},
            'current_name': None,
            'current_start': None,
            'preamble_lines': [],
            'domain_model_started': False,
            'concepts_lines': [],
            'extensions_lines': [],
            'in_extensions': False,
        }
        for i, line in enumerate(md_text.split('\n')):
            self._consume_model_section_line(i, line)
        self._flush_model_section()
        return self._section_state['sections']

    def _flush_model_section(self) -> None:
        state = self._section_state
        if not state['current_name']:
            return
        state['sections'][state['current_name']] = {
            'preamble': '\n'.join(state['preamble_lines']),
            'concepts_text': '\n'.join(state['concepts_lines']),
            'extensions_text': '\n'.join(state['extensions_lines']),
            'start': state['current_start'],
        }

    def _consume_model_section_line(self, index, line) -> None:
        state = self._section_state
        if line.startswith('## ') and (not line.startswith('###')):
            self._flush_model_section()
            state['current_name'] = line[3:].strip()
            state['current_start'] = index
            state['preamble_lines'] = []
            state['concepts_lines'] = []
            state['extensions_lines'] = []
            state['domain_model_started'] = False
            state['in_extensions'] = False
            return
        if line.strip() == '### Domain Model':
            state['domain_model_started'] = True
            return
        if line.strip().startswith('### Extensions'):
            state['in_extensions'] = True
            return
        if not state['current_name']:
            return
        if not state['domain_model_started'] and (not state['in_extensions']):
            state['preamble_lines'].append(line)
            return
        if state['in_extensions']:
            state['extensions_lines'].append(line)
            return
        if state['domain_model_started']:
            state['concepts_lines'].append(line)

    def _parse_concepts_from_md(self, concepts_text):
        """Parse concept blocks from the concepts portion of a model section."""
        self._md_concepts = []
        self._md_current = None
        self._md_in_operations = False
        for line in concepts_text.split('\n'):
            self._apply_md_concept_line(line.strip())
        if self._md_current:
            self._md_concepts.append(self._md_current)
        return self._md_concepts

    def _apply_md_concept_line(self, stripped) -> None:
        if stripped.startswith('**') and (not stripped.startswith('**Rollable extensions')):
            self._start_md_concept(stripped)
            return
        current = self._md_current
        if current is None:
            return
        if stripped == '- Operations:':
            self._md_in_operations = True
            return
        if stripped.startswith('- Invariant:'):
            self._md_in_operations = False
            current['invariants'].append(stripped[len('- Invariant:'):].strip())
            return
        if stripped.startswith('- examples:'):
            self._md_in_operations = False
            return
        if self._md_in_operations and stripped.startswith('- '):
            current['operations'].append(stripped[2:].strip())
            return
        if (not self._md_in_operations) and stripped.startswith('- ') and (not stripped.startswith('- Operations')):
            prop = stripped[2:].strip()
            if prop:
                current['properties'].append(prop)

    def _start_md_concept(self, stripped) -> None:
        match = re.match('\\*\\*(\\w+)\\*\\*(?:\\s*:\\s*(\\w+))?', stripped)
        if not match:
            return
        if self._md_current:
            self._md_concepts.append(self._md_current)
        self._md_current = {'name': match.group(1), 'base': match.group(2), 'properties': [], 'operations': [], 'invariants': []}
        self._md_in_operations = False

    def _diff_concept(self, old, new):
        """Compare two concept dicts. Returns list of diff strings, empty if identical."""
        diffs = []
        if old.get('base') != new.get('base'):
            diffs.append(f"base: {old.get('base') or '(none)'} -> {new.get('base') or '(none)'}")
        diffs.extend(self._diff_named_list(old['properties'], (new['properties'], 'prop')))
        diffs.extend(self._diff_named_list(old['operations'], (new['operations'], 'op')))
        diffs.extend(self._diff_named_list(old['invariants'], (new['invariants'], 'inv')))
        return diffs

    def _diff_named_list(self, old_items, labeled):
        new_items, label = labeled
        diffs = []
        for item in new_items:
            if item not in old_items:
                diffs.append(f'+ {label}: {item}')
        for item in old_items:
            if item not in new_items:
                diffs.append(f'- {label}: {item}')
        return diffs

    def _sync_page_to_model(self, drawio_path, _rest):
        page_name, md_path = _rest
        'Sync classes from a DrawIO page back to domain-model.md.\n    Returns a dict describing changes: {added: [], removed: [], updated: []}.\n    '
        _, mxfile = self._load_drawio(drawio_path)
        _, root = self._get_page(mxfile, page_name)
        if root is None:
            raise ValueError(f"Page '{page_name}' not found in {drawio_path}")
        diagram_concepts = self._read_classes_from_page(root)
        md_text = Path(md_path).read_text(encoding='utf-8')
        sections = self._parse_model_sections(md_text)
        if page_name not in sections:
            raise ValueError(f"Section '{page_name}' not found in {md_path}")
        section = sections[page_name]
        changes = self._sync_concept_changes(diagram_concepts, self._parse_concepts_from_md(section['concepts_text']))
        self._rewrite_model_section((md_path, md_text, page_name, section, diagram_concepts))
        return changes

    def _sync_concept_changes(self, diagram_concepts, md_concepts):
        diagram_by_name = {c['name']: c for c in diagram_concepts}
        md_by_name = {c['name']: c for c in md_concepts}
        changes = {'added': [], 'removed': [], 'updated': []}
        for name in diagram_by_name:
            if name not in md_by_name:
                changes['added'].append({'name': name, 'concept': diagram_by_name[name]})
        for name in md_by_name:
            if name not in diagram_by_name:
                changes['removed'].append({'name': name, 'concept': md_by_name[name]})
        for name in diagram_by_name:
            if name not in md_by_name:
                continue
            diffs = self._diff_concept(md_by_name[name], diagram_by_name[name])
            if diffs:
                changes['updated'].append({'name': name, 'diffs': diffs})
        return changes

    def _rewrite_model_section(self, parts) -> None:
        md_path, md_text, page_name, section, diagram_concepts = parts
        new_concepts_lines = []
        for dc in diagram_concepts:
            new_concepts_lines.append('')
            new_concepts_lines.append(self._concept_to_md(dc))
        new_section_body = section['preamble'].rstrip() + '\n\n### Domain Model\n' + '\n'.join(new_concepts_lines) + '\n\n### Extensions\n' + section['extensions_text']
        lines = md_text.split('\n')
        end_line = self._section_end_line(lines, (section['start'], page_name))
        new_lines = lines[:section['start']]
        new_lines.append(f'## {page_name}')
        new_lines.append('')
        new_lines.append(new_section_body.rstrip())
        new_lines.append('')
        new_lines.extend(lines[end_line:])
        Path(md_path).write_text('\n'.join(new_lines), encoding='utf-8')

    def _section_end_line(self, lines, span) -> int:
        section_start, page_name = span
        next_section_start = len(lines)
        found_current = False
        for i, line in enumerate(lines):
            if not (line.startswith('## ') and (not line.startswith('###'))):
                continue
            if found_current:
                next_section_start = i
                break
            if line[3:].strip() == page_name:
                found_current = True
        for i in range(next_section_start - 1, section_start, -1):
            if lines[i].strip() == '---':
                return i
        return next_section_start

    def _eap_parse_style(self, style: str) -> dict:
        out: dict = {}
        for kv in (style or '').split(';'):
            if '=' not in kv:
                continue
            key, value = kv.split('=', 1)
            try:
                out[key] = float(value)
            except ValueError:
                continue
        return out

    def _eap_anchor_side(self, frac_x, frac_y):
        if frac_x is None or frac_y is None:
            return None
        if abs(frac_x - 0) < 0.001:
            return 'left'
        if abs(frac_x - 1) < 0.001:
            return 'right'
        if abs(frac_y - 0) < 0.001:
            return 'top'
        if abs(frac_y - 1) < 0.001:
            return 'bottom'
        return None

    def _eap_seg_orient(self, seg):
        (x1, y1), (x2, y2) = seg
        dx, dy = (abs(x2 - x1), abs(y2 - y1))
        if dx < 1 and dy < 1:
            return None
        if dx < 1:
            return 'v'
        if dy < 1:
            return 'h'
        return None

    def _eap_seg_dir_signed(self, seg):
        (x1, y1), (x2, y2) = seg
        dx, dy = (x2 - x1, y2 - y1)
        if abs(dx) < 1 and abs(dy) < 1:
            return None
        if abs(dx) >= abs(dy):
            return 'right' if dx > 0 else 'left'
        return 'down' if dy > 0 else 'up'

    def _eap_expected_orient(self, side):
        return {'left': 'h', 'right': 'h', 'top': 'v', 'bottom': 'v'}.get(side or '')

    def _eap_outward(self, side):
        return {'left': 'left', 'right': 'right', 'top': 'up', 'bottom': 'down'}.get(side or '')

    def _eap_inward(self, side):
        return {'left': 'right', 'right': 'left', 'top': 'down', 'bottom': 'up'}.get(side or '')

    def _eap_classify_edge(self, style: str) -> str:
        style = (style or '').lower()
        if 'endarrow=block' in style and 'startarrow=block' not in style:
            if 'endfill=0' in style:
                return 'inheritance-orthogonal' if 'orthogonal' in style else 'inheritance'
            return 'association'
        if 'startarrow=diamondthin' in style or 'startarrow=diamond' in style:
            return 'composition' if 'startfill=1' in style else 'aggregation'
        return 'association'

    def _check_edges_approach_perpendicular(self, root) -> list:
        """Return list of (edge_desc, end, side, expected_dir, actual_dir) for violations."""
        classes = self._get_all_classes(root)
        self._id_to_name = {cid: name for cid, name, *_ in classes}
        self._id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}
        violations = []
        for cell in root.findall('mxCell'):
            self._record_eap_edge(cell, violations)
        return violations

    def _record_eap_edge(self, cell, violations) -> None:
        if cell.get('edge') != '1':
            return
        src_id = cell.get('source', '')
        tgt_id = cell.get('target', '')
        if src_id not in self._id_to_name or tgt_id not in self._id_to_name:
            return
        style = cell.get('style', '')
        attrs = self._eap_parse_style(style)
        segs, _ = self._compute_edge_segments_ex(cell, self._id_to_geo)
        if not segs:
            return
        etype = self._eap_classify_edge(style)
        self._approach_desc = f'{self._id_to_name[src_id]}->{self._id_to_name[tgt_id]} ({etype})'
        self._approach_end = 'source'
        self._approach_side = self._eap_anchor_side(attrs.get('exitX'), attrs.get('exitY'))
        self._append_eap_end(violations, segs[0])
        self._approach_end = 'target'
        self._approach_side = self._eap_anchor_side(attrs.get('entryX'), attrs.get('entryY'))
        self._append_eap_end(violations, segs[-1])

    def _append_eap_end(self, violations, seg) -> None:
        side = self._approach_side
        end = self._approach_end
        desc = self._approach_desc
        expected = self._eap_expected_orient(side)
        actual = self._eap_seg_orient(seg)
        if expected and actual and (actual != expected):
            violations.append((desc, end, side, expected, actual))
            return
        want = self._eap_outward(side) if end == 'source' else self._eap_inward(side)
        got = self._eap_seg_dir_signed(seg)
        if want and got and (got != want):
            violations.append((desc, end, side, want, got))

    def _check_leaf_nodes_horizontal_row(self, root) -> list:
        """Return list of violation strings for hubs with 4+ leaves in a wide horizontal row."""
        self._leaf_geo = self._page_vertex_geo(root)
        neighbours = self._hub_neighbours(root)
        violations = []
        for hub_id, leaf_ids in neighbours.items():
            violations.extend(self._wide_leaf_row_hits(root, (hub_id, leaf_ids)))
        return violations

    def _page_vertex_geo(self, root) -> dict:
        geo: dict = {}
        for cell in root.findall('mxCell'):
            if cell.get('vertex') != '1':
                continue
            geometry = cell.find('mxGeometry')
            if geometry is None:
                continue
            w = geometry.get('width')
            h = geometry.get('height')
            if w is None or h is None:
                continue
            geo[cell.get('id', '')] = (float(geometry.get('x', 0)), float(geometry.get('y', 0)), float(w), float(h))
        return geo

    def _hub_neighbours(self, root) -> dict:
        neighbours: dict = {}
        geo = self._leaf_geo
        for cell in root.findall('mxCell'):
            if cell.get('edge') != '1':
                continue
            src = cell.get('source')
            tgt = cell.get('target')
            if src and tgt and (src in geo):
                neighbours.setdefault(src, set()).add(tgt)
        return neighbours

    def _wide_leaf_row_hits(self, root, hub) -> list:
        hub_id, leaf_ids = hub
        if len(leaf_ids) < _LEAF_ROW_MIN_SIZE:
            return []
        geo = self._leaf_geo
        hits = []
        for members in self._leaf_row_groups(leaf_ids).values():
            hit = self._wide_row_message(root, (hub_id, members))
            if hit:
                hits.append(hit)
        return hits

    def _leaf_row_groups(self, leaf_ids) -> dict:
        geo = self._leaf_geo
        row_groups: dict = {}
        for lid in leaf_ids:
            if lid not in geo:
                continue
            bucket = round(geo[lid][1] / _LEAF_ROW_Y_TOLERANCE)
            row_groups.setdefault(bucket, []).append(lid)
        return row_groups

    def _wide_row_message(self, root, members) -> str | None:
        hub_id, member_ids = members
        if len(member_ids) < _LEAF_ROW_MIN_SIZE:
            return None
        geo = self._leaf_geo
        y_vals = [geo[m][1] for m in member_ids]
        x_vals = [geo[m][0] for m in member_ids]
        y_spread = max(y_vals) - min(y_vals)
        x_spread = max(x_vals) - min(x_vals)
        if y_spread > _LEAF_ROW_Y_TOLERANCE or x_spread <= 600:
            return None
        hub_name = self._hub_display_name(root, hub_id)
        return f'{hub_name} has {len(member_ids)} leaf neighbours in a horizontal row (y~{int(sum(y_vals) / len(y_vals))}, x-span={int(x_spread)}px)'

    def _hub_display_name(self, root, hub_id) -> str:
        hub_cell = root.find(f"mxCell[@id='{hub_id}']")
        if hub_cell is None:
            return hub_id
        raw = hub_cell.get('value') or hub_id
        text = re.sub('<[^>]+>', '', raw)
        text = re.sub('&[a-z]+;', ' ', text)
        return re.split('[\\s+]', text.strip())[0] or hub_id
