"""Scanner: edges-do-not-cross-other-edges - transverse edge crossings (not collinear overlap)."""
from __future__ import annotations
from pathlib import Path
from _drawio_base import DrawioScanner

class EdgesDoNotCrossOtherEdgesScanner(DrawioScanner):
    RULE = 'edges-do-not-cross-other-edges'

    def scan_page(self, page_root) -> list:
        return [
            self.violation(f'[{self._scan_page_name}] {desc_a} crosses {desc_b}: {detail}', location=str(self._scan_file_path))
            for desc_a, desc_b, detail in self._check_edges_crossing_edges(page_root)
        ]
if __name__ == '__main__':
    raise SystemExit(EdgesDoNotCrossOtherEdgesScanner().run_main())
