"""Scanner: leaf-nodes-not-in-horizontal-row - hubs must not fan leaves into one wide row."""
from __future__ import annotations
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from _drawio_base import DrawioScanner
Y_TOLERANCE = 30
MIN_ROW_SIZE = 4

class LeafNodesNotInHorizontalRowScanner(DrawioScanner):
    RULE = 'leaf-nodes-not-in-horizontal-row'

    def scan_page(self, page_root) -> list:
        return [self.violation(f'[{self._scan_page_name}] {message}', location=str(self._scan_file_path)) for message in self._check_page(page_root)]

    def _get_vertex_geo(self, root: ET.Element) -> dict[str, tuple[float, float, float, float]]:
        geo: dict[str, tuple[float, float, float, float]] = {}
        for cell in root.findall('mxCell'):
            if cell.get('vertex') != '1':
                continue
            geometry = cell.find('mxGeometry')
            if geometry is None:
                continue
            width = geometry.get('width')
            height = geometry.get('height')
            if width is None or height is None:
                continue
            geo[cell.get('id', '')] = (float(geometry.get('x', 0)), float(geometry.get('y', 0)), float(width), float(height))
        return geo

    def _get_edges(self, root: ET.Element) -> list[tuple[str, str]]:
        edges = []
        for cell in root.findall('mxCell'):
            if cell.get('edge') != '1':
                continue
            src = cell.get('source')
            tgt = cell.get('target')
            if src and tgt:
                edges.append((src, tgt))
        return edges

    def _check_page(self, root: ET.Element) -> list[str]:
        self._page_root = root
        self._page_geo = self._get_vertex_geo(root)
        neighbours = self._outgoing_neighbours()
        violations = []
        for hub_id, leaf_ids in neighbours.items():
            violations.extend(self._hub_row_violations(hub_id, leaf_ids))
        return violations

    def _outgoing_neighbours(self) -> dict[str, set[str]]:
        neighbours: dict[str, set[str]] = {}
        for src, tgt in self._get_edges(self._page_root):
            if src in self._page_geo:
                neighbours.setdefault(src, set()).add(tgt)
        return neighbours

    def _hub_row_violations(self, hub_id, leaf_ids) -> list[str]:
        if len(leaf_ids) < MIN_ROW_SIZE:
            return []
        violations = []
        self._hub_id = hub_id
        for members in self._row_groups(leaf_ids).values():
            message = self._wide_row_message(members)
            if message:
                violations.append(message)
        return violations

    def _row_groups(self, leaf_ids) -> dict[int, list[str]]:
        row_groups: dict[int, list[str]] = {}
        geo = self._page_geo
        for leaf_id in leaf_ids:
            if leaf_id not in geo:
                continue
            bucket = round(geo[leaf_id][1] / Y_TOLERANCE)
            row_groups.setdefault(bucket, []).append(leaf_id)
        return row_groups

    def _wide_row_message(self, members):
        if len(members) < MIN_ROW_SIZE:
            return None
        geo = self._page_geo
        y_vals = [geo[m][1] for m in members]
        x_vals = [geo[m][0] for m in members]
        y_spread = max(y_vals) - min(y_vals)
        x_spread = max(x_vals) - min(x_vals)
        if y_spread > Y_TOLERANCE or x_spread <= 600:
            return None
        hub_name = self._hub_display_name(self._hub_id)
        return f'{hub_name} has {len(members)} leaf neighbours in a horizontal row (y~{int(sum(y_vals) / len(y_vals))}, x-span={int(x_spread)}px)'

    def _hub_display_name(self, hub_id) -> str:
        hub_cell = self._page_root.find(f"mxCell[@id='{hub_id}']")
        if hub_cell is None:
            return hub_id
        raw = hub_cell.get('value') or hub_id
        text = re.sub('<[^>]+>', '', raw)
        text = re.sub('&[a-z]+;', ' ', text)
        return re.split('[\\s+]', text.strip())[0] or hub_id
if __name__ == '__main__':
    raise SystemExit(LeafNodesNotInHorizontalRowScanner().run_main())
