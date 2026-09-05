"""Geometric primitives shared by every diagram backend.

``Position`` is an immutable 2D point and ``Boundary`` is an axis-aligned
rectangle. Both are coordinate-system agnostic — backends decide whether
positive Y means "down" (DrawIO) or "down" (Miro; both use the same convention).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """Immutable 2D position with ``x`` and ``y`` coordinates."""

    x: float
    y: float

    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Position') -> 'Position':
        return Position(self.x - other.x, self.y - other.y)

    def distance_to(self, other: 'Position') -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5

    def is_within_tolerance(self, other: 'Position', tolerance: float) -> bool:
        return self.distance_to(other) <= tolerance


@dataclass(frozen=True)
class Boundary:
    """Axis-aligned rectangle anchored at top-left ``(x, y)`` with size."""

    x: float
    y: float
    width: float
    height: float

    @property
    def position(self) -> Position:
        return Position(self.x, self.y)

    @property
    def center(self) -> Position:
        return Position(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def contains_position(self, pos: Position) -> bool:
        return (self.x <= pos.x <= self.right
                and self.y <= pos.y <= self.bottom)

    def contains_boundary(self, other: 'Boundary') -> bool:
        return (self.x <= other.x
                and self.y <= other.y
                and self.right >= other.right
                and self.bottom >= other.bottom)

    def overlaps(self, other: 'Boundary') -> bool:
        return not (self.right < other.x
                    or other.right < self.x
                    or self.bottom < other.y
                    or other.bottom < self.y)

    def expand(self, padding: float) -> 'Boundary':
        return Boundary(
            x=self.x - padding,
            y=self.y - padding,
            width=self.width + 2 * padding,
            height=self.height + 2 * padding,
        )

    def union(self, other: 'Boundary') -> 'Boundary':
        min_x = min(self.x, other.x)
        min_y = min(self.y, other.y)
        max_right = max(self.right, other.right)
        max_bottom = max(self.bottom, other.bottom)
        return Boundary(
            x=min_x,
            y=min_y,
            width=max_right - min_x,
            height=max_bottom - min_y,
        )
