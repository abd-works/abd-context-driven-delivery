# Domain Driven Design Model

*BoundedContextMap* reads text into bounded contexts and aggregates, the way the class model reads files and folders. A nested bounded context is a bounded context whose parent is a bounded context. Each bounded context holds one or more aggregates. When the text has no bounded context, the map has one bounded context and there is no folder for it; the aggregates sit in that context. A bounded context is a module. An aggregate is a module. Entity, value object, repository, domain service, specification, and factory are classes; a domain event and an invariant object are properties. An aggregate's root is an entity with `is_root` true. Markdown continues through a class card when the file has one, and stops at the class name when the file has only the name.

The graph (*Ddd*'s `read_working_copy`, with its readers in `practices/ddd/model/graph_reading.py`) reads a bounded context from each folder holding `.context/bounded-context.md`, through `BoundedContext.load_context_folder`, and a building block from each class Clean Engineering read whose stereotypes or name give it a DDD kind. Each building block is a *BuildingBlock* node that holds the class Clean Engineering read (through a *TacticalClass*): the class's own facts are the class's, and the tactical facts DDD's rules read are the block's, worked out from the class's operations; the class itself stays Clean Engineering's node.

Callers use the base nodes. The practice's formats (`Ddd(...).formats`: sketch, markdown, drawio) each name the map class that reads and writes that format; `parse` reads text into a `BoundedContextMap` and `render` writes one back. The python and typescript formats are Clean Engineering's class models: the markdown map writes itself as one (`class_model()`) and reads one back (`read_class_model(model)`); a markdown text with no aggregate is a plain class model, which `Ddd` hands to its Clean Engineering companion's own adapter. A card's stereotypes are the class's `stereotypes`, which the code channels write as decorators (`@aggregate_root`, `@AggregateRoot()`) and read back: a decorator with no arguments, or a `<<Mark>>` on the first line of the doc comment, is a stereotype, so Clean Engineering keeps no list of DDD's words. `tactical_stereotypes` keeps DDD's own words from that list — aggregate root, entity, value object, repository, domain service or service, domain event, specification, factory, and system — and `ClassCard.named` makes the card of the building block they name. Where the class lives rides in its intent's first line (`Customer · Customer Profile`).

```
bounded_context_map = MarkdownBoundedContextMap().parse(text)
```

# practices/ddd/model

- **Purpose:** Structure the software as DDD building blocks — bounded contexts, aggregates, and the stereotyped classes — so the model answers domain logic questions.
- **Seam (terms):** BoundedContextMap, BoundedContext, Aggregate, Integration, Entity, InvariantObject, ValueObject, Repository, DomainService, DomainEvent, Specification, Factory, MarkdownBoundedContextMap, SketchDddModel, DrawIOBoundedContextMap, ClassCard
- **Dependencies (one-way):** practices/clean_engineering/model — Module, OoadClass, Property, Operation, CleanEngineeringModel; harness/graph — Graph, ModelChildren; actions/sketch — SketchOutline, SketchLens

*Module*, *OoadClass*, *Property*, *Operation*, and *CleanEngineeringModel* belong to Clean Engineering; this model only extends or uses them.

## BoundedContextMap

+ BoundedContextMap()
	// empty until load or parse
------
+ path: str
+ contexts: list[BoundedContext]
	// composition — a context has no map outside this bounded context map
	// a nested bounded context is a bounded context whose parent is a bounded context
	// no context in the text: the map has one context, and that context has no folder
+ bounded_context_type: type
+ aggregate_type: type
+ every_aggregate: list[Aggregate]
	// every context's aggregates, nested contexts included
+ every_context: list[BoundedContext]
	// every context, each before the contexts nested in it
----
+ aggregate_reached_by(integration: Integration): Aggregate | None
	// in the context the target names, its entity or its aggregate; with no such context, the aggregate by name
+ load(path: str): BoundedContextMap
	// stores path, then runs the same walk for every format
	self.path = path
	self.load_bounded_context_map_content()
	self.load_bounded_contexts()
+ save(): str
+ append_context(context: BoundedContext): None
- load_bounded_context_map_content(): None
	// the format prepares its cursor over path
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
+ every_aggregate: list[Aggregate]
	// this context's aggregates, then those of every context nested in it
+ enclosing_contexts: list[BoundedContext]
	// outermost first, ending with this context
+ context_file_lines: int
	// the lines in .context/bounded-context.md, so the graph node spans that file
----
+ append_context(context: BoundedContext): None
+ append_aggregate(aggregate: Aggregate): None
+ load_context_folder(folder: Path): None
	// the name is the title of .context/bounded-context.md, else the folder's name
+ load_bounded_contexts(): None
	// while has_more_bounded_context: append_context(load_next_bounded_context())
+ load_aggregates(): None
	// while has_more_aggregate: append_aggregate(load_next_aggregate())
- has_more_bounded_context(): bool
- load_next_bounded_context(): BoundedContext
- get_next_bounded_context_from_file(): BoundedContext
	// the next child context, in the map's bounded_context_type
- has_more_aggregate(): bool
- load_next_aggregate(): Aggregate
	// aggregate = get_next_aggregate_from_file()
	// -> aggregate.load_root()
- get_next_aggregate_from_file(): Aggregate
	// the next aggregate shell, in the map's aggregate_type

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
----
+ take_root(entity: Entity): None
	// the entity becomes the root, its only way in, and records this aggregate
+ load_root(): None
	// -> take_root(root)
	// -> root.load_invariant_objects()

## Integration

+ Integration()
------
+ context: str
+ aggregate: str
+ target: str
	// the class named on the arrow
+ direction: str
+ crosses: str
+ integration: str
+ pattern: str
	// Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Open Host / Published Language, or Separate Ways
+ target_parts: tuple[str, str, str]
	// the target's context, aggregate, and entity
+ target_name: str
	// the entity when the target names one, else the aggregate
----
+ lines(): list[str]
	// `- target`, then each field it has, indented: what an aggregate writes under `Integrations:`

## BuildingBlock : Node

A class Clean Engineering read, as the DDD building block it is in the graph (`graph_reading.py`). It holds the class
(`ooad_class`, through its *TacticalClass*); `get_fact` answers its own facts, then the class's, then the DDD nodes
around it, and it saves both.

+ BuildingBlock(practice: Ddd, tactical: TacticalClass, kind: str)
------
+ peer_private_operations: list[str]
+ public_derive_operations: list[str]
+ delegating_operations: list[str]
+ identity_free_loads: list[str]
	// load, get, find, or fetch with no parameters that reads ambient state such as the session or request
+ tactical_stereotype: bool
	// the class carries a DDD stereotype, or its name says its kind
+ public_operation_names: list[str]
+ lifecycle_operations: list[str]
+ drives_a_screen: bool
+ in_screen_module: bool
+ foreign_names: list[str]
	// the roots its lines name with `// foreign Name`

*DddReading* is one read of a working copy into the graph that holds the DDD practice: bounded contexts, aggregates,
and a *BuildingBlock* for each class the Clean Engineering practice it extends read.

## Entity : OoadClass

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

## ValueObject : OoadClass

+ ValueObject(name: str, sequential_order: int)
	// no write operations and no setters
	// create, clone, and mix always return a new instance
------
----
+ create(): ValueObject
+ clone(): ValueObject
+ mix(other: ValueObject): ValueObject

## Repository : OoadClass

+ Repository(name: str, sequential_order: int)
------
+ accesses: Entity | None
	// the entity in the model whose is_root is true
+ operations: list[Operation]
	// any of create, read, update, delete, and search. Not all of them
	// a search may appear more than once. Its name is search and what it searches

## DomainService : OoadClass

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

## Specification : OoadClass

## Factory : OoadClass

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
+ code_class(place: str, order: int): OoadClass
	// the class a code file writes for the card: a copy of its members, its place first in its intent

## MarkdownBoundedContextMap : BoundedContextMap, MarkdownDomainNode

The `markdown` format.

+ MarkdownBoundedContextMap()
------
+ bounded_context_type: MarkdownBoundedContext
+ aggregate_type: MarkdownAggregate
----
+ parse(text: str): MarkdownBoundedContextMap
	// fills this map and returns it
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str
	// saves the map it is given as it is
+ save(): str
	// contexts, then the event map
+ holds_classes_only: bool
	// the text named no aggregate: a plain class model
+ class_model(): CleanEngineeringModel
	// one module per aggregate, named by its place; each card a class with its place first in its intent and the arcs after the first class's
+ read_class_model(model: CleanEngineeringModel): MarkdownBoundedContextMap
	// each class's place names its context and aggregate; classes with no place gather around their roots
+ wire_events(entries: list[str]): None
	// each `Event: emitted by Producer; consumed by A, B` entry onto its producer's root
- load_bounded_context_map_content(): None
	// the lines of the file at path
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
+ aggregate_named(name: str): MarkdownAggregate

## MarkdownAggregate : Aggregate, MarkdownDomainNode

------
+ source_lines: list[str]
	// the lines under the aggregate's heading; load_root reads the root, its cards, and its arcs from them
+ cards: list[ClassCard]
+ sketch_fences: list[tuple[str, list[str]]]
	// the entity fences a sketch lists under the aggregate
+ members: list
	// the member cards, else the root's invariant objects
+ code_place: str
	// each enclosing context's label, then the aggregate's name, joined by ` · `
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
+ class_module(order: int): Module
+ take_code_integrations(): None
	// the arcs a code file kept after a class's intent, read by MarkdownIntegration
+ infer_relationships(): None

## MarkdownEntity : ClassCard, Entity

+ MarkdownEntity(name: str, sequential_order: int, member_lines: list[str] | None = None)
----
- has_more_invariant_object(): bool
- get_next_invariant_object_from_file(): MarkdownInvariantObject

## MarkdownInvariantObject : InvariantObject, MarkdownDomainNode

## MarkdownIntegration : Integration, MarkdownDomainNode

+ MarkdownIntegration.read_arcs(lines: list[str]): list[MarkdownIntegration]
	// each `- target` line opens an arc and the `key: value` lines under it fill it; markdown and code both read arcs this way
+ read_field(line: str): None

## SketchDddModel : MarkdownBoundedContextMap

The `sketch` format: the `domain driven design:` section of an integrated sketch.

----
+ parse(text: str): SketchDddModel
	// where each context starts, the prose it skips, and the event map; each context reads its own lines
	-> SketchOutline.body_for
	-> MarkdownBoundedContext.read_sketch_lines
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str

## DrawIOBoundedContextMap : MarkdownBoundedContextMap

The `drawio` format. A bounded context and an aggregate are modules and the building blocks are classes, so the map
draws and reads through Clean Engineering's draw.io diagram, its layout, and its arrow routing; DDD keeps no layout of
its own. The bounded context map is the modules view: each context a module, each aggregate a module nested in its
context's (named by its `module_path`, `Sales | custom/ShoppingCart`) listing its `drawn_members`, and each integration
a dependency arrow named by its pattern. The purpose line says which a module is: `bounded context` or `aggregate`. At
model fidelity the aggregate view is the class view of `class_model()`: each card a class with its stereotypes, kept
in the module its place names, with a dependency arrow where an operation calls into another aggregate and from the
root along each integration.

+ DrawIOBoundedContextMap()
------
+ diagram: DrawIOCleanEngineeringModel
	// composition — the Clean Engineering draw.io model the map writes and reads through
----
+ parse(text: str): DrawIOBoundedContextMap
	// a diagram with classes reads through read_class_model, taking each class's place from its module; otherwise each module is a context or an aggregate, and each labelled dependency an integration
	-> DrawIOCleanEngineeringModel.parse
	-> MarkdownBoundedContextMap.read_class_model
	-> MarkdownAggregate.take_drawn_root
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str
	// aggregates with class cards (model fidelity): the class view; otherwise the modules view
	-> MarkdownBoundedContextMap.class_model
	-> BoundedContextMap.aggregate_reached_by
	-> DrawIOCleanEngineeringModel.render

## DrawIOAggregateCell : DrawIOModule

An aggregate on the map: a module nested in its context's module that lists up to ten members, where Clean Engineering's
module lists six seam terms.

## Clean Engineering conversion

A code file is a Clean Engineering class model. `MarkdownBoundedContextMap.class_model()` writes the map as one: each aggregate a *Module* named by its place (`Context | owner · Aggregate`), each card a class of its own that keeps its stereotypes and has the place as the first line of its intent; a class belongs to one model, so code keeps its own copy of each card's members. `read_class_model(model)` reads one back. The arcs ride after the first class's intent under `Integrations:`, written by `Integration.lines` and read by `MarkdownIntegration.read_arcs`, the same as in markdown. Each class carries the relationships its properties' types name, a dependency on each class of another aggregate its operations call (named by the operation), and the root a dependency on each class an integration reaches (named by its pattern), so the draw.io class view draws them. A class whose intent names no place takes it from its module's name, which is where a diagram keeps it.

`BoundedContextMap` loads the contexts. `BoundedContext` loads its child contexts and its aggregates. `Aggregate` knows its root: the `Entity` whose `is_root` is true, and that entity records the aggregate. `Entity` loads its invariant objects; an invariant object is a property with the invariant stereotype, and it changes with the entity. A format overrides only the `has_more_*` and `get_next_*_from_file` reads for the nodes its text contains, plus `parse` and `render`.
