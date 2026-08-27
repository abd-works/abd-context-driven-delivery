# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity discovery
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories
"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

import importlib
import json
from typing import TYPE_CHECKING, Any

from context_tools.base.base_context_tool import BaseContextTool
from primitives.actions.action import agent_instructions
from primitives.instructions import Instruction
from primitives.instructions import instruction
from primitives.tools.tool import agent_tool  # noqa: F401

if TYPE_CHECKING:
    from utilities.diagnose.diagnose import Diagnose

_FIDELITY_FORMAT_DEFAULTS = {
    "scaffold": "markdown",
    "story_map": "markdown",
    "scenarios": "typescript",
    "acceptance_tests": "typescript",
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
    _fidelity_format_defaults = _FIDELITY_FORMAT_DEFAULTS
    supported_formats = _SUPPORTED_FORMATS


    fidelities = {
        BaseContextTool.SHAPING:   "scaffold",
        BaseContextTool.DISCOVERY: "story_map",
        BaseContextTool.SPEC:      "scenarios",
        BaseContextTool.ENGINEER:  "acceptance_tests",
    }

    def __init__(
        self,
        fidelity: str = "story_map",
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
        super().__init__(
            format=resolved_format, path=path, session=session, workspace=workspace
        )
        self.fidelity = fidelity

    def diagnostic(self) -> "Diagnose":
        """Diagnose companion — common six-phase loop as a tool (not inlined)."""
        # lazy import: keeps diagnose optional at module load
        from utilities.diagnose.diagnose import Diagnose

        return Diagnose()

    def ce(self) -> "BaseContextTool":
        """CleanEngineering companion at code fidelity — used at acceptance_tests fidelity
        to generate or update matching production class implementations after writing specs.
        Invoke as a tool (not inlined into stories guidance). Passes this Stories instance's
        own format through to CleanEngineering when CE recognizes it as a code channel
        (typescript, java, javascript, python) - e.g. format="typescript" here means the
        companion writes TypeScript, not CE's unrelated Python default."""
        from context_tools.clean_engineering.clean_engineering import CleanEngineering

        ce_format = self.format if self.format in _CODE_FORMATS else None
        instance = CleanEngineering(
            fidelity="code",
            format=ce_format,
            path=self._raw_path,
            session=(
                self.workspace.current_work_session.name
                if self.workspace.current_work_session
                else ""
            ),
            workspace=self.workspace.path,
        )
        instance.mode = "tool"
        return instance

    @instruction
    def contexts(self) -> Instruction: ...

    @agent_instructions
    def guidance(self) -> str:
        """Provide guidance for creating story maps, scenarios, and acceptance tests.
        At scaffold fidelity: write epic, sub-epic, and story names only.
        At story_map fidelity: write the story map and thin-slice only.
        At scenarios fidelity: write main-flow scenarios (single or multiple per story) with optional variations; fixtures live in examples/ and givens.ts at the lowest shared epic/sub-epic/story folder.
        At acceptance_tests fidelity: write tests/{epic}/{sub-epic}/{story}.{tier}.ts (one GWT file per story per seam, no story folder). When those files are written, call guidance on the CE companion and pass that companion to this action as a separate tools run so wrap classes under domain/ stay in sync.
        If the same acceptance scenario is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (tier wiring, stale Story constant, vocabulary drift, or transform that fixed the map while the leaf still fails).
        When this Stories work is done, call guidance on the Clean Engineering companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline."""
        super().guidance()
        self.ce().guidance()
        return (
            "When this Stories work is done, call guidance on the Clean Engineering companion "
            "and pass that companion to this action as a separate tools run. "
            "The action already knows what to do for every tool. Do not inline."
        )

    @agent_tool
    def transform(self, source_format: str, target_format: str, content: str) -> dict:
        """Parse content from source_format into the canonical StoryMap, then render into target_format.
        All formatters are peer channels. Sideways format move at the same fidelity.
        At acceptance_tests fidelity: after transforming story artifacts, call ce().transform() or call guidance on the CE companion and pass that companion to this action as a separate tools run."""
        source_cls = _load_channel_class(source_format)
        target_cls = _load_channel_class(target_format)
        source = source_cls()
        target = target_cls()
        parsed_input = _normalize_input(source_format, content)
        canonical = source.parse(parsed_input)
        rendered = target.render(canonical)
        return {"format": target_format, "content": rendered}

    @agent_tool
    def render(self, format: str, content: str = "") -> dict:
        """Render already-generated story output into ``format`` via channel parse/render."""
        if not content:
            raise ValueError("content is required — pass the already-generated artifact")
        source = self.format
        if not source:
            raise ValueError("source format is not set")
        return self.transform(source, format, content)
