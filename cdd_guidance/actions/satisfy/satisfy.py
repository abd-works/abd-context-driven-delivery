"""Satisfy — validate then generate fixes on each provided context tool."""

from __future__ import annotations

from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp

_SATISFY_MARKDOWN = Path(__file__).with_name("satisfy.md").read_text(encoding="utf-8")


@agent_toolset
class Satisfy(GuidanceAction):
    """Satisfy artifacts for provided context tools."""

    @Mcp
    @Skill
    @agent_instructions
    def satisfy(self, guidance: GuidanceArg) -> str:
        """Run validate for each listed guidance against the content; apply generate_fixes_from_validate, then validate again when done."""
        from generate.generate import Generate
        from harness.agent_tools.agent_tools import AgentInstructions
        from validate.validate import Validate

        self._bind_guidance(guidance)
        sections: list[str] = [_SATISFY_MARKDOWN.strip()]

        def on(item) -> None:
            validate = Validate()
            if isinstance(item, str):
                sections.append(validate.validate(item))
                fix_guidance: GuidanceArg = item
            else:
                sections.append(validate.validate(guidance=[item]))
                fix_guidance = [item]
            generate = Generate()
            generate._bind_guidance(fix_guidance)
            fix_prose = AgentInstructions.for_callable(
                Generate.generate_fixes_from_validate, generate
            ).expand({}, {}).instructions
            if fix_prose.strip():
                sections.append(fix_prose.strip())

        self.run(guidance, on, action="satisfy")
        sections.append(
            "When every applicable rule passes validate for artifacts under {session.path}/, "
            "reply with a short **Fixes** list: file path and rule slug per change."
        )
        return "\n\n".join(sections)
