"""Scanner: class-title-no-markdown-bold — class titles must not contain `**`."""
from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import (
    DrawioPage,
    DrawioScanner,
    DrawioViolation,
    class_title_in,
)


class ClassTitleNoMarkdownBoldScanner(DrawioScanner):
    RULE = "class-title-no-markdown-bold"

    def scan_page(self, page: DrawioPage) -> list[DrawioViolation]:
        violations = []
        for cell in page.root.iter("mxCell"):
            title = class_title_in(cell.get("value") or "") if cell.get("vertex") == "1" else None
            if title and "**" in title:
                violations.append(self.violation(
                    page,
                    f"Class title still contains markdown bold markers: {re.sub(r'<[^>]+>', '', title)[:80]!r}",
                ))
        return violations


if __name__ == "__main__":
    raise SystemExit(ClassTitleNoMarkdownBoldScanner().run_main())
