"""Scanner: class-title-no-markdown-bold — class titles must not contain `**`."""
from __future__ import annotations

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.drawio.page.drawio_page import (
    ClassDiagramPage,
    class_title_in,
    quoted_title,
)
from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner


class ClassTitleNoMarkdownBoldScanner(DrawioScanner):
    RULE = "class-title-no-markdown-bold"

    def scan_page(self, page: ClassDiagramPage) -> list[Violation]:
        violations = []
        for cell in page.vertices:
            title = class_title_in(cell.get("value") or "")
            if title and "**" in title:
                violations.append(self.violation(
                    page,
                    f"Class title still contains markdown bold markers: {quoted_title(title)!r}",
                ))
        return violations


if __name__ == "__main__":
    raise SystemExit(ClassTitleNoMarkdownBoldScanner().run_main())
