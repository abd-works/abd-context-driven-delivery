"""Scanner: edges-do-not-overlap-edges - orthogonal edges must not share a long collinear span."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner, collect_drawio_files
from context_tools.clean_engineering.class_model.drawio import drawio_tools


class EdgesDoNotOverlapEdgesScanner(DrawioScanner):
    RULE = "edges-do-not-overlap-edges"

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        overlaps = drawio_tools.check_edge_on_edge_overlaps(page_root)
        return [
            self.violation(
                f"[{page_name}] {desc_a} overlaps {desc_b}: {detail}",
                location=str(file_path),
            )
            for desc_a, desc_b, detail in overlaps
        ]


if __name__ == "__main__":
    from scan import ScannerRunner

    raise SystemExit(
        ScannerRunner.run_scanner_main(
            EdgesDoNotOverlapEdgesScanner,
            EdgesDoNotOverlapEdgesScanner.RULE,
            collect_drawio_files,
        )
    )
