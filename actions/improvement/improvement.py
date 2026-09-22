"""Improvement kit — repair / verify_fix for context tools (peer kit, not on Guidance)."""
from __future__ import annotations

import inspect
from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.markdown import markdown
from harness.agent_tools.agent_tools import agent_tool
from installation.files import Skill
from harness.mcp.mcp_server import Mcp

@agent_toolset
class Improvement(GuidanceAction):
    """Slash ``/repair`` runs this kit with ``arguments.guidance``; not composed on Guidance."""

    @property
    def module_dir(self) -> Path:
        """Directory of this module — used by @markdown extract."""
        return Path(inspect.getfile(type(self))).resolve().parent

    @markdown(label="repair")
    def repair_loop(self) -> str:
        """Deep root-cause recipe — why the toolset's expected behavior failed."""

    @Mcp
    @Skill
    @agent_instructions
    def repair(self, guidance: GuidanceArg, asset: str, violation: str) -> str:
        """Open a domain repair on each passed Guidance and instruct the fix. Pass a string to repair that text once."""
        self.repair_loop

        def on(item) -> None:
            if isinstance(item, str):
                return
            current = self._session()
            if current is None:
                raise ValueError("No current work session — open failed")
            repair = current.repairs.for_violation(asset, violation)
            repair.open(item, asset, violation)
            item.contexts
            item.examples
            item.templates

        self.run(guidance, on, action="repair")
        return (
            "Diagnose why the toolset's expected behavior failed for {{asset}} "
            "(run diagnose.diagnose:Diagnose). State the proposed kit change "
            "before any test. Do not list tactical file fixes. Then fail-first "
            "at the seam. See repair.md."
        )

    @Mcp
    @Skill
    @agent_tool
    def verify_fix(self, guidance: GuidanceArg, theme: str) -> str:
        """Re-run the regression check for a themed repair bucket on each listed Guidance. Open the work session first. Pass a string to verify that text once."""
        def on(item) -> str:
            current = self.workspace.current_work_session
            if current is None:
                raise ValueError("No current work session — open first")
            return current.repairs[theme].verify_fix()

        self._bind_guidance(guidance)
        lines = [line for line in self.each(on) if line]
        return "\n".join(lines) if lines else f"verify_fix theme={theme}"
