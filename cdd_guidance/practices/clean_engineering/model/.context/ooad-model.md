# Class model

*CleanEngineeringModel* is one class model that every format reads and writes: modules holding classes, each with properties, operations and their parameters, and the relationships its properties name. A nested module is a module whose parent is a module. Every node is a graph node (*ModelNode*), so the same objects the formats build are the nodes the graph holds.

A format is one subclass of *CleanEngineeringModel*: markdown, JSON, sketch, Python, TypeScript, JavaScript, Java, and draw.io. Each format reads text with `parse(text)`, which fills the format model itself and returns it, and writes with `render(canonical, previous)`: the format model becomes the canonical model once through `translate_from`, as its own subclasses of the modules and classes, then writes itself. A caller reading a file reads its text and hands it to `parse`; there is no second way in. A member written as a model line, `save(cart: Cart): Receipt` or `identity: Identity`, is read by `Operation.from_signature` and `Property.from_signature`, which every format that writes such lines uses.

One format's model becomes another's through `translate_from(source)`: each node copies what it says itself (`update_self`), then matches the source's children to its own by name, else by order, and builds each new child in its own format through `load_module`, `load_class`, `load_property`, `load_operation`, or `load_parameter`.

Callers use the base nodes. The practice picks a format by name from `CleanEngineering(...).formats`. A class's bases and stereotypes are part of what it says itself, so every format writes and reads them and `update_self`, `clone`, and `as_record` copy them. Text a format cannot read raises *UnreadableSource*; the graph read records each such file on its folder, where the `source-parses` rule reports it.

*CleanEngineering* (`practices/clean_engineering/clean_engineering.py`) says what the graph reads from the practice, and its readers are in `practices/clean_engineering/model/graph_reading.py`. When `Graph.load_working_copy`, `Graph.load_files`, or `Graph.refresh` reads files, `Graph._read_working_copy` in `harness/graph/working_copy.py` asks each practice the graph holds to read, in dependency order. *CleanEngineering* reads each source file with the class model of its language, which it finds among its own formats by the file's extension (`format_for`, which every practice has), and adds each folder as a *Module* that holds its *ModuleContext* (`load_folder_facts`), and each class, property, operation, and parameter the parser built, as nodes. The parser keeps the file's text on its module and the lines each class and operation spans on that class and operation (`take_lines`), so `load_source_facts` and `load_span_facts` read no file again. Each folder owns the folders under it and depends (`dependsOn` edges) on the folders its files import from; it keeps the class names its files import (`imported_names`). A getter is the operation its class shows as a property, so its node is that property (`Operation.is_property` makes its kind `Property`), typed by the type it returns (`value_type`); an operation's parameters are the *Parameter* nodes its `hasParameter` edges lead to (`parameters_of`), which every rule and BDD read. The practice's operations and properties are indexed once by name after each read (`members_named`), so every practice that links to the code asks one index. It then reads every `.context/*-model.md` in scope with the format the practice names for its model documents (`model_document_format`, its markdown format) and keeps the class model each one describes on the practice, which answers `described_member(owner, name)`: the operation or property a model document describes, so a realization follows the model's interactions without a second copy of any member in the graph. A graph read back from `graph.json` reads the documents under its source root the first time it is asked. DDD reads after Clean Engineering and sees its classes as building blocks.

```
model = CleanEngineering().formats["markdown"]().parse(text)
python = PythonCleanEngineeringModel().render(model, previous)
```

# practices/clean_engineering/model

- **Purpose:** One class model for every format. Callers see the base nodes; a format only differs in how it reads and spells its text.
- **Seam (terms):** CleanEngineeringModel, UnreadableSource, Module, OoadClass, Property, Operation, Parameter, Relationship, CodeBody
- **Dependencies (one-way):** harness/graph (*ModelNode*, *ModelChildren*, *Graph*), practices/sketch_document (*SketchOutline*), harness/guidance (*SketchLens*), practices/clean_engineering/model/drawio (*DrawIOCleanEngineeringModel*)

*ModelNode*, *ModelChildren*, *Graph*, *SketchOutline*, and *SketchLens* are owned by the modules above; this model only uses them. The draw.io format — *DrawIOCleanEngineeringModel*, *DrawIOModule*, *DrawIOClass*, and its *DrawIOImportedClass* — is modelled in [drawio-model.md](../drawio/.context/drawio-model.md).

## UnreadableSource : ValueError

A source file its language cannot read, such as Python that does not parse. Reading it as an empty or partial model would drop its classes from every check without saying so.

## OoadNode : ModelNode

`model/ooad_node.py`, beside the members and the classes that build on it, so `base_class_model` imports `property` and `operation` and neither imports it back. The practice's module registers itself on it (`OoadNode.register_practice(CleanEngineering)`), so a node finds its practice without importing it.


+ OoadNode(name: str, sequential_order: int, graph: Graph | None = None)
------
+ name: str
+ sequential_order: int
----
+ translate_from(source: OoadNode): None
	Invariant: source has the same semantic type as this node, else TranslationError
	// update_self, then each child list reconciles itself with the source's
	-> update_self
	-> reconcile_children
+ update_self(source: OoadNode): None
	// each node copies what it says itself, not its children
+ reconcile_children(source: OoadNode): None
	// each child list this node holds becomes the source's: ModelChildren.reconcile(source children, the load_* that builds a child in this format)
	-> ModelChildren.reconcile
+ declares(member: OoadNode): bool
	// only a class declares members: an operation's or property's owner is the class that declares it

## TranslationError : Exception

Raised when `translate_from` is given a node of another semantic type.

## CleanEngineeringModel : OoadNode

+ CleanEngineeringModel(name: str | Graph = "", sequential_order: int = 1, graph: Graph | None = None)
	// opened on a graph: a model named `model` whose nodes live on that graph
------
+ modules: list[Module]
	// composition — a module has no model outside this class model
----
+ is_modules_view: bool
	// property: modules only, no class carries a member or a drawn relationship
+ parse(text: str): CleanEngineeringModel
	// every format reads its own text
+ save(): str
+ described_member(owner: str, name: str): Operation | Property | None
	// the member the class owner describes as name; an operation before a property of the same name
+ every_class(): list[OoadClass]
	// every class in every module, nested modules included, in module order
+ clone(): CleanEngineeringModel
+ as_record(): dict
+ load_module(source: Module): Module
	// a new module in this format, for translate_from

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
+ path_parent: str | None
	// property: the module path that holds this one; None at the top
+ external_deps(): list[str]
	// dependencies other than the module's path parent
+ public_terms(): list[str]
	// seam terms, or the class names, or the seam string
+ load_module(source: Module): Module
+ load_class(source: OoadClass): OoadClass
	// a new class in this format, for translate_from
+ load(): None
	-> load_modules
	-> load_classes
+ source_text: str
	// the text of the file this module was read from, kept by its parser
+ imported_names: list[str]
	// the class names its code imports or reaches as module.Class
+ take_lines(text: str): None
	// keeps the file's text, and gives each class the lines it spans
	-> OoadClass.take_lines
+ load_source_facts(file: Path, root: Path): None
	// the graph facts the file it was read from gives: its imports, the class names it imports, and the classes that share it.
	// The graph keeps each class apart from its module, so the module gives each class its peers' names
+ import_targets(file: Path, root: Path): list[str]
	// root-relative paths of the relative script imports
+ load_folder_facts(folder: Path): None
	// the graph facts a code folder's context files give: what its module card says, read once, and whether it holds .context/bounded-context.md
	-> ModuleContext.model_blocks
+ holds_public_source(file_name: str): bool
	// production code whose name does not start with _
+ take_public_sources(sources: list[Module]): None
	// how many public source files the folder holds, and whether their documentation carries internal design notes
	-> Module.documentation
+ documentation: str
	// the doc strings and comments of the file it was read from; only a Python module's is read, from the syntax tree it keeps
+ clone(): Module
+ as_record(): dict

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
+ composes_peers: bool
	// an Entity or Aggregate Root builds the peers it owns; derived from its stereotypes
+ span: SourceText
	// the lines it spans in its file, kept by take_lines
+ module_helpers: list[list]
	// the module's private functions only this class calls
----
+ place_relationship(relationship: Relationship): None
	// puts the relationship on every property whose type names its target. Inheritance is not a property relationship
	-> Property.take_relationship
+ take_lines(lines: list[str]): None
	// keeps the lines from its line to its end line, and each operation's
+ load_source_facts(): None
	// the shape and source-span facts the graph reads: operation shapes, property names, what the constructor builds, prose comments
+ declared_bases(known_names: list[str]): list[str]
	// its bases, then the I{Class} contract it implements when known_names hold one
+ load_property(source: Property): Property
+ load_operation(source: Operation): Operation
+ load_relationship(source: Relationship): Relationship
+ clone(): OoadClass
+ as_record(): dict

## Property : InvariantHolder, OoadNode

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
+ take_note(text: str): None
	// a // line under the field: its stereotype, its cardinality, where it comes from, or an invariant
	-> derive_relationship
+ take_relationship(relationship: Relationship): None
	// becomes the field a relationship drawn to its type stands for
	-> derive_relationship
+ notes(): list[str]
	// origin, cardinality, then invariants, in file order
+ derive_relationship(): None
	// a relationship exists only when the type names a domain class; an unmarked lower-case collection adds none
+ save(): str
	// name: type
+ clone(): Property
+ as_record(): dict

## Operation : InvariantHolder, OoadNode

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
	// a getter: the operation its class shows as a property, so its kind is `Property`
+ value_type: str
	// the type a reader gets back: its return type
+ is_static: bool
+ is_classmethod: bool
+ line: int | None
+ end_line: int | None
+ line_count: int | None
----
+ source_lines: tuple[int, int]
	// its line through its end line, else as many lines as its body counts
+ span: SourceText
+ take_lines(lines: list[str]): None
+ load_span_facts(): None
	// the facts the operation rules read from its own source lines: private reach, I/O mixed with domain work, swallowed or empty-case exceptions, prose comments
	-> SourceText
+ language: CodeLanguage | None
	// the language a code operation is written in; none for one read from a model document
+ load_brace_body_facts(body: str, class_name: str): None
	// what the rules measure on a brace-language body of the class named class_name (empty for a module function): control-flow depth, catches, unnamed numbers, reads of another object's private fields (an object of the same class, by its name, a parameter typed as it, or a `new` of it, is not another)
	-> SourceText
+ save(): str
	// name(parameters): return type, with - for a private name
+ load_parameter(source: Parameter): Parameter
+ clone(): Operation
+ as_record(): dict

## InvariantHolder

What a property and an operation share: the // invariant lines under them.

------
+ invariants: list[Invariant]
+ description: str
	// the invariant lines joined, for formats that still read it
----
+ add_invariant(text: str): None
+ invariant_lines(): list[str]

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
+ reaches_peer_private(own_class: str = "", typed_own: frozenset[str] = frozenset()): bool
	// a read of another object's `_` member; a member of an object of own_class (the class itself, a typed_own parameter, a local built with `new`) is its own
+ mixes_io_and_domain(): bool
+ calls_io_and_domain(): bool
+ raises_on_empty(): bool
	// a builtin failure raised on an empty value; a failure the program declares is a named refusal and is left out
+ exception_without_message(): str
+ generic_exception_message(): bool
+ mutates_without_record(): bool
+ has_prose_comment(hash_only: bool = False): bool
+ prototype_swap(start_line: int): dict
+ markdown_bullet_lines(): dict
+ line_of(index: int): int
	// the line, counted from 1, holding the character at index
+ hits(pattern: Pattern): list[list]
	// [line, matched code] for each match

## PythonFunctionBody

A Python function read from its syntax tree, and what the rules measure in it.

+ PythonFunctionBody(node: FunctionDef, owner: ClassDef | None)
	// a method keeps the class that declares it; a module function has none
------
----
+ control_flow_depth(): int
+ except_flags(): tuple[bool, bool]
+ unnamed_numbers(): list[str]
+ reaches_peer_private(): bool
	// privacy in Python is per class: the class's own name, a parameter typed as it, the other operand of a comparison dunder, a local it builds from the class, and a loop over a field holding the class are all itself
+ packed_parameters(): dict[str, int]

## Parameter : OoadNode

+ Parameter(name: str, sequential_order: int = 0, type_hint: str = "")
------
+ type_hint: str
+ operation_name: str
	// derived from the operation that holds it
+ property_setter: bool
	// the parameter is the one value a property setter takes; derived from the operation that holds it
+ in_typed_language: bool
	// the operation that holds it is written in a language with a syntax for a parameter's type; plain JavaScript has none
----
+ save(): str

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
	// the card's text is read once, the first time it is asked, and every question below is answered from it
+ has_modules_heading(): bool
+ names_seam(): bool
+ names_constraint(): bool
+ says_is_a_type_of(): bool
+ writes_child_parent_headings(): bool
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
+ parse(text: str): MarkdownCleanEngineeringModel
	// fills this model and returns it; a card document keeps each card's text, so an unchanged class writes back as it was read
+ render(canonical: CleanEngineeringModel | None = None): str
	// a markdown model handed in writes itself; any other is translated in, then this model writes itself
	-> translate_from
	-> MarkdownModule.render
+ load_module(source: Module): MarkdownModule

## MarkdownModule : Module

------
----
+ render(): str
	// heading, description, Purpose / Seam (terms) / Dependencies when the module shows no members, then each class card
+ render_cards(module_level: int, card_level: int): str
+ load_class(source: OoadClass): MarkdownOoadClass

## MarkdownOoadClass : OoadClass

------
----
+ read_card(heading: ClassHeading, body: str, sequential_order: int): MarkdownOoadClass
	// class operation: the class a card shows, named and marked by its heading
	-> read_body
+ read_body(body: str): None
	// the class reads its own card body: intent, constructor, properties, operations, and the dependencies it names
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
	// raises UnreadableSource when the text is not JSON or holds neither modules nor classes
	-> JsonModule.from_record
+ render(canonical: CleanEngineeringModel | None = None): str
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

+ CodeLanguage(name: str, line_comment: str, indent: str, unfinished: str, spelling: CodeSpelling, type_names: dict[str, str], suffixes: tuple[str, ...] = (), declares_types: bool = True)
	// one instance per language, held as the module constants PYTHON, TYPESCRIPT, JAVASCRIPT, and JAVA
------
+ name: str
+ suffixes: tuple[str, ...]
+ declares_types: bool
	// false for plain JavaScript, which has no syntax for a parameter's type
+ line_comment: str
+ indent: str
+ unfinished: str
	// the statement that fails loudly when a body is not written. Never a silent no-op
----
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
+ lead: list[str]
+ heading: list[str]
+ inside: list[str]
+ inline: str
+ closing: list[str]
+ close: list[str]
+ << composition >> lead_body: CodeBody
	// made once when the reader sets lead
+ << composition >> closing_body: CodeBody
	// made once when the reader sets closing
+ << composition >> inside_body: CodeBody
	// made once when the reader sets inside or inline
----
+ is_in(language: CodeLanguage, key: str | tuple | None): bool
+ split_inside(lines: list[str], inside: tuple[int, int], children: list[tuple[int, int]]): tuple
	// the lines inside one block as setup, the lines above each child, and the lines after the last child
+ inside_for(body: CodeBody): list[str] | None
	// the lines exactly as read while the model's body still says the same

## CallGraphEntry

One line of an indented call graph, written with the same `->` and `<-` arrows as a model operation's interactions. Stories and BDD realizations use it.

------
+ depth: int
+ kind: str
	// call, out, or in
+ text: str

## CodeCleanEngineeringModel : CleanEngineeringModel

A class model written as code. The walk and the body rule live here; each language's module, class, property, and operation spell their own lines.

------
+ language: CodeLanguage
+ module_type: type[CodeModule]
	// the language's module, whose class_type, operation_type, and property_type are the language's parts
+ suffixes: tuple[str, ...]
	// the source file extensions it reads
----
+ file_module(): Module
	// the module the last parsed text forms, kept with that text even when it holds no class
+ render(canonical: CleanEngineeringModel, previous: str | None = None): str
	Invariant: an operation body read in this language is written back exactly as read
	// becomes the canonical model once, as the language's parts, then writes itself
	-> translate_from
	-> render_class
+ operation_body(class_name: str, operation_name: str): CodeBody
	// the body this model read. "constructor" finds the constructor in any language
+ render_class(oclass: CodeClass, known_names: list[str], kept: CodeCleanEngineeringModel): list[str]
	// the class's stand-in lines, else its opening, properties with their notes, constructor, operations, closing
	-> CodeClass.opening
	-> CodeProperty.lines
	-> CodeOperation.signature
+ render_body(operation: Operation, previous: CodeBody): list[str]
	-> CodeBody.in_language_of
	-> CodeBody.lines_in
+ file_header(preamble: CodeBody): list[str]

## CodeModule : Module

------
+ class_type: type[CodeClass]
----
+ load_module(source: Module): CodeModule
+ load_class(source: OoadClass): CodeClass

## CodeClass : OoadClass

A class as one language writes it.

------
+ language: CodeLanguage
+ property_type: type[CodeProperty]
+ operation_type: type[CodeOperation]
+ is_contract: bool
----
+ constructor(): CodeOperation | None
+ stand_in_lines(): list[str] | None
	// lines written instead of the class; JavaScript writes an example type as a note
+ opening(known_names: list[str]): list[str]
	// a blank line, the doc comment, the stereotype decorators, then the declaration for its kind
+ doc, doc_intent, stereotype_decorators, interface_declaration, class_declaration, heritage, class_modifiers
+ closing(has_members: bool): list[str]
+ block_close(): list[str]
+ constructor_lines(constructor: Operation | None, body: list[str]): list[str]
+ constructor_parameters(constructor: Operation | None): list[tuple]
	// the constructor's own parameters, else the class properties

## CodeProperty : Property

+ note_lines(): list[str]
+ lines(contract: bool): list[str]

## CodeOperation : Operation

+ doc_text(): str
	// the description when it is the operation's own text, not one joined from its comments
+ signature(contract: bool): list[str]
+ is_constructor_of(oclass: OoadClass): bool
+ answers_to(oclass: OoadClass, operation_name: str): bool

## BraceCleanEngineeringModel : CFamilyParse, CodeCleanEngineeringModel

A class model written in a brace language: TypeScript, JavaScript, or Java. Each reads its own text through the brace-language reading it shares.

## CFamilyParse

The brace-language reading mixed into BraceCleanEngineeringModel: reads TypeScript, JavaScript, or Java source into the model's own one module of classes, with each operation's body kept in the model's language.

------
+ language: CodeLanguage
	// the language of the model it is mixed into
----
+ parse(text: str): CFamilyParse
	// fills the model's modules with the language's own parts and returns the model
	// the preamble, each class with its doc comment, stereotypes, and the bases its heritage clause names, each field with its line, then the top-level functions
	// every operation records its line and its end line
	-> ClassHead.above
	-> Module.take_lines

## PythonCleanEngineeringModel : CodeCleanEngineeringModel

The `python` format.

------
+ language: CodeLanguage
	// PYTHON (the code_body constant)
----
+ parse(text: str): PythonCleanEngineeringModel
	// read from the syntax tree; text that does not parse raises UnreadableSource
+ file_header(preamble: CodeBody): list[str]

## PythonModule : CodeModule

Keeps the syntax tree its file was read into.

------
+ tree: ast.Module | None
----
+ keep_tree(tree: ast.Module): None
	// also records the module's private functions only one class calls
+ import_targets(file: Path, root: Path): list[str]
	// every import and from-import, absolute or relative, read from the kept tree

## PythonClass : CodeClass, PythonProperty : CodeProperty, PythonOperation : CodeOperation

Python spelling. The stereotypes are decorators with no arguments: @aggregate_root.

+ PythonOperation.from_function(node: FunctionDef, text: str, owner: ClassDef | None): PythonOperation
	// the whole operation from its own syntax tree: signature, body as written, and what the rules measure
	-> PythonFunctionBody
+ PythonProperty.from_annotation(node: AnnAssign, order: int): PythonProperty

## TypeScriptCleanEngineeringModel : BraceCleanEngineeringModel

The `typescript` format.

------
+ language: CodeLanguage
	// TYPESCRIPT (the code_body constant)
----
	// its parts, TypeScriptClass, TypeScriptProperty, TypeScriptOperation, spell TypeScript.
	// The stereotypes are decorators with no arguments: @AggregateRoot()

## JavaScriptCleanEngineeringModel : BraceCleanEngineeringModel

The `javascript` format.

------
+ language: CodeLanguage
	// JAVASCRIPT (the code_body constant)
----
	// its parts, JavaScriptClass, JavaScriptProperty, JavaScriptOperation, spell JavaScript. An example extension class
	// becomes a comment pointing at its base type. JavaScript has no interfaces, so an interface is a class that says it
	// is one, and the bases past the one it extends are named in an // implements line

## JavaCleanEngineeringModel : BraceCleanEngineeringModel

The `java` format.

------
+ language: CodeLanguage
	// JAVA (the code_body constant)
----
	// its parts, JavaClass, JavaProperty, JavaOperation, spell Java

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
+ seam_bullets: int
	// how many seam terms the card lists before it ends the list with `...`; six unless a subclass says otherwise
----
+ height(): int
+ header_height(): int
+ purpose_line(): str
+ shown_seam_terms(): list[str]

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

+ CardPlacement(cards: list[DiagramNode], arrows: list[DiagramArrow])
	Invariant: a base sits above what derives from it, and an owner above what it owns
	Invariant: the search is seeded, so the same model always gives the same diagram
------
----
+ place(): None
	// swaps cards on a compact grid, keeping each swap that scores better
	-> DiagramNode.geometry

## ArrowRouter

Routes every arrow between the placed cards.

+ ArrowRouter(cards: list[DiagramNode], arrows: list[DiagramArrow], obstacles: list[Geometry] = (), kept_paths: list[list] = ())
	Invariant: an arrow never passes through a card or runs along another arrow, and each has its own end points
	Invariant: the inheritance arrows of two or more subclasses that reach one base from the same side join into one trunk — a drop from each subclass to a shared bar, and one line from the bar to one point on the base; a single subclass keeps a direct arrow
------
----
+ route(): list[DiagramArrow]
	// lays each inheritance trunk first, breaking it into separate arrows when its lines would cross a card or run along another arrow
	// then routes the other arrows shortest first, and lifts each that crosses another and searches again with the rest in place
	-> DiagramArrow.corners
