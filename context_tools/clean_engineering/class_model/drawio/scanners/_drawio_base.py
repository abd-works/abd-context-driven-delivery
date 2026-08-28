"""Base scanner for Draw.io class-diagram layout rules."""
from __future__ import annotations

from pathlib import Path

from scan import Scanner

from context_tools.clean_engineering.class_model.drawio import drawio_tools

DRAWIO_EXTENSIONS = frozenset({".drawio", ".xml"})


class DrawioScanner(Scanner):
    """Scanners that read `.drawio` mxfile pages via ``drawio_tools``."""

    def scan_file(self, root: Path, file_path: Path) -> list:
        if file_path.suffix.lower() not in DRAWIO_EXTENSIONS:
            return []
        try:
            _, mxfile = drawio_tools.load_drawio(str(file_path))
        except Exception as exc:  # noqa: BLE001 - surface as a scan violation
            return [
                self.violation(
                    f"Could not load drawio file: {exc}",
                    location=str(file_path),
                )
            ]
        violations = []
        for diagram in mxfile.findall("diagram"):
            page_name = diagram.get("name") or "(unnamed)"
            _, page_root = drawio_tools.get_page(mxfile, page_name)
            if page_root is None:
                continue
            violations.extend(self.scan_page(file_path, page_name, page_root))
        return violations

    def scan_page(self, file_path: Path, page_name: str, page_root) -> list:
        """Override: return violations for one diagram page."""
        return []


def collect_drawio_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in DRAWIO_EXTENSIONS:
            continue
        if Scanner.is_skipped_path(path):
            continue
        files.append(path)
    return files
