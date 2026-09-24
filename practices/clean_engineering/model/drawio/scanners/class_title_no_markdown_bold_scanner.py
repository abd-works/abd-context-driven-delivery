"""Scanner: class-title-no-markdown-bold — class titles must not contain `**`."""
from __future__ import annotations

import html
import re
from pathlib import Path

from _drawio_base import DrawioScanner


class ClassTitleNoMarkdownBoldScanner(DrawioScanner):
    RULE = "class-title-no-markdown-bold"

    def scan_page(self, page_root) -> list:
        violations = []
        for cell in page_root.iter("mxCell"):
            if cell.get("vertex") != "1":
                continue
            raw = cell.get("value") or ""
            if not raw:
                continue
            text = self._unescape(html.unescape(raw))
            match = re.search(r"<b[^>]*>(.*?)</b>", text, re.IGNORECASE | re.DOTALL)
            if not match:
                continue
            title = match.group(1)
            if "**" in title or re.search(r"\*\*[^*]+\*\*", title):
                violations.append(
                    self.violation(
                        f"[{self._scan_page_name}] Class title still contains markdown bold "
                        f"markers: {re.sub(r'<[^>]+>', '', title)[:80]!r}",
                        location=str(self._scan_file_path),
                    )
                )
        return violations


if __name__ == "__main__":
    raise SystemExit(ClassTitleNoMarkdownBoldScanner().run_main())
