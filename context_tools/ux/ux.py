# @toolset-manifest python -m tools manifest context_tools.ux.ux:Ux
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity ia
# invoke-edit: action satisfy | toolset: context_tools.ux.ux:Ux
# invoke-check: action validate | toolset: context_tools.ux.ux:Ux
"""UX generator - multi-fidelity IA, mockups, specs, and production frontend (code)."""

from __future__ import annotations

import importlib
from typing import Any

from context_tools.base.base_context_tool import BaseContextTool
from primitives.instructions import Instruction
from primitives.instructions import instruction
from tools.tool import tool  # noqa: F401

_FIDELITY_FORMAT_DEFAULTS = {
    "ia": "drawio",
    "mockup": "html",
    "code": "html",
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


class Ux(BaseContextTool):
    """# Instructions"""

    default_workspace_folder: str = "ux"
    context_index_key: str = "ux"

    def __init__(
        self,
        fidelity: str = "ia",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        if fidelity not in _FIDELITY_FORMAT_DEFAULTS:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        resolved_format = format if format is not None else _FIDELITY_FORMAT_DEFAULTS[fidelity]
        if resolved_format not in _SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format {resolved_format!r}. Choose from: {sorted(_SUPPORTED_FORMATS)}"
            )
        super().__init__(
            format=resolved_format, path=path, session=session, workspace=workspace
        )
        self.fidelity = fidelity

    @instruction
    def contexts(self) -> Instruction: ...

    @tool
    def transform(self, source_format: str, target_format: str, content: str) -> dict:
        """Parse content from source_format into the canonical UxMap, then render into target_format.
        Peer channels: drawio, html, markdown, json. Sideways move at the same fidelity."""
        source_cls = _load_channel_class(source_format)
        target_cls = _load_channel_class(target_format)
        canonical = source_cls.parse(content)
        rendered = target_cls.render(canonical)
        return {"format": target_format, "content": rendered}

    @tool
    def ensure_javascript(self, generator: str, source_format: str, content: Any) -> dict:
        """Ensure Stories or Clean Engineering JS exists - transform via that generator if needed.
        generator: 'stories' | 'clean_engineering'. Returns {format: javascript, content: ...}."""
        if generator == "stories":
            from context_tools.stories.stories import Stories

            return Stories().transform(source_format, "javascript", content)
        if generator == "clean_engineering":
            from context_tools.clean_engineering.clean_engineering import CleanEngineering

            return CleanEngineering().transform(source_format, "javascript", content)
        raise ValueError(
            f"Unsupported generator {generator!r}. Choose from: stories, clean_engineering"
        )
