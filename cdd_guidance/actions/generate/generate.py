"""Generate — run generate on each provided context tool."""

from __future__ import annotations

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp
from validate.validate import Validate

@agent_toolset
class Generate(GuidanceAction):
    """Generate artifacts for provided context tools."""

    @Mcp
    @Skill
    @agent_instructions
    def generate(self, guidance: GuidanceArg) -> str:
        """Write artifacts for each listed guidance at its current fidelity. The shared rules and that fidelity's rules are part of these instructions. After the artifact is written, call validate with the same guidance."""
        self._bind_guidance(guidance)
        rules = self._rules(guidance)
        instructions(rules)
        tools(self._render().render)
        self.run(guidance, self._generate_item, action="generate")
        "After the artifact is written, call validate with this same guidance."
        tools(self._validate().validate)
        return ""

    def _rules(self, guidance: GuidanceArg) -> str:
        """Shared rules and the active fidelity's rules, inlined into generate."""
        return Validate().validate(guidance)

    def _validate(self) -> Validate:
        """Validate as a tool, so its rules are injected again when it is called."""
        action = Validate()
        action.mode = "tool"
        return action

    def _render(self):
        """Render action, available while generating code from another format."""
        from render.render import Render

        return Render()

    def _generate_item(self, item) -> None:
        if isinstance(item, str):
            instructions(item)
            self.generate_output()
        else:
            item.instructions
            item.generate_output()
        self.generate_fixes_from_validate()
        self.add_generate_header_to_generated()

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
