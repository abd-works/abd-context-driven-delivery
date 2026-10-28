<!-- @toolset-manifest python -m harness manifest practices.clean_engineering.clean_engineering:CleanEngineering -->
<!-- Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m harness run -. Follow response.instructions only. Do not author behavior from this Python source. -->
<!-- invoke-edit: action satisfy | toolset: practices.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: practices.clean_engineering.clean_engineering:CleanEngineering -->

# Class model

*CleanEngineeringModel* reads a path into modules and classes. A nested module is a module whose parent is a module. Markdown and JSON are one file and continue through properties, operations, parameters, and relationships. A code path is a folder: module folders, then nested module folders, then one class file per class. Draw.io and Miro are one file. A modules view stops at classes. A class view continues through properties and operations. Every channel uses the same walk. A channel only differs in how the next node is taken out of the path.

Callers use the base nodes. `CleanEngineeringModelFactory.load` takes a file or a folder, chooses the channel model, and returns a `CleanEngineeringModel`.

```
model = CleanEngineeringModelFactory.load(path)
```

# practices/clean_engineering/model

- **Purpose:** One class-model walk for every channel. Callers see the base nodes. The factory chooses the channel.
- **Seam (terms):** CleanEngineeringModelFactory, CleanEngineeringModel, Module, OoadClass, Property, Operation, Parameter, Relationship
- **Dependencies (one-way):** *(none)*

## CleanEngineeringModelFactory

+ load(path: str): CleanEngineeringModel
	// path is a file, or a folder of files
	// the file type, or the files in the folder, selects the channel model
	// that model loads itself
	// the return is a CleanEngineeringModel

## OoadNode

+ OoadNode(source: OoadNode)
	// copies name and sequential order
------
+ name: str
+ sequential_order: int

## CleanEngineeringModel : OoadNode

+ CleanEngineeringModel(source: CleanEngineeringModel)
	// source empty: the model is empty until load
	// source set: modules are this channel's types, built from source. A nested module uses module_type
	// the new model does not keep the source's channel types
------
+ path: str
+ modules: list[Module]
	// composition — a module has no model outside this class model
	// a nested module is a module whose parent is a module
+ module_type: type
----
+ load(path: str): CleanEngineeringModel
	// stores path, then runs the same walk for every channel
	self.path = path
	self.load_content()
	self.load_modules()
+ save(): str
	// every channel writes its path with this operation
- load_content(): None
	// each channel overrides this. load calls this one operation
	// a file channel prepares its cursor over the path
	// graph load: node and edge facts from the parser
- load_modules(): None
	// while has_more_module: append load_next_module()
- has_more_module(): bool
	// channel: another module remains in the path
- load_next_module(): Module
	// module = get_next_module_from_file()
	// -> module.load()
- get_next_module_from_file(): Module
	// channel: the next module shell from the path, in module_type

## Module : OoadNode

+ Module(source: Module)
	// copies name, order, description, seam, seam terms, dependencies, constraint, and preamble
	// a nested module is a module whose parent is a module
	// each source child module becomes this channel's module
	// each source class becomes this channel's class
------
+ description: str
+ preamble: CodeBody
	// the code above the first class as read: imports and constants. Empty outside code
+ seam: str
+ seam_terms: list[str]
+ dependencies: list[str]
+ constraint: str
+ modules: list[Module]
+ classes: list[OoadClass]
	// composition — a class has no module outside this module
+ module_type: type
+ class_type: type
----
+ public_terms(): list[str]
	// seam terms, or the class names, or the seam string
+ append_module(module: Module): None
+ append_class(class_: OoadClass): None
+ load(): None
	// this module loads its child modules and its classes
	self.load_modules()
	self.load_classes()
- load_modules(): None
	// while has_more_module: append_module(load_next_module())
- has_more_module(): bool
	// channel: another child module remains in the path
- load_next_module(): Module
	// child = get_next_module_from_file()
	// -> child.load()
- get_next_module_from_file(): Module
	// channel: the next child module, in the model's module_type
- load_classes(): None
	// while has_more_class: append_class(load_next_class())
- has_more_class(): bool
- load_next_class(): OoadClass
	// class_ = get_next_class_from_file()
	// -> class_.load_properties()
	// -> class_.load_operations()
	// -> class_.load_relationships()
- get_next_class_from_file(): OoadClass
	// channel: the next class shell from the path, in the module's class_type

## OoadClass : OoadNode

+ OoadClass(source: OoadClass)
	// copies name, order, and intent
	// each source property, operation, and relationship becomes this channel's property, operation, and relationship
------
+ intent: str
+ properties: list[Property]
	// composition
+ operations: list[Operation]
	// composition
+ relationships: list[Relationship]
	// read from properties that have a relationship. The class does not store this list
+ property_type: type
	// the channel class this class uses to build the next property. JsonOoadClass sets JsonProperty. A property's own type hint stays on Property
+ operation_type: type
	// the channel class this class uses to build the next operation
+ relationship_type: type
	// the channel class this class uses to build the next relationship
----
- load_properties(): None
	// while has_more_property: append load_next_property()
- has_more_property(): bool
- load_next_property(): Property
	// property = get_next_property_from_file()
- get_next_property_from_file(): Property
- load_operations(): None
	// while has_more_operation: append load_next_operation()
- has_more_operation(): bool
- load_next_operation(): Operation
	// operation = get_next_operation_from_file()
	// -> operation.load_parameters()
- get_next_operation_from_file(): Operation
- load_relationships(): None
	// while has_more_relationship: append load_next_relationship()
- has_more_relationship(): bool
- load_next_relationship(): Relationship
- get_next_relationship_from_file(): Relationship

## Property : OoadNode

+ Property(source: Property)
	// copies name, order, type hint, description, access, and invariants
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

## Operation : OoadNode

+ Operation(source: Operation)
	// copies name, order, return type, description, invariants, and body
	// each source parameter becomes this channel's parameter
------
+ return_type: str
+ description: str
+ body: CodeBody
	// the statements as read from code, in the language they were written in
	// empty when the operation came from markdown, JSON, or a diagram
+ invariants: list[Invariant]
	// composition. Each // line under the operation, in file order
+ parameters: list[Parameter]
	// composition
+ parameter_type: type
----
- load_parameters(): None
	// while has_more_parameter: append load_next_parameter()
- has_more_parameter(): bool
- load_next_parameter(): Parameter
- get_next_parameter_from_file(): Parameter

## Invariant : OoadNode

A rule that must stay true for one property or one operation. The text is the // line. Order is the line order in the file.

+ Invariant(text: str, sequential_order: int)
	// copies text and order
------
+ text: str

## Parameter : OoadNode

+ Parameter(source: Parameter)
	// copies name, order, and type hint
------
+ type_hint: str

## Relationship

Optional on a property. Cardinality lives here. A class reads these from its properties.

+ Relationship(source: Relationship)
	// copies target, kind, cardinality, description, and order
------
+ target: str
+ kind: str
+ cardinality: str
+ description: str
+ sequential_order: int

## MarkdownOoadNode

+ strip_markup(text: str): str
	// backticks, then the surrounding stars. A module and a class read names through this

## MarkdownCleanEngineeringModel : CleanEngineeringModel

+ MarkdownCleanEngineeringModel(source: CleanEngineeringModel)
------
+ module_type: MarkdownModule
----
- load_content(): None
	// cursor is the markdown headings in the file. One file
- has_more_module(): bool
- get_next_module_from_file(): MarkdownModule
+ save(): str

## MarkdownModule : Module, MarkdownOoadNode

- has_more_module(): bool
- get_next_module_from_file(): MarkdownModule
- has_more_class(): bool
- get_next_class_from_file(): MarkdownOoadClass

## MarkdownOoadClass : OoadClass, MarkdownOoadNode

- has_more_property(): bool
- get_next_property_from_file(): Property
- has_more_operation(): bool
- get_next_operation_from_file(): Operation
- has_more_relationship(): bool
- get_next_relationship_from_file(): Relationship

## JsonOoadNode

+ record(): dict
	// this node's JSON object

## JsonCleanEngineeringModel : CleanEngineeringModel

+ JsonCleanEngineeringModel(source: CleanEngineeringModel)
------
+ module_type: JsonModule
----
- load_content(): None
	// cursor is the JSON module array in the file. One file
- has_more_module(): bool
- get_next_module_from_file(): JsonModule
+ save(): str

## JsonModule : Module, JsonOoadNode

- has_more_module(): bool
- get_next_module_from_file(): JsonModule
- has_more_class(): bool
- get_next_class_from_file(): JsonOoadClass

## JsonOoadClass : OoadClass, JsonOoadNode

- has_more_property(): bool
- get_next_property_from_file(): JsonProperty
- has_more_operation(): bool
- get_next_operation_from_file(): JsonOperation
- has_more_relationship(): bool
- get_next_relationship_from_file(): JsonRelationship

## JsonProperty : Property, JsonOoadNode

## JsonOperation : Operation, JsonOoadNode

- has_more_parameter(): bool
- get_next_parameter_from_file(): JsonParameter

## JsonParameter : Parameter, JsonOoadNode

## JsonRelationship : Relationship, JsonOoadNode

## DiagramNode

+ geometry: Geometry
+ cell_id: str
----
+ height(): int
+ keep_or_place(default: Geometry): Geometry
	// a saved box stays. Otherwise the default geometry is used
+ overlaps(other: DiagramNode): bool
	// the two boxes share area. Placement moves one until this is false
+ draw(page): object
	// keep_or_place, then the page places this node

## DiagramCleanEngineeringModel : CleanEngineeringModel

+ DiagramCleanEngineeringModel(source: CleanEngineeringModel)
	// children are DiagramModule and DiagramClass. A nested module is a DiagramModule whose parent is a DiagramModule
------
+ module_type: DiagramModule
----
+ save(): str
+ place_modules(): None
	// roots sit in columns by dependency depth. A column gap separates the columns. A row gap separates roots in one column
	// -> module.size()
	// -> module.place_children()
+ place_classes(): None
	// classes of one module, or one aggregate, sit in a tight cluster. A clear gap separates clusters
	// a saved class box stays when the boxes do not overlap. A new class shifts clear of the boxes that stayed
	// -> class.place_below(base) for a derived class
	// -> imported.place_above() or imported.place_beside()

## DiagramModule : Module, DiagramNode

+ class_type: DiagramClass
----
+ purpose_line(): str
+ shown_seam_terms(): list[str]
+ external_deps(): list[str]
+ size(): Geometry
	// width and height include the header and the child grid. A module with no children is one cell
+ place_children(): None
	// nested modules sit in a grid under the header, with a gap between cells
	// this module grows to that grid
	// -> child.size()
	// -> child.place_children()

## DiagramClass : OoadClass, DiagramNode

+ display_name(): str
+ extends_base_name(): str
----
+ place_below(base: DiagramClass): None
	// the base sits above this class. Sibling subtypes share one row under the base
	// a hub does not put four or more leaves in one wide row. The leaves fan into rows

## ImportedClass : DiagramClass

+ ImportedClass(source: OoadClass)
	// a class owned by another module. from_module names that module
------
+ from_module: str
----
+ key_properties(): list[Property]
	// the first properties on the card
+ place_above(): None
	// an inheritance import sits in a band above the local classes. The locals shift down by that band
+ place_beside(): None
	// an import that is not an ancestor sits beside the local class it links

## DrawIONode : DiagramNode

+ style(): str
+ html(): str
	// the cell label. A module writes purpose and seam terms. A class writes properties and operations
+ cell(): Vertex
	// one mxCell from cell_id, html, geometry, and style

## DrawIORelationship : Relationship

+ route(source: DrawIOClass, target: DrawIOClass): None
	// an orthogonal edge between the two class boxes
	// a clear path uses a straight run. A blocked path uses a channel, with at most two waypoints
	// the first segment leaves the source side head-on. The last segment enters the target side head-on
	// the edge does not enter any other class box
	// two edges do not share a column or a row. Edges on the same side use distinct anchors
	// a saved edge stays. A new edge is routed

## DrawIOCleanEngineeringModel : DiagramCleanEngineeringModel

+ DrawIOCleanEngineeringModel(source: CleanEngineeringModel)
	// DrawIOModule for each module, including a nested module, then DrawIOClass
------
+ module_type: DrawIOModule
----
- load_content(): None
	// cursor is the vertex cells in the file. One file
- has_more_module(): bool
- get_next_module_from_file(): DrawIOModule
+ save(): str
	// writes this model's cells

## DrawIOModule : DiagramModule, DrawIONode

- has_more_module(): bool
- get_next_module_from_file(): DrawIOModule
- has_more_class(): bool
- load_next_class(): DrawIOClass
	// modules view: returns the class and stops. No properties, operations, or relationships
	// class view: the class loads properties and operations
- get_next_class_from_file(): DrawIOClass

## DrawIOClass : DiagramClass, DrawIONode

## MiroNode : DiagramNode

+ mermaid_id(): str
+ mermaid_lines(): list[str]
	// a module writes name, purpose, and seam terms. A class writes properties and operations

## MiroCleanEngineeringModel : DiagramCleanEngineeringModel

+ MiroCleanEngineeringModel(source: CleanEngineeringModel)
------
+ module_type: MiroModule
----
- load_content(): None
	// cursor is the Miro items in the file. One file
- has_more_module(): bool
- get_next_module_from_file(): MiroModule
+ save(): str

## MiroModule : DiagramModule, MiroNode

- has_more_module(): bool
- get_next_module_from_file(): MiroModule
- has_more_class(): bool
- load_next_class(): MiroClass
	// modules view: returns the class and stops. No properties, operations, or relationships
	// class view: the class loads properties and operations
- get_next_class_from_file(): MiroClass

## MiroClass : DiagramClass, MiroNode

## CodeLanguage

How one programming language spells what every code channel writes the same way. Python, TypeScript, JavaScript, and Java are instances, not subtypes: they differ only in data. Stories and BDD code channels use the same instances.

+ named(name: str): CodeLanguage
	// the instance for python, typescript, javascript, or java
------
+ name: str
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
+ assignment(name: str): str
	// the constructor line that stores a parameter on the new object
+ interaction(callee: str): str
	// one -> collaborator.operation note as a call in this language. Empty for a prose note

## CodeBody

The statements inside one operation, test, or step, kept with the language they were read in. The one rule every code channel uses to write a body lives here.

+ CodeBody(text: str, language: CodeLanguage | None)
	// text is dedented. A body that is_unfinished in its language is empty
------
+ text: str
+ language: CodeLanguage | None
+ is_empty: bool
----
+ lines_in(language: CodeLanguage, indent: str, unfinished: str): list[str]
	// same language: the text as read, under indent
	// another language: the text commented out under a note naming its language, then unfinished
	// empty: unfinished
	// unfinished is the line that marks a body still to write: language.unfinished for production code, the BDD signature marker for a spec, the step placeholder for a story
	// an empty unfinished writes no line: a constructor whose assignments complete it
+ in_language_of(other: CodeBody, language: CodeLanguage): CodeBody
	// whichever of self and other is written in language, self first. Neither: self
	// render uses this to keep a body from the previous file when the model's body is not in the target language

## CodeOoadNode

+ slug(): str
	// folder or file name
+ name_from_slug(slug: str): str
	// the name read back from a folder or a file

## CodeCleanEngineeringModel : CleanEngineeringModel

+ CodeCleanEngineeringModel(source: CleanEngineeringModel)
	// path for load is the path-to-content map of the source tree
------
+ module_type: CodeModule
+ language: CodeLanguage
	// each language model sets its instance
----
- load_content(): None
	// cursor is module folders, then nested module folders, then one class file per class
- has_more_module(): bool
- get_next_module_from_file(): CodeModule
+ save(): str
	// one class file per class, under the module folders
+ render(canonical: CleanEngineeringModel, previous: str | None): str
	// the one code render. Every language writes through this walk and changes only how a line is spelled
	// previous set: each operation keeps the previous file's body when the canonical body is not in this language
	// -> parse(previous)
	// -> body.in_language_of(previous_body, language)
	// file header with the preamble, then per module: a === name === banner comment, then each class
+ operation_body(class_name: str, operation_name: str): CodeBody
	// the body this model read. "constructor" finds the constructor in any language
- render_class(oclass: OoadClass, known_names: list[str], kept: CodeCleanEngineeringModel): list[str]
	// interface: signatures only. Otherwise class open, properties with their notes, constructor, operations, class close
	// one blank line between member groups
- render_operation(operation: Operation, contract: bool, previous: CodeBody): list[str]
	// signature, then render_body unless contract
- render_body(operation: Operation, previous: CodeBody): list[str]
	// a body in this language: body.lines_in
	// an empty body: invariant comments, then language.interaction for each callee, then language.unfinished
	// a body from another language: its text commented out, then language.unfinished
	// so a body from another language stays visible and the operation fails loudly until it is written
	// the constructor ends with a field assignment per parameter instead of language.unfinished
+ doc_text(operation: Operation): str
	// the description when it is the operation's own text, not one joined from its comments
- file_header(canonical: CleanEngineeringModel, preamble: CodeBody): list[str]
- class_open(oclass: OoadClass, known_names: list[str]): list[str]
- class_close(has_members: bool): list[str]
- property_line(property: Property, contract: bool): list[str]
- constructor_lines(oclass: OoadClass, constructor: Operation | None, body: list[str]): list[str]
- signature(operation: Operation, contract: bool): list[str]
- block_close(): list[str]
	// each language overrides the spelling operations above. None of them decides what a body holds

## CodeModule : Module, CodeOoadNode

+ class_type: CodeOoadClass
----
- has_more_module(): bool
- get_next_module_from_file(): CodeModule
- has_more_class(): bool
- get_next_class_from_file(): CodeOoadClass

## CodeOoadClass : OoadClass, CodeOoadNode

- has_more_property(): bool
- get_next_property_from_file(): Property
- has_more_operation(): bool
- get_next_operation_from_file(): CodeOperation
- has_more_relationship(): bool
- get_next_relationship_from_file(): Relationship

## CodeOperation : Operation, CodeOoadNode

- has_more_parameter(): bool
- get_next_parameter_from_file(): Parameter

## PythonCleanEngineeringModel : CodeCleanEngineeringModel

+ PythonCleanEngineeringModel(source: CleanEngineeringModel)
------
+ module_type: PythonModule
+ language: CodeLanguage
	// CodeLanguage.named("python")
----
+ save(): str
- file_header, class_open, class_close, property_line, constructor_lines, signature, block_close
	// Python spelling only. render, render_class, render_operation, and render_body stay on CodeCleanEngineeringModel

## PythonModule : CodeModule

+ class_type: PythonOoadClass

## PythonOoadClass : CodeOoadClass

- get_next_property_from_file(): Property
- get_next_operation_from_file(): CodeOperation
- get_next_parameter_from_file(): Parameter

## TypeScriptCleanEngineeringModel : CodeCleanEngineeringModel

+ TypeScriptCleanEngineeringModel(source: CleanEngineeringModel)
------
+ module_type: TypeScriptModule
+ language: CodeLanguage
	// CodeLanguage.named("typescript")
----
+ save(): str
- file_header, class_open, class_close, property_line, constructor_lines, signature, block_close
	// TypeScript spelling only. render, render_class, render_operation, and render_body stay on CodeCleanEngineeringModel

## TypeScriptModule : CodeModule

+ class_type: TypeScriptOoadClass

## TypeScriptOoadClass : CodeOoadClass

- get_next_property_from_file(): Property
- get_next_operation_from_file(): CodeOperation
- get_next_parameter_from_file(): Parameter

## JavaScriptCleanEngineeringModel : CodeCleanEngineeringModel

+ JavaScriptCleanEngineeringModel(source: CleanEngineeringModel)
------
+ module_type: JavaScriptModule
+ language: CodeLanguage
	// CodeLanguage.named("javascript")
----
+ save(): str
- file_header, class_open, class_close, property_line, constructor_lines, signature, block_close
	// JavaScript spelling only. render, render_class, render_operation, and render_body stay on CodeCleanEngineeringModel

## JavaScriptModule : CodeModule

+ class_type: JavaScriptOoadClass

## JavaScriptOoadClass : CodeOoadClass

- get_next_property_from_file(): Property
- get_next_operation_from_file(): CodeOperation
- get_next_parameter_from_file(): Parameter

## JavaCleanEngineeringModel : CodeCleanEngineeringModel

+ JavaCleanEngineeringModel(source: CleanEngineeringModel)
------
+ module_type: JavaModule
+ language: CodeLanguage
	// CodeLanguage.named("java")
----
+ save(): str
- file_header, class_open, class_close, property_line, constructor_lines, signature, block_close
	// Java spelling only. render, render_class, render_operation, and render_body stay on CodeCleanEngineeringModel

## JavaModule : CodeModule

+ class_type: JavaOoadClass

## JavaOoadClass : CodeOoadClass

- get_next_property_from_file(): Property
- get_next_operation_from_file(): CodeOperation
- get_next_parameter_from_file(): Parameter

## Graph explorer loading

`harness/graph/working_copy.py` walks the repo, parses TypeScript under `src/` with `TypeScriptCleanEngineeringModel`, and registers nodes and edges on `PracticeGraph`. `Graph.load_working_copy` calls `fill_working_copy`, then `root_node.populate()` for the explorer tree. DDD and cross-practice story edges are built in the same module after clean engineering facts exist.

Python, TypeScript, JavaScript, and Java extend the code types: model, module, and class. There is no language property type and no language parameter type. A language class reads the property, the operation, and the parameter. A nested module is a module whose parent is a module. `CleanEngineeringModel` loads the top modules. `Module` loads its child modules and its classes. `load_properties`, `load_operations`, and `load_relationships` stay on `OoadClass`. `load_parameters` stays on `Operation`. Every other model implements `save(): str`. Markdown and JSON are one file and continue through parameters and relationships. A code path is a folder of module folders and one class file per class. Draw.io and Miro extend `DiagramCleanEngineeringModel`. A modules view stops at classes. A class view continues through properties and operations. `DiagramNode` owns `geometry`, `height`, `keep_or_place`, `overlaps`, and `draw`. `DiagramCleanEngineeringModel.place_modules` lays out module columns. `DiagramModule.size` and `place_children` lay out the nested grid. `place_classes` clusters classes. `DiagramClass.place_below` puts a base above its subtypes. `ImportedClass` sits above or beside. A Draw.io node is a `DrawIONode`: `style`, `html`, and `cell`. `DrawIORelationship.route` draws the orthogonal edge. A Miro node is a `MiroNode`: `mermaid_id` and `mermaid_lines`. An `ImportedClass` is a `DiagramClass` owned by another module. A code node is a `CodeOoadNode`: `slug` and `name_from_slug`. A markdown node is a `MarkdownOoadNode`: `strip_markup`. A JSON node is a `JsonOoadNode`: `record`. A channel overrides only the `has_more_*` and `get_next_*_from_file` reads for the nodes its path contains.
