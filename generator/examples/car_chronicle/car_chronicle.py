# @toolset-manifest python -m tools manifest generator.examples.car_chronicle.car_chronicle:CarChronicle
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate
"""Minimal @generator example for generator specs."""

from __future__ import annotations

from generator import generator  # noqa: F401


@generator
class CarChronicle:
    """§ Instructions"""

    def __init__(self) -> None:
        super().__init__()
