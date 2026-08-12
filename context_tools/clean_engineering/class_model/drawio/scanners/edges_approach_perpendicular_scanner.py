"""Scanner: edges-approach-perpendicular - edge tips hit class sides head-on, not sliding along."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner, collect_drawio_files
from context_tools.clean_engineering.class_model.drawio import drawio_tools


def _classify_edge(style: str) -> str:
    style = (style or "").lower()
    if "endarrow=block" in style and "startarrow=block" not in style:
        if "endfill=0" in style:
            return "inheritance-orthogonal" if "orthogonal" in style else "inheritance"
        return "association"
    if "startarrow=diamondthin" in style or "startarrow=diamond" in style:
        return "composition" if "startfill=1" in style else "aggregation"
    return "association"


def _anchor_side(frac_x: float | None, frac_y: float | None) -> str | None:
    if frac_x is None or frac_y is None:
        return None
    if abs(frac_x - 0) < 1e-3:
        return "left"
    if abs(frac_x - 1) < 1e-3:
        return "right"
    if abs(frac_y - 0) < 1e-3:
        return "top"
    if abs(frac_y - 1) < 1e-3:
        return "bottom"
    return None


def _parse_style(style: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for kv in (style or "").split(";"):
        if "=" not in kv:
            continue
        key, value = kv.split("=", 1)
        try:
            out[key] = float(value)
        except ValueError:
            continue
    return out


def _segment_direction(seg) -> str | None:
    (x1, y1), (x2, y2) = seg
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    if dx < 1 and dy < 1:
        return None
    if dx < 1:
        return "v"
    if dy < 1:
        return "h"
    return None


def _segment_direction_signed(seg) -> str | None:
    (x1, y1), (x2, y2) = seg
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) < 1 and abs(dy) < 1:
        return None
    if abs(dx) >= abs(dy):
        return "right" if dx > 0 else "left"
    return "down" if dy > 0 else "up"


def _expected_direction_for_side(side: str | None) -> str | None:
    if side in ("left", "right"):
        return "h"
    if side in ("top", "bottom"):
        return "v"
    return None


def _outward_direction(side: str | None) -> str | None:
    return {"left": "left", "right": "right", "top": "up", "bottom": "down"}.get(side or "")


def _inward_direction(side: str | None) -> str | None:
    return {"left": "right", "right": "left", "top": "down", "bottom": "up"}.get(side or "")


def _check_edges_approach_perpendicular(root):
    classes = drawio_tools.get_all_classes(root)
    id_to_name = {cid: name for cid, name, *_ in classes}
    id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}

    violations = []
    for cell in root.findall("mxCell"):
        if cell.get("edge") != "1":
            continue
        src_id = cell.get("source", "")
        tgt_id = cell.get("target", "")
        if src_id not in id_to_name or tgt_id not in id_to_name:
            continue

        style = cell.get("style", "")
        attrs = _parse_style(style)
        exit_side = _anchor_side(attrs.get("exitX"), attrs.get("exitY"))
        entry_side = _anchor_side(attrs.get("entryX"), attrs.get("entryY"))

        segs, _ = drawio_tools._compute_edge_segments_ex(cell, id_to_geo)
        if not segs:
            continue

        etype = _classify_edge(style)
        desc = f"{id_to_name[src_id]}->{id_to_name[tgt_id]} ({etype})"

        expected_orient = _expected_direction_for_side(exit_side)
        actual_orient = _segment_direction(segs[0])
        if expected_orient and actual_orient and actual_orient != expected_orient:
            violations.append((desc, "source", exit_side, expected_orient, actual_orient))
        else:
            want = _outward_direction(exit_side)
            got = _segment_direction_signed(segs[0])
            if want and got and got != want:
                violations.append((desc, "source", exit_side, want, got))

        expected_orient = _expected_direction_for_side(entry_side)
        actual_orient = _segment_direction(segs[-1])
        if expected_orient and actual_orient and actual_orient != expected_orient:
            violations.append((desc, "target", entry_side, expected_orient, actual_orient))
        else:
            want = _inward_direction(entry_side)
            got = _segment_direction_signed(segs[-1])
            if want and got and got != want:
                violations.append((desc, "target", entry_side, want, got))

    return violations


class EdgesApproachPerpendicularScanner(DrawioScanner):
    RULE = "edges-approach-perpendicular"

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        return [
            self.violation(
                f"[{page_name}] {desc}: {end} segment goes {actual} but anchor is on "
                f"the {side} side (expected {expected})",
                location=str(file_path),
            )
            for desc, end, side, expected, actual in _check_edges_approach_perpendicular(
                page_root
            )
        ]


if __name__ == "__main__":
    from scanners import ScannerRunner

    raise SystemExit(
        ScannerRunner.run_scanner_main(
            EdgesApproachPerpendicularScanner,
            EdgesApproachPerpendicularScanner.RULE,
            collect_drawio_files,
        )
    )
