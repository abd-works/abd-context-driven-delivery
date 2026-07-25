# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity modules
# invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
# invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
"""Clean Engineering generator — multi-fidelity OO design and implementation."""

from __future__ import annotations

from focus import focus
from context_tools import context_tool
from context_tools.clean_engineering.class_model.drawio_class_model import DrawIOCleanEngineeringModel
from context_tools.clean_engineering.class_model.java_class_model import JavaCleanEngineeringModel
from context_tools.clean_engineering.class_model.javascript_class_model import JavaScriptCleanEngineeringModel
from context_tools.clean_engineering.class_model.json_class_model import JsonCleanEngineeringModel
from context_tools.clean_engineering.class_model.markdown_class_model import MarkdownCleanEngineeringModel
from context_tools.clean_engineering.class_model.python_class_model import PythonCleanEngineeringModel
from context_tools.clean_engineering.class_model.typescript_class_model import TypeScriptCleanEngineeringModel
from primitives.instructions import Instruction
from primitives.instructions import instruction
from echo import echo
from tools.tool import resource, tool  # noqa: F401

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


@context_tool
class CleanEngineering:
    """§ Instructions"""

    default_workspace_folder: str = "src"
    context_index_key: str = "clean_engineering"

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
                "language is not a fidelity — it is a companion prose layer refined at "
                "every stage. Use fidelity 'modules' (after partition), then 'model', "
                f"'specification', or 'code'. Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        if fidelity not in _FIDELITY_FORMAT_DEFAULTS:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        resolved_format = format if format is not None else _FIDELITY_FORMAT_DEFAULTS[fidelity]
        super().__init__(
            format=resolved_format, path=path, session=session, workspace=workspace
        )
        self.fidelity = fidelity

    # Resolves to § Contexts in clean_engineering.md (fidelities + design vocabulary).
    @instruction
    def contexts(self) -> Instruction: ...

    @tool
    def transform(self, source_format: str, target_format: str, content: str) -> dict:
        """Parse content from source_format into the canonical model, then render into target_format.
        Supported transform channels: markdown, json, python, typescript, java, javascript, drawio.
        drawio auto-selects modules view (system-context style) vs UML class view from model content.
        Generate AI surfaces: markdown / python / javascript templates under templates/;
        modules.drawio for modules-fidelity diagrams (seam bullets + dependency arrows).
        Moves content sideways between formats at the same fidelity — no analytical upgrade."""
        if source_format not in _CHANNELS:
            raise ValueError(
                f"Unsupported source_format {source_format!r}. Choose from: {sorted(_CHANNELS)}"
            )
        if target_format not in _CHANNELS:
            raise ValueError(
                f"Unsupported target_format {target_format!r}. Choose from: {sorted(_CHANNELS)}"
            )
        canonical = _CHANNELS[source_format].parse(content)
        rendered = _CHANNELS[target_format].render(canonical)
        return {"format": target_format, "content": rendered}
