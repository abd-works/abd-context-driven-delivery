"""Stand up the CDD MCP host and ping every enrolled tool."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

if TYPE_CHECKING:
    from harness.mcp.mcp_server import McpHost

HOST_PING = "cdd.ping"


@dataclass
class SanityReport:
    """Which tools answered their ping and which failed, with the reason each failure gave."""

    working: list[dict[str, str]] = field(default_factory=list)
    broken: list[dict[str, str]] = field(default_factory=list)
    host_down: bool = False

    def answered(self, tool: str) -> None:
        self.working.append({"tool": tool, "detail": "pong"})

    def failed(self, tool: str, error: str) -> None:
        self.broken.append({"tool": tool, "error": error})

    @property
    def ok(self) -> bool:
        return not self.broken

    @property
    def as_data(self) -> dict[str, object]:
        host_ping = "pong" if any(item["tool"] == HOST_PING for item in self.working) else "down"
        data: dict[str, object] = {"ok": self.ok, "ping": host_ping, "working": self.working, "broken": self.broken}
        if not self.host_down:
            data["counts"] = {"working": len(self.working), "broken": len(self.broken)}
        return data

    def emit(self) -> int:
        json.dump(self.as_data, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if self.ok else 1


class McpSanity:
    """Ask the host to ping each enrolled tool. The tool body does not run."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.repo = Path(repo or _REPO).resolve()
        self.report = SanityReport()

    def run(self) -> int:
        from harness.mcp.mcp_server import McpStandupFailed

        try:
            host = self._host()
        except McpStandupFailed as error:
            self.report.host_down = True
            self.report.failed("cdd", f"{type(error).__name__}: {error}")
            return self.report.emit()
        self._ping_enrolled(host)
        return self.report.emit()

    def _ping_enrolled(self, host: McpHost) -> None:
        server = host.checkout_server
        skipped = {item["tool"] for item in server.skipped.as_data}
        for item in server.skipped.as_data:
            self.report.failed(item["tool"], item["reason"])
        for name in [HOST_PING, *sorted(server.tools), *sorted(server.prompts)]:
            if name not in skipped:
                self._ping(host, name)

    def _host(self) -> McpHost:
        from harness.installation.installer import Installer
        from harness.mcp.mcp_server import McpHost

        installer = Installer(repo=self.repo)
        refs = tuple(str(reference) for reference in installer.toolsets.references())
        return McpHost.from_refs(refs, repo=str(self.repo), project=str(self.repo))

    def _ping(self, host: McpHost, name: str) -> None:
        from harness.mcp.mcp_server import ProjectIsClaudeSettings, ProjectNotNamed, ToolNotEnrolled

        try:
            reply = host.dispatch(name, {"ping": True})
        except (ToolNotEnrolled, ProjectNotNamed, ProjectIsClaudeSettings) as error:
            self.report.failed(name, f"{type(error).__name__}: {error}")
            return
        if reply == {"ping": "pong", "tool": name}:
            self.report.answered(name)
            return
        self.report.failed(name, f"ping returned {reply!r}")


if __name__ == "__main__":
    raise SystemExit(McpSanity().run())
