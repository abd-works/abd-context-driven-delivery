"""Scanner: edges-do-not-overlap-edges - orthogonal edges must not share a long collinear span."""
from __future__ import annotations

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.drawio.page.drawio_page import (
    DrawioPage,
    Segment,
    share_inheritance_trunk,
)
from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner

# Pixels a segment may lean and still count as horizontal or vertical.
ALIGNMENT_TOLERANCE = 2
# Parallel segments closer than this many pixels sit on top of each other.
PARALLEL_PROXIMITY = 4
# Parallel segments must share more than this many pixels of length to overlap.
SHARED_SPAN = 12


class EdgesDoNotOverlapEdgesScanner(DrawioScanner):
    RULE = "edges-do-not-overlap-edges"

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        """Each pair of edges that run on top of each other, except subclasses joined into one shared line to their base."""
        routes = [(edge, page.describe(edge), page.segments(edge)[0]) for edge in page.edges]
        violations = []
        for index, (first_edge, first_name, first_segments) in enumerate(routes):
            for second_edge, second_name, second_segments in routes[index + 1:]:
                if share_inheritance_trunk(first_edge, second_edge):
                    continue
                detail = _first_overlap(first_segments, second_segments)
                if detail:
                    violations.append(self.violation(page, f"{first_name} overlaps {second_name}: {detail}"))
        return violations


def _first_overlap(first_segments: list[Segment], second_segments: list[Segment]) -> str | None:
    for first in first_segments:
        for second in second_segments:
            if _segments_overlap(first, second):
                return f"segments {_shown(first)} and {_shown(second)} overlap"
    return None


def _segments_overlap(first: Segment, second: Segment) -> bool:
    """True when two axis-aligned segments run parallel, close together, along a shared span."""
    (ax1, ay1), (ax2, ay2) = first
    (bx1, by1), (bx2, by2) = second
    both_horizontal = abs(ay2 - ay1) < ALIGNMENT_TOLERANCE and abs(by2 - by1) < ALIGNMENT_TOLERANCE
    both_vertical = abs(ax2 - ax1) < ALIGNMENT_TOLERANCE and abs(bx2 - bx1) < ALIGNMENT_TOLERANCE
    if both_horizontal and abs(ay1 - by1) < PARALLEL_PROXIMITY and _shared_length((ax1, ax2), (bx1, bx2)) > SHARED_SPAN:
        return True
    return both_vertical and abs(ax1 - bx1) < PARALLEL_PROXIMITY and _shared_length((ay1, ay2), (by1, by2)) > SHARED_SPAN


def _shared_length(first: tuple[float, float], second: tuple[float, float]) -> float:
    return min(max(first), max(second)) - max(min(first), min(second))


def _shown(segment: Segment) -> str:
    (x1, y1), (x2, y2) = segment
    return f"({x1:.0f},{y1:.0f})->({x2:.0f},{y2:.0f})"


if __name__ == "__main__":
    raise SystemExit(EdgesDoNotOverlapEdgesScanner().run_main())
