"""Assemble agent instructions from @markdown properties."""
from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness.agent_tools.name import Name
from harness.guidance.rule import RulesCollection
from harness.agent_tools.agent_tools import (
    collect,
    agent_instructions,
    agent_tool,
    agent_toolset,
    AgentToolSetMark,
    instructions,
    toolset_collection,
)
from harness.installation.files import rules, skill
from harness.mcp.mcp_server import mcp
from harness.markdown import (
    AssetLocator,
    Markdown,
    MarkdownCollection,
    MarkdownText,
    markdown,
    markdownCollection,
)
from harness.markdown.format import Format


# Report names end with the time they were made, written so names sort by time.
REPORT_DATE_FORMAT = "%Y%m%dT%H%M%S"


class FidelityWithoutSessionError(ValueError):
    """A fidelity was asked where to save a report while its practice works in no session."""

    def __init__(self, slug: str) -> None:
        super().__init__(f"{slug} works in no session, so it has nowhere to save a validation report")


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
        return Name(self.domain_slug or type(self).__name__).kebab

    @property
    def install_folder(self) -> Path:
        return AssetLocator(self, "").class_file_directory()

    @property
    def module_dir(self) -> Path:
        try:
            return Path(inspect.getfile(type(self))).resolve().parent
        except (TypeError, OSError):
            return Path(".")

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
    @agent_instructions
    def sketch_template(self) -> str:
        """Sketch notation for this practice."""
        return self._sketch_template_text()

    def _sketch_template_text(self) -> str:
        folder = self._sketch_template_folder()
        if not folder.is_dir():
            return ""
        parts = [
            path.read_text(encoding="utf-8")
            for path in sorted(folder.glob("*-sketch.*"))
            if path.is_file()
        ]
        return "\n\n".join(part.strip() for part in parts if part.strip())

    def _sketch_template_folder(self) -> Path:
        practice = getattr(self, "practice_guidance", None)
        owner = practice if practice is not None else self
        return Path(inspect.getfile(type(owner))).resolve().parent / "templates"

    @property
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


@toolset_collection
class GuidanceCollection(MarkdownCollection, Guidance):
    def __init__(self, entries: dict[str, Guidance] | None = None, parent: Any = None) -> None:
        MarkdownCollection.__init__(self, entries, parent=parent)
        Guidance.__init__(self)
        self.current: Guidance | None = None

    def child_for_stage(self, stage: str) -> Guidance:
        values = self.entries.values() if isinstance(self.entries, dict) else self.entries
        for child in values:
            if getattr(child, "stage", "") == stage:
                return child
        raise KeyError(stage)

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
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str: ...


class PracticeGuidance(Guidance):
    sketch_titles: tuple[str, ...] = ()
    """The headings that open this practice's section of a sketch, lower case, such as `stories:`."""

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
        self._attach_workspace()
        self._activate(fidelity=fidelity)

    @markdownCollection("shared rules")
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    @property
    def key(self) -> str:
        """The practice's folder name, such as `clean_engineering`: how session log action lines and session.json name
        the practice."""
        return Path(inspect.getfile(type(self))).parent.name

    session_output: Any = None
    """What this practice has in the session it works in (a PracticeSessionOutput): its root, the folders it reads,
    and its saved formats; none until a session works on it. Each fidelity asks it for its outputs and files."""

    def files(self) -> dict[str, dict[str, list]]:
        """The files each fidelity of this practice declares in the session it works in, by fidelity name and then
        format."""
        fidelities = getattr(self, "fidelities", None) or []
        return {fidelity.name: fidelity.files() for fidelity in fidelities}

    def output_paths(self) -> dict[str, list[str]]:
        """Where the current fidelity writes each format in the session this practice works in; none when it has no
        current fidelity."""
        current = getattr(getattr(self, "fidelities", None), "current", None)
        return current.output_paths() if current is not None else {}

    @property
    def context_index_key(self) -> str:
        return AssetLocator(self, "").class_file_directory().name

    def project_rules(self, root=None) -> list:
        """Custom rulesets from the working folder, tagged project."""
        from harness.guidance.project_rules import load_project_rules

        folder = self._working_folder(root)
        if folder is None:
            return []
        fidelities = getattr(self, "fidelities", None)
        names = list(getattr(fidelities, "entries", {}) or {})
        return load_project_rules(folder, self.context_index_key, names)

    def _working_folder(self, root=None) -> Path | None:
        workspace = getattr(self, "workspace", None)
        candidates = (
            root,
            getattr(workspace, "path", None) if workspace is not None else None,
            getattr(self, "path", None),
        )
        for candidate in candidates:
            if candidate is None:
                continue
            text = str(candidate).strip()
            if not text or text == ".":
                continue
            return Path(text)
        return None

    @property
    def supported_formats(self) -> frozenset:
        own = dict(getattr(self, "_formats", None) or {})
        if own:
            return frozenset(own)
        return frozenset()
    
    ## workspace integration to move

    def _activate(self, fidelity: str | None = None, stage: str | None = None) -> None:
        if getattr(self, "_activating", False):
            return
        self._activating = True
        try:
            self._activate_fidelity(fidelity, stage)
        finally:
            self._activating = False

    def _activate_fidelity(self, fidelity: str | None, stage: str | None) -> None:
        if stage is not None:
            child = self.fidelities.child_for_stage(stage)
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
            self.format = Format(self.format).name
        supported = self.supported_formats
        if not supported and not getattr(self, "_formats", None) and self.format:
            allowed = {
                Format(child.default_format).name
                for child in self.fidelities.entries.values()
                if getattr(child, "default_format", None)
            }
            supported = frozenset(allowed)
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
    def active_session(self) -> str | None:
        """Session name bound on this guidance, when one was given."""
        return self.session

    @agent_instructions
    def generate_output(self) -> str:
        """Write this practice's artifact for the current fidelity.

        Override when the practice owns generation (for example drawio render).
        The default is instruction-only: generate already expanded instructions;
        the agent writes under the session path.
        """
        return ""

    @property
    def clean_engineering_companion(self) -> FidelityGuidance | None:
        companion = getattr(self.fidelities.current, "clean_engineering", None)
        return companion if isinstance(companion, FidelityGuidance) else None

    @property
    @agent_instructions
    def guidance(self) -> str:
        examples = str(self.examples or "").strip()
        templates = str(self.templates or "").strip()
        scoped = self.scoped_markdown().strip()
        if scoped:
            instructions(scoped)
        if examples:
            instructions(examples)
        if templates:
            instructions(templates)
        return "\n\n".join(part for part in self._guidance_parts() if part)

    def _guidance_parts(self) -> list[str]:
        parts = [Markdown.from_label(self, "guidance").extract().strip()]
        current = self.fidelities.current
        if current is not None:
            parts.append(Markdown.from_label(current, "guidance").extract().strip())
        companion = self.clean_engineering_companion
        extra = companion.instructions if companion is not None else ""
        if isinstance(extra, str):
            parts.append(extra.strip())
        return parts


    @property
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
        parent_text = Guidance.instructions.fget(self)
        extra = self.fidelities.instructions if self.fidelities.entries else ""
        return "\n\n".join(
            part
            for part in (self.schema_guide(), parent_text, extra, self.scoped_markdown())
            if part
        )

    @property
    def schema(self) -> str:
        """The practice schema at ``{practice}/model/schema.yaml``."""
        path = AssetLocator(self, "").class_file_directory() / "model" / "schema.yaml"
        if not path.is_file():
            return ""
        return path.read_text(encoding="utf-8").strip()

    def schema_guide(self) -> str:
        """Tell an action to conform its output to this practice schema."""
        body = (self.schema or "").strip()
        if not body:
            return ""
        return (
            "Guide this action so the output conforms to this schema.\n\n"
            f"{body}"
        )

    def schema_node_fidelities(self) -> dict[str, str]:
        """Each schema node type mapped to a fidelity name from ``model/schema.yaml``."""
        from harness.guidance.schema_map import node_fidelities

        return node_fidelities(self.schema)


    @toolset_collection
    @markdownCollection
    def fidelities(self) -> GuidanceCollection:
        """Fidelity children from the Fidelities section."""

    def domain_markdown_path(self) -> Path:
        class_dir = AssetLocator(self, "").class_file_directory()
        return class_dir / f"{class_dir.name}.md"

    @markdown
    def examples(self) -> str:
        """Examples folder content — not part of instructions."""

    ## format integration 


    @property
    def formats(self) -> dict[str, Any]:
        return dict(self._formats)

    def _format_adapter(self, format_name: str) -> Any:
        adapters = self.formats
        resolved = Format(format_name).name
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


    def read_paths(self, paths: list[str] | str, source: str | None = None) -> Any:
        """What render converts from the files at paths: their text, one after another."""
        from harness.guidance_actions.guidance_actions import load_document

        return load_document("", paths)

    @agent_tool
    def render(
        self,
        format: str,
        content: Any = "",
        source: str | None = None,
        previous: str = "",
        keep_positioning: bool = False,
        workspace: str = "",
    ) -> dict:
        """Turn content into the practice object model, then render the target format.
        workspace: the folder the rendered file sits in; a renderer that links to files finds them there."""
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
                workspace=workspace,
            )
        model = self._to_object_model(content, source)
        target = self._live_adapter(format)
        sketch_previous = previous
        if (source or "").lower() == "sketch" and isinstance(content, str) and content.strip():
            sketch_previous = previous or content
        rendered = self._call_render(target, model, sketch_previous, keep_positioning, workspace)
        return {"format": format, "content": rendered}

    def _to_object_model(self, content: Any, source: str | None) -> Any:
        if self._is_object_model(content):
            return content
        if self._is_tool(content):
            return self._instantiate_from_tool(content, source)
        source_format = Format(source or self.format).name
        if not source_format:
            raise ValueError("source format is not set")
        if Format(source_format).is_code and content in ("", None):
            return self._instantiate_from_tool(self, source_format)
        return self._parse_content(source_format, content)

    def _is_object_model(self, content: Any) -> bool:
        if isinstance(content, (str, bytes, dict, list)) or content is None:
            return False
        return callable(getattr(content, "semantic_type", None))

    def _is_tool(self, content: Any) -> bool:
        if self._is_object_model(content):
            return False
        return AgentToolSetMark.marks(type(content))

    def _instantiate_from_tool(self, tool: Any, source: str | None) -> Any:
        source_format = Format(source or getattr(tool, "format", None) or self.format).name
        if Format(source_format).is_code:
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

    def _call_render(
        self, target: Any, parsed: Any, previous: str, keep_positioning: bool, workspace: str = ""
    ) -> Any:
        try:
            parameters = inspect.signature(target.render).parameters
        except (TypeError, ValueError):
            return target.render(parsed)
        kwargs: dict[str, Any] = {}
        if "previous" in parameters:
            kwargs["previous"] = previous or None
        if "keep_positioning" in parameters:
            kwargs["keep_positioning"] = keep_positioning
        if workspace and "workspace" in parameters:
            kwargs["workspace"] = workspace
        return target.render(parsed, **kwargs)

    def _live_adapter(self, format_name: str) -> Any:
        adapter = self._format_adapter(format_name)
        if not inspect.isclass(adapter):
            return adapter
        create = getattr(adapter, "create", None)
        if callable(create):
            try:
                return create()
            except TypeError:
                pass
        try:
            return adapter(tests_root=self.default_workspace_folder)
        except TypeError:
            try:
                return adapter()
            except TypeError:
                return adapter

    def _incoming(self, format_name: str, content: Any) -> Any:
        if Format(format_name).is_code:
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
            current = self.fidelities.current
            current_name = current.name if current is not None else None
            for name, body in Markdown.from_label(self, "fidelities").fidelity_blocks(
                md_path.read_text(encoding="utf-8")
            ):
                if self._skip_inactive_fidelity(current_name, name):
                    continue
                parts.append(f"### {name}\n\n{body}")
        return "\n\n".join(part for part in parts if part.strip())

    def _skip_inactive_fidelity(self, current_name: str | None, name: str) -> bool:
        if not current_name:
            return False
        return Name(current_name).snake != Name(name).snake


@agent_toolset
class FidelityGuidance(Guidance):
    def __init__(
        self,
        name: str = "",
        stage: str = "",
        default_format: str = "",
        clean_engineering: FidelityGuidance | None = None,
    ) -> None:
        super().__init__(format=default_format)
        self.name = name
        self.stage = stage
        self.default_format = default_format
        # The root folder and each format's file, pattern, or folder; the yaml binder fills it, as it does stage.
        self.outputs: dict[str, str | list[str]] = {}
        if clean_engineering is not None:
            self.clean_engineering = clean_engineering

    def output_paths(self) -> dict[str, list[str]]:
        """Where this fidelity writes each format in the session its practice works in: its declared paths under the
        practice's root there. None when its practice works in no session."""
        output = self._session_output
        return output.output_paths_of(self) if output is not None else {}

    def files(self) -> dict[str, list]:
        """The files this fidelity declares, by format, in the session its practice works in, each with its path from
        the project and whether it exists; none when its practice works in no session."""
        output = self._session_output
        return output.files_of(self) if output is not None else {}

    def has_declared_output(self) -> bool:
        """Whether a file this fidelity declares is already in the session its practice works in, such as one a person
        wrote; false when its practice works in no session."""
        output = self._session_output
        return output is not None and output.has_output_of(self)

    @property
    def _session_output(self) -> Any:
        return getattr(self.practice_guidance, "session_output", None)

    def reports(self) -> list[Path]:
        """This fidelity's validation reports in the session its practice works in, oldest first; report names end with
        their date, which sorts by time. None when its practice works in no session."""
        folder = self._reports_folder
        return sorted(folder.glob(f"{self.slug}-*.md")) if folder is not None and folder.is_dir() else []

    def new_report_path(self) -> Path:
        """Where a validation report of this fidelity made now is saved, in the session its practice works in."""
        folder = self._reports_folder
        if folder is None:
            raise FidelityWithoutSessionError(self.slug)
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{self.slug}-{datetime.now(timezone.utc).strftime(REPORT_DATE_FORMAT)}.md"

    @property
    def _reports_folder(self) -> Path | None:
        session = getattr(self.practice_guidance, "workspace", None)
        return getattr(session, "reports_folder", None)

    @property
    def practice_guidance(self) -> PracticeGuidance | None:
        parent = getattr(self, "parent", None)
        while parent is not None and not isinstance(parent, PracticeGuidance):
            parent = getattr(parent, "parent", None)
        return parent

    @property
    def context_index_key(self) -> str:
        practice = self.practice_guidance
        if practice is not None:
            return practice.context_index_key
        return AssetLocator(self, "").class_file_directory().name

    @property
    def default_format(self) -> str:
        return getattr(self, "_default_format", "")

    @default_format.setter
    def default_format(self, value: str) -> None:
        self._default_format = value or ""
        if self._default_format:
            self.format = self._default_format

    @property
    def default_output(self) -> str | list[str]:
        """The output of this fidelity's default format."""
        return self.outputs.get(self.default_format, "")

    @property
    def clean_engineering(self) -> FidelityGuidance | None:
        stored = getattr(self, "_clean_engineering", None)
        if isinstance(stored, FidelityGuidance):
            return stored
        if not isinstance(stored, str) or not stored:
            return None
        from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

        companion = CleanEngineering().fidelities[stored]
        host = self.practice_guidance
        practice = companion.practice_guidance
        if (
            host is not None
            and practice is not None
            and Format(host.format).is_code
        ):
            practice.format = host.format
        self._clean_engineering = companion
        return companion

    @clean_engineering.setter
    def clean_engineering(self, value: Any) -> None:
        self._clean_engineering = value

    @property
    def slug(self) -> str:
        parent = self.practice_guidance.slug if self.practice_guidance is not None else super().slug
        leaf = Name(self.name).kebab
        return f"{parent}-{leaf}" if leaf else parent

    @property
    def install_folder(self) -> Path:
        practice = self.practice_guidance
        base = practice.install_folder if practice is not None else AssetLocator(self, "").class_file_directory()
        leaf = (self.name or "").replace(" ", "-")
        return base / leaf if leaf else base

    @property
    def overview(self) -> str:  # type: ignore[override]
        return Markdown.from_label(self, "overview").extract()

    @property
    def scaffold(self) -> str:
        """This fidelity's Scaffold subsection: the names a first cut writes, which are what a partition index lists;
        empty when the fidelity has none."""
        return Markdown.from_label(self, "scaffold").extract().strip()

    @property
    def section(self) -> str:
        """This fidelity's whole ``### {name}`` block in its practice's markdown: overview, sketch, guidance, and rules."""
        practice = self.practice_guidance
        if practice is None:
            return ""
        path = practice.domain_markdown_path()
        if not path.is_file():
            return ""
        return MarkdownText(path.read_text(encoding="utf-8")).fidelity_block(self.name)

    @markdown
    def guidance(self) -> str:
        """Fidelity guidance section."""

    @markdownCollection
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Fidelity rules section."""

    @property
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
            templates = Markdown.from_label(
                practice, "templates", fidelity=self.name, format=self.format or self.default_format
            ).extract().strip()
            if templates:
                templates = f"#### Template\n\n{templates}"
        schema = practice.schema_guide() if practice is not None else ""
        return "\n\n".join(
            part
            for part in (
                schema,
                *parent,
                (self.overview or "").strip(),
                (self.guidance or "").strip(),
                (self.rules.markdown or "").strip(),
                templates,
                companion_text,
            )
            if part
        )
