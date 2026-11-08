# Graph

`Graph` reads a working copy into the practices it holds: the `PracticeGuidance` objects it is given, which a session gives from its own practices and a graph no session holds makes with `PracticeCatalogue.create_all`. Each practice holds the graph (`practice.graph`), and the graph keeps every practice's nodes and edges itself, indexed by the practice. The graph names no practice: each practice's `PracticeGuidance` class says what the graph reads from it, and each pattern is a *PracticeGuidance* that makes its `GraphOverlay` once and keeps it as `graph_overlay`; the graph holds one *PatternOverlays* (`graph.applied_patterns`), which makes each pattern its overlays name once, when its overlays are set, so the practices depend on the graph and never the other way round.

A practice reader parses its files with the practice's own model and adds each parsed object (a class, an operation, a story, a spec's observation) to its practice in the graph as the node itself (`practice.in_graph.add(node, ...)`), so a rule reads its measurements from the same object the explorer shows. A node with no parsed object behind it, such as a story's example or a LERN tier file, is a plain `Node` made with `practice.in_graph.add_named`. Edges are recorded with `Graph.link`, on the parent's practice; an edge's place under its parent in the explorer tree comes from `EDGE_ORDER`.

A load runs in this order (`Graph._read_working_copy` in `graph.py`): each practice `read`s, in the order its `reads_after` needs; then each practice `link`s its nodes to other practices' nodes; then each applied overlay `read`s; then each practice's `in_graph.check()` runs its checks and records each finding as a `Violation` on its node; then each practice `rebuild_tree`s. `save_json` writes the result to `{folder}/.context/graph.json`, and a later `load_working_copy` reads that file back instead of parsing when it is still current.

A node's id is `{practice}:{type}:{file or folder}:{name}`, with the owning class or operation added when the name alone is not unique. The practice sections below give each one.

---

## Graph

The toolset the graph tools run on. A session holds one (`Session.graph`), with the session's practices in it; each project's cdd runtime also holds one for calls that work in no session. Annotated `@language_adapter(language="typescript")`, so the explorer app calls the same operations through the generated `GraphClientGenerated`.

+ practices: dict[str, PracticeGuidance]
	// the practices the last load reads, by key
+ every_practice: dict[str, PracticeGuidance]
	// every practice the graph holds, read or not
+ filter: Filter
+ overlays: list[str]
	// pattern overlay roots, each a folder holding practices/; setting them holds the pattern each one is and asks it for its GraphOverlay
+ pattern_overlays: list[GraphOverlay]
+ folder: str
	// the loaded folder; graph.json lives in its .context
- _held: dict[str, PracticeGuidance]
- _source_roots: dict[PracticeGuidance, Path]
- _roots: dict[PracticeGuidance, Node]
- _by_id: dict[PracticeGuidance, dict[str, Node]]
- _nodes: dict[PracticeGuidance, dict[str, list[Node]]]
	// by node type
- _node_types: dict[PracticeGuidance, set[str]]
- _edges: dict[PracticeGuidance, dict[str, list[Edge]]]
	// by kind; an edge is kept on its parent's practice, once for a parent and child of one kind
- _edge_types: dict[PracticeGuidance, dict[str, EdgeType]]
- _scope: list[Path] | None
	// the edited files a load_files reads; None when the whole folder loads
----
+ Graph(practices=None)
	// holds practices, each of which then holds this graph; with none, a set of its own from PracticeCatalogue.create_all(fidelity=None)
+ for_call(call): Graph
	// the call's session's graph, so every graph tool a call in that session makes runs on it
+ open(folder): None
	// every practice rooted on folder, holding its root node alone
+ practice(key): PracticeGuidance
	// the held practice of that key, opened in this graph the first time; never made here
+ PracticeNodes.root: Node
	// type Practice, id {practice}:Practice:.:{practice}. Facts about the practice as a whole live here
+ PracticeNodes.source_root: str
+ PracticeNodes.nodes(type=None): list[Node]
+ PracticeNodes.node_types: set[str]
+ PracticeNodes.edges(kind=None): list[Edge]
+ PracticeNodes.edge_types: dict[str, EdgeType]
+ node(node_id): Node | None
+ PracticeNodes.holds(node_id): bool
+ PracticeNodes.schema: PracticeSchema
	// the practice's schema with the graph's overlays applied
+ PracticeNodes.schema_with(overlays): PracticeSchema
	// made the first time and kept here
+ PracticeNodes.checks: dict
	// graph.applied_patterns.checks_of(practice): the practice's graph_checks, then each applied overlay's rules_for(practice)
+ PracticeNodes.rule_labels: list[str]
	// practice.NodeType.slug, with the owning pattern in front
+ PracticeNodes.add(node, node_id, file, start_line, end_line): Node
	// the node practice already calls node_id when there is one; else release it from any graph it was held in, place it, hold it
+ PracticeNodes.add_named(type, node_id, name, source): Node
+ PracticeNodes.hold(node): None
	// keep the node among its practice's nodes, by type and id
+ link(kind, parent, child, display="direct"): None
	// -> record(EdgeType.from_kind(kind, display), parent, child)
+ record(edge_type, parent, child): None
	// on the parent's practice
+ PracticeNodes.drop_edges(dropped): list[Edge]
+ PracticeNodes.unused_node_id(type, name): str
	// practice:type:name, numbered from 2 when taken
+ edges_from(kind, parent): list[Edge]
+ direct_parent(child): Node | None
+ PracticeNodes.rebuild_tree(): None
	// clear every node's children, then the practice's root populates
+ restored_from(saved: SavedGraph): None
	// the saved nodes back as plain Nodes at their saved lines, then the edges and violations
+ load_working_copy(folder, practices, database=None, overlays=None, force=False): GraphLoaded
	// @mcp. reuse the saved graph when it holds every requested practice on the same roots and overlays; no date is compared
	// else -> _build_working_copy, -> save_json
+ load_files(folder, practices, files, overlays=None): GraphLoaded
	// @mcp, /load-files. build from only the edited files; never reads or writes the saved graph
+ refresh(paths): GraphLoaded
	// @mcp. drop the nodes read from exactly paths, read them as they are now, link them, run every rule again
+ save_json(): GraphSaved
	// @mcp. merge into .context/graph.json through SavedGraphFile; practices already saved and not loaded now stay
+ saved(files=None): SavedGraph
	// taken under the lock a load, refresh, or write holds
	// this graph alone, without merging; with files, only the nodes read from them
+ loaded_folder: Path | None
	// where practices and overlays read from
	// the practice of that class the last load reads; an overlay asks for the practices it adds to this way
	// the applied overlays' pattern names
+ sync_schema_edges(): None
	// -> the graph's one SchemaEdges.sync(), unless a working copy loaded this graph (syncs_schema_edges is false) or a batch holds it
+ schema_sync_held(): contextmanager
	// hold schema-edge rebuilds until a batch of links is done, then rebuild once
+ set_overlays(overlays): AppliedOverlays
	// @mcp. reload the open folder with these overlays
+ overlay_of(folder): Overlay
	// @mcp. raises GraphFailure when the folder and its parents hold no practices/
+ practice_names(): list[str]
	// @mcp. the key of every practice the graph holds
+ inventory(): Inventory
	// @mcp
+ filter_choices(practices, node_types, practices_before): Filter
	// @mcp. a new Filter; clears the graph's own
+ source(node_id): NodeSource | None
	// @mcp
+ return_nodes(filter=None): list[FilteredNode]
	// @mcp, read-graph skill. keys: practice(s), type(s), name, rules, relationships, violations, path(s)
	// -> filter.narrowed_by(filter), walks each practice's root
+ source_files(root, suffixes): list[Path]
	// the edited files during a load_files, else every scanned file
+ edited_files(): list[Path] | None
+ scoped(found): list[Path]
+ scope_folders(): list[Path] | None
+ report_progress(message): None
	// -> harness.agent_tools.progress.report_progress

## Inventory

+ practices: dict[str, PracticeInventory]
+ overlays: list[str]
+ available_overlays: list[str]
	// each folder under cdd_guidance/patterns that holds practices/

## AppliedOverlays

Extends `Inventory`.

+ message: str

## PracticeInventory

One loaded practice as the explorer's inventory shows it, read from the graph that holds it (explorer.py).

+ node_counts: dict[str, int]
+ edge_count: int
+ node_types: list[str]
+ edge_types: list[str]
	// in EDGE_ORDER
+ rules: list[str]
	// -> practice.in_graph.rule_labels
+ tree: ExplorerEntry
	// -> practice.in_graph.root.serialize()

## Node

A parsed object a practice reader added, or a plain node read back from `graph.json`. Model objects that build their own edges extend `ModelNode`.

+ practice: PracticeGuidance
+ type: str
+ node_id: str
+ name: str
+ source: Source
+ stage: str
	// one of STAGES.names (harness/guidance/stages.py), or empty
+ data: dict
	// facts only the reader knows, such as a class's folder; a reloaded node holds every saved fact here
+ graph_facts: tuple[str, ...]
	// class attribute: the parsed object's attributes that save with the graph
+ children: list[Node]
+ parent: Node | None
+ facts: dict
	// graph_facts attributes, then data; what graph.json keeps
+ rules: GraphRulesCollection
	// -> GraphRulesCollection.from_node on first read
+ file_language: str | None
	// python, typescript, javascript, drawio, or graph
+ failed_rules: list[str]
+ passing_rules: list[str]
+ fidelity: FidelityGuidance | None
+ fidelities: list[FidelityGuidance]
	// the practice's fidelities its schema.yaml says create this node type, and every higher one
----
+ get_fact(key, default=None): object
	// this node's fact, else the nearest ancestor's: a fact a whole file owns is kept once, on the file's top node
+ set_fact(key, value): None
+ has_fact(key): bool
+ place(file, start_line, end_line): None
	// -> practice.guidance.align_node(node): the practice moves a node it found by a nearby line onto the lines that declare it
+ populate(parent=None): None
	// for each edge kind by order, for each edge leaving this node:
	//   direct: edge.child.populate(this)
	//   grouped | relationship: edge.child.populate(holder), holder being this node's child named for the kind
	// the types a practice lists in source_ordered_types follow their source lines
+ serialize(seen, via, stack): ExplorerEntry
	// the full child list only at the node's home parent; a relationship copy is empty; a node already on the path is a stub
+ rule_category(): GraphRulesCollection | None
+ release(): None

## ModelNode

Extends `Node`. A model object that is its own node in the graph it was made on (`model_node.py`). Appending a child to one of its `ModelChildren` lists records the edge.

+ register_practice(practice_class: type): None
	// class operation: a practice's module registers itself on its model's base class when it is imported (`StoryNode.register_practice(Stories)`), so the model never imports its practice
+ practice_kind(): type
	// class operation: the practice class registered for this class or its nearest base; the graph holds that practice (Graph.practice_of). A model class with none registered raises ModelWithoutPractice
+ _semantic_type_name: str
+ _belongs: set[tuple[str, str]]
	// (child type, parent type) pairs that also record a belongsTo edge back
+ sequential_order: int
+ has_source_file: bool
+ graph: Graph
----
+ batch_schema_sync(): contextmanager
	// holds schema-edge rebuilds until a batch of links is done
- _link(child, kind): None
	// -> practice.record(kind, direct), belongsTo when the pair is listed, -> graph.sync_schema_edges()

## ModelChildren

Extends `list`. `append`, `extend`, `insert`, `pop`, and slice assignment record or remove the owner's edge. Appending a
part makes the owner its parent.

## ModelReferences

Extends `list`. The objects an owner refers to without owning them, such as the stories an increment delivers. Appending
records a relationship edge and leaves the object under its own parent; an owner that moves to another graph records
its references there.

+ owner: ModelNode
+ kind: str

## EdgeType

+ kind: str
+ order: int
+ display: str
	// direct | grouped | relationship
----
+ from_kind(kind, display="direct"): EdgeType
	// the order EDGE_ORDER gives the kind; a kind only an overlay schema names sits at 2 when direct, 7 otherwise

## Edge

+ kind: str
+ order: int
+ display: str
+ parent: Node
+ child: Node
+ stage: str
	// the child's

## EDGE_ORDER

Where each kind's group sits under a node in the explorer tree, lowest first. `EdgeType.from_kind(kind, display)` reads it.

```
1  decomposedInto relative root descriptions participants screens
2  owns background contexts parameters aggregates given
3  scenarios properties observations
4  steps demonstrates shownOn specifiedBy specifies
5  examples belongsTo
6  hasParameter increments accesses
7  hasType returnType stories associates
8  observes demonstratedThrough
9  ands uses invokedBy
10 returns
11 retrievedUsing
12 invokes
13 dependsOn
14 usedBy
```

## Source

The text the explorer's source view shows.

+ file: str
+ start_line: int
+ end_line: int
+ root: str
+ calls: list[Call]
+ language: str
+ text: str
	// the lines start..end with /* call:name */ after each call; folds and inlining are built in app/source/call-expansion.ts
----
+ whole_file(relative, root): Source
+ align_to_label(label): None
+ widen_to_call_close(): None
+ align_to_example_export(root, name): None

## Call

+ line: int
+ order: int
+ operation: str

## Filter

+ practices: list[str]
+ node_types: list[str]
+ relationships: list[str]
+ rules: list[str]
+ violations: bool
+ name: str
+ paths: list[str]
----
+ select_practices(practices): None
	// offers the node types, relationships, and rules those practices hold
+ select_node_types(node_types): None
+ select_relationships(relationships): None
+ select_rules(rules): None
+ select_violations(): None
+ clear(): None
+ narrowed_by(request): Filter
+ matches(node): bool

## A practice in the graph (PracticeGuidance)

What one practice gives the graph is declared on its own `PracticeGuidance` class (`harness/guidance/guidance.py`); the base reads nothing and checks the rules in `{package}.rules`, so a practice that only checks rules overrides nothing. Each practice's readers live in `{practice}/model/graph_reading.py`.

+ graph: Graph | None
	// the graph that holds this practice; none for a practice no graph holds
+ extended: PracticeGuidance | None
	// the practice extends names, held: one of the same set of practices
+ checks(): dict[str, PracticeGraphRule]
	// graph_checks() with the rules the graph's overlays add
+ package: str
	// the practice's Python package, from PracticeCatalogue
+ reads_after: tuple[str, ...]
+ node_types: tuple[str, ...]
	// offered by the explorer before any node of them is read
+ read_working_copy(): None
+ link_to_other_practices(): None
+ align_node(node): None
+ graph_checks(): dict[str, PracticeGraphRule]
+ own_graph_checks(): dict[str, PracticeGraphRule]
	// -> rules_in(f"{package}.rules"): the module's BY_SLUG, else its RULES

`PracticeGuidance.checks()` is its part of the graph's `checks`, which adds each active overlay's `rules_for(practice)` to the practice's own (`PatternOverlays.checks_of`); `node.rules` keeps those whose `node_types` hold the node's type, its file language's, or the Clean Engineering type a pattern's schema anchors it to.

## GraphOverlay

What one pattern gives the graph on top of the practices.

+ GraphOverlay(pattern: PracticeGuidance)
	// made once by the pattern that owns it, as pattern.graph_overlay
------
+ pattern: PracticeGuidance
	// the pattern's guidance, which gives each overlay rule its prose
+ name: str
	// the pattern's folder name, such as lern_domain_driven
----
+ read(graph: Graph): None
+ rules_for(practice: PracticeGuidance): dict[str, PracticeGraphRule]
	// read once per practice from the pattern's own practices/{practice}/rules

## PracticeGraphRule

One rule a practice checks on loaded nodes (`practice_rule.py`). A practice writes each rule as a subclass in its `rules` package.

+ slug: str
+ node_types: tuple[str, ...]
----
+ check(node, context: RuleCheckContext): list[str]
	// one message per violation on node
+ check_practice(context: RuleCheckContext): list[tuple[str, str]]
	// (node_id, message) pairs from one pass over the whole practice
+ applies_to(node_type): bool

## RuleCheckContext

+ practice: PracticeGuidance
+ source_root: Path | None
----
+ child_count(node, edge_kinds): int
+ children(node, edge_kind): list[Node]
+ node_data(node): dict
+ scenario_outline(node): bool
+ scenario_evidence(node): list[str]

## GraphRulesCollection

Extends `RulesCollection` (harness/guidance). The rules that apply to one node, built by `GraphRulesCollection.from_node` from the slugs the practice's `model/schema.yaml` lists on the node's type (plus each active overlay's `schema.yaml` and `rules.yaml`). In the explorer tree it is the node's `rules` child.

+ node: Node
+ slugs: list[str]
+ shown: list[GraphRule]
	// every rule, or only the failing chosen ones when the graph's filter asks for violations
+ violations: list[Violation]
+ failed_slugs: list[str]
+ passing_slugs: list[str]
----
+ chosen(violations_only, selected): list[GraphRule]
+ record_violation(slug, message): None
	// a slug the node has no rule for records nothing
+ restore(violation): None
+ clear_violations(): None

## GraphRule

Extends `PracticeGraphRule` and `Rule`. One schema rule on one node.

+ node: Node
+ slug: str
+ body: str
	// the rule's prose from the practice's or pattern's guidance (PracticeSchema.rule_prose)
+ executable: bool
	// a check with this slug exists
+ status: str
	// violating | passing | prompt (no check runs it)
+ violations: list[Violation]
----
+ record(message): None
	// -> NodeViolation.at_node; the same message is kept once
+ restore(violation): None

## Violation

One place a rule is broken (`violation.py`). The saved graph keeps it, the explorer shows it under the node's rule, and the Validate action's report and the board read it back.

+ rule: str
+ practice: str
+ node_id: str
+ subject: str
	// what the node is, such as Operation `checkout`
+ location: str
	// the file, or unknown
+ line: int | None
+ end_line: int | None
+ message: str
+ severity: str
+ source: list[SourceLine]
+ described: str
----
+ from_data(data): Violation

*NodeViolation* : *Violation* is one found on a graph node: it holds the node's *GraphRule* (`found_by`), and its rule,
practice, node id, and subject are that rule's, its node's, and its practice's. It saves as the same data.

+ NodeViolation.at_node(found_by: GraphRule, message: str): NodeViolation
+ found_by: GraphRule
	// the data return_nodes sends and the saved graph keeps
+ is_under(prefixes): bool
+ in_file(location, file, lines_before, lines_after): Violation

## Explorer answers

`explorer.py`. Each is a `NodeAnswer`: it holds the node it describes and sends the node's `node_id`, `name`, and `type` from it.

- `ExplorerEntry` — one node at one place in the explorer tree, with the entries below it there.
- `FilteredNode` — a node `return_nodes` matched, with its practice, ancestors, children, and rules.
- `NodeSource` — a node's file, text, lines, and owning class; the opened node also lists every class, operation, and property the loaded graph holds, each as its own `NodeSource`, so a call in it can be opened. The practices name those types in their `PracticeGuidance.class_types` and `member_types`.
- `GraphLoaded`, `GraphSaved`, `Overlay` — the message, path, or overlay root a tool answers with.

## graph.json

`saved_graph.py`. `SavedGraph` owns the document: `SavedNode`, `SavedEdge`, and `SavedPractice` write and read each record by field name, and `SavedGraphFile` is the file in a folder's `.context` and decides whether it is still current. A node names `node_id`, `name`, `type`, and `practice` as `return_nodes` does, and a violation is the same data a returned node's rule lists.

```
{ version: 2, overlays: [..],
  practices: { <practice>: { source_root, root_facts, nodes, edges, violations } } }
node:      { node_id, name, type, practice, file, line, end_line, stage, facts }
edge:      { parent, child, kind, order, display }
violation: { rule, practice, node_id, subject, location, line, end_line, message, severity, source }
```

`root_facts` holds the practice root's facts, such as a file another practice could not read. A document of any other `version` is `SavedGraphOutdated`: the loader reads the folder again, and a reader of its violations is told to load the working copy again.

## What a practice declares on its PracticeGuidance

The graph names no practice, so each practice's `PracticeGuidance` class says what only it knows:

- `class_types`, `member_types` — the classes and their operations and properties a source view can open.
- `class_node_type` — the type its checks run on as a whole class; another practice's node inside one skips those checks.
- `source_ordered_types` — the types the explorer lists in file order.
- `extends`, `anchor_types` — the practice whose types its schema builds on with `is:`, and the `is:` words another practice uses for its own types.
- `rule_types` — node types that also carry the rules the schema gives other types.
- `align_node(node)` — moves a node found by a nearby line onto the lines that declare it.

A pattern's `GraphOverlay` declares `direct_kinds`, the relationship kinds of its schema the explorer shows as children.

---

# Clean Engineering

*CleanEngineering*, with its readers in `cdd_guidance/practices/clean_engineering/model/graph_reading.py`. It reads each source file with its language's class model, then the model documents `{folder}/.context/*-model.md` of the folders in scope.

## Nodes

```
Module      clean_engineering:Module:{folder}                 a folder that owns .context/module-context.md
Package     clean_engineering:Package:{folder}                any other folder with source
OoadClass   clean_engineering:OoadClass:{file}:{class}        facts: folder, plus the class's graph_facts
Property    clean_engineering:Property:{file}:{name}:{class}  facts: owner; a getter's measurements
Operation   clean_engineering:Operation:{file}:{name}:{class} facts: parameters, owner, line_count, callees, ...
Parameter   clean_engineering:Parameter:{file}:{name}:{class}.{operation}
```

A file's top-level functions are operations of the `_module` class its language model gives that file. The Clean Engineering practice keeps the class model each model document describes and answers `described_member(owner, name)`; the graph holds no copy of those members.

## Edges

```
owns         direct        Practice|Module -> Module|Package, Module|Package -> OoadClass, OoadClass -> Operation
belongsTo    relationship  Package -> enclosing folder, OoadClass -> its folder
properties   grouped       OoadClass -> Property
relative     direct        OoadClass -> Property whose type names another loaded class
hasType      relationship  Property -> OoadClass its type names
dependsOn    relationship  OoadClass -> OoadClass a property's type names
hasParameter relationship  Operation -> Parameter
returns      relationship  Operation -> OoadClass its return type names
```

`invokes`, `invokedBy`, `usedBy`, `demonstrates`, `demonstratedThrough`, and `retrievedUsing` are recorded here by Stories and BDD when they link.

## Rules

`cdd_guidance.practices.clean_engineering.rules`.

# DDD

*Ddd*, with its readers in `cdd_guidance/practices/ddd/model/graph_reading.py`. `reads_after = ("clean_engineering",)`: its building blocks are the classes Clean Engineering read, seen through the stereotype their declaration or name gives them (`TacticalClass.inferred_kind`); a class with neither is not a building block. A building block is a `BuildingBlock` node that holds the class and works out its tactical facts from the class's operations; the class's own facts stay the class's, and the class stays Clean Engineering's node.

## Nodes

```
BoundedContext  ddd:BoundedContext:{folder}:{name}   a folder holding .context/bounded-context.md; the whole folder when none does
Aggregate       ddd:Aggregate:{folder}               a folder outside tests/ and test-utils/ holding building blocks
EntityRoot | Entity | ValueObject | Repository
                ddd:{kind}:{file}:{class}            facts: folder, the class's facts, tactical facts
```

## Edges

```
owns        direct        Practice|BoundedContext -> BoundedContext, BoundedContext -> Aggregate, Aggregate -> member
root        direct        Aggregate -> EntityRoot
belongsTo   relationship  BoundedContext -> outer context, Aggregate -> BoundedContext, member -> Aggregate
accesses    relationship  {Root}Repository -> {Root}
associates  relationship  EntityRoot -> EntityRoot it names with a `// foreign Name` comment
```

## Rules

`cdd_guidance.practices.ddd.rules` together with every Clean Engineering rule.

# Stories

*Stories*, with its readers in `cdd_guidance/practices/stories/model/graph_reading.py`. It reads the TypeScript and JavaScript story tests into a story model (`TypeScriptStoryModel`), or the story maps (`StoryModel`) when there are none, and `StoryModel.record` has each object add itself to the practice graph.

## Nodes

```
Epic | SubEpic       stories:{Epic|SubEpic}:{folder}:{name}
Story                stories:Story:{file}:{name}
Background           stories:Background:{file}:{label}
Scenario             stories:Scenario:{file}:{name}
Given | When | Then | Step
                     stories:{type}:{file}:{line}:{label hash}   facts: keyword, text, phase, callees, ...
Example              stories:Example:{file}:{name}               a plain node
```

## Edges

```
decomposedInto  direct        Practice|Epic -> Epic|SubEpic|Story
background      direct        Story -> Background
scenarios       direct        Story -> Scenario
steps           direct        Scenario|Background -> step
ands            direct        step -> its continuation
examples        direct        Scenario -> Example
```

`link` (when Clean Engineering is loaded):

```
invokes         relationship  step -> Operation it calls          (Operation -> step as invokedBy on Clean Engineering)
uses            relationship  Epic -> Module of those operations  (the top-level epic whose tree holds the step; usedBy back on Clean Engineering)
observes        relationship  phased step -> Example its body names
demonstrates    grouped       Example -> OoadClass it names       (demonstrates, demonstratedThrough back on Clean Engineering)
retrievedUsing  relationship  Example -> Property it reads        (and back on Clean Engineering)
```

## Rules

`cdd_guidance.practices.stories.rules`.

# BDD

*Bdd*, with its readers in `cdd_guidance/practices/bdd/model/graph_reading.py`. Each spec file's language model (`PythonBddModel`, `TypeScriptBddModel`) parses its describe tree, whose objects are added as they are.

## Nodes

```
Spec          bdd:Spec:{file}
Description | Context | Observation
              bdd:{type}:{file}:{line}:{name}
```

## Edges

```
owns          direct        Practice -> Spec
descriptions  direct        -> Description
contexts      direct        -> Context
observations  direct        -> Observation
invokes       relationship  Observation -> Operation|Property it drives   (link; invokedBy back on Clean Engineering)
```

## Rules

`cdd_guidance.practices.bdd.rules`.

# UX

*Ux*. A working-copy load reads no UX files. It offers the node types `UxMap`, `Screen`, `Region`, `Control`, `StoryDemoControl`, `Interaction`, `Transition`, `ContentType`, `NavComponent`, `UxContext`, and checks `cdd_guidance.practices.ux.rules` on UX maps put on a graph.

# Pattern overlays

Each adds nodes and rules when `overlays` names it. Its rules live in `cdd_guidance/patterns/{pattern}/practices/{practice}/rules`, and its node types and rule slugs in that folder's `model/schema.yaml` and `model/rules.yaml`.

- `lern_domain_driven` (`LernOverlay`) — on DDD: each aggregate's tier files (`NodeRoot`, `ClientRoot`, `Route`, `JsonStore`, `View`), the behavior test files (`BehaviorShared`, `BehaviorDomain`, `BehaviorServer`, `BehaviorPlaywright`, `BehaviorE2e`), and `ContextMapping`s from a bounded context's arrows; on Stories: the story test files (`StoryShared`, `ServerSpec`, `DomainSpec`, `PlaywrightSpec`). Edge kinds come from the pattern schema (`owns`, `views`, `nodeRoot`, `interacts`, `calls`, `writes`, `nodeRepository`, `view`, `clientRoot`, `mappedTo`, ...).
- `cdd_web_domain_access` (`WebDomainAccessOverlay`) — on DDD: `AccessRoute`, `AccessNode`, `AccessHandWrittenAdapter`, and `AccessAnnotatedToolset`, one per file, with the facts its rules read.
- `cdd_claude_mod` (the base `GraphOverlay`) — adds no nodes; its guidance gives its rules their prose.

The behaviour of a load on `harness/graph/_examples/input` is specified in `harness/graph/graph_spec.py`.
