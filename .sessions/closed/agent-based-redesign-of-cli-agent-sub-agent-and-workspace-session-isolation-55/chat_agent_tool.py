"""Run ChatAgent phased tools for session unification queue."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
SESSION = "agent-based-redesign-of-cli-agent-sub-agent-and-workspace-session-isolation-55"
CTX = {"workspace": str(ROOT).replace("\\", "/"), "session": SESSION}


def run_tool(tool: str, arguments: dict | None = None) -> str:
    payload: dict = {
        "toolset": "agent.chat_agent:ChatAgent",
        "context": CTX,
        "tool": tool,
    }
    if arguments:
        payload["arguments"] = arguments
    env = os.environ.copy()
    env["PYTHONPATH"] = ";".join(
        [
            str(ROOT),
            str(ROOT / "primitives"),
            str(ROOT / "utilities"),
            str(ROOT / "context_tools"),
            str(ROOT / "context_tools" / "actions"),
            str(ROOT / "agents"),
        ]
    )
    proc = subprocess.run(
        [sys.executable, "-m", "tools", "run", "-"],
        input=yaml.safe_dump(payload, sort_keys=False),
        text=True,
        capture_output=True,
        cwd=ROOT,
        env=env,
        check=False,
    )
    print(f"=== {tool} ===")
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.stdout


if __name__ == "__main__":
    import sys as _sys

    tool = _sys.argv[1] if len(_sys.argv) > 1 else "run_doer"
    args = {}
    if tool == "run_judge":
        args = {"verdict": _sys.argv[2] if len(_sys.argv) > 2 else "PASS"}
    run_tool(tool, args or None)
