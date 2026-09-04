# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Instruction — @instruction. VS Code instruction file; Cursor deploys as Rule."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.bodies import ActionBody, ContextToolBody, UtilityBody
from harness.harness_tool import HarnessTool, instruction as instruction_decorator
from harness.rule import Rule

instruction = instruction_decorator


class Instruction(HarnessTool):
    def relative_path(self) -> Path:
        return Path("instructions") / f"{self.name}.instructions.md"

    def generate(self, source: Any = None, roots: list[Path] | None = None) -> HarnessTool:
        self.apply_source(source)
        if not self.body and isinstance(source, dict):
            name = self.name
            if source.get("action") or source.get("source_kind") == "action":
                self.body = ActionBody.from_source(
                    name=name,
                    class_string=source.get("class_string", name),
                    operation_instructions=source.get("guidance", ""),
                    toolset=source.get("toolset", ""),
                    context_tools=source.get("context_tools") or (),
                    invoke=source.get("invoke") or "action",
                    operation=source.get("operation") or "",
                    extended=source.get("extended") or False,
                )
            elif source.get("source_kind") == "utility":
                self.body = UtilityBody.from_source(
                    name=name,
                    class_string="",
                    operation_instructions=source.get("guidance", ""),
                    toolset=source.get("toolset", ""),
                    invoke=source.get("invoke") or "tool",
                    operation=source.get("operation") or "",
                )
            else:
                self.body = ContextToolBody.from_source(
                    name=name,
                    overview=self.description or source.get("overview", name),
                    toolset=source.get("toolset", ""),
                    fidelities=source.get("fidelities") or (),
                    actions=source.get("actions") or (),
                    extended=source.get("extended") or False,
                )
            if source.get("overview"):
                self.description = source["overview"]
        if self.type == "Cursor":
            rule = Rule(self.type, self.name)
            rule.description = self.description
            rule.body = self.body
            return rule.generate(source, roots)
        return super().generate(source, roots)
