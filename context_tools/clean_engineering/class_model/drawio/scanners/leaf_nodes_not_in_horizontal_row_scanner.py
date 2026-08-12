"""Scanner: leaf-nodes-not-in-horizontal-row - hubs must not fan leaves into one wide row."""
from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree as ET

from _drawio_base import DrawioScanner, collect_drawio_files

Y_TOLERANCE = 30
MIN_ROW_SIZE = 4


def _get_vertex_geo(root: ET.Element) -> dict[str, tuple[float, float, float, float]]:
    geo: dict[str, tuple[float, float, float, float]] = {}
    for cell in root.findall("mxCell"):
        if cell.get("vertex") != "1":
            continue
        geometry = cell.find("mxGeometry")
        if geometry is None:
            continue
        width = geometry.get("width")
        height = geometry.get("height")
        if width is None or height is None:
            continue
        geo[cell.get("id", "")] = (
            float(geometry.get("x", 0)),
            float(geometry.get("y", 0)),
            float(width),
            float(height),
        )
    return geo


def _get_edges(root: ET.Element) -> list[tuple[str, str]]:
    edges = []
    for cell in root.findall("mxCell"):
        if cell.get("edge") != "1":
            continue
        src = cell.get("source")
        tgt = cell.get("target")
        if src and tgt:
            edges.append((src, tgt))
    return edges


def _check_page(root: ET.Element) -> list[str]:
    geo = _get_vertex_geo(root)
    edges = _get_edges(root)

    neighbours: dict[str, set[str]] = {}
    for src, tgt in edges:
        if src in geo:
            neighbours.setdefault(src, set()).add(tgt)

    violations = []
    for hub_id, leaf_ids in neighbours.items():
        if len(leaf_ids) < MIN_ROW_SIZE:
            continue

        row_groups: dict[int, list[str]] = {}
        for leaf_id in leaf_ids:
            if leaf_id not in geo:
                continue
            y = geo[leaf_id][1]
            bucket = round(y / Y_TOLERANCE)
            row_groups.setdefault(bucket, []).append(leaf_id)

        for members in row_groups.values():
            if len(members) < MIN_ROW_SIZE:
                continue
            y_vals = [geo[m][1] for m in members]
            y_spread = max(y_vals) - min(y_vals)
            x_vals = [geo[m][0] for m in members]
            x_spread = max(x_vals) - min(x_vals)
            if y_spread <= Y_TOLERANCE and x_spread > 600:
                hub_cell = root.find(f"mxCell[@id='{hub_id}']")
                hub_name = hub_id
                if hub_cell is not None:
                    raw = hub_cell.get("value") or hub_id
                    text = re.sub(r"<[^>]+>", "", raw)
                    text = re.sub(r"&[a-z]+;", " ", text)
                    hub_name = re.split(r"[\s+]", text.strip())[0] or hub_id
                violations.append(
                    f"{hub_name} has {len(members)} leaf neighbours in a horizontal row "
                    f"(y~{int(sum(y_vals) / len(y_vals))}, x-span={int(x_spread)}px)"
                )
    return violations


class LeafNodesNotInHorizontalRowScanner(DrawioScanner):
    RULE = "leaf-nodes-not-in-horizontal-row"

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        return [
            self.violation(f"[{page_name}] {message}", location=str(file_path))
            for message in _check_page(page_root)
        ]


if __name__ == "__main__":
    from scanners import ScannerRunner

    raise SystemExit(
        ScannerRunner.run_scanner_main(
            LeafNodesNotInHorizontalRowScanner,
            LeafNodesNotInHorizontalRowScanner.RULE,
            collect_drawio_files,
        )
    )
