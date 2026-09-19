"""UX generator - multi-fidelity IA, mockups, specs, and production frontend (front_end_code)."""

from __future__ import annotations

import importlib
from typing import Any

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp
from agent_tools.agent_tools import agent_tool  # noqa: F401

_FIDELITY_FORMAT_DEFAULTS = {
    "ia": "drawio",
    "mockup": "html",
    "front_end_code": "html",
}

# Peer channels - same CLI surface; transform moves sideways at one fidelity.
_CHANNELS: dict[str, tuple[str, str]] = {
    "drawio": ("ux.diagram.drawio.nodes", "DrawioUxMap"),
    "html": ("ux.web.html.nodes", "HtmlUxMap"),
    "markdown": ("ux.document.markdown.nodes", "MarkdownUxMap"),
    "json": ("ux.document.json.nodes", "JsonUxMap"),
}

_SUPPORTED_FORMATS = frozenset(_CHANNELS)


def _load_channel_class(format_name: str) -> type:
    if format_name not in _CHANNELS:
        raise ValueError(
            f"Unsupported format {format_name!r}. Choose from: {sorted(_CHANNELS)}"
        )
    module_path, attr = _CHANNELS[format_name]
    return getattr(importlib.import_module(module_path), attr)


@agent_toolset
class Ux(PracticeGuidance):
    """# Instructions"""

    domain_slug = "ux"
    default_workspace_folder: str = "ux"
    context_index_key: str = "ux"
    _fidelity_format_defaults = dict(_FIDELITY_FORMAT_DEFAULTS)
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
    def render(self, format: str, content: str, source: str | None = None) -> dict:
        """Parse content into the canonical UxMap, then render into format.
        source defaults to this instance's format. Peer channels at the same fidelity."""
        source_format = source or self.format
        if not source_format:
            raise ValueError("source format is not set")
        source_cls = _load_channel_class(source_format)
        target_cls = _load_channel_class(format)
        return {"format": format, "content": target_cls.render(source_cls.parse(content))}

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
