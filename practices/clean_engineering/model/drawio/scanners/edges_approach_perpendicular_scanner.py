"""Scanner: edges-approach-perpendicular - edge tips hit class sides head-on, not sliding along."""
from __future__ import annotations
from pathlib import Path
from _drawio_base import DrawioScanner

class EdgesApproachPerpendicularScanner(DrawioScanner):
    RULE = 'edges-approach-perpendicular'

    def scan_page(self, page_root) -> list:
        return [self.violation(f'[{self._scan_page_name}] {desc}: {end} segment goes {actual} but anchor is on the {side} side (expected {expected})', location=str(self._scan_file_path)) for desc, end, side, expected, actual in self._check_edges_approach_perpendicular(page_root)]

    def _classify_edge(self, style: str) -> str:
        style = (style or '').lower()
        if 'endarrow=block' in style and 'startarrow=block' not in style:
            if 'endfill=0' in style:
                return 'inheritance-orthogonal' if 'orthogonal' in style else 'inheritance'
            return 'association'
        if 'startarrow=diamondthin' in style or 'startarrow=diamond' in style:
            return 'composition' if 'startfill=1' in style else 'aggregation'
        return 'association'

    def _anchor_side(self, frac_x: float | None, frac_y: float | None) -> str | None:
        if frac_x is None or frac_y is None:
            return None
        if abs(frac_x - 0) < 0.001:
            return 'left'
        if abs(frac_x - 1) < 0.001:
            return 'right'
        if abs(frac_y - 0) < 0.001:
            return 'top'
        if abs(frac_y - 1) < 0.001:
            return 'bottom'
        return None

    def _parse_style(self, style: str) -> dict[str, float]:
        out: dict[str, float] = {}
        for kv in (style or '').split(';'):
            if '=' not in kv:
                continue
            key, value = kv.split('=', 1)
            try:
                out[key] = float(value)
            except ValueError:
                continue
        return out

    def _segment_direction(self, seg) -> str | None:
        (x1, y1), (x2, y2) = seg
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        if dx < 1 and dy < 1:
            return None
        if dx < 1:
            return 'v'
        if dy < 1:
            return 'h'
        return None

    def _segment_direction_signed(self, seg) -> str | None:
        (x1, y1), (x2, y2) = seg
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) < 1 and abs(dy) < 1:
            return None
        if abs(dx) >= abs(dy):
            return 'right' if dx > 0 else 'left'
        return 'down' if dy > 0 else 'up'

    def _expected_direction_for_side(self, side: str | None) -> str | None:
        if side in ('left', 'right'):
            return 'h'
        if side in ('top', 'bottom'):
            return 'v'
        return None

    def _outward_direction(self, side: str | None) -> str | None:
        return {'left': 'left', 'right': 'right', 'top': 'up', 'bottom': 'down'}.get(side or '')

    def _inward_direction(self, side: str | None) -> str | None:
        return {'left': 'right', 'right': 'left', 'top': 'down', 'bottom': 'up'}.get(side or '')

    def _check_edges_approach_perpendicular(self, root):
        classes = self._get_all_classes(root)
        self._id_to_name = {cid: name for cid, name, *_ in classes}
        self._id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}
        violations = []
        for cell in root.findall('mxCell'):
            self._record_edge_approach(cell, violations)
        return violations

    def _record_edge_approach(self, cell, violations) -> None:
        if cell.get('edge') != '1':
            return
        src_id = cell.get('source', '')
        tgt_id = cell.get('target', '')
        if src_id not in self._id_to_name or tgt_id not in self._id_to_name:
            return
        style = cell.get('style', '')
        attrs = self._parse_style(style)
        segs, _ = self._compute_edge_segments_ex(cell, self._id_to_geo)
        if not segs:
            return
        etype = self._classify_edge(style)
        desc = f'{self._id_to_name[src_id]}->{self._id_to_name[tgt_id]} ({etype})'
        self._approach_desc = desc
        self._approach_end = 'source'
        self._approach_side = self._anchor_side(attrs.get('exitX'), attrs.get('exitY'))
        self._append_end_approach(violations, segs[0])
        self._approach_end = 'target'
        self._approach_side = self._anchor_side(attrs.get('entryX'), attrs.get('entryY'))
        self._append_end_approach(violations, segs[-1])

    def _append_end_approach(self, violations, seg) -> None:
        side = self._approach_side
        end = self._approach_end
        desc = self._approach_desc
        expected = self._expected_direction_for_side(side)
        actual = self._segment_direction(seg)
        if expected and actual and (actual != expected):
            violations.append((desc, end, side, expected, actual))
            return
        want = self._outward_direction(side) if end == 'source' else self._inward_direction(side)
        got = self._segment_direction_signed(seg)
        if want and got and (got != want):
            violations.append((desc, end, side, want, got))
if __name__ == '__main__':
    raise SystemExit(EdgesApproachPerpendicularScanner().run_main())
