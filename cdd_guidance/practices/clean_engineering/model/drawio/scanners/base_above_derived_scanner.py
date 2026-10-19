"""Scanner: base-above-derived - inheritance parents sit above children (lower y)."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner


class BaseAboveDerivedScanner(DrawioScanner):
    RULE = "base-above-derived"

    def scan_page(self, page_root) -> list:
        violations = []
        for rule, message in self._validate_layout(page_root):
            if rule != "hierarchy_flow":
                continue
            violations.append(
                self.violation(f"[{self._scan_page_name}] {message}", location=str(self._scan_file_path))
            )
        return violations


if __name__ == "__main__":
    raise SystemExit(BaseAboveDerivedScanner().run_main())
