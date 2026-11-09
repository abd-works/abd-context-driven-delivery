# Domain Driven Design Model

*BoundedContextMap* reads text into bounded contexts and aggregates, the way the class model reads files and folders. A nested bounded context is a bounded context whose parent is a bounded context. Each bounded context holds one or more aggregates. When the text has no bounded context, the map has one bounded context and there is no folder for it; the aggregates sit in that context. A bounded context is a module. An aggregate is a module. Entity, value object, repository, domain service, specification, and factory are classes; a domain event and an invariant object are properties. An aggregate's root is an entity with `is_root` true. Markdown continues through a class card when the file has one, and stops at the class name when the file has only the name.

The graph (*Ddd*'s reading part, *DddReading* in `practices/ddd/model/graph_reading.py`) reads a bounded context from each folder holding `.context/bounded-context.md`, through `BoundedContext.load_context_folder`, and a building block from each class Clean Engineering read whose DDD stereotype, or, in a folder that holds a domain, whose name gives it a DDD kind. Each building block is a *BuildingBlock* node that holds the class Clean Engineering read (through a *TacticalClass*): the class's own facts are the class's, and the tactical facts DDD's rules read are the block's, worked out from the class's operations; the class itself stays Clean Engineering's node.

Callers use the base nodes. The practice's formats (`Ddd(...).formats`: sketch, markdown, drawio) each name the map class that reads and writes that format; `parse` reads text into a `BoundedContextMap` and `render` writes one back. Every format subclasses `BoundedContextMap`, which holds the map's working operations (`context_at`, `aggregate_at`, `wire_events`, `has_class_cards`) and names the context type it reads into (`bounded_context_type`); each context type names the aggregate type it opens (`aggregate_type`), and a nested context is of its parent's own type. The sketch and draw.io formats name the markdown context type, whose nodes read and write the markdown and sketch notation. The draw.io map is itself Clean Engineering's draw.io diagram (`DrawIOBoundedContextMap(BoundedContextMap, DrawIOCleanEngineeringModel)`): it draws its contexts and aggregates as its own modules and renders itself; reading a drawing builds each cell as the cell type its style names (`kind=boundedContext;`, `kind=aggregate;`), and each cell reads itself into the map. The python and typescript formats are Clean Engineering's class models: the map writes itself into one as that format's own classes (`write_classes(model)`), so the format renders itself with no second copy, and reads one back (`read_class_model(model)`), each aggregate taking the classes its place names as the cards they are, with their own members; a markdown text with no aggregate is a plain class model, which `Ddd` hands to its Clean Engineering companion's own adapter. A card's stereotypes are the class's `stereotypes`, which the code channels write as decorators (`@aggregate_root`, `@AggregateRoot()`) and read back: a decorator with no arguments, or a `<<Mark>>` on the first line of the doc comment, is a stereotype, so Clean Engineering keeps no list of DDD's words. `stereotypes.KIND_OF_STEREOTYPE` is the one table of DDD's own words from that list — aggregate root, entity, value object, repository, domain service or service, domain event, specification, and factory — and the building block each names; a class marked `system` is another system's. `ClassCard.named` makes the card of the building block they name, the graph's building blocks read the same table through *TacticalClass*, and the tactical rules check `BUILDING_BLOCK_KINDS`. The DDD practice registers itself on `DomainNode`, the base of every DDD node, so the model never imports its practice. Where a class lives is its `module_path`, a Clean Engineering field (`["Customer | custom", "Customer Profile"]`), and an aggregate's integrations are dependencies of its root that carry the arc's fields as details (`Integration.as_dependency`, `MarkdownIntegration.kept_by`); the code formats write both in the class's doc comment and read them back.

```
bounded_context_map = MarkdownBoundedContextMap().parse(text)
```

# practices/ddd/model

- **Purpose:** Structure the software as DDD building blocks — bounded contexts, aggregates, and the stereotyped classes — so the model answers domain logic questions.
- **Seam (terms):** BoundedContextMap, BoundedContext, Aggregate, Integration, Entity, InvariantObject, ValueObject, Repository, DomainService, DomainEvent, Specification, Factory, MarkdownBoundedContextMap, SketchDddModel, DrawIOBoundedContextMap, ClassCard
- **Dependencies (one-way):** practices/clean_engineering/model — Module, OoadClass, Property, Operation, CleanEngineeringModel; harness/graph — Graph, ModelChildren; practices/sketch_document — SketchOutline; harness/guidance — SketchLens

*Module*, *OoadClass*, *Property*, *Operation*, and *CleanEngineeringModel* belong to Clean Engineering; this model only extends or uses them.

## BoundedContextMap

+ BoundedContextMap()
	// empty until parse
------
+ contexts: list[BoundedContext]
	// composition — a context has no map outside this bounded context map
	// a nested bounded context is a bounded context whose parent is a bounded context
	// no context in the text: the map has one context, and that context has no folder
+ bounded_context_type: type
	// the format's context type, which names its own aggregate type
+ every_aggregate: list[Aggregate]
	// every context's aggregates, nested contexts included
+ every_context: list[BoundedContext]
	// every context, each before the contexts nested in it
----
+ aggregate_reached_by(integration: Integration): Aggregate | None
	// in the context the target names, its entity or its aggregate; with no such context, the aggregate by name
+ has_class_cards: bool
	// a domain model, whose aggregates hold classes, rather than a bounded context map
+ context_at(labels: list[str]): BoundedContext
	// the context a place's labels name, opened the first time, in bounded_context_type
+ aggregate_at(path: str): Aggregate
	// the aggregate a module path names, `Sales | custom/ShoppingCart`
+ wire_events(entries: list[str]): None
	// each `Event: emitted by Producer; consumed by A, B` entry onto its producer's root
+ write_classes(model: CleanEngineeringModel): None
	// one module of model's own format per aggregate, named by its code_place
	-> Aggregate.write_classes_into(module)
+ read_class_model(model: CleanEngineeringModel): BoundedContextMap
	// each class's module_path, else the name of the module a drawing keeps it in, names its context and aggregate; classes with no place gather around the roots that hold them
	-> Aggregate.take_class(oclass)
	-> Aggregate.take_root_from_classes()
+ append_context(context: BoundedContext): None
- load_bounded_contexts(): None
	// while has_more_bounded_context: append load_next_bounded_context()
- has_more_bounded_context(): bool
- load_next_bounded_context(): BoundedContext
	// context = get_next_bounded_context_from_file()
	// -> context.load_bounded_contexts()
	// -> context.load_aggregates()
- get_next_bounded_context_from_file(): BoundedContext
	// the format: the next context shell, in bounded_context_type

## BoundedContext : Module

+ BoundedContext(name: str, sequential_order: int, graph: Graph | None = None)
	// a nested bounded context is a bounded context whose parent is a bounded context
------
+ owner: str
	// the heading text after |
+ label: str
	// the name, with the owner after | when it has one
+ contexts: ModelChildren[BoundedContext]
+ aggregates: ModelChildren[Aggregate]
	// composition — an aggregate has no context outside this one
+ aggregate_type: type
	// the aggregates this context opens, of its own format
+ every_aggregate: list[Aggregate]
	// this context's aggregates, then those of every context nested in it
+ enclosing_contexts: list[BoundedContext]
	// outermost first, ending with this context
+ context_file_lines: int
	// the lines in .context/bounded-context.md, so the graph node spans that file
+ module_path: str
	// each enclosing context's label, joined by `/`
----
+ append_context(context: BoundedContext): None
+ append_aggregate(aggregate: Aggregate): None
+ aggregate_named(name: str): Aggregate
	// this context's aggregate called name, opened the first time in this context's aggregate_type
+ load_context_folder(folder: Path): None
	// the name is the title of .context/bounded-context.md, else the folder's name
+ load_bounded_contexts(): None
	// while has_more_bounded_context: append_context(load_next_bounded_context())
+ load_aggregates(): None
	// while has_more_aggregate: append_aggregate(load_next_aggregate())
- has_more_bounded_context(): bool
- load_next_bounded_context(): BoundedContext
- get_next_bounded_context_from_file(): BoundedContext
	// the next child context, of this context's own type
- has_more_aggregate(): bool
- load_next_aggregate(): Aggregate
	// aggregate = get_next_aggregate_from_file()
	// -> aggregate.load_root()
- get_next_aggregate_from_file(): Aggregate
	// the next aggregate shell, in this context's aggregate_type

## Aggregate : Module

+ Aggregate(name: str, sequential_order: int, graph: Graph | None = None)
------
+ root: Entity | None
	// the entity in this aggregate whose is_root is true
+ integrations: list[Integration]
	// an arrow that sits on the aggregate
+ events: list[DomainEvent]
	// the domain events the root emits
+ members: list
	// what the root holds: its invariant objects; at model fidelity, the member cards
+ classes: list[OoadClass]
	// its building blocks: the aggregate is a Module, and they are its classes
+ place_labels: list[str]
	// each enclosing context's label, then the aggregate's name: the module path of each class it writes
+ code_place: str
	// the place labels as one module name, joined by ` · ` (`joined_module_path`)
+ module_path: str
	// its context's module_path, then its name: `Sales | custom/ShoppingCart`
----
+ take_root(entity: Entity): None
	// the entity becomes the root, its only way in, and records this aggregate
+ take_class(oclass: OoadClass): None
	// holds a class read from a class model
+ take_root_from_classes(): None
	// the class marked <<Aggregate Root>> becomes the root
+ write_classes_into(module: Module): None
	// each class as module's own class
+ load_root(): None
	// -> take_root(root)
	// -> root.load_invariant_objects()

## Integration

+ Integration(context: str = "", aggregate: str = "", entity: str = "", held_by: str = "")
------
+ context: str
	// the bounded context the arrow reaches
+ aggregate: str
	// the aggregate the arrow reaches
+ entity: str
	// the class the arrow reaches; a target that names one class names only its entity
+ held_by: str
	// the identity the aggregate holds that class by
+ direction: str
+ crosses: str
+ integration: str
+ pattern: str
	// Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Open Host / Published Language, or Separate Ways
+ FIELDS: tuple[str, ...]
	// pattern, direction, crosses, integration: the fields in the order an arc's lines write them under its target
+ PARTS: tuple[str, ...]
	// context, aggregate, entity, held_by: the parts of the target, each its own detail when a class model keeps the arc
+ target_name: str
	// the entity when the target names one, else the aggregate
----
+ as_dependency(): Relationship
	// the arc as a class model keeps it on the root: a dependency on target_name, labelled by its pattern, with each
	// part of its target and each of its other fields as a detail
+ Integration.keeps_one(dependency: Relationship): bool
	// whether a class model's dependency keeps an arc: it names a part of the arc's target as a detail
+ read_dependency(dependency: Relationship): None
	// the pattern from the label, the parts and the other fields from the details

## BuildingBlock : Node

A class Clean Engineering read, as the DDD building block it is in the graph (`graph_reading.py`). It holds the class
(`ooad_class`, through its *TacticalClass*); `get_fact` answers its own facts, then the class's, then the DDD nodes
around it, and it saves both.

+ BuildingBlock(practice: Ddd, tactical: TacticalClass, kind: str)
------
+ ooad_class: OoadClass
	// the class Clean Engineering read, which this building block is
+ peer_private_operations: list[str]
+ public_derive_operations: list[str]
+ delegating_operations: list[str]
+ identity_free_loads: list[str]
	// load, get, find, or fetch with no parameters that reads ambient state such as the session or request
+ named_for_its_kind: bool
	// the class's name follows the naming convention of the building block it is
+ public_operation_names: list[str]
+ lifecycle_operations: list[str]
	// the public operations that add to, find in, or remove from a collection
+ drives_a_screen: bool
	// it opens and shows, or its name is a screen's

*DddReading* is one read of a working copy into the graph that holds the DDD practice: bounded contexts, aggregates,
and a *BuildingBlock* for each class the Clean Engineering practice it extends read. A class's DDD stereotype always
names its building block; its name names one (`TacticalClass.inferred_kind`) only in a folder that holds a domain: one
a folder's `.context/bounded-context.md` covers, or one where a class carries a DDD stereotype. Elsewhere, such as a
toolkit folder whose `MarkdownRepository` or `AgentOperation` only ends like a building block, DDD makes nothing.
Each aggregate keeps the production classes in its folder that are no building block as its `bare_classes` fact,
leaving out test code, React screen modules, and classes marked as another system's;
`every-class-carries-ddd-stereotype` reports them. Each repository accesses the root its name says it keeps, and each
root associates with every other root its lines name with `// foreign Name`.

## DomainClass : OoadClass

The base of every DDD class: a Clean Engineering class that is one of the domain's building blocks, made with its name,
its order, and its intent.

+ DomainClass(name: str, sequential_order: int, intent: str = "")
------
+ tactical: TacticalClass
	// made once with the class: the one reading of which building block its stereotypes make it

## Entity : DomainClass

+ Entity(name: str, sequential_order: int)
------
+ identity: list[Property]
	// the properties that keep this entity the same thing
+ is_root: bool
	// true when this entity is an aggregate's root
+ aggregate: Aggregate | None
	// the aggregate this root is for. Set when is_root is true
+ invariant_objects: list[InvariantObject]
	// composition — properties with the invariant stereotype. These sub-objects change with this entity
+ invariant_object_type: type
----
+ load_invariant_objects(): None
	// while has_more_invariant_object: append load_next_invariant_object()
- has_more_invariant_object(): bool
- load_next_invariant_object(): InvariantObject
- get_next_invariant_object_from_file(): InvariantObject
	// the format: the next property with the invariant stereotype

## InvariantObject : Property

+ InvariantObject(name: str, sequential_order: int)
------
+ stereotype: str
	// invariant

## ValueObject : DomainClass

+ ValueObject(name: str, sequential_order: int)
	// no write operations and no setters: a change makes a new value
	// it clones as every class does (OoadClass.clone), members and stereotypes included

## Repository : DomainClass

+ Repository(name: str, sequential_order: int)
------
+ accesses: Entity | None
	// the entity in the model whose is_root is true
+ operations: list[Operation]
	// any of create, read, update, delete, and search. Not all of them
	// a search may appear more than once. Its name is search and what it searches

## DomainService : DomainClass

+ DomainService(name: str, sequential_order: int)
	// no state
	// an operation here is one no domain object can perform

## DomainEvent : Property

+ DomainEvent(name: str, sequential_order: int)
------
+ producer: Aggregate | None
+ consumers: list[Aggregate | DomainService]
	// one or many
+ subject: Property
	// the state of the event. A domain event always has one

## Specification : DomainClass

## Factory : DomainClass

`ClassCard.named(name, stereotypes)` makes the card a class with those stereotypes is read into: specification, value object, repository, domain service (or service), factory, entity, or aggregate root (an entity); a card with none is a plain class card.

## MarkdownDomainNode

+ plain_name(text: str): str
	// ** and backticks removed, and the text before |. Context, aggregate, and class names all come through this
+ owner_from(heading: str): str
	// the text after | on a context heading

## ClassCard : MarkdownDomainNode

The `####` card a building block reads and writes itself in markdown, and in a sketch's fence. Each markdown building
block is one: *MarkdownEntity*, *MarkdownValueObject*, *MarkdownRepository*, *MarkdownDomainService*,
*MarkdownSpecification*, *MarkdownFactory*, and *MarkdownClass* for a card whose stereotypes name no building block. Its
stereotypes are the class's `stereotypes`.

+ ClassCard.named(name: str, stereotypes: list[str]): ClassCard
+ ClassCard.from_heading(heading: str): ClassCard
+ ClassCard.read(section: list[str]): ClassCard
+ ClassCard.from_sketch(heading: str, lines: list[str]): list[ClassCard]
	// the card, then the repository its fence's `repo:` names
------
+ invariants: list[str]
+ is_root: bool
	// marked <<Aggregate Root>>, or made its aggregate's root
+ is_repository: bool
+ heading: str
+ plain_properties: list[Property]
	// what the class holds, not its events or invariant objects
----
+ add_member(line: str, as_operation: bool): Property | Operation | None
+ read_lines(lines: list[str]): None
+ read_sketch_lines(lines: list[str]): list[ClassCard]
+ lines(): list[str]
+ property_lines(): list[str]
+ operation_lines(): list[str]
+ sketch_lines(): list[str]
+ write_into(module: Module, place: list[str]): OoadClass
	// adds the card to module as that format's own class: its stereotypes, its intent, its members, and place as its module_path
+ ClassCard.from_code(oclass: OoadClass): ClassCard
	// the card a class read from code or a class drawing is, holding the class's own members and intent, without its constructor

## MarkdownBoundedContextMap : BoundedContextMap, MarkdownDomainNode

The `markdown` format.

+ MarkdownBoundedContextMap()
------
+ bounded_context_type: MarkdownBoundedContext
	// whose aggregate_type is MarkdownAggregate
----
+ parse(text: str): MarkdownBoundedContextMap
	// fills this map and returns it
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str
	// writes the map it is given: each context's own lines, then the event map
+ save(): str
	// this map, as render writes it
+ holds_classes_only: bool
	// the text named no aggregate: a plain class model
- has_more_bounded_context(): bool
- get_next_bounded_context_from_file(): MarkdownBoundedContext
	// the next `## Context | owner` heading; the context reads the lines under it
	-> MarkdownBoundedContext.read_lines

## MarkdownBoundedContext : BoundedContext, MarkdownDomainNode

------
+ notes: list[str]
	// why the context exists, as the sketch noted it above its aggregates; written as `> ` lines
+ module_name: str
+ module_notes: list[str]
	// the clean-engineering module the context is built as, with its seam and constraint
+ group_notes: dict[str, list[str]]
	// the notes under each heading that groups aggregates
----
+ read_lines(lines: list[str]): None
	// its own lines: notes, module, group headings, and each aggregate, which reads its own section
	-> MarkdownAggregate.load_root
+ lines(): list[str]
+ read_note(line: str, group: str | None): None
	// to the group it sits under, else the module, else the context
+ read_sketch_lines(lines: list[str]): None
	// its lines of a sketch: holders, entities, notes, and each aggregate's fences
+ sketch_lines(): list[str]

## MarkdownAggregate : Aggregate, MarkdownDomainNode

------
+ source_lines: list[str]
	// the lines under the aggregate's heading; load_root reads the root, its cards, and its arcs from them
+ classes: list[ClassCard]
	// its building blocks, as the cards of its Module classes
+ sketch_fences: list[tuple[str, list[str]]]
	// the entity fences a sketch lists under the aggregate
+ members: list
	// the member cards, else the root's invariant objects
+ group: str | None
	// the sketch heading the aggregate was listed under
+ root_card: ClassCard | None
+ repository: ClassCard | None
+ member_cards: list[ClassCard]
+ ordered_cards: list[ClassCard]
	// root, then its repository, then members — the one card order every format uses
----
+ load_root(): None
+ take_root_card(): None
	// the <<Aggregate Root>> card's class becomes the root
+ lines(): list[str]
+ integration_lines(indent: str = ""): list[str]
	// the aggregate's arcs under `Integrations:` and the root's events under `emits events:`
+ load_sketch(): None
+ sketch_lines(): list[str]
+ take_class(oclass: OoadClass): None
	// a class read from a class model, held as the card it is; each dependency of it that keeps an arc is one of this aggregate's integrations
	-> ClassCard.from_code
	-> MarkdownIntegration.kept_by
+ take_root_from_classes(): None
	// once its cards are read: relationships, and the root card
+ write_classes_into(module: Module): None
	// each card as module's own class, kept in the aggregate's place; the root depends on each class an integration reaches, the arc whole as that dependency
	-> ClassCard.write_into
	-> Integration.as_dependency
+ infer_relationships(): None

## MarkdownEntity : ClassCard, Entity

+ MarkdownEntity(name: str, sequential_order: int, member_lines: list[str] | None = None)
----
- has_more_invariant_object(): bool
- get_next_invariant_object_from_file(): MarkdownInvariantObject

## MarkdownInvariantObject : InvariantObject, MarkdownDomainNode

## MarkdownIntegration : Integration, MarkdownDomainNode

+ MarkdownIntegration.read_arcs(lines: list[str]): list[MarkdownIntegration]
	// each `- target` line opens an arc and the `key: value` lines under it fill it
+ MarkdownIntegration.targeting(text: str): MarkdownIntegration
	// the arc to `→ Context · Aggregate · Entity (by Identity)`, or to one class alone: the one reading of the `·` text
+ MarkdownIntegration.kept_by(dependency: Relationship): MarkdownIntegration | None
	// the arc a class model's dependency keeps, when its details name a part of the arc's target
------
+ target: str
	// the target as the arc's line writes it: the one writing of the `·` text
----
+ lines(): list[str]
	// `- target`, then each field it has, indented: what an aggregate writes under `Integrations:`
+ read_field(line: str): None

## SketchDddModel : BoundedContextMap

The `sketch` format: the `domain driven design:` section of an integrated sketch.

----
+ parse(text: str): SketchDddModel
	// where each context starts, the prose it skips, and the event map; each context reads its own lines
	-> SketchOutline.body_for
	-> MarkdownBoundedContext.read_sketch_lines
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str

## DrawIOBoundedContextMap : BoundedContextMap, DrawIOCleanEngineeringModel

The `drawio` format. A bounded context and an aggregate are modules and the building blocks are classes, so the map is
Clean Engineering's draw.io diagram, with its layout and its arrow routing; DDD keeps no layout of its own. The bounded
context map is the modules view: each context a module, each aggregate a module nested in its context's (named by its
`module_path`, `Sales | custom/ShoppingCart`) listing its `drawn_members`, and each integration a dependency arrow named
by its pattern. Each cell's style names its kind (`kind=boundedContext;`, `kind=aggregate;`), which Clean
Engineering's reader builds back into the cell type through `module_cell_types`; the purpose line (`bounded context`,
`aggregate`) is there for the reader of the drawing. At model fidelity the aggregate view is the class view: the map
writes its cards into its own modules (`write_classes`), each card a class with its stereotypes, kept in the module its
place names, with a dependency arrow where an operation calls into another aggregate and from the root along each
integration.

+ DrawIOBoundedContextMap()
------
+ module_cell_types: (DrawIOContextCell, DrawIOAggregateCell, DrawIOModule)
	// the cell types its drawing reads back, each picked by the kind its style names
----
+ parse(text: str): DrawIOBoundedContextMap
	// a diagram with classes reads through read_class_model, taking each class's place from its module; otherwise each cell reads itself into the map, then each draws its integrations
	-> DrawIOCleanEngineeringModel.parse
	-> BoundedContextMap.read_class_model
	-> DrawIOMapCell.read_into
	-> DrawIOMapCell.read_integrations_into
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str
	// aggregates with class cards (model fidelity): the class view; otherwise the modules view, drawn as its own modules
	-> BoundedContextMap.write_classes
	-> BoundedContextMap.aggregate_reached_by
	-> DrawIOCleanEngineeringModel.render

## DrawIOMapCell : DrawIOModule

A module on the map that reads itself back into the map.

----
+ read_into(drawn: DrawIOBoundedContextMap): None
+ read_integrations_into(drawn: DrawIOBoundedContextMap): None

## DrawIOContextCell : DrawIOMapCell

A bounded context on the map: a module named by the context's `module_path`, of kind `boundedContext`, whose purpose
line is `bounded context`. It reads itself back as the context its path names.

## DrawIOAggregateCell : DrawIOMapCell

An aggregate on the map: a module nested in its context's module, of kind `aggregate`, whose purpose line is
`aggregate`, that lists up to ten of the aggregate's `drawn_members`, where Clean Engineering's module lists six seam
terms. It reads itself back as the aggregate its path names, with the root its members show, and each arrow it draws as
an integration.

## Clean Engineering conversion

A code file is a Clean Engineering class model. `BoundedContextMap.write_classes(model)` writes the map into the format's own model: each aggregate a module of that format named by its place (`Context | owner · Aggregate`), each card a class of that format that keeps its stereotypes and has the aggregate's place labels as its `module_path`. The format renders that model as itself, so the map is copied once, into the format, as every format copies the model it writes; a code class writes its module path as its doc comment's `Module:` line, and the dependencies that carry details as `---<<pattern>>--> Target` lines with their details under them (Clean Engineering's `DocComment`). `read_class_model(model)` reads one back: each aggregate takes its classes as the cards they are, holding the classes' own members and intent, and the arcs their dependencies keep as its integrations. Each class carries the relationships its properties' types name, a dependency on each class of another aggregate its operations call (named by the operation), and the root a dependency on each class an integration reaches (the arc whole, `Integration.as_dependency`), so the draw.io class view draws them. A class with no module path takes its place from its module's name, which is where a diagram keeps it.

`BoundedContextMap` loads the contexts. `BoundedContext` loads its child contexts and its aggregates. `Aggregate` knows its root: the `Entity` whose `is_root` is true, and that entity records the aggregate. `Entity` loads its invariant objects; an invariant object is a property with the invariant stereotype, and it changes with the entity. A format overrides only the `has_more_*` and `get_next_*_from_file` reads for the nodes its text contains, plus `parse` and `render`.
