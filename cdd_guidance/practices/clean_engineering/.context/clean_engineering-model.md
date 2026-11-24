# cdd_guidance/practices/clean_engineering

*CleanEngineering* is the practice; its *GraphReading* is its part in the knowledge graph, reading the code and then the model documents. *CleanEngineeringModel* is the one class model every format reads and writes (modules, classes, properties, operations, relationships); *CodeCleanEngineeringModel* is that model written as code; *CodeLanguage*, *CodeBody*, *WrittenBlock*, *BraceCall*, and *BracketStructure* are what every code format shares; *CallGraph* is an indented call graph; *SourceText* is a span of source and what the rules measure in it; *Drawio* draws the model as a class diagram, through *DrawIOCleanEngineeringModel* and its *DrawIOModule* cards. The whole model of this module, internals included, is `cdd_guidance/practices/clean_engineering/model/.context/ooad-model.md` and `cdd_guidance/practices/clean_engineering/model/drawio/.context/drawio-model.md`; those documents are canonical, and this section shows only the classes other modules use.

- **Purpose:** Keep boundaries, types, and code consistent, so a change stays inside one module instead of spreading to every caller.
- **Seam (terms):** CleanEngineering, GraphReading, CleanEngineeringModel, Module, OoadClass, Property, Operation, Relationship, CodeCleanEngineeringModel, PythonCleanEngineeringModel, TypeScriptCleanEngineeringModel, CodeLanguage, CodeBody, WrittenBlock, BraceCall, BracketStructure, CallGraph, CallGraphEntry, SourceText, Drawio, DrawIOCleanEngineeringModel, DrawIOModule
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/markdown, harness/guidance, harness/installation, harness/graph, cdd_guidance/practices/sketch_document

## CleanEngineering : PracticeGuidance

The Clean Engineering practice: modules, model, and code.

+ CleanEngineering(fidelity: str = 'modules', format: str | None = None)
------
+ reading_type: type
	// GraphReading
+ model_document_format: type
	// MarkdownCleanEngineeringModel
+ << composition >> drawio: Drawio
----
+ generate_output(): str
---<<renders>>--> Drawio
---<<creates>>--> Drawio
---<<reads the graph with>>--> GraphReading
---<<registers with>>--> OoadNode

## GraphReading : PracticeReading

How Clean Engineering takes part in the graph: it reads the code, then the model documents; every practice that links to the code asks its code index.

+ GraphReading(practice: PracticeGuidance)
------
+ class_types: tuple[str, ...]
+ code_index: CodeIndex
+ model_documents: ModelDocuments
----
+ read_working_copy(): None
---<<creates>>--> CodeIndex
---<<creates>>--> ModelDocuments

## CleanEngineeringModel : OoadNode

One class model that every format reads and writes: modules holding classes.

+ CleanEngineeringModel(name: str | Graph = '', sequential_order: int = 1, graph: Graph | None = None)
------
+ module_type: type
+ << composition >> modules: list[Module]
+ is_modules_view: bool
----
+ described_member(owner: str, name: str): Operation | Property | None
+ every_class(): list[OoadClass]
+ as_record(): dict
+ update_self(source: OoadNode): None
+ clone(): CleanEngineeringModel
+ save(): str
+ parse(text: str): CleanEngineeringModel
+ load_module(source: Module): Module
+ reconcile_children(source: OoadNode): None
---<<creates>>--> Module
---<<keeps>>--> Module
---<<keeps>>--> OoadClass

## Module : OoadNode

A named module boundary grouping closely related classes.

+ Module(name: str, sequential_order: int, graph: Graph | None = None)
------
+ class_type: type
+ description: str
+ seam: str
+ constraint: str
+ seam_terms: list[str]
+ dependencies: list[str]
+ imported_classes: list[ClassReference]
+ modules: list[Module]
+ << composition >> classes: list[OoadClass]
+ path_parent: str | None
+ documentation: str
+ << composition >> source_facts: ModuleSourceFacts
----
+ as_record(): dict
+ external_deps(): list[str]
+ public_terms(): list[str]
+ update_self(source: OoadNode): None
+ clone(): Module
+ load_module(source: Module): Module
+ load_class(source: OoadClass): OoadClass
+ import_targets(file: Path, root: Path): list[str]
+ reconcile_children(source: OoadNode): None
---<<creates>>--> OoadClass
---<<keeps>>--> OoadClass

## OoadClass : OoadNode

A class in the model: what it remembers, what it does, and how it relates.

+ OoadClass(name: str, sequential_order: int, intent: str = '')
------
+ property_type: type
+ operation_type: type
+ intent: str
+ stereotypes: list[str]
+ module_path: list[str]
+ bases: list[str]
+ collaborators: list[str]
+ dependencies: list[Relationship]
+ << composition >> properties: list[Property]
+ << composition >> operations: list[Operation]
+ public_properties: list[Operation | Property]
+ relationships: list[Relationship]
+ composes_peers: bool
+ held_fields: dict[str, str]
+ << composition >> source_facts: ClassSourceFacts
+ << composition >> arrows: ClassArrows
+ << association >> folded: list[OoadClass]
+ folded_into: str
----
+ fold(other: OoadClass): None
+ doc_comment(marked: bool): DocComment
+ declared_bases(known_names: Iterable[str]): list[str]
+ update_self(source: OoadNode): None
+ clone(): OoadClass
+ as_record(): dict
+ load_property(source: Property): Property
+ load_operation(source: Operation): Operation
+ reconcile_children(source: OoadNode): None
+ declares(member: OoadNode): bool
---<<keeps>>--> Operation
---<<keeps>>--> Property
---<<keeps>>--> Relationship

## Property : InvariantHolder, OoadNode

Something a class remembers or derives, with its relationship when its type names a domain class.

+ Property(name: str, sequential_order: int = 0, type_hint: str = '')
------
+ type_hint: str
+ description: str
+ value_type: str
+ owner: str
+ relationship: Relationship | None
+ << composition >> arrow: FieldArrow
----
+ from_signature(text: str): Property | None
+ keep_owner(): None
+ clone(): Property
+ take_note(text: str): None
+ notes(): list[str]
+ save(): str
+ marked_signature(): str
	// the property as a model line writes it with the relationship written on it; a property nobody marked is written with none
+ as_record(): dict
+ update_self(source: OoadNode): None
---<<keeps>>--> Relationship

## Operation : InvariantHolder, OoadNode

Something a class does: its parameters, return, interactions, and invariants.

+ Operation(name: str, sequential_order: int = 0, return_type: str = '')
------
+ return_type: str
+ callees: list[str]
+ << composition >> body: CodeBody
+ body_text: str
+ owner: str
+ parameters: list[Parameter]
+ is_constructor: bool
+ is_property: bool
+ value_type: str
+ source_lines: tuple[int, int]
+ << composition >> source_facts: OperationSourceFacts
----
+ from_signature(text: str): Operation | None
+ attach(child, kind: str): None
+ keep_owner(): None
+ clone(): Operation
+ save(): str
+ as_record(): dict
+ update_self(source: OoadNode): None
+ reconcile_children(source: OoadNode): None
---<<creates>>--> CodeBody

## Relationship

One line from a class to another: its target, its kind, and its label.

------
+ target: str
+ kind: str
+ cardinality: str
+ description: str
+ sequential_order: int
+ label: str
+ details: dict[str, str]
+ name: str
----
+ read_line(line: str): Relationship | None
+ split_off(lines: list[str]): tuple[list[str], list[Relationship]]
+ read_lines(lines: list[str]): list[Relationship]
+ line(): str
+ lines(): list[str]
+ as_record(): dict[str, Any]
+ translate_from(source: Relationship): None
+ update_self(source: Relationship): None
+ clone(): Relationship

## CodeCleanEngineeringModel : CleanEngineeringModel

A class model written as code; the Python, TypeScript, JavaScript, and Java formats each spell their own lines.

------
+ << association >> language: CodeLanguage
+ suffixes: tuple
+ class_type: type
+ operation_type: type
+ property_type: type
----
+ file_module(): Module
+ render(canonical: CleanEngineeringModel, previous: str | None = None): str
+ operation_body(class_name: str, operation_name: str): CodeBody
+ render_class(oclass: CodeClass, known_names: list[str], kept: CodeCleanEngineeringModel): list[str]
+ render_operation(oclass: CodeClass, operation: CodeOperation, previous: CodeBody): list[str]
+ render_body(operation: Operation, previous: CodeBody): list[str]
+ file_header(preamble: CodeBody): list[str]
---<<creates>>--> CodeBody

## PythonCleanEngineeringModel : CodeCleanEngineeringModel

The Python format of the class model; DDD names it as its own python format.

------
----
+ parse(text: str): PythonCleanEngineeringModel
+ file_header(preamble: CodeBody): list[str]

## TypeScriptCleanEngineeringModel : BraceCleanEngineeringModel

The TypeScript format of the class model; DDD names it as its own typescript format.

------
----

## CodeLanguage

How one programming language spells what every code format writes the same way. `PYTHON`, `TYPESCRIPT`, and `JAVASCRIPT` are its instances other modules import.

+ CodeLanguage(name: str, line_comment: str, indent: str, unfinished: str, spelling: CodeSpelling, type_names: dict[str, str], suffixes: tuple[str, ...] = ())
------
+ name: str
+ suffixes: tuple[str, ...]
+ line_comment: str
+ indent: str
+ unfinished: str
----
+ comment(text: str): str
+ is_unfinished(text: str): bool
+ identifier(name: str): str
+ type_name(hint: str): str
+ interaction(callee: str): str
+ assignment(name: str): str

## CodeBody

The statements inside one operation, test, or step, kept with the language they were read in.

+ CodeBody(text: str = '', language: CodeLanguage | None = None)
------
+ text: str
+ << association >> language: CodeLanguage | None
+ is_empty: bool
	// a body that is unfinished in its language is empty
----
+ mentions(word: str): bool
+ lines_in(language: CodeLanguage, indent: str, unfinished: str): list[str]
+ in_language_of(other: CodeBody, language: CodeLanguage): CodeBody
---<<calls is_unfinished on>>--> CodeLanguage
---<<calls comment on>>--> CodeLanguage

## WrittenBlock

The source lines around one block of code that no node holds, kept exactly as read, under a `WrittenKey`.

+ WrittenBlock(language: CodeLanguage, key: WrittenKey, heading: list[str])
------
+ << association >> language: CodeLanguage
+ key: WrittenKey
+ heading: list[str]
+ lead: list[str]
+ closing: list[str]
+ inside: list[str]
+ inline: str
----
+ is_in(language: CodeLanguage, key: WrittenKey): bool
+ inside_for(body: CodeBody): list[str] | None

## InsideLines

The lines inside one block of a file, which its child blocks divide.

+ InsideLines(lines: list[str], inside: tuple[int, int])
----
+ split(children: list[tuple[int, int]]): tuple[list[str], list[list[str]], list[str]]

## BraceCall

One call whose last argument is a callback, such as `describe("a cart", () => { ... })` or `story(...)`, and where its parts sit in the text.

+ BraceCall(text: str, start: int, name: str)
------
+ text: str
+ start: int
+ name: str
+ close: int
+ brace: int
+ inner_end: int
+ end: int
+ is_whole: bool
+ body: str
----

## BracketStructure

A span of text read for its brackets.

+ BracketStructure(text: str)
------
----
+ closing_bracket(open_at: int, opener: str = '{', closer: str = '}'): int | None
+ opening_bracket(close_at: int, opener: str = '(', closer: str = ')'): int
+ top_level_indexes(mark: str): list[int]
+ top_level_index(mark: str): int
+ braced(open_at: int): str | None

## CallGraph : list

An indented call graph: the operations a step or an observation reaches, one entry per line.

------
----
+ read(text: str): CallGraph
+ add_line(line: str, depth: int): None
+ block(): str
+ callees(): list[str]
---<<keeps>>--> CallGraphEntry

## CallGraphEntry

One line in an indented call graph.

------
+ depth: int
+ kind: str
+ text: str
----

## SourceText : MeasuredBody

A span of source in any language, such as an operation body, a class, or a markdown card, and what the rules measure in it.

+ SourceText(text: str)
------
+ text: str
+ << composition >> failures: SpanFailures
+ << composition >> collaborators: SpanCollaborators
----
+ control_flow_depth(): int
+ unnamed_numbers(): list[str]
+ catches_everything(): bool
+ swallows(): bool
+ mixes_io_and_domain(): bool
+ calls_io_and_domain(): bool
+ mutates_without_record(): bool
+ has_prose_comment(hash_only: bool = False): bool
+ prototype_swap(start_line: int): dict[str, str | int]
+ markdown_bullet_lines(): dict
+ line_of(index: int): int
+ hits(pattern: re.Pattern[str]): list[list]

## Drawio

Draw the class model as a draw.io diagram, then scan its layout and repair the generator.

+ Drawio()
------
+ module_dir: Path
+ domain_slug: str
----
+ contexts(): str
+ examples(): str
+ create_diagram(content: str, path: str): str
+ scan(paths: list[str]): str
+ validate(): str
+ repair(asset: str, violation: str): str
+ render(content: str = '', path: str = ''): str
+ verify_regression(examples_root: str = ''): str

## DrawIOCleanEngineeringModel : DiagramCleanEngineeringModel

The draw.io format of the class model: a modules view of rounded module cards, or a class view of class cards and the arrows between them. DDD's bounded-context map extends it.

+ DrawIOCleanEngineeringModel(name: str = '', sequential_order: int = 1)
------
+ module_cell_types: tuple[type, ...]
+ previous: str | None
+ keep_positioning: bool
----
+ save(): str
+ load_module_cell(source: Module): DrawIOModule
+ imported_class(source: OoadClass, from_module: str = ''): DrawIOImportedClass
+ parse(text: str): DrawIOCleanEngineeringModel
+ render(canonical: CleanEngineeringModel, previous: str | None = None): str
	// with previous, the cards and arrows a person placed there stay where they are
+ kept_previous(): str | None
---<<creates>>--> DrawIOModule

## DrawIOModule : DiagramModule, DrawioVertex

A rounded modules-view cell.

+ DrawIOModule(name: str = '', sequential_order: int = 1, **kwargs)
------
+ dependency_labels: dict[str, str]
----
+ draws(style: str): bool
+ html(): str
+ style(): str
+ from_cell(value: str, sequential_order: int): DrawIOModule | None
