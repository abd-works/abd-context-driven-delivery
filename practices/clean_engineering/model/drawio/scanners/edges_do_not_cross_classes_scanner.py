"""Scanner: edges-do-not-cross-classes - edge routes must not cut through unrelated class boxes."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner
from practices.clean_engineering.model.drawio import drawio_tools


class EdgesDoNotCrossClassesScanner(DrawioScanner):
    RULE = "edges-do-not-cross-classes"

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        crossings = drawio_tools.check_edges_crossing_classes(page_root)
        # Definitive only - approximate auto-router guesses are warnings elsewhere.
        definitive = [
            (edge, cls) for edge, cls in crossings if "(approx)" not in edge
        ]
        return [
            self.violation(
                f"[{page_name}] Edge {edge} crosses through {cls}",
                location=str(file_path),
            )
            for edge, cls in definitive
        ]


if __name__ == "__main__":
    raise SystemExit(EdgesDoNotCrossClassesScanner.run_main())
