"""Stand up the CDD MCP host and ping every enrolled tool."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


class McpSanity:
    """Ask the host to ping each enrolled tool. The tool body does not run."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.repo = Path(repo or _REPO).resolve()

    def run(self) -> int:
        try:
            host = self._host()
        except Exception as error:
            return self._emit(
                {
                    "ok": False,
                    "ping": "down",
                    "working": [],
                    "broken": [{"tool": "cdd", "error": f"{type(error).__name__}: {error}"}],
                }
            )
        working: list[dict[str, str]] = []
        broken: list[dict[str, str]] = []
        failed = {item.tool for item in host._runtime.exceptions}
        for item in host._runtime.exceptions:
            broken.append({"tool": item.tool, "error": item.reason})
        names = [
            "cdd.ping",
            *sorted(host._runtime.tools),
            *sorted(host._runtime.prompts),
        ]
        for name in names:
            if name in failed:
                continue
            self._ping(host, name, working, broken)
        host_ping = "pong" if any(item["tool"] == "cdd.ping" for item in working) else "down"
        return self._emit(
            {
                "ok": not broken,
                "ping": host_ping,
                "working": working,
                "broken": broken,
                "counts": {"working": len(working), "broken": len(broken)},
            }
        )

    def _host(self) -> Any:
        from installation.installer import Installer
        from harness.mcp.mcp_server import McpHost

        installer = Installer(repo=self.repo)
        refs = tuple(installer.collect_toolsets())
        return McpHost.from_refs(refs, repo=str(self.repo), project=str(self.repo))

    def _ping(
        self,
        host: Any,
        name: str,
        working: list[dict[str, str]],
        broken: list[dict[str, str]],
    ) -> None:
        try:
            reply = host.dispatch(name, {"ping": True})
        except Exception as error:
            broken.append({"tool": name, "error": f"{type(error).__name__}: {error}"})
            return
        if reply == {"ping": "pong", "tool": name}:
            working.append({"tool": name, "detail": "pong"})
            return
        broken.append({"tool": name, "error": f"ping returned {reply!r}"})

    def _emit(self, report: dict[str, Any]) -> int:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(McpSanity().run())
