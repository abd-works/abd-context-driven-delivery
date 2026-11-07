"""Scanner: edges-do-not-cross-classes - edge routes must not cut through unrelated class boxes."""
from __future__ import annotations

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.drawio.drawio_page import (
    DrawioPage,
    segment_hits_box,
)
from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner

# How close, in pixels, an edge may pass a class box before it counts as touching it.
BOX_MARGIN = 3


class EdgesDoNotCrossClassesScanner(DrawioScanner):
    RULE = "edges-do-not-cross-classes"

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        """Only routes the file states exactly; Draw.io's router may find a better way for an edge with no waypoints."""
        violations = []
        for edge in page.edges:
            segments, approximate = page.segments(edge)
            if approximate:
                continue
            ends = (edge.get("source", ""), edge.get("target", ""))
            for cell_id, box in page.boxes.items():
                if cell_id in ends or not any(segment_hits_box(segment, box, BOX_MARGIN) for segment in segments):
                    continue
                violations.append(self.violation(page, f"Edge {page.describe(edge)} crosses through {page.class_names[cell_id]}"))
        return violations


if __name__ == "__main__":
    raise SystemExit(EdgesDoNotCrossClassesScanner().run_main())
