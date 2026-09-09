# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Rule — Cursor .mdc project rule."""

from __future__ import annotations

from pathlib import Path

from harness.harness_tool import HarnessTool


class Rule(HarnessTool):
    """One `.cursor/rules/**/*.mdc` or `.kilo/rules/**/*.md` file with YAML frontmatter."""

    def __init__(self, type: str, name: str = "") -> None:
        super().__init__(type, name)
        self.globs: str = ""
        self.always_apply: bool = False
        self.subfolder: str = ""

    def relative_path(self) -> Path:
        if self.type == "Cursor":
            ext = ".mdc"
            folder = "rules"
        elif self.type == "VS Code":
            ext = ".md"
            folder = "instructions"
        else:
            ext = ".md"
            folder = "rules"

        if self.subfolder:
            return Path(folder) / self.subfolder / f"{self.name}{ext}"
        return Path(folder) / f"{self.name}{ext}"

    def _render_body(self) -> str:
        if self.body is None:
            return ""
        if isinstance(self.body, str):
            return self.body
        if hasattr(self.body, "render"):
            return self.body.render()
        return str(self.body)

    def render(self) -> str:
        lines = ["---"]
        if self.description:
            safe = self.description.replace('"', "'").splitlines()[0]
            lines.append(f'description: "{safe}"')
        if self.globs:
            lines.append(f"globs: {self.globs}")
        lines.append(f"alwaysApply: {'true' if self.always_apply else 'false'}")
        lines.append("---")
        lines.append("")
        body = self._render_body().strip()
        if body:
            lines.append(body)
            lines.append("")
        return "\n".join(lines)
