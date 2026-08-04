"""Scan kit - mergeable toolset face over ScannerCollection."""

from __future__ import annotations

from pathlib import Path

from tools.tool import tool

from .scanner_collection import ScannerCollection


class Scan:
    """Toolset-facing scan binding; domains override ``_scanner_collection``."""

    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection()

    @tool
    def scan(self, paths: list[str], root: str | None = None, rule: str | None = None) -> str:
        """scan

        ``root`` defaults to ``cwd`` for ordinary project scans. Callers that
        already know the narrow directory a scan belongs to (e.g. one
        regression fixture folder) should pass it explicitly - a graph-wide
        scanner (``StoryWorkspaceScanner``) loads everything under ``root``,
        so an unscoped ``cwd`` makes it walk the whole repo.

        ``rule`` narrows the ``ok`` verdict to violations of that one rule
        slug - a regression fixture built to exercise a single rule is not
        a complete artifact and would otherwise trip every unrelated
        scanner too."""
        files = [Path(path) for path in paths]
        scan_root = Path(root) if root is not None else Path.cwd()
        report = self._scanner_collection().run(scan_root, files)
        result = report.to_dict()
        if rule is not None:
            result["violations"] = [v for v in result["violations"] if v["rule"] == rule]
            result["ok"] = len(result["violations"]) == 0
        return str(result)
