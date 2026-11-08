---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Knowledge Graph

**Sources / context:** `harness/graph/.context/module-context.md`, `harness/graph/.context/defects.md`; `graph.py`, `explorer.py`, `schema_rules.py`, `schema_edges.py`, `node_rules.py`, `graph_rules_collection.py`, `practice_rules_registry.py`, `guidance_prose_index.py`, `bound_node.py`, `skipped_folders.py`; the Graph app in `harness/graph/app/` (`App.tsx`, `filter/FilterView.tsx`, `graph/GraphView.tsx`, `graph/GraphClient.ts`, `graph/graph-api.ts`, `graph/query-progress.ts`, `source/SourceView.tsx`, `source/call-expansion.ts`, `source/violation-prompt.ts`, `overlay-labels.ts`, `server.ts`, `choose_folder.py`); the specs `app/app.test.tsx`, `app_smoke_spec.py`, `graph_spec.py`, `graph_json_spec.py`, `graph_view_spec.py`, `load_progress_spec.py`, `pattern_overlay_spec.py`, `rule_category_spec.py`, `schema_rules_spec.py`, `working_copy_scan_spec.py`, `bdd_invokes_spec.py`, `ce_rules_spec.py`, `ddd_rules_spec.py`, `stories_examples_spec.py`, `stories_rules_spec.py`, `story_scenario_count_spec.py`, `bdd_examples_spec.py`, `drawio_rules_spec.py`; callers `cdd_guidance/actions/validate/validate.py`, `validate_spec.py`, `checked_graph_spec.py`, `space/kanban/report.py`, `space/session/session.py`, `cdd_guidance/practices/bdd/bdd.md`, `cdd_guidance/practices/stories/story-realizations/SKILL.md`, `harness/mcp/mcp_server.py`.

**Evidence:** **Observed** means the code and specs do it today (name the file); **Inferred** means the code does it but no spec presses it; **Intended** means a source (such as defects.md) asks for it and the code does not do it yet (name the source).

---

# (E) Map Work Into Knowledge Graph
## (E) Load And Save Graph
### (S) Agent --> Load Working Copy Into Graph

Observed: `graph.load_working_copy` opens each practice on its source root in a repo folder and builds the explorer tree for every practice asked for (`graph.py` `Graph.load_working_copy`, `graph_spec.py` "loaded from the account credentials working copy").

### (S) Knowledge Graph --> Reuse Saved Graph

Observed: a load reads `.context/graph.json` instead of scanning when the saved graph already holds the requested practices on the same roots and nothing is newer than it, and it can load a subset of the saved practices (`graph_json_spec.py` "should load the saved json", "should load a subset of the saved practices").

### (S) Knowledge Graph --> Rebuild Graph After Source Or Rule Changes

Observed: a source file or a rule file (`rules.py`, `schema.yaml`, `rules.yaml`) newer than the saved graph makes the load scan the folder again (`graph.py` `_saved_graph_is_current`, `graph_json_spec.py` "should reload the folder", "should reload").

### (S) Person --> Force Graph Reload

Observed: the Force reload button at the top right of the Graph app rebuilds the graph from source even when the saved graph is current (`App.tsx`, `app.test.tsx` "should force a reload from the top right of the page", `graph_json_spec.py` "that is forced to reload").

### (S) Agent --> Load Only Edited Files

Observed: `graph.load_files` builds each practice from only the named files or folders as they are now, runs the rules on them, keeps edges to classes declared in other files, and leaves the saved graph alone (`graph.py` `Graph.load_files`, `working_copy_scan_spec.py` "limited to the edited files", `graph_spec.py` "loaded from only the edited files").

### (S) Knowledge Graph --> Skip Build And Cache Folders

Observed: a scan leaves out `node_modules`, `dist`, test-run output, caches, dot-folders, and the `_examples` and `fixtures` folders, but still reads `.examples` folders (`skipped_folders.py`, `working_copy_scan_spec.py` "over build and test-run output").

### (S) Knowledge Graph --> Report Load Progress

Observed: a load names the saved-graph check, each source file it reads, and each rule as it runs, so whoever called it can watch (`graph.py` `report_progress`, `PracticeNodes.check`, `load_progress_spec.py`).

### (S) Agent --> Save Graph To Context Folder

Observed: `graph.save_json` writes the serialized graph to the loaded folder's `.context/graph.json`, and every rebuild saves itself there (`graph.py` `Graph.save_json`, `graph_json_spec.py` "should save serialized json in the folder context").

### (S) Knowledge Graph --> Keep Other Practices When Saving

Observed: saving merges into the existing `graph.json`, so practices already saved that this load did not include stay in the file (`graph.py` `_merged_graph_document`, `graph_json_spec.py` "should keep other practices when saving a different load").

## (E) Build Practice Trees From Source
### (S) Knowledge Graph --> Read Modules Classes And Operations

Observed: Clean Engineering reads modules (folders with a module card), packages, classes, operations, properties and parameters, keeps each file's top-level functions in a `_module` class, and orders their groups under each node (`graph.py` `_record_clean`, `graph_spec.py` "with clean engineering", `working_copy_scan_spec.py` "over module cards").

### (S) Knowledge Graph --> Read Clean Engineering Model Documents

Inferred: the load reads each scoped folder's `.context/*-model.md` beside the code so members and interactions the model document names join the graph (`graph.py` `_record_clean_models`, described in `cdd_guidance/practices/bdd/bdd.md`).

### (S) Knowledge Graph --> Place DDD Building Blocks Under Aggregates

Observed: DDD reads bounded contexts from folders holding `.context/bounded-context.md` and places aggregates, entity roots, value objects and repositories under them by stereotype (`graph.py` `_record_ddd`, `graph_spec.py` "with domain-driven design").

### (S) Knowledge Graph --> Read Story Maps And Story Tests

Observed: Stories reads epics, sub-epics and stories from story map markdown and draw.io files, and scenarios, steps and examples from story tests, keeping each node's path and line (`graph.py` `_record_stories`, `graph_spec.py` "with stories", `working_copy_scan_spec.py` "limited to an edited story map markdown file", "limited to an edited Python story test").

### (S) Knowledge Graph --> Read BDD Spec Trees

Observed: BDD reads each spec file's describe tree into spec, description, context and observation nodes (`graph.py` `_record_bdd`, `graph_spec.py` "with behavior-driven development").

### (S) Knowledge Graph --> Link Steps And Observations To Operations

Observed: a story step and a BDD observation each get an `invokes` edge to the operations their code calls, with `invokedBy` back on the operation and setup calls of the enclosing context first (`graph.py` `_record_story_edges`, `_record_bdd_edges`, `graph_spec.py` "with a step that invokes an operation", `bdd_invokes_spec.py`).

### (S) Knowledge Graph --> Link Examples To Classes And Steps

Observed: an example that demonstrates a class, a then step that observes an example, and an example retrieved using a property each get their relationship edge in both directions (`schema_edges.py` `sync_schema_edges`, `graph_spec.py` "with an example that demonstrates a class", "with a then step that observes an example").

### (S) Knowledge Graph --> Place Story Nodes On Their Source Lines

Observed: scenarios and steps sit in source-line order, a step opens on the call holding its label, a scenario runs through its closing brace, and an imported example sits in its examples file (`graph.py` `Node._edges_in_source_order`, `Source.align_to_label`, `align_to_example_export`, `graph_spec.py` "a scenario", "a step", "an example a story test imports"); `defects.md` still lists scenario and step order under Not fixed.

### (S) Knowledge Graph --> Give Each Node Its Fidelity

Observed: each node knows the fidelity its practice's schema creates it at and every higher fidelity it belongs to (`graph.py` `Node.fidelities`, `graph_spec.py` "a node's fidelity").

## (E) Apply Pattern Overlays
### (S) Person --> Add Named Overlay From Catalog

Observed: the Graph app lists the pattern overlays under `cdd_guidance/patterns` that hold practices, such as Lern domain driven, and applying one rebuilds the graph (`FilterView.tsx`, `graph.py` `available_pattern_overlays`, `app.test.tsx` "should offer built-in overlay names from the catalog").

### (S) Person --> Add Overlay Folder

Observed: Add folder opens a folder dialog, `graph.overlay_of` resolves the chosen folder to the overlay root that holds `practices/`, and the app applies it (`GraphClient.ts` `chooseOverlayFolder`, `app.test.tsx` "should apply overlays through the api when a folder is chosen", `pattern_overlay_spec.py`).

### (S) Person --> Remove Overlay

Observed: the remove control on an applied overlay takes it off and the graph rebuilds without it (`App.tsx` `removeOverlay`, `app.test.tsx` "should remove an overlay when its remove control is clicked").

### (S) Agent --> Rebuild Graph With Overlay Nodes

Observed: `graph.set_overlays` applies the overlays, reloads the open folder, and adds the overlay's node types, such as LERN node roots, client roots, routes and views parented on their aggregate (`graph.py` `Graph.set_overlays`, `working_copy.py` `_record_lern`, `pattern_overlay_spec.py` "should add the lern nodes when that overlay is applied").

### (S) Graph App --> Remember Applied Overlays

Inferred: the app stores the applied overlays in browser storage and sends them with the next load (`App.tsx` `LAST_OVERLAYS`, `readSavedOverlays`).

## (E) Explore Graph In Graph App
### (S) Person --> Choose Repo Folder

Observed: the Repo folder button opens a folder dialog on the server's machine, or the person types a path, and the app loads every practice on that folder and shows its classes (`App.tsx` `browse`, `choose_folder.py`, `app.test.tsx` "should put the chosen folder on the page and show its classes").

### (S) Graph App --> Reopen Last Folder

Observed: the app reloads the last loaded folder when it opens (`App.tsx` `cdd-graph-folder`, `app.test.tsx` "should reload the last folder when the app opens", `defects.md`).

### (S) Person --> Expand Practice Tree

Observed: each practice starts collapsed and the person opens nodes one level at a time, such as a customer aggregate with its entity, repository and value objects (`GraphView.tsx` `TreeNode`, `app.test.tsx` "should leave every practice collapsed until it is opened", `defects.md`).

### (S) Person --> Follow Relationships Under Node

Observed: a node shows its relationship groups as children, such as every invoke under an operation and invokes, observes and demonstrates on a step, and a module copy shown under a class appears without its own children (`graph.py` `Node.serialize`, `app.test.tsx` "should list every invoke under an operation", "should show invokes, observes, and demonstrates on a step", "should show a module without its children and a class with its module").

### (S) Person --> Open Node Source

Observed: selecting a node shows its file, lines and text in a read-only editor, numbered from the file's own lines (`graph.py` `Graph.source`, `SourceView.tsx`, `app.test.tsx` "should number a step from its line in the file", `app_smoke_spec.py` "with an operation opened").

### (S) Person --> Unfold Calls And Classes In Source

Observed: calls, classes and blocks in the source fold and unfold in place, opening the called operation or the class of a typed variable under the line, and stories, scenarios and steps fold the same way (`source/call-expansion.ts` `inlineCallLayout`, `app.test.tsx` "should fold calls, classes, and blocks in the source", "should fold a story, a scenario, and a step the way a class folds", `defects.md`).

### (S) Graph App --> Show Load Steps While Loading

Observed: while a load runs the app polls `/cdd/progress` and shows the current step, elapsed time, a meter and a log of steps (`App.tsx`, `GraphView.tsx`, `graph/query-progress.ts`, `app.test.tsx` "should show each load step while the graph is loading").

### (S) Person --> Copy Load Failure For Agent

Observed: a failed call shows the server's diagnosis and traceback instead of loading forever, with a Copy for AI button (`server.ts` `diagnosis`, `GraphView.tsx`, `app.test.tsx` "should show the backend traceback instead of loading forever").

### (S) Person --> Switch Display Theme

Inferred: the Executive and Engineering buttons switch the page and editor between light and dark themes and remember the choice (`App.tsx` `applyTheme`, `main.tsx`).

## (E) Filter Graph In Graph App
### (S) Person --> Filter By Practice

Observed: choosing practices selects every node type, connector and rule those practices hold, and adding another practice keeps the first practice's choices (`App.tsx` `practiceSelection`, `app.test.tsx` "should select every node, connector, and rule for the practice", "should keep the first practice filters when another practice is added").

### (S) Person --> Filter By Node Type

Observed: choosing node types keeps only those nodes in the tree and narrows the connectors and rules offered to the ones those types carry (`App.tsx` `applyFilter`, `graph.py` `Graph.filter_choices`, `app.test.tsx` "should keep the selected node type and drop the other class", `graph_spec.py` "with operations selected").

### (S) Person --> Filter By Connector

Observed: choosing a connector keeps the nodes that sit on that kind of edge (`graph.py` `Filter._on_relationship`, `graph_view_spec.py` "should return the nodes on the selected edge").

### (S) Person --> Show Only Violations

Observed: the Violations switch sends `violations: true`, and the tree keeps only failing nodes with their violations attached (`FilterView.tsx`, `filter/filter-selection.ts`, `app.test.tsx` "should send violations when the switch is turned on", "should keep the violation attached when violations are filtered", `defects.md`).

### (S) Person --> Filter Violations By Rule

Observed: with violations on, the chosen rules decide which failures count, so a node that passes the chosen rule is left out (`graph.py` `Filter._fails_selected_rule`, `graph_spec.py` "with violations of the parameter rule").

### (S) Person --> Select All Or No Filter Choices

Inferred: each filter list has All and None buttons that choose every option or clear the list (`FilterView.tsx` `FilterSelect`).

## (E) Find Nodes For Agent
### (S) Agent --> Return Matching Nodes With Relationships

Observed: `graph.return_nodes` (the read-graph skill) returns each node matching practice, type, name, relationship and source path with its practice, ancestors, children and rules (`graph.py` `Graph.return_nodes`, `explorer.py` `FilteredNode`, `app_smoke_spec.py` "with operations selected", `working_copy_scan_spec.py` "should keep only nodes under the given path").

### (S) Agent --> Return Only Failing Nodes And Rules

Observed: `violations: true` returns only nodes that fail a rule, each with only its failing rule entries and their hits (`graph.py` `Node.rule_rows`, `working_copy_scan_spec.py` "returning violations", `rule_category_spec.py`).

### (S) Agent --> List Practice Inventory

Observed: `graph.inventory` returns each loaded practice's node counts, edge count, node types, edge kinds, rules and explorer tree, with the overlays applied and available, and the app shows the same counts (`graph.py` `Graph.inventory`, `app_smoke_spec.py` "should count the same nodes as the graph").

### (S) Agent --> List Filter Choices

Observed: `graph.filter_choices` returns the node types, relationships and rules a filter offers once practices and node types are chosen, and clears the graph's own filter (`graph.py` `Graph.filter_choices`, `app_smoke_spec.py` "with clean engineering chosen in the filter").

### (S) Agent --> Read Node Source With Members

Observed: `graph.source` returns a node's file, lines and text with every class, operation and property the graph holds so calls in it can be opened, and nothing for an id with no node such as a rule entry (`graph.py` `Graph.source`, `explorer.py` `NodeSource`, `app_smoke_spec.py` "with an id the graph holds no node for").

## (E) Check Nodes Against Graph Rules
### (S) Knowledge Graph --> Attach Schema Rules To Nodes

Observed: each node gets the rules its practice's `schema.yaml` lists for its type, with the rule's prose and whether it has an executable check (`node_rules.py`, `schema_rules.py` `slugs_for_type`, `schema_rules_spec.py` "schema rules on a node", `rule_category_spec.py`).

### (S) Knowledge Graph --> Check Nodes Against Practice Rules

Observed: each practice's rule checks run on its loaded nodes and record violations, for example Clean Engineering operation size and module depth, DDD stereotypes and repositories, Stories verb-noun names and child counts, BDD spec shape, and draw.io class titles (`rules.py` `attach_rules`, `practice_rules_registry.py`, `ce_rules_spec.py`, `ddd_rules_spec.py`, `stories_examples_spec.py`, `story_scenario_count_spec.py`, `bdd_examples_spec.py`, `drawio_rules_spec.py`).

### (S) Knowledge Graph --> Inherit Clean Engineering Rules On DDD Types

Observed: DDD types that extend a Clean Engineering type, such as an entity on a class or a bounded context on a module, carry that type's rules too (`schema_rules.py` `ce_anchor_type`, `schema_rules_spec.py` "DDD schema extends clean engineering").

### (S) Knowledge Graph --> Add Overlay Rules

Observed: an applied pattern overlay adds its own rules to the node types it names, such as LERN tier rules on a node root (`practice_rules_registry.py` `pattern_rules_for_practice`, `schema_rules_spec.py` "LERN overlay rules").

### (S) Knowledge Graph --> Mark Prose Rules As Prompts

Observed: a rule with no executable check shows as a prompt rather than passing or violating (`graph.py` `Node.rule_rows`, `graph_spec.py` "should leave do-not-invent-requirements prompt", `stories_examples_spec.py` "vocabulary-traces-to-domain-source").

### (S) Knowledge Graph --> Place Violation At Node Lines

Observed: each recorded violation keeps the file and lines of the node it was found on (`graph_rules_collection.py` `GraphRule.record`, `schema_rules_spec.py` "should place a recorded violation at the node's source", `graph_spec.py` "should store the epic child-count hit on the line that names the epic").

### (S) Knowledge Graph --> Name Rules By Practice Node And Rule

Observed: every rule is labelled `practice.node.rule`, with the owning pattern in front for an overlay rule (`schema_rules.py` `qualified_rule_label`, `schema_rules_spec.py` "a rule label", `app.test.tsx` "should list rules as practice, node, then rule").

## (E) Review Violations In Graph App
### (S) Person --> See Rules Under Node

Observed: each node has a rules entry listing its passing, violating and prompt rules, and a violating node is marked in the tree (`graph.py` `Node.rule_category`, `GraphView.tsx`, `app.test.tsx` "should show a passing rule and a violating rule under the operation").

### (S) Person --> Hover Violating Rule For Message

Observed: hovering a violating rule shows its violation messages (`GraphView.tsx` `violationHint`, `app.test.tsx` "should expose the violation message when hovering a violating rule").

### (S) Person --> Open Violation In Source

Observed: selecting a violating rule opens the node's source with a banner naming the rule and message and highlights the lines the hit names (`SourceView.tsx`, `graph/graph-selection.ts` `selectionForRule`, `app.test.tsx` "should show the violation banner, highlight the source").

### (S) Person --> Copy Correct Prompt

Observed: the Correct button copies a prompt holding the node, file and lines, rule, code excerpt and violation, asking for a test-driven fix (`source/violation-prompt.ts`, `app.test.tsx` "should build a Correct prompt with the rule, excerpt, and violation message").

## (E) Report Graph Rules In Validate
### (S) Validate --> Build Graph From Edited Files

Observed: Validate given edited paths loads every graph practice from just those files and writes `edited-graph.json` beside the session, without touching the workspace graph (`validate.py` `_edited_graph_json`, `validate_spec.py` "should write the edited graph beside the session", "should not write the workspace graph").

### (S) Validate --> Report Own Practice Violations

Observed: the graph-rule report lists only the violations of the guidance's own practice, at each node's path and line, alongside the AI-judged rules (`validate.py` `_graph_and_ai_rule_report`, `validate_spec.py` "should report only the violations of the guidance's own practice", "should append a graph-rule report from summary JSON and still include AI rules").

### (S) Validate --> Report Saved Graph Hits

Observed: with `graph: true` or a graph path, Validate reads the hits from the saved `graph.json` or `graph_return_nodes` JSON (`validate.py` `_resolve_graph_json_paths`, `validate_spec.py` "with the saved graph", `checked_graph_spec.py` "that was named a saved graph document").

### (S) Validate --> Leave Unedited Files Out

Observed: hits in files outside the named paths stay out of the report (`validate_spec.py` "should leave files outside the edited paths out of the report").

### (S) Validate --> Refuse Missing Path

Observed: a named path that is not there, or not under the session's root, is refused with the path and the root it was read from, so no graph is built from nothing (`validate.py`, `validate_spec.py` "should refuse, naming the path and the root it was read from").

### (S) Validate --> Save Checked Graph Beside Report

Observed: the graph a validation checked is saved beside its report under the same name, keeping the rule hits on their nodes and leaving earlier reports' graphs as they were (`validate.py` `_save_reports`, `validate_spec.py` "should save the graph it checked beside the report, under the same name").

### (S) Session Board --> Count Graph Hits From Report

Observed: the session board reads the graph saved beside a validation report and counts its rule hits, so a fidelity with graph-rule violations still needs Validate (`harness/kanban/report.py` `ReportFile.report`, `validate_fidelity_story.test.py` "Count Validate done only with no graph-rule violations").

---

## Scope boundary

**In scope:** building the knowledge graph from a working copy or edited files for Clean Engineering, DDD, Stories and BDD; reusing, rebuilding and saving `.context/graph.json`; pattern overlays; browsing, filtering and reading source and violations in the Graph app; the `graph.*` MCP tools the agent calls; running graph rules on nodes; and how Validate and the session board report the graph's rule hits.

**Out of scope:** the content of each practice's individual rules and parsers (owned by `cdd_guidance/practices/*`), UX map and screen nodes (the load offers the types but reads no UX source), rendering a BDD realization from a saved graph (the Render action), the AI-judged half of Validate, and the CDD MCP server and web domain access adapter the app reaches the graph through.
