# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Rule — not a decorator. Cursor write for @instruction."""

from __future__ import annotations

from pathlib import Path

from harness.harness_tool import HarnessTool


class Rule(HarnessTool):
    def relative_path(self) -> Path:
        return Path("rules") / f"{self.name}.mdc"
