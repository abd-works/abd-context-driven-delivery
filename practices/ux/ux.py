"""UX generator - multi-fidelity IA, mockups, specs, and production frontend (front_end_code)."""

from __future__ import annotations

from typing import Any

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class Ux(PracticeGuidance):
    """# Instructions"""

    def __init__(
        self,
        fidelity: str = "ia",
        format: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            fidelity=fidelity,
            default_workspace_folder="ux",
            formats={
                "drawio": ("ux.model.drawio.nodes", "DrawioUxMap"),
                "html": ("ux.model.html.nodes", "HtmlUxMap"),
                "markdown": ("ux.model.markdown.nodes", "MarkdownUxMap"),
                "json": ("ux.model.json.nodes", "JsonUxMap"),
            },
        )

    @agent_tool
    def ensure_javascript(self, generator: str, source_format: str, content: Any) -> dict:
        """Ensure Stories or Clean Engineering JS exists - transform via that generator if needed.
        generator: 'stories' | 'clean_engineering'. Returns {format: javascript, content: ...}."""
        if generator == "stories":
            from practices.stories.stories import Stories

            return Stories().render("javascript", content, source=source_format)
        if generator == "clean_engineering":
            from practices.clean_engineering.clean_engineering import CleanEngineering

            return CleanEngineering().render("javascript", content, source=source_format)
        raise ValueError(
            f"Unsupported generator {generator!r}. Choose from: stories, clean_engineering"
        )
