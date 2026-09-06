"""Pixel constants for the row-based outline layout.

Both DrawIO and Miro renderers share these so a story map produced for one
backend has the same visual rhythm (bar heights, story squares, lane gaps) as
the other. Backends are free to scale or override individual values, but the
defaults are tuned to the DrawIO reference diagram.
"""

CELL_SIZE = 50
"""Side length of a story or actor square."""

CELL_SPACING = 10
"""Horizontal gap between sibling cells."""

EPIC_Y = 120
"""Y position of the epic row (top of the diagram)."""

EPIC_HEIGHT = 60
"""Height of an epic bar."""

SUB_EPIC_HEIGHT = 60
"""Height of a sub-epic bar."""

ROW_GAP = 15
"""Vertical gap between bar rows."""

ACTOR_GAP = 25
"""Extra vertical gap above the actor row."""

BAR_PADDING = 5
"""Horizontal padding inside epic / sub-epic bars."""

SPACING = CELL_SPACING
"""Backward-compatible alias for ``CELL_SPACING``."""

CONTAINER_PADDING = BAR_PADDING
"""Backward-compatible alias for ``BAR_PADDING``."""
