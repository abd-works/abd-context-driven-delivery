# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""AgentGuidance — later. HarnessTool subclass; generate is not implemented yet."""

from __future__ import annotations

from typing import Any

from harness.harness_tool import HarnessTool


class AgentGuidance(HarnessTool):
    def generate(self, source: Any = None, roots: list[Path] | None = None) -> HarnessTool:
        raise NotImplementedError("later")
