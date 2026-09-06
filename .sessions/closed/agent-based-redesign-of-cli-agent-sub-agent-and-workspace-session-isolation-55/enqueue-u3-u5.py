"""One-shot: enqueue U3, U4, U5 judged jobs on ChatAgent backlog."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
SESSION = "agent-based-redesign-of-cli-agent-sub-agent-and-workspace-session-isolation-55"
CTX = {
    "workspace": str(ROOT).replace("\\", "/"),
    "session": SESSION,
}

JOBS = [
    (
        "U3",
        """Run /sub-agent with Bdd and CleanEngineering tools and Generate action.

Migration U3: base_context_tool.py opens agent.agent.Workspace + AgentSession. Remove workspace.workspace WorkSession import. Canonical: agents/.context/agent-session-redesign-sketch.md. Vanilla BDD first; green base_context_tool_spec. Finish the Turn. Do not contact the judge or edit the job queue.""",
        "PASS only when: (1) BaseContextTool uses agent.agent.Workspace.open -> AgentSession; (2) WorkSession import gone; (3) mamba context_tools/base/base_context_tool_spec.py green; (4) judge ran validate with Bdd + CleanEngineering.",
    ),
    (
        "U4",
        """Run /sub-agent with Bdd and CleanEngineering tools and Generate action.

Migration U4: SessionLog and tools run coalesce/bind to AgentSession (name, folder, turn). Judge validate shares session with agent BDD. Touch utilities/workspace/session_log.py and primitives/tools/tool.py only. Canonical: agents/.context/agent-session-redesign-sketch.md. Finish the Turn. Do not contact the judge or edit the job queue.""",
        "PASS only when: (1) SessionLog and tools run bind AgentSession; (2) validate kit on agents passes; (3) judge ran validate with Bdd + CleanEngineering.",
    ),
    (
        "U5",
        """Run /sub-agent with Bdd and CleanEngineering tools and Generate action.

Migration U5: CliAgent queue/model/bindings use AgentSession.folder (.agent_sessions/{name}/), not WorkSession paths. Touch utilities/_internal_cli/cli_agent.py and cli_agent_spec. Canonical: agents/.context/agent-session-redesign-sketch.md. Finish the Turn. Do not contact the judge or edit the job queue.""",
        "PASS only when: (1) CliAgent session artifacts under AgentSession.folder; (2) mamba utilities/_internal_cli/cli_agent_spec.py green; (3) judge ran validate with Bdd + CleanEngineering.",
    ),
]


def run_tool(tool: str, arguments: dict | None = None) -> str:
    payload: dict = {
        "toolset": "agent.chat_agent:ChatAgent",
        "context": CTX,
        "tool": tool,
    }
    if arguments:
        payload["arguments"] = arguments
    yaml_text = yaml.safe_dump(payload, sort_keys=False)
    print(f"=== {tool} ===")
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
        input=yaml_text,
        text=True,
        capture_output=True,
        cwd=ROOT,
        env=env,
        check=False,
    )
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.stdout


def main() -> None:
    run_tool("open_session", {"name": SESSION, "goal": "Session unification U3-U5"})
    for _label, doer, judge in JOBS:
        run_tool(
            "add_tasks",
            {"doer_prompt": doer, "judge_prompt": judge},
        )
    state_path = ROOT / ".agent_sessions" / SESSION / "chat-agent-state.json"
    print("=== chat-agent-state.json ===")
    print(state_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
