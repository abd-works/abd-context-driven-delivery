# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity modules
# invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
# invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
"""Clean Engineering generator - multi-fidelity OO design and implementation."""

from __future__ import annotations

from focus import focus
from context_tools.base.base_context_tool import BaseContextTool
from context_tools.clean_engineering.class_model.drawio.drawio import Drawio
from context_tools.clean_engineering.class_model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from context_tools.clean_engineering.class_model.java_class_model import JavaCleanEngineeringModel
from context_tools.clean_engineering.class_model.javascript_class_model import JavaScriptCleanEngineeringModel
from context_tools.clean_engineering.class_model.json_class_model import JsonCleanEngineeringModel
from context_tools.clean_engineering.class_model.markdown_class_model import MarkdownCleanEngineeringModel
from context_tools.clean_engineering.class_model.python_class_model import PythonCleanEngineeringModel
from context_tools.clean_engineering.class_model.typescript_class_model import TypeScriptCleanEngineeringModel
from primitives.actions.action import agent_instructions
from primitives.instructions import Instruction
from primitives.instructions import instruction
from tools.tool import resource, agent_tool  # noqa: F401

_FIDELITY_FORMAT_DEFAULTS = {
    "modules": "markdown",
    "model": "python",
    "specification": "python",
    "code": "python",
}

# Each entry: channel class with .parse(text) -> CleanEngineeringModel and .render(model) -> str
_CHANNELS: dict[str, type] = {
    "markdown": MarkdownCleanEngineeringModel,
    "json": JsonCleanEngineeringModel,
    "python": PythonCleanEngineeringModel,
    "typescript": TypeScriptCleanEngineeringModel,
    "java": JavaCleanEngineeringModel,
    "javascript": JavaScriptCleanEngineeringModel,
    "drawio": DrawIOCleanEngineeringModel,
}

_SUPPORTED_FORMATS = frozenset(_CHANNELS)


class CleanEngineering(BaseContextTool):
    """# Instructions"""

    default_workspace_folder: str = "src"
    context_index_key: str = "clean_engineering"
    _fidelity_format_defaults = dict(_FIDELITY_FORMAT_DEFAULTS)
    supported_formats = _SUPPORTED_FORMATS


    fidelities = {
        BaseContextTool.DISCOVERY: "modules",
        BaseContextTool.SPEC:      "model",
        BaseContextTool.ENGINEER:  "code",
    }

    def __init__(
        self,
        fidelity: str = "modules",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        if fidelity == "language":
            raise ValueError(
                "language is not a fidelity - it is a companion prose layer refined at "
                "every stage. Use fidelity 'modules' (after partition), then 'model', "
                f"'specification', or 'code'. Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        fidelity = type(self).resolve_fidelity(fidelity)
        if fidelity not in _FIDELITY_FORMAT_DEFAULTS:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        resolved_format = format if format is not None else _FIDELITY_FORMAT_DEFAULTS[fidelity]
        super().__init__(
            format=resolved_format, path=path, session=session, workspace=workspace
        )
        self.fidelity = fidelity
        self.drawio = Drawio(workspace=self.workspace)

    # Resolves to # Contexts in clean_engineering.md (fidelities + design vocabulary).
    @instruction
    def contexts(self) -> Instruction: ...

    @agent_instructions
    def guidance(self) -> str:
        """Provide guidance for creating OO modules, models, and code."""
        return super().guidance()

    @agent_instructions
    def generate_output(self) -> str:
        """Write the fidelity artifact under the session.

        When ``format`` is ``drawio``, call ``drawio.render`` (create diagram →
        scan layout rules in drawio contexts → repair sub-agent on definitive
        layout failures). Otherwise produce the active channel output
        (markdown / python / …) from contexts, examples, and templates — do
        not invoke drawio.render.
        """
        self.drawio.mode = "tool"
        self.drawio.render()
        return "Artifact written under {session.path}/."

    @agent_tool
    def transform(
        self,
        source_format: str,
        target_format: str,
        content: str,
        previous: str = "",
        keep_positioning: bool = False,
    ) -> dict:
        """Parse content from source_format into the canonical model, then render into target_format.
        Supported transform channels: markdown, json, python, typescript, java, javascript, drawio.
        drawio auto-selects modules view (system-context style) vs UML class view from model content.
        When target_format is drawio and keep_positioning is true, pass previous Draw.io XML
        (or leave previous empty and use drawio.render / create_diagram with a path) so existing
        class positions and relationship routing are kept; only new classes/edges are laid out.
        For a persisted class diagram with layout scan/repair, use ``drawio.render`` (via generate when format is drawio) instead of transform alone.
        Moves content sideways between formats at the same fidelity - no analytical upgrade."""
        if source_format not in _CHANNELS:
            raise ValueError(
                f"Unsupported source_format {source_format!r}. Choose from: {sorted(_CHANNELS)}"
            )
        if target_format not in _CHANNELS:
            raise ValueError(
                f"Unsupported target_format {target_format!r}. Choose from: {sorted(_CHANNELS)}"
            )
        canonical = _CHANNELS[source_format].parse(content)
        if target_format == "drawio":
            rendered = _CHANNELS[target_format].render(
                canonical,
                previous=previous or None,
                keep_positioning=keep_positioning,
            )
        else:
            rendered = _CHANNELS[target_format].render(canonical)
        return {"format": target_format, "content": rendered}

    @agent_tool
    def render(
        self,
        format: str,
        content: str = "",
        previous: str = "",
        keep_positioning: bool = False,
    ) -> dict:
        """Render already-generated output into ``format`` via channel parse/render."""
        if not content:
            raise ValueError("content is required — pass the already-generated artifact")
        source = self.format
        if not source:
            raise ValueError("source format is not set")
        return self.transform(
            source,
            format,
            content,
            previous=previous,
            keep_positioning=keep_positioning,
        )
