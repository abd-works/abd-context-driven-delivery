"""UX generator - multi-fidelity IA, mockups, specs, and production frontend (front_end_code)."""

from __future__ import annotations

from typing import Any

from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp

_FORMATS: dict[str, tuple[str, str]] = {
    "drawio": ("ux.model.drawio.nodes", "DrawioUxMap"),
    "html": ("ux.model.html.nodes", "HtmlUxMap"),
    "markdown": ("ux.model.markdown.nodes", "MarkdownUxMap"),
    "json": ("ux.model.json.nodes", "JsonUxMap"),
}

_SUPPORTED_FORMATS = frozenset(_FORMATS)


@agent_toolset
class Ux(PracticeGuidance):
    """# Instructions"""

    domain_slug = "ux"
    default_workspace_folder: str = "ux"
    context_index_key: str = "ux"
    _formats = _FORMATS
    supported_formats = _SUPPORTED_FORMATS

    def __init__(
        self,
        fidelity: str = "ia",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
        stage: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            path=path,
            session=session,
            workspace=workspace,
            fidelity=fidelity,
            stage=stage,
        )

    @property
    @Mcp
    @Skill
    @agent_instructions
    def instructions(self) -> str:
        """UX looks at the product through user navigation and information architecture, from layout and transitions to more formal screens, regions, and controls — how users see and act on the solution — mapped at increasing fidelity."""
        return super().instructions

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
