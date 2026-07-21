# @toolset-manifest python -m tools manifest contexts.stories.stories:Stories
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity discovery
# invoke-edit: action satisfy | toolset: contexts.stories.stories:Stories
# invoke-check: action validate | toolset: contexts.stories.stories:Stories
"""Stories generator — multi-fidelity story maps and acceptance tests."""

from __future__ import annotations

import importlib
import json
from typing import Any

from primitives.actions.action import action
from contexts import context
from grill_context import grill_with_context
from primitives.instructions import Instruction
from primitives.instructions import instruction
from sketch import sketch
from tools.tool import tool  # noqa: F401

_FIDELITY_FORMAT_DEFAULTS = {
    "discovery": "markdown",
    "exploration": "python",
    "specification": "python",
    "engineering": "python",
}

# Adapter class path per format — peer channels, same CLI surface.
_CHANNELS: dict[str, tuple[str, str]] = {
    "markdown": ("stories.document.markdown.nodes", "MarkdownStoryMap"),
    "json": ("stories.document.json.nodes", "JsonStoryMap"),
    "drawio": ("stories.diagram.drawio.nodes", "DrawIOStoryMap"),
    "miro": ("stories.diagram.miro.nodes", "MiroStoryMap"),
    "python": ("stories.code.python.python_story_map", "PythonStoryMap"),
    "typescript": ("stories.code.typescript.typescript_story_map", "TypeScriptStoryMap"),
    "java": ("stories.code.java.java_story_map", "JavaStoryMap"),
    "javascript": ("stories.code.javascript.javascript_story_map", "JavaScriptStoryMap"),
}

_SUPPORTED_FORMATS = frozenset(_CHANNELS)
_CODE_FORMATS = frozenset({"python", "typescript", "java", "javascript"})


def _load_channel_class(format_name: str) -> type:
    if format_name not in _CHANNELS:
        raise ValueError(
            f"Unsupported format {format_name!r}. Choose from: {sorted(_CHANNELS)}"
        )
    module_path, attr = _CHANNELS[format_name]
    return getattr(importlib.import_module(module_path), attr)


def _normalize_input(format_name: str, content: Any) -> Any:
    if format_name in _CODE_FORMATS:
        if isinstance(content, dict):
            return content
        if isinstance(content, str):
            return json.loads(content)
        raise TypeError(f"{format_name} transform expects a path→content dict or JSON object")
    if not isinstance(content, str):
        raise TypeError(f"{format_name} transform expects a string")
    return content


@context
class Stories:
    """§ Instructions"""

    def __init__(self, fidelity: str = "discovery", format: str | None = None) -> None:
        if fidelity not in _FIDELITY_FORMAT_DEFAULTS:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        resolved_format = format if format is not None else _FIDELITY_FORMAT_DEFAULTS[fidelity]
        if resolved_format not in _SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format {resolved_format!r}. Choose from: {sorted(_SUPPORTED_FORMATS)}"
            )
        super().__init__(format=resolved_format)
        self.fidelity = fidelity

    @instruction
    def contexts(self) -> Instruction: ...

    @grill_with_context
    @sketch
    @action
    def generate(self) -> str: ...

    @tool
    def transform(self, source_format: str, target_format: str, content: str) -> dict:
        """Parse content from source_format into the canonical StoryMap, then render into target_format.
        All formatters are peer channels. Sideways format move at the same fidelity."""
        source_cls = _load_channel_class(source_format)
        target_cls = _load_channel_class(target_format)
        source = source_cls()
        target = target_cls()
        parsed_input = _normalize_input(source_format, content)
        canonical = source.parse(parsed_input)
        rendered = target.render(canonical)
        return {"format": target_format, "content": rendered}
