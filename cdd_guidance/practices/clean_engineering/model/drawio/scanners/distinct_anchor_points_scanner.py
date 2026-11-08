"""Scanner: distinct-anchor-points - multiple edges on one side must not share the default anchor."""
from __future__ import annotations

from xml.etree import ElementTree as ET

from harness.graph.violation import Violation

from cdd_guidance.practices.clean_engineering.model.drawio.drawio_page import (
    DrawioPage,
    anchor_fractions,
    share_inheritance_trunk,
)
from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner

# Anchor fractions are compared to two places, so 0.501 and 0.5 are the same point.
ANCHOR_PRECISION = 2


class DistinctAnchorPointsScanner(DrawioScanner):
    RULE = "distinct-anchor-points"

    def scan_page(self, page: DrawioPage) -> list[Violation]:
        """Edges that leave or enter the same class at exactly the same anchor; no anchor in the style means the centre.
        Subclasses joined into one shared line to their base meet it at one anchor on purpose."""
        users: dict[tuple[str, str, tuple], list[ET.Element]] = {}
        for edge in page.edges:
            for cell_id, end in ((edge.get("source", ""), "exit"), (edge.get("target", ""), "entry")):
                users.setdefault((cell_id, end, self._anchor(edge, end)), []).append(edge)
        return [
            self.violation(
                page,
                f"{page.class_names.get(cell_id, '?')} {end}({anchor[0]},{anchor[1]}): {len(edges)} edges share "
                f"default anchor - {', '.join(page.describe(edge) for edge in edges)}",
            )
            for (cell_id, end, anchor), edges in users.items()
            if len(edges) > 1 and not _one_trunk(edges)
        ]

    def _anchor(self, edge: ET.Element, end: str) -> tuple:
        return tuple(round(value, ANCHOR_PRECISION) if value is not None else "def" for value in anchor_fractions(edge, end))


def _one_trunk(edges: list[ET.Element]) -> bool:
    return all(share_inheritance_trunk(edges[0], edge) for edge in edges[1:])


if __name__ == "__main__":
    raise SystemExit(DistinctAnchorPointsScanner().run_main())
