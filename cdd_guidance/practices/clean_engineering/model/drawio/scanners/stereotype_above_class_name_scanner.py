"""Scanner: stereotype-above-class-name — <<Stereotype>> is not inside <b> with the name."""
from __future__ import annotations

import re

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.drawio.drawio_page import (
    DrawioPage,
    class_title_in,
)
from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner

_STEREOTYPE = re.compile(r"<<[^>]+>>|«[^»]+»")


class StereotypeAboveClassNameScanner(DrawioScanner):
    RULE = "stereotype-above-class-name"

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        violations = []
        for cell in page.vertices:
            title = class_title_in(cell.get("value") or "")
            if title and _STEREOTYPE.search(title):
                violations.append(self.violation(
                    page,
                    "Stereotype sits on the same line as the class name inside <b>: "
                    f"{re.sub(r'<[^>]+>', '', title)[:80]!r}",
                ))
        return violations


if __name__ == "__main__":
    raise SystemExit(StereotypeAboveClassNameScanner().run_main())
