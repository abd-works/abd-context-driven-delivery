"""Scan kit — host-bound scanner collection over files on disk."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools.agent_tools import AgentToolSet, agent_toolset
from agent_tools.agent_tools import agent_tool
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp

from .scanner import Scanner
from .scanner_collection import ScannerCollection, ScannerReport

class ScanReport:
    """Scan result consumed by eval Repair: ``ok`` plus ``matches(mistake)``."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self.ok = bool(payload.get("ok", True))
        self.violations = list(payload.get("violations") or [])
        self.payload = payload

    @classmethod
    def from_scan(cls, raw: str | dict[str, Any] | ScanReport) -> ScanReport:
        if isinstance(raw, ScanReport):
            return raw
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

@agent_toolset
class Scan(GuidanceAction):
    """Action kit: ``/scan`` lists context tools; composed ``self.scanner`` is bound to the host."""

    def __init__(self, path: str = ".", session: str = "") -> None:
        self._host = None
        self._bound_collection = None
        super().__init__(path=path, session=session)

    @classmethod
    def bound_to(cls, host: Any, collection: ScannerCollection | None = None) -> Scan:
        """Composed Scan — same kit, bound to a host's rule set. Does not open a workspace."""
        inst = cls.__new__(cls)
        AgentToolSet.__init__(inst)
        inst._host = host
        inst._bound_collection = collection
        inst.workspace = getattr(host, "workspace", None)
        inst._session_name = ""
        inst._guidance_text = None
        inst._tool_items = []
        return inst

    def _scanner_collection(self) -> ScannerCollection:
        if self._bound_collection is not None:
            return self._bound_collection
        host = self._host
        if host is not None:
            return host._scanner_collection()
        raise ValueError(
            "Scan requires a host (or an explicit collection bound from a host) "
            "to know which scanners run"
        )

    def _run(
        self,
        collection: ScannerCollection,
        paths: list[str],
        root: str | None,
        rule: str | None,
    ) -> str:
        files = [Path(path) for path in paths]
        scan_root = Path(root) if root is not None else Path.cwd()
        with Scanner.explicitly_requested(files):
            report: ScannerReport = collection.run(scan_root, files)
        result = report.to_dict()
        if rule is not None:
            result["violations"] = [v for v in result["violations"] if v["rule"] == rule]
            result["ok"] = len(result["violations"]) == 0
        return str(result)

    @Mcp
    @Skill
    @agent_tool
    def scan(
        self,
        paths: list[str],
        root: str | None = None,
        rule: str | None = None,
        guidance: GuidanceArg | None = None,
    ) -> str:
        """Run the listed Guidance hosts' mechanical scanners on the given paths and report potential violations. Fix the source that failed the rule; do not patch the scanner to make the report green. Pass a string to scan once with the bound collection."""
        if guidance is None:
            return self._run(self._scanner_collection(), paths, root, rule)

        def on(item) -> str:
            if isinstance(item, str):
                return self._run(self._scanner_collection(), paths, root, rule)
            return Scan.bound_to(item)._run(
                item._scanner_collection(), paths, root, rule
            )

        results = self.run(guidance, on, action="scan")
        return results[-1] if results else ""
