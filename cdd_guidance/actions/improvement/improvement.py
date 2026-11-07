"""Improvement action: repair a toolset whose expected behaviour failed, then verify the fix by theme."""
from __future__ import annotations

import inspect
from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.markdown import markdown
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp

@agent_toolset
class Improvement(GuidanceAction):
    """Slash ``/repair`` runs this action on each listed guidance; it is an action of its own, not an operation of a
    practice."""

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
    def repair(self, guidance: GuidanceArg, asset: str = "", violation: str = "") -> str:
        """Open a domain repair on each listed guidance and instruct the fix.
        asset: path to the file under repair. Pass the file. Do not paste its body.
        violation: the rule name, or a path to the violation report. Do not paste the asset."""
        self._bind_guidance(guidance)
        self.repair_loop

        def on(item) -> None:
            if isinstance(item, str):
                return
            item.examples
            item.templates

        self.run(on, action="repair")
        return (
            "Diagnose why the toolset's expected behavior failed for {{asset}} "
            "(run cdd_guidance.actions.diagnose.diagnose:Diagnose). State the proposed toolset change "
            "before any test. Do not list tactical file fixes. Then fail-first "
            "at the seam. See repair.md."
        )

    @Mcp
    @Skill
    @agent_tool
    def verify_fix(self, guidance: GuidanceArg, theme: str) -> str:
        """Re-run the regression check for a themed repair bucket on each listed guidance.
        theme: the repair bucket to re-check."""
        self._bind_guidance(guidance)
        return (
            f"Re-check the repair theme {theme}: re-run the fail-first test written for it, then the original scenario "
            "of each mistake tagged with it. Report each as passing or failing; a failing one reopens the theme for "
            "diagnose, as repair.md describes."
        )
