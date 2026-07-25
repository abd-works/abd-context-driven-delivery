"""Scan kit — mergeable toolset face over ScannerCollection."""

from __future__ import annotations

from pathlib import Path

from tools.tool import tool

from .scanner_collection import ScannerCollection


class Scan:
    """Toolset-facing scan binding; domains override ``_scanner_collection``."""

    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection()

    @tool
    def scan(self, paths: list[str]) -> str:
        """scan"""
        files = [Path(path) for path in paths]
        report = self._scanner_collection().run(Path.cwd(), files)
        return str(report.to_dict())
