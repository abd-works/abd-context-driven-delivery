"""Assemble agent instructions from @markdown properties."""
from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from typing import Any

from actions.scan.rule import RulesCollection
from harness.agent_tools.agent_tools import (
    collect,
    agent_instructions,
    agent_tool,
    agent_toolset,
    toolsetCollection,
)
from installation.harness_files.harness_files import rules, skill
from installation.hooks.prompt_echo.prompt_echo import echo
from installation.mcp.mcp_server import mcp
from harness.markdown import (
    Markdown,
    MarkdownCollection,
    class_file_directory,
    fidelity_blocks,
    markdown,
    markdownCollection,
)


@agent_toolset
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
        return re.sub(r"(?<!^)(?=[A-Z])", "-", type(self).__name__).lower()

    @property
    def install_folder(self) -> Path:
        return class_file_directory(self)

    @markdownCollection("shared rules")
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

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
                (self.rules.markdown or "").strip(),
                (self.templates or "").strip(),
            )
            if part
        )


@toolsetCollection
class GuidanceCollection(MarkdownCollection, Guidance):
    def __init__(self, entries: dict[str, Guidance] | None = None, parent: Any = None) -> None:
        MarkdownCollection.__init__(self, entries, parent=parent)
        Guidance.__init__(self)
        self.current: Guidance | None = None
        self.stage: dict[str, Guidance] = {
            key: child
            for child in self.entries.values()
            if (key := getattr(child, "stage", "") or "")
        }

    @classmethod
    def child(cls, name: str, body: str = "") -> FidelityGuidance:
        return FidelityGuidance(name=name)

    @collect
    def overview(self) -> str: ...

    @collect
    def guidance(self) -> str: ...

    @collect
    def rules(self) -> RulesCollection: ...

    @collect
    def templates(self) -> str: ...

    @collect
    @echo
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str: ...


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
        from actions.scan.scan import Scan

        self.scanner = Scan.bound_to(self)
        self._attach_workspace()
        self._activate(fidelity=fidelity)

    @property
    def context_index_key(self) -> str:
        return class_file_directory(self).name

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
    
    ## workspace integration to move

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
        if self.format:
            self.format = self._canonical_format(self.format)
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
        if path is not None:
            self.path = path
        if session is not None:
            self.session = session
        if workspace is not None:
            self.workspace = workspace

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

    @property
    @agent_instructions
    def guidance(self) -> str:
        text = Markdown.from_label(self, "guidance").extract()
        companion = self.clean_engineering_companion
        extra = companion.instructions if companion is not None else ""
        return "\n\n".join(part for part in (text, extra) if part)


    @property
    @echo
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
        parts = [super().instructions]
        if self.fidelities.entries:
            parts.append(self.fidelities.instructions)
        return "\n\n".join(part for part in parts if part)


    @toolsetCollection
    @markdownCollection
    def fidelities(self) -> GuidanceCollection:
        """Fidelity children from the Fidelities section."""

    def domain_markdown_path(self) -> Path:
        class_dir = class_file_directory(self)
        return class_dir / f"{class_dir.name}.md"

    @markdown
    def examples(self) -> str:
        """Examples folder content — not part of instructions."""

    ## format integration 


    @property
    def formats(self) -> dict[str, Any]:
        return dict(self._formats)

    _format_aliases = {"md": "markdown"}

    def _canonical_format(self, format_name: str) -> str:
        return self._format_aliases.get(format_name, format_name)

    def _format_adapter(self, format_name: str) -> Any:
        adapters = self.formats
        resolved = self._canonical_format(format_name)
        if resolved not in adapters:
            raise ValueError(
                f"Unsupported format {format_name!r}. Choose from: {sorted(adapters)}"
            )
        entry = adapters[resolved]
        if isinstance(entry, tuple):
            module_path, attr = entry
            import importlib

            return getattr(importlib.import_module(module_path), attr)
        return entry


    _code_formats = frozenset({"python", "typescript", "java", "javascript"})

    @agent_tool
    def render(
        self,
        format: str,
        content: Any = "",
        source: str | None = None,
        previous: str = "",
        keep_positioning: bool = False,
    ) -> dict:
        """Turn content into the practice object model, then render the target format."""
        if not self.formats:
            companion = self.clean_engineering_companion
            owner = companion.practice_guidance if companion is not None else None
            if owner is None or owner is self:
                return {"format": source or self.format or format, "content": content}
            return owner.render(
                format,
                content,
                source=source,
                previous=previous,
                keep_positioning=keep_positioning,
            )
        model = self._to_object_model(content, source)
        target = self._live_adapter(format)
        rendered = self._call_render(target, model, previous, keep_positioning)
        return {"format": format, "content": rendered}

    def _to_object_model(self, content: Any, source: str | None) -> Any:
        if self._is_object_model(content):
            return content
        if self._is_tool(content):
            return self._instantiate_from_tool(content, source)
        source_format = self._canonical_format(source or self.format or "")
        if not source_format:
            raise ValueError("source format is not set")
        if source_format in self._code_formats and content in ("", None):
            return self._instantiate_from_tool(self, source_format)
        return self._parse_content(source_format, content)

    def _is_object_model(self, content: Any) -> bool:
        if isinstance(content, (str, bytes, dict, list)) or content is None:
            return False
        return callable(getattr(content, "semantic_type", None))

    def _is_tool(self, content: Any) -> bool:
        if self._is_object_model(content):
            return False
        return bool(getattr(type(content), "_is_agent_toolset", False))

    def _instantiate_from_tool(self, tool: Any, source: str | None) -> Any:
        source_format = self._canonical_format(
            source or getattr(tool, "format", None) or self.format or ""
        )
        if source_format in self._code_formats:
            adapter = self._live_adapter(source_format)
            return adapter.parse(self._code_tree(self._context_root(tool), adapter))
        return self._parse_content(source_format, "")

    def _context_root(self, tool: Any) -> Path:
        workspace = getattr(tool, "workspace", None)
        path = getattr(workspace, "path", None) or getattr(tool, "path", None) or "."
        return Path(path)

    def _code_tree(self, root: Path, adapter: Any) -> dict[str, str]:
        extension = getattr(adapter, "LEAF_EXTENSION", "") or ""
        tree: dict[str, str] = {}
        if not extension:
            return tree
        for path in root.rglob(f"*{extension}"):
            if path.is_file():
                tree[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")
        return tree

    def _parse_content(self, source_format: str, content: Any) -> Any:
        adapter = self._live_adapter(source_format)
        return adapter.parse(self._incoming(source_format, content))

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
        self.parent = practice_guidance
        self.fidelity = name
        if clean_engineering is not None:
            self.clean_engineering = clean_engineering

    @property
    def practice_guidance(self) -> PracticeGuidance | None:
        parent = getattr(self, "parent", None)
        if parent is None:
            return None
        owner = getattr(parent, "parent", None)
        return owner if owner is not None else parent

    @property
    def context_index_key(self) -> str:
        practice = self.practice_guidance
        if practice is not None:
            return practice.context_index_key
        return class_file_directory(self).name

    @property
    def default_format(self) -> str:
        return getattr(self, "_default_format", "")

    @default_format.setter
    def default_format(self, value: str) -> None:
        self._default_format = value or ""
        if self._default_format:
            self.format = self._default_format

    @property
    def clean_engineering(self) -> FidelityGuidance | None:
        stored = getattr(self, "_clean_engineering", None)
        if isinstance(stored, FidelityGuidance):
            return stored
        if not isinstance(stored, str) or not stored:
            return None
        from practices.clean_engineering.clean_engineering import CleanEngineering

        companion = CleanEngineering().fidelities[stored]
        self._clean_engineering = companion
        return companion

    @clean_engineering.setter
    def clean_engineering(self, value: Any) -> None:
        self._clean_engineering = value

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

    @markdownCollection
    @rules
    @agent_tool
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
                (practice.rules.markdown or "").strip(),
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
                (self.rules.markdown or "").strip(),
                templates,
                companion_text,
            )
            if part
        )
