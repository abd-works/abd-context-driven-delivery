"""Scan kit - mergeable toolset face over ScannerCollection."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from tools.tool import agent_tool

from .scanner import Scanner
from .scanner_collection import ScannerCollection


class ScanReport:
    """Scan result consumed by eval Repair: ``ok`` plus ``matches(mistake)``."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self.ok = bool(payload.get("ok", True))
        self.violations = list(payload.get("violations") or [])
        self.payload = payload

    @classmethod
    def from_scan(cls, raw: str | dict[str, Any]) -> ScanReport:
        payload = ast.literal_eval(raw) if isinstance(raw, str) else raw
        return cls(payload)

    def matches(self, mistake: Any) -> bool:
        """True when a violation is already this Mistake (rule + artifact)."""
        rule = str(getattr(mistake, "rule", "") or "")
        artifact = str(getattr(mistake, "artifact", "") or "")
        artifact_name = Path(artifact).name if artifact else ""
        for violation in self.violations:
            if rule and str(violation.get("rule") or "") != rule:
                continue
            location = str(violation.get("location") or "")
            if artifact and artifact not in location and artifact_name not in location:
                if location:
                    continue
            return True
        return False


class Scan:
    """Toolset-facing scan binding; domains override ``_scanner_collection``."""

    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection()

    @agent_tool
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
        with Scanner.explicitly_requested(files):
            report = self._scanner_collection().run(scan_root, files)
        result = report.to_dict()
        if rule is not None:
            result["violations"] = [v for v in result["violations"] if v["rule"] == rule]
            result["ok"] = len(result["violations"]) == 0
        return str(result)
