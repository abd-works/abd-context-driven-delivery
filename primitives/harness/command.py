# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Command — not a decorator. Cursor write for @prompt."""

from __future__ import annotations

from pathlib import Path

from harness.harness_tool import HarnessTool


class Command(HarnessTool):
    def relative_path(self) -> Path:
        return Path("commands") / f"{self.name}.md"
