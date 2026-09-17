"""Fixture hosts — co-located markdown beside this module."""
from __future__ import annotations

from primitives.guidance.guidance import Guidance, PracticeGuidance
from primitives.agent_tools.agent_tools import agent_instructions
from primitives.harness.marks import mcp, skill
from primitives.markdown import HTML, Markdown, markdown


class SampleToolHost:
    domain_slug = "sample_tool"
    toolset_name = "sample_tool"
    name = None

    @markdown
    def guidance(self) -> str:
        """Guidance section body."""

    def read_guidance_as_html(self) -> HTML:
        return Markdown.from_label(self, "guidance").html()


class SampleGuidance(Guidance):
    domain_slug = "sample_tool"
    default_format = "markdown"
    name = None


class SampleMcpGuidance(SampleGuidance):
    @markdown
    @mcp
    @skill
    @agent_instructions
    def guidance(recipe) -> str:
        """Guidance section body."""


class SamplePracticeGuidance(PracticeGuidance):
    domain_slug = "sample_tool"
    default_format = "markdown"
    name = None


class SamplePracticeWithFidelities(SamplePracticeGuidance):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.load_fidelities_from_markdown()


class SampleMcpPractice(SamplePracticeWithFidelities):
    @markdown
    @mcp
    @skill
    @agent_instructions
    def guidance(recipe) -> str:
        """Guidance section body."""
