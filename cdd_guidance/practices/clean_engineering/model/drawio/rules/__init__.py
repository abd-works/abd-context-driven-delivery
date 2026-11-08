"""Draw.io layout rules — each scanner in ../scanners, found by DrawioScanner discovery, checks each diagram once."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DRAWIO_EXTENSIONS, DrawioScanner

# The most violations of one rule a diagram reports; the rest repeat what the first already show.
_SHOWN = 3


class _DrawioScannerRule(PracticeGraphRule):
    """One layout scanner as a graph rule. A diagram's file is scanned once, and what it finds is reported on the first
    class, module, or package the graph read from that file."""

    node_types = ("OoadClass", "Module", "Package")

    def __init__(self, slug: str, scanner_type: type[DrawioScanner]) -> None:
        self.slug = slug
        self.scanner = scanner_type(rule=slug)

    def check_practice(self, context) -> list[tuple[str, str]]:
        if context.source_root is None:
            return []
        found: list[tuple[str, str]] = []
        for relative, node in self._first_node_of_each_diagram(context).items():
            path = context.source_root / relative
            if path.is_file():
                found.extend((node.node_id, violation.message) for violation in self.scanner.scan_file(context.source_root, path)[:_SHOWN])
        return found

    def _first_node_of_each_diagram(self, context) -> dict:
        diagrams: dict = {}
        for node_type in self.node_types:
            for node in context.nodes(node_type):
                relative = node.source.file or ""
                if relative.lower().endswith(tuple(DRAWIO_EXTENSIONS)):
                    diagrams.setdefault(relative, node)
        return diagrams


RULES: tuple[PracticeGraphRule, ...] = tuple(
    _DrawioScannerRule(slug, scanner_type) for slug, scanner_type in DrawioScanner.discover().items()
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
