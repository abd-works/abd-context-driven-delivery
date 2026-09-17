"""Assemble agent instructions from @markdown properties."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from actions.scan.rule import RulesCollection
from primitives.agent_tools.agent_tools import ToolSetCollection, agent_instructions, tools
from primitives.installer.marks import command, mcp, rules, skill
from primitives.markdown import Markdown, canonical_format, class_file_directory, fidelity_blocks, markdown


class Guidance:
    default_format: str = ""
    name: str | None = None
    domain_slug: str | None = None

    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: Any = None,
    ) -> None:
        self.format = format if format is not None else self.default_format
        self.path = path
        self.session = session
        self.workspace = workspace
        self.nested_toolsets = ToolSetCollection()

    @markdown("contexts")
    def context(self) -> str:
        """Contexts preamble for this host scope."""

    @markdown
    def guidance(self) -> str:
        """Guidance section body."""

    @markdown("shared rules")
    @rules
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    @markdown
    def templates(self) -> dict[str, str]:
        """Format key to relative path under templates/."""

    def _template_text(self) -> str:
        mapping = self.templates
        if not mapping:
            return ""
        key = canonical_format(self.format or self.default_format)
        if not key:
            return ""
        rel = mapping.get(key)
        if not rel:
            return ""
        path = class_file_directory(self) / rel
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
        return ""

    @property
    @skill
    @agent_instructions
    def instructions(self) -> str:
        return "\n\n".join(
            part
            for part in (
                (self.context or "").strip(),
                (self.guidance or "").strip(),
                self.rules.format_rules(),
                self._template_text(),
            )
            if part
        )

    @property
    def tools(self) -> dict[str, Any]:
        from primitives.agent_tools.agent_tools import AgentTool
        from primitives.installer.declared_installations import declared_installations

        found: dict[str, Any] = {}
        for declared in declared_installations(self):
            if (
                declared.invoke in {"action", "tool"}
                or declared.kind == "rules"
            ):
                found[declared.operation] = AgentTool(
                    name=declared.operation,
                    callable=declared.member,
                    toolset=self,
                )
        return found


class GuidanceCollection(ToolSetCollection, Guidance):
    def __init__(self, entries: dict[str, Guidance] | None = None) -> None:
        ToolSetCollection.__init__(self, entries)
        Guidance.__init__(self)

    @property
    def context(self) -> str:  # type: ignore[override]
        return "\n\n".join(child.context for child in self if child.context)

    @property
    def guidance(self) -> str:  # type: ignore[override]
        return "\n\n".join(child.guidance for child in self if child.guidance)

    @property
    def rules(self) -> RulesCollection:  # type: ignore[override]
        return RulesCollection({key: child.rules for key, child in self.entries.items()})

    @property
    def templates(self) -> dict[str, str]:  # type: ignore[override]
        merged: dict[str, str] = {}
        for child in self:
            merged.update(child.templates or {})
        return merged

    @property
    def instructions(self) -> str:
        return "\n\n".join(child.instructions for child in self if child.instructions)


class PracticeGuidance(Guidance):
    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: Any = None,
    ) -> None:
        super().__init__(format=format, path=path, session=session, workspace=workspace)
        self.fidelities = GuidanceCollection()
        self.nested_toolsets = self.fidelities
        self.fidelity: str | None = None
        from actions.scan.scan import Scan

        self.scanner = Scan.bound_to(self)

    @property
    def active(self) -> Any:
        """Current work session on this practice's workspace, when one is open."""
        workspace = self.workspace
        if workspace is None:
            return None
        return workspace.current_work_session

    @markdown
    def examples(self) -> str:
        """Examples folder content — not part of instructions."""

    @property
   
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        parts = [super().instructions]
        if self.fidelities.entries:
            for fidelity in self.fidelities.entries.values():
                tools(fidelity.instructions)
        return "\n\n".join(part for part in parts if part)


    def domain_markdown_path(self) -> Path:
        class_dir = class_file_directory(self)
        slug = self.domain_slug or class_dir.name
        return class_dir / f"{slug}.md"

    def prior_fidelity_context(self, fidelity_name: str) -> str:
        md_path = self.domain_markdown_path()
        if not md_path.is_file():
            return ""
        blocks = fidelity_blocks(md_path.read_text(encoding="utf-8"))
        parts: list[str] = []
        for name, body in blocks:
            if name == fidelity_name:
                break
            parts.append(body)
        return "\n\n".join(parts)

    def attach_fidelities(self, entries: dict[str, Guidance]) -> None:
        self.fidelities = GuidanceCollection(entries)
        self.nested_toolsets = self.fidelities

    def load_fidelities_from_markdown(self) -> None:
        md_path = self.domain_markdown_path()
        if not md_path.is_file():
            return
        text = md_path.read_text(encoding="utf-8")
        entries: dict[str, Guidance] = {}
        for name, _body in fidelity_blocks(text):
            entries[name] = FidelityGuidance(
                name=name,
                practice_guidance=self,
                default_format=self.default_format,
            )
        self.attach_fidelities(entries)
        if self.fidelity and self.fidelity in entries:
            child = entries[self.fidelity]
            self.format = child.default_format or self.format


class FidelityGuidance(Guidance):
    def __init__(
        self,
        name: str,
        stage: str = "",
        default_format: str = "",
        practice_guidance: PracticeGuidance | None = None,
    ) -> None:
        super().__init__(format=default_format)
        self.name = name
        self.stage = stage
        self.default_format = default_format
        self.practice_guidance = practice_guidance
        self.fidelity = name
        if practice_guidance is not None and self.domain_slug is None:
            self.domain_slug = practice_guidance.domain_slug

    @property
    def context(self) -> str:  # type: ignore[override]
        practice = self.practice_guidance
        if practice is None or not self.name:
            return super().context
        return practice.prior_fidelity_context(self.name)

    @markdown
    def guidance(self) -> str:
        """Fidelity guidance section."""

    @markdown("rules")
    @rules
    def rules(self) -> RulesCollection:
        """Fidelity rules section."""

    @property
    @command
    @agent_instructions
    def instructions(self) -> str:
        return super().instructions

    @property
    def templates(self) -> dict[str, str]:  # type: ignore[override]
        mapping = dict(super().templates or {})
        needle = self.name.replace(" ", "_")
        filtered = {key: rel for key, rel in mapping.items() if needle in str(key)}
        return filtered
