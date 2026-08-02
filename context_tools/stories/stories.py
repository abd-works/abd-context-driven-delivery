# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity discovery
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories
"""Stories generator - multi-fidelity story maps and acceptance tests."""

from __future__ import annotations

import importlib
import json
from typing import TYPE_CHECKING, Any

from context_tools.base.base_context_tool import BaseContextTool
from primitives.actions.action import action
from primitives.instructions import Instruction
from primitives.instructions import instruction
from primitives.tools.tool import tool  # noqa: F401

if TYPE_CHECKING:
    from utilities.diagnose.diagnose import Diagnose

_FIDELITY_FORMAT_DEFAULTS = {
    "discovery": "markdown",
    "exploration": "python",
    "engineering": "python",
}

# Adapter class path per format - peer channels, same CLI surface.
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
        raise TypeError(f"{format_name} transform expects a path->content dict or JSON object")
    if not isinstance(content, str):
        raise TypeError(f"{format_name} transform expects a string")
    return content


class Stories(BaseContextTool):
    """# Instructions"""

    default_workspace_folder: str = "tests"
    context_index_key: str = "stories"

    def __init__(
        self,
        fidelity: str = "discovery",
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

    def diagnostic(self) -> "Diagnose":
        """Diagnose companion — common six-phase loop as a tool (not inlined)."""
        # lazy import: keeps diagnose optional at module load
        from utilities.diagnose.diagnose import Diagnose

        return Diagnose()

    @instruction
    def contexts(self) -> Instruction: ...

    @action
    def iterate(self) -> str:
        """Iterate then generate - grill + formal generate/validate/one-fix ticks.
        If the same acceptance scenario is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (tier wiring, stale Story constant, vocabulary drift, or transform that fixed the map while the leaf still fails)."""
        super().iterate()
        self.diagnostic().diagnose()
        return "Iterate complete; generate instructions applied."

    @action
    def satisfy(self) -> str:
        """Find and fix every problem in the story artifacts under the session root.
        If the same acceptance scenario is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (tier wiring, stale Story constant, vocabulary drift, or transform that fixed the map while the leaf still fails)."""
        super().satisfy()
        self.diagnostic().diagnose()
        return "When done, run validate on artifacts under {session.path}/."

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
