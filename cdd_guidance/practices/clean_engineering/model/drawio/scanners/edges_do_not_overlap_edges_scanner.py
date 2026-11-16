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
X_AXIS, Y_AXIS = 0, 1


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
                detail = self._first_overlap(first_segments, second_segments)
                if detail:
                    violations.append(self.violation(page, f"{first_name} overlaps {second_name}: {detail}"))
        return violations

    def _first_overlap(self, first_segments: list[Segment], second_segments: list[Segment]) -> str | None:
        for first in first_segments:
            for second in second_segments:
                if self._segments_overlap(first, second):
                    return f"segments {self._shown(first)} and {self._shown(second)} overlap"
        return None

    def _segments_overlap(self, first: Segment, second: Segment) -> bool:
        """True when two axis-aligned segments run parallel, close together, along a shared span."""
        return any(
            self._is_level(first, level_axis) and self._is_level(second, level_axis)
            and abs(first[0][level_axis] - second[0][level_axis]) < PARALLEL_PROXIMITY
            and self._shared_length(first, second, 1 - level_axis) > SHARED_SPAN
            for level_axis in (Y_AXIS, X_AXIS)
        )

    def _is_level(self, segment: Segment, axis: int) -> bool:
        """True when the segment keeps the same coordinate on axis: horizontal for the y axis, vertical for x."""
        return abs(segment[1][axis] - segment[0][axis]) < ALIGNMENT_TOLERANCE

    def _shared_length(self, first: Segment, second: Segment, axis: int) -> float:
        first_span = (first[0][axis], first[1][axis])
        second_span = (second[0][axis], second[1][axis])
        return min(max(first_span), max(second_span)) - max(min(first_span), min(second_span))

    def _shown(self, segment: Segment) -> str:
        start, end = segment
        return f"({start[0]:.0f},{start[1]:.0f})->({end[0]:.0f},{end[1]:.0f})"


if __name__ == "__main__":
    raise SystemExit(EdgesDoNotOverlapEdgesScanner().run_main())
