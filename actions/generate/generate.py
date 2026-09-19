"""Generate — run generate on each provided context tool."""

from __future__ import annotations

from guidance_actions import GuidanceArg, GuidanceAction
from agent_tools import agent_instructions, agent_toolset, instructions
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp
from workspace import SessionLog
@agent_toolset
class Generate(GuidanceAction):
    """Generate artifacts for provided context tools."""

    @Mcp
    @Skill
    @agent_instructions
    def generate(self, guidance: GuidanceArg) -> str:
        """Write artifacts for each listed Guidance host at its current fidelity. Opens the work session, generates each host's output, applies validate-driven fixes, then closes the turn. When finished, run validate. Pass a string to generate from that text once."""
        self.run(guidance, self._generate_item, action="generate")
        return "When done, run validate."

    def _generate_item(self, item) -> None:
        if isinstance(item, str):
            instructions(item)
            self.generate_output()
        else:
            item.instructions
            item.generate_output()
        self.generate_fixes_from_validate()
        self.add_generate_header_to_generated()
        if not isinstance(item, str):
            SessionLog.instance().append(
                toolset=item.registration_name,
                name="generate",
                summary="generate",
                ok=True,
                role="run",
            )

    @agent_instructions
    def add_generate_header_to_generated(self) -> str:
        """Prepend the following block verbatim as the very first lines of the file you are writing - before any imports, before any code."""
        return (
            '"""\n'
            '"""\n'
        )

    @agent_instructions
    def generate_output(self) -> str:
        """Write this context tool's artifact for the current fidelity. Override on the practice; the default writes nothing."""
        return ""

    @agent_instructions
    def generate_fixes_from_validate(self) -> str:
        """Apply fixes implied by the latest validate report before considering generate done. Override on the practice when generate must close those gaps in the same pass."""
        return ""
