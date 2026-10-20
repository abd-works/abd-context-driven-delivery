"""Full off-host agent-tools probe (ping + invoke + heavy) — same as MCP child work, for manual runs."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    from harness.agent_tools.agent_tools_probe import probe_agent_tools_standalone
    from harness.installation.installer import Installer

    installer = Installer(repo=_REPO)
    report = probe_agent_tools_standalone(installer)
    print(report)
    return 1 if report.split("\n", 1)[0].lstrip("!").startswith("red") else 0


if __name__ == "__main__":
    raise SystemExit(main())
