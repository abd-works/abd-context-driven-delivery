# @toolset-manifest python -m tools manifest improvement.improvement:Improvement
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Improvement kit — repair / verify_fix for context tools (peer kit, not on host)."""
from __future__ import annotations

import inspect
from pathlib import Path

from harness.harness_tool import prompt
from lifecycle import LifecycleAction
from primitives.actions.action import agent_instructions, agentic_toolset
from primitives.instructions import Instruction, instruction
from tools.tool import agent_tool
from workspace import SessionLog


@agentic_toolset
class Improvement(LifecycleAction):
    """Slash ``/repair`` runs this kit with ``arguments.tools``; not composed on the host."""

    @property
    def module_dir(self) -> Path:
        """Directory of this module — used by @instruction slots to locate markdown files."""
        return Path(inspect.getfile(type(self))).resolve().parent

    @instruction(label="repair")
    def repair_loop(self) -> Instruction:
        """Deep root-cause recipe — why the toolset's expected behavior failed."""
        ...

    @prompt(name="repair")
    @agent_instructions
    def repair(self, tools: list, asset: str, violation: str) -> str:
        """Open a domain repair on each passed context tool and instruct the fix."""
        self.repair_loop
        self.begin(tools, action="repair")
        for host in self.context_tools(tools):
            current = self._session()
            if current is None:
                raise ValueError("No current work session — open failed")
            repair = current.repairs.for_violation(asset, violation)
            repair.open(host, asset, violation)
            host.contexts
            host.examples
            host.templates
            SessionLog.instance().append(
                toolset=type(self).manifest_path,
                name="repair",
                summary=f"repair {asset}",
                ok=True,
                role="run",
            )
        self.end()
        return (
            "Diagnose why the toolset's expected behavior failed for {{asset}} "
            "(run diagnose.diagnose:Diagnose). State the proposed kit change "
            "before any test. Do not list tactical file fixes. Then fail-first "
            "at the seam. See repair.md."
        )

    @agent_tool
    def verify_fix(self, tools: list, theme: str) -> str:
        """verify_fix — regression check on a themed repair bucket."""
        lines: list[str] = []
        for host in self.context_tools(tools):
            current = self.workspace.current_work_session
            if current is None:
                raise ValueError("No current work session — open first")
            lines.append(current.repairs[theme].verify_fix())
        return "\n".join(lines) if lines else f"verify_fix theme={theme}"
