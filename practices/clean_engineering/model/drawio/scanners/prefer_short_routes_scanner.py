"""Scanner: prefer-short-routes — keep related classes close; few waypoints."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner


class PreferShortRoutesScanner(DrawioScanner):
    RULE = "prefer-short-routes"

    def scan_page(self, page_root) -> list:
        return [
            self.violation(
                f"[{self._scan_page_name}] {desc}: {reason}",
                location=str(self._scan_file_path),
            )
            for desc, reason in self._check_prefer_short_routes(page_root)
        ]


if __name__ == "__main__":
    raise SystemExit(PreferShortRoutesScanner().run_main())
