"""Axis-aligned box for a placed diagram node. Shared by Draw.io and Miro."""
from __future__ import annotations

from typing import NamedTuple


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

    def shifted(self, dx: float, dy: float) -> 'Geometry':
        return Geometry(self.x + dx, self.y + dy, self.width, self.height)

    def moved_to(self, x: float, y: float) -> 'Geometry':
        return Geometry(x, y, self.width, self.height)

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)


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
