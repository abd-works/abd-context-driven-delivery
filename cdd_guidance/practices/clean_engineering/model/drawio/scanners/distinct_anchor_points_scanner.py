"""Scanner: distinct-anchor-points - multiple edges on one side must not share the default anchor."""
from __future__ import annotations

from xml.etree import ElementTree as ET

from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import (
    DrawioPage,
    DrawioScanner,
    DrawioViolation,
    style_number,
)

# Anchor fractions are compared to two places, so 0.501 and 0.5 are the same point.
ANCHOR_PRECISION = 2


class DistinctAnchorPointsScanner(DrawioScanner):
    RULE = "distinct-anchor-points"

    def scan_page(self, page: DrawioPage) -> list[DrawioViolation]:
        """Edges that leave or enter the same class at exactly the same anchor; no anchor in the style means the centre."""
        users: dict[tuple[str, str, tuple], list[str]] = {}
        for edge in page.edges:
            description = page.describe(edge)
            for cell_id, end in ((edge.get("source", ""), "exit"), (edge.get("target", ""), "entry")):
                users.setdefault((cell_id, end, self._anchor(edge, end)), []).append(description)
        return [
            self.violation(
                page,
                f"{page.class_names.get(cell_id, '?')} {end}({anchor[0]},{anchor[1]}): {len(descriptions)} edges share "
                f"default anchor - {', '.join(descriptions)}",
            )
            for (cell_id, end, anchor), descriptions in users.items()
            if len(descriptions) > 1
        ]

    def _anchor(self, edge: ET.Element, end: str) -> tuple:
        style = edge.get("style", "")
        fractions = (style_number(style, f"{end}X"), style_number(style, f"{end}Y"))
        return tuple(round(value, ANCHOR_PRECISION) if value is not None else "def" for value in fractions)


if __name__ == "__main__":
    raise SystemExit(DistinctAnchorPointsScanner().run_main())
