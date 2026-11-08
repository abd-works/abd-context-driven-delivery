"""Scanner: prefer-short-routes — keep related classes close; few waypoints."""
from __future__ import annotations

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.drawio.diagram.geometry import Geometry
from cdd_guidance.practices.clean_engineering.model.drawio.page.drawio_page import (
    DrawioPage,
    cell_box,
)
from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner

SHORT_ROUTE_MAX_WAYPOINTS = 2
SHORT_ROUTE_MAX_BOX_GAP = 320


class PreferShortRoutesScanner(DrawioScanner):
    RULE = "prefer-short-routes"

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        """Edges that dog-leg across a short gap, and related boxes placed too far apart."""
        boxes = _vertex_boxes(page)
        violations = []
        for edge in page.cells:
            source, target = edge.get("source", ""), edge.get("target", "")
            if edge.get("edge") != "1" or source not in boxes or target not in boxes:
                continue
            name = f"{page.class_names.get(source, source)} → {page.class_names.get(target, target)}"
            waypoints = len(edge.findall("mxGeometry/Array/*"))
            gap = _clear_gap(boxes[source], boxes[target])
            if waypoints > SHORT_ROUTE_MAX_WAYPOINTS and gap <= SHORT_ROUTE_MAX_BOX_GAP:
                violations.append(self.violation(
                    page,
                    f"{name}: {waypoints} waypoints across a {gap:.0f}px gap (max {SHORT_ROUTE_MAX_WAYPOINTS}) — prefer a short orthogonal route",
                ))
            if gap > SHORT_ROUTE_MAX_BOX_GAP:
                violations.append(self.violation(
                    page, f"{name}: endpoint gap {gap:.0f}px (max {SHORT_ROUTE_MAX_BOX_GAP}) — place related classes closer"
                ))
        return violations


def _vertex_boxes(page: DrawioPage) -> dict[str, Geometry]:
    """Every vertex with a geometry, class or not, since an edge may end on any of them."""
    boxes: dict[str, Geometry] = {}
    for cell in page.cells:
        box = cell_box(cell) if cell.get("vertex") == "1" else None
        if box and cell.get("id"):
            boxes[cell.get("id")] = box
    return boxes


def _clear_gap(first: Geometry, second: Geometry) -> float:
    """The empty space between two boxes; 0 when they touch or overlap."""
    ax, ay, aw, ah = first
    bx, by, bw, bh = second
    across = max(0.0, ax - (bx + bw), bx - (ax + aw))
    down = max(0.0, ay - (by + bh), by - (ay + ah))
    if across == 0.0 or down == 0.0:
        return across + down
    return (across ** 2 + down ** 2) ** 0.5


if __name__ == "__main__":
    raise SystemExit(PreferShortRoutesScanner().run_main())
