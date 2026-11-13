"""Assemble agent instructions from @markdown properties."""
from __future__ import annotations

import functools
import re
from dataclasses import replace
from pathlib import Path
from typing import Any, ClassVar

from harness.annotations.annotation import hosted_only
from harness.annotations.class_folder import class_folder
from harness.annotations.name import Name
from harness.guidance.action_catalogue import FidelityActions
from harness.guidance.practice_formats import PracticeFormats, RenderRequest
from harness.guidance.practice_reading import PracticeReading
from harness.guidance.rule import Rule, RulesCollection
from harness.guidance.schema import Schema
from harness.guidance.stages import STAGES, ApproachStage
from harness.agent_tools.agent_tools import (
    collect,
    agent_instructions,
    agent_tool,
    agent_toolset,
    instructions,
    toolset_collection,
)
from harness.installation.files import rules, skill
from harness.installation.data_class import data_field, identity
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


# The practice whose fidelities accompany other practices' fidelities, by its key: a fidelity's ``clean_engineering:``
# setting names the fidelity of this practice whose instructions join its own.
COMPANION_PRACTICE = "clean_engineering"


class SketchLens:
    """The section of a sketch that one practice writes, opened by the headings the practice declares, such as
    ``stories:``. Each practice holds its own (``PracticeGuidance.sketch_lens``), so a reader of a sketch asks the
    practice for it rather than naming the practice."""

    def __init__(self, titles: tuple[str, ...]) -> None:
        self.titles = titles

    def opens(self, title: str) -> bool:
        """True when this title is the section heading or marker this practice writes under."""
        return title.strip().lower() in self.titles


_DECLARED_PART = re.compile(r"(\{[^{}/]+\}/?|\*\*/|\*)")


class DeclaredFile:
    """A file a fidelity declares in its outputs, such as ``{bounded_context}/{aggregate}/{aggregate}.ts``, as a
    pattern that matches the end of a path. A named folder matches folders at any depth and a named part of a file name
    matches within it; a name used twice must be the same text both times, and ``**/`` and ``*`` keep their glob
    meaning."""

    def __init__(self, declared: str) -> None:
        self._declared = declared

    @functools.cached_property
    def glob(self) -> str:
        """The declared path as the glob a file search reads, which finds every file the pattern can match: a named
        folder is ``**/`` and a named part of a file name is ``*``. A path with no named parts stays the plain path."""
        folders = re.sub(r"\{[^{}/]+\}/", "**/", self._declared)
        return re.sub(r"\{[^{}/]+\}", "*", folders)

    @property
    def names_one_path(self) -> bool:
        """Whether the declared path is one plain path, with no named parts or wildcards."""
        return "*" not in self.glob

    @functools.cached_property
    def pattern(self) -> re.Pattern[str]:
        """The pattern, made once."""
        named: set[str] = set()
        parts = [self._part(token, named) for token in _DECLARED_PART.split(self._declared) if token]
        return re.compile(r"(?:^|/)" + "".join(parts) + "$", re.I)

    def _part(self, token: str, named: set[str]) -> str:
        """The pattern for one part; ``named`` holds the names earlier parts of the same path used."""
        if token == "**/":
            return r"(?:[^/]+/)*"
        if token == "*":
            return r"[^/]*"
        if not token.startswith("{"):
            return re.escape(token)
        name = re.sub(r"\W", "_", token.strip("{}/"))
        folder = "/" if token.endswith("/") else ""
        if name in named:
            return f"(?P={name}){folder}"
        named.add(name)
        return f"(?P<{name}>[^/]+(?:/[^/]+)*)/" if folder else f"(?P<{name}>[^/]+)"


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
        return MarkdownScope(folder, self.domain_slug or folder.name, format=self.format or None)

    def section_text(self, label: str) -> str:
        """The prose of one of its own labelled sections, such as its Overview, from the Markdown it keeps for that
        section, so a second read answers from the text the first read found."""
        return Markdown.held_by(self, label).extract()

    @markdownCollection("shared rules")
    @rules
    @agent_tool
    def rules(self) -> RulesCollection:
        """Shared rules as a collection."""

    session: Any = None
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

    def checked_rule_collections(self) -> list[RulesCollection]:
        """The rule collections a validate of this guidance checks: its own rules."""
        return [self.rules] if self.rules is not None else []

    def checked_rules(self) -> list[Rule]:
        """The rules a validate of this guidance checks, one by one."""
        return [rule for collection in self.checked_rule_collections() for rule in collection]

    def checked_rules_text(self) -> str:
        """The rules a validate of this guidance checks, as their markdown: what an agent judges against, and what an
        action that writes or fixes the artifact tells it to follow."""
        texts = (collection.validate.strip() for collection in self.checked_rule_collections())
        return "\n\n".join(text for text in texts if text)

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

    def rules_after_edit(self, payload: Any) -> str:
        """The rules an action hands the agent after the edit payload's hook names: the rules that apply to the edited
        file, else all of them; none while this guidance's rules hook is turned off."""
        rules = self.rules
        if rules is None or Hook.disabled_on(rules.inject_rules):
            return ""
        applied = (rules.inject_rules(payload).get("additional_context") or "").strip()
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
class GuidanceCollection(MarkdownCollection, Guidance):
    def __init__(self, entries: dict[str, Guidance] | None = None, parent: Any = None) -> None:
        MarkdownCollection.__init__(self, entries, parent=parent)
        Guidance.__init__(self)
        self.current: Guidance | None = None

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
    formats_type: type[PracticeFormats] = PracticeFormats
    """The kind of formats this practice holds: a practice whose formats read or convert in a way of their own names its
    own kind."""
    reading_type: type[PracticeReading] = PracticeReading
    """The kind of reading this practice takes part in the knowledge graph with: a practice that reads files from the
    working copy, or declares node types the graph treats in a way of their own, names its own kind."""
    extends: str = ""
    """The practice whose types this practice's schema builds on with ``is:``, such as a DDD entity that is a Clean
    Engineering class; its types also carry that practice's rules."""
    extended: PracticeGuidance | None = None
    """The practice whose types this practice's schema builds on, which ``extends`` names, held by reference: the one of
    the same set of practices, such as the session's Clean Engineering for its DDD."""
    companion: PracticeGuidance | None = None
    """The Clean Engineering practice whose fidelities accompany this practice's: the one of the set this practice was
    made with, which the catalogue hands it, so a companion works in the same session; none for a practice made apart
    from any set."""
    editor: ClassVar[Any] = None
    """The app that edits this practice's files beside the chat (an *App* of harness/diagnostics, which sits above this
    module, so it is not named here): the Story UI editor for Stories, none for every other practice. Every instance of the practice, in every session, edits with the same app, so the module that makes the
    app sets it on the practice's class (``Stories.editor = STORY_UI_APP``), and the framework and the practice import no
    app."""

    def __init__(
        self,
        format: str | None = None,
        fidelity: str | None = None,
        default_workspace_folder: str = ".",
        formats: dict[str, Any] | None = None,
    ) -> None:
        self._own_format = Format()
        super().__init__(format=format)
        self.default_workspace_folder = default_workspace_folder
        self.formats = self.formats_type(self, formats or {})
        self.reading = self.reading_type(self)
        # The fidelity a practice is made at is named by configuration, such as ``create("stories", fidelity="story_map")``;
        # it is looked up once here and stays the practice's current fidelity: an action that works at another fidelity
        # holds that fidelity itself, since every call in a session shares the session's practices. A format the
        # practice is made with is the one that fidelity works in.
        entries = self.fidelities.entries
        if fidelity is not None and entries and fidelity not in entries:
            raise ValueError(f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(entries)}")
        named = entries.get(fidelity) if fidelity is not None else None
        if named is not None:
            if self._own_format:
                named.format = self._own_format
            self.fidelities.current = named
        self.formats.check()

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

    @functools.cached_property
    def schema(self) -> Schema:
        """The practice's schema, ``model/schema.yaml`` beside its class, read once: the types it declares, the fidelity
        that creates each, and the text that tells an action the shape its output conforms to."""
        return Schema.load(self.module_dir / "model" / "schema.yaml")

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

    @classmethod
    def class_key(cls) -> str:
        """The key of the practice this class makes: the name of the folder it is defined in."""
        return class_folder(cls).name

    @property
    def set_keys(self) -> tuple[str, ...]:
        """The keys of the practices this one works with in its set: the one it extends and its Clean Engineering
        companion. The catalogue makes them with it when it makes this practice on its own."""
        return tuple(key for key in (self.extends, COMPANION_PRACTICE) if key and key != self.key)

    def hold_set(self, practices: dict[str, PracticeGuidance]) -> None:
        """Hold the practices of the set this one was made with, by key: the one it extends, and the Clean Engineering
        practice whose fidelities accompany its own, so it works with the same objects as the rest of its set."""
        if self.extends:
            self.extended = practices[self.extends]
        self.companion = practices.get(COMPANION_PRACTICE)

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

    def fidelity_called(self, name: str) -> FidelityGuidance | None:
        """The fidelity a person names by its bare name, as its practice document writes it (``story_map``) or in
        kebab case (``story-map``); none when this practice has no fidelity of that name."""
        return next((fidelity for fidelity in self.fidelities if name in (fidelity.name, Name(fidelity.name).kebab)), None)

    @property
    def fidelity_slugs(self) -> list[str]:
        """The slug of each of the practice's fidelities, such as `stories-story-map`, which a guidance action lists
        when it refuses a word no practice or fidelity has. Not sent as data: the session board sends each fidelity once,
        with its practice (`BoardFidelity`)."""
        return [fidelity.slug for fidelity in self.fidelities]

    def work_in(self, session_output: Any) -> None:
        """Work in the session that session_output, this practice's PracticeSessionOutput, belongs to: the practice
        knows that session, and each of its fidelities is given what it has there, so it answers its outputs, files and
        reports itself."""
        self.session = session_output.session
        self._session_output = session_output
        for fidelity in self.fidelities:
            fidelity.work_in(session_output.of_fidelity(fidelity))

    # The PracticeSessionOutput it works in, which work_in gives it; none until a session works on it.
    _session_output: Any = None

    @property
    def session_root(self) -> Path | None:
        """The folder the session this practice works in names for it, where it writes and the Graph app reads it from;
        none outside a session."""
        return None if self._session_output is None else self._session_output.folder

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
        scoped = self.scoped_markdown().strip()
        if scoped:
            instructions(scoped)
        if examples:
            instructions(examples)
        if templates:
            instructions(templates)
        # The practice's own Guidance section, then its current fidelity's guidance and companion text, which that
        # fidelity answers.
        current = self.fidelities.current
        parts = [self.section_text("guidance").strip(), *(current.guidance_parts() if current is not None else ())]
        return "\n\n".join(part for part in parts if part)

    @property
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
        parent_text = Guidance.instructions.fget(self)
        extra = self.fidelities.instructions if self.fidelities.entries else ""
        return "\n\n".join(part for part in (parent_text, extra, self.scoped_markdown()) if part)

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

    @agent_tool
    def render(self, format: str, content: Any = "", source: str | None = None, previous: str = "") -> dict:
        """Turn content into the practice object model, then render the target format. Content is in source, the
        format this practice works in when none is named; with no content, the practice renders its own model.
        previous is the target file as it is now. It renders at the fidelity the practice was made at, which renders
        it (``FidelityGuidance.render``); a practice with no fidelity renders through its formats."""
        current = self.fidelities.current
        if current is not None:
            return current.render(format, content, source, previous)
        return self.formats.render(RenderRequest(Format(format), content, Format(source), previous))

    def scoped_markdown(self) -> str:
        """Overview, practice sections, and the current fidelity's block, or every fidelity's when none is current."""
        parts = [self.section_text(label) for label in ("overview", "guidance", "shared rules", "language")]
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
        if COMPANION_PRACTICE in settings:
            self.clean_engineering = str(settings[COMPANION_PRACTICE] or "")
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

    _format: Format = Format()
    _default_format: Format = Format()

    @property
    def format(self) -> Format:
        """The format this fidelity works in: the one it was last given while that is still chosen in the session its
        practice works in, else the first format chosen there, else the one it was given or its default. A format it
        does not write, such as one an action names for a practice of its own, is worked in for as long as it is held."""
        chosen = self.session_output.chosen_formats if self.session_output is not None else []
        if not chosen or self._format in chosen or not self.offers(self._format):
            return self._format
        return Format(chosen[0])

    @format.setter
    def format(self, value: str | None) -> None:
        """Work in value from now on; in a session, a format the fidelity writes is chosen there too, so the next
        action on it works in it without being told."""
        self._format = Format(value)
        if self._format and self.session_output is not None and self.offers(self._format):
            self.session_output.choose_format(self._format, True)

    def offers(self, format: str) -> bool:
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

    def _first_word(self, value: str) -> str:
        return value.split()[0].strip("()`") if value.strip() else ""

    @property
    def clean_engineering(self) -> FidelityGuidance | None:
        """The Clean Engineering fidelity this fidelity's `clean_engineering:` field names, whose instructions join
        this fidelity's: that fidelity itself, of the Clean Engineering practice of its practice's set, held once it is
        first asked for. None when its field names none, or its practice was made apart from any set."""
        stored = getattr(self, "_clean_engineering", None)
        if isinstance(stored, FidelityGuidance):
            return stored
        practice = self.practice_guidance
        companion = practice.companion if practice is not None else None
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
        return companion.instructions_in(self.format if self.format.is_code else companion.format)

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

    def render(self, format: str, content: Any = "", source: str | None = None, previous: str = "") -> dict:
        """Render content into format at this fidelity, through its practice's formats: content is in source, else in
        the format this fidelity works in; with no content, its practice renders its own model. The practice is shared
        by every call in a session, so a call working at this fidelity asks this fidelity, never the practice."""
        return self.practice_guidance.formats.render(RenderRequest(Format(format), content, Format(source), previous, fidelity=self))

    def render_files(self, format: str, paths: list[str] | str, source: str | None = None) -> dict:
        """Render the files at paths into format at this fidelity, read from the project of the session its practice
        works in, in source, else in the format this fidelity works in. A renderer that links to other files, such as a
        story map linking to each story's file, finds them in the folder the first path is, or sits in."""
        formats = self.practice_guidance.formats
        request = RenderRequest(Format(format), source=Format(source), folder=_folder_of(paths), fidelity=self)
        return formats.render(replace(request, content=formats.read(paths, request)))

    def guidance_parts(self) -> list[str]:
        """Its own guidance, then its Clean Engineering companion's instructions: what a practice working at this
        fidelity adds to its own guidance."""
        return [self.section_text("guidance").strip(), self.companion_instructions.strip()]

    @property
    def templates(self) -> str:
        """Its template in the format it works in, else in its default format."""
        return self.templates_in(self.format)

    def templates_in(self, format: Format) -> str:
        """Its template in format, else in its default format: a companion writing TypeScript still shows Clean
        Engineering's reference template when no TypeScript one exists."""
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
        return self.instructions_in(self.format)

    def instructions_in(self, format: Format) -> str:
        """Its instructions with its template in format: its own format for its own instructions, the code format of
        the fidelity it accompanies when it is a Clean Engineering companion."""
        practice = self.practice_guidance
        parent = ()
        templates = ""
        if practice is not None:
            parent = (
                (practice.overview or "").strip(),
                practice.section_text("guidance").strip(),
                (practice.rules.markdown or "").strip(),
            )
            templates = self.templates_in(format)
            if templates:
                templates = f"#### Template\n\n{templates}"
        return "\n\n".join(
            part
            for part in (
                self.schema_guide(),
                *parent,
                (self.overview or "").strip(),
                (self.guidance or "").strip(),
                (self.rules.markdown or "").strip(),
                templates,
                self.companion_instructions,
            )
            if part
        )
