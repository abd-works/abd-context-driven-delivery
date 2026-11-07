# Class model

*CleanEngineeringModel* is one class model that every format reads and writes: modules holding classes, each with properties, operations and their parameters, and the relationships its properties name. A nested module is a module whose parent is a module. Every node is a graph node (*ModelNode*), so the same objects the formats build are the nodes the graph holds.

A format is one subclass of *CleanEngineeringModel*: markdown, JSON, sketch, Python, TypeScript, JavaScript, Java, and draw.io. Each format reads text with `parse(text)` and writes a model with `render(canonical, previous)`. Markdown also reads a file through the walk on the base nodes: `load(path)` asks `has_more_module` / `get_next_module_from_file`, each module asks `has_more_class` / `get_next_class_from_file`, and each class loads its properties, operations, and relationships the same way. A format overrides only the `has_more_*` and `get_next_*_from_file` reads for the nodes its text contains.

One format's model becomes another's through `translate_from(source)`: each node copies what it says itself (`update_self`), then matches the source's children to its own by name, else by order, and builds each new child in its own format through `load_module`, `load_class`, `load_property`, `load_operation`, or `load_parameter`.

Callers use the base nodes. The practice picks a format by name from `CleanEngineering(...).formats`. A class's bases and stereotypes are part of what it says itself, so every format writes and reads them and `update_self`, `clone`, and `as_record` copy them. Text a format cannot read raises *UnreadableSource*; the graph read records each such file on its folder, where the `source-parses` rule reports it.

`CleanEngineeringGraph` in `practices/clean_engineering/graph_practice.py` is the practice's `GraphPractice`. When `Graph.load_working_copy` or `Graph.load_files` builds the graph, `fill_working_copy` in `harness/graph/working_copy.py` asks each registered practice to read in dependency order. Clean Engineering reads each source file with its language's model and adds each folder as a *Module* (`load_folder_facts`), and each class, property, operation, and parameter the parser built, as nodes; `load_source_facts` and `load_span_facts` fill the facts its rules read. It then reads every `.context/*-model.md` in scope with *MarkdownCleanEngineeringModel* into *ModelDescriptions*. DDD reads after Clean Engineering and sees its classes as building blocks.

```
model = CleanEngineering().formats["markdown"]().parse(text)
python = PythonCleanEngineeringModel().render(model, previous)
```

# practices/clean_engineering/model

- **Purpose:** One class model for every format. Callers see the base nodes; a format only differs in how it reads and spells its text.
- **Seam (terms):** CleanEngineeringModel, UnreadableSource, Module, OoadClass, Property, Operation, Parameter, Relationship, CodeBody
- **Dependencies (one-way):** harness/graph (*ModelNode*, *ModelChildren*, *Graph*), actions/sketch (*SketchOutline*, *SketchLens*), practices/clean_engineering/model/drawio (*DrawIOCleanEngineeringModel*)

*ModelNode*, *ModelChildren*, *Graph*, *SketchOutline*, and *SketchLens* are owned by the modules above; this model only uses them. The draw.io format — *DrawIOCleanEngineeringModel*, *DrawIOModule*, *DrawIOClass*, and its *DrawIOImportedClass* — is modelled in [drawio-model.md](../drawio/.context/drawio-model.md).

## UnreadableSource : ValueError

A source file its language cannot read, such as Python that does not parse. Reading it as an empty or partial model would drop its classes from every check without saying so.

## OoadNode : ModelNode

+ OoadNode(name: str, sequential_order: int, graph: Graph | None = None)
------
+ name: str
+ sequential_order: int
----
+ translate_from(source: OoadNode): None
	Invariant: source has the same semantic type as this node, else TranslationError
	// update_self, then reconcile each child collection: match by name, else by order; a source child with no match is built by the pair's load
	-> update_self
	-> child_collections
+ update_self(source: OoadNode): None
	// each node copies what it says itself, not its children
+ child_collections(source: OoadNode): list[ChildCollectionPair]

## ChildCollectionPair

One child list on this node, the same list on the source, and the operation that builds a new child in this node's format.

------
+ self_children: list[OoadNode]
+ source_children: list[OoadNode]
+ load: Callable[[OoadNode], OoadNode]

## TranslationError : Exception

Raised when `translate_from` is given a node of another semantic type.

## CleanEngineeringModel : OoadNode

+ CleanEngineeringModel(name: str | Graph = "", sequential_order: int = 1, graph: Graph | None = None)
	// opened on a graph: the model copies the modules another model already holds on that graph
------
+ path: str
+ modules: list[Module]
	// composition — a module has no model outside this class model
+ module_type: type
	// the format's module class the walk builds
----
+ load(path: str): CleanEngineeringModel
	// stores path, empties modules, then runs the same walk for every format
	-> load_content
	-> load_modules
+ parse(text: str): CleanEngineeringModel
	// every format reads its own text
+ save(): str
+ every_class(): list[OoadClass]
	// every class in every module, nested modules included, in module order
+ clone(): CleanEngineeringModel
+ as_record(): dict
+ load_module(source: Module): Module
	// a new module in this format, for translate_from
+ load_content(): None
	// a file format prepares its cursor over path
+ load_modules(): None
	// while has_more_module: append load_next_module()
+ has_more_module(): bool
+ load_next_module(): Module
	// module = get_next_module_from_file()
	-> module.load
+ get_next_module_from_file(): Module

## Module : OoadNode

+ Module(name: str, sequential_order: int, description: str = "", seam: str = "", constraint: str = "", seam_terms: list[str] | None = None, dependencies: list[str] | None = None, graph: Graph | None = None)
------
+ description: str
+ seam: str
+ seam_terms: list[str]
+ dependencies: list[str]
+ constraint: str
+ preamble: CodeBody
	// the code above the first class as read: imports and constants. Empty outside code
+ modules: list[Module]
	// composition — a nested module is a module whose parent is a module
+ classes: list[OoadClass]
	// composition — a class has no module outside this module
----
+ public_terms(): list[str]
	// seam terms, or the class names, or the seam string
+ append_module(module: Module): None
+ append_class(oclass: OoadClass): None
+ load_module(source: Module): Module
+ load_class(source: OoadClass): OoadClass
	// a new class in this format, for translate_from
+ load(): None
	-> load_modules
	-> load_classes
+ load_source_facts(text: str, file: Path, root: Path): None
	// the graph facts one parsed source file gives: its imports, the classes that share it, and which of them compose their peers
+ import_targets(text: str, file: Path, root: Path): list[str]
	// root-relative paths of the relative script imports
+ load_folder_facts(folder: Path): None
	// the graph facts a code folder gives: its module card, whether it holds .context/bounded-context.md, and its source files
	-> ModuleContext.model_blocks
+ clone(): Module
+ as_record(): dict
+ load_modules(): None
+ has_more_module(): bool
+ load_next_module(): Module
	// child = get_next_module_from_file()
	-> child.load
+ get_next_module_from_file(): Module
+ load_classes(): None
	// while has_more_class: append_class(load_next_class())
+ has_more_class(): bool
+ load_next_class(): OoadClass
	// class = get_next_class_from_file()
	-> oclass.load_properties
	-> oclass.load_operations
	-> oclass.load_relationships
+ get_next_class_from_file(): OoadClass

## OoadClass : OoadNode

+ OoadClass(name: str, sequential_order: int, intent: str = "", properties: list[Property] | None = None, operations: list[Operation] | None = None, relationships: list[Relationship] | None = None, collaborators: list[str] | None = None, line: int | None = None, graph: Graph | None = None)
------
+ intent: str
+ stereotypes: list[str]
	// the UML stereotypes the class carries, as words: Aggregate Root, Value Object
	// code writes each as a decorator with no arguments (@aggregate_root, @AggregateRoot()); a language without decorators marks <<Aggregate Root>> on the first line of the doc comment
+ properties: list[Property]
	// composition
+ operations: list[Operation]
	// composition
+ relationships: list[Relationship]
	// read from the properties that have one. The class does not store this list
+ collaborators: list[str]
+ line: int | None
+ end_line: int | None
+ bases: list[str]
	// the classes it extends or implements, as its declaration names them
+ peer_names: list[str]
	// the other classes in the same source file
+ module_helpers: list[list]
	// the module's private functions only this class calls
----
+ place_relationship(relationship: Relationship): None
	// puts the relationship on every property whose type names its target. Inheritance is not a property relationship
	-> Property.derive_relationship
+ load_source_facts(class_text: str): None
	// the shape and source-span facts the graph reads: operation shapes, property names, what the constructor builds, prose comments
+ declared_bases(known_names: list[str]): list[str]
	// its bases, then the I{Class} contract it implements when known_names hold one
+ load_property(source: Property): Property
+ load_operation(source: Operation): Operation
+ load_relationship(source: Relationship): Relationship
+ clone(): OoadClass
+ as_record(): dict
+ load_properties(): None
	// while has_more_property: append load_next_property()
+ has_more_property(): bool
+ load_next_property(): Property
+ get_next_property_from_file(): Property
+ load_operations(): None
	// while has_more_operation: append load_next_operation()
+ has_more_operation(): bool
+ load_next_operation(): Operation
	// operation = get_next_operation_from_file()
	-> operation.load_parameters
+ get_next_operation_from_file(): Operation
+ load_relationships(): None
	// while has_more_relationship: place_relationship(load_next_relationship())
+ has_more_relationship(): bool
+ load_next_relationship(): Relationship
+ get_next_relationship_from_file(): Relationship

## Property : OoadNode

+ Property(name: str, sequential_order: int = 0, type_hint: str = "", description: str = "", graph: Graph | None = None)
------
+ type_hint: str
+ description: str
+ access: str
	// readable, writable, or both
+ stereotype: str
	// composition, aggregation, or association. Copied onto relationship.kind
+ cardinality: str
	// the // line. Copied onto relationship.cardinality
+ origin: str
	// the module the field comes from, written // from Billing
+ relationship: Relationship | None
	// set when the type names a domain class. A primitive or a third-party type such as string, Error, or Collection has none. Collection<Customer> relates to Customer
+ invariants: list[Invariant]
	// composition. Each // line under the field, in file order
+ callees: list[str]
	// a derived property can ask collaborators for its value, written under it as -> Sessions.saved
----
+ derive_relationship(): None
	// a relationship exists only when the type names a domain class; an unmarked lower-case collection adds none
+ save(): str
	// name: type
+ clone(): Property
+ as_record(): dict

## Operation : OoadNode

+ Operation(name: str, sequential_order: int = 0, return_type: str = "", description: str = "", callees: list[str] | None = None, parameters: list[str] | None = None)
------
+ return_type: str
+ description: str
+ callees: list[str]
	// the -> lines under the operation: the collaborators it calls
+ body: CodeBody
	// the statements as read from code, in the language they were written in
	// empty when the operation came from markdown, JSON, or a diagram
+ invariants: list[Invariant]
	// composition. Each // line under the operation, in file order
+ parameters: list[Parameter]
	// composition
+ owner: str
	// the name of the class that holds this operation
+ is_property: bool
+ is_static: bool
+ is_classmethod: bool
+ line: int | None
+ end_line: int | None
+ line_count: int | None
----
+ load_span_facts(source_span: str): None
	// the facts the operation rules read from its own source lines: private reach, I/O mixed with domain work, swallowed or empty-case exceptions, prose comments
	-> SourceText
+ load_brace_body_facts(body: str): None
	// what the rules measure on a brace-language body: control-flow depth, catches, unnamed numbers, reads of a peer's private fields
	-> SourceText
+ load_python_function_facts(node: FunctionDef): None
	// the same measures read from Python's syntax tree, plus the parameters a tuple packs
	-> PythonFunctionBody
+ save(): str
	// name(parameters): return type, with - for a private name
+ load_parameter(source: Parameter): Parameter
+ clone(): Operation
+ as_record(): dict
+ load_parameters(): None
	// while has_more_parameter: append load_next_parameter()
+ has_more_parameter(): bool
+ load_next_parameter(): Parameter
+ get_next_parameter_from_file(): Parameter

## Invariant : OoadNode

A rule that must stay true for one property or one operation. The text is the // line. Order is the line order in the file.

+ Invariant(text: str, sequential_order: int = 0)
------
+ text: str

## SourceText

A span of source in any language — an operation body, a class, a markdown card — and what the rules measure in it.

+ SourceText(text: str)
------
----
+ control_flow_depth(): int
+ has_bare_catch(): bool
+ swallows_exceptions(): bool
+ unnamed_numbers(): list[str]
+ reaches_peer_private(parameter_names: frozenset[str]): bool
+ mixes_io_and_domain(): bool
+ calls_io_and_domain(): bool
+ raises_on_empty(): bool
+ exception_without_message(): str
+ generic_exception_message(): bool
+ mutates_without_record(): bool
+ private_reach(): bool
+ has_prose_comment(hash_only: bool = False): bool
+ prototype_swap(start_line: int): dict
+ markdown_bullet_lines(): dict
+ line_of(index: int): int
	// the line, counted from 1, holding the character at index
+ hits(pattern: Pattern): list[list]
	// [line, matched code] for each match

## PythonFunctionBody

A Python function read from its syntax tree, and what the rules measure in it.

+ PythonFunctionBody(node: FunctionDef)
------
----
+ control_flow_depth(): int
+ except_flags(): tuple[bool, bool]
+ unnamed_numbers(): list[str]
+ reaches_peer_private(): bool
+ packed_parameters(): dict[str, int]

## Parameter : OoadNode

+ Parameter(name: str, sequential_order: int = 0, type_hint: str = "")
------
+ type_hint: str
+ operation_name: str
+ property_setter: bool
	// the parameter is the one value a property setter takes
----
+ save(): str
+ load_operation_facts(operation: Operation): None

## Relationship

Optional on a property. Cardinality lives here. A class reads these from its properties.

+ Relationship(target: str, kind: str = "", cardinality: str = "", description: str = "", sequential_order: int = 0)
------
+ target: str
+ kind: str
	// composition, aggregation, association, or relative
+ cardinality: str
+ description: str
+ sequential_order: int
----
+ translate_from(source: Relationship): None
+ clone(): Relationship
+ as_record(): dict

## ModelDescriptions

Every member the model documents describe, by `Class.member`, with the document that describes it. The graph keeps them as the Clean Engineering practice root's `model_members` fact, so a BDD realization can follow an interaction into a class the load left out.

------
+ is_empty: bool
+ model_members: dict[str, dict]
	// each member's kind, interactions, parameters, return type, and document
----
+ read(model: CleanEngineeringModel, file: str): None
	// a later document's description of the same member replaces an earlier one

## ModuleContext

The module card, `.context/module-context.md`, of one code folder.

+ ModuleContext(folder: Path)
------
+ folder: Path
+ path: Path
----
+ exists(): bool
+ read(): str
	// empty when the folder has no card
+ has_modules_heading(): bool
+ model_blocks(): list[str]
	// model-fidelity detail written into the card: a ------ member list, a Sources / context list, a Live instance list

## DocumentedIntent

A doc comment read into the stereotypes its first line marks and the intent the rest of it says.

------
+ stereotypes: list[str]
+ intent: str
----
+ read(doc: str): DocumentedIntent

## ClassHead

What sits above a class declaration in brace-language source: its doc comment and the stereotypes its decorators and comment lines carry. A decorator with no arguments is a stereotype; one with arguments configures the class.

------
+ doc: str
+ stereotypes: list[str]
----
+ above(text_before_class: str): ClassHead

## MarkdownCleanEngineeringModel : CleanEngineeringModel

The `markdown` format: a `#` heading per module and a `##` card per class, or a document of class cards under deeper headings.

------
+ module_type: MarkdownModule
----
+ parse(text: str): MarkdownCleanEngineeringModel
	// a card document keeps each card's text, so an unchanged class writes back as it was read
+ render(canonical: CleanEngineeringModel | None = None, previous: str | None = None): str
	-> translate_from
	-> MarkdownModule.render
+ load_module(source: Module): MarkdownModule
+ load_content(): None
	// cursor is the # headings in the file. One file
+ has_more_module(): bool
+ get_next_module_from_file(): MarkdownModule

## MarkdownModule : Module

------
----
+ render(): str
	// heading, description, Purpose / Seam (terms) / Dependencies when the module shows no members, then each class card
+ render_cards(module_level: int, card_level: int): str
+ load_class(source: OoadClass): MarkdownOoadClass
+ get_next_class_from_file(): MarkdownOoadClass
	-> MarkdownOoadClass.parse_body

## MarkdownOoadClass : OoadClass

------
----
+ parse_body(heading: ClassHeading, body: str, sequential_order: int): MarkdownOoadClass
+ render(known_names: list[str] | None = None): str
+ heading(known_names: list[str]): ClassHeading
	-> OoadClass.declared_bases
+ render_card(level: int): str
+ keep_card(card: str, heading: ClassHeading): None
	// remembers the card this class was read from

## ClassHeading

A class heading as written: `Cart <<Aggregate Root>> : Basket, Auditable`, or a card's `**Cart** <<Entity>> — note`.

+ ClassHeading(name: str, stereotypes: list[str] = [], bases: list[str] = [], note: str = "")
------
+ name: str
+ stereotypes: list[str]
+ bases: list[str]
+ note: str
	// a card's note after its marks, kept as written
----
+ read(raw: str): ClassHeading
+ text(): str
+ card_text(): str

## JsonCleanEngineeringModel : CleanEngineeringModel

The `json` format: one array of module records.

------
----
+ parse(text: str): JsonCleanEngineeringModel
	// raises JsonParseError when the text is not the module array
	-> JsonModule.from_record
+ render(canonical: CleanEngineeringModel | None = None, previous: str | None = None): str
+ load_module(source: Module): JsonModule

## JsonModule : Module

------
----
+ from_record(record: dict, sequential_order: int): JsonModule
	-> JsonOoadClass.from_record
+ render(): str
+ load_class(source: OoadClass): JsonOoadClass

## JsonOoadClass : OoadClass

------
----
+ from_record(record: dict, sequential_order: int): JsonOoadClass
	-> JsonProperty.from_record
	-> JsonOperation.from_record
	-> JsonRelationship.from_record
+ render(): str
+ load_property(source: Property): JsonProperty
+ load_operation(source: Operation): JsonOperation
+ load_relationship(source: Relationship): JsonRelationship

## JsonProperty : Property

------
----
+ from_record(record: dict): JsonProperty

## JsonOperation : Operation

------
----
+ from_record(record: dict): JsonOperation

## JsonRelationship : Relationship

------
----
+ from_record(record: dict): JsonRelationship

## JsonParseError : ValueError

## SketchCleanEngineeringModel : CleanEngineeringModel

The `sketch` format: the `clean engineering:` section of an integrated sketch, modules as `name/` headings and classes with their members beneath them.

------
----
+ parse(text: str): SketchCleanEngineeringModel
	-> SketchOutline.body_for
+ render(canonical: CleanEngineeringModel, previous: str | None = None): str
	// the clean engineering: section; in previous, it replaces the section already there

## CodeSpelling

How a language writes the receiver, a constructor call, and the end of a statement.

+ CodeSpelling(receiver: str, construct: str, statement_end: str, camel_case: bool, base_call: tuple)
------
+ receiver: str
+ construct: str
+ statement_end: str
+ camel_case: bool
+ base_constructor: str
+ base_receiver: str

## CodeLanguage

How one programming language spells what every code format writes the same way. Python, TypeScript, JavaScript, and Java are instances, not subtypes: they differ only in data. Stories and BDD code formats use the same instances.

+ CodeLanguage(name: str, line_comment: str, indent: str, unfinished: str, spelling: CodeSpelling, type_names: dict[str, str])
------
+ name: str
+ line_comment: str
+ indent: str
+ unfinished: str
	// the statement that fails loudly when a body is not written. Never a silent no-op
----
+ named(name: str): CodeLanguage
	// the instance for python, typescript, javascript, or java
+ comment(text: str): str
+ is_unfinished(text: str): bool
	// the body is empty, a placeholder (... or pass), or this language's unfinished statement
+ identifier(name: str): str
	// snake case for python, camel case otherwise
+ type_name(hint: str): str
	// the language's name for a Python type hint such as str or list
+ assignment(name: str): str
	// the constructor line that stores a parameter on the new object
+ interaction(callee: str): str
	// one -> collaborator.operation note as a call in this language. Empty for a prose note

## CodeBody

The statements inside one operation, test, or step, kept with the language they were read in. The one rule every code format uses to write a body lives here.

+ CodeBody(text: str = "", language: CodeLanguage | None = None)
	// text is dedented. A body that is_unfinished in its language is empty
------
+ text: str
+ language: CodeLanguage | None
+ is_empty: bool
----
+ mentions(word: str): bool
+ lines_in(language: CodeLanguage, indent: str, unfinished: str): list[str]
	// same language: the text as read, under indent
	// another language: the text commented out under a note naming its language, then unfinished
	// empty: unfinished
	// unfinished is the line that marks a body still to write: language.unfinished for production code, the BDD signature marker for a spec, the step placeholder for a story
	// an empty unfinished writes no line: a constructor whose assignments complete it
+ in_language_of(other: CodeBody, language: CodeLanguage): CodeBody
	// whichever of self and other is written in language, self first. Neither: self
	// render uses this to keep a body from the previous file when the model's body is not in the target language

## WrittenBlock

The source lines around one block of code that no node holds, kept exactly as read: a BDD describe, context, or it; a story, scenario, or step chain. The language writes these lines back unchanged while the node still has the key it was read with.

+ WrittenBlock(language: CodeLanguage, key: str | tuple | None, lead: list[str], heading: list[str])
------
+ language: CodeLanguage
+ key: str | tuple | None
+ path: str
+ lead: list[str]
+ heading: list[str]
+ inside: list[str]
+ inline: str
+ closing: list[str]
+ close: list[str]
----
+ is_in(language: CodeLanguage, key: str | tuple | None): bool
+ split_inside(lines: list[str], inside: tuple[int, int], children: list[tuple[int, int]]): tuple
	// the lines inside one block as setup, the lines above each child, and the lines after the last child
+ inside_for(body: CodeBody): list[str] | None
	// the lines exactly as read while the model's body still says the same
+ lead_body(): CodeBody
+ closing_body(): CodeBody

## CallGraphEntry

One line of an indented call graph, written with the same `->` and `<-` arrows as a model operation's interactions. Stories and BDD realizations use it.

------
+ depth: int
+ kind: str
	// call, out, or in
+ text: str

## CodeCleanEngineeringModel : CleanEngineeringModel

A class model written as code. The walk and the body rule live here; a language only spells the lines.

------
+ language: CodeLanguage
	// each language model sets its instance
----
+ render(canonical: CleanEngineeringModel, previous: str | None = None): str
	Invariant: an operation body read in this language is written back exactly as read
	// previous set: each operation keeps the previous file's body when the canonical body is not in this language
	// file header with the preamble, then per module: a === name === banner comment, then each class
	-> parse
	-> render_class
+ operation_body(class_name: str, operation_name: str): CodeBody
	// the body this model read. "constructor" finds the constructor in any language
+ render_class(oclass: OoadClass, known_names: list[str], kept: CodeCleanEngineeringModel): list[str]
	// an interface: signatures only. Otherwise class open, properties with their notes, constructor, operations, class close
	// one blank line between member groups
+ render_operation(operation: Operation, contract: bool, previous: CodeBody): list[str]
	// signature, then render_body unless contract
+ render_body(operation: Operation, previous: CodeBody): list[str]
	// a body in this language: body.lines_in
	// an empty body: invariant comments, then language.interaction for each callee, then language.unfinished
	// a body from another language: its text commented out, then language.unfinished
	// the constructor ends with a field assignment per parameter instead of language.unfinished
	-> CodeBody.in_language_of
	-> CodeBody.lines_in
+ doc_text(operation: Operation): str
	// the description when it is the operation's own text, not one joined from its comments
+ file_header(canonical: CleanEngineeringModel, preamble: CodeBody): list[str]
+ class_open(oclass: OoadClass, known_names: list[str]): list[str]
	// a blank line, the doc comment, the stereotype decorators, then the declaration for its kind: an interface, or a class with the bases it declares
	-> OoadClass.declared_bases
+ class_doc(intent: str): list[str]
+ class_intent(oclass: OoadClass): str
+ stereotype_decorators(oclass: OoadClass): list[str]
	// none for a language that marks stereotypes in the doc comment
+ interface_declaration(oclass: OoadClass): list[str]
+ class_declaration(oclass: OoadClass, bases: list[str]): list[str]
	// class Name extends Base implements Contract, Other {
+ heritage(bases: list[str]): tuple
	// the one base a class extends, and the bases it implements
+ class_modifiers(implemented: list[str]): str
+ class_close(has_members: bool): list[str]
+ property_line(prop: Property, contract: bool): list[str]
+ constructor_lines(oclass: OoadClass, constructor: Operation | None, body: list[str]): list[str]
+ constructor_parameters(oclass: OoadClass, constructor: Operation | None): list[tuple]
	// the constructor's own parameters, else the class properties
+ signature(operation: Operation, contract: bool): list[str]
+ block_close(): list[str]
	// each language overrides the spelling operations above. None of them decides what a body holds

## BraceCleanEngineeringModel : CodeCleanEngineeringModel

A class model written in a brace language: TypeScript, JavaScript, or Java. They read through one parse.

------
----
+ parse(text: str): BraceCleanEngineeringModel
	-> CFamilyParse.parse

## CFamilyParse

Reads brace-language source — TypeScript, JavaScript, and Java — into one module of classes, with each operation's body kept in its language.

+ CFamilyParse(model_factory: Callable[[], CleanEngineeringModel], class_factory: Callable[..., OoadClass], language: CodeLanguage)
------
----
+ parse(text: str): CleanEngineeringModel
	// the preamble, each class with its doc comment, stereotypes, and the bases its heritage clause names, then the top-level functions
	-> ClassHead.above
+ method_span_in_text(text: str, name: str, fallback_line: int = 1): tuple[int, int]
	// the lines a brace-language method spans, when the graph load has no end line

## PythonCleanEngineeringModel : CodeCleanEngineeringModel

The `python` format.

------
+ language: CodeLanguage
	// CodeLanguage.named("python")
----
+ parse(text: str): PythonCleanEngineeringModel
	// read from the syntax tree; text that does not parse raises UnreadableSource
+ load_module(source: Module): PythonModule
+ file_header, class_open, class_close, property_line, constructor_lines, signature, block_close
	// Python spelling only. The stereotypes are decorators with no arguments: @aggregate_root

## PythonModule : Module

------
----
+ load_source_facts(text: str, file: Path, root: Path): None
	// also records the module's private functions only one class calls
+ import_targets(text: str, file: Path, root: Path): list[str]
	// every import and from-import, absolute or relative

## TypeScriptCleanEngineeringModel : BraceCleanEngineeringModel

The `typescript` format.

------
+ language: CodeLanguage
	// CodeLanguage.named("typescript")
----
+ class_doc, class_intent, stereotype_decorators, interface_declaration, class_modifiers, property_line, constructor_lines, signature
	// TypeScript spelling only. The stereotypes are decorators with no arguments: @AggregateRoot()

## JavaScriptCleanEngineeringModel : BraceCleanEngineeringModel

The `javascript` format.

------
+ language: CodeLanguage
	// CodeLanguage.named("javascript")
----
+ render_class(oclass: OoadClass, known_names: list[str], kept: CodeCleanEngineeringModel): list[str]
	// an example extension class becomes a comment pointing at its base type
+ interface_declaration, class_declaration, property_line, constructor_lines, signature
	// JavaScript spelling only. JavaScript has no interfaces, so an interface is a class that says it is one, and the bases past the one it extends are named in an // implements line

## JavaCleanEngineeringModel : BraceCleanEngineeringModel

The `java` format.

------
+ language: CodeLanguage
	// CodeLanguage.named("java")
----
+ interface_declaration, class_modifiers, property_line, constructor_lines, signature
	// Java spelling only

## DiagramNode

One placed cell. Draw.io writes it as HTML; the box, its placement, and its arrows are shared.

------
+ geometry: Geometry
+ cell_id: str
+ parent_id: str
+ group: str
	// the module the node belongs to; card placement keeps one group's cards together
----
+ height(): int

## DiagramClass : OoadClass, DiagramNode

A class on a page. The format fills the label.

------
----
+ height(): int
	// grows with the number of properties and operations

## ImportedClass : DiagramClass

A compact card for a class owned by another module, drawn beside the local class it links.

------
+ from_module: str
----
+ key_properties(): list[Property]
	// the first four properties
+ height(): int

## DiagramModule : Module, DiagramNode

A module on a page: purpose, seam, nesting, and height. The format fills the label.

------
+ nested: bool
----
+ height(): int
+ header_height(): int
+ purpose_line(): str
+ shown_seam_terms(): list[str]
+ external_deps(): list[str]
	// dependencies other than the module's path parent
+ load_class(source: OoadClass): DiagramClass

## ContainmentForest

Path nesting and dependency depth for ordering modules on a page.

------
+ by_name: dict[str, Module]
+ children_of: dict[str, list[str]]
+ roots: list[str]
----
+ build(modules: list[Module], synthesize_parents: bool = False): ContainmentForest
+ module_dep_depth(name: str): int

## DiagramCleanEngineeringModel : CleanEngineeringModel

The diagram format draw.io extends. A modules view (`is_modules_view`: modules with no class members to show) stops at modules; a class view continues through properties and operations.

------
+ module_type: DiagramModule

## Geometry

+ Geometry(x: float, y: float, width: float, height: float)
------
+ x: float
+ y: float
+ width: float
+ height: float
+ center: tuple[float, float]
----
+ overlaps(other: Geometry): bool
+ shifted(dx: float, dy: float): Geometry
+ moved_to(x: float, y: float): Geometry

## DiagramCard

A box to place or route around for a view with no diagram node of its own, such as the DDD aggregate view. Placement and routing read only `cell_id`, `geometry`, and `group`.

+ DiagramCard(cell_id: str, width: float, height: float, group: str = "", x: float = 0, y: float = 0)
------
+ geometry: Geometry

## DiagramArrow

The line drawn between two cards for every relationship one class has to another. Several properties can stand behind one arrow, so it carries their names as its label.

+ DiagramArrow(source: str, target: str, kind: str = "association", label: str = "")
------
+ source: str
+ target: str
+ kind: str
+ label: str
+ exit_side: str
+ entry_side: str
+ exit_point: tuple
+ entry_point: tuple
+ corners: list[tuple]
+ routed: bool
+ path: list[tuple]
	// exit point, corners, entry point

## CardPlacement

Finds the grid position for every card that leaves the fewest crossings and the shortest arrows.

+ CardPlacement(cards: list[DiagramNode | DiagramCard], arrows: list[DiagramArrow])
	Invariant: a base sits above what derives from it, and an owner above what it owns
	Invariant: the search is seeded, so the same model always gives the same diagram
------
----
+ place(): None
	// swaps cards on a compact grid, keeping each swap that scores better
	-> DiagramNode.geometry

## ArrowRouter

Routes every arrow between the placed cards.

+ ArrowRouter(cards: list[DiagramNode | DiagramCard], arrows: list[DiagramArrow], obstacles: list[Geometry] = (), kept_paths: list[list] = ())
	Invariant: an arrow never passes through a card or runs along another arrow, and each has its own end points
------
----
+ route(): list[DiagramArrow]
	// routes shortest first, then lifts each arrow that crosses another and searches again with the rest in place
	-> DiagramArrow.corners
