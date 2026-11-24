# harness/guidance

A *PracticeGuidance* is one practice: its *FidelityGuidance* fidelities, its *Rule* lists, templates, and examples, read from its markdown, and three parts made once (*PracticeFormats*, *PracticeReading*, *Schema*). *PracticeCatalogue* and *ActionCatalogue* are registries the practices and actions join when their packages are imported; *ApproachStage* is a stage of the approach. The whole model of this module, internals included, is `harness/guidance/.context/practice-guidance-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Let a practice be one class plus its markdown, with fidelities, rules, templates, and examples an agent can follow and a validator can check against.
- **Seam (terms):** Guidance, PracticeGuidance, FidelityGuidance, GuidanceCollection, SketchLens, DeclaredFile, PracticeFormats, RenderRequest, PracticeReading, Rule, RulesCollection, Schema, PracticeCatalogue, UnknownPractice, ActionCatalogue, Action, ApproachStage, StageScope; `STAGES`, `DISCOVERY`, `SPECIFICATION`, `IMPLEMENTATION`, `GENERATE`, `VALIDATE`, `RENDER`, `REVIEW`; `load_document`, `document_in`, `rules_in`
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown, harness/installation, harness/hooks, harness/mcp

## Guidance : AgentToolSet

Words and rules an agent follows, read from markdown beside the class.

+ Guidance(format: str | None = None)
------
+ default_format: str
+ name: str | None
+ domain_slug: str | None
+ format: str | None
+ session: Any
+ module_dir: Path
+ markdown_scope: MarkdownScope
+ overview: str
+ guidance: str
+ << aggregation >> listed_rules: list[Rule]
+ sketch_template: str
+ schema: Schema
+ instructions: str
+ checked_rule_collections: list[RulesCollection]
+ every_rule: list[Rule]
----
+ section_text(label: str): str
+ rules(): RulesCollection
+ checked_rules(): list[Rule]
+ checked_rules_text(): str
+ templates(): str
+ rules_after_edit(payload: Any): str
+ schema_guide(): str
---<<loads the prose it needs through>>--> Markdown
---<<published as rules by>>--> Rules
---<<published as a skill by>>--> Skill
---<<published as an MCP prompt by>>--> Mcp
---<<creates>>--> Name

## PracticeGuidance : Guidance

One practice as a class plus its markdown: its identity, overview, shared rules, fidelities, templates, examples, and the set of practices it works with. It holds three parts, each made once: its formats, its part in the knowledge graph, and its schema.

+ PracticeGuidance(format: str | None = None, fidelity: str | None = None)
------
+ sketch_lens: SketchLens
+ SHORT_NAME: str
+ COLOUR: str
+ shows_every_fidelity: bool
+ formats_type: type[PracticeFormats]
+ reading_type: type[PracticeReading]
+ extends: str
+ << association >> extended: PracticeGuidance | None
+ << association >> companion: PracticeGuidance | None
+ default_workspace_folder: str
+ format_adapters: dict[str, Any]
+ << composition >> formats: PracticeFormats
+ << composition >> reading: PracticeReading
+ format: Format
+ markdown_scope: MarkdownScope
+ document: MarkdownText
+ << composition >> schema: Schema
+ set_keys: tuple[str, ...]
+ key: str
+ practice_slug: str
+ short_name: str
+ colour: str
+ fidelity_slugs: list[str]
+ guidance: str
+ instructions: str
+ checked_rule_collections: list[RulesCollection]
+ every_rule: list[Rule]
+ domain_markdown_path: Path
+ scoped_markdown: str
----
+ claims(file: Path): bool
+ rules(): RulesCollection
+ hold_set(practices: dict[str, PracticeGuidance], supplements: list[Any] | None = None): None
+ answers_to(slug: str): PracticeGuidance | FidelityGuidance | None
+ work_in(session_output: Any): None
+ generate_output(): str
+ fidelities(): GuidanceCollection
+ examples(): str
+ render(format: str, content: Any = '', source: str | None = None, previous: str = ''): dict
	-> PracticeFormats.render
---<<creates>>--> PracticeFormats
---<<creates>>--> PracticeReading
---<<creates>>--> Schema
---<<creates>>--> RenderRequest
---<<creates>>--> Format
---<<loads>>--> GuidanceCollection
---<<loads>>--> RulesCollection
---<<keeps>>--> SketchLens
---<<annotated with>>--> Identity
---<<annotated with>>--> HostedOnly

## FidelityGuidance : Guidance

One fidelity of a practice, such as the story map: its stage, its outputs, its rules, its template, and the actions that work on it.

+ FidelityGuidance(name: str = '', stage: str = '')
------
+ session_output: Any
+ judged_on: str
+ name: str
+ stage: str
+ approach_stage: ApproachStage | None
+ is_judged_on_graph: bool
+ outputs: dict[str, str | list[str]]
+ << composition >> declared: DeclaredOutputs
+ << association >> practice_guidance: PracticeGuidance | None
+ format: Format
+ default_format: Format
+ << association >> clean_engineering: FidelityGuidance | None
+ companion_instructions: str
+ slug: str
+ markdown_scope: MarkdownScope
+ module_dir: Path
+ install_folder: Path
+ scaffold: str
+ section: str
+ titled_section: str
+ examples: str
+ templates: str
+ template_file: Path | None
+ << composition >> actions: FidelityActions
+ instructions: str
+ checked_rule_collections: list[RulesCollection]
+ every_rule: list[Rule]
----
+ from_block(name: str, body: str = ''): FidelityGuidance
+ work_in(session_output: Any): None
+ schema_guide(): str
+ rules(): RulesCollection
+ generate_output(): str
+ render(format: str, content: Any = '', source: str | None = None): dict
+ render_files(format: str, paths: list[str] | str, source: str | None = None, previous: str = ''): dict
	// previous is the target file as it is now, whose layout a diagram keeps
+ guidance_parts(): list[str]
---<<reads its stage from>>--> ApproachStage
---<<runs actions through>>--> ActionCatalogue
---<<renders through the formats of>>--> PracticeGuidance
---<<creates>>--> RenderRequest
---<<creates>>--> Format
---<<creates>>--> MarkdownText
---<<creates>>--> Name
---<<holds the files it declares in>>--> DeclaredOutputs
---<<annotated with>>--> Identity

## GuidanceCollection : MarkdownCollection, Guidance

A practice's fidelities, read from its markdown, published together, with the one it is at now (`current`).

+ GuidanceCollection(entries: dict[str, Guidance] | None = None, parent: Any = None)
------
+ << association >> current: Guidance | None
----
+ child(name: str, body: str = ''): FidelityGuidance
+ called(name: str): FidelityGuidance | None
+ overview(): str
+ guidance(): str
+ rules(): RulesCollection
+ templates(): str
+ instructions(): str
---<<creates>>--> FidelityGuidance
---<<annotated with>>--> ToolSetCollectionAnnotation
---<<joins its children's properties with>>--> Collect

## SketchLens

A practice's section of a sketch: the headings that open it, lower case, such as `stories:`.

+ SketchLens(titles: tuple[str, ...])
------
+ titles: tuple[str, ...]
----
+ opens(title: str): bool

## DeclaredFile

A path a fidelity declares as its output, as a glob over the session's current root, so a session's output makes one for a declared path.

+ DeclaredFile(declared: str)
------
+ glob: str
+ names_one_path: bool
+ pattern: re.Pattern[str]
----
+ parts_of(path: str): dict[str, str]
+ named_with(parts: dict[str, str]): str

## DeclaredOutputs

The files one fidelity declares, made from its outputs: whether a path is one of them, and where they are in the session its practice works in.

+ DeclaredOutputs(fidelity: FidelityGuidance, outputs: dict[str, str | list[str]])
------
+ outputs: dict[str, str | list[str]]
----
+ includes(path: str, format: str = ''): bool
+ output_paths(): dict[str, list[str]]
+ files(): dict[str, list]
+ has_output(): bool
+ files_to_review(): dict[str, list]
+ file_name_beside(source: str, format: str): str
	// the file a render of source into format is saved as, beside source
---<<matches with>>--> DeclaredFile

## PracticeFormats

A practice's formats, made once: each format's adapter, the format that reads a file, and the conversion of a render request into output. A practice whose formats convert in a way of their own names its own kind (`formats_type`).

+ PracticeFormats(practice: PracticeGuidance, adapters: dict[str, Any])
------
+ supported: frozenset[Format]
+ adapter_settings: dict[str, Any]
+ suffixes: frozenset[str]
----
+ check(): None
+ adapter_class(format: str): Any
+ adapter(format: str): Any
+ reading(file: Path): Format | None
+ reading_with(file: Path, others: Iterable[PracticeGuidance]): Format | None
+ for_file(file: Path): Any
+ read(paths: list[str] | str, request: RenderRequest): Any
+ render(request: RenderRequest): dict
+ parse(format: Format, content: Any): Any
+ model_for(target: Any, model: Any): Any
---<<renders>>--> RenderRequest
---<<creates>>--> Format

## RenderRequest

One render a practice's formats perform: the target format, the content and its source format, the previous output, the folder, and the fidelity it renders at.

+ RenderRequest(format: Format, content: Any, source: Format, previous: str, folder: str, fidelity: FidelityGuidance | None)
------
+ format: Format
+ content: Any
+ source: Format
+ previous: str
+ folder: str
+ << association >> fidelity: FidelityGuidance | None
+ source_format: Format
+ companion: FidelityGuidance | None
----
+ keeping_sketch_wording(): RenderRequest

## PracticeReading

A practice's part in the knowledge graph: the node types the graph treats as classes, members, or source-ordered, the practices it reads after, how it reads a working copy into its graph, and the graph rules it checks. Each practice names its kind (`reading_type`) in its `model/graph_reading.py`, so the graph never imports a practice.

+ PracticeReading(practice: PracticeGuidance)
------
+ reads_after: tuple[str, ...]
+ node_types: tuple[str, ...]
+ class_types: tuple[str, ...]
+ member_types: tuple[str, ...]
+ class_node_type: str
+ source_ordered_types: frozenset[str]
+ anchor_types: dict[str, str]
+ rule_types: dict[str, tuple[str, ...]]
+ << association >> practice: PracticeGuidance
+ graph: Any
+ in_graph: Any
+ graph_checks: dict[str, Any]
+ package: str
----
+ held_in(graph: Any, nodes: Any): None
+ read(): None
+ read_working_copy(): None
+ own_graph_checks(): dict[str, Any]
+ checks(): dict[str, Any]

## Rule

One rule a practice checks, by its slug, with its body.

+ Rule(slug: str, body: str, fidelity: str | None = None, tag: str = 'base')
------
+ fidelity: str | None
+ tag: str
+ practice: str
+ pattern: str
+ shared: bool
+ slug: str
+ body: str
----
+ validate(): str
+ from_bullet(text: str, fidelity: str | None = None): Rule
---<<creates>>--> Name

## RulesCollection : MarkdownCollection

The rules of one practice or fidelity, and the paths they apply to; a practice's rules are injected into the chat when a file they apply to is edited.

+ RulesCollection(entries: dict[str, Rule | RulesCollection] | None = None, applies_to: AppliesTo | None = None, parent: Any = None)
------
+ applies_to: AppliesTo
+ prose: str
+ injection: RuleInjection
+ practice_key: str
+ fidelity_name: str
+ owner_practice: Any
----
+ inject_rules(payload: HookPayload): dict[str, Any]
+ from_markdown(text: str, fidelity: str | None = None, parent: Any = None): RulesCollection
+ formatted(): str
+ validate(): str
+ scan(paths: Any): Any
---<<reads the annotation>>--> Hook
---<<calls edited_path on>>--> HookPayload
---<<creates>>--> MarkdownText
---<<loads>>--> Rule
---<<only its holder publishes it, annotated>>--> PublishedWhereHeld
---<<annotated with>>--> HostedOnly

## Schema

The types one schema file declares, keyed by their schema key, in the order written.

+ Schema(text: str)
------
+ types: dict[str, SchemaType]
----
+ load(path: Path): Schema
+ guide(): str
+ fidelities(): dict[str, str]
+ node_fidelities(order: list[str]): dict[str, list[str]]
+ fidelity_errors(declared: list[str]): list[str]
+ rules(): dict[str, tuple[str, ...]]

## PracticeCatalogue

Every practice CDD ships, in the order the approach walks them: Stories, DDD, UX, Clean Engineering, BDD. `cdd_guidance/practices` registers their classes when it is imported; the catalogue holds classes only, so every reader makes and holds its own practices.

------
----
+ register(*practice_classes: type[PracticeGuidance]): None
+ keys(): tuple[str, ...]
+ has(key: str): bool
+ create(key: str, **arguments): PracticeGuidance
+ create_all(**arguments): list[PracticeGuidance]
	// each practice of the new set holds the practice it extends and the Clean Engineering practice of the same set
+ practice_class(key: str): type[PracticeGuidance]
---<<creates>>--> PracticeGuidance
---<<raises>>--> UnknownPractice
---<<raises>>--> PracticesNotRegistered

## UnknownPractice : KeyError

A key names no practice the catalogue holds.

+ UnknownPractice(key: str, keys: tuple[str, ...])
------
+ key: str
----

## ActionCatalogue

Every action CDD ships: `cdd_guidance/actions` registers each action folder's toolset when it is imported, and each operation a toolset publishes as a skill is one *Action*. harness/guidance_actions registers how an action runs on a fidelity with `run_actions_with`.

------
----
+ register(*toolset_classes: type): None
+ run_actions_with(runner: ActionRunner): None
+ runner(): ActionRunner
+ fidelity_actions(): tuple[Action, ...]
+ toolsets(): tuple[type, ...]
+ actions(): tuple[Action, ...]
+ names(): tuple[str, ...]
+ has(name: str): bool
+ action(name: str): Action | None
---<<creates>>--> Action
---<<counts as actions the operations annotated>>--> Skill
---<<reads constants of>>--> InstallDestination
---<<raises>>--> ActionsNotRegistered

## Action

One action CDD ships: an operation an action toolset installs as a skill, such as generate, repair, or validate.

+ Action(name: str, toolset_class: type)
------
+ name: str
+ toolset_class: type
+ operation
+ folder: Path
----
+ run_on(fidelity: WorkedFidelity, **arguments): Any
	-> ActionRunner.run

## ApproachStage

One stage of the CDD approach: the name each fidelity's **Stage:** gives it, its title, its scope, and the actions a person runs on a fidelity in it.

+ ApproachStage(name: str, scope: StageScope)
------
+ name: str
+ title: str
+ << composition >> scope: StageScope
+ steps: list[str]
+ actions: list[str]
+ producing_actions: list[str]
+ actions_with_formats: list[str]
----

## StageScope

How much of the solution a stage's work covers, drawn as a shape that narrows and deepens along the board: Discovery takes in the whole solution wide and shallow, Implementation one story narrow and deep.

+ StageScope(shape: str, name: str, reach: str)
------
+ shape: str
+ name: str
+ reach: str
+ covers: str
----
+ covering(covers: str): StageScope
