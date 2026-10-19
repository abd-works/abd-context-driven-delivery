"""Scanner: distinct-anchor-points - multiple edges on one side must not share the default anchor."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner


class DistinctAnchorPointsScanner(DrawioScanner):
    RULE = "distinct-anchor-points"

    def scan_page(self, page_root) -> list:
        anchors = self._check_shared_anchors(page_root)
        return [
            self.violation(
                f"[{self._scan_page_name}] {cls_name} {side}: {len(descs)} edges share "
                f"default anchor - {', '.join(descs)}",
                location=str(self._scan_file_path),
            )
            for cls_name, side, descs in anchors
        ]


if __name__ == "__main__":
    raise SystemExit(DistinctAnchorPointsScanner().run_main())
