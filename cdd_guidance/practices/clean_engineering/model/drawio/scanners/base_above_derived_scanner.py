"""Scanner: base-above-derived - inheritance parents sit above children (lower y)."""
from __future__ import annotations

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import (
    DrawioPage,
    DrawioScanner,
    is_inheritance,
)


class BaseAboveDerivedScanner(DrawioScanner):
    RULE = "base-above-derived"

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        violations = []
        for edge in page.edges:
            if not is_inheritance(edge):
                continue
            child_id, parent_id = edge.get("source", ""), edge.get("target", "")
            if child_id not in page.boxes or parent_id not in page.boxes:
                continue
            child_y, parent_y = page.boxes[child_id][1], page.boxes[parent_id][1]
            if child_y <= parent_y:
                violations.append(self.violation(
                    page,
                    f"Inheritance: {page.class_names[child_id]} (y={child_y}) should be below parent "
                    f"{page.class_names[parent_id]} (y={parent_y}); base at top, children below",
                ))
        return violations


if __name__ == "__main__":
    raise SystemExit(BaseAboveDerivedScanner().run_main())
