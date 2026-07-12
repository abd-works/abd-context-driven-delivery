# YOU MUST READ AND FOLLOW THE INSTRUCTIONS BELOW
# @toolset-manifest python -m tools manifest clean_code.clean_code:CleanCode
# Agent reading this file: instructions load via CLI only.
# 1. Run the manifest command on line 2
# 2. Run: python -m tools run -
# 3. Follow response.instructions before writing any production module.
# invoke-new: action generate | context.format python
# invoke-edit: action satisfy | context.format python
# invoke-check: action validate | context.format python — then scan output paths
# request-generate:
#   toolset: clean_code.clean_code:CleanCode
#   context:
#     format: python
#   action: generate
"""Clean production code generator."""

from __future__ import annotations

from pathlib import Path

from agents.action import action  # noqa: F401 — re-export for domain modules
from generator import generator_class_annotation  # noqa: F401
from tools.tool import resource  # noqa: F401 — re-export for domain modules


@generator_class_annotation
class CleanCode:
    """§ Instructions"""

    def __init__(self, format: str = "python") -> None:
        super().__init__(format=format)

    @property
    def module_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent / "clean-code"
