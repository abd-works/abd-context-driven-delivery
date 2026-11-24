"""Whether two straight lines cross, and the sizes a diagram's cards are drawn at. A placed node's box is the
framework's one rectangle, harness/whiteboard's *Box*; the layout writer and the draw.io layout scanners both measure
diagrams with these."""
from __future__ import annotations

Point = tuple[float, float]
Segment = tuple[Point, Point]


def segments_cross(first: Segment, second: Segment) -> bool:
    """True when two straight segments cross each other; an end that lies on the other segment's line touches it, and
    touching counts."""
    (first_start, first_end), (second_start, second_end) = first, second
    return (
        _turns_left(first_start, second) != _turns_left(first_end, second)
        and _turns_left(second_start, first) != _turns_left(second_end, first)
    )


def flowed(sizes: list[tuple[float, float]], row_width: float, gap: float) -> list[tuple[float, float]]:
    """The top-left corner of each box of sizes, laid left to right gap apart, a new row gap under the last when a box
    would run the row wider than row_width; the first box at (0, 0)."""
    corners: list[tuple[float, float]] = []
    left, top, row_bottom = 0.0, 0.0, 0.0
    for width, height in sizes:
        if left > 0 and left + width > row_width:
            left, top = 0.0, row_bottom + gap
        corners.append((left, top))
        left += width + gap
        row_bottom = max(row_bottom, top + height)
    return corners


def _turns_left(point: Point, line: Segment) -> bool:
    """True when walking from the line's start towards ``point`` turns left of the line's direction."""
    (start, end) = line
    return (point[1] - start[1]) * (end[0] - start[0]) > (end[1] - start[1]) * (point[0] - start[0])


CELL_WIDTH = 260
CELL_MIN_HEIGHT = 80
LINE_HEIGHT = 16
SECTION_PAD = 8
MODULE_CELL_WIDTH = 280
MODULE_CELL_MIN_HEIGHT = 100
MODULE_LINE_HEIGHT = 16
MODULE_HEADER_HEIGHT = 48
MODULE_MAX_SEAM_BULLETS = 6
MODULE_PURPOSE_MAX_CHARS = 90
