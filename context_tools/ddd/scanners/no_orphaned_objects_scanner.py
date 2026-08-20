"""Scanner: no-orphaned-objects — every domain class vertex must have an edge."""
from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from scanners import Scanner, ScannerRunner

RULE = "no-orphaned-objects"
_SUFFIXES = frozenset({".drawio", ".xml"})
_CLASSISH = re.compile(
    r"<<|Aggregate Root|Entity|Value Object|Repository|Factory|Domain Service"
)


def _cell_label(cell: ET.Element) -> str:
    raw = cell.get("value") or ""
    return html.unescape(re.sub(r"<[^>]+>", " ", raw)).strip()


class NoOrphanedObjectsScanner(Scanner):
    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if file_path.suffix.lower() not in _SUFFIXES:
            return []
        try:
            tree = ET.parse(file_path)
        except ET.ParseError as exc:
            return [
                self.violation(
                    f"Could not parse diagram: {exc}",
                    location=str(file_path),
                )
            ]
        connected: set[str] = set()
        vertices: list[ET.Element] = []
        for cell in tree.iter("mxCell"):
            cell_id = cell.get("id") or ""
            if cell.get("edge") == "1":
                for end in (cell.get("source"), cell.get("target")):
                    if end:
                        connected.add(end)
                continue
            if cell.get("vertex") != "1":
                continue
            label = _cell_label(cell)
            if not label or not cell_id:
                continue
            if not (_CLASSISH.search(label) or re.match(r"^[A-Z][A-Za-z0-9]+", label)):
                continue
            vertices.append(cell)
        violations = []
        for cell in vertices:
            cell_id = cell.get("id") or ""
            if cell_id in connected:
                continue
            label = _cell_label(cell).split()[0]
            violations.append(
                self.violation(
                    f"Domain object '{label}' has no relationship. "
                    "Connect it with a dependency, composition, or association.",
                    location=str(file_path),
                )
            )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            NoOrphanedObjectsScanner,
            RULE,
            lambda root: sorted(p for p in root.rglob("*") if p.suffix.lower() in _SUFFIXES),
        )
    )
