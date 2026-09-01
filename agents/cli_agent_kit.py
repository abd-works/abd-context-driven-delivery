# @toolset-manifest python -m tools manifest agents.cli_agent_kit:CliAgentKit
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""CliAgentKit — slash ``/cli-agent`` calls ``CliAgent.run``."""
from __future__ import annotations

import os
from pathlib import Path

from agents.agent import CliAgent, _CursorCli
from harness.harness_tool import prompt
from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool


@agentic_toolset
class CliAgentKit:
    """Slash ``/cli-agent`` — bind session, enqueue, ``CliAgent.run``."""

    def __init__(self, workspace: str = "", session: str = "") -> None:
        self._workspace = Path((workspace or os.getcwd()).strip())
        self._session_name = (session or "cli-agent").strip()

    @prompt(name="cli-agent")
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
        """Open the session, add tasks, spawn cursor-agent, drain the backlog."""

        name = (session_name or self._session_name).strip()
        engine = CliAgent(_workspace=self._workspace, _cli=_CursorCli())
        engine.open_session(name, goal=goal)
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

    @agent_tool
    def kick(self, session_name: str = "") -> str:
        """Kick the current doer on the live CLI chat (continue, not named resume)."""

        name = (session_name or self._session_name).strip()
        engine = CliAgent(_workspace=self._workspace, _cli=_CursorCli())
        engine.open_session(name)
        if engine.current_task is None:
            return engine.queue_status()
        engine.kick(engine.current_task.doer)
        return engine.queue_status()

    @agent_tool
    def close_agents(self, session_name: str = "") -> str:
        name = (session_name or self._session_name).strip()
        engine = CliAgent(_workspace=self._workspace)
        engine.open_session(name)
        engine.close_agents()
        return "agents closed"

    @agent_tool
    def cleanup(self, session_name: str = "") -> str:
        name = (session_name or self._session_name).strip()
        engine = CliAgent(_workspace=self._workspace)
        engine.open_session(name)
        engine.cleanup()
        return "cleaned"

    @agent_tool
    def close_cli_session(self, session_name: str = "") -> str:
        name = (session_name or self._session_name).strip()
        engine = CliAgent(_workspace=self._workspace)
        engine.open_session(name)
        engine.close_cli_session()
        return "cli session closed"
