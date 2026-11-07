"""Scanner: edges-do-not-cross-other-edges - transverse edge crossings (not collinear overlap)."""
from __future__ import annotations

from xml.etree import ElementTree as ET

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import (
    DrawioPage,
    DrawioScanner,
    Point,
    Segment,
)

# A few crossings are hard to avoid on a busy page; more than this many make it hard to read.
MOST_CROSSINGS_ON_A_PAGE = 5
# Pixels a segment may lean and still count as horizontal or vertical.
CROSSING_TOLERANCE = 2
# Pixels around a shared card where two edges meeting it do not count as crossing.
SHARED_CARD_MARGIN = 5

Route = tuple[ET.Element, list[Segment]]


class EdgesDoNotCrossOtherEdgesScanner(DrawioScanner):
    RULE = "edges-do-not-cross-other-edges"

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        """Each pair of edges that cross at a right angle, away from a card they share, once a page has too many."""
        routes = [(edge, page.segments(edge)[0]) for edge in page.edges]
        crossings = []
        for index, first in enumerate(routes):
            for second in routes[index + 1:]:
                point = self._crossing(page, first, second)
                if point is not None:
                    crossings.append(self.violation(
                        page,
                        f"{self._name(page, first[0])} crosses {self._name(page, second[0])}: "
                        f"cross at ~({int(point[0])},{int(point[1])})",
                    ))
        return crossings if len(crossings) > MOST_CROSSINGS_ON_A_PAGE else []

    def _name(self, page: DrawioPage, edge: ET.Element) -> str:
        return f"{page.class_names.get(edge.get('source', ''), '?')} -> {page.class_names.get(edge.get('target', ''), '?')}"

    def _crossing(self, page: DrawioPage, first: Route, second: Route) -> Point | None:
        shared = {first[0].get("source"), first[0].get("target")} & {second[0].get("source"), second[0].get("target")}
        for first_segment in first[1]:
            for second_segment in second[1]:
                point = _right_angle_crossing(first_segment, second_segment)
                if point is not None and not _beside_shared_card(page, point, shared):
                    return point
        return None


def _beside_shared_card(page: DrawioPage, point: Point, shared: set) -> bool:
    for cell_id in shared:
        box = page.boxes.get(cell_id)
        if not box:
            continue
        near_across = abs(point[0] - (box[0] + box[2] / 2)) < box[2] / 2 + SHARED_CARD_MARGIN
        near_down = abs(point[1] - (box[1] + box[3] / 2)) < box[3] / 2 + SHARED_CARD_MARGIN
        if near_across and near_down:
            return True
    return False


def _right_angle_crossing(first: Segment, second: Segment) -> Point | None:
    """Where a horizontal segment crosses a vertical one strictly inside both, or None."""
    horizontal, vertical = (first, second) if abs(first[1][1] - first[0][1]) < CROSSING_TOLERANCE else (second, first)
    (ax1, ay1), (ax2, ay2) = horizontal
    (bx1, by1), (bx2, by2) = vertical
    if abs(ay2 - ay1) >= CROSSING_TOLERANCE or abs(bx2 - bx1) >= CROSSING_TOLERANCE:
        return None
    y, x = (ay1 + ay2) / 2, (bx1 + bx2) / 2
    low_x, high_x = sorted((ax1, ax2))
    low_y, high_y = sorted((by1, by2))
    if low_x + CROSSING_TOLERANCE < x < high_x - CROSSING_TOLERANCE and low_y + CROSSING_TOLERANCE < y < high_y - CROSSING_TOLERANCE:
        return (x, y)
    return None


if __name__ == "__main__":
    raise SystemExit(EdgesDoNotCrossOtherEdgesScanner().run_main())
