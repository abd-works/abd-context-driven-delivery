"""Improvement action: repair a toolset whose expected behaviour failed, then verify the fix by theme."""
from __future__ import annotations

from cdd_guidance.actions.diagnose.diagnose import Diagnose
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, tools
from harness.markdown import markdown
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp

@agent_toolset
class Improvement(GuidanceAction):
    """Slash ``/repair`` runs this action on each listed guidance; it is an action of its own, not an operation of a
    practice."""

    @markdown(label="repair")
    def repair_loop(self) -> str:
        """Deep root-cause recipe — why the toolset's expected behavior failed."""

    @mcp
    @skill
    @agent_instructions
    def repair(self, guidance: GuidanceArg, asset: str = "", violation: str = "") -> str:
        """Open a domain repair on each listed guidance and instruct the fix.
        asset: path to the file under repair. Pass the file. Do not paste its body.
        violation: the rule name, or a path to the violation report. Do not paste the asset."""
        self._work_on(guidance)
        self.repair_loop

        def on(item) -> str:
            if isinstance(item, str):
                return ""
            return "\n\n".join(part.strip() for part in (str(item.examples or ""), item.templates or "") if part.strip())

        self.run(on, action="repair")
        "After the fix is written, call refresh with exactly the files you wrote, so the session's graph holds them as they are now; nothing watches the files."
        if self._session is not None:
            tools(self.graph.refresh)
        tools(self._diagnose().diagnose)
        return (
            "Diagnose why the toolset's expected behavior failed for {{asset}} "
            "(call the diagnose tool with this guidance). State the proposed toolset change "
            "before any test. Do not list tactical file fixes. Then fail-first "
            "at the seam. See repair.md."
        )

    def _diagnose(self) -> Diagnose:
        """The diagnosis the repair starts with, whose diagnose tool the agent calls on what this repair lists."""
        return self._inside(Diagnose)

    @mcp
    @skill
    @agent_tool
    def verify_fix(self, guidance: GuidanceArg, theme: str) -> str:
        """Re-run the regression check for a themed repair bucket on each listed guidance.
        theme: the repair bucket to re-check."""
        self._work_on(guidance)
        return (
            f"Re-check the repair theme {theme}: re-run the fail-first test written for it, then the original scenario "
            "of each mistake tagged with it. Report each as passing or failing; a failing one reopens the theme for "
            "diagnose, as repair.md describes."
        )
