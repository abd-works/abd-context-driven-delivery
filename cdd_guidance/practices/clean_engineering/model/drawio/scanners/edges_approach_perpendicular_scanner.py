"""Scanner: edges-approach-perpendicular - edge tips hit class sides head-on, not sliding along."""
from __future__ import annotations

from xml.etree import ElementTree as ET

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.drawio.page.drawio_page import (
    STRAIGHT_TOLERANCE,
    DrawioPage,
    Segment,
    style_number,
)
from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner

# An anchor fraction this close to 0 or 1 sits on that side of the box.
SIDE_TOLERANCE = 0.001
_AXIS_OF_SIDE = {"left": "h", "right": "h", "top": "v", "bottom": "v"}
_LEAVING_HEADING = {"left": "left", "right": "right", "top": "up", "bottom": "down"}
_ENTERING_HEADING = {"left": "right", "right": "left", "top": "down", "bottom": "up"}


class EdgesApproachPerpendicularScanner(DrawioScanner):
    RULE = "edges-approach-perpendicular"

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        violations = []
        for edge in page.edges:
            if edge.get("source", "") not in page.boxes or edge.get("target", "") not in page.boxes:
                continue
            segments = page.segments(edge)[0]
            if not segments:
                continue
            for end, segment in (("source", segments[0]), ("target", segments[-1])):
                message = self._sliding_end(edge, end, segment)
                if message:
                    violations.append(self.violation(page, f"{page.describe(edge)}: {message}"))
        return violations

    def _sliding_end(self, edge: ET.Element, end: str, segment: Segment) -> str | None:
        """Why this end of the edge meets its box side at an angle or the wrong way, or None when it meets it head-on."""
        prefix = "exit" if end == "source" else "entry"
        style = edge.get("style", "")
        side = _anchor_side(style_number(style, f"{prefix}X"), style_number(style, f"{prefix}Y"))
        expected, actual = _AXIS_OF_SIDE.get(side or ""), _axis(segment)
        if expected and actual and actual != expected:
            return f"{end} segment goes {actual} but anchor is on the {side} side (expected {expected})"
        wanted = (_LEAVING_HEADING if end == "source" else _ENTERING_HEADING).get(side or "")
        heading = _heading(segment)
        if wanted and heading and heading != wanted:
            return f"{end} segment goes {heading} but anchor is on the {side} side (expected {wanted})"
        return None


def _anchor_side(fraction_x: float | None, fraction_y: float | None) -> str | None:
    if fraction_x is None or fraction_y is None:
        return None
    for side, fraction, side_value in (("left", fraction_x, 0), ("right", fraction_x, 1), ("top", fraction_y, 0), ("bottom", fraction_y, 1)):
        if abs(fraction - side_value) < SIDE_TOLERANCE:
            return side
    return None


def _axis(segment: Segment) -> str | None:
    """`h` or `v` for a straight segment, None for a point or a slanted one."""
    (x1, y1), (x2, y2) = segment
    across, down = abs(x2 - x1), abs(y2 - y1)
    if across < STRAIGHT_TOLERANCE and down >= STRAIGHT_TOLERANCE:
        return "v"
    if down < STRAIGHT_TOLERANCE and across >= STRAIGHT_TOLERANCE:
        return "h"
    return None


def _heading(segment: Segment) -> str | None:
    (x1, y1), (x2, y2) = segment
    across, down = x2 - x1, y2 - y1
    if abs(across) < STRAIGHT_TOLERANCE and abs(down) < STRAIGHT_TOLERANCE:
        return None
    if abs(across) >= abs(down):
        return "right" if across > 0 else "left"
    return "down" if down > 0 else "up"


if __name__ == "__main__":
    raise SystemExit(EdgesApproachPerpendicularScanner().run_main())
