"""Assemble agent instructions from @markdown properties."""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

from actions.scan.rule import RulesCollection
from harness.agent_tools.agent_tools import (
    ToolSetCollection,
    agent_instructions,
    agent_tool,
    agent_toolset,
    tools,
)
from installation.harness_files.harness_files import rules, skill
from installation.mcp.mcp_server import mcp
from harness.markdown import Markdown, class_file_directory, fidelity_blocks, fidelity_stage, markdown


class Guidance:
    default_format: str = ""
    name: str | None = None
    domain_slug: str | None = None

    @property
    def slug(self) -> str:
        if self.domain_slug:
            return str(self.domain_slug).replace("_", "-")
        return type(self).__name__.replace("_", "-").lower()

    @property
    def install_folder(self) -> Path:
        return class_file_directory(self)

    @property
    def registration_name(self) -> str:
        typ = type(self)
        return f"{typ.__module__}:{typ.__name__}"

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

    @markdown
    def overview(self) -> str:
        """Overview section for this host."""

    @markdown
    def guidance(self) -> str:
        """Guidance section body."""

    @property
    @rules
    def rules_markdown(self) -> str:
        return Markdown.from_label(self, "shared rules").extract().strip()

    @markdown("shared rules")
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    @markdown
    def templates(self) -> str:
        """Active template file for this host's format and fidelity."""

    @property
    def prompt_message(self) -> str:
        """Overview for skill/MCP/prompt copy — not the instructions docstring."""
        return (self.overview or "").strip() or (self.guidance or "").strip()

    @property
    @skill
    @mcp
    @agent_instructions
    def instructions(self) -> str:
        return "\n\n".join(
            part
            for part in (
                (self.overview or "").strip(),
                (self.guidance or "").strip(),
                (self.rules_markdown or "").strip(),
                (self.templates or "").strip(),
            )
            if part
        )

    @property
    def tools(self) -> dict[str, Any]:
        from harness.agent_tools.agent_tools import AgentTool

        found: dict[str, Any] = {}
        cls = type(self)
        seen: set[str] = set()
        members: list[tuple[str, Any]] = []
        for name, member in inspect.getmembers(cls, predicate=inspect.isfunction):
            seen.add(name)
            members.append((name, member))
        for name, member in inspect.getmembers(cls, predicate=inspect.isdatadescriptor):
            getter = getattr(member, "fget", None)
            if getter is not None and name not in seen:
                members.append((name, getter))
        for name, member in members:
            is_instructions = getattr(member, "_is_agent_instructions", False)
            is_tool = getattr(member, "_is_agent_tool", False)
            is_rules = getattr(member, "_rules", False)
            if not (is_instructions or is_tool or is_rules):
                continue
            found[name] = AgentTool(name=name, callable=member, toolset=self)
        return found


class GuidanceCollection(ToolSetCollection, Guidance):
    def __init__(self, entries: dict[str, Guidance] | None = None) -> None:
        ToolSetCollection.__init__(self, entries)
        Guidance.__init__(self)
        self.current: Guidance | None = None
        self.stage: dict[str, Guidance] = {
            key: child
            for child in self.entries.values()
            if (key := getattr(child, "stage", "") or "")
        }

    def __getitem__(self, name: str) -> Guidance:
        return self.entries[name]

    @property
    def overview(self) -> str:  # type: ignore[override]
        return "\n\n".join(child.overview for child in self if child.overview)

    @property
    def guidance(self) -> str:  # type: ignore[override]
        return "\n\n".join(child.guidance for child in self if child.guidance)

    @property
    def rules(self) -> RulesCollection:  # type: ignore[override]
        return RulesCollection({key: child.rules for key, child in self.entries.items()})

    @property
    def templates(self) -> str:  # type: ignore[override]
        return "\n\n".join(child.templates for child in self if child.templates)

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
        fidelity: str | None = None,
        stage: str | None = None,
    ) -> None:
        defaults = getattr(type(self), "_fidelity_format_defaults", None) or {}
        supported = getattr(type(self), "supported_formats", None)
        super().__init__(format=format, path=path, session=session or "", workspace=workspace)
        self.fidelities = GuidanceCollection()
        self.nested_toolsets = self.fidelities
        from actions.scan.scan import Scan

        self.scanner = Scan.bound_to(self)
        self._attach_workspace(path=path, session=session, workspace=workspace)
        self.load_fidelities_from_markdown()
        if stage is not None:
            child = self.fidelities.stage[stage]
            fidelity = getattr(child, "name", None) or fidelity
        if fidelity is not None:
            if defaults and fidelity not in defaults:
                raise ValueError(
                    f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(defaults)}"
                )
            if format is None and fidelity in defaults:
                self.format = defaults[fidelity]
            if fidelity in self.fidelities.entries:
                self.fidelities.current = self.fidelities[fidelity]
        if supported and self.format and self.format not in supported:
            raise ValueError(
                f"Unsupported format {self.format!r}. Choose from: {sorted(supported)}"
            )

    def _attach_workspace(
        self,
        path: str | None,
        session: str | None,
        workspace: Any,
    ) -> None:
        from tools.workspace.workspace import Workspace

        if path is not None:
            self.path = path
        if session is not None:
            self.session = session
        if isinstance(workspace, Workspace):
            self.workspace = workspace
            return
        root = workspace or self.path or "."
        self.workspace = Workspace(str(root))
        self.workspace.load()
        if self.session:
            self.workspace.open(
                self,
                name=self.session,
                path=self.path or "",
            )

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

    @mcp
    @agent_tool
    def fidelityInstructions(self, fidelity: str) -> str:
        """Assembled instructions for one fidelity."""
        return self.fidelities[fidelity].instructions

    def domain_markdown_path(self) -> Path:
        class_dir = class_file_directory(self)
        slug = self.domain_slug or class_dir.name
        return class_dir / f"{slug}.md"

    def attach_fidelities(self, entries: dict[str, Guidance]) -> None:
        self.fidelities = GuidanceCollection(entries)
        self.nested_toolsets = self.fidelities

    def load_fidelities_from_markdown(self) -> None:
        md_path = self.domain_markdown_path()
        if not md_path.is_file():
            return
        text = md_path.read_text(encoding="utf-8")
        entries: dict[str, Guidance] = {}
        defaults = getattr(type(self), "_fidelity_format_defaults", None) or {}
        for name, body in fidelity_blocks(text):
            child_format = defaults.get(name) or self.format or self.default_format or ""
            entries[name] = FidelityGuidance(
                name=name,
                stage=fidelity_stage(body),
                practice_guidance=self,
                default_format=child_format,
            )
        self.attach_fidelities(entries)

    def scoped_markdown(self) -> str:
        """Overview, practice sections, and the active fidelity (or every fidelity)."""
        parts = [
            Markdown.from_label(self, label).extract()
            for label in ("overview", "guidance", "shared rules", "language")
        ]
        md_path = self.domain_markdown_path()
        if md_path.is_file():
            for name, body in fidelity_blocks(md_path.read_text(encoding="utf-8")):
                current = self.fidelities.current
                current_name = getattr(current, "fidelity", None) or getattr(current, "name", None)
                if current_name and name != current_name:
                    continue
                parts.append(f"### {name}\n\n{body}")
        return "\n\n".join(part for part in parts if part.strip())


@agent_toolset
class FidelityGuidance(Guidance):
    def __init__(
        self,
        name: str = "",
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
    def slug(self) -> str:
        parent = self.practice_guidance.slug if self.practice_guidance is not None else super().slug
        leaf = (self.name or "").replace("_", "-")
        return f"{parent}-{leaf}" if leaf else parent

    @property
    def install_folder(self) -> Path:
        practice = self.practice_guidance
        base = practice.install_folder if practice is not None else class_file_directory(self)
        leaf = (self.name or "").replace(" ", "-")
        return base / leaf if leaf else base

    @property
    def overview(self) -> str:  # type: ignore[override]
        return Markdown.from_label(self, "overview").extract()

    @markdown
    def guidance(self) -> str:
        """Fidelity guidance section."""

    @property
    @rules
    def rules_markdown(self) -> str:
        return Markdown.from_label(self, "rules").extract().strip()

    @markdown("rules")
    def rules(self) -> RulesCollection:
        """Fidelity rules section."""

    @property
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        practice = self.practice_guidance
        parent = ()
        templates = ""
        if practice is not None:
            parent = (
                (practice.overview or "").strip(),
                (practice.guidance or "").strip(),
                (practice.rules_markdown or "").strip(),
            )
            previous = practice.fidelities.current
            previous_format = practice.format
            practice.fidelities.current = practice.fidelities[self.name]
            practice.format = self.format or self.default_format
            try:
                templates = (practice.templates or "").strip()
            finally:
                practice.fidelities.current = previous
                practice.format = previous_format
            if templates:
                templates = f"#### Template\n\n{templates}"
        return "\n\n".join(
            part
            for part in (
                *parent,
                (self.overview or "").strip(),
                (self.guidance or "").strip(),
                (self.rules_markdown or "").strip(),
                templates,
            )
            if part
        )
