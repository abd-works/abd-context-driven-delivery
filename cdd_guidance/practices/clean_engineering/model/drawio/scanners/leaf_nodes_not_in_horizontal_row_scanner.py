"""Scanner: leaf-nodes-not-in-horizontal-row - hubs must not fan leaves into one wide row."""
from __future__ import annotations

import re

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Geometry
from cdd_guidance.practices.clean_engineering.model.drawio.page.drawio_page import (
    DrawioPage,
)
from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner

Y_TOLERANCE = 30
MIN_ROW_SIZE = 4
# A line of leaves narrower than this many pixels still reads as a cluster, not a wide row.
WIDE_ROW_SPAN = 600


class LeafNodesNotInHorizontalRowScanner(DrawioScanner):
    RULE = "leaf-nodes-not-in-horizontal-row"

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        boxes = _sized_vertex_boxes(page)
        neighbours: dict[str, set[str]] = {}
        for edge in page.edges:
            source, target = edge.get("source"), edge.get("target")
            if source and target and source in boxes:
                neighbours.setdefault(source, set()).add(target)
        violations = []
        for hub_id, leaf_ids in neighbours.items():
            if len(leaf_ids) < MIN_ROW_SIZE:
                continue
            for members in _lines_of(leaf_ids, boxes):
                message = _wide_line_message(_hub_name(page, hub_id), members, boxes)
                if message:
                    violations.append(self.violation(page, message))
        return violations


def _sized_vertex_boxes(page: DrawioPage) -> dict[str, Geometry]:
    boxes: dict[str, Geometry] = {}
    for cell in page.cells:
        geometry = cell.find("mxGeometry")
        if cell.get("vertex") != "1" or geometry is None or geometry.get("width") is None or geometry.get("height") is None:
            continue
        boxes[cell.get("id", "")] = (
            float(geometry.get("x", 0)), float(geometry.get("y", 0)), float(geometry.get("width")), float(geometry.get("height"))
        )
    return boxes


def _lines_of(leaf_ids: set[str], boxes: dict[str, Geometry]) -> list[list[str]]:
    """The leaves grouped by roughly equal height on the page."""
    lines: dict[int, list[str]] = {}
    for leaf_id in leaf_ids:
        if leaf_id in boxes:
            lines.setdefault(round(boxes[leaf_id][1] / Y_TOLERANCE), []).append(leaf_id)
    return list(lines.values())


def _wide_line_message(hub_name: str, members: list[str], boxes: dict[str, Geometry]) -> str | None:
    if len(members) < MIN_ROW_SIZE:
        return None
    y_values = [boxes[member][1] for member in members]
    x_values = [boxes[member][0] for member in members]
    x_spread = max(x_values) - min(x_values)
    if max(y_values) - min(y_values) > Y_TOLERANCE or x_spread <= WIDE_ROW_SPAN:
        return None
    return (
        f"{hub_name} has {len(members)} leaf neighbours in a horizontal row "
        f"(y~{int(sum(y_values) / len(y_values))}, x-span={int(x_spread)}px)"
    )


def _hub_name(page: DrawioPage, hub_id: str) -> str:
    hub_cell = page.cell(hub_id)
    if hub_cell is None:
        return hub_id
    text = re.sub("<[^>]+>", "", hub_cell.get("value") or hub_id)
    text = re.sub("&[a-z]+;", " ", text)
    return re.split(r"[\s+]", text.strip())[0] or hub_id


if __name__ == "__main__":
    raise SystemExit(LeafNodesNotInHorizontalRowScanner().run_main())
