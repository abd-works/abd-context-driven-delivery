"""Scanner: edges-do-not-cross-other-edges - transverse edge crossings (not collinear overlap)."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner, collect_drawio_files
from context_tools.clean_engineering.class_model.drawio import drawio_tools


def _segments_cross(seg_a, seg_b, endpoint_tol=2):
    (ax1, ay1), (ax2, ay2) = seg_a
    (bx1, by1), (bx2, by2) = seg_b

    a_horiz = abs(ay2 - ay1) < 2
    a_vert = abs(ax2 - ax1) < 2
    b_horiz = abs(by2 - by1) < 2
    b_vert = abs(bx2 - bx1) < 2

    if a_horiz and b_vert:
        y = (ay1 + ay2) / 2
        x = (bx1 + bx2) / 2
        a_lo_x, a_hi_x = sorted((ax1, ax2))
        b_lo_y, b_hi_y = sorted((by1, by2))
        if (
            a_lo_x + endpoint_tol < x < a_hi_x - endpoint_tol
            and b_lo_y + endpoint_tol < y < b_hi_y - endpoint_tol
        ):
            return True, (x, y)
    if a_vert and b_horiz:
        x = (ax1 + ax2) / 2
        y = (by1 + by2) / 2
        a_lo_y, a_hi_y = sorted((ay1, ay2))
        b_lo_x, b_hi_x = sorted((bx1, bx2))
        if (
            a_lo_y + endpoint_tol < y < a_hi_y - endpoint_tol
            and b_lo_x + endpoint_tol < x < b_hi_x - endpoint_tol
        ):
            return True, (x, y)

    return False, None


def _describe_edge(edge_cell, id_to_name):
    src = id_to_name.get(edge_cell.get("source", ""), "?")
    tgt = id_to_name.get(edge_cell.get("target", ""), "?")
    return f"{src} -> {tgt}"


class EdgesDoNotCrossOtherEdgesScanner(DrawioScanner):
    RULE = "edges-do-not-cross-other-edges"

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        classes = drawio_tools.get_all_classes(page_root)
        id_to_name = {cid: name for cid, name, *_ in classes}
        id_to_geo = {cid: (x, y, w, h) for cid, name, x, y, w, h in classes}
        edges = [c for c in page_root.findall("mxCell") if c.get("edge") == "1"]

        edge_segs = [
            (ec, drawio_tools._compute_edge_segments(ec, id_to_geo)) for ec in edges
        ]

        crossings = []
        for i, (ec_a, segs_a) in enumerate(edge_segs):
            for j in range(i + 1, len(edge_segs)):
                ec_b, segs_b = edge_segs[j]
                shared = {ec_a.get("source"), ec_a.get("target")} & {
                    ec_b.get("source"),
                    ec_b.get("target"),
                }
                found = False
                for sa in segs_a:
                    for sb in segs_b:
                        crossed, pt = _segments_cross(sa, sb)
                        if not crossed:
                            continue
                        if shared and pt is not None:
                            skip = False
                            for sid in shared:
                                geo = id_to_geo.get(sid)
                                if not geo:
                                    continue
                                gx, gy, gw, gh = geo
                                if abs(pt[0] - (gx + gw / 2)) < gw / 2 + 5 and abs(
                                    pt[1] - (gy + gh / 2)
                                ) < gh / 2 + 5:
                                    skip = True
                                    break
                            if skip:
                                continue
                        crossings.append(
                            (
                                _describe_edge(ec_a, id_to_name),
                                _describe_edge(ec_b, id_to_name),
                                f"cross at ~({int(pt[0])},{int(pt[1])})",
                            )
                        )
                        found = True
                        break
                    if found:
                        break

        return [
            self.violation(
                f"[{page_name}] {desc_a} crosses {desc_b}: {detail}",
                location=str(file_path),
            )
            for desc_a, desc_b, detail in crossings
        ]


if __name__ == "__main__":
    from scan import ScannerRunner

    raise SystemExit(
        ScannerRunner.run_scanner_main(
            EdgesDoNotCrossOtherEdgesScanner,
            EdgesDoNotCrossOtherEdgesScanner.RULE,
            collect_drawio_files,
        )
    )
