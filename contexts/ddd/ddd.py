# @toolset-manifest python -m tools manifest contexts.ddd.ddd:Ddd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity bounded_context
# invoke-edit: action satisfy | toolset: contexts.ddd.ddd:Ddd
# invoke-check: action validate | toolset: contexts.ddd.ddd:Ddd
"""DDD generator — domain emphasis, contexts, building blocks over clean_engineering."""

from __future__ import annotations

from primitives.actions.action import action
from contexts import context
from grill_context import grill_with_context
from primitives.instructions import Instruction
from primitives.instructions import instruction
from sketch import sketch
from tools.tool import tool  # noqa: F401

_FIDELITY_FORMAT_DEFAULTS = {
    "bounded_context": "markdown",
    "building_blocks": "markdown",
    "code": "python",
}

# DDD fidelity → clean_engineering fidelity (CE owns OO ladder; DDD overlays domain/strategic).
_CE_FIDELITY = {
    "bounded_context": "modules",
    "building_blocks": "specification",
    "code": "code",
}

_SUPPORTED_FORMATS = frozenset(
    {"markdown", "json", "python", "typescript", "java", "javascript", "drawio"}
)


@context
class Ddd:
    """§ Instructions"""

    def __init__(self, fidelity: str = "bounded_context", format: str | None = None) -> None:
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

    def _clean_engineering(self):
        from contexts.clean_engineering.clean_engineering import CleanEngineering

        return CleanEngineering(fidelity=_CE_FIDELITY[self.fidelity], format=self.format)

    @instruction
    def contexts(self) -> Instruction: ...

    @grill_with_context
    @sketch
    @action
    def generate(self) -> str: ...

    @action
    def generate_output(self) -> str:
        """"""
        self._clean_engineering().generate()
        return ""

    @action
    def validate(self) -> str:
        self.contexts
        self._clean_engineering().validate()
        self.scan()
        return "Validation report."

    @action
    def satisfy(self) -> str:
        self.contexts
        self.templates
        self._clean_engineering().satisfy()
        return "When done, run validate."

    @action
    def repair(self, asset: str, violation: str) -> str:
        self.scan()
        self.contexts
        self.examples
        self.templates
        self._clean_engineering().satisfy()
        self.validate()
        return "Repair {asset} until validate passes."

    @tool
    def transform(self, source_format: str, target_format: str, content: str) -> dict:
        """Sideways format conversion at the same fidelity.
        Delegates to clean_engineering.transform — DDD adds no separate channel model."""
        return self._clean_engineering().transform(source_format, target_format, content)
