"""Places the modules of a modules view. Shared by every diagram format that draws one.

Top-level modules stand in columns by dependency depth, left to right, each column in the model's order; a module's
path children nest inside it, two to a row, under its header. A format sizes each module's header from the words it
writes there; the layout grows each module to hold what it nests.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import ContainmentForest, DiagramModule
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Geometry

MODULE_COL_GAP = 48
MODULE_ROW_GAP = 32
MODULE_START_X = 40
MODULE_START_Y = 100
MODULE_CHILD_PAD_X = 16
MODULE_CHILD_PAD_Y = 12
MODULE_CHILD_GAP = 12
MODULE_CHILD_COLS = 2


class ModuleLayout:
    """Where each module of one modules view stands: a top-level module's box on the page, a nested module's box from
    the corner of the module it sits in, and the module each nested one sits in."""

    column_gap = MODULE_COL_GAP
    row_gap = MODULE_ROW_GAP
    start_x = MODULE_START_X
    start_y = MODULE_START_Y
    child_pad_x = MODULE_CHILD_PAD_X
    child_pad_y = MODULE_CHILD_PAD_Y
    child_gap = MODULE_CHILD_GAP
    child_columns = MODULE_CHILD_COLS

    def __init__(self, forest: ContainmentForest, cells: Dict[str, DiagramModule]) -> None:
        self.forest = forest
        self.cells = cells
        self.bounds: Dict[str, Geometry] = {}
        self.parent_of: Dict[str, Optional[str]] = {}

    def lay_out(self) -> "ModuleLayout":
        """Layer roots by dependency depth, left to right; nest path children inside their parents."""
        layers: Dict[int, List[str]] = {}
        for root in self.forest.roots:
            layers.setdefault(self.forest.module_dep_depth(root), []).append(root)
        x_cursor = float(self.start_x)
        for depth in sorted(layers):
            names = sorted(layers[depth], key=lambda n: (self.forest.by_name[n].sequential_order or 0, n))
            y = float(self.start_y)
            for name in names:
                self._place(name, (x_cursor, y), None)
                y += self.bounds[name][3] + self.row_gap
            x_cursor += max(self.size(name)[0] for name in names) + self.column_gap
        return self

    def page_box(self, name: str) -> Geometry:
        """Where the module stands on the page, nested or not."""
        box = self.bounds[name]
        parent = self.parent_of.get(name)
        if parent is None:
            return box
        corner = self.page_box(parent)
        return box.shifted(corner.x, corner.y)

    def size(self, name: str) -> Tuple[float, float]:
        """Width and height of a module cell, grown to hold its nested children."""
        cell = self.cells[name]
        header_height = float(cell.header_height())
        children = self.forest.children_of.get(name, [])
        if not children:
            return (float(cell.cell_width), max(float(cell.cell_min_height), header_height))
        columns = min(self.child_columns, len(children))
        widths, heights = grid_extents([self.size(child) for child in children], columns)
        grid_width = sum(widths) + self.child_gap * (columns - 1)
        grid_height = sum(heights) + self.child_gap * (len(heights) - 1)
        return (max(float(cell.cell_width), grid_width + 2 * self.child_pad_x), header_height + grid_height + 2 * self.child_pad_y)

    def _place(self, name: str, position: Tuple[float, float], parent: Optional[str]) -> None:
        if parent is None:
            self.bounds[name] = Geometry(position[0], position[1], *self.size(name))
        self.parent_of[name] = parent
        children = self.forest.children_of.get(name, [])
        if not children:
            return
        header_height = float(self.cells[name].header_height())
        sizes = [self.size(child) for child in children]
        columns = min(self.child_columns, len(children))
        widths, heights = grid_extents(sizes, columns)
        for index, child in enumerate(children):
            column, line = index % columns, index // columns
            relative_x = self.child_pad_x + sum(widths[:column]) + self.child_gap * column
            relative_y = header_height + self.child_pad_y + sum(heights[:line]) + self.child_gap * line
            self.bounds[child] = Geometry(relative_x, relative_y, *sizes[index])
            self._place(child, (position[0] + relative_x, position[1] + relative_y), name)


def grid_extents(sizes: List[Tuple[float, float]], columns: int) -> Tuple[List[float], List[float]]:
    """The widest card in each column and the tallest in each line of a grid filled left to right."""
    widths = [0.0] * columns
    heights = [0.0] * ((len(sizes) + columns - 1) // columns)
    for index, (width, height) in enumerate(sizes):
        widths[index % columns] = max(widths[index % columns], width)
        heights[index // columns] = max(heights[index // columns], height)
    return (widths, heights)
