# Domain Driven Design Model

*BoundedContextMap* reads text into bounded contexts and aggregates, the way the class model reads files and folders. A nested bounded context is a bounded context whose parent is a bounded context. Each bounded context holds one or more aggregates. When the text has no bounded context, the map has one bounded context and there is no folder for it; the aggregates sit in that context. A bounded context is a module. An aggregate is a module. Entity, value object, repository, domain service, specification, and factory are classes; a domain event and an invariant object are properties. An aggregate's root is an entity with `is_root` true. Markdown continues through a class card when the file has one, and stops at the class name when the file has only the name.

The graph (*Ddd*'s reading part, *DddReading* in `practices/ddd/reading/graph_reading.py`) reads a bounded context from each folder holding `.context/bounded-context.md`, through `BoundedContext.load_context_folder`, and a building block from each class Clean Engineering read whose DDD stereotype, or, in a folder that holds a domain, whose name gives it a DDD kind. Each building block is a *BuildingBlock* node that holds the class Clean Engineering read (through a *TacticalClass*): the class's own facts are the class's, and the tactical facts DDD's rules read are the block's, worked out from the class's operations; the class itself stays Clean Engineering's node.

Callers use the base nodes. The practice's formats (`Ddd(...).formats`: sketch, markdown, drawio) each name the map class that reads and writes that format; `parse` reads text into a `BoundedContextMap` and `render` writes one back. Every format subclasses `BoundedContextMap`, which holds the map's working operations (`context_at`, `aggregate_at`, `wire_events`, `has_class_cards`) and names the context type it reads into (`bounded_context_type`); each context type names the aggregate type it opens (`aggregate_type`), and a nested context is of its parent's own type. Every format reads into the base nodes and writes from them: an aggregate holds its building blocks as the cards they are (*DomainClass*) and answers its root card, its repository, and its members whichever format it was read from, so the markdown format writes a map read from a sketch or a drawing, and the sketch writes one read from markdown. Each text format keeps only its notation: markdown's *ContextSection*, *AggregateSection* and *CardSection*, the sketch's *SketchedContext*, *SketchedAggregate* and *SketchedCard*, and *AggregateLines*, an aggregate's own lines, which both write (cdr 0004). The draw.io map is itself Clean Engineering's draw.io diagram (`DrawIOBoundedContextMap(BoundedContextMap, DrawIOCleanEngineeringModel)`): it draws its contexts and aggregates as its own modules and renders itself; reading a drawing builds each cell as the cell type its style names (`kind=boundedContext;`, `kind=aggregate;`), and each cell reads itself into the map. The python and typescript formats are Clean Engineering's class models: the map writes itself into one as that format's own classes (`write_classes(model)`), so the format renders itself with no second copy, and reads one back (`read_class_model(model)`), each aggregate taking the classes its place names as the cards they are, with their own members; a markdown text with no aggregate is a plain class model, which `Ddd` hands to its Clean Engineering companion's own adapter. A card's stereotypes are the class's `stereotypes`, which the code channels write as decorators (`@aggregate_root`, `@AggregateRoot()`) and read back: a decorator with no arguments, or a `<<Mark>>` on the first line of the doc comment, is a stereotype, so Clean Engineering keeps no list of DDD's words. `stereotypes.KIND_OF_STEREOTYPE` is the one table of DDD's own words from that list — aggregate root, entity, value object, repository, domain service or service, domain event, specification, and factory — and the building block each names; a class marked `system` is another system's. `DomainClass.named` makes the card of the building block they name, the graph's building blocks read the same table through *TacticalClass*, and the tactical rules check `BUILDING_BLOCK_KINDS`. The DDD practice registers itself on `DomainNode`, the base of every DDD node, so the model never imports its practice. Where a class lives is its `module_path`, a Clean Engineering field (`["Customer | custom", "Customer Profile"]`), and an aggregate's integrations are dependencies of its root that carry the arc's fields as details (`Integration.as_dependency`, `Integration.kept_by`); the code formats write both in the class's doc comment and read them back.

```
bounded_context_map = MarkdownBoundedContextMap().parse(text)
```

# practices/ddd/model

- **Purpose:** Structure the software as DDD building blocks — bounded contexts, aggregates, and the stereotyped classes — so the model answers domain logic questions.
- **Seam (terms):** BoundedContextMap, BoundedContext, Aggregate, Integration, Entity, InvariantObject, ValueObject, Repository, DomainService, DomainEvent, Specification, Factory, DomainClass, MarkdownBoundedContextMap, SketchDddModel, DrawIOBoundedContextMap, AggregateLines
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
+ notes: list[str]
	// why the context exists, as a sketch or a document notes it above its aggregates
+ module_name: str
+ module_notes: list[str]
	// the Clean Engineering module the context is built as, with its seam and constraint
+ group_notes: dict[str, list[str]]
	// the notes under each heading that groups aggregates
----
+ append_context(context: BoundedContext): None
+ append_aggregate(aggregate: Aggregate): None
+ aggregate_named(name: str): Aggregate
	// this context's aggregate called name, opened the first time in this context's aggregate_type
+ load_context_folder(folder: Path): None
	// the name is the title of .context/bounded-context.md, else the folder's name; its mappings are that file's `Local → Remote` lines
+ mappings: list[ContextMapping]

## Aggregate : Module

+ Aggregate(name: str, sequential_order: int, graph: Graph | None = None)
------
+ root: Entity | None
	// the entity in this aggregate whose is_root is true
+ integrations: list[Integration]
	// an arrow that sits on the aggregate
+ group: str | None
	// the heading a sketch or a document groups the aggregate under
+ consumed_events: list[str]
	// the events it reacts to, which another aggregate's root emits
+ events: list[DomainEvent]
	// the domain events the root emits
+ members: list
	// what the root holds: its invariant objects; at model fidelity, the member cards
+ classes: list[DomainClass]
	// its building blocks, as their cards: the aggregate is a Module, and they are its classes
+ root_card: DomainClass | None
	// the card marked <<Aggregate Root>>, or made the root; none at bounded-context fidelity
+ repository: DomainClass | None
+ member_cards: list[DomainClass]
	// the entities and values the root composes
+ ordered_cards: list[DomainClass]
	// root, then its repository, then members — the one card order every format uses
+ drawn_members: list[str]
	// the members a map lists under the aggregate: what the root holds, without the root, prose, or operations
+ place_labels: list[str]
	// each enclosing context's label, then the aggregate's name: the module path of each class it writes
+ code_place: str
	// the place labels as one module name, joined by ` · ` (`joined_module_path`)
+ module_path: str
	// its context's module_path, then its name: `Sales | custom/ShoppingCart`
----
+ take_root(entity: Entity): None
	// the entity becomes the root, its only way in, and records this aggregate
+ open_root(name: str, members: list[str], emitted: list[str]): None
	// the root a document's or a drawing's lines name, with its members, operations, and the events it emits
+ take_drawn_root(members: list[str]): None
	// the root a map drawing shows: the aggregate's own entity, holding the members listed under it
+ take_root_card(): None
	// the <<Aggregate Root>> card becomes the root; each repository card collects it
+ take_class(oclass: OoadClass): None
	// a class read from a class model, held as the card it is; each dependency that keeps an arc is an integration
	-> DomainClass.from_code
	-> Integration.kept_by
+ read_arrows_across(homes: dict[str, Aggregate]): None
	// each labelled arrow a class drawing shows to another aggregate's class: a call by the operation it names, else an integration
+ take_root_from_classes(): None
	// once its cards are read: the relationships their types name, then the root card, else a root named after it
+ write_classes_into(module: Module): None
	// each card as module's own class, kept in the aggregate's place; the root depends on each class an integration reaches
	-> DomainClass.write_into
	-> Integration.as_dependency
+ take_words_from(earlier: Aggregate): None
	// keeps its own words and takes earlier's where it has none: sentence, group, consumed events, its root's and its cards'
+ load_root(): None
	// -> take_root(root)
	// -> root.load_invariant_objects()

## Integration

+ Integration()
+ Integration.from_aggregate(target: Aggregate): Integration
	// an arc to target, named by its context and its own name
+ Integration.read_arcs(lines: list[str]): list[Integration]
	// each `- target` line opens an arc and the `key: value` lines under it fill it
+ Integration.targeting(text: str): Integration
	// the arc to `→ Context · Aggregate · Entity (by Identity)`, or to one class alone: the one reading of the `·` text
+ Integration.kept_by(dependency: Relationship): Integration | None
	// the arc a class model's dependency keeps, when its details name a part of the arc's target
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
+ target: str
	// the target as the arc's line writes it: the one writing of the `·` text
----
+ as_dependency(): Relationship
	// the arc as a class model keeps it on the root: a dependency on target_name, labelled by its pattern, with each
	// part of its target and each of its other fields as a detail
+ lines(): list[str]
	// `- target`, then each field it has, indented: what every text format writes under `Integrations:`
+ read_field(line: str): None

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
root associates with every other root its lines name with `// foreign Name`. Each *ContextMapping* a bounded context's
file lists sits under that context and is linked to the aggregates its sides name.

## ContextMapping : DomainNode

How one bounded context maps to another: a `Local → Remote` line its `.context/bounded-context.md` lists, on the line it
sits on. *DddReading* adds each under its context (`mappedTo`) and links it to the aggregates its sides name (`local`,
`remote`), whether or not a pattern is applied; the LERN overlay reads none of the context's file.

+ ContextMapping(local: str, remote: str, line: int)
------
+ local, remote: str
	// saved facts: each side as the line writes it, alone or after its context (`Sales · cart`)
+ aggregate_names: dict[str, str]
	// the aggregate each side names: the last `·` part

## DomainClass : OoadClass

The base of every DDD class (`building_blocks.py`): a Clean Engineering class that is one of the domain's building
blocks, made with its name, its order, and its intent, and the card every format writes for it. A class whose
stereotypes name no building block is a plain *DomainClass*. Its members are read and written in Clean Engineering's one
class-card notation (*ClassCard* and *SketchFence*), with DDD's own options: no constructor line, the stereotypes in
their order, a repository drawn inside its root's card, and the invariants it lists.

+ DomainClass(name: str, sequential_order: int, intent: str = "")
+ DomainClass.named(name: str, stereotypes: list[str]): DomainClass
	// the empty card of the building block its stereotypes name: specification, value object, repository, domain
	// service (or service), factory, entity, or aggregate root (an entity); a plain DomainClass for none
+ DomainClass.from_heading(heading: str): DomainClass
+ DomainClass.from_code(oclass: OoadClass): DomainClass
	// the card a class read from code or a class drawing is, holding its own members and intent, without its constructor
------
+ tactical: TacticalClass
	// made once with the class: the one reading of which building block its stereotypes make it
+ invariants: list[str]
+ drawn_in_root: bool
	// a repository written and drawn inside its root's card
+ is_root: bool
	// marked <<Aggregate Root>>, or made its aggregate's root
+ is_repository: bool
+ heading: str
+ plain_properties: list[Property]
	// what the class holds, not its events or invariant objects
----
+ take_words_from(earlier: DomainClass): None
	// keeps its own words and takes earlier's where it has none: invariants, intent, member notes, each operation's calls
+ write_into(module: Module, place: list[str]): OoadClass
	// adds the card to module as that format's own class: its stereotypes, its intent, its members, and place as its module_path

## Entity : DomainClass

+ Entity(name: str, sequential_order: int, member_lines: list[str] | None = None)
------
+ identity: list[Property]
	// the properties that keep this entity the same thing
+ aggregate: Aggregate | None
	// the aggregate this root is for. Set when is_root is true
+ invariant_objects: list[InvariantObject]
	// composition — properties with the invariant stereotype. These sub-objects change with this entity
----
+ load_invariant_objects(): None
	// each member line a document named under the root, once, as one of its invariant objects

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

## MarkdownBoundedContextMap : BoundedContextMap

The `markdown` format.

+ MarkdownBoundedContextMap()
----
+ parse(text: str): MarkdownBoundedContextMap
	// fills this map and returns it
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str
	// writes the map it is given: each context's own lines, then the event map
+ save(): str
	// this map, as render writes it
+ holds_classes_only: bool
	// the text named no aggregate: a plain class model
- _read_contexts(): None
	// each `## Context | owner` heading in turn; the context reads the lines under it, then the event map is wired
	-> ContextSection.read

## ContextSection

A context's `## Context | owner` section in markdown (`markdown/nodes.py`): what it is, its `> ` notes, its module, the
`*Group*` headings that group its aggregates with their notes, and each aggregate's section. It reads into and writes
from the base *BoundedContext*, so a context read from any format writes as markdown.

+ ContextSection(context: BoundedContext)
----
+ read(lines: list[str]): None
	// its own lines: notes, module, group headings, and each aggregate, which reads its own section
	-> AggregateSection.read
+ lines(): list[str]

## AggregateSection

+ AggregateSection(aggregate: Aggregate)
----
+ read(lines: list[str]): None
	// each `####` card section, then the aggregate's own lines
	-> CardSection.read
	-> AggregateLines.read
+ lines(): list[str]
	// what it keeps true, its cards in ordered_cards order or its root line and members, then its arcs and events

## CardSection

A building block's `####` card in markdown (`markdown/class_cards.py`).

+ CardSection(card: DomainClass)
+ CardSection.read(section: list[str]): list[DomainClass]
	// the card, then the repository a `**Name** «Repository»` line writes inside it
----
+ read_body(body: list[str]): None
	// its members in the class-card notation, then the invariants its **Invariants** lists
+ lines(): list[str]

## AggregateLines

An aggregate's own lines, as markdown writes them under its `###` heading and a sketch inside its fence
(`aggregate_lines.py`): what it keeps true, its root line and members, its arcs under `Integrations:`, and its events.

+ AggregateLines(aggregate: Aggregate)
----
+ read(lines: list[str]): None
	// then the root card, when it holds cards, becomes the root
	-> Aggregate.open_root
	-> Aggregate.take_root_card
+ integration_lines(): list[str]
	// the arcs under `Integrations:`, the root's events under `emits events:`, the events it reacts to under `consumes events:`

## SketchDddModel : BoundedContextMap

The `sketch` format: the `domain driven design:` section of an integrated sketch.

----
+ parse(text: str): SketchDddModel
	// where each context starts, the prose it skips, and the event map; each context reads its own lines
	-> SketchOutline.body_for
	-> SketchBoundedContext.read_sketch_lines
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str
	-> SketchedContext.lines

## SketchBoundedContext : BoundedContext

A context read from a sketch (`sketch/sketch_nodes.py`); its aggregate_type is *SketchAggregate*.

----
+ read_sketch_lines(lines: list[str]): None
	// its lines of a sketch: holders, entities, notes, and each aggregate's fences
	-> SketchAggregate.take_sketch_line
	-> SketchAggregate.load_sketch

## SketchAggregate : Aggregate

------
+ sketch_fences: list[tuple[str, list[str]]]
	// the entity fences a sketch lists under the aggregate
----
+ take_sketch_line(raw: str): None
+ load_sketch(): None
	-> SketchedCard.read
	-> AggregateLines.read

## SketchedContext

A context of any format as a sketch writes it: its heading, notes, module, then each aggregate under its holder.

+ SketchedContext(context: BoundedContext)
----
+ lines(): list[str]
	-> SketchedAggregate.lines

## SketchedAggregate

+ SketchedAggregate(aggregate: Aggregate)
------
+ holder: str | None
	// its own name when its root card is named apart, else its group
----
+ lines(): list[str]

## SketchedCard

A building block in a sketch's entity fence: its members, its operations with their calls, then its invariants.

+ SketchedCard(card: DomainClass)
+ SketchedCard.read(heading: str, lines: list[str]): list[DomainClass]
	// the card, then the repository the fence's `repo:` names; a *SketchFence* reads the fence onto the card
----
+ lines(): list[str]

## DrawnBoundedContextMap : BoundedContextMap

The map drawn as Clean Engineering modules (`drawn/drawn_map.py`), shared by the draw.io and whiteboard formats. A bounded
context and an aggregate are modules and the building blocks are classes, so the map is Clean Engineering's drawing,
with its layout and its arrow routing; DDD keeps no layout of its own. The bounded context map is the modules view: each
context a module, each aggregate a module nested in its context's (named by its `module_path`, `Sales |
custom/ShoppingCart`) listing its `drawn_members`, and each integration a dependency arrow named by its pattern. At model
fidelity the aggregate view is the class view: the map writes its cards into its own modules (`write_classes`), each
card a class with its stereotypes, kept in the module its place names, with a dependency arrow where an operation calls
into another aggregate and from the root along each integration.

------
+ context_cell_type: type[ContextCell]
+ aggregate_cell_type: type[AggregateCell]
	// the format's own cell types, each in front of the format's module class
----
+ draw(source: BoundedContextMap): None
	// aggregates with class cards (model fidelity): the class view; otherwise the modules view, drawn as its own modules
	-> BoundedContextMap.write_classes
	-> BoundedContextMap.aggregate_reached_by
+ read_drawing(): DrawnBoundedContextMap
	// a drawing with classes reads through read_class_model, taking each class's place from its module; otherwise each cell reads itself into the map, then each draws its integrations
	-> BoundedContextMap.read_class_model
	-> MapCell.read_into
	-> MapCell.read_integrations_into

## MapCell

A module on a drawn map that reads itself back into the map. *ContextCell* is a bounded context: a module named by the
context's `module_path`, whose purpose line is `bounded context`, read back as the context its path names.
*AggregateCell* is an aggregate: a module nested in its context's module, whose purpose line is `aggregate`, that lists up
to ten of the aggregate's `drawn_members`, where Clean Engineering's module lists six seam terms; it reads itself back as
the aggregate its path names, with the root its members show, and each arrow it draws as an integration
(`Integration.from_aggregate`).

----
+ read_into(drawn: BoundedContextMap): None
+ read_integrations_into(drawn: BoundedContextMap): None

## DrawIOBoundedContextMap : DrawnBoundedContextMap, DrawIOCleanEngineeringModel

The `drawio` format. Its cells are *DrawIOContextCell* (*ContextCell*, *DrawIOModule*) and *DrawIOAggregateCell*
(*AggregateCell*, *DrawIOModule*); each cell's style names its kind (`kind=boundedContext;`, `kind=aggregate;`), which
Clean Engineering's reader builds back into the cell type through `module_cell_types`.

----
+ parse(text: str): DrawIOBoundedContextMap
	-> DrawIOCleanEngineeringModel.parse
	-> DrawnBoundedContextMap.read_drawing
+ render(canonical: BoundedContextMap | None = None, previous: str | None = None): str
	-> DrawnBoundedContextMap.draw
	-> DrawIOCleanEngineeringModel.render

## WhiteboardBoundedContextMap : DrawnBoundedContextMap, WhiteboardCleanEngineeringModel

The `whiteboard` format, the same map as a Clean Engineering board: *WhiteboardContextCell* a section (`context.`),
*WhiteboardAggregateCell* a module nested in it (`aggregate.`).

## Clean Engineering conversion

A code file is a Clean Engineering class model. `BoundedContextMap.write_classes(model)` writes the map into the format's own model: each aggregate a module of that format named by its place (`Context | owner · Aggregate`), each card a class of that format that keeps its stereotypes and has the aggregate's place labels as its `module_path`. The format renders that model as itself, so the map is copied once, into the format, as every format copies the model it writes; a code class writes its module path as its doc comment's `Module:` line, and the dependencies that carry details as `---<<pattern>>--> Target` lines with their details under them (Clean Engineering's `DocComment`). `read_class_model(model)` reads one back: each aggregate takes its classes as the cards they are, holding the classes' own members and intent, and the arcs their dependencies keep as its integrations. Each class carries the relationships its properties' types name, a dependency on each class of another aggregate its operations call (named by the operation), and the root a dependency on each class an integration reaches (the arc whole, `Integration.as_dependency`), so the draw.io class view draws them. A class with no module path takes its place from its module's name, which is where a diagram keeps it.

Each format's `parse` reads its contexts into the map, and each context reads its own lines into its aggregates. `Aggregate` knows its root: the `Entity` whose `is_root` is true, and that entity records the aggregate. `Entity` loads its invariant objects; an invariant object is a property with the invariant stereotype, and it changes with the entity. A format's entity reads its own invariant objects (`load_invariant_objects`).
