"""Run agent-tools diagnostics only when this process is the CDD MCP host."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent-tools diagnostics (MCP host process only).")
    parser.add_argument("--guidance", action="append", default=None)
    args = parser.parse_args()
    from harness.agent_tools.agent_tools_probe import ProbeRequiresServingHost, probe_agent_tools
    from harness.installation.installer import Installer
    from harness.mcp.mcp_server import serving_mcp_host

    if serving_mcp_host() is None:
        sys.stderr.write(
            "This script does not start another MCP host. Invoke "
            "agent-tools-diagnostics.agent_tools_diagnostics on the live CDD MCP server.\n"
        )
        return 1
    try:
        report = probe_agent_tools(Installer(repo=_REPO), args.guidance)
    except ProbeRequiresServingHost:
        return 1
    print(report)
    first = report.split("\n", 1)[0].lstrip("!")
    return 1 if first == "red" else 0


if __name__ == "__main__":
    raise SystemExit(main())
