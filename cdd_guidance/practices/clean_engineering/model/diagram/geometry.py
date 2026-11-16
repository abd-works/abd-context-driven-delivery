"""Axis-aligned box for a placed diagram node, and whether two straight lines cross. The layout writer and the
draw.io layout scanners both measure diagrams with these."""
from __future__ import annotations

from typing import NamedTuple

Point = tuple[float, float]
Segment = tuple[Point, Point]


class Geometry(NamedTuple):
    """x, y, width, height of one placed node."""

    x: float
    y: float
    width: float
    height: float

    def overlaps(self, other: 'Geometry') -> bool:
        return not (
            self.x + self.width <= other.x
            or other.x + other.width <= self.x
            or self.y + self.height <= other.y
            or other.y + other.height <= self.y
        )

    def shifted(self, rightward: float, downward: float) -> 'Geometry':
        return Geometry(self.x + rightward, self.y + downward, self.width, self.height)

    def moved_to(self, left: float, top: float) -> 'Geometry':
        return Geometry(left, top, self.width, self.height)

    def clear_gap_to(self, other: 'Geometry') -> float:
        """The empty space between this box and other, corner to corner when they are apart both ways; 0 when they
        touch or overlap."""
        across = max(0.0, self.x - (other.x + other.width), other.x - (self.x + self.width))
        down = max(0.0, self.y - (other.y + other.height), other.y - (self.y + self.height))
        if across == 0.0 or down == 0.0:
            return across + down
        return (across ** 2 + down ** 2) ** 0.5

    @property
    def center(self) -> Point:
        return (self.x + self.width / 2, self.y + self.height / 2)


def segments_cross(first: Segment, second: Segment) -> bool:
    """True when two straight segments cross each other; an end that lies on the other segment's line touches it, and
    touching counts."""
    (first_start, first_end), (second_start, second_end) = first, second
    return (
        _turns_left(first_start, second) != _turns_left(first_end, second)
        and _turns_left(second_start, first) != _turns_left(second_end, first)
    )


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
