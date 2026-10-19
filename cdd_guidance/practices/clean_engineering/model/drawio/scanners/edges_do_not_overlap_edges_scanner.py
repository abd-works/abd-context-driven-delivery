"""Scanner: edges-do-not-overlap-edges - orthogonal edges must not share a long collinear span."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner


class EdgesDoNotOverlapEdgesScanner(DrawioScanner):
    RULE = "edges-do-not-overlap-edges"

    def scan_page(self, page_root) -> list:
        overlaps = self._check_edge_on_edge_overlaps(page_root)
        return [
            self.violation(
                f"[{self._scan_page_name}] {desc_a} overlaps {desc_b}: {detail}",
                location=str(self._scan_file_path),
            )
            for desc_a, desc_b, detail in overlaps
        ]


if __name__ == "__main__":
    raise SystemExit(EdgesDoNotOverlapEdgesScanner().run_main())
