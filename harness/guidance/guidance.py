"""Assemble agent instructions from @markdown properties."""
from __future__ import annotations

from functools import cached_property
from dataclasses import replace
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, ClassVar

from harness.annotations.annotation import hosted_only
from harness.annotations.class_folder import class_folder
from harness.annotations.name import Name
from harness.guidance.action_catalogue import ACTION_CATALOGUE, FidelityActions
from harness.guidance.declared_outputs import DeclaredOutputs
from harness.guidance.guidance_instructions import GuidanceInstructions
from harness.guidance.practice_formats import PracticeFormats, RenderContent, Rendered, RenderRequest
from harness.guidance.rule import Rule, RulesCollection
from harness.guidance.schema import Schema
from harness.guidance.stages import STAGES, ApproachStage
from harness.guidance.worked_session import NO_SESSION_OUTPUT, FidelityOutput, NamedPaths, PracticeOutput, WorkedSession
from harness.guidance.working_set import COMPANION_PRACTICE, WorkingSet
from harness.agent_tools.agent_tools import (
    AgentInstructions,
    AgentTool,
    AgentToolSet,
    InstalledName,
    collect,
    agent_instructions,
    agent_tool,
    agent_toolset,
    instructions,
    toolset_collection,
)
from harness.installation.context_config import CONTEXT_FOLDER
from harness.installation.files import rules, skill
from harness.installation.data_class import data_field, identity
from harness.hooks.hooks import Hook
from harness.mcp.mcp_annotations import mcp
from harness.markdown import (
    FileFilter,
    Markdown,
    MarkdownCollection,
    MarkdownScope,
    MarkdownText,
    markdown,
    markdown_collection,
)
from harness.markdown.format import Format

# The heading of a practice document under which each fidelity has a block of its own, ``### {fidelity}``.
FIDELITIES_HEADING = "Fidelities"
# The member of every guidance that answers its whole guidance, published as its own tool.
OWN_INSTRUCTIONS = "instructions"

if TYPE_CHECKING:
    from harness.graph.pattern_overlays import GraphOverlay
    from harness.guidance.practice_supplement import PracticeSupplement
    from harness.hooks.hook_server import HookPayload


class SketchLens:
    """The section of a sketch that one practice writes, opened by the headings the practice declares, such as
    ``stories:``. Each practice holds its own (``PracticeGuidance.sketch_lens``), so a reader of a sketch asks the
    practice for it rather than naming the practice."""

    def __init__(self, titles: tuple[str, ...]) -> None:
        self.titles = titles

    def opens(self, title: str) -> bool:
        """True when this title is the section heading or marker this practice writes under."""
        return title.strip().lower() in self.titles


@agent_toolset
class Guidance:
    default_format: str = ""
    name: str | None = None
    domain_slug: str | None = None

    @property
    def module_dir(self) -> Path:
        """The folder beside the guidance's class: ``key`` and every markdown read ask it."""
        return class_folder(type(self))

    @property
    def markdown_scope(self) -> MarkdownScope:
        """Where this guidance's markdown lives, handed to each Markdown it reads: the folder beside its class, its
        ``{slug}.md``, and the format it works in."""
        folder = self.module_dir
        return MarkdownScope(folder, self.domain_slug or folder.name, format=self.format or None, values=tuple(sorted(self.markdown_values.items())))

    @property
    def markdown_values(self) -> dict[str, str]:
        """The values this guidance's code holds that its markdown names by a marker, such as a band a check reads
        (``{{child_band.sub_epic}}``), each by the marker's name: its document, rules and templates are filled from
        them as they are read, so the number is typed in the code alone. None unless a guidance says otherwise."""
        return {}

    def section_text(self, label: str) -> str:
        """The prose of one of its own labelled sections, such as its Overview, from the Markdown it keeps for that
        section, so a second read answers from the text the first read found."""
        return Markdown.held_by(self, label).extract()

    # -- how its tools are published and installed ----------------------------------------------------------------

    def instructions_type(self, name: str) -> type[AgentInstructions]:
        """Its own ``instructions`` member is published as its whole guidance (*GuidanceInstructions*); every other
        ``@agent_instructions`` member as any toolset's."""
        return GuidanceInstructions if name == OWN_INSTRUCTIONS else super().instructions_type(name)

    def installed_as(self, tool: AgentTool) -> InstalledName:
        """Its files go in its install folder; its own instructions are named after the guidance alone."""
        return InstalledName(self.install_folder, is_own=isinstance(tool, GuidanceInstructions))

    def listed_parts(self) -> list[AgentToolSet]:
        """The parts the file of its own instructions lists, each with the call to its instructions: the toolsets it
        holds in its collections, such as each fidelity of a practice."""
        return list(self.child_toolsets())

    @markdown_collection("shared rules")
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    session: WorkedSession | None = None
    """The Session this guidance works in, which its work_in gives it; none until a session works on it."""

    def __init__(self, format: str | None = None) -> None:
        self.format = Format(format if format is not None else self.default_format)

    @property
    @data_field
    def overview(self) -> str:
        """Its Overview section: what this guidance is for, which a person reads on its help."""
        return self.section_text("overview")

    @property
    @data_field
    def guidance(self) -> str:
        """Its Guidance section: how to do the work well, which a person reads on its help."""
        return self.section_text("guidance")

    @property
    @data_field(key="rules")
    def listed_rules(self) -> list[Rule]:
        """Its rules one by one, as its help lists them: a practice's shared rules, or a fidelity's own."""
        return list(self.rules)

    @property
    def checked_rule_collections(self) -> list[RulesCollection]:
        """The rule collections a validate of this guidance checks: its own rules."""
        return [self.rules] if self.rules is not None else []

    def checked_rules(self) -> list[Rule]:
        """The rules a validate of this guidance checks, one by one."""
        return [rule for collection in self.checked_rule_collections for rule in collection]

    def checked_rules_text(self) -> str:
        """The rules a validate of this guidance checks, as their markdown: what an agent judges against, and what an
        action that writes or fixes the artifact tells it to follow."""
        texts = (collection.validate.strip() for collection in self.checked_rule_collections)
        return "\n\n".join(text for text in texts if text)

    @property
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
        """The templates folder beside this guidance's class, which its sketch notation is read from."""
        return self.module_dir / "templates"

    def rules_after_edit(self, tool_use: HookPayload) -> str:
        """The rules an action hands the agent after the edit tool_use names: the rules that apply to the edited file,
        else all of them; none while this guidance's rules hook is turned off."""
        rules = self.rules
        if rules is None or Hook.disabled_on(rules.inject_rules):
            return ""
        applied = (rules.inject_rules(tool_use).get("additional_context") or "").strip()
        return applied or (rules.markdown or "").strip()

    @property
    def schema(self) -> Schema:
        """The schema this guidance's output conforms to: a practice's ``model/schema.yaml``; an empty one for guidance
        that is no practice."""
        return Schema("")

    def schema_guide(self) -> str:
        """What tells an action to conform its output to this guidance's schema; none for an empty schema."""
        return self.schema.guide()

    @property
    @skill
    @mcp
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
        return "\n\n".join(
            part
            for part in (
                self.schema_guide(),
                (self.overview or "").strip(),
                (self.guidance or "").strip(),
                (self.rules.markdown or "").strip(),
                (self.templates or "").strip(),
            )
            if part
        )


@hosted_only
@toolset_collection
class GuidanceCollection(MarkdownCollection["Guidance", "FidelityGuidance"], Guidance):
    def __init__(self, entries: dict[str, Guidance] | None = None, parent: Guidance | None = None) -> None:
        MarkdownCollection.__init__(self, entries, parent=parent)
        Guidance.__init__(self)
        self.current: Guidance | None = None

    def child(self, name: str, body: str = "") -> FidelityGuidance:
        """The fidelity a ``### name`` block of the practice document declares, with the settings its ```yaml block
        gives it."""
        return FidelityGuidance.from_block(name, body)

    def called(self, name: str) -> FidelityGuidance | None:
        """The fidelity a person names by its bare name, as its practice document writes it (``story_map``) or in kebab
        case (``story-map``); none when the collection holds no fidelity of that name."""
        return next((fidelity for fidelity in self if name in (fidelity.name, Name(fidelity.name).kebab)), None)

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
    """One practice: its identity, its words (its document, guidance, rules, and examples), its fidelities, and the set
    of practices it works with. It holds three parts, each made once: its formats (``formats``), which read and write
    its artifacts and render between them; its part in the knowledge graph (``reading``); and its schema (``schema``)."""

    sketch_lens: ClassVar[SketchLens] = SketchLens(())
    """This practice's section of a sketch: the headings that open it, lower case, such as `stories:`. A practice holds
    the one lens its sketch format reads with, so its sketch format and a sketch's reader hold it rather than naming the
    practice."""
    SHORT_NAME: str = ""
    """The practice's name where there is little room, such as `CE` on a session board's chip."""
    COLOUR: str = ""
    """The colour a session board draws the practice's chips and tiles in, such as `#6BCB77` for Stories."""
    shows_every_fidelity: bool = False
    """Whether scoped markdown shows every fidelity's block even when one is current, as DDD's does; otherwise it shows
    only the current fidelity's."""
    default_workspace_folder: str = "."
    """The folder under a session's workpath this practice writes into while no root is chosen for it, such as
    ``tests`` for Stories; the whole workpath for a practice that names none."""
    format_adapters: ClassVar[dict[str, Any]] = {}
    """The parse and render adapter of each format this practice owns, by format name: a class, or the module and class
    name it is imported from when first used. A practice with none defers rendering to its fidelity's Clean Engineering
    companion."""
    formats_type: type[PracticeFormats] = PracticeFormats
    """The kind of formats this practice holds: a practice whose formats read or convert in a way of their own names its
    own kind."""
    reading_type: type | None = None
    """The kind of reading this practice takes part in the knowledge graph with (a *PracticeReading* of harness/graph,
    which sits above this module, so it is not named here): a practice that reads files from the working copy, or
    declares node types the graph treats in a way of their own, names its own kind; harness/graph sets the default,
    *PracticeReading*, when it is imported."""
    extends: str = ""
    """The practice whose types this practice's schema builds on with ``is:``, such as a DDD entity that is a Clean
    Engineering class; its types also carry that practice's rules."""
    working_set_type: type[WorkingSet] = WorkingSet
    """The kind of working set this practice holds: the practices of its set it works with. A supplement, which also
    reads the fidelities it supplements from the set, names its own kind."""
    editor: ClassVar[Any] = None
    """The app that edits this practice's files beside the chat (an *App* of harness/diagnostics, which sits above this
    module, so it is not named here): the Story UI editor for Stories, none for every other practice. Every instance of the practice, in every session, edits with the same app, so the module that makes the
    app sets it on the practice's class (``Stories.editor = STORY_UI_APP``), and the framework and the practice import no
    app."""

    def claims(self, file: Path) -> bool:
        """Whether file, production code under a folder one of its fidelities writes code to, is this practice's own:
        a fidelity that declares a folder per module, such as Clean Engineering's ``{module}/``, names no file, so the
        practice says which code there is its. Every practice claims all of it unless it narrows that."""
        return True

    def is_production_code(self, file: str) -> bool:
        """Whether file, named from the project's root, is production code a fidelity of this practice that writes a
        folder per module writes there, rather than a test of it. Every file is, unless the practice tells its tests
        apart, as a practice that writes code does."""
        return True

    def placed_under(self, declared: PurePosixPath, root: Path) -> Path | None:
        """Where a path one of its fidelities declares, such as ``.context/story-map.md``, lands under root, that
        fidelity's root in a session: ``root / declared``. A root inside a ``.context`` folder, such as
        ``harness/.context/stories``, holds the practice's documents itself, so a declared ``.context/...`` file lands in
        it rather than in a ``.context`` within the ``.context``. None when the path lands nowhere under root; a practice
        that keeps files of its own beside the ``.context`` places those itself."""
        if CONTEXT_FOLDER in root.parts and declared.parts[:1] == (CONTEXT_FOLDER,):
            declared = PurePosixPath(*declared.parts[1:])
        return root / declared

    claims_some_code: ClassVar[bool] = False
    """True for a practice whose claim narrows to some code, as DDD's does to a domain's. A practice that claims all code,
    such as Clean Engineering, proposes no root for a file such a practice claims: that file's folder is the narrower
    practice's piece, as an aggregate's folder is DDD's."""

    # The format the practice works in while it has no current fidelity.
    _own_format: Format = Format()

    first_fidelity: ClassVar[str | None] = None
    """The fidelity the practice starts at when it is made without naming one, such as DDD's ``bounded_context``;
    none leaves it with no current fidelity."""

    def __init__(self, format: str | None = None, fidelity: str | None = "") -> None:
        """fidelity left out starts the practice at its ``first_fidelity``; ``None`` starts it at no fidelity."""
        super().__init__(format=format)
        self.formats = self.formats_type(self, dict(self.format_adapters))
        self.working_set = self.working_set_type(self)
        self._start_at(self.first_fidelity if fidelity == "" else fidelity)
        self._check_format()

    def _start_at(self, fidelity: str | None) -> None:
        """Make the fidelity configuration names, such as ``create("stories", fidelity="story_map")``, the practice's
        current fidelity, looked up once here: an action that works at another fidelity holds that fidelity itself,
        since every call in a session shares the session's practices. A format the practice is made with is the one
        that fidelity works in."""
        entries = self.fidelities.entries
        if fidelity is not None and entries and fidelity not in entries:
            raise ValueError(f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(entries)}")
        named = entries.get(fidelity) if fidelity is not None else None
        if named is None:
            return
        if self._own_format:
            named.format = self._own_format
        self.fidelities.current = named

    def _check_format(self) -> None:
        """Raise ValueError for a format the practice works in but does not write: one its formats' adapters do not
        read, or, for a practice with no adapters, one no fidelity names as its default."""
        format = self.format
        supported = self.formats.supported
        if not supported and format:
            supported = frozenset(child.default_format for child in self.fidelities if child.default_format)
        if supported and format and format not in supported:
            raise ValueError(f"Unsupported format {format!r}. Choose from: {sorted(supported)}")

    @property
    def format(self) -> Format:
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
            self._own_format = Format(value)

    @property
    def _current_fidelity(self) -> FidelityGuidance | None:
        """The current fidelity, read without reading the fidelities from the practice's document when nothing has
        read them yet, since none can be current then."""
        fidelities = vars(self).get("fidelities")
        return getattr(fidelities, "current", None)

    @markdown_collection("shared rules")
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    @property
    def markdown_scope(self) -> MarkdownScope:
        """Where this practice's markdown lives, at its current fidelity and format, read without reading the
        fidelities from the practice's document when nothing has read them yet."""
        return self.scope_at(self._current_fidelity)

    def scope_at(self, fidelity: FidelityGuidance | None) -> MarkdownScope:
        """Where this practice's markdown lives when read at fidelity: its templates are looked for by that fidelity's
        name first, and the files of its folders are those the practice reads at that fidelity (``reads_file_at``)."""
        name = fidelity.name if fidelity is not None else None
        return replace(super().markdown_scope, template_name=name or None, reads_file=self.reads_file_at(name))

    def reads_file_at(self, fidelity: str | None) -> FileFilter | None:
        """Which files of its folders, such as its examples, the practice reads at fidelity, given the label read and
        the file; every file unless a practice says otherwise."""
        return None

    @cached_property
    def reading(self) -> Any:
        """How the practice takes part in the knowledge graph, made from its ``reading_type`` the first time the graph
        or the practice's own code asks, and kept."""
        if self.reading_type is None:
            raise TypeError(f"{self.key} has no kind of reading: harness/graph, which gives the default, is not imported")
        return self.reading_type(self)

    @property
    def graph_overlay(self) -> GraphOverlay | None:
        """What the practice gives the knowledge graph on top of the practices it works with, as a pattern or a
        supplement does: the rules it adds to each and the facts it records. None for a practice that gives none, which
        is every practice but a pattern and a supplement that checks graph rules."""
        return None

    @cached_property
    def document(self) -> MarkdownText:
        """The practice's own document, ``{key}.md`` beside its class, read once: its sections and each fidelity's
        block are read from this text."""
        path = self.domain_markdown_path
        return MarkdownText(self.markdown_scope.filled(path.read_text(encoding="utf-8")) if path.is_file() else "")

    @cached_property
    def schema(self) -> Schema:
        """The practice's schema, ``model/schema.yaml`` beside its class, read once: the types it declares, the fidelity
        that creates each, and the text that tells an action the shape its output conforms to."""
        return Schema.load(self.module_dir / "model" / "schema.yaml")

    @property
    def checked_rule_collections(self) -> list[RulesCollection]:
        """The rule collections a validate of this practice checks: its current fidelity's, which start with the shared
        rules, or the shared rules and every fidelity's when it has no current one."""
        current = self.fidelities.current
        if current is not None:
            return current.checked_rule_collections
        collections = [self.rules, *(fidelity.rules for fidelity in self.fidelities)]
        return list({id(collection): collection for collection in collections if collection is not None}.values())

    @property
    def every_rule(self) -> list[Rule]:
        """Its shared rules and every fidelity's: a saved graph holds the whole practice's hits, so each one's rule text
        is there to show beside it."""
        collections = (self.rules, *(fidelity.rules for fidelity in self.fidelities))
        return [rule for collection in collections if collection is not None for rule in collection]

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

    def answers_to(self, slug: str) -> PracticeGuidance | FidelityGuidance | None:
        """The guidance of this practice that slug names: the practice itself for its slug, such as ``stories``, or the
        fidelity whose slug it is, such as ``stories-story-map``; none for any other slug."""
        if slug == self.slug:
            return self
        return next((fidelity for fidelity in self.fidelities if fidelity.slug == slug), None)

    def guidance_stating(self, rule: str) -> PracticeGuidance | FidelityGuidance:
        """The guidance of this practice that states rule, by its slug: the fidelity whose rules hold it, such as
        ``stories-story-map`` for ``verb-noun-format``, else the practice itself, whose shared rules every fidelity
        follows, so a fix of the rule is made by the guidelines that wrote it."""
        return next((fidelity for fidelity in self.fidelities if any(stated.slug == rule for stated in fidelity.rules)), self)

    @property
    def fidelity_slugs(self) -> list[str]:
        """The slug of each of the practice's fidelities, such as `stories-story-map`, which a guidance action lists
        when it refuses a word no practice or fidelity has. Not sent as data: the session board sends each fidelity once,
        with its practice (`BoardFidelity`)."""
        return [fidelity.slug for fidelity in self.fidelities]

    def work_in(self, session_output: PracticeOutput) -> None:
        """Work in the session that session_output, this practice's PracticeSessionOutput, belongs to: the practice
        knows that session, and each of its fidelities is given what it has there, so it answers its outputs, files and
        reports itself."""
        self.session = session_output.session
        self._session_output = session_output
        for fidelity in self.fidelities:
            fidelity.work_in(session_output.of_fidelity(fidelity))

    # The PracticeSessionOutput it works in, which work_in gives it; none until a session works on it.
    _session_output: PracticeOutput | None = None

    @property
    def session_roots(self) -> list[Path]:
        """The folders the session this practice works in names for it, where it writes and the Graph app reads it
        from: the practice's own folder, then each further folder a person added to one of its fidelities, such as a
        second bounded context's folder added to DDD's tactics. None outside a session."""
        if self._session_output is None:
            return []
        roots = [self._session_output.folder, *(root for fidelity in self.fidelities for root in fidelity.session_output.roots)]
        return list(dict.fromkeys(Path(root).resolve() for root in roots))

    @agent_instructions
    def generate_output(self) -> str:
        """Write this practice's artifact for the current fidelity.

        Override when the practice owns generation (for example drawio render).
        The default is instruction-only: generate already expanded instructions;
        the agent writes under the session's root.
        """
        return ""

    @property
    @data_field
    @agent_instructions
    def guidance(self) -> str:
        examples = str(self.examples or "").strip()
        templates = str(self.templates or "").strip()
        scoped = self.scoped_markdown.strip()
        if scoped:
            instructions(scoped)
        if examples:
            instructions(f"{self._EXAMPLES_PREAMBLE}\n\n{examples}")
        if templates:
            instructions(templates)
        # The practice's own Guidance section, then its current fidelity's guidance and companion text, which that
        # fidelity answers.
        current = self.fidelities.current
        parts = [self.section_text("guidance").strip(), *(current._guidance_parts() if current is not None else ())]
        return "\n\n".join(part for part in parts if part)

    @property
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
        parent_text = Guidance.instructions.fget(self)
        extra = self.fidelities.instructions if self.fidelities.entries else ""
        return "\n\n".join(part for part in (parent_text, extra, self.scoped_markdown) if part)

    @toolset_collection
    @markdown_collection
    def fidelities(self) -> GuidanceCollection:
        """Fidelity children from the Fidelities section."""

    @property
    def domain_markdown_path(self) -> Path:
        """The practice's own document, ``{key}.md`` in the folder beside its class."""
        class_dir = self.module_dir
        return class_dir / f"{class_dir.name}.md"

    # What the examples the guidance shows are for, set above them: an agent shown one example copies its structure
    # into every artifact unless it is told the structure belongs to the example's own domain.
    _EXAMPLES_PREAMBLE = (
        "## Examples\n\n"
        "These examples show notation, naming, depth, and tone. Their structure, such as how many epics, modules, or "
        "screens they have and how those nest, belongs to their own domain: take the structure of what you write from "
        "your sources, never from an example."
    )

    @markdown
    def examples(self) -> str:
        """Examples folder content — not part of instructions."""

    @agent_tool
    def render(self, format: str, content: RenderContent = "", source: str | None = None, previous: str = "") -> Rendered:
        """Turn content into the practice object model, then render the target format. Content is in source, the
        format this practice works in when none is named; with no content, the practice renders its own model.
        previous is the target file as it is now. It renders through its formats at the fidelity the practice was made
        at, whose Clean Engineering companion writes its code; a practice with no fidelity renders at none."""
        return self.formats.render(RenderRequest(Format(format), content, Format(source), previous, fidelity=self.fidelities.current))

    @property
    def scoped_markdown(self) -> str:
        """Overview, practice sections, and the current fidelity's block, or every fidelity's when none is current."""
        parts = [self.section_text(label) for label in ("overview", "guidance", "shared rules", "language")]
        current = self.fidelities.current
        current_name = current.name if current is not None else None
        shown = [fidelity for fidelity in self.fidelities if self.shows_every_fidelity or current_name in (None, fidelity.name)]
        parts.extend(fidelity._titled_section for fidelity in shown)
        return "\n\n".join(part for part in parts if part.strip())


@hosted_only
@identity("slug")
@agent_toolset
class FidelityGuidance(Guidance):
    session_output: FidelityOutput = NO_SESSION_OUTPUT
    """What this fidelity has in the session its practice works in (a FidelitySessionOutput): where it writes each
    format, the files it declares there, and its reports folder; none until a session works on its practice."""
    judged_on: str = "artifacts"
    """What a validate judges this fidelity's rules against, as its practice document's ``judged_on`` says: the
    ``artifacts`` it writes, read as text, or the ``graph`` validate builds from the code, where rules about the object
    model the code holds (one model, classes with one job, one-way dependencies) can be checked."""
    example: str = ""
    """The worked example of what it writes, as its practice document's ``example`` names it: a file of its practice's
    folder, or a folder of code files. Its format trip (``FormatTrip``) takes this example to each format the fidelity
    declares and back; a fidelity that names none has no format proven to hold what it writes."""
    leaves_out: dict[str, str] = {}
    """What each format it declares cannot hold and where that content is kept, as its practice document's
    ``leaves_out`` says for the format: a drawing holds no description, which stays in the markdown file. Whoever picks
    a format that holds less is told here what the file will not carry."""
    reviews_files_of: tuple[str, ...] = ()
    """The fidelities of its own practice whose files a person reviews for this one, as its practice document's
    ``reviews_files_of`` names them: UX's front-end code is reviewed against its information architecture and mockup,
    since its view code is Clean Engineering's code to review. None reviews its own files."""

    def __init__(self, name: str = "", stage: str = "") -> None:
        # A fidelity is made in no format: its block's ```yaml names its default (``from_block``).
        super().__init__(format="")
        self._is_format_given = False
        self.name = name
        self.stage = stage
        self.outputs = {}

    @classmethod
    def from_block(cls, name: str, body: str = "") -> FidelityGuidance:
        """The fidelity a ``### name`` block of its practice's document declares, with the settings its ```yaml block
        gives it."""
        fidelity = cls(name=name)
        fidelity._apply_settings(MarkdownText(body).yaml_fields)
        return fidelity

    def _apply_settings(self, block_fields: dict[str, Any]) -> None:
        """Take the settings its block's ```yaml gives it: the stage it is in, its default format, the files it writes
        in each format, its worked example and what each format leaves out of it, its Clean Engineering companion, and
        what a validate judges it on. A setting it does not know
        is the reader's, such as a rules block's ``globs``, and stays unread here."""
        if "stage" in block_fields:
            self.stage = str(block_fields["stage"] or "")
        if "default_format" in block_fields:
            self.default_format = str(block_fields["default_format"] or "")
        if "outputs" in block_fields:
            self.outputs = block_fields["outputs"] if isinstance(block_fields["outputs"], dict) else {}
        if COMPANION_PRACTICE in block_fields:
            self.clean_engineering = str(block_fields[COMPANION_PRACTICE] or "")
        if "judged_on" in block_fields:
            self.judged_on = str(block_fields["judged_on"] or "artifacts")
        if "example" in block_fields:
            self.example = str(block_fields["example"] or "")
        if "leaves_out" in block_fields:
            said = block_fields["leaves_out"] if isinstance(block_fields["leaves_out"], dict) else {}
            self.leaves_out = {str(Format(str(format))): str(words) for format, words in said.items()}
        if "reviews_files_of" in block_fields:
            self.reviews_files_of = tuple(str(name) for name in block_fields["reviews_files_of"] or ())

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
        return dict(self.declared.outputs)

    @outputs.setter
    def outputs(self, value: dict[str, str | list[str]]) -> None:
        """Write each format to the file, pattern, or folder value names; the files it declares are made again from
        them (``declared``)."""
        self.declared = DeclaredOutputs(value or {})

    def work_in(self, session_output: FidelityOutput) -> None:
        """Work in a session through session_output, the FidelitySessionOutput holding what this fidelity has there."""
        self.session_output = session_output

    def schema_guide(self) -> str:
        """Its practice's schema guide, which its output conforms to; none when it belongs to no practice."""
        practice = self.practice_guidance
        return practice.schema_guide() if practice is not None else ""

    def published_name(self, tool: AgentTool) -> str:
        """Its own instructions are published under its slug alone, ``stories-story-map``, when a practice holds it;
        its other tools as any guidance's."""
        if self.practice_guidance is not None and isinstance(tool, GuidanceInstructions):
            return self.slug
        return super().published_name(tool)

    def installed_as(self, tool: AgentTool) -> InstalledName:
        """A fidelity a practice holds is one part of it: its files sit in its practice's install folder, named after
        its own slug, ``stories-story-map``. One made apart from any practice is installed as any guidance."""
        practice = self.practice_guidance
        if practice is None:
            return super().installed_as(tool)
        return InstalledName(practice.install_folder, Name(self.slug).kebab, is_own=isinstance(tool, GuidanceInstructions))

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

    _format: Format = Format()
    _default_format: Format = Format()
    # Whether the format was given, by a person or an action, rather than taken from the fidelity's default.
    _is_format_given: bool = False

    @property
    def format(self) -> Format:
        """The format this fidelity works in: the one it was last given while that is still chosen in the session its
        practice works in, else the first format chosen there, else the one it was given or its default. A format it
        does not write, such as one an action names for a practice of its own, is worked in for as long as it is held."""
        chosen = self.session_output.chosen_formats
        if not chosen or not self._offers(self._format) or (self._is_format_given and self._format in chosen):
            return self._format
        return Format(chosen[0])

    @format.setter
    def format(self, value: str | None) -> None:
        """Work in value from now on; in a session, a format the fidelity writes is chosen there too, so the next
        action on it works in it without being told."""
        self._format = Format(value)
        self._is_format_given = bool(self._format)
        if self._format and self._offers(self._format):
            self.session_output.choose_format(self._format, True)

    def _offers(self, format: str) -> bool:
        """Whether this fidelity writes format: one of its outputs names it."""
        return Format(format).name in self.outputs

    @property
    @data_field
    def default_format(self) -> Format:
        return self._default_format

    @default_format.setter
    def default_format(self, value: str) -> None:
        """value as a practice document writes it, such as ``markdown (md)``: its first word, as the format's name."""
        self._default_format = Format(self._first_word(value)) if value else Format()
        # Each read of the fidelity's document names its default again; a format already chosen stays.
        if self._default_format and not self._format:
            self._format = self._default_format

    def _first_word(self, written: str) -> str:
        """The first word of a setting as a practice document writes it, such as ``code`` of ``code (Clean
        Engineering)``."""
        return written.split()[0].strip("()`") if written.strip() else ""

    @property
    def formats_without_an_adapter(self) -> list[str]:
        """Each format it declares in its outputs that nothing reads and writes, named (``PracticeFormats.lacking``):
        asked of its practice's formats, or, for a practice with no adapters of its own, of the formats of its Clean
        Engineering companion, which renders for it. None for a fidelity whose practice has neither."""
        practice = self.practice_guidance
        formats = practice.formats if practice is not None else None
        if formats is not None and not len(formats) and self.clean_engineering is not None:
            formats = self.clean_engineering.practice_guidance.formats
        return formats.lacking(self.declared) if formats is not None else []

    @property
    def clean_engineering(self) -> FidelityGuidance | None:
        """The Clean Engineering fidelity this fidelity's `clean_engineering:` field names, whose instructions join
        this fidelity's: that fidelity itself, of the Clean Engineering practice of its practice's set, held once it is
        first asked for. None when its field names none, or its practice was made apart from any set."""
        stored = getattr(self, "_clean_engineering", None)
        if isinstance(stored, FidelityGuidance):
            return stored
        practice = self.practice_guidance
        companion = practice.working_set.companion if practice is not None else None
        if not isinstance(stored, str) or not stored or companion is None:
            return None
        self._clean_engineering = companion.fidelities[stored]
        return self._clean_engineering

    @property
    def companion_instructions(self) -> str:
        """Its Clean Engineering companion's instructions as they join its own: while it works in a code format the
        companion's template is the one in that format, since the companion writes this fidelity's code; else the
        companion's own. None when it has no companion."""
        companion = self.clean_engineering
        if companion is None:
            return ""
        return companion._instructions_in(self.format if self.format.is_code else companion.format)

    @clean_engineering.setter
    def clean_engineering(self, value: FidelityGuidance | str | None) -> None:
        """A companion fidelity, or its name as a practice document writes it, such as ``code (Clean Engineering)``."""
        self._clean_engineering = Name(self._first_word(value)).snake if isinstance(value, str) else value

    @cached_property
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
        base = practice.scope_at(self) if practice is not None else super().markdown_scope
        within = (FIDELITIES_HEADING, self.name) if self.name else ()
        return replace(base, template_name=self.name or None, format=self.format or None, within=within)

    @property
    def module_dir(self) -> Path:
        """The folder beside its practice's class, which holds the practice document its block is in and the templates
        it reads; the folder beside its own class when it belongs to no practice."""
        practice = self.practice_guidance
        return practice.module_dir if practice is not None else super().module_dir

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
        return self.section_text("scaffold").strip()

    @property
    def section(self) -> str:
        """This fidelity's whole ``### {name}`` block in its practice's document: overview, sketch, guidance, and
        rules."""
        practice = self.practice_guidance
        return practice.document.block_under(FIDELITIES_HEADING, self.name) if practice is not None else ""

    @property
    def _titled_section(self) -> str:
        """Its block under its own ``### {name}`` heading, as a practice's scoped markdown shows it; empty when the
        practice document has no block for it."""
        body = self.section
        return f"### {self.name}\n\n{body}" if body else ""

    @markdown_collection
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Fidelity rules section."""

    @property
    def checked_rule_collections(self) -> list[RulesCollection]:
        """The rule collections a validate of this fidelity checks: its practice's shared rules, then its own, then each
        supplement's rules for it. A collection it shares with its practice is listed once."""
        practice = self.practice_guidance
        added = [collection for supplement in self.supplements for collection in supplement.rules_for(self)]
        collections = [practice.rules if practice is not None else None, self.rules, *added]
        return list({id(collection): collection for collection in collections if collection is not None}.values())

    @property
    def supplements(self) -> list[PracticeSupplement]:
        """The supplements of its practice that supplement this fidelity, such as TDD for BDD development."""
        practice = self.practice_guidance
        held = practice.working_set.supplements if practice is not None else ()
        return [supplement for supplement in held if self in supplement.supplemented_fidelities]

    @property
    def every_rule(self) -> list[Rule]:
        """Every rule of its practice, shared and each fidelity's: a saved graph holds the whole practice's hits, so a
        report on this fidelity still shows each hit's rule text; its own rules when it belongs to no practice."""
        practice = self.practice_guidance
        return practice.every_rule if practice is not None else super().every_rule

    @property
    def examples(self) -> str:
        """Its practice's examples at this fidelity, in the format it works in; none when it belongs to no practice."""
        practice = self.practice_guidance
        if practice is None:
            return ""
        return str(Markdown.from_label(practice, "examples", practice.scope_at(self).at(self.format)).extract() or "").strip()

    def generate_output(self) -> str:
        """What its practice tells the agent about writing this fidelity's artifact: the practice's generate_output
        recipe, expanded, so a practice that renders a format itself, such as Clean Engineering's draw.io, says so."""
        practice = self.practice_guidance
        return practice.instruction("generate_output").expand({}).instructions if practice is not None else ""

    def render(self, format: str, content: RenderContent = "", source: str | None = None) -> Rendered:
        """Render content into format at this fidelity, through its practice's formats: content is in source, else in
        the format this fidelity works in; with no content, its practice renders its own model. The practice is shared
        by every call in a session, so a call working at this fidelity asks this fidelity, never the practice."""
        return RenderRequest(Format(format), content, Format(source), fidelity=self).render()

    def render_files(self, format: str, paths: NamedPaths, source: str | None = None, previous: str = "") -> Rendered:
        """Render the files at paths into format at this fidelity (``RenderRequest.from_files``)."""
        return RenderRequest.from_files(self, format, paths, source, previous).render()

    def _guidance_parts(self) -> list[str]:
        """Its own guidance, then its Clean Engineering companion's instructions: what a practice working at this
        fidelity adds to its own guidance."""
        return [self.section_text("guidance").strip(), self.companion_instructions.strip()]

    @property
    def templates(self) -> str:
        """Its template in the format it works in, else in its default format."""
        return self._templates_in(self.format)

    def _templates_in(self, format: Format) -> str:
        """Its template in format, else in its default format: a companion writing a language it keeps no template for
        still shows its reference template in its default language."""
        located = self._template_markdown(format)
        return located.extract().strip() if located is not None else ""

    @property
    def template_file(self) -> Path | None:
        """The file its template is read from, in the format it works in, else its default format; none when it has
        no template."""
        located = self._template_markdown(self.format)
        return located.location.path if located is not None else None

    def _template_markdown(self, wanted: Format) -> Markdown | None:
        for format in [spelling for spelling in dict.fromkeys((wanted, self.default_format)) if spelling] or [""]:
            located = Markdown.from_label(self, "templates", MarkdownScope.of(self).at(format=format))
            path = located.location.path
            if path is not None and path.is_file():
                return located
        return None

    @cached_property
    def actions(self) -> FidelityActions:
        """The actions that work on this fidelity, each run on it: ``fidelity.actions.generate(format="drawio")``.
        The actions register with the action catalogue, so guidance names none of them."""
        return FidelityActions(self, ACTION_CATALOGUE)

    @property
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
        return "\n\n".join(part for part in (self.process, self.own_instructions) if part)

    @property
    def process(self) -> str:
        """The order of work its supplements give, such as TDD's flows: what to do first, ahead of any rule."""
        return "\n\n".join(supplement.process for supplement in self.supplements)

    def supplement_records(self, files: list[Path] | None = None) -> str:
        """What its supplements keep in the session about the files a generate or a render at this fidelity writes,
        such as TDD's test tiers of the module a test is for, with what each leaves the agent to decide. files are the
        files just saved; with none, each supplement reads the files the fidelity has in the session. Empty when no
        supplement keeps anything."""
        records = (supplement.records_for(self, files) for supplement in self.supplements)
        return "\n\n".join(record for record in records if record)

    @property
    def own_instructions(self) -> str:
        """Its instructions without its supplements' process, for a reply that gives that process once for several
        fidelities: its own words, then each supplement's section written for it."""
        added = (supplement.text_for(self) for supplement in self.supplements)
        return "\n\n".join(part for part in (self._instructions_in(self.format), *added) if part)

    def _instructions_in(self, format: Format) -> str:
        """Its instructions with its template in format: its own format for its own instructions, the code format of
        the fidelity it accompanies when it is a Clean Engineering companion."""
        return "\n\n".join(
            part
            for part in (
                self.schema_guide(),
                *self._practice_parts(),
                (self.overview or "").strip(),
                (self.guidance or "").strip(),
                (self.rules.markdown or "").strip(),
                self._template_part(format),
                self.companion_instructions,
            )
            if part
        )

    def _practice_parts(self) -> tuple[str, ...]:
        """What its practice says before its own words: the practice's overview, guidance, and shared rules; none when
        it belongs to no practice."""
        practice = self.practice_guidance
        if practice is None:
            return ()
        return (
            (practice.overview or "").strip(),
            practice.section_text("guidance").strip(),
            (practice.rules.markdown or "").strip(),
        )

    def _template_part(self, format: Format) -> str:
        """Its template in format under its own heading; none when it belongs to no practice or has no template."""
        templates = self._templates_in(format) if self.practice_guidance is not None else ""
        return f"#### Template\n\n{templates}" if templates else ""
