# @toolset-manifest python -m tools manifest bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.format python
# invoke-edit: action satisfy | context.format python
# invoke-check: action validate | context.format python
"""Vanilla BDD generator — RED-GREEN-REFACTOR test bodies from signatures."""

from __future__ import annotations

from agents.action import action  # noqa: F401 — re-export
from generator import generator_class_annotation  # noqa: F401


@generator_class_annotation
class Bdd:
    """§ Instructions"""

    def __init__(self, format: str = "python") -> None:
        super().__init__(format=format)
