"""Dev helper: full agent-tools probe without stdio MCP (loads a one-off host — slow)."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_DIAG = _REPO.parent / "cdd-diagnostic" / "src"
if _DIAG.is_dir() and str(_DIAG) not in sys.path:
    sys.path.insert(0, str(_DIAG))
os.environ.setdefault("CDD_DIAGNOSTIC_REPO", str(_REPO.parent / "cdd-diagnostic"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--guidance", action="append", default=None)
    args = parser.parse_args()
    from harness.agent_tools.agent_tools_probe import probe_agent_tools_standalone
    from harness.installation.installer import Installer

    installer = Installer(path=args.path, repo=_REPO)
    installer.ensure_import_path()
    report = probe_agent_tools_standalone(installer, args.guidance)
    print(report)
    first_lines = [line.lstrip("!") for line in report.split("\n") if line.strip()]
    return 1 if any(line.startswith("red") for line in first_lines[:4]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
