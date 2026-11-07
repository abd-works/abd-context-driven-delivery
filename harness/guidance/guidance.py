"""Assemble agent instructions from @markdown properties."""
from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness.name.name import Name
from harness.guidance.documents import load_document
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.guidance.rule import RulesCollection
from harness.guidance.schema import Schema
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
from harness.installation.destination import data_field
from harness.hooks.hooks import Hook
from harness.mcp.mcp_server import mcp
from harness.markdown import (
    Markdown,
    MarkdownCollection,
    MarkdownText,
    markdown,
    markdownCollection,
)
from harness.markdown.format import Format


# Report names end with the time they were made, written so names sort by time.
REPORT_DATE_FORMAT = "%Y%m%dT%H%M%S"


@dataclass(frozen=True)
class RenderRequest:
    """One render: the format to write, the content to render and the format it is in, the target file as it is now,
    and the folder the files it links to are in."""

    format: str
    content: Any = ""
    source: str | None = None
    previous: str = ""
    folder: str = ""


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
        return self.module_dir

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

    session: Any = None
    """The Session this guidance works in, which its work_in gives it; none until a session works on it."""

    def __init__(self, format: str | None = None) -> None:
        self.format = format if format is not None else self.default_format

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

    def rules_after_edit(self, payload: Any) -> str:
        """The rules an action hands the agent after the edit payload's hook names: the rules that apply to the edited
        file, else all of them; none while this guidance's rules hook is turned off."""
        rules = self.rules
        if rules is None or Hook.disabled_on(rules.inject_rules):
            return ""
        applied = (rules.inject_rules(payload).get("additional_context") or "").strip()
        return applied or (rules.markdown or "").strip()

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
    SHORT_NAME: str = ""
    """The practice's name where there is little room, such as `CE` on a session board's chip."""
    COLOUR: str = ""
    """The colour a session board draws the practice's chips and tiles in, such as `#6BCB77` for Stories."""

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
        self._activate(fidelity=fidelity)

    @markdownCollection("shared rules")
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    @property
    @data_field
    def key(self) -> str:
        """The practice's folder name, such as `clean_engineering`: how session log action lines and session.json name
        the practice."""
        return Path(inspect.getfile(type(self))).parent.name

    @property
    @data_field(key="slug")
    def practice_slug(self) -> str:
        """The practice's slug, such as `clean-engineering`, which each of its fidelities' slugs begins with."""
        return self.slug

    @property
    @data_field
    def short_name(self) -> str:
        return type(self).SHORT_NAME or type(self).__name__

    @property
    @data_field
    def colour(self) -> str:
        return type(self).COLOUR

    @property
    @data_field(key="fidelities")
    def fidelity_slugs(self) -> list[str]:
        """The slug of each of the practice's fidelities, such as `stories-story-map`, so a reader holding a fidelity's
        slug finds its practice without taking the slug apart."""
        return [fidelity.slug for fidelity in self.fidelities]

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
        return self.module_dir.name

    def project_rules(self) -> list:
        """The custom rules the project keeps for this practice in `.context/rules/{practice}/rules.md`, and for a
        fidelity in a folder named after it, each tagged project; none when the practice works in no folder."""
        from harness.guidance.project_rules import ProjectRulesets

        folder = self._working_folder()
        if folder is None or not folder.is_dir():
            return []
        rules: list = []
        seen: set[Path] = set()
        for rules_dir in ProjectRulesets(folder).folders_for(self.context_index_key):
            rules.extend(self._project_rules_in(rules_dir / "rules.md", None, seen))
            for fidelity in self.fidelities.entries:
                for spelling in Name(fidelity).spellings:
                    rules.extend(self._project_rules_in(rules_dir / spelling / "rules.md", fidelity, seen))
        return rules

    def _project_rules_in(self, path: Path, fidelity: str | None, seen: set[Path]) -> list:
        """The rules in one project rules file, once each however many spellings lead to it."""
        if not path.is_file() or path.resolve() in seen:
            return []
        seen.add(path.resolve())
        collection = RulesCollection.from_markdown(path.read_text(encoding="utf-8"), fidelity=fidelity)
        return [
            rule.attribute_to(self.context_index_key, tag="project", shared=fidelity is None) for rule in collection
        ]

    def _working_folder(self) -> Path | None:
        """The folder the session this practice works in works in; none while it works in no session."""
        return self.session.root if self.session is not None else None

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
            self._make_current(fidelity)
        if self.format:
            self.format = Format(self.format).name
        self._check_format()

    def _make_current(self, fidelity: str) -> None:
        """Make fidelity current; the practice takes its default format when it works in none yet."""
        entries = self.fidelities.entries
        if entries and fidelity not in entries:
            raise ValueError(f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(entries)}")
        if fidelity not in entries:
            return
        if not self.format and entries[fidelity].default_format:
            self.format = entries[fidelity].default_format
        self.fidelities.current = entries[fidelity]

    def _check_format(self) -> None:
        """Raise ValueError for a format the practice does not write: one its adapters do not read, or, for a practice
        with no adapters, one no fidelity names as its default."""
        supported = self.supported_formats
        if not supported and not getattr(self, "_formats", None) and self.format:
            supported = frozenset(
                Format(child.default_format).name for child in self.fidelities.entries.values() if getattr(child, "default_format", None)
            )
        if supported and self.format and self.format not in supported:
            raise ValueError(f"Unsupported format {self.format!r}. Choose from: {sorted(supported)}")

    def work_in(self, session_output: Any) -> None:
        """Work in the session that session_output, this practice's PracticeSessionOutput, belongs to: the practice
        knows that session, and each of its fidelities is given what it has there, so it answers its outputs and files
        itself."""
        self.session = session_output.session
        for fidelity in self.fidelities:
            fidelity.work_in(session_output.of_fidelity(fidelity))

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
        path = self.module_dir / "model" / "schema.yaml"
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

    def schema_node_fidelities(self) -> dict[str, list[str]]:
        """Each node type of the practice schema with the fidelity that creates it and every higher fidelity: a node a
        low fidelity creates also belongs to the higher ones, which build it out rather than replace it."""
        order = [fidelity.name for fidelity in self.fidelities]
        created = Schema(self.schema).fidelities()
        return {node: order[order.index(fidelity):] for node, fidelity in created.items() if fidelity in order}

    def schema_fidelity_errors(self) -> list[str]:
        """What is wrong between the practice schema and the practice's fidelities: a schema with no node fidelity, or a
        node fidelity that is not one of the practice's. Empty when they agree."""
        created = Schema(self.schema).fidelities()
        if not created:
            return ["schema defines no node fidelity entries"]
        declared = sorted(fidelity.name for fidelity in self.fidelities)
        return [
            f"{node} maps to fidelity {fidelity!r}, which is not under ## Fidelities (have {declared!r})"
            for node, fidelity in sorted(created.items()) if fidelity not in declared
        ]


    @toolset_collection
    @markdownCollection
    def fidelities(self) -> GuidanceCollection:
        """Fidelity children from the Fidelities section."""

    def domain_markdown_path(self) -> Path:
        class_dir = self.module_dir
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
        return load_document("", paths)

    @agent_tool
    def render(self, format: str, content: Any = "", source: str | None = None, previous: str = "") -> dict:
        """Turn content into the practice object model, then render the target format. Content is in source, the
        format this practice works in when none is named; previous is the target file as it is now."""
        return self._render(RenderRequest(format, content, source, previous))

    def render_files(self, format: str, paths: list[str] | str, source: str | None = None) -> dict:
        """Render the files at paths into format. A renderer that links to other files, such as a story map linking
        to each story's file, finds them in the folder the first path is, or sits in."""
        content = self.read_paths(paths, source)
        return self._render(RenderRequest(format, self if content in ("", None) else content, source, "", _folder_of(paths)))

    def _render(self, request: RenderRequest) -> dict:
        """The target format of one call is the call's: practices are shared between callers, so the format a practice
        works in stays as it is and the render request carries the one it writes."""
        if not self.formats:
            companion = self.clean_engineering_companion
            owner = companion.practice_guidance if companion is not None else None
            if owner is None or owner is self:
                return {"format": request.source or self.format or request.format, "content": request.content}
            return owner._render(request)
        model = self._to_object_model(request.content, request.source)
        target = self._live_adapter(request.format)
        rendered = self._call_render(target, self._model_for(target, model), self._kept_wording(request))
        return {"format": request.format, "content": rendered}

    def _kept_wording(self, request: RenderRequest) -> RenderRequest:
        """A sketch rendered to a document format keeps the sketch's own wording; code is never read from a sketch."""
        content = request.content
        from_sketch = (request.source or "").lower() == "sketch" and isinstance(content, str) and content.strip()
        if not from_sketch or Format(request.format).is_code:
            return request
        return replace(request, previous=request.previous or content)

    def _model_for(self, target: Any, model: Any) -> Any:
        """The object model in the form target renders; a practice whose formats read another practice's model
        converts it here."""
        return model

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
        """The folder tool's code is read from: the root of the session it works in."""
        session = getattr(tool, "session", None)
        return session.root if session is not None else Path(".")

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

    def _call_render(self, target: Any, parsed: Any, request: RenderRequest) -> Any:
        """Ask target to render parsed, giving it the previous file and the linked files' folder when it takes them."""
        try:
            parameters = inspect.signature(target.render).parameters
        except (TypeError, ValueError):
            return target.render(parsed)
        kwargs: dict[str, Any] = {}
        if "previous" in parameters:
            kwargs["previous"] = request.previous or None
        if request.folder and "workspace" in parameters:
            kwargs["workspace"] = request.folder
        return target.render(parsed, **kwargs)

    def _live_adapter(self, format_name: str) -> Any:
        """The format's adapter, made the way its class says: through its own ``create``, with the folder tests are
        written under when its constructor takes ``tests_root``, or bare. An adapter whose constructor needs more is
        used as its class, whose operations read and write the format."""
        adapter = self._format_adapter(format_name)
        if not inspect.isclass(adapter):
            return adapter
        create = getattr(adapter, "create", None)
        if callable(create) and self._takes_no_arguments(create):
            return create()
        parameters = inspect.signature(adapter).parameters
        if "tests_root" in parameters:
            return adapter(tests_root=self.default_workspace_folder)
        return adapter() if self._takes_no_arguments(adapter) else adapter

    def _takes_no_arguments(self, operation: Any) -> bool:
        required = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        return all(
            parameter.default is not inspect.Parameter.empty or parameter.kind not in required
            for parameter in inspect.signature(operation).parameters.values()
        )

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
            for name, body in MarkdownText(md_path.read_text(encoding="utf-8")).fidelity_blocks():
                if self._skip_inactive_fidelity(current_name, name):
                    continue
                parts.append(f"### {name}\n\n{body}")
        return "\n\n".join(part for part in parts if part.strip())

    def _skip_inactive_fidelity(self, current_name: str | None, name: str) -> bool:
        if not current_name:
            return False
        return Name(current_name).snake != Name(name).snake


def _folder_of(paths: list[str] | str) -> str:
    """The folder the files at paths sit in: the first path when it is a folder, else its parent."""
    first = paths[0] if isinstance(paths, (list, tuple)) and paths else paths
    if not first or not isinstance(first, str):
        return ""
    path = Path(first)
    if path.is_dir():
        return str(path)
    return str(path.parent) if path.parent.is_dir() else ""


@agent_toolset
class FidelityGuidance(Guidance):
    companion_of: FidelityGuidance | None = None
    """The fidelity this one is the Clean Engineering companion of, such as Stories' acceptance_tests for code; none
    for a fidelity of its own practice."""
    session_output: Any = None
    """What this fidelity has in the session its practice works in (a FidelitySessionOutput): where it writes each
    format, the files it declares there, and its reports folder; none until a session works on its practice."""

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
        self.outputs = {}
        if clean_engineering is not None:
            self.clean_engineering = clean_engineering

    @property
    @data_field
    def name(self) -> str:
        """The fidelity's name in its practice, such as `story_map`."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value or ""

    @property
    @data_field
    def outputs(self) -> dict[str, str | list[str]]:
        """Each format this fidelity writes, with its file, pattern, or folder; the fidelity's YAML fields fill it, as they
        do stage."""
        return dict(self._outputs)

    @outputs.setter
    def outputs(self, value: dict[str, str | list[str]]) -> None:
        self._outputs = dict(value or {})

    def work_in(self, session_output: Any) -> None:
        """Work in a session through session_output, the FidelitySessionOutput holding what this fidelity has there."""
        self.session_output = session_output

    def output_paths(self) -> dict[str, list[str]]:
        """Where this fidelity writes each format in the session its practice works in: its declared paths under the
        practice's root there. None when its practice works in no session."""
        return self.session_output.output_paths() if self.session_output is not None else {}

    def files(self) -> dict[str, list]:
        """The files this fidelity declares, by format, in the session its practice works in, each with its path from
        the project and whether it exists; none when its practice works in no session."""
        return self.session_output.files() if self.session_output is not None else {}

    def has_declared_output(self) -> bool:
        """Whether a file this fidelity declares is already in the session its practice works in, such as one a person
        wrote; false when its practice works in no session."""
        return self.session_output is not None and self.session_output.has_output()

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
        return self.session_output.reports_folder if self.session_output is not None else None

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
        return self.module_dir.name

    @property
    def format(self) -> str | None:
        """The format this fidelity works in. A Clean Engineering companion writes the code of the fidelity it is the
        companion of, so while that fidelity's practice works in a code format the companion works in it too, read when
        asked so it follows that practice."""
        served = self.companion_of.practice_guidance if self.companion_of is not None else None
        if served is not None and Format(served.format).is_code:
            return served.format
        return getattr(self, "_format", None)

    @format.setter
    def format(self, value: str | None) -> None:
        self._format = value

    @property
    @data_field
    def default_format(self) -> str:
        return getattr(self, "_default_format", "")

    @default_format.setter
    def default_format(self, value: str) -> None:
        """value as a practice document writes it, such as ``markdown (md)``: its first word, as the format's name."""
        self._default_format = Format(self._first_word(value)).name if value else ""
        if self._default_format:
            self.format = self._default_format

    def _first_word(self, value: str) -> str:
        return value.split()[0].strip("()`") if value.strip() else ""

    @property
    def default_output(self) -> str | list[str]:
        """The output of this fidelity's default format."""
        return self.outputs.get(self.default_format, "")

    @property
    def clean_engineering(self) -> FidelityGuidance | None:
        """The Clean Engineering fidelity this fidelity's `clean_engineering:` field names, whose instructions join
        this fidelity's. It knows this fidelity as the one it is the companion of and reads the code format from it."""
        stored = getattr(self, "_clean_engineering", None)
        if isinstance(stored, FidelityGuidance):
            return stored
        if not isinstance(stored, str) or not stored:
            return None
        # A companion of its own, since it knows this fidelity as the one it accompanies.
        companion = PracticeCatalogue.create("clean_engineering").fidelities[stored]
        companion.companion_of = self
        self._clean_engineering = companion
        return companion

    @clean_engineering.setter
    def clean_engineering(self, value: FidelityGuidance | str | None) -> None:
        """A companion fidelity, or its name as a practice document writes it, such as ``code (Clean Engineering)``."""
        self._clean_engineering = Name(self._first_word(value)).snake if isinstance(value, str) else value

    @property
    @data_field
    def slug(self) -> str:
        parent = self.practice_guidance.slug if self.practice_guidance is not None else super().slug
        leaf = Name(self.name).kebab
        return f"{parent}-{leaf}" if leaf else parent

    @property
    def install_folder(self) -> Path:
        practice = self.practice_guidance
        base = practice.install_folder if practice is not None else self.module_dir
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
            templates = self._template(practice)
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

    def _template(self, practice: PracticeGuidance) -> str:
        """This fidelity's template in the format it works in, else in its default format: a companion writing
        TypeScript still shows Clean Engineering's reference template when no TypeScript one exists."""
        formats = [spelling for spelling in dict.fromkeys((self.format, self.default_format)) if spelling] or [""]
        for format in formats:
            found = Markdown.from_label(practice, "templates", fidelity=self.name, format=format).extract().strip()
            if found:
                return found
        return ""
