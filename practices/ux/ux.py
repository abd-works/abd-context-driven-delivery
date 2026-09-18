"""UX generator - multi-fidelity IA, mockups, specs, and production frontend (front_end_code)."""

from __future__ import annotations

import importlib
from typing import Any

from practices.stages import DISCOVERY, ENGINEER, SPEC, resolve_stage_fidelity
from practices.workspace_bind import init_practice_guidance
from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance
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

    STAGE_TO_FIDELITY = {
        DISCOVERY: "ia",
        SPEC: "mockup",
        ENGINEER: "front_end_code",
    }

    @classmethod
    def resolve_fidelity(cls, fidelity: str) -> str:
        return resolve_stage_fidelity(fidelity, cls.STAGE_TO_FIDELITY)

    def __init__(
        self,
        fidelity: str = "ia",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        fidelity = type(self).resolve_fidelity(fidelity)
        if fidelity not in _FIDELITY_FORMAT_DEFAULTS:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        resolved_format = format if format is not None else _FIDELITY_FORMAT_DEFAULTS[fidelity]
        if resolved_format not in _SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format {resolved_format!r}. Choose from: {sorted(_SUPPORTED_FORMATS)}"
            )
        init_practice_guidance(
            self,
            format=resolved_format,
            path=path,
            session=session,
            workspace=workspace,
            fidelity=fidelity,
            stage_to_fidelity=self.STAGE_TO_FIDELITY,
        )

    @agent_tool
    def transform(self, source_format: str, target_format: str, content: str) -> dict:
        """Parse content from source_format into the canonical UxMap, then render into target_format.
        Peer channels: drawio, html, markdown, json. Sideways move at the same fidelity."""
        source_cls = _load_channel_class(source_format)
        target_cls = _load_channel_class(target_format)
        canonical = source_cls.parse(content)
        rendered = target_cls.render(canonical)
        return {"format": target_format, "content": rendered}

    @agent_tool
    def render(self, format: str, content: str = "") -> dict:
        """Render already-generated UX output into ``format`` via channel parse/render."""
        if not content:
            raise ValueError("content is required — pass the already-generated artifact")
        source = self.format
        if not source:
            raise ValueError("source format is not set")
        return self.transform(source, format, content)

    @agent_tool
    def ensure_javascript(self, generator: str, source_format: str, content: Any) -> dict:
        """Ensure Stories or Clean Engineering JS exists - transform via that generator if needed.
        generator: 'stories' | 'clean_engineering'. Returns {format: javascript, content: ...}."""
        if generator == "stories":
            from practices.stories.stories import Stories

            return Stories().transform(source_format, "javascript", content)
        if generator == "clean_engineering":
            from practices.clean_engineering.clean_engineering import CleanEngineering

            return CleanEngineering().transform(source_format, "javascript", content)
        raise ValueError(
            f"Unsupported generator {generator!r}. Choose from: stories, clean_engineering"
        )
