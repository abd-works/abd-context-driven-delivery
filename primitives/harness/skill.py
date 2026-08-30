# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Skill — @skill. Cursor/VS Code: skills/{name}/SKILL.md."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.bodies import ActionBody, ContextToolBody, UtilityBody
from harness.harness_tool import HarnessTool, _frontmatter, skill as skill_decorator

skill = skill_decorator


class Skill(HarnessTool):
    def relative_path(self) -> Path:
        return Path("skills") / self.name / "SKILL.md"

    def render(self) -> str:
        return _frontmatter(self.name, self.description, self.model) + str(self.body)

    def generate(self, source: Any = None, roots: list[Path] | None = None) -> HarnessTool:
        self.apply_source(source)
        if not self.body:
            name = self.name
            meta = source if isinstance(source, dict) else {}
            if meta.get("action") or meta.get("source_kind") == "action":
                self.body = ActionBody.from_source(
                    name=name,
                    class_string=meta.get("class_string", name),
                    operation_instructions=meta.get("guidance", ""),
                    toolset=meta.get("toolset", ""),
                    kind="action",
                    fidelities=meta.get("fidelities") or (),
                    context_tools=meta.get("context_tools") or (),
                    invoke=meta.get("invoke") or "action",
                    operation=meta.get("operation") or "",
                )
            elif meta.get("source_kind") == "utility":
                self.body = UtilityBody.from_source(
                    name=name,
                    class_string=meta.get("class_string", name),
                    operation_instructions=meta.get("guidance", ""),
                    toolset=meta.get("toolset", ""),
                    invoke=meta.get("invoke") or "tool",
                    operation=meta.get("operation") or "",
                )
            else:
                self.body = ContextToolBody.from_source(
                    name=name,
                    overview=self.description or meta.get("overview", name),
                    toolset=meta.get("toolset", ""),
                    fidelities=meta.get("fidelities") or (),
                    actions=meta.get("actions") or (),
                )
            if not self.description:
                self.description = meta.get("overview", name)
        return super().generate(source, roots)
