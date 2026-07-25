# @toolset-manifest python -m tools manifest context_tools.base.examples.car_chronicle.car_chronicle:CarChronicle
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate
"""Minimal @context_tool example for generator specs."""

from __future__ import annotations

from context_tools import context_tool  # noqa: F401


@context_tool
class CarChronicle:
    """§ Instructions"""

    def __init__(self, path: str | None = None, session: str | None = None) -> None:
        super().__init__(path=path, session=session)
