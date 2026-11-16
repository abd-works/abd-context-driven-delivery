"""Scanner: prefer-short-routes — keep related classes close; few waypoints."""
from __future__ import annotations

from xml.etree import ElementTree as ET

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Geometry
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
        boxes = self._vertex_boxes(page)
        violations = []
        for edge in page.cells:
            source, target = edge.get("source", ""), edge.get("target", "")
            if edge.get("edge") != "1" or source not in boxes or target not in boxes:
                continue
            name = f"{page.class_names.get(source, source)} → {page.class_names.get(target, target)}"
            violations.extend(self.violation(page, f"{name}: {message}") for message in self._long_route_messages(edge, boxes))
        return violations

    def _long_route_messages(self, edge: ET.Element, boxes: dict[str, Geometry]) -> list[str]:
        """What is too long about one edge: many waypoints across a short gap, or its two boxes placed far apart."""
        waypoints = len(edge.findall("mxGeometry/Array/*"))
        gap = boxes[edge.get("source", "")].clear_gap_to(boxes[edge.get("target", "")])
        messages = []
        if waypoints > SHORT_ROUTE_MAX_WAYPOINTS and gap <= SHORT_ROUTE_MAX_BOX_GAP:
            messages.append(f"{waypoints} waypoints across a {gap:.0f}px gap (max {SHORT_ROUTE_MAX_WAYPOINTS}) — prefer a short orthogonal route")
        if gap > SHORT_ROUTE_MAX_BOX_GAP:
            messages.append(f"endpoint gap {gap:.0f}px (max {SHORT_ROUTE_MAX_BOX_GAP}) — place related classes closer")
        return messages

    def _vertex_boxes(self, page: DrawioPage) -> dict[str, Geometry]:
        """Every vertex with a geometry, class or not, since an edge may end on any of them."""
        boxes: dict[str, Geometry] = {}
        for cell in page.cells:
            box = cell_box(cell) if cell.get("vertex") == "1" else None
            if box and cell.get("id"):
                boxes[cell.get("id")] = box
        return boxes


if __name__ == "__main__":
    raise SystemExit(PreferShortRoutesScanner().run_main())
