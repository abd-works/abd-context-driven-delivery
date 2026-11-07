# Domain Driven Design Model

*BoundedContextMap* reads text into bounded contexts and aggregates, the way the class model reads files and folders. A nested bounded context is a bounded context whose parent is a bounded context. Each bounded context holds one or more aggregates. When the text has no bounded context, the map has one bounded context and there is no folder for it; the aggregates sit in that context. A bounded context is a module. An aggregate is a module. Entity, value object, repository, domain service, specification, and factory are classes; a domain event and an invariant object are properties. An aggregate's root is an entity with `is_root` true. Markdown continues through a class card when the file has one, and stops at the class name when the file has only the name.

The graph (*Ddd*'s `read_working_copy`, with its readers in `practices/ddd/model/graph_reading.py`) reads a bounded context from each folder holding `.context/bounded-context.md`, through `BoundedContext.load_context_folder`, and a building block from each class Clean Engineering read whose stereotypes or name give it a DDD kind. The building block's node holds the class's own facts and the tactical facts `tactical_facts(parsed, kind)` reads from the parsed class; the class itself stays Clean Engineering's node.

Callers use the base nodes. The practice's formats (`Ddd(...).formats`: sketch, markdown, drawio) each name the map class that reads and writes that format; `parse` reads text into a `BoundedContextMap` and `render` writes one back. The python and typescript formats are Clean Engineering's class models: `Ddd` converts the map with `to_clean_engineering` and back with `from_clean_engineering`. A card's stereotypes are the class's `stereotypes`, which the code channels write as decorators (`@aggregate_root`, `@AggregateRoot()`) and read back: a decorator with no arguments, or a `<<Mark>>` on the first line of the doc comment, is a stereotype, so Clean Engineering keeps no list of DDD's words. `tactical_stereotypes` keeps DDD's own words from that list — aggregate root, entity, value object, repository, domain service or service, domain event, specification, factory, and system — and `building_block_type` reads a card's class from them. Where the class lives rides in its intent's first line (`Customer · Customer Profile`).

```
bounded_context_map = MarkdownBoundedContextMap().parse(text)
```

# practices/ddd/model

- **Purpose:** Structure the software as DDD building blocks — bounded contexts, aggregates, and the stereotyped classes — so the model answers domain logic questions.
- **Seam (terms):** BoundedContextMap, BoundedContext, Aggregate, Integration, Entity, InvariantObject, ValueObject, Repository, DomainService, DomainEvent, Specification, Factory, MarkdownBoundedContextMap, SketchDddModel, DrawIOBoundedContextMap, ClassCard
- **Dependencies (one-way):** practices/clean_engineering/model — Module, OoadClass, Property, Operation, CleanEngineeringModel; harness/graph — Graph, ModelChildren; actions/sketch — SketchOutline, SketchLens

*Module*, *OoadClass*, *Property*, *Operation*, and *CleanEngineeringModel* belong to Clean Engineering; this model only extends or uses them.

## BoundedContextMap

+ BoundedContextMap(source: BoundedContextMap | None = None)
	// source empty: the map is empty until load
	// source set: each source context becomes this format's context
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
----
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

+ BoundedContext(name: str, sequential_order: int, source: BoundedContext | None = None, graph: Graph | None = None)
	// copies name, owner, and order
	// a nested bounded context is a bounded context whose parent is a bounded context
------
+ owner: str
	// the heading text after |
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

+ Aggregate(name: str, sequential_order: int, source: Aggregate | None = None)
	// copies name and order
	// each source integration becomes this format's integration
------
+ root: Entity | None
	// the entity in this aggregate whose is_root is true
+ integrations: list[Integration]
	// an arrow that sits on the aggregate
+ events: list[DomainEvent]
	// the domain events the root emits
----
+ take_root(entity: Entity): None
	// the entity becomes the root, its only way in, and records this aggregate
+ load_root(): None
	// -> take_root(root)
	// -> root.load_invariant_objects()

## Integration

+ Integration(source: Integration | None = None)
	// copies the target and the arc
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

`tactical_facts(parsed: OoadClass, kind: str): dict` — the facts DDD's tactical rules read about a parsed class seen as a building block of kind, recorded on the building block's graph node:

------
+ peer_private_operations: list[str]
+ public_derive_operations: list[str]
+ delegating_operations: list[str]
+ identity_free_loads: list[str]
	// load, get, find, or fetch with no parameters that reads ambient state such as the session or request
+ tactical_stereotype: bool
	// the class carries a DDD stereotype, or its name says its kind

## Entity : OoadClass

+ Entity(name: str, sequential_order: int, source: Entity | None = None)
	// copies identity, is_root, and the aggregate
	// each source invariant object becomes an invariant object here
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

+ InvariantObject(name: str, sequential_order: int, source: InvariantObject | None = None)
	// copies name, order, type hint, description, and access
------
+ stereotype: str
	// invariant

## ValueObject : OoadClass

+ ValueObject(name: str, sequential_order: int, source: ValueObject | None = None)
	// no write operations and no setters
	// create, clone, and mix always return a new instance
------
----
+ create(): ValueObject
+ clone(): ValueObject
+ mix(other: ValueObject): ValueObject

## Repository : OoadClass

+ Repository(name: str, sequential_order: int, source: Repository | None = None)
	// a repository is a collection; it copies the root it collects
------
+ accesses: Entity | None
	// the entity in the model whose is_root is true
+ operations: list[Operation]
	// any of create, read, update, delete, and search. Not all of them
	// a search may appear more than once. Its name is search and what it searches

## DomainService : OoadClass

+ DomainService(name: str, sequential_order: int, source: DomainService | None = None)
	// no state
	// an operation here is one no domain object can perform

## DomainEvent : Property

+ DomainEvent(name: str, sequential_order: int, source: DomainEvent | None = None)
	// copies name, order, type hint, description, access, producer, consumers, and subject
------
+ producer: Aggregate | None
+ consumers: list[Aggregate | DomainService]
	// one or many
+ subject: Property
	// the state of the event. A domain event always has one

## Specification : OoadClass

## Factory : OoadClass

`building_block_type(stereotypes)` names the class a card with those stereotypes is read into: specification, value object, repository, domain service (or service), factory, entity, or aggregate root (an entity); a card with none is a plain *OoadClass*.

## MarkdownDomainNode

+ plain_name(text: str): str
	// ** and backticks removed, and the text before |. Context, aggregate, and class names all come through this
+ owner_from(heading: str): str
	// the text after | on a context heading

## ClassCard

One `####` card in markdown: a classified class with its stereotypes.

+ ClassCard(node: OoadClass, stereotypes: list[str])
+ ClassCard.from_heading(heading: str): ClassCard
+ ClassCard.from_name(name: str, stereotypes: list[str]): ClassCard
	// the class is typed by building_block_type
------
+ node: OoadClass
+ stereotypes: list[str]
+ invariants: list[str]
+ is_root: bool
+ is_repository: bool
+ heading: str
----
+ add_member(line: str, as_operation: bool): Property | Operation | None
	// one `+ name: Type` or `+ name(parameters): Type` line onto the card's class
+ lines(): list[str]
+ property_lines(): list[str]
+ operation_lines(): list[str]
+ sketch_lines(): list[str]

## MarkdownBoundedContextMap : BoundedContextMap, MarkdownDomainNode

The `markdown` format.

+ MarkdownBoundedContextMap(source: BoundedContextMap | None = None)
------
+ bounded_context_type: MarkdownBoundedContext
+ aggregate_type: MarkdownAggregate
----
+ parse(text: str): MarkdownBoundedContextMap
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str
+ save(): str
	// contexts, then the event map
+ wire_events(entries: list[str]): None
	// each `Event: emitted by Producer; consumed by A, B` entry onto its producer's root
- load_bounded_context_map_content(): None
	// the lines of the file at path
- has_more_bounded_context(): bool
- get_next_bounded_context_from_file(): MarkdownBoundedContext
	// the next `## Context | owner` heading

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
+ lines(): list[str]
+ read_note(line: str, group: str | None): None
	// to the group it sits under, else the module, else the context

## MarkdownAggregate : Aggregate, MarkdownDomainNode

------
+ source_lines: list[str]
	// the lines under the aggregate's heading; load_root reads the root, its cards, and its arcs from them
+ cards: list[ClassCard]
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

## MarkdownEntity : Entity, MarkdownDomainNode

+ MarkdownEntity(name: str, sequential_order: int, member_lines: list[str] | None = None)
----
- has_more_invariant_object(): bool
- get_next_invariant_object_from_file(): MarkdownInvariantObject

## MarkdownInvariantObject : InvariantObject, MarkdownDomainNode

## MarkdownIntegration : Integration, MarkdownDomainNode

## SketchDddModel : MarkdownBoundedContextMap

The `sketch` format: the `domain driven design:` section of an integrated sketch.

----
+ parse(text: str): SketchDddModel
	-> SketchOutline.body_for
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str

## DrawIOBoundedContextMap : MarkdownBoundedContextMap

The `drawio` format.

----
+ parse(text: str): DrawIOBoundedContextMap
	// the aggregate view page reads through DrawIOAggregateModel; any other page is the context map
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str
	// aggregates with class cards (model fidelity): the aggregate view; otherwise the context map
	-> DrawIOAggregateModel.render

## DrawIOAggregateModel

Writes and reads the aggregate view: each context a dashed box, its aggregates inside, and each aggregate's class cards.

+ DrawIOAggregateModel()
----
+ render(model: BoundedContextMap): str
+ contexts_in(diagram: DrawnDiagram): list[MarkdownBoundedContext]

## Clean Engineering conversion

`to_clean_engineering(bounded_context_map)` makes one *Module* per aggregate, each class keeping its stereotypes and place (`Context · Aggregate`) in its intent. `from_clean_engineering(model)` rebuilds contexts and aggregates from each class's place, or groups classes around their roots. Both live in `clean_engineering_bridge.py`.

`BoundedContextMap` loads the contexts. `BoundedContext` loads its child contexts and its aggregates. `Aggregate` knows its root: the `Entity` whose `is_root` is true, and that entity records the aggregate. `Entity` loads its invariant objects; an invariant object is a property with the invariant stereotype, and it changes with the entity. A format overrides only the `has_more_*` and `get_next_*_from_file` reads for the nodes its text contains, plus `parse` and `render`.
