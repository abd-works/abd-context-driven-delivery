"""Assemble agent instructions from @markdown properties."""
from __future__ import annotations

import functools
import importlib
import inspect
import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar

from harness.annotations.annotation import hosted_only
from harness.annotations.name import Name
from harness.guidance.action_catalogue import FidelityActions
from harness.guidance.declared_file import DeclaredFile
from harness.guidance.documents import load_document
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.guidance.rule import Rule, RulesCollection
from harness.guidance.schema import Schema
from harness.guidance.sketch_lens import SketchLens
from harness.guidance.stages import STAGES, ApproachStage
from harness.agent_tools.agent_tools import (
    collect,
    agent_instructions,
    agent_tool,
    agent_toolset,
    AgentToolSetAnnotation,
    instructions,
    toolset_collection,
)
from harness.installation.files import rules, skill
from harness.installation.destination import data_field, identity
from harness.hooks.hooks import Hook
from harness.mcp.mcp_server import mcp
from harness.markdown import (
    Markdown,
    MarkdownCollection,
    MarkdownScope,
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


def rules_in(module_path: str) -> dict[str, Any]:
    """The graph rules a rules module lists, by slug: its ``BY_SLUG``, else each of its ``RULES``. A module that is not
    there has none."""
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as missing:
        if missing.name and module_path.startswith(missing.name):
            return {}
        raise
    by_slug = getattr(module, "BY_SLUG", None)
    if isinstance(by_slug, dict):
        return dict(by_slug)
    return {rule.slug: rule for rule in getattr(module, "RULES", ()) if getattr(rule, "slug", "")}


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

    @functools.cached_property
    def _own_name(self) -> Name:
        """The guidance's name, made once from its declared slug or its class."""
        return Name(self.domain_slug or type(self).__name__)

    @property
    def slug(self) -> str:
        return self._own_name.kebab

    @property
    def install_folder(self) -> Path:
        return self.module_dir

    @property
    def module_dir(self) -> Path:
        try:
            return Path(inspect.getfile(type(self))).resolve().parent
        except (TypeError, OSError):
            return Path(".")

    @property
    def markdown_scope(self) -> MarkdownScope:
        """Where this guidance's markdown lives, handed to each Markdown it reads: the folder beside its class, its
        ``{slug}.md``, and the format it works in."""
        folder = self.module_dir
        return MarkdownScope(folder, self.domain_slug or folder.name, format=self.format or None)

    def _section(self, label: str) -> Markdown:
        """The Markdown of one of its own labelled sections, made once and kept, so a second read answers from the
        text the first read found."""
        held = vars(self).setdefault("_held_sections", {})
        if label not in held:
            held[label] = Markdown.from_label(self, label)
        return held[label]

    @markdownCollection("shared rules")
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    session: Any = None
    """The Session this guidance works in, which its work_in gives it; none until a session works on it."""

    def __init__(self, format: str | None = None) -> None:
        self.format = format if format is not None else self.default_format

    @property
    @data_field
    def overview(self) -> str:
        """Its Overview section: what this guidance is for, which a person reads on its help."""
        return self._section("overview").extract()

    @property
    @data_field
    def guidance(self) -> str:
        """Its Guidance section: how to do the work well, which a person reads on its help."""
        return self._section("guidance").extract()

    @property
    @data_field(key="rules")
    def listed_rules(self) -> list[Rule]:
        """Its rules one by one, as its help lists them: a practice's shared rules, or a fidelity's own."""
        return list(self.rules)

    def checked_rule_collections(self) -> list[RulesCollection]:
        """The rule collections a validate of this guidance checks: its own rules."""
        return [self.rules] if self.rules is not None else []

    def checked_rules(self) -> list[Rule]:
        """The rules a validate of this guidance checks, one by one."""
        return [rule for collection in self.checked_rule_collections() for rule in collection]

    def every_rule(self) -> list[Rule]:
        """Every rule this guidance holds, which a report describes beside a saved graph's hits."""
        return list(self.rules or ())

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


@hosted_only
@toolset_collection
class GuidanceCollection(MarkdownCollection, Guidance):
    def __init__(self, entries: dict[str, Guidance] | None = None, parent: Any = None) -> None:
        MarkdownCollection.__init__(self, entries, parent=parent)
        Guidance.__init__(self)
        self.current: Guidance | None = None

    def at_stage(self, stage: ApproachStage | None) -> FidelityGuidance:
        """The fidelity that holds stage as the stage it is in; KeyError when none does."""
        found = next((fidelity for fidelity in self if fidelity.approach_stage is stage and stage is not None), None)
        if found is None:
            raise KeyError(stage.name if stage is not None else stage)
        return found

    @classmethod
    def child(cls, name: str, body: str = "") -> FidelityGuidance:
        """The fidelity a ``### name`` block of the practice document declares, with the settings its ```yaml block
        gives it."""
        fidelity = FidelityGuidance(name=name)
        fidelity.apply_settings(MarkdownText(body).yaml_fields)
        return fidelity

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


@hosted_only
@identity("key")
class PracticeGuidance(Guidance):
    sketch_titles: tuple[str, ...] = ()
    """The headings that open this practice's section of a sketch, lower case, such as `stories:`."""
    sketch_lens: ClassVar[SketchLens] = SketchLens(())
    """This practice's section of a sketch, made once from its ``sketch_titles`` when the practice class is made, so its
    sketch format and a sketch's reader hold it rather than naming the practice."""
    SHORT_NAME: str = ""
    """The practice's name where there is little room, such as `CE` on a session board's chip."""
    COLOUR: str = ""
    """The colour a session board draws the practice's chips and tiles in, such as `#6BCB77` for Stories."""
    shows_every_fidelity: bool = False
    """Whether scoped markdown shows every fidelity's block even when one is current, as DDD's does; otherwise it shows
    only the current fidelity's."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls.sketch_lens.titles != cls.sketch_titles:
            cls.sketch_lens = SketchLens(cls.sketch_titles)

    def __init__(
        self,
        format: str | None = None,
        fidelity: str | None = None,
        default_workspace_folder: str = ".",
        formats: dict[str, Any] | None = None,
    ) -> None:
        self._own_format: str | None = None
        super().__init__(format=format)
        self.default_workspace_folder = default_workspace_folder
        self._formats = dict(formats or {})
        self._activate(fidelity=fidelity)

    @property
    def format(self) -> str | None:
        """The format this practice works in: the format its current fidelity works in, which that fidelity holds; the
        practice's own while it has no current fidelity."""
        current = self._current_fidelity
        return current.format if current is not None else self._own_format

    @format.setter
    def format(self, value: str | None) -> None:
        """Work in value: its current fidelity keeps it, or the practice itself while it has none."""
        current = self._current_fidelity
        if current is not None:
            current.format = value
        else:
            self._own_format = value

    @property
    def _current_fidelity(self) -> FidelityGuidance | None:
        """The current fidelity, read without reading the fidelities from the practice's document when nothing has
        read them yet, since none can be current then."""
        fidelities = vars(self).get("fidelities")
        return getattr(fidelities, "current", None)

    @markdownCollection("shared rules")
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    @property
    def markdown_scope(self) -> MarkdownScope:
        """Where this practice's markdown lives, at its current fidelity and format, read without reading the
        fidelities from the practice's document when nothing has read them yet."""
        current = self._current_fidelity
        return replace(super().markdown_scope, fidelity=current.name if current is not None else None)

    @functools.cached_property
    def document(self) -> MarkdownText:
        """The practice's own document, ``{key}.md`` beside its class, read once: its sections and each fidelity's
        block are read from this text."""
        path = self.domain_markdown_path()
        return MarkdownText(path.read_text(encoding="utf-8") if path.is_file() else "")

    def checked_rule_collections(self) -> list[RulesCollection]:
        """The rule collections a validate of this practice checks: its current fidelity's, which start with the shared
        rules, or the shared rules and every fidelity's when it has no current one."""
        current = self.fidelities.current
        if current is not None:
            return current.checked_rule_collections()
        collections = [self.rules, *(fidelity.rules for fidelity in self.fidelities)]
        return list({id(collection): collection for collection in collections if collection is not None}.values())

    def every_rule(self) -> list[Rule]:
        """Its shared rules and every fidelity's: a saved graph holds the whole practice's hits, so each one's rule text
        is there to show beside it."""
        collections = (self.rules, *(fidelity.rules for fidelity in self.fidelities))
        return [rule for collection in collections if collection is not None for rule in collection]

    ## the knowledge graph
    # A practice takes part in the knowledge graph itself: it says which of its node types the graph treats as
    # classes, members, or source-ordered, reads its files into the graph, links its nodes to other practices', and
    # names the graph rules it checks. The graph names no practice, so these words live here, on the practice.

    graph: Any = None
    """The graph that holds this practice (harness/graph's *Graph*), which keeps the practice's nodes and edges; none for
    a practice no graph holds. A session's practices are held by the session's graph, so the practice an action works
    with is the one the graph reads."""

    extended: PracticeGuidance | None = None
    """The practice whose types this practice's schema builds on, which ``extends`` names, held by reference: the one of
    the same set of practices, such as the session's Clean Engineering for its DDD."""

    reads_after: tuple[str, ...] = ()
    """The practices whose nodes this one reads while it reads its own; the graph reads them first."""

    node_types: tuple[str, ...] = ()
    """Node types the graph explorer offers for this practice even before any node of them is read."""

    class_types: tuple[str, ...] = ()
    """Node types that are classes, which the source view opens a call into and folds in place."""

    member_types: tuple[str, ...] = ()
    """Node types that are a class's operations and properties, which the source view can open a call to."""

    class_node_type: str = ""
    """The node type this practice's checks run on as a whole class. Another practice's node that lies inside one of
    these classes skips this practice's checks, since they already ran on the class."""

    source_ordered_types: frozenset[str] = frozenset()
    """Node types the explorer lists in the order they appear in their files, not the order they were read."""

    extends: str = ""
    """The practice whose types this practice's schema builds on with ``is:``, such as a DDD entity that is a Clean
    Engineering class; its types also carry that practice's rules."""

    anchor_types: dict[str, str] = {}
    """The ``is:`` words another practice's schema uses to say one of its types is a type of this practice
    (``class`` for a Clean Engineering class), each with the node type it names."""

    rule_types: dict[str, tuple[str, ...]] = {}
    """Node types that also carry the rules the schema gives other types, such as every story node's rules on a story."""

    @property
    def package(self) -> str:
        """The Python package that holds this practice, such as ``cdd_guidance.practices.stories``; empty for a practice
        the catalogue does not hold."""
        return PracticeCatalogue.module_of(self.key) if PracticeCatalogue.has(self.key) else ""

    def align_node(self, node: Any) -> None:
        """Move node's source onto the lines that declare it, when this practice's reader found it by a nearby line."""

    def read_working_copy(self) -> None:
        """Read this practice's nodes and edges into its graph from the working copy that graph is loading."""

    def link_to_other_practices(self) -> None:
        """Record the edges between this practice's nodes and other practices' nodes in its graph, once every practice
        is read."""

    def graph_checks(self) -> dict[str, Any]:
        """Every graph rule (a *PracticeGraphRule*) this practice checks, by slug; read once."""
        found = getattr(self, "_graph_checks", None)
        if found is None:
            found = self._graph_checks = self.own_graph_checks()
        return found

    def own_graph_checks(self) -> dict[str, Any]:
        """The graph rules this practice's ``rules`` package lists; a practice that checks more overrides this."""
        return rules_in(f"{self.package}.rules") if self.package else {}

    def checks(self) -> dict[str, Any]:
        """The graph rules this practice checks, with those the pattern overlays its graph applies add to it, by slug."""
        merged = dict(self.graph_checks())
        if self.graph is not None:
            merged.update(self.graph.overlay_checks_of(self))
        return merged

    def language_checks(self, language: str) -> dict[str, Any]:
        """The graph rules this practice checks only on nodes read from a file in ``language``, such as ``drawio``."""
        return {}

    @property
    @data_field
    def key(self) -> str:
        """The practice's folder name, such as `clean_engineering`: how session log action lines and session.json name
        the practice."""
        return self.module_dir.name

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
    def supported_formats(self) -> frozenset:
        own = dict(getattr(self, "_formats", None) or {})
        if own:
            return frozenset(own)
        return frozenset()
    
    ## workspace integration to move

    def _activate(self, fidelity: str | None = None) -> None:
        if getattr(self, "_activating", False):
            return
        self._activating = True
        try:
            self._activate_fidelity(fidelity)
        finally:
            self._activating = False

    def _activate_fidelity(self, fidelity: str | None) -> None:
        if fidelity is not None:
            self._make_current(fidelity)
        if self.format:
            self.format = Format(self.format).name
        self._check_format()

    def _make_current(self, fidelity: str) -> None:
        """Make fidelity current. A format the practice was made with, before it had a current fidelity, is the one that
        fidelity works in; otherwise the fidelity keeps its own."""
        entries = self.fidelities.entries
        if entries and fidelity not in entries:
            raise ValueError(f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(entries)}")
        if fidelity not in entries:
            return
        if self._own_format:
            entries[fidelity].format = self._own_format
        self.fidelities.current = entries[fidelity]

    def work_at(self, fidelity: str) -> FidelityGuidance:
        """Work at fidelity, one of this practice's by name, from now on: it is the practice's current fidelity until
        another is worked at. The practice keeps it; nothing sets it back."""
        self._make_current(fidelity)
        return self.fidelities.current

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
    @data_field
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
        """The practice's own Guidance section, then its current fidelity's guidance and companion text, which that
        fidelity answers."""
        current = self.fidelities.current
        return [self._section("guidance").extract().strip(), *(current.guidance_parts() if current is not None else ())]


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

    @functools.cached_property
    def schema(self) -> str:
        """The practice schema at ``{practice}/model/schema.yaml``, read once."""
        path = self._schema_path
        return path.read_text(encoding="utf-8").strip() if path.is_file() else ""

    @property
    def _schema_path(self) -> Path:
        return self.module_dir / "model" / "schema.yaml"

    @functools.cached_property
    def schema_types(self) -> Schema:
        """The types the practice schema declares, read once for the process."""
        return Schema.load(self._schema_path)

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
        created = self.schema_types.fidelities()
        return {node: order[order.index(fidelity):] for node, fidelity in created.items() if fidelity in order}

    def schema_fidelity_errors(self) -> list[str]:
        """What is wrong between the practice schema and the practice's fidelities: a schema with no node fidelity, or a
        node fidelity that is not one of the practice's. Empty when they agree."""
        created = self.schema_types.fidelities()
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
            return getattr(importlib.import_module(module_path), attr)
        return entry

    def format_for(self, file: Path) -> Any:
        """A new model of the file's format: the one among this practice's formats whose adapter reads the file's
        extension, such as Python for ``cart_spec.py``. A format whose adapter names no ``suffixes`` reads no file by
        its extension. Raises ValueError when none of its formats reads it."""
        suffix = file.suffix.lower()
        for name in self.formats:
            adapter = self._format_adapter(name)
            if suffix in getattr(adapter, "suffixes", ()):
                return adapter()
        raise ValueError(f"No {type(self).__name__} format reads {file.name}")

    def read_paths(self, paths: list[str] | str, source: str | None = None) -> Any:
        """What render converts from the files at paths: their text, one after another, read from the project of the
        session this practice works in."""
        return self.session.document_named("", paths) if self.session is not None else load_document("", paths)

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
        return AgentToolSetAnnotation.annotates(type(content))

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
        """The format's adapter, made once on first use and kept by the format it reads and writes."""
        adapters = vars(self).setdefault("_live_adapters", {})
        name = Format(format_name).name
        if name not in adapters:
            adapters[name] = self._made_adapter(name)
        return adapters[name]

    def _made_adapter(self, format_name: str) -> Any:
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
        """Overview, practice sections, and the current fidelity's block, or every fidelity's when none is current."""
        parts = [self._section(label).extract() for label in ("overview", "guidance", "shared rules", "language")]
        current = self.fidelities.current
        current_name = current.name if current is not None else None
        shown = [fidelity for fidelity in self.fidelities if self.shows_every_fidelity or current_name in (None, fidelity.name)]
        parts.extend(fidelity.titled_section for fidelity in shown)
        return "\n\n".join(part for part in parts if part.strip())



def _folder_of(paths: list[str] | str) -> str:
    """The folder the files at paths sit in: the first path when it is a folder, else its parent."""
    first = paths[0] if isinstance(paths, (list, tuple)) and paths else paths
    if not first or not isinstance(first, str):
        return ""
    path = Path(first)
    if path.is_dir():
        return str(path)
    return str(path.parent) if path.parent.is_dir() else ""


@hosted_only
@identity("slug")
@agent_toolset
class FidelityGuidance(Guidance):
    companion_of: FidelityGuidance | None = None
    """The fidelity this one is the Clean Engineering companion of, such as Stories' acceptance_tests for code; none
    for a fidelity of its own practice."""
    session_output: Any = None
    """What this fidelity has in the session its practice works in (a FidelitySessionOutput): where it writes each
    format, the files it declares there, and its reports folder; none until a session works on its practice."""
    judged_on: str = "artifacts"
    """What a validate judges this fidelity's rules against, as its practice document's ``judged_on`` says: the
    ``artifacts`` it writes, read as text, or the ``graph`` validate builds from the code, where rules about the object
    model the code holds (one model, classes with one job, one-way dependencies) can be checked."""

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

    def apply_settings(self, settings: dict[str, Any]) -> None:
        """Take the settings its block's ```yaml gives it: the stage it is in, its default format, the files it writes
        in each format, its Clean Engineering companion, and what a validate judges it on. A setting it does not know
        is the reader's, such as a rules block's ``globs``, and stays unread here."""
        if "stage" in settings:
            self.stage = str(settings["stage"] or "")
        if "default_format" in settings:
            self.default_format = str(settings["default_format"] or "")
        if "outputs" in settings:
            self.outputs = settings["outputs"] if isinstance(settings["outputs"], dict) else {}
        if "clean_engineering" in settings:
            self.clean_engineering = str(settings["clean_engineering"] or "")
        if "judged_on" in settings:
            self.judged_on = str(settings["judged_on"] or "artifacts")

    @property
    def stage(self) -> str:
        """The stage this fidelity's **Stage:** names, such as `discovery`."""
        return self._stage

    @stage.setter
    def stage(self, value: str) -> None:
        """Name the stage this fidelity is in; the approach's stage of that name is held from now on."""
        self._stage = value or ""
        self._approach_stage = STAGES.of(self._stage)

    @property
    def approach_stage(self) -> ApproachStage | None:
        """The approach's stage this fidelity is in, held since its stage was named; none for a name that is no
        stage."""
        return self._approach_stage

    @property
    def is_judged_on_graph(self) -> bool:
        """Whether a validate judges this fidelity against the graph it builds from the code."""
        return self.judged_on == "graph"

    @property
    @data_field
    def name(self) -> str:
        """The fidelity's name in its practice, such as `story_map`."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value or ""
        vars(self).pop("_own_name", None)

    @property
    @data_field
    def outputs(self) -> dict[str, str | list[str]]:
        """Each format this fidelity writes, with its file, pattern, or folder; the fidelity's YAML fields fill it, as they
        do stage."""
        return dict(self._outputs)

    @outputs.setter
    def outputs(self, value: dict[str, str | list[str]]) -> None:
        self._outputs = dict(value or {})
        vars(self).pop("_declared_files", None)

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

    def schema_guide(self) -> str:
        """Its practice's schema guide, which its output conforms to; none when it belongs to no practice."""
        practice = self.practice_guidance
        return practice.schema_guide() if practice is not None else ""

    @property
    def is_part_of_practice(self) -> bool:
        """A fidelity is a part of the practice that holds it; one made apart from any practice is not."""
        return self.practice_guidance is not None

    @property
    def is_served_on_mcp(self) -> bool:
        """Only a fidelity its practice holds is served; one made apart from any practice has no practice to reach it
        through."""
        return self.practice_guidance is not None

    @property
    def practice_guidance(self) -> PracticeGuidance | None:
        parent = getattr(self, "parent", None)
        while parent is not None and not isinstance(parent, PracticeGuidance):
            parent = getattr(parent, "parent", None)
        return parent

    @property
    def format(self) -> str | None:
        """The format this fidelity works in: the one it last used, which it keeps in the session its practice works
        in, else its default. A Clean Engineering companion writes the code of the fidelity it is the companion of, so
        while that fidelity works in a code format the companion works in it too, read when asked so it follows it."""
        served = self.companion_of.format if self.companion_of is not None else None
        if served is not None and Format(served).is_code:
            return served
        kept = self.session_output.kept_format if self.session_output is not None else ""
        return kept or getattr(self, "_format", None)

    @format.setter
    def format(self, value: str | None) -> None:
        """Work in value from now on; in a session, the fidelity keeps it there, so the next action on it works in it
        without being told."""
        self._format = value
        if value and self.session_output is not None:
            self.session_output.keep_format(value)

    @property
    @data_field
    def default_format(self) -> str:
        return getattr(self, "_default_format", "")

    @default_format.setter
    def default_format(self, value: str) -> None:
        """value as a practice document writes it, such as ``markdown (md)``: its first word, as the format's name."""
        self._default_format = Format(self._first_word(value)).name if value else ""
        # Each read of the fidelity's document names its default again; a format already chosen stays.
        if self._default_format and not getattr(self, "_format", None):
            self._format = self._default_format

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

    @functools.cached_property
    def _own_name(self) -> Name:
        """The fidelity's name in its practice, made once."""
        return Name(self.name)

    @property
    @data_field
    def slug(self) -> str:
        parent = self.practice_guidance.slug if self.practice_guidance is not None else Name(type(self).__name__).kebab
        leaf = self._own_name.kebab
        return f"{parent}-{leaf}" if leaf else parent

    @property
    def markdown_scope(self) -> MarkdownScope:
        """Where this fidelity's markdown lives: its own ``### {name}`` block of its practice's document, with the
        practice's templates and examples at this fidelity and the format it works in."""
        practice = self.practice_guidance
        base = practice.markdown_scope if practice is not None else super().markdown_scope
        return replace(base, fidelity=self.name or None, format=self.format or None, in_fidelity_block=True)

    @property
    def install_folder(self) -> Path:
        practice = self.practice_guidance
        base = practice.install_folder if practice is not None else self.module_dir
        leaf = (self.name or "").replace(" ", "-")
        return base / leaf if leaf else base

    @property
    def scaffold(self) -> str:
        """This fidelity's Scaffold subsection: the names a first cut writes, which are what a partition index lists;
        empty when the fidelity has none."""
        return self._section("scaffold").extract().strip()

    @property
    def section(self) -> str:
        """This fidelity's whole ``### {name}`` block in its practice's document: overview, sketch, guidance, and
        rules."""
        practice = self.practice_guidance
        return practice.document.fidelity_block(self.name) if practice is not None else ""

    @property
    def titled_section(self) -> str:
        """Its block under its own ``### {name}`` heading, as a practice's scoped markdown shows it; empty when the
        practice document has no block for it."""
        body = self.section
        return f"### {self.name}\n\n{body}" if body else ""

    @markdownCollection
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Fidelity rules section."""

    def checked_rule_collections(self) -> list[RulesCollection]:
        """The rule collections a validate of this fidelity checks: its practice's shared rules, then its own. A
        collection it shares with its practice is listed once."""
        practice = self.practice_guidance
        collections = [practice.rules if practice is not None else None, self.rules]
        return list({id(collection): collection for collection in collections if collection is not None}.values())

    def every_rule(self) -> list[Rule]:
        """Every rule of its practice, shared and each fidelity's: a saved graph holds the whole practice's hits, so a
        report on this fidelity still shows each hit's rule text; its own rules when it belongs to no practice."""
        practice = self.practice_guidance
        return practice.every_rule() if practice is not None else super().every_rule()

    @property
    def examples(self) -> str:
        """Its practice's examples at this fidelity, in the format it works in; none when it belongs to no practice."""
        practice = self.practice_guidance
        if practice is None:
            return ""
        return str(Markdown.from_label(practice, "examples", fidelity=self.name, format=self.format).extract() or "").strip()

    def generate_output(self) -> str:
        """What its practice tells the agent about writing this fidelity's artifact: the practice's generate_output
        recipe, expanded, so a practice that renders a format itself, such as Clean Engineering's draw.io, says so."""
        practice = self.practice_guidance
        return practice.instruction("generate_output").expand({}).instructions if practice is not None else ""

    def guidance_parts(self) -> list[str]:
        """Its own guidance, then its Clean Engineering companion's instructions: what a practice working at this
        fidelity adds to its own guidance."""
        companion = self.clean_engineering
        return [self._section("guidance").extract().strip(), companion.instructions.strip() if companion is not None else ""]

    @property
    def templates(self) -> str:
        """Its template in the format it works in, else in its default format: a companion writing TypeScript still
        shows Clean Engineering's reference template when no TypeScript one exists."""
        located = self._template_markdown()
        return located.extract().strip() if located is not None else ""

    @property
    def template_file(self) -> Path | None:
        """The file its template is read from, in the format it works in, else its default format; none when it has
        no template."""
        located = self._template_markdown()
        return located.location.path if located is not None else None

    def _template_markdown(self) -> Markdown | None:
        for format in [spelling for spelling in dict.fromkeys((self.format, self.default_format)) if spelling] or [""]:
            located = Markdown.from_label(self, "templates", format=format)
            path = located.location.path
            if path is not None and path.is_file():
                return located
        return None

    def declares(self, path: str, format: str = "") -> bool:
        """Whether path, written from the project's root or absolute, is a file one of its outputs names, in format when
        one is named: a declared file such as ``{bounded_context}/{aggregate}/{aggregate}.ts`` matches the end of a
        path. A declared folder names no file."""
        held = self._declared_files
        chosen = held.get(format, []) if format else [declared for files in held.values() for declared in files]
        return any(declared.pattern.search(path) for declared in chosen)

    @functools.cached_property
    def _declared_files(self) -> dict[str, list[DeclaredFile]]:
        """The files each format of its outputs declares, by format."""
        return {
            label: [DeclaredFile(name) for name in ([names] if isinstance(names, str) else names) if name and not name.endswith("/")]
            for label, names in self.outputs.items()
        }

    @functools.cached_property
    def actions(self) -> FidelityActions:
        """The actions that work on this fidelity, each run on it: ``fidelity.actions.generate(format="drawio")``.
        The actions register with the action catalogue, so guidance names none of them."""
        return FidelityActions(self)

    @property
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
        practice = self.practice_guidance
        parent = ()
        templates = ""
        if practice is not None:
            parent = (
                (practice.overview or "").strip(),
                practice._section("guidance").extract().strip(),
                (practice.rules.markdown or "").strip(),
            )
            templates = self.templates
            if templates:
                templates = f"#### Template\n\n{templates}"
        companion = self.clean_engineering if practice is not None else None
        schema = self.schema_guide()
        return "\n\n".join(
            part
            for part in (
                schema,
                *parent,
                (self.overview or "").strip(),
                (self.guidance or "").strip(),
                (self.rules.markdown or "").strip(),
                templates,
                companion.instructions if companion is not None else "",
            )
            if part
        )
