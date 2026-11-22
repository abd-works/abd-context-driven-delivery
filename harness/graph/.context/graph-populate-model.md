# Graph

`Graph` reads a working copy into the practices it holds: the `PracticeGuidance` objects it is given, which a session gives from its own practices and a graph no session holds makes with `PRACTICE_CATALOGUE.create_all`. Each practice holds the graph (`practice.graph`), and the graph keeps every practice's nodes and edges itself, indexed by the practice. The graph names no practice: each practice's `PracticeGuidance` class says what the graph reads from it, and each pattern is a *PracticeGuidance* that makes its `GraphOverlay` once and keeps it as `graph_overlay`; the graph holds one *PatternOverlays* (`graph.applied_patterns`), which makes each pattern its overlays name once, when its overlays are set, so the practices depend on the graph and never the other way round.

A practice reader parses its files with the practice's own model and adds each parsed object (a class, an operation, a story, a spec's observation) to its practice in the graph as the node itself (`practice.reading.in_graph.add(node, ...)`), so a rule reads its measurements from the same object the explorer shows. A node with no parsed object behind it, such as a story's example or a LERN tier file, is a plain `Node` made with `practice.reading.in_graph.add_named`. Edges are recorded through the graph's *GraphEdges* (`graph.edges.link`, `.relate`, `.group`), on the parent's practice; an edge's place under its parent in the explorer tree comes from `_EDGE_ORDER`.

A load runs in this order (`GraphBuild._read_working_copy` in `graph_build.py`): each practice's reading part `read`s, in the order its `reads_after` needs, and links its nodes to the nodes of the practices it read after; then each applied overlay `read`s; then each practice's `reading.in_graph.rule_run.check()` runs its checks and records each finding as a `Violation` on its node; then each practice `rebuild_tree`s. `save_json` writes the result to `{folder}/.context/graph.json`, and a later `load_working_copy` reads that file back instead of parsing when it is still current.

A node's id is `{practice}:{type}:{file or folder}:{name}`, with the owning class or operation added when the name alone is not unique. The practice sections below give each one.

---

## Graph

The toolset the graph tools run on. A session holds one (`Session.graph`), with the session's practices in it; each project's cdd runtime also holds one for calls that work in no session. Annotated `@language_adapter(language="typescript")`, so the explorer app calls the same operations through the generated `GraphClientGenerated`. Each of its jobs is a part it makes once and keeps; its MCP operations are the one entry and hand each job to its part. It extends *GraphExplorer*, the `@hosted_only` class whose queries are published under the toolset name `graph` too. The call a tool answers stops here: a tool says whether its build runs apart, in a worker process (`call.request.answers_a_chat`), and hands its reads that word.

+ practices: GraphPractices
	// the practices it holds, those a load reads, and those open now
+ scope: LoadScope
	// the folder and files of the load or refresh it last made; each read makes its own
+ build: GraphBuild
	// loads, refreshes, and rule runs, here or in a worker for a chat's call
+ schema_edges: SchemaEdges
+ applied_patterns: PatternOverlays
+ overlays: list[str]
	// pattern overlay roots, each a folder holding practices/; setting them holds the pattern each one is and asks it for its GraphOverlay
+ folder: str
	// the loaded folder; graph.json lives in its .context
----
+ Graph(practices=None)
	// holds practices, each of which then holds this graph and its PracticeNodes; with none, a set of its own from PRACTICE_CATALOGUE.create_all(fidelity=None)
+ reads: GraphReads
	// what the graph reads and when, each read run alone; every load tool hands its call to it in one line
+ for_call(call): Graph
	// the call's session's graph, so every graph tool a call in that session makes runs on it
+ node(node_id): Node | None
+ link(kind, parent, child, display="direct"): None
	// -> record(EdgeType.from_kind(kind, display), parent, child)
+ record(edge_type, parent, child): None
	// on practices.part_of(parent.practice)
+ edges_from(kind, parent): list[Edge]
+ direct_parent(child): Node | None
+ load_working_copy(folder, practices, database=None, overlays=None, force=False, call=None): GraphLoaded
	// @mcp. holding reads.changing, chooses the scope, the practices' roots, and the overlays, then -> reads.load(force, apart)
+ load_practice_roots(call=None): GraphLoaded
	// @mcp. -> reads.practice_roots(apart)
+ load_files(folder, practices, files, overlays=None, call=None): GraphLoaded
	// @mcp, /load-files. holding reads.changing, scope = LoadScope.of_paths(folder, files), then -> reads.edited_files(apart); never touches the saved graph
+ refresh(paths, call=None): GraphLoaded
	// @mcp. -> reads.refresh(paths, apart)
+ save_json(): GraphSaved
	// @mcp. -> saved_file.save(SavedGraph.from_graph(self)); practices already saved and not loaded now stay
+ saved_file: SavedGraphFile
+ set_overlays(overlays, call=None): AppliedOverlays
	// @mcp. -> AppliedOverlays(reads.apply_overlays(overlays, apart)), which names the overlays now applied

## GraphExplorer

`@hosted_only`, extended by *Graph*: the explorer's queries, published as the graph's own tools under the toolset name
`graph`. Each query makes a *Filter* for the *FilterRequest* its call sends, so no filter stays chosen on the server.

+ overlay_of(folder): Overlay
	// @mcp. raises GraphFailure when the folder and its parents hold no practices/
+ practice_names(): list[str]
	// @mcp. the key of every practice the graph holds
+ inventory(): Inventory
+ filter_choices(practices, node_types, practices_before=None): FilterChoices
+ source(node_id): NodeSource | None
+ source_members(): list[NodeSource]
+ return_nodes(filter: FilterRequest | None = None), explorer_trees(filter=None), explorer_branch(node_id, filter=None)
	// @mcp. explorer_trees sends each root with the entries below it closed; explorer_branch sends one
	// entry's next level, so the page reads only the levels a person opens

## GraphReads (graph_reads.py)

What a graph reads, and when: the graph makes it once and keeps it (`graph.reads`). It holds the lock that runs a load,
a refresh, and a write alone (`changing`), since calls in one session can arrive at once. `apart` says a build runs in a
worker process; the graph's tools work it out from the call they answer.

+ GraphReads(graph)
+ changing: RLock
----
+ open(folder): None
	// every practice rooted on folder, holding its root node alone
+ open_saved(folder): None
	// open, then hold the saved graph's practices on their saved roots
+ load(force, apart): GraphLoaded
	// the chosen practices from the saved graph when it holds them, else read and saved
+ edited_files(apart): GraphLoaded
	// build from only the edited files the scope names
+ practice_roots(apart): GraphLoaded
	// each practice on its session root that is there to read, then -> load(False, apart)
+ refresh(paths, apart): GraphLoaded
+ hold_whole(apart=False): None
	// load the whole working copy when the graph holds only some files
+ refreshed(paths, checked, apart=False): None
	// refresh, and write the nodes read from paths at checked, as one change; the worker writes them when apart
+ apply_overlays(overlays, apart): Graph
	// apply the overlays and load the open folder again with them; answers the graph

## GraphPractices (graph_practices.py)

+ held: dict[str, PracticeGuidance]
	// every practice the graph holds, read or not
+ opened: dict[str, PracticeGuidance]
	// the practices open in the graph, which hold its nodes
+ chosen: list[PracticeGuidance]
	// the practices the next load reads, each on the root its part keeps
----
+ named(key), of(kind), loaded(kind), part_of(practice)
	// of opens the practice of that class; loaded answers it only when open; part_of refuses a practice another graph holds
+ choose(roots), roots_by_key, open_chosen(), reopen(saved), restore(saved), hold(saved)
	// restore: the saved overlays, then hold(saved)
+ rebuild_trees()

## LoadScope (load_scope.py)

+ folder: Path | None
+ named: list[Path] | None
	// every file a load of edited files or a refresh names, gone or not; None for the whole folder
+ edited_files: list[Path] | None
	// the named files that are there to read
----
+ of_paths(folder, paths, skipped=()): LoadScope
+ refreshing(paths): LoadScope
	// skips the folders no practice reads, keeps a gone file so its nodes drop
+ source_files(root, suffixes): list[Path]
+ folders: list[Path] | None

## GraphBuild (graph_build.py)

+ run(task: BuildTask, state=None), carry_out(order), changed()
	// a task that runs apart (BuildTask(step, saves, checked, apart)) builds in a worker (WorkerBuild); the worker's answer is taken whole (practices.hold) or as changes (WorkerBuild, each practice's restore). HeldAnswer counts each change, so an order names the last answer while the graph still holds it

## PracticeNodes

+ root, source_root, nodes(type=None), nodes_read_now(type=None), node(node_id), holds(node_id), node_types, offer_node_types(types), add(...), add_file(type, relative, name=""), hold(node), release(node), drop(dropped), put_in_source_order(), unused_node_id(type, name)
	// add_file: the practice's node for a whole file or folder (a pattern's tier file, an aggregate's folder), the one held or a new one; one place for every pattern overlay
	// it holds its nodes itself, by id, by type, and the relationship groups its tree puts edges under
+ edge_index: EdgeIndex
	// the edges by kind (edge_index.of(kind)), with the kinds' EdgeTypes and the indexes by pair, by parent, and by direct child
+ rule_run: PracticeRuleRun
	// schema, schema_with(overlays), checks, rule_labels, rule_labels_for(types), check(), renew()
+ loading: PracticeLoading
	// open(root), close(), forget_files(files): what a load, a refresh, or a restore does to the nodes the practice holds
+ restore: PracticeRestore
	// nodes(saved), changes(changes), links(saved): one way to take saved state, for a restore and a worker's changes

## Inventory

+ practices: dict[str, PracticeInventory]
+ overlays: list[str]
+ available_overlays: list[str]
	// each folder under cdd_guidance/patterns that holds practices/; all three read from the graph

## AppliedOverlays

Extends `Inventory`.

+ message: str

## PracticeInventory

One loaded practice as the explorer's inventory shows it, read from the graph that holds it (explorer.py).

+ node_counts: dict[str, int]
+ edge_count: int
+ node_types: list[str]
+ edge_types: list[str]
	// in _EDGE_ORDER
+ rules: list[str]
	// -> practice.reading.in_graph.rule_run.rule_labels
	// no tree: graph.explorer_trees answers each practice's tree as the explorer's filter leaves it; a whole
	// repository's tree runs to hundreds of megabytes, which no page reads and no call sends within ten minutes

## Node

A parsed object a practice reader added, or a plain node read back from `graph.json`. Model objects that build their own edges extend `ModelNode`.

+ Node(practice, identity: NodeIdentity, source)
	// NodeIdentity(type, node_id, name): what a node is called, as one value
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
+ tree: NodeTree
	// its place in the explorer tree, made once
+ facts: dict
	// graph_facts attributes, then data; what graph.json keeps
+ rules: GraphRulesCollection
	// -> GraphRulesCollection.from_node on first read
+ file_language: str | None
	// python, typescript, javascript, drawio, or graph
+ failed_rules: list[str]
+ fidelity: FidelityGuidance | None
+ fidelities: list[FidelityGuidance]
	// the practice's fidelities its schema.yaml says create this node type, and every higher one
----
+ get_fact(key, default=None): FactValue
	// this node's fact, else the nearest ancestor's: a fact a whole file owns is kept once, on the file's top node
+ set_fact(key, fact): None
+ set_facts(facts: NodeFacts): None
	// each fact as set_fact records it: an overlay records the facts a tier file's reader found in one call
+ merge_fact(key, values): None
+ has_fact(key): bool
+ place(file, start_line, end_line): None
	// a practice whose reader finds a node by a nearby line, as Stories' recording does, moves it onto the lines that declare it
+ forget_rules(): None

## NodeTree

One node's place in its practice's explorer tree, which the node makes once and keeps (`node.tree`). The node keeps
its `parent` and `children`; this part keeps whether its children are placed yet.

+ NodeTree(node)
----
+ populate(parent=None): None
	// for each edge kind by order, for each edge leaving the node:
	//   direct: edge.child.tree.populate(node)
	//   grouped | relationship: edge.child.tree.populate(holder), holder being the node's child named for the kind
	// the types a practice lists in source_ordered_types follow their source lines
+ leave(): None
	// out of the tree, so the next populate places it again
+ rebuild(): None
	// on a practice's root: every node of the practice leaves the tree, then the root places them again
+ serialize(seen, via, stack): ExplorerEntry
	// the full child list only at the node's home parent; a relationship copy is empty; a node already on the path is a stub

## ModelNode

Extends `Node`. A model object that is its own node in the graph it was made on (`model_node.py`). Appending a child to one of its `ModelChildren` lists records the edge.

+ practice_class: type | None
	// class attribute: a practice's module sets itself on its model's base class when it is imported (`StoryNode.practice_class = Stories`), so the model never imports its practice
+ practice_kind: type
	// the practice class of this object's class or its nearest base; the graph holds that practice (graph.practices.of). A model class naming none raises ModelWithoutPractice
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
	// -> practice.record(kind, direct), belongsTo when the pair is listed, -> graph.schema_edges.sync()

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
	// the order _EDGE_ORDER gives the kind; a kind only an overlay schema names sits at 2 when direct, 7 otherwise

## Edge

+ kind: str
+ order: int
+ display: str
+ parent: Node
+ child: Node
+ stage: str
	// the child's

## _EDGE_ORDER

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
+ align_to_example_export(name, files): None

## Call

+ line: int
+ order: int
+ operation: str

## FilterRequest, FilterChoices, Filter (node_filter.py)

*FilterRequest* is the TypedDict a call sends: practice(s), type(s), name, rules, relationships, violations, path(s).

*FilterChoices* (`graph.filter_choices`) answers what the explorer's filter offers, made for one question and kept by no one.

+ FilterChoices(graph, practices, node_types, practices_before=None)
+ node_types, offered_node_types, relationships, rules: list[str]
	// after a change of practice, the chosen node types the new practices still hold stay chosen, with every type of each practice added

*Filter* is made for one request; no filter stays chosen on the graph between calls.

+ Filter(graph, request: FilterRequest | None)
+ practices, node_types, relationships, rules, paths: list[str]; violations: bool; name: str
----
+ matches(node): bool
+ lists(file): bool
+ collect(roots): list[FilteredNode]

## A practice in the graph (PracticeReading)

What one practice gives the graph is its reading part, a *PracticeReading* (`harness/graph/practice_reading.py`) the practice holds as `practice.reading`, of the kind its class names (`reading_type`); the base reads nothing and checks the rules in `{package}.rules`, so a practice that only checks rules names no kind of its own. Each practice's kind of reading lives in `{practice}/model/graph_reading.py`, or in its own `{practice}/reading/` package for Clean Engineering and DDD, whose class models other practices import.

+ held_in(graph, nodes): None
	// the graph hands the part itself and the practice's PracticeNodes
+ graph: Graph | None
	// the graph that holds this practice; none for a practice no graph holds
+ in_graph: PracticeNodes | None
+ checks(): dict[str, PracticeGraphRule]
	// graph_checks with the rules the graph's overlays add
+ package: str
	// the practice's Python package, from PracticeCatalogue
+ reads_after: tuple[type[PracticeGuidance], ...]
	// the practices read first, by their classes; the build finds each open one with graph.practices.loaded(kind)
+ node_types: tuple[str, ...]
	// offered by the explorer before any node of them is read
+ read(): None
	// offers node_types, then read_working_copy
+ read_working_copy(): None
	// reads the practice's nodes, then links them to the nodes of the practices it reads after
+ graph_checks: dict[str, PracticeGraphRule]
	// read once
+ own_graph_checks(): dict[str, PracticeGraphRule]
	// -> rules_in(f"{package}.rules")
+ rules_in(module_path: str): dict[str, PracticeGraphRule]
	// static: the module's BY_SLUG, else its RULES; a pattern's overlay reads its rules modules with it too

`PracticeReading.checks()` is its part of the graph's `checks`, which adds each active overlay's `rules_for(practice)` to the practice's own, then each always-on supplement the practice holds (`practice.supplements`), whatever overlays the session chose (`PatternOverlays.checks_of`). A practice's schema reads the same overlays (`PatternOverlays.overlays_for(practice)`: the applied patterns', then its supplements'), so a supplement's `practices/<practice>/model/rules.yaml` gives its node types the supplement's rules, labelled with its name (`tdd.bdd.Spec.unit-tier-fakes-every-boundary`), and their prose comes from the supplement's sections. The build reads each supplement's overlay after the practices, as it reads each pattern's, so it records its facts on their nodes; `node.rules` keeps those whose `node_types` hold the node's type, its file language's, or the Clean Engineering type a pattern's schema anchors it to.

## GraphOverlay

What one pattern or one practice supplement gives the graph on top of the practices.

+ GraphOverlay(pattern: PracticeGuidance)
	// made once by the pattern or supplement that owns it, as its graph_overlay
------
+ pattern: PracticeGuidance
	// the pattern's or supplement's guidance, which gives each overlay rule its prose
+ name: str
	// its folder name, such as lern_domain_driven or tdd
----
+ read(graph: Graph): None
+ rules_for(practice: PracticeGuidance): dict[str, PracticeGraphRule]
	// read once per practice: its own practices/{practice}/rules, then its shared rules/ bound to that practice
	-> PracticeReading.rules_in(f"{package}.practices.{practice.key}.rules")
	-> PracticeReading.rules_in(f"{package}.rules")
	-> SharedPracticeGraphRule.for_practice(practice)

## PracticeGraphRule

One rule a practice checks on loaded nodes (`practice_rule.py`). A practice writes each rule as a subclass in its `rules` package.

+ slug: str
+ node_types: tuple[str, ...]
----
+ check(node, context: RuleCheckContext): list[Finding]
	// one Finding per violation on node
+ check_practice(context: RuleCheckContext): list[Finding]
	// each Finding names the node it was found on, from one pass over the whole practice
+ applies_to(node_type): bool
	Invariant: check and check_practice read only node facts (`get_fact`), node identity and source, and the graph's edges, and compare them with the rule's limit; a fact that compares a node with others is recorded by the practice's read, never worked out here (CDR 0004)

## SharedPracticeGraphRule : PracticeGraphRule

One rule an overlay checks on several practices' nodes, such as TDD's `one-outcome-per-test` on BDD observations and Stories Thens (`practice_rule.py`). It lives once, in the overlay's `rules/` package; each practice runs a copy bound to its own node types.

------
+ node_types_by_practice: dict[type[PracticeGuidance], tuple[str, ...]]
	// each practice's class to the node types it checks there, such as {Bdd: ("Observation",), Stories: ("Then",)}
----
+ for_practice(practice: PracticeGuidance): PracticeGraphRule | None
	// a copy whose node_types are that practice's, matched by its class; none for a practice it does not name
	Invariant: check reads only facts every named practice's reading records on its nodes

## RuleCheckContext

+ practice: PracticeGuidance
----
+ node_data(node): dict

## Finding

One thing a check found (`violation.py`): no longer a `str`, so a check that returns a plain string fails as soon as
it fires.

+ Finding(node: Node, message: str, lines: tuple[int, int] | None = None)
	// lines: the lines it is on when they are not the node's own, such as a module helper only one class uses

## GraphRulesCollection

A plain holder of the node's *GraphRule*s by slug (`entries`). The rules that apply to one node, built by `GraphRulesCollection.from_node` from the slugs the practice's `model/schema.yaml` lists on the node's type (plus each active overlay's `schema.yaml` and `rules.yaml`). In the explorer tree it is the node's `rules` child.

+ node: Node
+ slugs: list[str]
+ shown: list[GraphRule]
	// every rule, or only the failing chosen ones when the graph's filter asks for violations
+ violations: list[Violation]
+ failed_slugs: list[str]
+ passing_slugs: list[str]
----
+ chosen(violations_only, selected): list[GraphRule]
+ record(check: PracticeGraphRule, finding: Finding): None
	// the rule check's slug names on this node keeps the finding; a check the node has no rule for records nothing
+ restore(violation): None

## GraphRule

One schema rule on one node; it holds the graph check that runs it (a *PracticeGraphRule*) when one exists, rather
than being one, and is no guidance *Rule*: a rule an agent judges has no check and keeps only the prose.

+ node: Node
+ slug: str
+ body: str
	// the rule's prose from the practice's or pattern's guidance (PracticeSchema.rule_prose)
+ executable: bool
	// a check with this slug exists
+ runs: bool
	// its check applies to the node's type, or to the type it is anchored to
+ status: str
	// violating | passing | prompt (no check runs it)
+ violations: list[Violation]
----
+ check(context): list[Finding]
	// -> its check's check(node, context); none when no check runs it
+ record(finding: Finding): None
	// a NodeViolation on the lines finding names, else at the node's place
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
+ in_file(location, file): Violation

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
- `anchor_types` — the `is:` words another practice uses for this practice's types; the practice whose types a schema builds on with `is:` is the practice's `extends`.
- `rule_types` — node types that also carry the rules the schema gives other types.

A pattern's `GraphOverlay` declares `direct_kinds`, the relationship kinds of its schema the explorer shows as children.

---

# Clean Engineering

*CleanEngineering*, with its readers in `cdd_guidance/practices/clean_engineering/reading/graph_reading.py`. It reads each source file with its language's class model, then the model documents `{folder}/.context/*-model.md` of the folders in scope.

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

*Ddd*, with its readers in `cdd_guidance/practices/ddd/reading/graph_reading.py`. `reads_after = (CleanEngineering,)`: its building blocks are the classes Clean Engineering read, seen through the stereotype their declaration gives them, or, in a folder a bounded context covers or where a class carries a DDD stereotype, the one their name gives them (`TacticalClass.inferred_kind`); a class with neither is not a building block. A building block is a `BuildingBlock` node that holds the class and works out its tactical facts from the class's operations; the class's own facts stay the class's, and the class stays Clean Engineering's node.

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

- `lern_domain_driven` (`LernOverlay`) — on DDD: each aggregate's tier files (`NodeRoot`, `ClientRoot`, `Route`, `JsonStore`, `View`), and the behavior test files (`BehaviorShared`, `BehaviorDomain`, `BehaviorServer`, `BehaviorPlaywright`, `BehaviorE2e`); on Stories: the story test files (`StoryShared`, `ServerSpec`, `DomainSpec`, `PlaywrightSpec`). Edge kinds come from the pattern schema (`owns`, `views`, `nodeRoot`, `interacts`, `calls`, `writes`, `nodeRepository`, `view`, `clientRoot`, ...). A bounded context's `ContextMapping`s, from its `Local → Remote` lines, are DDD's own nodes (`DddReading`), whether or not a pattern is applied.
- `cdd_web_domain_access` (`WebDomainAccessOverlay`) — on DDD: `AccessRoute`, `AccessNode`, `AccessHandWrittenAdapter`, and `AccessAnnotatedToolset`, one per file, with the facts its rules read.
- `cdd_claude_mod` (the base `GraphOverlay`) — adds no nodes; its guidance gives its rules their prose.

The behaviour of a load on `harness/graph/_examples/input` is specified in `harness/graph/graph_spec.py`.
