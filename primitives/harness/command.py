# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Command — not a decorator. Cursor write for @prompt."""

from __future__ import annotations

from pathlib import Path

from harness.harness_tool import HarnessTool, _frontmatter


class Command(HarnessTool):
    def relative_path(self) -> Path:
        return Path("commands") / f"{self.name}.md"

    def render(self) -> str:
        # Cursor commands may ignore model; emit frontmatter only when a model is set.
        # Never emit disable-model-invocation.
        if self.model:
            return _frontmatter(
                self.name, self.description or self.name, self.model
            ) + str(self.body)
        return str(self.body)
