# @toolset-manifest python -m tools manifest {module_path}:{ClassName}
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""{ClassName} generator."""

from __future__ import annotations

from primitives.actions.action import action  # noqa: F401
from context_tools import context  # noqa: F401


@context
class {ClassName}:
    """§ Instructions"""

    def __init__(self, format: str = "python", path: str | None = None, session: str | None = None) -> None:
        super().__init__(format=format, path=path, session=session)
