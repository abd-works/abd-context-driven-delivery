"""Isolation fixture — same label, this module's markdown only."""
from __future__ import annotations

from harness.markdown import markdown


class OtherTool:
    domain_slug = "other_tool"
    toolset_name = "other_tool"
    name = None

    @markdown
    def guidance(self) -> str:
        """Guidance section body."""
