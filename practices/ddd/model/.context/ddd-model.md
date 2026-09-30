# Domain Driven Design Model

*BoundedContextMap* reads a path into bounded contexts and aggregates, the way the class model reads files and folders. It looks for markers that stereotype a folder, a file, or a class as a DDD building block. A top-level folder with that marker is a bounded context. A nested bounded context is a bounded context whose parent is a bounded context. Each bounded context holds one or more aggregates. When the path has no bounded context folder, the map has one bounded context and there is no folder for it; the aggregates sit in that context. A bounded context is a module. An aggregate is a module. Entity, value object, repository, domain service, domain event, specification, and factory are classes. An aggregate's root is an entity in that model with `is_root` true. Each one carries its stereotype and the constraints on its operations and relationships. Markdown continues through a class block when the file has one, and stops at the class name when the file has only the name. CodeQL continues through the stereotyped class it finds in code. Every channel uses the same walk. A channel only differs in how the next node is taken out of the path.

Callers use the base nodes. `DDDModelFactory.load` takes a file or a folder, chooses the channel map, and returns a `BoundedContextMap`.

```
bounded_context_map = DDDModelFactory.load(path)
```

# practices/ddd/model

- **Purpose:** Structure the software as DDD building blocks — bounded contexts, aggregates, and the stereotyped classes — so the model answers domain logic questions.
- **Seam (terms):** DDDModelFactory, BoundedContextMap, BoundedContext, Aggregate, Entity, InvariantObject, ValueObject, Repository, DomainService, DomainEvent, Specification, Factory
- **Dependencies (one-way):** practices/clean_engineering/model — Module, OoadClass, Property, Operation, Relationship

## DDDModelFactory

+ load(path: str): BoundedContextMap
	// path is a file, or a folder of files
	// the file type, or the files in the folder, selects the channel map
	// that map loads itself
	// the return is a BoundedContextMap

## BoundedContextMap

+ BoundedContextMap(source: BoundedContextMap)
	// source empty: the map is empty until load
	// source set: contexts, aggregates, and classes are this channel's types. A nested bounded context uses bounded_context_type
	// the new map does not keep the source's channel types
------
+ path: str
+ contexts: list[BoundedContext]
	// composition — a context has no map outside this bounded context map
	// a nested bounded context is a bounded context whose parent is a bounded context
	// no context folder: the map has one context, and that context has no folder
+ bounded_context_type: type
+ aggregate_type: type
----
+ load(path: str): BoundedContextMap
	// stores path, then runs the same walk for every channel
	self.path = path
	self.load_bounded_context_map_content()
	self.load_bounded_contexts()
+ save(): str
	// every channel writes its path with this operation
- load_bounded_context_map_content(): None
	// channel prepares its cursor over path
- load_bounded_contexts(): None
	// while has_more_bounded_context: append load_next_bounded_context()
- has_more_bounded_context(): bool
	// channel: another context folder remains in the path
	// no context folder: one context, and it has no folder
- load_next_bounded_context(): BoundedContext
	// context = get_next_bounded_context_from_file()
	// -> context.load_bounded_contexts()
	// -> context.load_aggregates()
- get_next_bounded_context_from_file(): BoundedContext
	// channel: the next context shell from the path, in bounded_context_type
	// the marker on the folder says this folder is a bounded context

## BoundedContext : Module

+ BoundedContext(source: BoundedContext)
	// copies name, owner, and order
	// a nested bounded context is a bounded context whose parent is a bounded context
	// each source child context becomes this channel's context
	// each source aggregate becomes this channel's aggregate
------
+ owner: str
	// the heading text after |
+ contexts: list[BoundedContext]
	// a nested bounded context is a bounded context whose parent is a bounded context
+ aggregates: list[Aggregate]
	// composition — an aggregate has no context outside this one
	// one or more aggregates in this context
----
+ append_context(context: BoundedContext): None
+ append_aggregate(aggregate: Aggregate): None
- load_bounded_contexts(): None
	// while has_more_bounded_context: append_context(load_next_bounded_context())
- has_more_bounded_context(): bool
	// channel: another child context folder remains
- load_next_bounded_context(): BoundedContext
	// child = get_next_bounded_context_from_file()
	// -> child.load_bounded_contexts()
	// -> child.load_aggregates()
- get_next_bounded_context_from_file(): BoundedContext
	// channel: the next child context, in the map's bounded_context_type
- load_aggregates(): None
	// while has_more_aggregate: append_aggregate(load_next_aggregate())
- has_more_aggregate(): bool
	// channel: another aggregate remains in this context
- load_next_aggregate(): Aggregate
	// aggregate = get_next_aggregate_from_file()
	// -> aggregate.load_root()
- get_next_aggregate_from_file(): Aggregate
	// channel: the next aggregate shell from the path, in the map's aggregate_type
	// the marker on the folder or file says this is an aggregate

## Aggregate : Module

+ Aggregate(source: Aggregate)
	// copies name and order
	// the root is this channel's entity, the same entity already in the model
	// each source integration becomes this channel's integration
------
+ root: Entity
	// the entity in this aggregate whose is_root is true
+ integrations: list[Integration]
	// an arrow that sits on the aggregate
----
- load_root(): None
	// root is the Entity in this aggregate whose is_root is true
	// that entity's aggregate is this aggregate
	// -> root.load_invariant_objects()
	// iterating this aggregate includes those objects. The entity does that walk

## Integration

+ Integration(source: Integration)
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

## Entity : OoadClass

+ Entity(source: Entity)
	// copies identity and is_root
	// each source invariant object becomes this channel's property
	// when is_root: copies the aggregate this root is for
------
+ identity: list[Property]
	// the properties that keep this entity the same thing
+ is_root: bool
	// true when this entity is an aggregate's root
+ aggregate: Aggregate
	// the aggregate this root is for. Set when is_root is true
+ invariant_objects: list[InvariantObject]
	// composition — properties with the invariant stereotype. These sub-objects change with this entity
+ invariant_object_type: type
----
- load_invariant_objects(): None
	// while has_more_invariant_object: append load_next_invariant_object()
- has_more_invariant_object(): bool
- load_next_invariant_object(): InvariantObject
	// object = get_next_invariant_object_from_file()
- get_next_invariant_object_from_file(): InvariantObject
	// channel: the next property with the invariant stereotype

## InvariantObject : Property

+ InvariantObject(source: InvariantObject)
	// copies name, order, type hint, description, and access
	// stereotype is invariant
------
+ stereotype: str
	// invariant

## ValueObject : OoadClass

+ ValueObject(source: ValueObject)
	// no write operations
	// no setters
	// create, clone, and mix are only state mutation ops EG always returns a new instance
------
----
+ create(): ValueObject
+ clone(): ValueObject
+ mix(other: ValueObject): ValueObject

## Repository : OoadClass

+ Repository(source: Repository)
	// a repository is a collection
	// each operation is create, read, update, delete, or search
	// a repository has any of these, not all of them
	// search may appear more than once. Its name is search and what it searches
	// copies the root this repository collects
------
+ accesses: Entity
	// the entity in the model whose is_root is true
+ operations: list[Operation]
	// any of create, read, update, delete, and search. Not all of them
	// a search may appear more than once. Its name is search and what it searches

## DomainService : OoadClass

+ DomainService(source: DomainService)
	// no state
	// an operation here is one no domain object can perform
------

## DomainEvent : Property

+ DomainEvent(source: DomainEvent)
	// copies name, order, type hint, description, and access
	// copies the producer and the subject
	// each source consumer becomes this channel's aggregate or domain service
------
+ producer: Aggregate
+ consumers: list[Aggregate | DomainService]
	// one or many
+ subject: Property
	// the state of the event. A domain event always has one

## Specification : OoadClass

## Factory : OoadClass

## MarkdownDomainNode

+ plain_name(text: str): str
	// stars and << >> removed. Context, aggregate, and class names all come through this
+ owner_from(heading: str): str
	// the text after | on a context heading
+ stereotypes(text: str): list[str]
	// the << >> tags on a class block
+ building_block_type(text: str): type
	// specification, entity, value object, repository, domain event, domain service, factory. An entity with is_root is the aggregate root
	// no tag: OoadClass

## MarkdownBoundedContextMap : BoundedContextMap

+ MarkdownBoundedContextMap(source: BoundedContextMap)
------
+ bounded_context_type: MarkdownBoundedContext
+ aggregate_type: MarkdownAggregate
----
- load_bounded_context_map_content(): None
	// cursor is the markdown headings and bullets in file
- has_more_bounded_context(): bool
- get_next_bounded_context_from_file(): MarkdownBoundedContext
+ save(): str

## MarkdownBoundedContext : BoundedContext, MarkdownDomainNode

- has_more_aggregate(): bool
- get_next_aggregate_from_file(): MarkdownAggregate

## MarkdownAggregate : Aggregate, MarkdownDomainNode

- has_more_integration(): bool
- get_next_integration_from_file(): MarkdownIntegration

## MarkdownIntegration : Integration, MarkdownDomainNode

## MarkdownProperty : Property, MarkdownDomainNode

## MarkdownOperation : Operation, MarkdownDomainNode

## MarkdownEntity : Entity, MarkdownDomainNode

- has_more_invariant_object(): bool
- get_next_invariant_object_from_file(): MarkdownInvariantObject

## MarkdownInvariantObject : InvariantObject, MarkdownDomainNode

## MarkdownValueObject : ValueObject, MarkdownDomainNode

## MarkdownRepository : Repository, MarkdownDomainNode

## MarkdownDomainService : DomainService, MarkdownDomainNode

## MarkdownDomainEvent : DomainEvent, MarkdownDomainNode

## MarkdownSpecification : Specification, MarkdownDomainNode

## MarkdownFactory : Factory, MarkdownDomainNode

## CodeqlDomainNode

+ plain_name(text: str): str
+ building_block_type(kind: str): type
	// the stereotype kind already on the type: Entity, ValueObject, Repository, DomainEvent, DomainService, Specification, Factory. is_root marks the aggregate root
	// no kind: OoadClass

## CodeqlBoundedContextMap : BoundedContextMap

+ CodeqlBoundedContextMap(source: BoundedContextMap)
------
+ bounded_context_type: CodeqlBoundedContext
+ aggregate_type: CodeqlAggregate
----
- load_bounded_context_map_content(): None
	// cursor is the code query rows in file
- has_more_bounded_context(): bool
- get_next_bounded_context_from_file(): CodeqlBoundedContext
+ save(): str

## CodeqlBoundedContext : BoundedContext, CodeqlDomainNode

- has_more_aggregate(): bool
- get_next_aggregate_from_file(): CodeqlAggregate

## CodeqlAggregate : Aggregate, CodeqlDomainNode

## CodeqlIntegration : Integration, CodeqlDomainNode

## CodeqlProperty : Property, CodeqlDomainNode

## CodeqlOperation : Operation, CodeqlDomainNode

## CodeqlEntity : Entity, CodeqlDomainNode

- get_next_property_from_file(): CodeqlProperty
	// an identity property is recorded on identity
	// is_root is true on the entity that is the aggregate root
- has_more_invariant_object(): bool
- get_next_invariant_object_from_file(): CodeqlInvariantObject

## CodeqlInvariantObject : InvariantObject, CodeqlDomainNode

## CodeqlValueObject : ValueObject, CodeqlDomainNode

## CodeqlRepository : Repository, CodeqlDomainNode

## CodeqlDomainService : DomainService, CodeqlDomainNode

## CodeqlDomainEvent : DomainEvent, CodeqlDomainNode

## CodeqlSpecification : Specification, CodeqlDomainNode

## CodeqlFactory : Factory, CodeqlDomainNode

`BoundedContextMap` loads the contexts. A nested bounded context is a bounded context whose parent is a bounded context. When the path has no context folder, the map has one context and that context has no folder. `BoundedContext` loads its child contexts and its aggregates. `Aggregate` knows its root: the `Entity` in the model whose `is_root` is true, and that entity records the aggregate. `Entity` loads its invariant objects. An invariant object is a property with the invariant stereotype, and it changes with the entity. An iteration of an aggregate includes those properties, and that walk stays on the entity. Every map implements `save(): str`. Markdown extends the base types and adds `MarkdownDomainNode`: `plain_name`, `owner_from`, `stereotypes`, and `building_block_type`. CodeQL extends the base types and adds `CodeqlDomainNode`. It reads stereotyped types from code and continues through the building block. A channel overrides only the `has_more_*` and `get_next_*_from_file` reads for the nodes its path contains. A markdown map is one file. A folder path is context folders, then nested context folders, then aggregate folders. No context folder means one context and no folder for it. CodeQL reads the same markers on the code the query sees.
