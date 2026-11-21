# Practice Guidance — class model (model fidelity)

Markdown channel for `harness/guidance`. The module's purpose, seam, and dependencies are in [module-context.md](module-context.md); this document holds only its classes. *Markdown*, *MarkdownCollection*, *MarkdownScope*, and *MarkdownText* belong to `harness/markdown`; the *Render* action to `cdd_guidance/actions/render`; *CleanEngineering* to `cdd_guidance/practices/clean_engineering`; *ToolCall* to `harness/agent_tools`; *Hook* and *HookPayload* to `harness/hooks`; *SessionLog* to `space/session`; *GuidanceProbe* and *GuidanceDiagnostics* to `harness/diagnostics`. They appear here only as names this module uses.

**Out of scope:** the guidance actions (`harness/guidance_actions`), each practice's own subclass and its `model/{format}/` adapters.

---

## Language companion

A *PracticeGuidance* reads its *FidelityGuidance* children from the Fidelities section of `{practice}/{practice}.md`; each fidelity's `stage` (held as its *ApproachStage*), `default_format`, `outputs`, `judged_on`, and optional `clean_engineering` companion come from the YAML fields in its block, which the fidelity applies itself when its block makes it (`FidelityGuidance.from_block`). The practice holds its document (`document`, read once), and each fidelity reads its block, its instructions, rules, templates, template file, and declared files from itself, so an action holding a fidelity reads only that fidelity's text whatever fidelity is current. Each guidance hands its *Markdown* a *MarkdownScope*: its folder, slug, fidelity, and format. The practice's current fidelity, `fidelities.current`, is fixed at construction: a session's practices are shared by every call in it, so an action holds the fidelity it works at and never moves the practice's. Each fidelity keeps the format it last used, so the practice's `format` is its current fidelity's. Callers convert artifacts through *Render*, which asks the fidelity the action works at (*FidelityGuidance.render* or *render_files*); that fidelity hands its practice a *RenderRequest* that carries it. A practice that owns an artifact keeps one adapter per format under `{practice}/model/{format}/` and passes them as `formats`; every practice CDD ships passes formats today; a practice with none renders through the Clean Engineering companion of the fidelity the request works at (`RenderRequest.companion`, which is `FidelityGuidance.clean_engineering`).

---

## Guidance

Base of every guidance class; an *AgentToolSet* through `@agent_toolset`.

Guidance(format)
------
format: Format
	Invariant: an omitted format uses default_format
	// a Format is its own name as text, made once from the spelling given and held
default_format: str
session: Session | None
	// the session work_in gives a practice; none until a session works on it
name: str | None
slug: str
registration_name: str
install_folder: Path
module_dir: Path
overview: str
guidance: str
templates: str
sketch_template: str
	// every *-sketch.* file in the practice's templates folder
rules: RulesCollection
	// the "shared rules" section
instructions: str
	// overview, guidance, rules, and templates joined; published as a skill and an MCP prompt

## GuidanceCollection : MarkdownCollection, Guidance

A practice's fidelities, read as one collection; `@collect` gathers each member across the children.

GuidanceCollection(entries: dict[str, Guidance] | None, parent: Any)
------
current: Guidance | None
overview, guidance, rules, templates, instructions
	// gathered from every child
----
child(name: str, body: str): FidelityGuidance
	-> FidelityGuidance.from_block

## PracticeGuidance : Guidance

One practice: its identity, its words, its fidelities, and its set. It holds three parts, each made once at construction:
its formats, its part in the knowledge graph, and its schema.

PracticeGuidance(format, fidelity)
------
default_workspace_folder: str
	// a class attribute each practice sets, such as "tests" for Stories
first_fidelity: str | None
	// a class attribute: the fidelity a practice made without naming one starts at, such as "bounded_context" for DDD; a constructor given fidelity=None starts at no fidelity
format_adapters: dict[str, Any]
	// a class attribute: the parse and render adapter of each format the practice owns
domain_markdown_path: Path
scoped_markdown: str
	// overview, guidance, shared rules, language, and the active fidelity's block (every block when none is active)
fidelities: GuidanceCollection
	// the Fidelities section; fidelities.current is the active fidelity
format: Format
	Invariant: the current fidelity's format; the practice's own only while it has no current fidelity
	Invariant: a constructor format is the format the fidelity made current at construction works in
	// the fidelity a constructor names is looked up once, at construction, and stays current: an action holds the fidelity it works at
formats: PracticeFormats
	// made once from the adapters the constructor names, as the kind formats_type names
reading: PracticeReading
	// made once, as the kind reading_type names; the graph that holds the practice talks to it
schema: Schema
	// {practice}/model/schema.yaml, read once
working_set: WorkingSet
	// made once, as the kind working_set_type names: the practices of its set it works with
	Invariant: an unsupported fidelity or format raises ValueError at construction
extends: str
sketch_lens: SketchLens
	// the headings that open this practice's section of a sketch, such as "stories:"; the practice holds the one lens its sketch format reads its section with
SHORT_NAME: str
	// the practice's name where there is little room, such as "CE" on a session board chip
COLOUR: str
	// the colour a session board draws the practice's chips and tiles in
key: str
	// the practice folder name, such as clean_engineering
practice_slug: str
short_name: str
colour: str
fidelity_slugs: list[str]
	// the slugs a guidance action lists when it refuses a word; not data: the board sends each fidelity once
guidance: str
	// practice guidance, the active fidelity's guidance, and the companion's instructions
instructions: str
	// Guidance.instructions (its schema guide first), every fidelity's instructions, and scoped_markdown
examples: str
----
answers_to(slug: str): PracticeGuidance | FidelityGuidance | None
	// itself for its slug, the fidelity whose slug it is, else none
work_in(session_output: PracticeSessionOutput): None
	// the practice works in that output's session; each fidelity is given its FidelitySessionOutput through FidelityGuidance.work_in
generate_output(): str
	// instruction-only by default; a practice that owns generation overrides it
render(format: str, content: RenderContent, source: str | None, previous: str): dict
	// at the fidelity the practice was made at, which renders it; a practice with no fidelity renders through its formats
	-> fidelities.current.render
	-> formats.render

## WorkingSet

The practices one practice works with, held by reference from the set it was made with. The catalogue that makes a set hands each practice's working set the set; a practice made apart from any set holds none of them.

WorkingSet(practice: PracticeGuidance)
------
extended: PracticeGuidance | None
	// the practice its practice's extends names, from the same set of practices
companion: PracticeGuidance | None
	// the Clean Engineering practice of the set; none for a practice made apart from any set
supplements: list[PracticeSupplement]
	// the supplements of its set whose supplemented_practices hold its practice, by reference
names: tuple[str, ...]
	// the names of the practices it works with in its set: the one its practice extends and its Clean Engineering companion
----
hold(practices: Mapping[str, PracticeGuidance], supplements: Sequence[PracticeSupplement]): None
	// holds the practice its practice extends, its Clean Engineering companion, and each supplement whose supplemented_practices hold its practice

## SupplementWorkingSet : WorkingSet

A supplement's working set: beside the practices it works with, it reads the fidelities its supplement names into the set's own.

SupplementWorkingSet(practice: PracticeSupplement)
------
----
hold(practices: Mapping[str, PracticeGuidance], supplements: Sequence[PracticeSupplement]): None
	-> WorkingSet.hold
	-> PracticeSupplement.hold_supplemented

## PracticeSupplement : PracticeGuidance

Guidance that adds to other practices at the fidelities it names, such as TDD on Clean Engineering code, Stories acceptance_tests, BDD development, and DDD tactics. It is a practice of its own (its folder sits with the practices), but it has no stage and no fidelities on the board: it never moves work forward, it only adds guidance and rules to the fidelities it supplements. Its markdown's front matter names them:

```yaml
always_apply: true
supplements:
  clean_engineering: code
  stories: acceptance_tests
  bdd: development
  ddd: tactics
```

Its markdown keeps the usual Overview and Guidance, then sections headed with the slugs of the fidelities they apply to (`## bdd-development`, or `## stories-acceptance-tests, bdd-development` for rules both share), each with its guidance and a `### Rules` list. It has no rules for every fidelity it supplements: each rule names the fidelities it is for. Its graph rules live in its own folder the way a pattern's do: `rules/` for one rule checked on several named practices (*SharedPracticeGraphRule*), and `practices/<practice>/rules` and `model/{schema,rules}.yaml` for those of one practice.

PracticeSupplement(format)
------
supplemented_fidelities: list[FidelityGuidance]
	// the fidelities it supplements (named apart from its working set's supplements): the same set's own FidelityGuidance objects, held by reference once its working set is handed the set, such as bdd.fidelities["development"]
	Invariant: the front matter's names are read once, in hold_supplemented, into the set's objects; nothing after holds a practice name or fidelity name as text
	Invariant: a name with no practice in the set, or no such fidelity on that practice, raises UnknownSupplementedFidelity in hold_supplemented
supplemented_practices: list[PracticeGuidance]
	// the practice of each fidelity it supplements, once each: each fidelity's practice_guidance
always_apply: bool
	// on for every session without being chosen; a supplement that is not always on applies only when a session's overlays name it
graph_overlay: GraphOverlay
	// on a subclass that checks graph rules, made once, as a pattern makes its own: harness/guidance imports no graph
----
hold_supplemented(practices: Mapping[str, PracticeGuidance]): None
	// resolves the front matter's practice and fidelity names into the set's own fidelities, once; its working set calls it
	-> practices[key].fidelities.called(name)
text_for(fidelity: FidelityGuidance): str
	// its Overview and Guidance, then each section whose heading names that fidelity's slug, headed "## Supplement: {name}"; empty for a fidelity it does not supplement
rules_for(fidelity: FidelityGuidance): list[RulesCollection]
	// the Rules of each section whose heading names that fidelity's slug; empty for a fidelity it does not supplement
instructions: str
	// read on its own (its skill and MCP prompt): its Overview, its Guidance, then every section named for a fidelity
checked_rule_collections: list[RulesCollection]
	// the Rules of every section named for a fidelity; it has no Shared rules
every_rule: list[Rule]

## PracticeFormats

The formats one practice reads and writes, each through its adapter. A practice whose formats convert in a way of their
own names its own kind (DDD's *DddFormats*, Stories' *StoriesFormats*).

PracticeFormats(practice: PracticeGuidance, adapters: dict[str, Any])
------
supported: frozenset[Format]
suffixes: frozenset[str]
	// every file extension one of its adapters reads
adapter_settings: dict[str, Any]
	// what an adapter's constructor is handed when it takes it: tests_root, and Stories' story_test_folder
----
check(): None
	// ValueError for a format the practice works in but does not write
adapter_class(format: str): Any
	// imported once
adapter(format: str): Any
	// made once and kept
reading(file: Path): Format | None
reading_with(file: Path, others: Iterable[PracticeGuidance]): Format | None
for_file(file: Path): Any
	// a new model of the format that reads the file
read(paths, request: RenderRequest): Any
	// what a render converts from files: their text, read through the session's project
render(request: RenderRequest): dict
	Interaction:
		# no adapters: hand the request to the companion's practice
		-> request.companion.practice_guidance.formats.render
		# otherwise: read content into the object model, then render the target format
		-> parse
		-> model_for
		-> adapter(request.format).render
parse(format: Format, content: Any): Any
model_for(target: Any, model: Any): Any

## PracticeReading

How one practice takes part in the knowledge graph. It lives in harness/graph (`harness/graph/practice_reading.py`, described in `harness/graph/.context/graph-populate-model.md`), which sits above this module: *PracticeGuidance* names its kind as `reading_type: type | None`, harness/graph sets the default when it is imported, and the practice makes its reading the first time it is asked (`practice.reading`).

## FidelityGuidance : Guidance

One fidelity of a practice, such as Stories' `story_map`.

FidelityGuidance(name, stage)
------
name: str
stage: str
default_format: Format
	// setting it sets format when no format has been chosen yet
outputs: dict[str, str | list[str]]
	// each format this fidelity writes, with its file, pattern, or folder
format: Format
	Invariant: the format this fidelity last used, kept in the session its practice works in, else its default
practice_guidance: PracticeGuidance | None
	// the nearest PracticeGuidance parent
clean_engineering: FidelityGuidance | None
	// the Clean Engineering fidelity its clean_engineering field names: that fidelity itself, of its practice's companion
	Invariant: Clean Engineering's own fidelities have none; a practice made apart from any set has none
companion_instructions: str
	// the companion's _instructions_in this fidelity's format while it is code, else the companion's own format
_instructions_in(format: Format): str
	// its instructions with its template in format; instructions is _instructions_in(format)
_templates_in(format: Format): str
session_output: FidelitySessionOutput | None
	// set when a session works on the practice
slug: str
	// "{practice slug}-{fidelity name}"
install_folder: Path
overview: str
scaffold: str
section: str
	// the whole ### {name} block in the practice markdown
guidance: str
rules: RulesCollection
	// the fidelity's Rules section
supplements: list[PracticeSupplement]
	// its practice's supplements that hold this fidelity among their supplements, such as TDD for BDD development
	-> practice_guidance.working_set.supplements
	Invariant: a supplement supplements this fidelity exactly when this object is in supplement.supplemented_fidelities
instructions: str
	// practice overview, guidance, and shared rules, the companion's instructions, the template, this fidelity's own text, then each supplement's text for it
	-> PracticeSupplement.text_for
templates: str
	// its template in the format it works in, else its default format
examples: str
	// its practice's examples at this fidelity and format
checked_rule_collections: list[RulesCollection]
	// the practice's shared rules, then its own, then each supplement's rules for this fidelity
	-> PracticeSupplement.rules_for
every_rule: list[Rule]
	-> practice_guidance.every_rule
declared: DeclaredOutputs
	// the files its outputs declare, made again whenever its outputs change
----
generate_output(): str
	// the practice's generate_output recipe, expanded
render(format: str, content: RenderContent, source: str | None): dict
	// at this fidelity: content is in source, else in this fidelity's format
	-> practice_guidance.formats.render RenderRequest(fidelity=self)
render_files(format: str, paths: list[str] | str, source: str | None): dict
	// a renderer that links to other files finds them in the folder of the first path
	-> practice_guidance.formats.read
	-> practice_guidance.formats.render RenderRequest(fidelity=self)
work_in(session_output: FidelitySessionOutput): None
	// its reports and where a new one goes are its session output's: session_output.validation_reports.listed(), validation_reports.new_path()

## DeclaredOutputs

The files one fidelity declares, made from its outputs. The fidelity holds it (`fidelity.declared`).

DeclaredOutputs(fidelity: FidelityGuidance, outputs: dict[str, str | list[str]])
------
outputs: dict[str, str | list[str]]
----
includes(path: str, format: str = ""): bool
	// a file one of its outputs names, in format when one is named; DeclaredFile matches the end of the path
output_paths(): dict[str, list[str]]
	-> fidelity.session_output.written.output_paths
files(): dict[str, list[SessionFile]]
	-> fidelity.session_output.written.files
has_output(): bool
files_to_review(): dict[str, list]
	// its fidelity's own files, or those of the fidelities it reviews files of, each file once

## Rule

One named rule a practice or fidelity holds.

Rule(slug: str, body: str, fidelity: str | None)
------
slug: str
body: str
fidelity: str | None
practice: str
pattern: str
shared: bool
----
validate(): str
	// the instructions to check the current context against this rule
_from_bullet(text: str, fidelity: str | None): Rule

## RulesCollection : MarkdownCollection

A practice's or fidelity's rules with where they apply.

RulesCollection(entries, applies_to: AppliesTo | None, parent)
------
applies_to: AppliesTo
	// which edited files the rules apply to: always, or the files its glob patterns match
practice_key: str
fidelity_name: str
----
matches(path: str): bool
from_markdown(text: str, fidelity: str | None, parent): RulesCollection
formatted(): str
validate(): str
	// gathered from every rule
inject_rules(tool_use: HookPayload): dict
	// @Hook("postToolUse", disabled=True): the rules that apply to an edited file, as additional_context, with a read-only notice as the toast
	// notes the rules in the session open in the hook's project, even while the hook is disabled
	-> ToolCall(tool_use.tool_input, tool_use.project).session.log.injected_rules.note

## AppliesTo

AppliesTo(always_apply, globs)
------
always_apply: bool | None
globs: str
----
from_value(fence_fields: AppliesTo | dict[str, object] | None): AppliesTo
from_markdown(text: str): AppliesTo

## PracticeCatalogue

Every practice CDD ships, in the order the approach walks them: Stories, DDD, UX, Clean Engineering, BDD. The package that defines the practices registers their classes with the process's one catalogue, `PRACTICE_CATALOGUE`, when it is imported; the framework names none of them. Its classes are kept in a *ClassRegistry* (harness/annotations), the one registry the practices, the actions, and the patterns register with.

PracticeCatalogue
------
names: tuple[str, ...]
	// each practice's name, its folder's name; PracticesNotRegistered when no package registered the practices in this process
practice_classes: tuple[type[PracticeGuidance], ...]
supplement_classes: tuple[type[PracticeSupplement], ...]
----
register(*practice_classes: type[PracticeGuidance])
	// called by cdd_guidance/practices when it is imported; each class by its name (its folder's name)
has(name: str): bool
	// the catalogue holds classes only: every reader makes its own practices and holds them
create(name: str): PracticeGuidance
	Invariant: outside a session, a caller that changes a practice's fidelity or format makes its own instance here; a session makes its set once with create_all
	// made with the practices of its set it works with (working_set.names), each holding the others (working_set.hold)
register_supplements(*supplement_classes: type[PracticeSupplement])
	// called by cdd_guidance/practices when it is imported; held apart from the practices, so names and the board never list a supplement
create_all(): PracticeSet
	// also makes one of each registered supplement that is always on; each supplement's working set holds the set first, then each practice's holds the set and the supplements
	-> SupplementWorkingSet.hold
	-> WorkingSet.hold
	// each practice holds the one it extends and the Clean Engineering practice whose fidelities accompany its own, from the same set
practice_class(name: str): type[PracticeGuidance]

## PracticeSet

One set of practices a reader made and holds, in catalogue order. It answers which of its practices or fidelities a slug names, so every reader that reads a slug asks its own set once.

PracticeSet(practices: Iterable[PracticeGuidance]) : Sequence[PracticeGuidance]
------
slugs: list[str]
	// each practice's slug, then each of its fidelities'
----
answering(slug: str): PracticeGuidance | FidelityGuidance | None
	// the practice or fidelity whose slug it is
	-> PracticeGuidance.answers_to
practice_answering(slug: str): PracticeGuidance | None
	// the practice the slug names, by its own slug or a fidelity's
named(slug: str): PracticeGuidance | FidelityGuidance | None
	// answering, else a fidelity by its bare name
	-> GuidanceCollection.called

## ActionCatalogue

Every action CDD ships, held once per process as `ACTION_CATALOGUE`: `cdd_guidance/actions` registers each action folder's toolset when it is imported, and each operation that toolset installs as a skill is one *Action*; a `@noDeploy` operation is not installed, so it is no action. A new action folder joins the catalogue by being there. harness/guidance_actions registers how an action runs on a fidelity (`run_actions_with`).

ActionCatalogue
------
toolsets: tuple[type, ...]
	// the registered toolsets, kept in a ClassRegistry
actions: tuple[Action, ...]
	// made once from the registered toolsets, each holding this catalogue
names: tuple[str, ...]
_registered_runner: ActionRunner
	// ActionsNotRegistered while no runner is registered
_fidelity_actions: tuple[Action, ...]
	// the actions the runner runs on a fidelity
----
register(*toolset_classes: type)
	// called by cdd_guidance/actions when it is imported
run_actions_with(runner: ActionRunner): None

## Action

One action CDD ships, such as generate, repair, or verify_fix. One toolset can install several.

Action(name: str, toolset_class: type, catalogue: ActionCatalogue)
------
name: str
toolset_class: type
	// "{module}:{Class}" of the toolset
operation: Callable
folder: Path
	// the toolset's folder under cdd_guidance/actions
----
_run_on(fidelity: WorkedFidelity, **arguments): Any
	// through the runner the catalogue that made it holds
	-> ActionCatalogue._registered_runner

## ApproachStages

The stages of the CDD approach in the order it walks them. `STAGES` in `harness/guidance/stages.py` is the one instance; `DISCOVERY`, `SPECIFICATION`, and `IMPLEMENTATION` are the stage names each fidelity's **Stage:** gives.

ApproachStages(stages: tuple[ApproachStage, ...])
------
names: tuple[str, ...]
----
of(name: str): ApproachStage | None

## ApproachStage

One stage: its name, its title, its scope, and the actions a person runs on a fidelity in it. The session board's and the catalog's stage columns are each built on one.

One stage reads its actions from the action catalogue: each action's operation carries an `@on_stage` annotation (*OnStage*) saying where it sits, which the stage reads back with `OnStage.recorded_on`, so no list of action names is kept here.

ApproachStage(name: str, scope: StageScope, catalogue: ActionCatalogue)
------
name: str
title: str
scope: StageScope
steps: list[str]
	// the actions annotated on_stage(rank, STEP), in rank order: generate, validate
actions: list[str]
	// every action annotated on_stage, in rank order: partition, generate, validate, iterate, sketch, render, document
producing_actions: list[str]
	// every one but those that check a fidelity's files (on_stage(rank, CHECKS)): every action but validate
actions_with_formats: list[str]
	// those annotated on_stage(rank, TAKES_FORMATS): generate, render
----

## OnStage : Annotation

The annotation on an action's operation that says where it sits among the actions a person runs on a fidelity in its stage, typed `@on_stage(rank, *traits)` with the traits `STEP`, `TAKES_FORMATS`, and `CHECKS`, as `@on_stage(1, STEP, TAKES_FORMATS)` on generate.

OnStage(rank: int, *traits: str)
------
rank: int
step: bool
takes_formats: bool
checks: bool
----

## StageScope

How much of the solution a stage's work covers, from the whole solution (Discovery) to one story (Implementation).

StageScope(shape: str, name: str, reach: str, covers: str = "")
------
shape: str
name: str
reach: str
covers: str
	// what its work decides, such as `outcomes · scope · boundaries`; empty unless the scope was made with it


## Schema

One practice's `model/schema.yaml` (or a pattern overlay's `rules.yaml`).

Schema(text: str)
Schema.load(path: Path): Schema
	// an empty schema when there is no file; each file is read once per process
------
types: dict[str, SchemaType]
----
_fidelities(): dict[str, str]
rules(): dict[str, tuple[str, ...]]

## SchemaType

SchemaType(key: str)
------
key: str
fields: list[tuple[str, str]]
rules: list[str]
fidelity: str
supertype: str
----
field(name: str): str

## load_document

`load_document(content: str = "", paths: list[str] | str | None = None): str` in `documents.py`: the document a call names, read from the files at paths, so an MCP call carries no body.

