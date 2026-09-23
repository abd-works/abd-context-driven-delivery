# Knowledge graph — grill answers

## Package location

**Q:** Where should the navigable graph types live, given harness must not import practices?

**A:** Put `knowledge_graph` under `practices/` so it can subclass the existing Clean Engineering and Stories nodes (`OoadNode`, `Module`, `OoadClass`, `Epic`, `SubEpic`, `Story`) directly. Not under `harness/`.

Grounded in `practices/clean_engineering/model/base_class_model.py`, `practices/stories/model/nodes.py`, `harness/.context/module-context.md`.

## First increment scope

**Q:** What populates increment 1 so Paradise navigation tests can be real?

**A:** A subset of My Paradise onboard: **Create Customer** and **Get Number**, plus the supporting Clean Engineering / DDD types those stories use. Later, a complete semantic model we can test against.

Not the full onboard epic (11 child epics on `stories/story-map.md`). Increment 1 child epics are `create-customer` and `get-number` only.

Grounded in `stories/onboard-a-customer/create-customer/`, `stories/onboard-a-customer/get-number/`, `domain/customer/Customer.ts` (`CustomerRepository.create` / `load`).

## Module is not a repository owner

**Correction:** `Module` does not have a `repository`. DDD adds two **Module** subtypes: **Bounded Context** (language boundary) and **Aggregate** (consistency cluster). An Aggregate must have a known **root** Entity. **Repository** is a **Class** that lives in the Aggregate when that root has an independent collection lifecycle — not a field on Module.

**Class subtypes:** Entity (identity that outlives attributes), Entity Root (Entity that is the Aggregate’s only entry — same identity rule; `aggregate` link is the only difference), Value Object, Repository, Domain Event, Domain Service.

## Cross-module class dependencies

**A:** `Property — hasType — Class`, `Parameter — hasType — Class`, `Operation — returns — Class`, and `Operation — invokes — Operation` are first-class edges. Emit `Class — dependsOn — Class` when any of those reach a Class in another Module; roll up to Module. Same-module refs use `Class — associates — Class`. CodeQL populates types, params, returns, and call graph.

## Practice graph, not parallel guidelines

**A:** One `PracticeGraph`; every node is a `GraphNode` and a practice instance. Every edge is a `GraphRelationship` with explicit **from**, **kind**, and **to** — e.g. `Step — invokes — Operation`, not a one-sided field on Step alone. `usedBy` is the reverse index on `GraphNode`.

Grounded in `practices/ddd/guidance/building_blocks.md`, `practices/ddd/templates/ddd-sketch.md`, `domain/bounded-context-map.md` (`Customer` BC holds Customer, Cart, …; `Inventory` holds Porting).

## Story and BDD depth

**Correction:** The graph includes the Stories tree below Story: **Scenario**, **Background**, **Step** (existing `Clause`), **Example**. BDD has its own tree: **Description** (`describe`), **Context** (`that` / `with`), **Observation** (`it should`). The important work is the edges that join Stories, CE, DDD, and BDD — not four disconnected trees.

Grounded in `practices/stories/model/scenario.py`, `practices/bdd/bdd.md`, `gwt-steps-trace-to-domain-operations`.

## Guidance rules on graph nodes

**Q:** How do practice guidance rules attach to the unified graph?

**A:** Every node is subject to rules **directly** (rule `applies_to` matches the node type at a fidelity) or **through a parent** (inherited scope). Each practice has **shared rules** plus **fidelity-specific rules**; fidelity narrows which node types are in scope — e.g. `scenarios` → Scenario/Step/Example; `acceptance_tests` → Step with `Step — invokes — Operation`; `building_blocks` → Repository/Entity with DDD edges.

**Query surface (sketch):** `node.rules.violations` (all applicable); `node.rules.direct.violations` (closest practice+fidelity match); `node.rules.practice(p).fidelity(f).violations` (filtered).

**Evaluation:** Rules are graph/CodeQL predicates over the loaded practice graph — not per-file scanner re-parses. CodeQL supplies calls/mutations; the graph supplies practice identity and cross-practice edges. See `knowledge-graph-sketch.md` § Guidance rules on nodes.
### Explorer shape from backlog

The explorer shows one KnowledgeGraph that contains several PracticeGraphs. Each PracticeGraph is a tree of root Node → sub Node with property:value on the node and Relationship (connector) lines to other nodes, including across PracticeGraphs. Filters are connector kind, practice, and node. Grounded in backlog.txt lines 9–35, module-context.md (PracticeGraph seam, node.rules.violations), and graph_node.py Kind / Relationship.

## Rules are a Node property, not a second tree

Do not use two trees or a Nodes vs Rules overlay. There is one KnowledgeGraph tree of PracticeGraphs and Nodes. For every Node that can have rules, rules is a property on that Node. Selecting rules shows the complete list appropriate to that Node; each rule is passing or violating.

## Explorer layout: filters top-left, tree left, source right

Filters sit in a thin strip at the top left — they do not own a column. The left body is the PracticeGraph tree. The right pane is the Node's source file. Selecting a file Node opens that file and highlights the Node's range. Selecting a folder Node leaves the right pane unchanged. Grounded in RuleViolation.location / line (graph_rules.py) and CodeQL populate file facts.

## Filters include violations and a specific rule

The filter strip includes practice, connector kind, node, violations, and rule. Violations shows only Nodes whose rules are failing. Rule shows only Nodes that have that named rule. Same Filter Graph mechanic as the other knobs — not a second tree. The story map and main scenarios live in knowledge-graph-explorer-sketch.md with the screen sketch.

## Cross-aggregate sync

single-aggregate. KnowledgeGraph is the aggregate root. PracticeGraph, Node, Relationship, and rules live inside that root's snapshot. One lowdb file `data/knowledge-graphs.json`.

## Given seeds passing and failing source

A KnowledgeGraph is loaded from source that passes a named rule and source that fails that rule. Given names those two Nodes. Then names the passing listing and the violating listing. Do not write "each rule is passing or violating" — that restates the property without seeding the code.

## File change: async graph check, not glob inject

**Q:** How should a changed file get graph rule hits without blocking Cursor, and without a second RulesCollection?

**A:** Do not hang a second bag on the practice. `RulesCollection` has no graph knowledge. At guidance load, parse markdown as `RulesCollection.from_markdown`, then **promote** to `GraphRulesCollection` (subtype) when any rule slug has `practices/{practice}/model/codeql/{slug}.ql`. Mixed bags: put `GraphRule` (subtype of `Rule`) in the entries for slugs that have a query; leave markdown-only as `Rule`. `RuleRegistry` as a flat second catalog goes away.

**Inject stays on the supertype.** `GraphRulesCollection` inherits `inject_rules` / `matches` (globs). Do not override applicability with classify yet — that path is untested. Later, override `matches` so even vanilla inject can use graph matching. `HookInstallation` still skips collection hosts (`isinstance` RulesCollection covers the subtype).

**Classify with CodeQL, not `AppliesTo.globs`.** `PracticeGraph.classify` calls `CodeQL.populate` — the same query list and `model.qll` predicates (`storyCall`, `scenarioCall`, `inSubject`). Filter populate rows by the changed path. `FIDELITY_NODE_SCOPE` then picks which GraphRules to run. Do not invent a path-glob matcher for graph *validate* scope.

**One verb, one shape: `validate`.** `Rule.validate()` is instruction text. `GraphRule.validate()` is the same signature (no graph/rows args — graph is parent) and runs CodeQL, writes `node.rules.violations`, returns `str`. Callers do not branch: `rule.validate()`. `@collect` on `RulesCollection.validate` already walks entries, so `GraphRulesCollection` does not need its own evaluate/validate API — the inherited collect calls the override. Do not add `evaluate` on `GraphRule`, the collection, or `PracticeGraph`. On file change (and on `/turn`), classify the path, then `rules.validate`. Do not run CodeQL inside the Cursor hook process (30s timeout).

**Sync hook.** One enrolled `@Hook` on `PracticeGraph` (same install pattern as inject: not one handler per rules bag). Reads the **last** evaluation for that file. If there are `RuleViolation`s whose `location` is the path, return `additional_context` with a count and the **report path** so the agent can `Read` it. Empty when the file has no hits. User says what to do next.

Grounded in `Rule.validate`, `RulesCollection.validate`, `RulesCollection.inject_rules`, `HookInstallation` skip of collection hosts, `stories.ql` / `scenarios.ql`, `CodeQL.populate`, `GraphRule.validate`, `RuleViolation.location`.

### Overlay roles stay on CodeQL

Overlay-base and overlay are two jobs of CodeQL.ensure_database, not a second type family. Overlay-base is the golden `.codeql/{language}-db` (rebuild with --overlay-base when promoting). Overlay is a disposable copy `.codeql/{language}-overlay` used for dirty-file extract plus rules.ql. Do not add OverlayManager or OverlayDatabase. Grounded in codeql.py ensure_database and the overlay recap.

### include_edits toggle, default on

Both file-change validate and the hierarchy report share one CodeQL property: include_edits, default on. When on, they extract overlay (copy of overlay-base + dirty files) then run populate/rules.ql. When off, they use overlay-base read-only. Promote still rebuilds overlay-base. Grounded in codeql.py ensure_database callers and the overlay sketch increment.

### Validate walks Guidance, collection walks rules

Validate.validate iterates Guidance via GuidanceAction.run, not the rule catalog. No rule means item.rules.validate (@collect). A passed Rule is that object once; guidance is the practice binding (workspace, inject, session), not a slug lookup. GraphRulesCollection stays on this same seam. Graph hits are one CodeQL batch (combined rules.ql), not N GraphRule.validate query runs; markdown Rules still collect as instruction text. Grounded in actions/validate/validate.py and the prior hook/file-change grill.

### Overlay is born with overlay-base

Overlay is created once with overlay-base, not on every file edit. Promote rebuilds golden `.codeql/{language}-db` and at the same time creates `.codeql/{language}-overlay`. While hacking, extract the current dirty set onto that standing overlay (`include_edits`). Recopy only when promoting a new golden (or the overlay is stale/corrupt). Grounded in user correction of the overlay recap.

### Classify returns nodes, not a rule plan

Classify belongs on PracticeGraph. It returns nodes (what these files are), via CodeQL.populate — the existing fact-query batch, not a classify.ql and not a rule list. Which rules run is GraphRule.applies_to / FIDELITY_NODE_SCOPE after those nodes exist. Mixed edits (BDD tests + production code) are one classify of the dirty set, then each practice's GraphRulesCollection.validate. Grounded in codeql.py populate, graph_rules.py FIDELITY_NODE_SCOPE, and the file-change sketch.

### Classify filters the held KnowledgeGraph

The in-memory aggregate is KnowledgeGraph (already the explorer root; filterGraph already returns KnowledgeGraph). Classify is a method on that instance: same PracticeGraphs, same node.rules, same hierarchy, filtered to the changed files. Callers then validate from what is in that slice — they do not get a rule plan from classify, and they do not get a flat node list. Populate still refreshes the full instance from CodeQL; classify only filters. Grounded in knowledge-graph.ts KnowledgeGraph.filterGraph and the explorer grill (KnowledgeGraph aggregate).

### KnowledgeGraph.update is the seam

The public seam is KnowledgeGraph.update(files/folders/paths) on the dirty in-memory copy. Overlay extract, populate, and filtering stay under that call. After update, validate is the existing path — a filter with violations, not a second classify or a master classification query. Grounded in user correction of KnowledgeGraph.classify.

### Populate is the same; extract and database differ

Populate is one method either way: the same fact queries (classes, operations, stories, …) applied onto the KnowledgeGraph. KnowledgeGraph.update extracts dirty paths onto the standing overlay, then populate. Promote extracts the full tree into overlay-base (and creates overlay), then the same populate. Do not add a second integrate/classify populate. Grounded in codeql.py populate and the overlay vs update seams.

### updateWorkingCopy and refreshMaster on KnowledgeGraph

KnowledgeGraph has two operations, not one populate that switches: updateWorkingCopy(paths) for the dirty/working overlay, refreshMaster for a new golden overlay-base plus overlay. CodeQL.populate stays under both; it is not the public seam. Grounded in user naming of updateWorkingCopy and refreshMaster.

### KG reads overlay; only refreshMaster rewrites master

KnowledgeGraph always reads the overlay copy. Only refreshMaster rewrites overlay-base (master) and then copies it to overlay. updateWorkingCopy extracts onto that overlay and never writes master. Grounded in user correction of the two KnowledgeGraph methods.

### Master and working-copy database names

Domain names are master and working copy. Folders are `.codeql/{language}-master` and `.codeql/{language}-working-copy` — CodeQL accepts any database path. CLI still uses `--overlay-base` on master create and overlay-changes extract on the working copy. KnowledgeGraph always reads working copy. Only refreshMaster rewrites master then copies to working copy. Grounded in user rename of overlay/overlay-base.

### HookInstallation is the installer, not the graph

HookInstallation is harness/hooks, not a KnowledgeGraph type. At install it writes Cursor hooks.json so postToolUse runs marked operations. For this sketch it enrolls PracticeGraph.notice_changed_file once (read last hits) and Guidance.inject_rules once per practice. It skips inject_rules on RulesCollection and FidelityGuidance so those bags are not enrolled a second time. Grounded in hooks.py HookInstallation.write.

### CodeQL.populate takes master or working copy

CodeQL.populate is one operation with a database parameter: master or working copy. Same fact queries. KnowledgeGraph still never reads master; refreshMaster calls populate(master), then copies master to working copy. updateWorkingCopy calls populate(working copy). Do not add a second populate method on CodeQL. Grounded in user question on sketch populate vs master.

### File-change hook lives on GraphRulesCollection

The file-change hook is a @Hook method on GraphRulesCollection, same pattern as RulesCollection.inject_rules in rule.py. PracticeGuidance.rules and FidelityGuidance.rules return GraphRulesCollection. Entries are GraphRule when a .ql exists and Rule otherwise; GraphRule.validate defers to Rule.validate when there is no query. Do not sketch HookInstallation.write or PracticeGraph.notice_changed_file. Grounded in rule.py inject_rules and user correction.

### File-change hook is stop, not postToolUse

inject_rules stays @Hook("postToolUse") — one file, glob markdown. GraphRulesCollection file-change is @Hook("stop") — existing Cursor event when the turn ends. Change set is dirty paths vs master, not the hook payload path. afterAgentResponse fires per assistant message and can land before later edits. Grounded in Hook.EVENTS and hook_spec.py stop handlers.

### Stop updates and validates; a second hook presents the report

On agent-loop stop, GraphRulesCollection takes dirty paths vs master, KnowledgeGraph.updateWorkingCopy, then validate (CodeQL on the working copy). The outcome is the existing hierarchy report with prune_to_violations — only nodes that have hits, with the rule and message, same shape as write_practice_hierarchy. A second hook then feeds that report into the chat with instructions to present it so the user can navigate errors, recommend a fix per violation, and drop items that later validate clean. Reverses “read last evaluation only / no CodeQL on the hook.” Grounded in write_practice_hierarchy.py prune_to_violations and user correction of the file-change scenarios.

### Hook reads filtered KnowledgeGraph objects, not a report file

Better: no violations report file for the hook. Cursor hooks are a new process, so “in memory” means load the KnowledgeGraph (already persisted in knowledge-graphs.json after updateWorkingCopy + validate), then filterGraph to dirty paths and violations. Source of truth is node.rules.violations on those objects. The hook still has to project that slice to a string (additional_context / followup_message); do not make the agent Read a report_path. write_practice_hierarchy stays an optional dump, not the chat contract. Grounded in knowledge-graph.ts filterGraph and knowledge-graphs.json.

### HookServer holds the KnowledgeGraph objects

The KnowledgeGraph lives on HookServer, not in a report file and not reloaded from knowledge-graphs.json for each chat. notice_changed_file updates those objects (updateWorkingCopy, validate, filterGraph). present_violations reads the same objects and only then projects a string for Cursor stdout. Grounded in hook_server.py HookServer and user correction.

### KnowledgeGraph is an instance field on a long-lived HookServer

HookServer today does not hold a KnowledgeGraph: Cursor spawns python hook_server.py per event, run() reads stdin, prints JSON, exits. Catalog only. In-memory across stop and present needs the same long-lived process as codeql_query_daemon: spawn once, keep knowledge_graph as an instance field, stdin hook_server.py connects and mutates that field. Grounded in hook_server.py run() and codeql_query_daemon.ensure_query_server.

### Session in harness/session holds knowledge_graph

New type Session in harness/session. HookServer and McpServer each hold a session reference. Session.knowledge_graph is a lazy property: first get instantiates, setter replaces, reset() clears so the next get instantiates again. That field is the in-memory KnowledgeGraph — not a field on HookServer itself, not a report file. Do not reuse tools.workspace WorkSession or session_logs name slug. Grounded in user naming and mcp_server.py McpServer / hook_server.py HookServer.

### Session holds each PracticeGuidance

Session also holds the PracticeGuidance instances (one per practice), lazy like knowledge_graph. HookServer and McpServer read session.practices instead of AgentToolSet.load_toolsets on every event. reset() clears practices too so the next get instantiates again. Fidelities stay on those PracticeGuidance objects. Grounded in guidance.py PracticeGuidance, hook_server.py HandlerCatalog.load_toolsets, mcp_server.py load_toolsets.

### Persistent HookServer daemon holds Session

This work replaces one-shot python hook_server.py with a persistent HookServer (ensure/spawn like codeql_query_daemon). Cursor hooks.json still points at a short CLI that connects; Session lives on the daemon. Hook events and McpServer share that same Session in RAM. Do not accept two Sessions. Grounded in user correction and codeql_query_daemon.ensure_query_server.

### present_violations is stop followup_message

present_violations is @Hook("stop") on GraphRulesCollection, same event as notice_changed_file, after the objects are updated. Channel is followup_message (optional additional_context). Not afterAgentResponse — that fires before stop. Empty followup when the slice has no hits. Grounded in hook_server.py stop followup and Cursor stop output.

### Persistent hook daemon; two Sessions; stop followup_message

This work adds a persistent HookServer daemon; hook_server.py per Cursor event is the CLI client. That daemon holds one Session so hook runs share RAM. McpServer keeps a second Session for now — do not merge hook and MCP onto one object. present_violations is @Hook("stop") after notice_changed_file; Cursor channel is followup_message, not afterAgentResponse. Grounded in hook_server.py run() spawn-per-event, codeql_query_daemon ensure, and user lock.

### present_violations echoes a violations-count toast

present_violations is @echo and @Hook("stop"), same as inject_rules in rule.py. After the followup_message, PromptEcho.show_ide_toast reports that violations were found and the count. No toast when the slice is empty. Grounded in rule.py inject_rules @echo and PromptEcho.show_ide_toast.

