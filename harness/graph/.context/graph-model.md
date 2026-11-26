# harness/graph

A *Graph* holds the practices it is given and, for each, a *PracticeNodes*: that practice's part of the graph, a tree of *Node* objects read from source, with its edges and the run of its graph rules; *PracticeGraphRule* checks report *Violation* records, and *SavedGraph* is the graph as `.context/graph.json` keeps it. What a practice gives the graph is its *PracticeReading* (harness/guidance), not a class of this module, and the graph's own jobs sit in parts of their own files: `graph_practices.py` (*GraphPractices*), `load_scope.py` (*LoadScope*), `graph_build.py` (*GraphBuild*, the worker build), `explorer.py` (the explorer's answers), `saved_graph.py`, `model_node.py`, `pattern_overlays.py`. The whole model of this module, internals included, is `harness/graph/.context/graph-populate-model.md`; that document is canonical, and this section shows only the classes other modules use.

- **Purpose:** Turn a working copy into a graph of its practices that rules can check and a person can explore.
- **Seam (terms):** Graph, GraphPractices, PracticeNodes, LoadScope, Node, NodeIdentity, Source, ModelNode, ModelChildren, ModelReferences, GraphOverlay, PatternOverlays, PracticeGraphRule, RuleCheckContext, Violation, SavedGraph, SavedNode, SavedPractice, SavedGraphOutdated; `schema_sync_paused()` (`model_node.py`), `scanned_files(root, suffixes)` and `skips_folder(name)` (`skipped_folders.py`), `GRAPH_APP_PORTS` (`graph_app.py`); the spec support RuleFixture, RulePair, SchemaRuleRun (`rule_fixture.py`), which each practice's `rules/rule_examples.py` imports
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/mcp, harness/guidance

## Graph

One graph. Builders fill nodes, edges, and rules; the explorer reads the tree. Each of its jobs is a part it makes once and keeps.

+ Graph(practices: Iterable[PracticeGuidance] | None = None)
------
+ << composition >> build: GraphBuild
+ << composition >> practices: GraphPractices
+ scope: LoadScope
+ << composition >> applied_patterns: PatternOverlays
+ << composition >> schema_edges: SchemaEdges
+ << composition >> edges: GraphEdges
+ << composition >> reads: GraphReads
+ folder: str
+ overlays: list[str]
+ saved_file: SavedGraphFile
----
+ for_call(call: ToolCall): Graph
+ node(node_id: str): Node | None
+ load_working_copy(folder: str, practices: dict[str, str], database: str | None = None, overlays: list[str] | None = None, force: bool = False, call: ToolCall | None = None): GraphLoaded
+ load_files(folder: str, practices: list[str], files: list[str], overlays: list[str] | None = None, call: ToolCall | None = None): GraphLoaded
+ refresh(paths: list[str], call: ToolCall | None = None): GraphLoaded
+ save_json(): GraphSaved
+ set_overlays(overlays: list[str], call: ToolCall | None = None): AppliedOverlays
---<<extends>>--> GraphExplorer
---<<makes its practices with>>--> PracticeCatalogue
---<<gives each practice its part through>>--> PracticeReading
---<<creates>>--> PracticeNodes
---<<creates>>--> GraphPractices
---<<creates>>--> LoadScope
---<<creates>>--> PatternOverlays
---<<creates>>--> GraphBuild
---<<keeps>>--> PracticeGuidance
---<<restores from>>--> SavedGraph
---<<reads the call's session from>>--> ToolCall

## GraphExplorer

`@hosted_only`, extended by *Graph*: the explorer's queries, published as the graph's own tools under the toolset name `graph`. Each query makes a *Filter* for the *FilterRequest* its call sends, so no filter stays chosen on the server between calls.

----
+ overlay_of(folder: str): Overlay
+ practice_names(): list[str]
+ inventory(): Inventory
+ filter_choices(practices: list[str], node_types: list[str], practices_before: list[str] | None = None): FilterChoices
+ source(node_id: str): NodeSource | None
+ source_members(): list[NodeSource]
+ return_nodes(filter: FilterRequest | None = None): list[FilteredNode]
+ explorer_trees(filter: FilterRequest | None = None): list[ExplorerEntry]
+ explorer_branch(node_id: str, filter: FilterRequest | None = None): ExplorerEntry | None
---<<creates>>--> Filter
---<<creates>>--> FilterChoices

## GraphPractices

The practices one graph holds, which the graph makes once and keeps (`graph.practices`): code that knows a practice's class reaches it by that class, and only a call that names a practice by its key looks it up by key.

+ GraphPractices(graph: Graph, held: Iterable[PracticeGuidance])
------
+ held: dict[str, PracticeGuidance]
+ opened: dict[str, PracticeGuidance]
+ chosen: list[PracticeGuidance]
+ roots_by_key: dict[str, Path]
----
+ named(key: str): PracticeGuidance
+ of(kind: type): PracticeGuidance
+ loaded(kind: type): PracticeGuidance | None
+ part_of(practice: PracticeGuidance): PracticeNodes
+ choose(roots: dict[PracticeGuidance, Path]): None
+ open_chosen(): None
+ reopen(saved: SavedGraph, folder: Path): None
+ hold(saved: SavedGraph, folder: Path | None): None
+ rebuild_trees(): None
---<<keeps>>--> PracticeGuidance
---<<reads the part of a practice from>>--> PracticeNodes
---<<restores each practice from>>--> SavedGraph
---<<raises>>--> UnknownPractice

## GraphReads

What a graph reads, and when (`graph.reads`): open it on a folder, with or without its saved graph; load a working copy, its practices' session roots, or some files; refresh the files an action wrote; make sure it holds the whole working copy; apply pattern overlays. Each read runs alone. The graph's load tools choose what to read while they hold its lock (`changing`) and say whether the build runs apart, in a worker process, so no read takes the call.

+ GraphReads(graph: Graph)
------
+ << association >> graph: Graph
----
+ changing: RLock
----
+ open(folder: Path): None
+ open_saved(folder: Path): None
+ load(force: bool, apart: bool): GraphLoaded
+ edited_files(apart: bool): GraphLoaded
+ practice_roots(apart: bool): GraphLoaded
+ refresh(paths: list[str], apart: bool): GraphLoaded
+ hold_whole(apart: bool = False): None
+ refreshed(paths: list[str], checked: Path, apart: bool = False): None
+ apply_overlays(overlays: list[str], apart: bool): Graph
---<<runs each BuildTask on>>--> GraphBuild
---<<creates>>--> LoadScope

## PracticeNodes

One practice's part of the graph that holds it: the root node its explorer tree starts from, the folder its source is read from, and its nodes, which it holds itself by type and by id. The graph makes one for each practice it holds and gives it to the practice, which reads it as `practice.reading.in_graph`.

+ PracticeNodes(graph: Graph, practice: PracticeGuidance)
------
+ << association >> graph: Graph
+ << association >> practice: PracticeGuidance
+ << composition >> edge_index: EdgeIndex
+ << composition >> rule_run: PracticeRuleRun
+ << composition >> loading: PracticeLoading
+ << composition >> restore: PracticeRestore
+ source_root_path: Path | None
+ source_root: str
+ root: Node
+ node_types: list[str]
----
+ nodes(type: str | None = None): list[Node]
+ nodes_read_now(type: str | None = None): list[Node]
+ node(node_id: str): Node | None
+ holds(node_id: str): bool
+ offer_node_types(types: Iterable[str]): None
+ add(node: Node, node_id: str, location: Location): Node
+ add_file(type: str, relative: str, name: str): Node
+ hold(node: Node): None
+ release(node: Node): None
+ drop(dropped: set[int]): set[int]
+ put_in_source_order(): None
+ unused_node_id(type: str, name: str): str
---<<keeps>>--> Node
---<<creates>>--> Source
---<<creates>>--> EdgeIndex
---<<creates>>--> PracticeRuleRun
---<<creates>>--> PracticeLoading
---<<creates>>--> PracticeRestore

## PracticeLoading

What a load, a refresh, or a restore does to the nodes one practice holds (`practice.reading.in_graph.loading`): open the practice on a root with its root node alone, close it, and drop the nodes read from files read again.

+ PracticeLoading(part: PracticeNodes)
------
+ << association >> part: PracticeNodes
----
+ open(root: Path | None): None
+ close(): None
+ forget_files(files: Iterable[Path]): set[int]
+ from_root(files: Iterable[Path]): set[str]

## LoadScope

The folder one load or refresh reads, and the files it is limited to; the graph keeps the scope of the read it last made (`graph.scope`), which the practices' readers ask while they read.

+ LoadScope(folder: Path | None, named: Iterable[Path] | None = None)
------
+ folder: Path | None
+ named: list[Path] | None
+ edited_files: list[Path] | None
+ folders: list[Path] | None
----
+ of_paths(folder: Path, paths: Iterable[str], skipped: frozenset[str] = frozenset()): LoadScope
+ refreshing(paths: Iterable[str]): LoadScope
+ source_files(root: Path, suffixes: set[str]): list[Path]
---<<lists files with>>--> scanned_files

## Node

children is the list its tree's populate writes on this node. Direct edges are the children; grouped and relationship edges sit under one child named for the kind. *NodeIdentity* (`type`, `node_id`, `name`) is what a node is called, as one value.

+ Node(practice: PracticeGuidance, identity: NodeIdentity, source: Source)
------
+ << association >> practice: PracticeGuidance
+ type: str
+ node_id: str
+ name: str
+ << composition >> source: Source
+ stage: str
+ data: dict
+ << aggregation >> children: list[Node]
+ parent: Node | None
+ << composition >> tree: NodeTree
+ graph_facts: tuple[str, ...]
+ facts: dict
+ graph: Graph
+ schema: PracticeSchema
+ fidelity: FidelityGuidance | None
+ fidelities: list[FidelityGuidance]
+ rules: GraphRulesCollection
+ file_language: str | None
+ places: dict[str, Location]
+ failed_rules: list[str]
+ passing_rules: list[str]
----
+ set_fact(key: str, value): None
+ get_fact(key: str, default = None): None
+ merge_fact(key: str, values: list): None
+ has_fact(key: str): bool
+ forget_rules(): None
+ place(file: str, start_line: int, end_line: int): None
+ written_at(location: Location): None
---<<creates>>--> NodeTree
---<<reads its part of the graph from>>--> PracticeReading
---<<calls changed on>>--> PracticeNodes
---<<calls from_parent on>>--> GraphEdges
---<<reads schema from>>--> PracticeRuleRun
---<<creates>>--> GraphRulesCollection

## NodeTree

One node's place in its practice's explorer tree (`node.tree`): it puts the node under its parent and the nodes its edges lead to under it, takes it out again for a rebuild, and writes the node's entry with the entries below it.

+ NodeTree(node: Node)
------
+ << association >> node: Node
----
+ populate(parent: Node | None = None): None
+ leave(): None
+ rebuild(): None
+ serialize(seen: set[str] | None = None, via: Node | None = None, stack: set[str] | None = None, label: str = ""): ExplorerEntry
---<<calls from_parent on>>--> GraphEdges
---<<creates>>--> ExplorerEntry
---<<creates>>--> PlaceLabels

## ModelNode : Node

Base model object for one practice. An object made without a graph is detached: it belongs to no practice and records no edge until a practice adopts it with its whole tree (`join`) or an owner on a graph takes it as a part.

+ ModelNode(name: str, sequential_order: int, graph: Graph | None = None)
------
+ sequential_order: int
+ has_source_file: bool
+ node: ModelNode
+ << association >> graph: Graph
----
+ practice_kind: type
+ semantic_type(): str
+ finish_building(): None
+ keeps_list(listed: ModelChildren | ModelReferences): None
+ attach(child, kind: str): None
+ join(practice): None
+ subtree(): list[ModelNode]
+ batch_schema_sync(): Iterator[None]
---<<joins a practice through>>--> GraphPractices
---<<calls add on>>--> PracticeNodes
---<<calls record on>>--> GraphEdges
---<<calls held on>>--> SchemaEdges
---<<keeps>>--> ModelChildren
---<<keeps>>--> ModelReferences
---<<creates>>--> Source
---<<raises>>--> ModelDetached

## ModelChildren : list

The list of the parts an owner is made of. Appending a part makes the owner its parent and records the edge.

+ ModelChildren(owner: ModelNode, kind: str)
------
+ << association >> owner: ModelNode
+ kind: str
----
+ append(item): None
+ extend(items: Iterable): None
+ insert(index: int, item): None
+ pop(index: int = -1): None
+ refill(incoming: Iterable): None
+ reconcile(sources: Iterable, load: Callable): None
---<<calls attach on>>--> ModelNode
---<<calls detach on>>--> ModelNode

## ModelReferences : list

The list of model objects an owner refers to without owning them, such as the stories an increment delivers; each one is a relationship edge.

+ ModelReferences(owner: ModelNode, kind: str)
------
+ << association >> owner: ModelNode
+ kind: str
----
+ append(item): None
+ extend(items: Iterable): None
+ insert(index: int, item): None
+ pop(index: int = -1): None
+ refill(incoming: Iterable): None
+ record_all(): None
---<<calls refer on>>--> ModelNode
---<<calls detach on>>--> ModelNode

## Source

Source text Monaco displays: file, start and end line, and text with each call marked.

+ Source(path: str, line_start: int, line_end: int, root: str = '')
------
+ file: str
+ start_line: int
+ end_line: int
+ root: str
+ calls: list[Call]
+ text: str
+ contents: str
----
+ whole_file(relative: str, root: str): Source
+ load_calls(raw: str): None
+ insert_calls(raw: str): str
+ align_to_label(label: str): None
+ widen_to_call_close(): None
+ align_to_example_export(root: str, name: str, files: Iterable[Path]): None
---<<keeps>>--> Call

## GraphOverlay

What one pattern gives the graph on top of the practices: the nodes it reads and the rules it adds to each practice, which live in `<pattern>/practices/<practice>/rules`. A pattern makes its overlay once and keeps it as `graph_overlay`.

+ GraphOverlay(pattern: Any)
------
+ << association >> pattern: PracticeGuidance
+ name: str
+ direct_kinds: frozenset[str]
----
+ display_of(kind: str): str
+ read(graph: Graph): None
+ practice_file(practice_key: str, name: str): Path
+ rules_for(practice: Any): dict[str, PracticeGraphRule]
---<<finds rules with>>--> PracticeReading
---<<loads>>--> PracticeGraphRule

## PatternOverlays

The pattern overlays one graph applies. The patterns package registers its pattern classes here when it is imported, and each graph makes each pattern once, the first time it applies it or reads its schemas, so the graph never imports a pattern.

+ PatternOverlays(overlays: list[str] | tuple[str, ...] = ())
------
+ paths: list[str]
+ patterns: list[PracticeGuidance]
+ graph_overlays: list[GraphOverlay]
+ every_graph_overlay: list[GraphOverlay]
+ available: list[str]
----
+ register(*pattern_classes): None
+ apply(overlays: list[str] | tuple[str, ...]): None
+ checks_of(practice: Any, overlays: list[str] | None = None): dict[str, PracticeGraphRule]
+ root_of(overlay: str): Path
---<<creates>>--> PracticeGuidance
---<<reads graph_overlay of>>--> GraphOverlay
---<<finds the folder of a pattern with>>--> class_folder

## PracticeGraphRule

One graph rule: the node types it checks and what it reports on a node or on the whole practice.

------
+ slug: str
+ node_types: tuple[str, ...]
----
+ check(node, context: RuleCheckContext): list[Finding]
+ check_practice(context: RuleCheckContext): list[Finding]
+ applies_to(node_type: str): bool
---<<checks a node within>>--> RuleCheckContext

## RuleCheckContext

The practice one load checks, the graph that holds it, and the folder its source was read from.

+ RuleCheckContext(practice, source_root: Path | None)
------
+ << association >> practice: PracticeGuidance
+ << association >> graph: Graph
+ source_root: Path | None
----
+ index(kind: type): None
+ targets(node, kind: str): list
+ nodes(type: str | None = None): list
+ edges(kind: str): list
+ node(node_id: str): None
+ child_count(node, edge_kinds: tuple[str, ...]): int
+ children(node, edge_kind: str): list
+ node_data(node): dict
---<<calls nodes on>>--> PracticeNodes
---<<calls edges on>>--> PracticeNodes
---<<calls from_parent on>>--> GraphEdges
---<<calls node on>>--> Graph

## Violation

A rule broken at one place: the rule and the practice that checks it, the node it was found on, what that node is (`Operation `checkout``), the file and lines, the message, and how severe it is. A violation found on a graph node is a *NodeViolation*, which holds the node's rule that found it (`NodeViolation.at_node`).

+ Violation(found_by: FoundBy, message: str, location: Location = NOWHERE)
------
+ rule: str
+ practice: str
+ node_id: str
+ subject: str
+ location: Annotated[str, SourceFile]
+ line: int | None
+ end_line: int | None
+ message: str
+ severity: str
+ source: list[SourceLine]
+ described: str
----
+ from_data(data: dict): Violation
+ by_rule(violations: list[Violation]): dict[str, list[Violation]]
+ is_under(prefixes: list[str]): bool
+ in_file(location: str, file: Path): Violation
---<<annotated with>>--> SourceFile
---<<keeps>>--> SourceLine

## SavedGraph

Every practice a folder's saved graph keeps, with the pattern overlays it was loaded with. A graph kept for the files a validate checks also names the folders of the other files the graph held (`held_beside`).

+ SavedGraph(overlays: list[str], practices: dict[str, SavedPractice], held_beside: list[str] | None = None)
------
+ overlays: list[str]
+ << composition >> practices: dict[str, SavedPractice]
+ held_beside: list[str]
+ document: dict
+ text: str
----
+ from_graph(graph: Graph, files: list[str] | None = None): SavedGraph
+ from_document(document: dict, source: str = ''): SavedGraph
+ from_text(text: str, source: str = ''): SavedGraph
+ from_file(path: Path): SavedGraph
+ from_nodes(nodes: list[dict]): SavedGraph
+ from_violations(violations: list[Violation], overlays: list[str] | None = None): SavedGraph
+ of_practices(keys: list[str]): SavedGraph
+ merged_over(older: SavedGraph | None): SavedGraph
+ holds(practice_roots: dict[str, Path], overlays: list[str]): bool
+ violations(practices: list[str] | None = None): list[Violation]
---<<reads practices of>>--> Graph
---<<creates>>--> SavedPractice
---<<raises>>--> SavedGraphOutdated

## SavedPractice

One practice as the saved graph keeps it: the folder its source was read from, the facts about the practice as a whole, its nodes, its edges, and the violations its rules found.

+ SavedPractice(name: str, source_root: str, root_facts: dict, nodes: list[SavedNode], edges: list[SavedEdge], violations: list[Violation])
------
+ name: str
+ source_root: str
+ root_facts: dict
+ << composition >> nodes: list[SavedNode]
+ << composition >> edges: list[SavedEdge]
+ violations: list[Violation]
+ violations_by_node: dict[str, list[Violation]]
+ record: dict
----
+ from_practice(practice: PracticeGuidance, files: list[str] | None = None): SavedPractice
+ from_record(name: str, record: dict): SavedPractice
+ root_in(folder: Path | None): Path | None
---<<reads nodes and edges of>>--> PracticeNodes
---<<creates>>--> SavedNode
---<<creates>>--> Violation

## SavedNode

One node as the saved graph keeps it: what it is, where it sits in its file, its stage, and its facts.

+ SavedNode(node_id: str, name: str, type: str, practice: str, file: str, line: int, end_line: int, stage: str, facts: dict)
------
+ node_id: str
+ name: str
+ type: str
+ practice: str
+ file: str
+ line: int
+ end_line: int
+ stage: str
+ facts: dict
+ record: dict
----
+ from_record(record: dict): SavedNode

## SavedGraphOutdated : Exception

A saved graph in another shape than this code writes. Load the working copy again to replace it.

+ SavedGraphOutdated(source: str, version: object)
------
----

## RuleFixture

Spec support: fixture files written to a folder of their own and read by one practice, the way a live load reads a working copy, so a rule is checked on the nodes the practice really reads.

+ RuleFixture(practice_class: type, files: dict[str, str])
------
+ context: RuleCheckContext
----
+ read_only(paths: list[str]): None
+ hits(rule): list[str]
---<<creates>>--> Graph
---<<creates>>--> RuleCheckContext

## RulePair

Spec support: a rule's failing fixture and its repaired fixture; the rule must flag the first and pass the second.

+ RulePair(rule, faulty: RuleFixture, repaired: RuleFixture)
------
----
+ check(): None
---<<checks>>--> RuleFixture

## SchemaRuleRun

Spec support: one rule's findings over one practice's nodes, as the graph's own check records them when validate runs it.

+ SchemaRuleRun(rule, context: RuleCheckContext)
------
----
+ hits(): list[str]
+ node_hits(node): list[str]
---<<reads nodes through>>--> RuleCheckContext
