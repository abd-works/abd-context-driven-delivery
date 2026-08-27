"""Scanner: base-above-derived - inheritance parents sit above children (lower y)."""
from __future__ import annotations

from pathlib import Path

from _drawio_base import DrawioScanner, collect_drawio_files
from context_tools.clean_engineering.class_model.drawio import drawio_tools


class BaseAboveDerivedScanner(DrawioScanner):
    RULE = "base-above-derived"

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        violations = []
        for rule, message in drawio_tools.validate_layout(page_root):
            if rule != "hierarchy_flow":
                continue
            violations.append(
                self.violation(f"[{page_name}] {message}", location=str(file_path))
            )
        return violations


if __name__ == "__main__":
    from scan import ScannerRunner

    raise SystemExit(
        ScannerRunner.run_scanner_main(
            BaseAboveDerivedScanner,
            BaseAboveDerivedScanner.RULE,
            collect_drawio_files,
        )
    )
