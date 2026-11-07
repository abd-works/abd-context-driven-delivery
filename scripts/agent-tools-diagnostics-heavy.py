"""Full off-host agent-tools probe (ping + invoke + heavy) — same as MCP child work, for manual runs."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    from harness.diagnostics.agent_tools_probe import AgentToolsProbe
    from harness.installer.installer import Installer

    installer = Installer(repo=_REPO)
    report = AgentToolsProbe(installer).run_standalone()
    print(report)
    return 1 if report.split("\n", 1)[0].lstrip("!").startswith("red") else 0


if __name__ == "__main__":
    raise SystemExit(main())
