"""Assemble agent instructions from @markdown properties."""
from __future__ import annotations

import fnmatch
import inspect
import json
import re
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
from installation.hooks.prompt_echo.prompt_echo import echo, inject_rules_toast, show_ide_toast
from installation.hooks.hooks import Hook
from installation.mcp.mcp_server import mcp
from harness.markdown import (
    Markdown,
    bind_yaml,
    class_file_directory,
    fidelity_blocks,
    fidelity_clean_engineering,
    fidelity_format,
    fidelity_stage,
    markdown,
)


class Guidance:
    default_format: str = ""
    name: str | None = None
    domain_slug: str | None = None

    @property
    def registration_name(self) -> str:
        typ = type(self)
        return f"{typ.__module__}:{typ.__name__}"

    @property
    def slug(self) -> str:
        if self.domain_slug:
            return str(self.domain_slug).replace("_", "-")
        return type(self).__name__.replace("_", "-").lower()

    @property
    def rules_label(self) -> str:
        """Practice or context name for an inject toast — shared rules, not a fidelity."""
        return self._words_from_slug(self.slug)

    def _words_from_slug(self, slug: str) -> str:
        return str(slug).replace("_", "-").replace("-", " ").strip()

    def _hook_tool_path(self, payload: dict[str, Any]) -> str:
        raw = payload.get("tool_input") or {}
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                return ""
        if not isinstance(raw, dict):
            return ""
        return str(
            raw.get("path") or raw.get("file_path") or raw.get("target_notebook") or ""
        )

    def _path_matches_globs(self, path: str, globs: str) -> bool:
        if not path or not globs:
            return False
        posix = Path(path).as_posix()
        name = Path(path).name
        for pattern in (part.strip().strip("\"'") for part in globs.split(",")):
            if not pattern:
                continue
            if Path(posix).match(pattern) or fnmatch.fnmatch(posix, pattern) or fnmatch.fnmatch(
                name, pattern.split("/")[-1]
            ):
                return True
        return False

    @property
    def install_folder(self) -> Path:
        return class_file_directory(self)

    @property
    @rules
    def rules_markdown(self) -> str:
        return Markdown.from_label(self, "shared rules").extract().strip()

    @markdown("shared rules")
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    @echo
    @Hook("preToolUse")
    def inject_rules(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Inject the rules markdown from this Guidance when the agent writes a file that matches the rule file glob pattern."""
        data = payload or {}
        tool_name = str(data.get("tool_name") or "")
        if tool_name not in {"Write", "StrReplace", "EditNotebook"}:
            return {}
        path = self._hook_tool_path(data)
        globs = getattr(getattr(self.rules, "appliesTo", None), "globs", "") or ""
        if not path or not self._path_matches_globs(path, globs):
            return {}
        body = (self.rules_markdown or "").strip()
        if not body:
            return {}
        show_ide_toast(inject_rules_toast("edit injecting rules:", [self.rules_label]))
        return {"permission": "allow", "additional_context": body, "agent_message": body}

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
        """Overview section for this Guidance."""

    @markdown
    def guidance(self) -> str:
        """Guidance section body."""

    @markdown
    def templates(self) -> str:
        """Active template file for this Guidance format and fidelity."""

    @property
    @echo
    @skill
    @mcp
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
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
            is_hook = getattr(member, "_hook", False)
            if not (is_instructions or is_tool or is_rules or is_hook):
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
        fidelity: str | None = None,
        default_workspace_folder: str = ".",
        formats: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(format=format)
        self.default_workspace_folder = default_workspace_folder
        self._formats = dict(formats or {})
        self.fidelities = GuidanceCollection()
        self.nested_toolsets = self.fidelities
        from actions.scan.scan import Scan

        self.scanner = Scan.bound_to(self)
        self._attach_workspace()
        self.load_fidelities_from_markdown()
        self._activate(fidelity=fidelity)

    @echo
    @Hook("preToolUse")
    def inject_rules(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Inject this practice's shared rules and any fidelity whose globs match the file."""
        data = payload or {}
        tool_name = str(data.get("tool_name") or "")
        if tool_name not in {"Write", "StrReplace", "EditNotebook"}:
            return {}
        path = self._hook_tool_path(data)
        if not path:
            return {}
        parts: list[str] = []
        labels: list[str] = []
        for guidance in (self, *self.fidelities.entries.values()):
            globs = getattr(getattr(guidance.rules, "appliesTo", None), "globs", "") or ""
            if not self._path_matches_globs(path, globs):
                continue
            body = (guidance.rules_markdown or "").strip()
            if not body:
                continue
            parts.append(body)
            labels.append(guidance.rules_label)
        if not parts:
            return {}
        show_ide_toast(inject_rules_toast("chat edit", labels))
        return {
            "permission": "allow",
            "additional_context": "\n\n".join(parts),
            "agent_message": "\n\n".join(parts),
        }

    @property
    def domain_slug(self) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", type(self).__name__).lower()

    @property
    def context_index_key(self) -> str:
        return self.domain_slug

    @property
    def supported_formats(self) -> frozenset:
        own = self.formats
        if own:
            return frozenset(own)
        companion = self.clean_engineering_companion
        owner = companion.practice_guidance if companion is not None else None
        if owner is not None and owner is not self:
            return frozenset(owner.formats)
        return frozenset()

    def _activate(self, fidelity: str | None = None, stage: str | None = None) -> None:
        if stage is not None:
            child = self.fidelities.stage[stage]
            fidelity = getattr(child, "name", None) or fidelity
        if fidelity is not None:
            names = sorted(self.fidelities.entries)
            if names and fidelity not in self.fidelities.entries:
                raise ValueError(f"Unsupported fidelity {fidelity!r}. Choose from: {names}")
            if not self.format and fidelity in self.fidelities.entries:
                child_format = self.fidelities[fidelity].default_format
                if child_format:
                    self.format = child_format
            if fidelity in self.fidelities.entries:
                self.fidelities.current = self.fidelities[fidelity]
        supported = self.supported_formats
        if supported and self.format and self.format not in supported:
            raise ValueError(
                f"Unsupported format {self.format!r}. Choose from: {sorted(supported)}"
            )

    def _attach_workspace(
        self,
        path: str | None = None,
        session: str | None = None,
        workspace: Any = None,
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
    def active_session(self) -> Any:
        """Current work session on this practice's workspace, when one is open."""
        workspace = self.workspace
        if workspace is None:
            return None
        return workspace.current_work_session

    @property
    def clean_engineering_companion(self) -> FidelityGuidance | None:
        companion = getattr(self.fidelities.current, "clean_engineering", None)
        return companion if isinstance(companion, FidelityGuidance) else None

    def _bind_clean_engineering_companions(self, companions: dict[str, str]) -> None:
        if not companions or self.domain_slug == "clean_engineering":
            return
        from practices.clean_engineering.clean_engineering import CleanEngineering

        ce = CleanEngineering()
        if self.format in {"python", "typescript", "java", "javascript"}:
            ce.format = self.format
        for name, ce_fidelity in companions.items():
            child = self.fidelities.entries.get(name)
            companion = ce.fidelities.entries.get(ce_fidelity)
            if isinstance(child, FidelityGuidance):
                child.clean_engineering = companion if isinstance(companion, FidelityGuidance) else None


    @property
    @agent_instructions
    def guidance(self) -> str:
        text = Markdown.from_label(self, "guidance").extract()
        companion = self.clean_engineering_companion
        extra = companion.instructions if companion is not None else ""
        return "\n\n".join(part for part in (text, extra) if part)

    @markdown
    def examples(self) -> str:
        """Examples folder content — not part of instructions."""

    @property
    @echo
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
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

    def attach_fidelities(self, entries: dict[str, Guidance]) -> None:
        self.fidelities = GuidanceCollection(entries)
        self.nested_toolsets = self.fidelities

    def load_fidelities_from_markdown(self) -> None:
        md_path = self.domain_markdown_path()
        if not md_path.is_file():
            return
        text = md_path.read_text(encoding="utf-8")
        entries: dict[str, Guidance] = {}
        companions: dict[str, str] = {}
        for name, body in fidelity_blocks(text):
            child = FidelityGuidance(name=name, practice_guidance=self)
            bind_yaml(child, body)
            if not child.default_format:
                child.default_format = (
                    fidelity_format(body) or self.format or self.default_format or ""
                )
            if not child.stage:
                child.stage = fidelity_stage(body)
            child.format = child.default_format
            entries[name] = child
            ce_name = (
                child.clean_engineering
                if isinstance(child.clean_engineering, str)
                else ""
            )
            if not ce_name:
                ce_name = fidelity_clean_engineering(body)
            if ce_name:
                companions[name] = ce_name
        self.attach_fidelities(entries)
        self._bind_clean_engineering_companions(companions)

    def domain_markdown_path(self) -> Path:
        class_dir = class_file_directory(self)
        slug = self.domain_slug or class_dir.name
        return class_dir / f"{slug}.md"


    @property
    def formats(self) -> dict[str, Any]:
        return dict(self._formats)

    def _format_adapter(self, format_name: str) -> Any:
        adapters = self.formats
        if format_name not in adapters:
            raise ValueError(
                f"Unsupported format {format_name!r}. Choose from: {sorted(adapters)}"
            )
        entry = adapters[format_name]
        if isinstance(entry, tuple):
            module_path, attr = entry
            import importlib

            return getattr(importlib.import_module(module_path), attr)
        return entry


    @agent_tool
    def render(
        self,
        format: str,
        content: str,
        source: str | None = None,
        previous: str = "",
        keep_positioning: bool = False,
    ) -> dict:
        """Parse source format into the practice model, then render the target format."""
        source_format = source or self.format
        if not self.formats:
            companion = self.clean_engineering_companion
            owner = companion.practice_guidance if companion is not None else None
            if owner is None or owner is self:
                return {"format": source_format or format, "content": content}
            return owner.render(
                format,
                content,
                source=source_format,
                previous=previous,
                keep_positioning=keep_positioning,
            )
        if not source_format:
            raise ValueError("source format is not set")
        source = self._live_adapter(source_format)
        target = self._live_adapter(format)
        parsed = source.parse(self._incoming(source_format, content))
        rendered = self._call_render(target, parsed, previous, keep_positioning)
        return {"format": format, "content": rendered}

    def _call_render(self, target: Any, parsed: Any, previous: str, keep_positioning: bool) -> Any:
        try:
            parameters = inspect.signature(target.render).parameters
        except (TypeError, ValueError):
            return target.render(parsed)
        kwargs: dict[str, Any] = {}
        if "previous" in parameters:
            kwargs["previous"] = previous or None
        if "keep_positioning" in parameters:
            kwargs["keep_positioning"] = keep_positioning
        return target.render(parsed, **kwargs)

    def _live_adapter(self, format_name: str) -> Any:
        adapter = self._format_adapter(format_name)
        if not inspect.isclass(adapter):
            return adapter
        try:
            return adapter(tests_root=self.default_workspace_folder)
        except TypeError:
            try:
                return adapter()
            except TypeError:
                return adapter

    def _incoming(self, format_name: str, content: Any) -> Any:
        if format_name in {"python", "typescript", "java", "javascript"}:
            if isinstance(content, dict):
                return content
            if isinstance(content, str):
                text = content.strip()
                if text.startswith("{") or text.startswith("["):
                    return json.loads(content)
        return content
    

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
        clean_engineering: FidelityGuidance | None = None,
    ) -> None:
        super().__init__(format=default_format)
        self.name = name
        self.stage = stage
        self.default_format = default_format
        self.practice_guidance = practice_guidance
        self.clean_engineering = clean_engineering
        self.fidelity = name
        if practice_guidance is not None and self.domain_slug is None:
            self.domain_slug = practice_guidance.domain_slug

    @property
    def slug(self) -> str:
        parent = self.practice_guidance.slug if self.practice_guidance is not None else super().slug
        leaf = (self.name or "").replace("_", "-")
        return f"{parent}-{leaf}" if leaf else parent

    @property
    def rules_label(self) -> str:
        practice = self.practice_guidance
        head = self._words_from_slug(practice.slug if practice is not None else self.slug)
        fidelity = str(self.fidelity or self.name or "").replace("_", " ").strip()
        return f"{head} {fidelity}".strip()

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
    @echo
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
        practice = self.practice_guidance
        parent = ()
        templates = ""
        companion_text = ""
        if practice is not None:
            parent = (
                (practice.overview or "").strip(),
                Markdown.from_label(practice, "guidance").extract().strip(),
                (practice.rules_markdown or "").strip(),
            )
            companion = self.clean_engineering
            companion_text = (
                companion.instructions if isinstance(companion, FidelityGuidance) else ""
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
                companion_text,
            )
            if part
        )
