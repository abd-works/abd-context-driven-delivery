"""Fixtures — co-located markdown beside this module."""
from __future__ import annotations

from harness.guidance.guidance import Guidance, PracticeGuidance
from harness.agent_tools.agent_tools import agent_instructions
from installation.harness_files.harness_files import skill
from installation.mcp.mcp_server import mcp
from harness.markdown import HTML, Markdown, markdown


class SampleTool:
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
    @property
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        return super().instructions


class SamplePracticeGuidance(PracticeGuidance):
    domain_slug = "sample_tool"
    default_format = "markdown"
    name = None


class SamplePracticeWithFidelities(SamplePracticeGuidance):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.load_fidelities_from_markdown()


class SampleMcpPractice(SamplePracticeWithFidelities):
    @property
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        return super().instructions
