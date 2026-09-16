"""Layer 1 fixture host — co-located markdown beside this module."""
from __future__ import annotations

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
