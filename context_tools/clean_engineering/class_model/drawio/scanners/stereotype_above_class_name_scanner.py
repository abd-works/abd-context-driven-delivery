"""Scanner: stereotype-above-class-name — <<Stereotype>> is not inside <b> with the name."""
from __future__ import annotations

import html
import re
from pathlib import Path

from _drawio_base import DrawioScanner, collect_drawio_files
from context_tools.clean_engineering.class_model.drawio.drawio_tools import unescape

RULE = "stereotype-above-class-name"
_STEREOTYPE = re.compile(r"<<[^>]+>>|«[^»]+»")


class StereotypeAboveClassNameScanner(DrawioScanner):
    RULE = RULE

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        violations = []
        for cell in page_root.iter("mxCell"):
            if cell.get("vertex") != "1":
                continue
            raw = cell.get("value") or ""
            if not raw:
                continue
            text = unescape(html.unescape(raw))
            match = re.search(r"<b[^>]*>(.*?)</b>", text, re.IGNORECASE | re.DOTALL)
            if not match:
                continue
            title = match.group(1)
            if _STEREOTYPE.search(title):
                violations.append(
                    self.violation(
                        f"[{page_name}] Stereotype sits on the same line as the "
                        f"class name inside <b>: "
                        f"{re.sub(r'<[^>]+>', '', title)[:80]!r}",
                        location=str(file_path),
                    )
                )
        return violations


if __name__ == "__main__":
    from scanners import ScannerRunner

    raise SystemExit(
        ScannerRunner.run_scanner_main(
            StereotypeAboveClassNameScanner,
            RULE,
            collect_drawio_files,
        )
    )
