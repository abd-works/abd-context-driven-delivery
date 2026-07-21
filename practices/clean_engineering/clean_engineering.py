# @toolset-manifest python -m tools manifest clean_engineering.clean_engineering:CleanEngineering
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity language
# @toolset-manifest python -m tools manifest bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: bdd.bdd:Bdd
# invoke-check: action validate | toolset: bdd.bdd:Bdd
"""Clean Engineering generator — multi-fidelity OO design and implementation."""

from __future__ import annotations

from action.action import action
from focus import focus
from generator import generator
from grill_context import grill_with_context
from clean_engineering.class_model.drawio_class_model import DrawIOCleanEngineeringModel
from clean_engineering.class_model.java_class_model import JavaCleanEngineeringModel
from clean_engineering.class_model.javascript_class_model import JavaScriptCleanEngineeringModel
from clean_engineering.class_model.json_class_model import JsonCleanEngineeringModel
from clean_engineering.class_model.markdown_class_model import MarkdownCleanEngineeringModel
from clean_engineering.class_model.python_class_model import PythonCleanEngineeringModel
from clean_engineering.class_model.typescript_class_model import TypeScriptCleanEngineeringModel
from primitives.instruction import Instruction
from primitives.instruction_slot import instruction
from sketch import sketch
from echo import echo
from tools.tool import resource, tool  # noqa: F401

_FIDELITY_FORMAT_DEFAULTS = {
    "language": "markdown",
    "modules": "python",
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


@generator
class CleanEngineering:
    """§ Instructions"""

    def __init__(self, fidelity: str = "language", format: str | None = None) -> None:
        
        resolved_format = format if format is not None else _FIDELITY_FORMAT_DEFAULTS[fidelity]
        super().__init__(format=resolved_format)
        self.fidelity = fidelity

    # Test: consolidated concepts.md instead of fidelities/{fidelity}/concepts.md
    # @focus(focus="fidelities")
    @instruction
    def concepts(self) -> Instruction: ...

    @grill_with_context
    @sketch
    # @focus(focus="fidelities")
    @action
    def generate(self) -> str: ...

    @tool
    def transform(self, source_format: str, target_format: str, content: str) -> dict:
        """Parse content from source_format into the canonical model, then render into target_format.
        Supported transform channels: markdown, json, python, typescript, java, javascript, drawio.
        Generate/validate AI surfaces exist only for markdown and python.
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
