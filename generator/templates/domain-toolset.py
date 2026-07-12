# @toolset-manifest python -m tools manifest {module_path}:{ClassName}
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""{ClassName} generator."""

from __future__ import annotations

from agents.action import action  # noqa: F401
from generator import generator_class_annotation  # noqa: F401


@generator_class_annotation
class {ClassName}:
    """§ Instructions"""

    def __init__(self, format: str = "python") -> None:
        super().__init__(format=format)
