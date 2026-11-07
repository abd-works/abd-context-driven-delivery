# Practice Guidance — class model (model fidelity)

Markdown channel for `harness/guidance`. The module's purpose, seam, and dependencies are in [module-context.md](module-context.md); this document holds only its classes. *Markdown*, *MarkdownCollection*, and *YamlFields* belong to `harness/markdown`; the *Render* action to `cdd_guidance/actions/render`; *CleanEngineering* to `cdd_guidance/practices/clean_engineering`; *ToolCall* to `harness/agent_tools`; *Hook* and *HookPayload* to `harness/hooks`; *SessionLog* to `space/session`; *GuidanceProbe* and *GuidanceDiagnostics* to `harness/diagnostics`. They appear here only as names this module uses.

**Out of scope:** the guidance actions (`harness/guidance_actions`), each practice's own subclass and its `model/{format}/` adapters.

---

## Language companion

A *PracticeGuidance* reads its *FidelityGuidance* children from the Fidelities section of `{practice}/{practice}.md`; each fidelity's `stage`, `default_format`, `outputs`, and optional `clean_engineering` companion come from the YAML fields in its block, which *YamlFields* assigns. The practice keeps its current fidelity on `fidelities.current` (`work_at` makes one current), and each fidelity keeps the format it last used, so the practice's `format` is its current fidelity's. Callers convert artifacts through *Render*, which asks *PracticeGuidance.render*. A practice that owns an artifact keeps one adapter per format under `{practice}/model/{format}/` and passes them as `formats`; every practice CDD ships passes formats today; a practice with none renders through its current fidelity's Clean Engineering companion.

---

## Guidance

Base of every guidance class; an *AgentToolSet* through `@agent_toolset`.

Guidance(format)
------
format: str
	Invariant: an omitted format uses default_format
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
child_for_stage(stage: str): Guidance
	// raises KeyError when no child has that stage
child(name: str, body: str): FidelityGuidance

## PracticeGuidance : Guidance

PracticeGuidance(format, fidelity, default_workspace_folder, formats)
------
fidelities: GuidanceCollection
	// the Fidelities section; fidelities.current is the active fidelity
format: str
	Invariant: the current fidelity's format; the practice's own only while it has no current fidelity
	Invariant: a constructor format is the format the fidelity made current at construction works in
	Invariant: an unsupported fidelity or format raises ValueError at construction
graph: Graph | None
	// the graph that holds this practice; a session's practices are held by the session's graph
extended: PracticeGuidance | None
	// the practice extends names, held by reference from the same set of practices
formats: dict[str, Any]
	Invariant: keys are format names; values are adapters in {practice}/model/{format}/
supported_formats: frozenset
sketch_titles: tuple[str, ...]
	// the headings that open this practice's section of a sketch, such as "stories:"
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
clean_engineering_companion: FidelityGuidance | None
	-> fidelities.current.clean_engineering
guidance: str
	// practice guidance, the active fidelity's guidance, and the companion's instructions
instructions: str
	// schema guide, Guidance.instructions, every fidelity's instructions, and scoped_markdown
schema: str
	// {practice}/model/schema.yaml
examples: str
----
files(): dict[str, dict[str, list]]
	-> FidelityGuidance.files
output_paths(): dict[str, list[str]]
	-> fidelities.current.output_paths
work_in(session_output: PracticeSessionOutput): None
	// the practice works in that output's session; each fidelity is given its FidelitySessionOutput through FidelityGuidance.work_in
project_rules(): list[Rule]
	// .context/rules/{practice}/rules.md and its per-fidelity folders in the working folder
	-> ProjectRulesets.folders_for
	-> RulesCollection.from_markdown
schema_guide(): str
schema_node_fidelities(): dict[str, list[str]]
	// each schema node type with the fidelity that creates it and every higher one
schema_fidelity_errors(): list[str]
	// node fidelities the schema names that the practice does not have
domain_markdown_path(): Path
scoped_markdown(): str
	// overview, guidance, shared rules, language, and the active fidelity's block (every block when none is active)
generate_output(): str
	// instruction-only by default; a practice that owns generation overrides it
render(format: str, content: Any, source: str | None, previous: str): dict
	Interaction:
		# formats empty: hand the call to the companion's practice
		-> clean_engineering_companion.practice_guidance._render
		# otherwise: parse content into the object model, then render the target format
		-> formats[source or self.format].parse
		-> formats[format].render
read_paths(paths: list[str] | str, source: str | None): Any
	-> load_document
render_files(format: str, paths: list[str] | str, source: str | None): dict
	// a renderer that links to other files finds them in the folder of the first path
	-> read_paths
	-> render

## FidelityGuidance : Guidance

One fidelity of a practice, such as Stories' `story_map`.

FidelityGuidance(name, stage, default_format, clean_engineering)
------
name: str
stage: str
default_format: str
	// setting it sets format when no format has been chosen yet
outputs: dict[str, str | list[str]]
	// each format this fidelity writes, with its file, pattern, or folder
default_output: str | list[str]
format: str | None
	Invariant: the format this fidelity last used, kept in the session its practice works in, else its default
	Invariant: a Clean Engineering companion writes in the format of the fidelity it serves while that format is code
practice_guidance: PracticeGuidance | None
	// the nearest PracticeGuidance parent
clean_engineering: FidelityGuidance | None
	// the CleanEngineering fidelity named in the clean_engineering field; the companion records this fidelity in its `companion_of` field
	Invariant: Clean Engineering's own fidelities have none
companion_of: FidelityGuidance | None
	// set only on a Clean Engineering companion
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
instructions: str
	// practice overview, guidance, and shared rules, the companion's instructions, the template, and this fidelity's own text
----
work_in(session_output: FidelitySessionOutput): None
output_paths(): dict[str, list[str]]
	-> session_output.output_paths
files(): dict[str, list]
	-> session_output.files
has_declared_output(): bool
reports(): list[Path]
new_report_path(): Path
	// raises FidelityWithoutSessionError when the practice works in no session

## Rule

One named rule a practice or fidelity holds.

Rule(slug: str, body: str, fidelity: str | None, tag: str = "base")
------
slug: str
body: str
fidelity: str | None
tag: str
	// "base" or "project"
practice: str
pattern: str
shared: bool
----
attribute_to(practice: str, tag: str, shared: bool): Rule
validate(): str
	// the instructions to check the current context against this rule
from_bullet(text: str, fidelity: str | None): Rule

## RulesCollection : MarkdownCollection

A practice's or fidelity's rules with where they apply.

RulesCollection(entries, applies_to: AppliesTo | None, parent)
------
applies_to: AppliesTo
	// which edited files the rules apply to: always, or the files its glob patterns match
practice_key: str
fidelity_name: str
markdown_block: str
	// the original Rules markdown of the practice and its active fidelity
----
matches(path: str): bool
from_markdown(text: str, fidelity: str | None, parent): RulesCollection
formatted(): str
validate(): str
	// gathered from every rule
inject_rules(payload: HookPayload): dict
	// @Hook("postToolUse", disabled=True): the rules that apply to an edited file, as additional_context, with a read-only notice as the toast
	// notes the rules in the session open in the hook's project, even while the hook is disabled
	-> ToolCall(payload.tool_input, payload.project).session.log.injected_rules.note
scan(paths: Any): Any
	// none here; a practice's rules collection that scans files overrides it

## AppliesTo

AppliesTo(always_apply, globs)
------
always_apply: bool | None
globs: str
----
from_value(value: Any): AppliesTo
from_markdown(text: str): AppliesTo

## ProjectRulesets

The project's own rule folders, `.context/rules/{practice}/`.

ProjectRulesets(root: Path)
------
----
folders_for(practice: str): list[Path]

## PracticeCatalogue

Every practice CDD ships, in the order the approach walks them: Stories, DDD, UX, Clean Engineering, BDD.

PracticeCatalogue
------
----
keys(): tuple[str, ...]
	// imports no practice code
has(key: str): bool
practices(): tuple[PracticeGuidance, ...]
	// the shared instances
practice(key: str): PracticeGuidance
create(key: str): PracticeGuidance
	Invariant: outside a session, a caller that changes a practice's fidelity or format makes its own instance here; a session makes its set once with create_all
practice_class(key: str): type[PracticeGuidance]
module_of(key: str): str
practice_named(slug: str): PracticeGuidance | None
toolset_ref(slug: str): str | dict | None
	// the toolset ref a guidance action lists for a practice's or fidelity's slug, or a fidelity's bare name

## ActionCatalogue

Every action CDD ships, read from the folders under `cdd_guidance/actions`: each folder holds its toolset as the class of the folder's name in Pascal case, and each operation that toolset installs as a skill is one *Action*; a `@noDeploy` operation is not installed, so it is no action. A new action folder joins the catalogue by being there.

ActionCatalogue
------
----
toolsets(): tuple[type, ...]
	// imported on first use and kept for the process
actions(): tuple[Action, ...]
names(): tuple[str, ...]
has(name: str): bool
action(name: str): Action | None

## Action

One action CDD ships, such as generate, repair, or verify_fix. One toolset can install several.

Action(name: str, toolset_class: type)
------
name: str
toolset_class: type
toolset_ref: str
	// "{module}:{Class}" of the toolset
operation: Callable
folder: Path
	// the toolset's folder under cdd_guidance/actions
----

## ApproachStages

The stages of the CDD approach in the order it walks them. `STAGES` in `harness/guidance/stages.py` is the one instance; `DISCOVERY`, `SPECIFICATION`, and `IMPLEMENTATION` are the stage names each fidelity's **Stage:** gives.

ApproachStages(stages: tuple[ApproachStage, ...])
------
names: tuple[str, ...]
----
of(name: str): ApproachStage | None

## ApproachStage

One stage: its name, its title, its scope, and the actions a person runs on a fidelity in it. The session board's and the catalog's stage columns are each built on one.

ApproachStage(name: str, scope: StageScope)
------
name: str
title: str
scope: StageScope
steps: list[str]
	// generate, validate, review
actions: list[str]
	// the steps, then iterate, sketch, render, document
producing_actions: list[str]
	// every action but validate and review
----

## StageScope

How much of the solution a stage's work covers, from the whole solution (Discovery) to one story (Implementation).

StageScope(shape: str, name: str, reach: str, covers: str)
------
shape: str
name: str
reach: str
covers: str
----

## Schema

One practice's `model/schema.yaml` (or a pattern overlay's `rules.yaml`).

Schema(text: str)
Schema.load(path: Path): Schema
	// an empty schema when there is no file; each file is read once per process
------
types: dict[str, SchemaType]
----
fidelities(): dict[str, str]
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

## FidelityWithoutSessionError : ValueError

FidelityWithoutSessionError(slug: str)
------
----
