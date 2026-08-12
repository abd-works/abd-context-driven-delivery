"""
DrawIO class diagram toolkit — core XML read/write functions.

All CLI commands use these shared functions to manipulate DrawIO files.
"""

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path


CELL_WIDTH = 260
CELL_MIN_HEIGHT = 80
LINE_HEIGHT = 16
SECTION_PAD = 8

CLASS_STYLE = (
    "verticalAlign=top;align=left;overflow=fill;"
    "fontSize=12;fontFamily=Helvetica;html=1;whiteSpace=wrap;"
)

CLASS_STYLE_IMPORT = (
    "verticalAlign=top;align=left;overflow=fill;"
    "fontSize=12;fontFamily=Helvetica;html=1;whiteSpace=wrap;"
    "dashed=1;dashPattern=8 4;strokeColor=#999999;fontColor=#666666;"
)

EDGE_ORTHOGONAL = "edgeStyle=orthogonalEdgeStyle;rounded=1;"

EDGE_STYLES = {
    "inheritance": "endArrow=block;endSize=16;endFill=0;html=1;",
    "inheritance-orthogonal": f"{EDGE_ORTHOGONAL}endArrow=block;endSize=16;endFill=0;html=1;",
    "composition": f"{EDGE_ORTHOGONAL}endArrow=none;html=1;startArrow=diamondThin;startFill=1;startSize=14;",
    "aggregation": f"{EDGE_ORTHOGONAL}endArrow=none;html=1;startArrow=diamondThin;startFill=0;startSize=14;",
    "association": f"{EDGE_ORTHOGONAL}endArrow=open;endSize=12;html=1;",
    "association-straight": "endArrow=open;endSize=12;html=1;",
    "composition-straight": "endArrow=none;html=1;startArrow=diamondThin;startFill=1;startSize=14;",
    "aggregation-straight": "endArrow=none;html=1;startArrow=diamondThin;startFill=0;startSize=14;",
    "dependency": "endArrow=open;endSize=12;dashed=1;html=1;",
    "dependency-orthogonal": f"{EDGE_ORTHOGONAL}endArrow=open;endSize=12;dashed=1;html=1;",
}


def escape(text):
    return html.escape(str(text), quote=True)


def unescape(text):
    return html.unescape(str(text))


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def load_drawio(path):
    """Load a DrawIO file. Returns (tree, root_element)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    tree = ET.parse(str(path))
    return tree, tree.getroot()


def save_drawio(path, root_element):
    """Write an mxfile element tree to disk."""
    path = Path(path)
    tree = ET.ElementTree(root_element)
    ET.indent(tree, space="  ")
    tree.write(str(path), encoding="unicode", xml_declaration=False)


def create_empty_mxfile():
    """Create a new empty mxfile element."""
    return ET.fromstring('<mxfile host="drawio_tools.py"></mxfile>')


def get_page(mxfile, page_name=None):
    """Get a diagram page by name. Returns (diagram_element, root_cell_parent).
    If page_name is None, returns the first page."""
    diagrams = mxfile.findall("diagram")
    if page_name:
        for d in diagrams:
            if d.get("name") == page_name:
                model = d.find("mxGraphModel")
                root = model.find("root") if model is not None else None
                return d, root
        return None, None
    if diagrams:
        d = diagrams[0]
        model = d.find("mxGraphModel")
        root = model.find("root") if model is not None else None
        return d, root
    return None, None


def add_page(mxfile, page_name, page_width=1600, page_height=1200):
    """Add a new diagram page to the mxfile. Returns (diagram, root)."""
    diagram = ET.SubElement(mxfile, "diagram")
    diagram.set("id", f"page_{page_name.replace(' ', '_').lower()}")
    diagram.set("name", page_name)

    model = ET.SubElement(diagram, "mxGraphModel")
    model.set("dx", "1200")
    model.set("dy", "800")
    model.set("grid", "1")
    model.set("gridSize", "10")
    model.set("guides", "1")
    model.set("tooltips", "1")
    model.set("connect", "1")
    model.set("arrows", "1")
    model.set("fold", "1")
    model.set("page", "1")
    model.set("pageScale", "1")
    model.set("pageWidth", str(page_width))
    model.set("pageHeight", str(page_height))
    model.set("math", "0")
    model.set("shadow", "0")

    root = ET.SubElement(model, "root")
    cell0 = ET.SubElement(root, "mxCell")
    cell0.set("id", "0")
    cell1 = ET.SubElement(root, "mxCell")
    cell1.set("id", "1")
    cell1.set("parent", "0")

    return diagram, root


# ---------------------------------------------------------------------------
# Cell lookup
# ---------------------------------------------------------------------------

def next_id(root):
    """Find the next available integer cell id."""
    max_id = 1
    for cell in root.iter("mxCell"):
        try:
            max_id = max(max_id, int(cell.get("id", "0")))
        except ValueError:
            pass
    return max_id + 1


def _extract_class_name(value):
    """Extract class name from the HTML value of a class cell.
    The name is in the <b> tag. Stereotype (if any) is in a separate <i> tag."""
    if not value:
        return None
    match = re.search(r"<b>([^<]+)</b>", unescape(value))
    if match:
        name = match.group(1).strip()
        if " : " in name:
            name = name.split(" : ")[0].strip()
        return name
    return None


def find_cell_by_name(root, class_name):
    """Find a class mxCell by its displayed name."""
    for cell in root.findall("mxCell"):
        value = cell.get("value", "")
        extracted = _extract_class_name(value)
        if extracted == class_name:
            return cell
    return None


def find_cell_by_id(root, cell_id):
    """Find an mxCell by its id attribute."""
    for cell in root.findall("mxCell"):
        if cell.get("id") == str(cell_id):
            return cell
    return None


def get_all_classes(root):
    """Return list of (cell_id, class_name, x, y, w, h) for all class cells."""
    classes = []
    for cell in root.findall("mxCell"):
        if cell.get("vertex") != "1":
            continue
        name = _extract_class_name(cell.get("value", ""))
        if not name:
            continue
        geo = get_geometry(cell)
        if geo:
            classes.append((cell.get("id"), name, *geo))
    return classes


def get_all_edges(root):
    """Return list of (cell_id, edge_type, source_id, target_id) for all edges."""
    edges = []
    for cell in root.findall("mxCell"):
        if cell.get("edge") != "1":
            continue
        style = cell.get("style", "")
        source = cell.get("source", "")
        target = cell.get("target", "")
        edge_type = _classify_edge(style)
        edges.append((cell.get("id"), edge_type, source, target))
    return edges


def _classify_edge(style):
    """Determine edge type from style string."""
    is_orthogonal = "orthogonalEdgeStyle" in style
    if "endFill=0" in style and "endArrow=block" in style:
        return "inheritance-orthogonal" if is_orthogonal else "inheritance"
    if "startFill=1" in style and "diamondThin" in style:
        return "composition"
    if "startFill=0" in style and "diamondThin" in style:
        return "aggregation"
    if "dashed=1" in style and "endArrow=open" in style:
        return "dependency-orthogonal" if is_orthogonal else "dependency"
    if "endArrow=open" in style:
        return "association"
    return "unknown"


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def get_geometry(cell):
    """Return (x, y, width, height) from a cell's mxGeometry, or None."""
    geo = cell.find("mxGeometry")
    if geo is None:
        return None
    return (
        float(geo.get("x", "0")),
        float(geo.get("y", "0")),
        float(geo.get("width", "0")),
        float(geo.get("height", "0")),
    )


def set_geometry(cell, x=None, y=None, w=None, h=None):
    """Update position and/or size on a cell's mxGeometry."""
    geo = cell.find("mxGeometry")
    if geo is None:
        geo = ET.SubElement(cell, "mxGeometry")
        geo.set("as", "geometry")
    if x is not None:
        geo.set("x", str(int(x)))
    if y is not None:
        geo.set("y", str(int(y)))
    if w is not None:
        geo.set("width", str(int(w)))
    if h is not None:
        geo.set("height", str(int(h)))


def check_overlaps(classes):
    """Return list of overlapping pairs: [(name_a, name_b), ...]."""
    overlaps = []
    for i, (_, name_a, xa, ya, wa, ha) in enumerate(classes):
        for j, (_, name_b, xb, yb, wb, hb) in enumerate(classes):
            if j <= i:
                continue
            if xa < xb + wb and xa + wa > xb and ya < yb + hb and ya + ha > yb:
                overlaps.append((name_a, name_b))
    return overlaps


def _rect_center(x, y, w, h):
    """Return center point of a rectangle."""
    return (x + w / 2, y + h / 2)


def _line_intersects_rect(x1, y1, x2, y2, rx, ry, rw, rh, margin=5):
    """Check if line segment (x1,y1)-(x2,y2) passes through rectangle (rx,ry,rw,rh).
    Uses margin to detect near-misses (edges that visually touch)."""
    rx -= margin
    ry -= margin
    rw += 2 * margin
    rh += 2 * margin

    def _ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)

    def _segments_cross(ax, ay, bx, by, cx, cy, dx, dy):
        return (_ccw(ax, ay, cx, cy, dx, dy) != _ccw(bx, by, cx, cy, dx, dy) and
                _ccw(ax, ay, bx, by, cx, cy) != _ccw(ax, ay, bx, by, dx, dy))

    corners = [
        (rx, ry), (rx + rw, ry),
        (rx + rw, ry + rh), (rx, ry + rh),
    ]
    sides = [
        (corners[0], corners[1]), (corners[1], corners[2]),
        (corners[2], corners[3]), (corners[3], corners[0]),
    ]
    for (cx, cy), (dx, dy) in sides:
        if _segments_cross(x1, y1, x2, y2, cx, cy, dx, dy):
            return True

    if rx <= x1 <= rx + rw and ry <= y1 <= ry + rh:
        return True
    return False


def _orthogonal_crosses_rect(src_geo, tgt_geo, rx, ry, rw, rh, margin=5):
    """Approximate check: does an orthogonal edge between two classes cross a third?
    Orthogonal edges go horizontal then vertical (or vice versa). We check both
    possible L-shaped paths and report a crossing if BOTH paths hit the obstacle."""
    sx, sy, sw, sh = src_geo
    tx, ty, tw, th = tgt_geo
    scx, scy = _rect_center(*src_geo)
    tcx, tcy = _rect_center(*tgt_geo)

    path_a_crosses = (
        _line_intersects_rect(scx, scy, tcx, scy, rx, ry, rw, rh, margin) or
        _line_intersects_rect(tcx, scy, tcx, tcy, rx, ry, rw, rh, margin)
    )
    path_b_crosses = (
        _line_intersects_rect(scx, scy, scx, tcy, rx, ry, rw, rh, margin) or
        _line_intersects_rect(scx, tcy, tcx, tcy, rx, ry, rw, rh, margin)
    )
    return path_a_crosses and path_b_crosses


def check_edge_crossings(root):
    """Check if any edge passes through a class it is not connected to.
    Returns list of (edge_desc, crossed_class_name) tuples."""
    classes = get_all_classes(root)
    edges = get_all_edges(root)
    id_to_name = {cid: name for cid, name, *_ in classes}
    id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}

    crossings = []
    for eid, etype, src_id, tgt_id in edges:
        src_name = id_to_name.get(src_id, "?")
        tgt_name = id_to_name.get(tgt_id, "?")
        src_geo = id_to_geo.get(src_id)
        tgt_geo = id_to_geo.get(tgt_id)
        if src_geo is None or tgt_geo is None:
            continue

        is_straight = etype in ("inheritance", "dependency",
                                "association-straight", "composition-straight",
                                "aggregation-straight")

        for cid, cname, cx, cy, cw, ch in classes:
            if cid in (src_id, tgt_id):
                continue

            if is_straight:
                scx, scy = _rect_center(*src_geo)
                tcx, tcy = _rect_center(*tgt_geo)
                if _line_intersects_rect(scx, scy, tcx, tcy, cx, cy, cw, ch):
                    crossings.append((f"{src_name}->{tgt_name} ({etype})", cname))
            else:
                if _orthogonal_crosses_rect(src_geo, tgt_geo, cx, cy, cw, ch):
                    crossings.append((f"{src_name}->{tgt_name} ({etype})", cname))

    return crossings


def check_shared_anchors(root):
    """Detect edges that share the same anchor point on the same class.

    Groups edges by the (class_id, exit/entry_x, exit/entry_y) anchor.  When
    explicit anchors are set in the style, those are used; otherwise the
    default center anchor is assumed.  Reports a conflict only when two or
    more edges share the *exact same* anchor coordinates on the same class.
    """
    classes = get_all_classes(root)
    id_to_name = {cid: name for cid, name, *_ in classes}
    id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}

    anchor_map = {}

    for cell in root.findall("mxCell"):
        if cell.get("edge") != "1":
            continue
        style = cell.get("style", "")
        src_id = cell.get("source", "")
        tgt_id = cell.get("target", "")
        src_name = id_to_name.get(src_id, "?")
        tgt_name = id_to_name.get(tgt_id, "?")
        etype = _classify_edge(style)
        desc = f"{src_name}->{tgt_name} ({etype})"

        ex = _parse_style_float(style, "exitX")
        ey = _parse_style_float(style, "exitY")
        src_anchor = (round(ex, 2) if ex is not None else "def",
                      round(ey, 2) if ey is not None else "def")

        nx = _parse_style_float(style, "entryX")
        ny = _parse_style_float(style, "entryY")
        tgt_anchor = (round(nx, 2) if nx is not None else "def",
                      round(ny, 2) if ny is not None else "def")

        key_src = (src_id, "exit", src_anchor)
        key_tgt = (tgt_id, "entry", tgt_anchor)

        anchor_map.setdefault(key_src, []).append(desc)
        anchor_map.setdefault(key_tgt, []).append(desc)

    conflicts = []
    for (cid, end, anchor), descs in anchor_map.items():
        if len(descs) > 1:
            cls_name = id_to_name.get(cid, "?")
            anchor_label = f"{end}({anchor[0]},{anchor[1]})"
            conflicts.append((cls_name, anchor_label, descs))
    return conflicts


def _parse_style_float(style, key):
    """Extract a float value from a Draw.io style string, e.g. 'exitX=0.3'."""
    m = re.search(rf"{key}=([0-9.]+)", style)
    return float(m.group(1)) if m else None


def _edge_anchor_point(style, cell_geo, end="exit"):
    """Compute the absolute (x, y) anchor point for one end of an edge.

    Reads exitX/exitY or entryX/entryY from the style.  Falls back to the
    centre of the class box when no explicit anchor is set.
    """
    x, y, w, h = cell_geo
    ax = _parse_style_float(style, f"{end}X")
    ay = _parse_style_float(style, f"{end}Y")
    if ax is not None and ay is not None:
        return (x + w * ax, y + h * ay)
    return _rect_center(x, y, w, h)


def _compute_edge_segments(edge_cell, id_to_geo):
    """Compute the polyline segments of an edge.

    For straight edges: one segment from source anchor to target anchor.
    For orthogonal edges with explicit waypoints: follow those waypoints.
    For orthogonal edges without waypoints: approximate using both possible
    L-shaped routes (H-V and V-H) and return the one less likely to cross.

    Returns a list of ((x1,y1),(x2,y2)) segments, and a boolean
    ``is_approximate`` indicating whether the route is a best-guess.
    Callers that need is_approximate can call _compute_edge_segments_ex.
    """
    segs, _ = _compute_edge_segments_ex(edge_cell, id_to_geo)
    return segs


def _compute_edge_segments_ex(edge_cell, id_to_geo):
    """Like _compute_edge_segments but also returns is_approximate flag."""
    style = edge_cell.get("style", "")
    src_id = edge_cell.get("source", "")
    tgt_id = edge_cell.get("target", "")
    src_geo = id_to_geo.get(src_id)
    tgt_geo = id_to_geo.get(tgt_id)
    if src_geo is None or tgt_geo is None:
        return [], False

    p1 = _edge_anchor_point(style, src_geo, "exit")
    p2 = _edge_anchor_point(style, tgt_geo, "entry")

    is_orthogonal = "orthogonal" in style.lower() or "edgestyle=orthogonal" in style.lower()
    if not is_orthogonal:
        return [(p1, p2)], False

    geo = edge_cell.find("mxGeometry")
    waypoints = []
    if geo is not None:
        arr = geo.find("Array")
        if arr is not None:
            for pt in arr.findall("mxPoint"):
                px = float(pt.get("x", "0"))
                py = float(pt.get("y", "0"))
                waypoints.append((px, py))

    def _expand_orthogonal_seg(pa, pb, prev_dir):
        """Return list of points (excluding ``pa``) representing the H-V or
        V-H expansion of segment ``pa→pb`` (or a single point if it is
        already axis-aligned). ``prev_dir`` is the direction of the
        previous segment ("h", "v" or None).
        """
        ax, ay = pa
        bx, by = pb
        if abs(bx - ax) < 1 or abs(by - ay) < 1:
            return [(bx, by)], ("v" if abs(bx - ax) < 1 else "h")
        # Diagonal. Follow the previous direction first so the rendered
        # geometry doesn't ricochet.
        if prev_dir == "v":
            corner = (ax, by)
            return [corner, (bx, by)], "h"
        corner = (bx, ay)
        return [corner, (bx, by)], "v"

    if waypoints:
        points = [p1] + waypoints + [p2]
        # Walk consecutive pairs, expanding any diagonal so the audit sees
        # what drawio renders. The is_approximate flag stays False because
        # we explicitly have route geometry.
        expanded = [points[0]]
        prev_dir = None
        for i in range(len(points) - 1):
            next_pts, prev_dir = _expand_orthogonal_seg(
                expanded[-1], points[i + 1], prev_dir
            )
            expanded.extend(next_pts)
        return [
            (expanded[i], expanded[i + 1]) for i in range(len(expanded) - 1)
        ], False

    x1, y1 = p1
    x2, y2 = p2
    if abs(x2 - x1) < 1 or abs(y2 - y1) < 1:
        return [(p1, p2)], False

    mid_x = (x1 + x2) / 2
    return [
        (p1, (mid_x, y1)),
        ((mid_x, y1), (mid_x, y2)),
        ((mid_x, y2), p2),
    ], True


def _segments_overlap_1d(a_start, a_end, b_start, b_end, threshold=8):
    """Check whether two 1D intervals overlap by more than *threshold* pixels."""
    lo_a, hi_a = min(a_start, a_end), max(a_start, a_end)
    lo_b, hi_b = min(b_start, b_end), max(b_start, b_end)
    overlap = min(hi_a, hi_b) - max(lo_a, lo_b)
    return overlap > threshold


def _edge_segments_overlap(seg_a, seg_b, proximity=12):
    """Check whether two line segments visually overlap (run parallel and
    close together for a shared span).  Works for axis-aligned segments
    produced by orthogonal routing.
    """
    (ax1, ay1), (ax2, ay2) = seg_a
    (bx1, by1), (bx2, by2) = seg_b

    a_horiz = abs(ay2 - ay1) < 2
    a_vert = abs(ax2 - ax1) < 2
    b_horiz = abs(by2 - by1) < 2
    b_vert = abs(bx2 - bx1) < 2

    if a_horiz and b_horiz:
        if abs(ay1 - by1) < proximity:
            if _segments_overlap_1d(ax1, ax2, bx1, bx2):
                return True
    if a_vert and b_vert:
        if abs(ax1 - bx1) < proximity:
            if _segments_overlap_1d(ay1, ay2, by1, by2):
                return True

    return False


def check_edge_on_edge_overlaps(root):
    """Detect pairs of edges whose route segments visually overlap.

    Returns list of (edge_a_desc, edge_b_desc, detail) tuples.
    """
    classes = get_all_classes(root)
    edges_raw = get_all_edges(root)
    id_to_name = {cid: name for cid, name, *_ in classes}
    id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}

    edge_cells = []
    for cell in root.findall("mxCell"):
        if cell.get("edge") == "1":
            edge_cells.append(cell)

    edge_info = []
    for cell in edge_cells:
        src_id = cell.get("source", "")
        tgt_id = cell.get("target", "")
        src_name = id_to_name.get(src_id, "?")
        tgt_name = id_to_name.get(tgt_id, "?")
        etype = _classify_edge(cell.get("style", ""))
        desc = f"{src_name}->{tgt_name} ({etype})"
        segs = _compute_edge_segments(cell, id_to_geo)
        edge_info.append((desc, segs))

    overlaps = []
    for i, (desc_a, segs_a) in enumerate(edge_info):
        for j, (desc_b, segs_b) in enumerate(edge_info):
            if j <= i:
                continue
            for sa in segs_a:
                for sb in segs_b:
                    if _edge_segments_overlap(sa, sb):
                        overlaps.append((desc_a, desc_b,
                            f"segments {_fmt_seg(sa)} and {_fmt_seg(sb)} overlap"))
                        break
                else:
                    continue
                break

    return overlaps


def _fmt_seg(seg):
    (x1, y1), (x2, y2) = seg
    return f"({x1:.0f},{y1:.0f})->({x2:.0f},{y2:.0f})"


def check_edges_crossing_classes(root):
    """Check edges whose route segments pass through a class box they are
    not connected to.

    For straight edges and orthogonal edges with explicit waypoints the
    route is known exactly.  For orthogonal edges WITHOUT waypoints the
    route is approximated — Draw.io's auto-router may find a better path.
    Approximate crossings are tagged ``(approx)`` in the description so
    the agent can decide whether to fix or ignore them.

    Returns list of (edge_desc, crossed_class_name) tuples.
    """
    classes = get_all_classes(root)
    id_to_name = {cid: name for cid, name, *_ in classes}
    id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}

    crossings = []
    for cell in root.findall("mxCell"):
        if cell.get("edge") != "1":
            continue
        src_id = cell.get("source", "")
        tgt_id = cell.get("target", "")
        src_name = id_to_name.get(src_id, "?")
        tgt_name = id_to_name.get(tgt_id, "?")
        etype = _classify_edge(cell.get("style", ""))

        segs, is_approx = _compute_edge_segments_ex(cell, id_to_geo)
        suffix = " (approx)" if is_approx else ""
        desc = f"{src_name}->{tgt_name} ({etype}){suffix}"

        for cid, cname, cx, cy, cw, ch in classes:
            if cid in (src_id, tgt_id):
                continue
            for (x1, y1), (x2, y2) in segs:
                if _line_intersects_rect(x1, y1, x2, y2, cx, cy, cw, ch, margin=3):
                    crossings.append((desc, cname))
                    break

    return crossings


def validate_layout(root):
    """Validate diagram against class_diagram rules. Returns list of (rule, message) violations."""
    violations = []
    classes = get_all_classes(root)
    edges = get_all_edges(root)
    id_to_name = {cid: name for cid, name, *_ in classes}
    name_to_geo = {name: (x, y, w, h) for cid, name, x, y, w, h in classes}

    overlaps = check_overlaps(classes)
    for name_a, name_b in overlaps:
        violations.append(("class_overlap", f"{name_a} overlaps {name_b}"))

    crossings = check_edges_crossing_classes(root)
    for edge_desc, crossed in crossings:
        violations.append(("edge_crosses_class", f"Edge {edge_desc} crosses through {crossed}"))

    edge_overlaps = check_edge_on_edge_overlaps(root)
    for desc_a, desc_b, detail in edge_overlaps:
        violations.append(("edge_on_edge_overlap", f"{desc_a} overlaps {desc_b} — {detail}"))

    anchors = check_shared_anchors(root)
    for cls_name, side, descs in anchors:
        violations.append(("shared_anchor", f"{cls_name} {side}: {len(descs)} edges share default anchor — {', '.join(descs)}"))

    for eid, etype, src_id, tgt_id in edges:
        if etype not in ("inheritance", "inheritance-orthogonal"):
            continue
        src_name = id_to_name.get(src_id)
        tgt_name = id_to_name.get(tgt_id)
        if src_name is None or tgt_name is None:
            continue
        src_geo = name_to_geo.get(src_name)
        tgt_geo = name_to_geo.get(tgt_name)
        if src_geo is None or tgt_geo is None:
            continue
        _, child_y, _, _ = src_geo
        _, parent_y, _, _ = tgt_geo
        if child_y <= parent_y:
            violations.append(
                (
                    "hierarchy_flow",
                    f"Inheritance: {src_name} (y={child_y}) should be below parent {tgt_name} (y={parent_y}); base at top, children below",
                )
            )

    return violations


def audit_diagram(path, page_name=None):
    """Run all layout checks on one or all pages.  Returns a dict:
    {page_name: {"pass": bool, "violations": [(rule, msg), ...]}}
    Designed to be called from CLI or by the agent after every render.
    """
    _, mxfile = load_drawio(path)
    pages = []
    if page_name:
        pages = [(page_name,)]
    else:
        for d in mxfile.findall("diagram"):
            pages.append((d.get("name"),))

    results = {}
    for (pname,) in pages:
        _, root = get_page(mxfile, pname)
        if root is None:
            results[pname] = {"pass": False, "violations": [("page_missing", f"Page '{pname}' not found")]}
            continue
        v = validate_layout(root)
        results[pname] = {"pass": len(v) == 0, "violations": v}

    return results


def audit_diagram_report(path, page_name=None):
    """Human-readable audit report. Returns the text string."""
    results = audit_diagram(path, page_name)
    lines = []
    all_pass = True
    for pname, info in results.items():
        status = "PASS" if info["pass"] else "FAIL"
        if not info["pass"]:
            all_pass = False
        lines.append(f"\n=== Page: {pname} — {status} ===")
        if info["violations"]:
            for rule, msg in info["violations"]:
                lines.append(f"  [{rule}] {msg}")
        else:
            lines.append("  No issues found.")

    summary = "ALL PAGES PASS" if all_pass else "VIOLATIONS FOUND"
    lines.insert(0, f"Audit: {summary}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Class cell builder
# ---------------------------------------------------------------------------

def calc_cell_height(props_count, ops_count, inv_count):
    """Compute cell height from content line counts."""
    sections = 2
    if inv_count > 0:
        sections = 3
    content_lines = props_count + ops_count + inv_count
    return max(CELL_MIN_HEIGHT, 30 + content_lines * LINE_HEIGHT + sections * SECTION_PAD)


def build_class_html(name, base=None, properties=None, operations=None, invariants=None, stereotype=None):
    """Build the HTML value string for a UML class cell."""
    properties = properties or []
    operations = operations or []
    invariants = invariants or []

    base_label = f" : {escape(base)}" if base else ""
    stereotype_html = f'<i style="font-size:9px;color:#888;">{escape(stereotype)}</i><br/>' if stereotype else ""

    props_html = ""
    for p in properties:
        props_html += f"+ {escape(p)}<br/>"
    if not props_html:
        props_html = "<br/>"

    ops_html = ""
    for o in operations:
        ops_html += f"+ {escape(o)}<br/>"
    if not ops_html:
        ops_html = "<br/>"

    label = (
        f'<p style="margin:0px;margin-top:4px;text-align:center;">'
        f'{stereotype_html}'
        f'<b>{escape(name)}{base_label}</b></p>'
        f'<hr size="1"/>'
        f'<p style="margin:0px;margin-left:4px;font-size:10px;">{props_html}</p>'
        f'<hr size="1"/>'
        f'<p style="margin:0px;margin-left:4px;font-size:10px;">{ops_html}</p>'
    )

    if invariants:
        inv_html = ""
        for inv in invariants:
            short = inv[:80] + "..." if len(inv) > 80 else inv
            inv_html += f"<i>{escape(short)}</i><br/>"
        label += (
            f'<hr size="1"/>'
            f'<p style="margin:0px;margin-left:4px;font-size:9px;color:#666;">{inv_html}</p>'
        )

    return label


def parse_class_html(value):
    """Extract (name, base, properties, operations, invariants) from class cell HTML."""
    text = unescape(value)

    name = None
    base = None
    match = re.search(r"<b>([^<]+)</b>", text)
    if match:
        raw = match.group(1).strip()
        if " : " in raw:
            name, base = raw.split(" : ", 1)
            name = name.strip()
            base = base.strip()
        else:
            name = raw

    sections = re.split(r'<hr size="1"\s*/?>', text)

    properties = []
    operations = []
    invariants = []

    def extract_items(section_html):
        items = []
        for line in re.findall(r"\+\s*([^<]+)", section_html):
            line = line.strip()
            if line:
                items.append(line)
        return items

    def extract_invariants(section_html):
        items = []
        for line in re.findall(r"<i>([^<]+)</i>", section_html):
            line = line.strip()
            if line:
                items.append(line)
        return items

    if len(sections) >= 3:
        properties = extract_items(sections[1])
        operations = extract_items(sections[2])
    if len(sections) >= 4:
        invariants = extract_invariants(sections[3])

    return name, base, properties, operations, invariants


# ---------------------------------------------------------------------------
# Cell creation
# ---------------------------------------------------------------------------

def create_class_cell(root, name, base=None, properties=None, operations=None,
                      invariants=None, x=40, y=40, imported_from=None):
    """Create and append a class mxCell to root. Returns the cell element.
    If imported_from is set, the class is rendered with dashed border and the
    source module name shown as a stereotype."""
    properties = properties or []
    operations = operations or []
    invariants = invariants or []

    cell_id = str(next_id(root))
    stereotype = f"\u00ABfrom: {imported_from}\u00BB" if imported_from else None
    label = build_class_html(name, base, properties, operations, invariants, stereotype=stereotype)
    height = calc_cell_height(len(properties), len(operations), len(invariants))
    if imported_from:
        height += LINE_HEIGHT

    style = CLASS_STYLE_IMPORT if imported_from else CLASS_STYLE
    cell = ET.SubElement(root, "mxCell")
    cell.set("id", cell_id)
    cell.set("value", label)
    cell.set("style", style)
    cell.set("vertex", "1")
    cell.set("parent", "1")

    geo = ET.SubElement(cell, "mxGeometry")
    geo.set("x", str(int(x)))
    geo.set("y", str(int(y)))
    geo.set("width", str(CELL_WIDTH))
    geo.set("height", str(int(height)))
    geo.set("as", "geometry")

    return cell


def update_class_cell(cell, name=None, base=None, properties=None,
                      operations=None, invariants=None):
    """Update an existing class cell's content. Recalculates height."""
    old_name, old_base, old_props, old_ops, old_invs = parse_class_html(
        unescape(cell.get("value", ""))
    )

    new_name = name if name is not None else old_name
    new_base = base if base is not None else old_base
    new_props = properties if properties is not None else old_props
    new_ops = operations if operations is not None else old_ops
    new_invs = invariants if invariants is not None else old_invs

    label = build_class_html(new_name, new_base, new_props, new_ops, new_invs)
    cell.set("value", label)

    height = calc_cell_height(len(new_props), len(new_ops), len(new_invs))
    set_geometry(cell, h=height)


# ---------------------------------------------------------------------------
# Edge creation
# ---------------------------------------------------------------------------

def create_edge(root, source_id, target_id, edge_type, label="",
                exit_x=None, exit_y=None, entry_x=None, entry_y=None):
    """Create and append an edge mxCell. Returns the cell element.

    Anchor points (0.0–1.0) control where the edge leaves/arrives on the
    class box.  0,0 = top-left; 1,1 = bottom-right; 0.5,0 = top-center.
    When multiple edges share a side, callers MUST supply distinct anchors.
    """
    if edge_type not in EDGE_STYLES:
        raise ValueError(f"Unknown edge type: {edge_type}. Use: {list(EDGE_STYLES.keys())}")

    cell_id = str(next_id(root))
    style = EDGE_STYLES[edge_type]

    anchor_parts = []
    if exit_x is not None:
        anchor_parts.append(f"exitX={exit_x}")
    if exit_y is not None:
        anchor_parts.append(f"exitY={exit_y}")
    if entry_x is not None:
        anchor_parts.append(f"entryX={entry_x}")
    if entry_y is not None:
        anchor_parts.append(f"entryY={entry_y}")
    if anchor_parts:
        if exit_x is not None or exit_y is not None:
            anchor_parts.append("exitDx=0")
            anchor_parts.append("exitDy=0")
        if entry_x is not None or entry_y is not None:
            anchor_parts.append("entryDx=0")
            anchor_parts.append("entryDy=0")
        style = style.rstrip(";") + ";" + ";".join(anchor_parts) + ";"

    cell = ET.SubElement(root, "mxCell")
    cell.set("id", cell_id)
    cell.set("value", label or "")
    cell.set("style", style)
    cell.set("edge", "1")
    cell.set("parent", "1")
    cell.set("source", str(source_id))
    cell.set("target", str(target_id))

    geo = ET.SubElement(cell, "mxGeometry")
    geo.set("relative", "1")
    geo.set("as", "geometry")

    return cell


def add_edge_waypoints(edge_cell, points):
    """Attach ``<Array as="points">`` waypoints to an edge's geometry.

    ``points`` is a sequence of ``(x, y)`` tuples in absolute page coordinates.
    Existing waypoints on the edge are replaced.

    Draw.io's orthogonal router honours these waypoints, so callers can use them
    to dog-leg an edge around an intervening class.
    """
    if not points:
        return
    geo = edge_cell.find("mxGeometry")
    if geo is None:
        geo = ET.SubElement(edge_cell, "mxGeometry")
        geo.set("relative", "1")
        geo.set("as", "geometry")
    for existing in geo.findall("Array"):
        geo.remove(existing)
    arr = ET.SubElement(geo, "Array")
    arr.set("as", "points")
    for x, y in points:
        pt = ET.SubElement(arr, "mxPoint")
        pt.set("x", str(int(round(x))))
        pt.set("y", str(int(round(y))))


def set_edge_anchors(cell, exit_x=None, exit_y=None, entry_x=None, entry_y=None):
    """Set or update exit/entry anchor points on an existing edge cell."""
    style = cell.get("style", "")
    for key in ("exitX", "exitY", "entryX", "entryY",
                "exitDx", "exitDy", "entryDx", "entryDy"):
        style = re.sub(rf"{key}=[^;]*;?", "", style)
    style = style.rstrip(";") + ";"

    parts = []
    if exit_x is not None:
        parts.append(f"exitX={exit_x}")
    if exit_y is not None:
        parts.append(f"exitY={exit_y}")
    if exit_x is not None or exit_y is not None:
        parts.append("exitDx=0")
        parts.append("exitDy=0")
    if entry_x is not None:
        parts.append(f"entryX={entry_x}")
    if entry_y is not None:
        parts.append(f"entryY={entry_y}")
    if entry_x is not None or entry_y is not None:
        parts.append("entryDx=0")
        parts.append("entryDy=0")
    if parts:
        style += ";".join(parts) + ";"

    cell.set("style", style)


# ---------------------------------------------------------------------------
# Deletion
# ---------------------------------------------------------------------------

def delete_cell(root, cell):
    """Remove a cell from root."""
    root.remove(cell)


def delete_class_and_edges(root, class_name):
    """Remove a class cell and all edges connected to it."""
    cell = find_cell_by_name(root, class_name)
    if cell is None:
        return False

    cell_id = cell.get("id")
    edges_to_remove = []
    for edge in root.findall("mxCell"):
        if edge.get("edge") != "1":
            continue
        if edge.get("source") == cell_id or edge.get("target") == cell_id:
            edges_to_remove.append(edge)

    for e in edges_to_remove:
        root.remove(e)
    root.remove(cell)
    return True


def delete_edge_between(root, source_name, target_name):
    """Remove edge(s) between two named classes. Returns count removed."""
    source_cell = find_cell_by_name(root, source_name)
    target_cell = find_cell_by_name(root, target_name)
    if source_cell is None or target_cell is None:
        return 0

    source_id = source_cell.get("id")
    target_id = target_cell.get("id")

    to_remove = []
    for edge in root.findall("mxCell"):
        if edge.get("edge") != "1":
            continue
        s, t = edge.get("source", ""), edge.get("target", "")
        if (s == source_id and t == target_id) or (s == target_id and t == source_id):
            to_remove.append(edge)

    for e in to_remove:
        root.remove(e)
    return len(to_remove)


# ---------------------------------------------------------------------------
# Domain model sync (DrawIO -> markdown)
# ---------------------------------------------------------------------------

def read_classes_from_page(root):
    """Read all class data from a DrawIO page root. Returns list of concept dicts."""
    concepts = []
    for cell in root.findall("mxCell"):
        if cell.get("vertex") != "1":
            continue
        value = cell.get("value", "")
        name = _extract_class_name(value)
        if not name:
            continue
        full_name, base, props, ops, invs = parse_class_html(value)
        concepts.append({
            "name": full_name or name,
            "base": base,
            "properties": props,
            "operations": ops,
            "invariants": invs,
        })
    return concepts


def concept_to_md(concept):
    """Render a single concept dict to domain-model.md format."""
    name = concept["name"]
    base = concept.get("base")
    header = f"**{name}**" + (f" : {base}" if base else "")

    lines = [header]

    for p in concept.get("properties", []):
        lines.append(f"- {p}")

    ops = concept.get("operations", [])
    if ops:
        lines.append("- Operations:")
        for o in ops:
            lines.append(f"  - {o}")

    for inv in concept.get("invariants", []):
        lines.append(f"- Invariant: {inv}")

    return "\n".join(lines)


def parse_model_sections(md_text):
    """Parse domain-model.md into sections by foundational model name."""
    lines = md_text.split("\n")
    sections = {}
    current_name = None
    current_start = None
    preamble_lines = []
    domain_model_started = False
    concepts_lines = []
    extensions_lines = []
    in_extensions = False

    def _flush():
        if current_name:
            sections[current_name] = {
                "preamble": "\n".join(preamble_lines),
                "concepts_text": "\n".join(concepts_lines),
                "extensions_text": "\n".join(extensions_lines),
                "start": current_start,
            }

    for i, line in enumerate(lines):
        if line.startswith("## ") and not line.startswith("###"):
            _flush()
            current_name = line[3:].strip()
            current_start = i
            preamble_lines = []
            concepts_lines = []
            extensions_lines = []
            domain_model_started = False
            in_extensions = False
        elif line.strip() == "### Domain Model":
            domain_model_started = True
        elif line.strip().startswith("### Extensions"):
            in_extensions = True
        elif current_name and not domain_model_started and not in_extensions:
            preamble_lines.append(line)
        elif current_name and in_extensions:
            extensions_lines.append(line)
        elif current_name and domain_model_started and not in_extensions:
            concepts_lines.append(line)

    _flush()
    return sections


def parse_concepts_from_md(concepts_text):
    """Parse concept blocks from the concepts portion of a model section."""
    concepts = []
    current = None

    in_operations = False
    for line in concepts_text.split("\n"):
        stripped = line.strip()

        if stripped.startswith("**") and not stripped.startswith("**Rollable extensions"):
            match = re.match(r"\*\*(\w+)\*\*(?:\s*:\s*(\w+))?", stripped)
            if match:
                if current:
                    concepts.append(current)
                current = {
                    "name": match.group(1),
                    "base": match.group(2),
                    "properties": [],
                    "operations": [],
                    "invariants": [],
                }
                in_operations = False
            continue

        if current is None:
            continue

        if stripped == "- Operations:":
            in_operations = True
            continue

        if stripped.startswith("- Invariant:"):
            in_operations = False
            current["invariants"].append(stripped[len("- Invariant:"):].strip())
            continue

        if stripped.startswith("- examples:"):
            in_operations = False
            continue

        if in_operations and stripped.startswith("- "):
            current["operations"].append(stripped[2:].strip())
            continue

        if not in_operations and stripped.startswith("- ") and not stripped.startswith("- Operations"):
            prop = stripped[2:].strip()
            if prop:
                current["properties"].append(prop)
            continue

    if current:
        concepts.append(current)

    return concepts


def _diff_concept(old, new):
    """Compare two concept dicts. Returns list of diff strings, empty if identical."""
    diffs = []

    if old.get("base") != new.get("base"):
        diffs.append(f"base: {old.get('base') or '(none)'} -> {new.get('base') or '(none)'}")

    added_props = [p for p in new["properties"] if p not in old["properties"]]
    removed_props = [p for p in old["properties"] if p not in new["properties"]]
    for p in added_props:
        diffs.append(f"+ prop: {p}")
    for p in removed_props:
        diffs.append(f"- prop: {p}")

    added_ops = [o for o in new["operations"] if o not in old["operations"]]
    removed_ops = [o for o in old["operations"] if o not in new["operations"]]
    for o in added_ops:
        diffs.append(f"+ op: {o}")
    for o in removed_ops:
        diffs.append(f"- op: {o}")

    added_invs = [v for v in new["invariants"] if v not in old["invariants"]]
    removed_invs = [v for v in old["invariants"] if v not in new["invariants"]]
    for v in added_invs:
        diffs.append(f"+ inv: {v}")
    for v in removed_invs:
        diffs.append(f"- inv: {v}")

    return diffs


def sync_page_to_model(drawio_path, page_name, md_path):
    """Sync classes from a DrawIO page back to domain-model.md.
    Returns a dict describing changes: {added: [], removed: [], updated: []}.
    """
    _, mxfile = load_drawio(drawio_path)
    _, root = get_page(mxfile, page_name)
    if root is None:
        raise ValueError(f"Page '{page_name}' not found in {drawio_path}")

    diagram_concepts = read_classes_from_page(root)
    diagram_by_name = {c["name"]: c for c in diagram_concepts}

    md_text = Path(md_path).read_text(encoding="utf-8")
    sections = parse_model_sections(md_text)

    if page_name not in sections:
        raise ValueError(f"Section '{page_name}' not found in {md_path}")

    section = sections[page_name]
    md_concepts = parse_concepts_from_md(section["concepts_text"])
    md_by_name = {c["name"]: c for c in md_concepts}

    changes = {"added": [], "removed": [], "updated": []}

    for name in diagram_by_name:
        if name not in md_by_name:
            changes["added"].append({"name": name, "concept": diagram_by_name[name]})

    for name in md_by_name:
        if name not in diagram_by_name:
            changes["removed"].append({"name": name, "concept": md_by_name[name]})

    for name in diagram_by_name:
        if name in md_by_name:
            dc = diagram_by_name[name]
            mc = md_by_name[name]
            diffs = _diff_concept(mc, dc)
            if diffs:
                changes["updated"].append({"name": name, "diffs": diffs})

    new_concepts_lines = []
    for dc in diagram_concepts:
        new_concepts_lines.append("")
        new_concepts_lines.append(concept_to_md(dc))

    new_section_body = (
        section["preamble"].rstrip() + "\n\n"
        "### Domain Model\n"
        + "\n".join(new_concepts_lines) + "\n\n"
        "### Extensions\n"
        + section["extensions_text"]
    )

    lines = md_text.split("\n")
    section_start = section["start"]

    next_section_start = len(lines)
    found_current = False
    for i, line in enumerate(lines):
        if line.startswith("## ") and not line.startswith("###"):
            if found_current:
                next_section_start = i
                break
            if line[3:].strip() == page_name:
                found_current = True

    separator_line = None
    for i in range(next_section_start - 1, section_start, -1):
        if lines[i].strip() == "---":
            separator_line = i
            break

    end_line = separator_line if separator_line else next_section_start
    new_lines = lines[:section_start]
    new_lines.append(f"## {page_name}")
    new_lines.append("")
    new_lines.append(new_section_body.rstrip())
    new_lines.append("")
    new_lines.extend(lines[end_line:])

    Path(md_path).write_text("\n".join(new_lines), encoding="utf-8")
    return changes


# ---------------------------------------------------------------------------
# check_edges_approach_perpendicular
# ---------------------------------------------------------------------------

def _eap_parse_style(style: str) -> dict:
    out: dict = {}
    for kv in (style or "").split(";"):
        if "=" not in kv:
            continue
        key, value = kv.split("=", 1)
        try:
            out[key] = float(value)
        except ValueError:
            continue
    return out


def _eap_anchor_side(frac_x, frac_y):
    if frac_x is None or frac_y is None:
        return None
    if abs(frac_x - 0) < 1e-3:
        return "left"
    if abs(frac_x - 1) < 1e-3:
        return "right"
    if abs(frac_y - 0) < 1e-3:
        return "top"
    if abs(frac_y - 1) < 1e-3:
        return "bottom"
    return None


def _eap_seg_orient(seg):
    (x1, y1), (x2, y2) = seg
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    if dx < 1 and dy < 1:
        return None
    if dx < 1:
        return "v"
    if dy < 1:
        return "h"
    return None


def _eap_seg_dir_signed(seg):
    (x1, y1), (x2, y2) = seg
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) < 1 and abs(dy) < 1:
        return None
    if abs(dx) >= abs(dy):
        return "right" if dx > 0 else "left"
    return "down" if dy > 0 else "up"


def _eap_expected_orient(side):
    return {"left": "h", "right": "h", "top": "v", "bottom": "v"}.get(side or "")


def _eap_outward(side):
    return {"left": "left", "right": "right", "top": "up", "bottom": "down"}.get(side or "")


def _eap_inward(side):
    return {"left": "right", "right": "left", "top": "down", "bottom": "up"}.get(side or "")


def _eap_classify_edge(style: str) -> str:
    style = (style or "").lower()
    if "endarrow=block" in style and "startarrow=block" not in style:
        if "endfill=0" in style:
            return "inheritance-orthogonal" if "orthogonal" in style else "inheritance"
        return "association"
    if "startarrow=diamondthin" in style or "startarrow=diamond" in style:
        return "composition" if "startfill=1" in style else "aggregation"
    return "association"


def check_edges_approach_perpendicular(root) -> list:
    """Return list of (edge_desc, end, side, expected_dir, actual_dir) for violations."""
    classes = get_all_classes(root)
    id_to_name = {cid: name for cid, name, *_ in classes}
    id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}

    violations = []
    for cell in root.findall("mxCell"):
        if cell.get("edge") != "1":
            continue
        src_id = cell.get("source", "")
        tgt_id = cell.get("target", "")
        if src_id not in id_to_name or tgt_id not in id_to_name:
            continue

        style = cell.get("style", "")
        attrs = _eap_parse_style(style)
        exit_side = _eap_anchor_side(attrs.get("exitX"), attrs.get("exitY"))
        entry_side = _eap_anchor_side(attrs.get("entryX"), attrs.get("entryY"))

        segs, _ = _compute_edge_segments_ex(cell, id_to_geo)
        if not segs:
            continue

        etype = _eap_classify_edge(style)
        desc = f"{id_to_name[src_id]}->{id_to_name[tgt_id]} ({etype})"

        expected = _eap_expected_orient(exit_side)
        actual = _eap_seg_orient(segs[0])
        if expected and actual and actual != expected:
            violations.append((desc, "source", exit_side, expected, actual))
        else:
            want = _eap_outward(exit_side)
            got = _eap_seg_dir_signed(segs[0])
            if want and got and got != want:
                violations.append((desc, "source", exit_side, want, got))

        expected = _eap_expected_orient(entry_side)
        actual = _eap_seg_orient(segs[-1])
        if expected and actual and actual != expected:
            violations.append((desc, "target", entry_side, expected, actual))
        else:
            want = _eap_inward(entry_side)
            got = _eap_seg_dir_signed(segs[-1])
            if want and got and got != want:
                violations.append((desc, "target", entry_side, want, got))

    return violations


# ---------------------------------------------------------------------------
# check_leaf_nodes_horizontal_row
# ---------------------------------------------------------------------------

_LEAF_ROW_Y_TOLERANCE = 30
_LEAF_ROW_MIN_SIZE = 4


def check_leaf_nodes_horizontal_row(root) -> list:
    """Return list of violation strings for hubs with 4+ leaves in a wide horizontal row."""
    geo: dict = {}
    for cell in root.findall("mxCell"):
        if cell.get("vertex") != "1":
            continue
        geometry = cell.find("mxGeometry")
        if geometry is None:
            continue
        w = geometry.get("width")
        h = geometry.get("height")
        if w is None or h is None:
            continue
        geo[cell.get("id", "")] = (
            float(geometry.get("x", 0)),
            float(geometry.get("y", 0)),
            float(w),
            float(h),
        )

    neighbours: dict = {}
    for cell in root.findall("mxCell"):
        if cell.get("edge") != "1":
            continue
        src = cell.get("source")
        tgt = cell.get("target")
        if src and tgt and src in geo:
            neighbours.setdefault(src, set()).add(tgt)

    violations = []
    for hub_id, leaf_ids in neighbours.items():
        if len(leaf_ids) < _LEAF_ROW_MIN_SIZE:
            continue
        row_groups: dict = {}
        for lid in leaf_ids:
            if lid not in geo:
                continue
            y = geo[lid][1]
            bucket = round(y / _LEAF_ROW_Y_TOLERANCE)
            row_groups.setdefault(bucket, []).append(lid)
        for members in row_groups.values():
            if len(members) < _LEAF_ROW_MIN_SIZE:
                continue
            y_vals = [geo[m][1] for m in members]
            x_vals = [geo[m][0] for m in members]
            y_spread = max(y_vals) - min(y_vals)
            x_spread = max(x_vals) - min(x_vals)
            if y_spread <= _LEAF_ROW_Y_TOLERANCE and x_spread > 600:
                hub_cell = root.find(f"mxCell[@id='{hub_id}']")
                hub_name = hub_id
                if hub_cell is not None:
                    import re as _re
                    raw = hub_cell.get("value") or hub_id
                    text = _re.sub(r"<[^>]+>", "", raw)
                    text = _re.sub(r"&[a-z]+;", " ", text)
                    hub_name = _re.split(r"[\s+]", text.strip())[0] or hub_id
                violations.append(
                    f"{hub_name} has {len(members)} leaf neighbours in a horizontal row "
                    f"(y~{int(sum(y_vals)/len(y_vals))}, x-span={int(x_spread)}px)"
                )
    return violations


# ---------------------------------------------------------------------------
# CLI entry point — `python drawio_tools.py audit <file> [--page <name>]`
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    def _cli_audit(args):
        if len(args) < 1:
            print("Usage: python drawio_tools.py audit <file> [--page <name>]")
            sys.exit(1)
        path = args[0]
        page = None
        if "--page" in args:
            idx = args.index("--page")
            if idx + 1 < len(args):
                page = args[idx + 1]
        print(audit_diagram_report(path, page))
        results = audit_diagram(path, page)
        any_fail = any(not info["pass"] for info in results.values())
        sys.exit(1 if any_fail else 0)

    if len(sys.argv) < 2:
        print("Commands: audit")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "audit":
        _cli_audit(sys.argv[2:])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
