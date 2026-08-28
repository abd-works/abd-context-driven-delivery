"""Scanner: distinct-anchor-points - multiple edges on one side must not share the default anchor."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner, collect_drawio_files
from context_tools.clean_engineering.class_model.drawio import drawio_tools


class DistinctAnchorPointsScanner(DrawioScanner):
    RULE = "distinct-anchor-points"

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        anchors = drawio_tools.check_shared_anchors(page_root)
        return [
            self.violation(
                f"[{page_name}] {cls_name} {side}: {len(descs)} edges share "
                f"default anchor - {', '.join(descs)}",
                location=str(file_path),
            )
            for cls_name, side, descs in anchors
        ]


if __name__ == "__main__":
    from scan import ScannerRunner

    raise SystemExit(
        ScannerRunner.run_scanner_main(
            DistinctAnchorPointsScanner,
            DistinctAnchorPointsScanner.RULE,
            collect_drawio_files,
        )
    )
