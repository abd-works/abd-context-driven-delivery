# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Skill — @skill. Cursor/VS Code: skills/{folder}/{name}/SKILL.md."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness.bodies import ActionBody, ContextToolBody, ContextToolFidelityBody, UtilityBody
from harness.harness_tool import HarnessTool, _frontmatter, skill as skill_decorator

skill = skill_decorator


class Skill(HarnessTool):
    def relative_path(self) -> Path:
        if self.folder:
            return Path("skills") / self.folder / self.name / "SKILL.md"
        return Path("skills") / self.name / "SKILL.md"

    def render(self) -> str:
        return _frontmatter(
            self.name,
            self.description,
            self.model,
            disable_model_invocation=self.disable_model_invocation,
        ) + str(self.body)

    def generate(self, source: Any = None, roots: list[Path] | None = None) -> HarnessTool:
        self.apply_source(source)
        if not self.body:
            name = self.name
            meta = source if isinstance(source, dict) else {}
            if meta.get("fidelity"):
                fidelity_name = meta.get("fidelity_slug") or name
                if meta.get("extended"):
                    self.body = ContextToolFidelityBody.from_source(
                        overview=meta.get("overview", name),
                        toolset=meta.get("toolset", ""),
                        guidance=meta.get("guidance", ""),
                        instructions=meta.get("returned", ""),
                        fidelities=meta.get("fidelities") or (),
                        actions=meta.get("actions") or (),
                        fidelity=fidelity_name,
                        constructor_context=meta.get("constructor_context") or None,
                    )
                else:
                    self.body = ActionBody.from_source(
                        name=fidelity_name,
                        class_string=meta.get("class_string", name),
                        operation_instructions=meta.get("guidance", ""),
                        toolset=meta.get("toolset", ""),
                        kind="fidelity",
                        fidelities=meta.get("fidelities") or (),
                        constructor_context=meta.get("constructor_context") or None,
                    )
            elif meta.get("action") or meta.get("source_kind") == "action":
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
                    extended=meta.get("extended") or False,
                    constructor_context=meta.get("constructor_context") or None,
                )
            elif meta.get("source_kind") == "utility":
                self.body = UtilityBody.from_source(
                    name=name,
                    class_string=meta.get("class_string", name),
                    operation_instructions=meta.get("guidance", ""),
                    toolset=meta.get("toolset", ""),
                    invoke=meta.get("invoke") or "tool",
                    operation=meta.get("operation") or "",
                    constructor_context=meta.get("constructor_context") or None,
                )
            else:
                self.body = ContextToolBody.from_source(
                    name=name,
                    overview=self.description or meta.get("overview", name),
                    toolset=meta.get("toolset", ""),
                    fidelities=meta.get("fidelities") or (),
                    actions=meta.get("actions") or (),
                    extended=meta.get("extended") or False,
                )
            if not self.description:
                self.description = meta.get("overview", name)
        return super().generate(source, roots)
