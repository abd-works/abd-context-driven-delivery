"""Scanner: prefer-short-routes — keep related classes close; few waypoints."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner, collect_drawio_files
from context_tools.clean_engineering.class_model.drawio import drawio_tools


class PreferShortRoutesScanner(DrawioScanner):
    RULE = "prefer-short-routes"

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        return [
            self.violation(
                f"[{page_name}] {desc}: {reason}",
                location=str(file_path),
            )
            for desc, reason in drawio_tools.check_prefer_short_routes(page_root)
        ]


if __name__ == "__main__":
    from scan import ScannerRunner

    raise SystemExit(
        ScannerRunner.run_scanner_main(
            PreferShortRoutesScanner,
            PreferShortRoutesScanner.RULE,
            collect_drawio_files,
        )
    )
