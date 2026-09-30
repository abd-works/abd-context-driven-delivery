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
	// CodeQL runs once over the database. Its cursor is the row lists
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
	// copies name, order, description, seam, seam terms, dependencies, and constraint
	// a nested module is a module whose parent is a module
	// each source child module becomes this channel's module
	// each source class becomes this channel's class
------
+ description: str
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
	// copies name, order, return type, description, and invariants
	// each source parameter becomes this channel's parameter
------
+ return_type: str
+ description: str
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
----
- load_content(): None
	// cursor is module folders, then nested module folders, then one class file per class
- has_more_module(): bool
- get_next_module_from_file(): CodeModule
+ save(): str
	// one class file per class, under the module folders

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
----
+ save(): str

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
----
+ save(): str

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
----
+ save(): str

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
----
+ save(): str

## JavaModule : CodeModule

+ class_type: JavaOoadClass

## JavaOoadClass : CodeOoadClass

- get_next_property_from_file(): Property
- get_next_operation_from_file(): CodeOperation
- get_next_parameter_from_file(): Parameter

## CodeQL class model

CodeQL mixes the graph node into the class-model types. `Node` is that common node: identity, edges, and the graph. `CodeQLOoadNode` adds the clean-engineering behavior every CodeQL class-model type uses. Each type then adds only its own links. CodeQL runs over the database built from a folder, or a collection of folders. It does not copy another model. Its `load_content` is that one run, and it returns five row lists: classes, operations, properties, parameters, and calls. `load_next` reads the next row for the node it is building. `named()` looks up a node that run already loaded. Markdown, JSON, Draw.io, Miro, and the code languages do not resolve it.

## Node

The same graph node the story types mix in.

+ practice: str
+ source
	// the file and line this node was read from
+ node_id: str
	// the same id is the same node
+ graph
	// the practice graph this node has joined
----
+ semantic_type(): str
+ slug(name: str): str
+ join(graph): Node
	// registers this node and sets node_id
+ relate(kind, to): Relationship
	// one edge from this node to another
+ related(kind): list
	// the nodes on that edge. Incoming edges are read with direction in
+ children(): list
	// the nodes this node owns

## CodeQLOoadNode : Node

+ practice: clean_engineering
+ home_module: Node
	// the module this node belongs to, or empty
----
- relate_once(kind, to): None
	// relate when this kind does not already hold that node_id
- named(name, semantic_type): Node
	// the node this run already loaded, with this name and type

## CodeQLCleanEngineeringModel : CleanEngineeringModel, CodeQLOoadNode

+ CodeQLCleanEngineeringModel()
	// empty until load
	// the database holds a folder, or a collection of folders
------
+ module_type: CodeQLModule
----
- load_content(): None
	// CodeQL override: one run over the database
	// cursor is the class rows, operation rows, property rows, parameter rows, and call rows
- has_more_module(): bool
	// another class row names a module not yet built
- get_next_module_from_file(): CodeQLModule
	// the module named on that class row
+ save(): str
	// no-op. The graph is the structure this model built

## CodeQLModule : Module, CodeQLOoadNode

+ CodeQLModule()
	// built from the module name on a class row
	// owns is each child module and each class row for this module
	// depends_on is each module a call row leaves for another module
------
+ owns
	// each child module and class. The child belongs to this module
+ depends_on
	// a module whose operation this module's operation invokes
----
- load_next_module(): CodeQLModule
	// the next class row names a child module. relate_once stores owns, and the child belongs to this module
- load_next_class(): CodeQLOoadClass
	// the next class row for this module. relate_once stores owns, and the class belongs to this module
	// a class whose name carries a DDD stereotype is that DDD graph class

## CodeQLOoadClass : OoadClass, CodeQLOoadNode

+ CodeQLOoadClass()
	// the next class row
	// owns is each property row and operation row for this class
	// depends_on is each class a call row leaves for another class
------
+ owns
	// each property and operation. The member belongs to this class
+ depends_on
	// a class whose operation this class's operation invokes
----
- load_next_property(): CodeQLProperty
	// the next property row for this class. relate_once stores owns, and the property belongs to this class
	// -> property.load_has_type()
	// -> property.load_relationship()
- load_next_operation(): CodeQLOperation
	// the next operation row for this class. relate_once stores owns, and the operation belongs to this class
	// -> operation.load_parameters()
	// -> operation.load_returns()
	// -> operation.load_invokes()

## CodeQLProperty : Property, CodeQLOoadNode

+ CodeQLProperty()
	// the next property row for this class
	// has_type and the relationship are the class named on that row
------
+ has_type
	// the class named by the type hint. A primitive or a third-party type has none
----
- load_has_type(): None
	// named() finds the class this run already loaded. relate_once stores it on has_type
- load_relationship(): None
	// composition, aggregation, or associates, from the property stereotype
	// relate_once stores that edge from this class to the same class

## CodeQLOperation : Operation, CodeQLOoadNode

+ CodeQLOperation()
	// the next operation row for this class
	// has_parameter is each parameter row for this operation
	// returns and invokes are the call rows and the return named on this operation row
------
+ has_parameter
	// each parameter. The parameter belongs to this operation
+ returns
	// the class named by the return type, or empty
+ invokes
	// each operation this operation calls. The operation includes its class
----
- load_parameters(): None
	// the next parameter row for this operation. relate_once stores has_parameter, and the parameter belongs to this operation
- load_returns(): None
	// named() finds the class this run already loaded. relate_once stores it on returns
- load_invokes(): None
	// the next call row for this operation. named() finds the callee this run already loaded. relate_once stores it on invokes
	// a callee on another class: relate_once stores depends_on on this class
	// a callee in another module: relate_once stores depends_on on this module

## CodeQLParameter : Parameter, CodeQLOoadNode

+ CodeQLParameter()
	// the next parameter row for this operation

A transform builds the other channel from this model. The copy traverses owns, belongs to, has type, the relationship, has parameter, returns, invokes, and depends on, and writes each related node in that channel's format.

```
markdown = MarkdownCleanEngineeringModel(codeql_model)
markdown.save()
```

`codeql_model.save()` returns an empty string.

Python, TypeScript, JavaScript, and Java extend the code types: model, module, and class. There is no language property type and no language parameter type. A language class reads the property, the operation, and the parameter. A nested module is a module whose parent is a module. `CleanEngineeringModel` loads the top modules. `Module` loads its child modules and its classes. `load_properties`, `load_operations`, and `load_relationships` stay on `OoadClass`. `load_parameters` stays on `Operation`. `CodeQLCleanEngineeringModel.save` returns an empty string. Every other model implements `save(): str`. Markdown and JSON are one file and continue through parameters and relationships. A code path is a folder of module folders and one class file per class. Draw.io and Miro extend `DiagramCleanEngineeringModel`. A modules view stops at classes. A class view continues through properties and operations. `DiagramNode` owns `geometry`, `height`, `keep_or_place`, `overlaps`, and `draw`. `DiagramCleanEngineeringModel.place_modules` lays out module columns. `DiagramModule.size` and `place_children` lay out the nested grid. `place_classes` clusters classes. `DiagramClass.place_below` puts a base above its subtypes. `ImportedClass` sits above or beside. A Draw.io node is a `DrawIONode`: `style`, `html`, and `cell`. `DrawIORelationship.route` draws the orthogonal edge. A Miro node is a `MiroNode`: `mermaid_id` and `mermaid_lines`. An `ImportedClass` is a `DiagramClass` owned by another module. A code node is a `CodeOoadNode`: `slug` and `name_from_slug`. A markdown node is a `MarkdownOoadNode`: `strip_markup`. A JSON node is a `JsonOoadNode`: `record`. A channel overrides only the `has_more_*` and `get_next_*_from_file` reads for the nodes its path contains.
