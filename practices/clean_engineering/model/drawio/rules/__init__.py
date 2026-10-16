"""Draw.io layout rules — reuse scanners in ../scanners via DrawioScanner discovery."""

from __future__ import annotations

from pathlib import Path

from harness.graph.practice_rule import PracticeGraphRule

from practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner


class _DrawioDiscovery(DrawioScanner):
    def scan_file(self, root: Path, file_path: Path) -> list:
        return []


def _scanner_types() -> dict[str, type]:
    helper = _DrawioDiscovery()
    return helper.discover()


class _DrawioScannerRule(PracticeGraphRule):
    node_types = ("OoadClass", "Module", "Package")

    def __init__(self, slug: str, scanner_type: type) -> None:
        self.slug = slug
        self._scanner_type = scanner_type

    def check(self, node, context) -> list[str]:
        relative = node.source.file or ""
        if not relative.lower().endswith((".drawio", ".xml")):
            return []
        if context.source_root is None:
            return []
        path = context.source_root / relative
        if not path.is_file():
            return []
        scanner = self._scanner_type(rule=self.slug)
        violations = scanner.scan_file(context.source_root, path)
        return [v.message for v in violations[:3]]


RULES: tuple[PracticeGraphRule, ...] = tuple(
    _DrawioScannerRule(slug, scanner_type) for slug, scanner_type in _scanner_types().items()
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
