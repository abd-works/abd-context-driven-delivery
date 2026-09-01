# @toolset-manifest python -m tools manifest agents.sub_agent_kit:SubAgentKit
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""SubAgentKit — slash ``/sub-agent`` calls ``SubAgent.run``."""
from __future__ import annotations

import os
from pathlib import Path

from agents.agent import SubAgent
from harness.harness_tool import prompt
from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool


def _waiter_prompt(role: str, runtime: Path) -> str:
    incoming = (runtime / f"{role}.in").as_posix()
    outgoing = (runtime / f"{role}.out").as_posix()
    if role == "judge":
        job = "Reply with PASS or FAIL only."
    elif role == "healer":
        job = "Heal as instructed. Write the heal or no heal needed."
    else:
        job = "Do the work. Write only the answer."
    return (
        f"You are the SubAgent {role} waiter for this Cursor chat. "
        f"Stay in a loop until the file {incoming} contains STOP. "
        f"When {incoming} has any other text, {job} "
        f"Write the result to {outgoing}, then clear {incoming}. "
        "Sleep briefly and poll again. Do not exit the loop. "
        "Do not wait for the parent chat to send another Task."
    )


def _runtime_job(workspace: Path, session_name: str) -> str:
    runtime = workspace / ".agent_sessions" / session_name / "runtime"
    enabled = (runtime / "enabled").as_posix()
    return (
        "Runtime job — once in this chat, then the parent is done:\n"
        "1. Spawn a Task sub-agent (generalPurpose) as the DOER waiter:\n\n"
        f"{_waiter_prompt('doer', runtime)}\n\n"
        "2. Spawn a Task sub-agent (generalPurpose) as the JUDGE waiter:\n\n"
        f"{_waiter_prompt('judge', runtime)}\n\n"
        "3. Spawn a Task sub-agent (generalPurpose) as the HEALER waiter:\n\n"
        f"{_waiter_prompt('healer', runtime)}\n\n"
        f"4. Create empty file {enabled}\n"
        "5. Call tool run with session_name and the tasks (or again with no new tasks). "
        "SubAgent.run feeds those three chats. Do not hop run per item."
    )


@agentic_toolset
class SubAgentKit:
    """Slash ``/sub-agent`` — bind session, enqueue, ``SubAgent.run``."""

    def __init__(self, workspace: str = "", session: str = "") -> None:
        self._workspace = Path((workspace or os.getcwd()).strip())
        self._session_name = (session or "sub-agent").strip()

    @prompt(name="sub-agent")
    @agent_instructions
    @agent_tool
    def run(
        self,
        session_name: str = "",
        goal: str = "",
        doer_prompt: str = "",
        judge_prompt: str = "",
        tasks: list[dict] | None = None,
    ) -> str:
        """Spawn doer/judge/healer waiters, create runtime/enabled, then this tool: add_tasks and run_backlog."""

        name = (session_name or self._session_name).strip()
        engine = SubAgent.load(self._workspace, name)
        if engine is None:
            engine = SubAgent(_workspace=self._workspace)
            engine.open_session(name, goal=goal)
        elif goal and engine.session is not None:
            engine.session.goal = goal
        specs = list(tasks or [])
        if doer_prompt.strip():
            specs.append(
                {
                    "doer_prompt": doer_prompt.strip(),
                    "judge_prompt": judge_prompt.strip(),
                }
            )
        if specs and engine.current_task is None:
            engine.add_tasks_from_specs(specs)
        return engine.run()
