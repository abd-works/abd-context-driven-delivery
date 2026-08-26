# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Prompt — @prompt. VS Code prompt file; Cursor deploys as Command."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.bodies import ActionBody, FormatBody
from harness.command import Command
from harness.harness_tool import HarnessTool, prompt as prompt_decorator

prompt = prompt_decorator


class Prompt(HarnessTool):
    def relative_path(self) -> Path:
        return Path("prompts") / f"{self.name}.prompt.md"

    def generate(self, source: Any = None, roots: list[Path] | None = None) -> HarnessTool:
        self.apply_source(source)
        if not self.body and isinstance(source, dict):
            name = self.name
            if source.get("format"):
                self.body = FormatBody.from_source(format=name)
                self.description = self.description or name
            else:
                self.body = ActionBody.from_source(
                    name=name,
                    class_string=source.get("class_string", name),
                    operation_instructions=source.get("guidance", ""),
                    toolset=source.get("toolset", ""),
                )
                if source.get("overview"):
                    self.description = source["overview"]
        if self.type == "Cursor":
            command = Command(self.type, self.name)
            command.description = self.description
            command.body = self.body
            return command.generate(source, roots)
        return super().generate(source, roots)
