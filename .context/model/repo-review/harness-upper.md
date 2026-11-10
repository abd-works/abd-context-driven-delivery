# Relationship review, verified: harness-upper

Area: harness/guidance (with the stage list, the practice catalogue, and the action catalogue), harness/guidance_actions, harness/graph, harness/diagnostics (harness/health has already been merged into it: `ServerHealth` is now `harness/diagnostics/server_health.py`), harness/catalog_generator, harness/design_canvas, harness/chat.

Every entry below was checked by reading the code as it stands in this worktree on 2026-11-07. The relationships among `PracticeGraph`, `GraphPractice`, `GraphPractices`, and `GraphOverlay` belong to item 1 of `.context/repo-model-disconnected.md`, which is already decided (option A); they are listed as **item 1** and not judged again. Line numbers are today's.

Two shapes recur through this area and explain most of the W verdicts:

- **A file another object already holds is read again on every call.** `Markdown.from_label(owner, label)` locates and re-reads the owner's practice document on each call (harness/markdown/markdown.py:856-868), and `MarkdownText(path.read_text())` does the same by hand. The practice document belongs to the `PracticeGuidance`; it should hold its `Markdown` (composition 1) and every section reader should read that.
- **An object is looked up again by a name string instead of being held.** `fidelity.stage` is a string, so the catalog and the board look the column up with `STAGE_COLUMNS.of(stage)` / `STAGES.of(stage)`; a practice key is a string, so the catalog and the project approach look the practice up again with `PracticeCatalogue.practice(key)`; a format is a string, so guidance builds `Format(name)` eleven times. The fix each time is that the owner holds the object (a `FidelityGuidance` holds its `ApproachStage`, its `Format`; a `CatalogPractice` holds its `CatalogFidelity` objects).

## 1. Runtime relationships, verified

Verdict **R**: the two objects are independent and one asks the other to act. **W**: the shape is wrong. "changed from" names the earlier verdict where this pass overturns it; "new" marks a relationship the earlier files missed.

### harness/guidance

| from → to | interaction | file:line | verdict | changed from | reason; for W: owner, relationship, redesign |
|---|---|---|---|---|---|
| Guidance → Name | `Name(self.domain_slug or type(self).__name__).kebab` on every `slug` read | harness/guidance/guidance.py:75 | W | | The guidance's own identity passed into a spelling helper on each read. Owner Guidance, composition 1: hold a `Name` made once from its class or `domain_slug`, and `slug` reads `self.name.kebab`. |
| Guidance → Markdown | `Markdown.from_label(self, "overview" / "guidance")` re-locates and re-reads the practice document on every property read | guidance.py:104, :110 | W | | Owner Guidance (the practice document it is defined by), composition 1: hold the `Markdown` of its document once and read each labelled section from it. |
| Guidance → Hook | `Hook.disabled_on(rules.inject_rules)` | guidance.py:160 | R | | Reads an annotation an author typed. |
| GuidanceCollection → FidelityGuidance | `child(name)` builds one fidelity per `###` block | guidance.py:198 | R | W | `child` is the factory `MarkdownCollection.from_markdown` calls once per entry while it builds the collection (harness/markdown/markdown.py:766-776); the collection then holds them. This is composition 0..* made once, not a per-call build. |
| GuidanceCollection → ToolSetCollectionAnnotation | annotated `@toolset_collection` | guidance.py:183 | R | | Annotation. |
| PracticeGuidance → Name | `Name(fidelity).spellings` over the fidelity names in `project_rules`; `Name(...).snake` compare in `_skip_inactive_fidelity` | guidance.py:316, :679 | W | | Iterates fidelity name strings and respells them instead of the `FidelityGuidance` objects it holds. Owner FidelityGuidance (its own `Name`, composition 1); the practice iterates `self.fidelities` and asks each one. (`project_rules` itself is dead code, see section 2.) |
| PracticeGuidance → RulesCollection | `RulesCollection.from_markdown(path.read_text())` per project rules file | guidance.py:325 | W | | Reached only from the dead `project_rules`; if kept, owner ProjectRulesets (a folder's rules), composition 1 per folder. Recommended: delete with `project_rules` (section 2). |
| PracticeGuidance → ProjectRulesets | `ProjectRulesets(folder).folders_for(self.key)` per call, with a process-wide class dict cache `_found` | guidance.py:313; project_rules.py:22 | W | new | Built per call from the session's folder and kept in global state. Dead path (section 2): delete. |
| PracticeGuidance → Format | `Format(self.format).name`, `Format(child.default_format)`, `Format(format_name)`, `Format(request.format).is_code`, `Format(source or self.format)` (×2), `Format(source_format)` | guidance.py:359, :379, :508, :557, :571, :574, :589, :590, :650 | W | | The format is kept as a string and re-parsed at every use. Owner FidelityGuidance, composition 1: the current fidelity holds its `Format`; the practice reads `self.fidelities.current.format`. A render request carries a `Format`, not a string. |
| PracticeGuidance → format adapters (`_formats` entries) | `_format_adapter` imports the adapter module by `(module, attr)` string on every call; `_live_adapter` constructs a new adapter on every parse and render | guidance.py:506-519, :627-640 | W | new | The adapters are built per call from strings. Owner PracticeGuidance, composition 0..* (one adapter per format), made once on first use and kept by `Format`. |
| PracticeGuidance → Schema | `Schema(self.schema).fidelities()` re-reads `model/schema.yaml` and re-parses it per call | guidance.py:470, :476 | W | (cardinality) | Owner PracticeGuidance, composition **1** (not 0..*): hold `Schema.load(path)` once (the cached loader already exists, schema.py:56). `PracticeSchema` and `SchemaFields` in harness/graph read the same file a second and third way; they should read the practice's `Schema`. |
| PracticeGuidance → Markdown | `Markdown.from_label(self, "guidance")`, `(current, "guidance")`, and four labels in `scoped_markdown` | guidance.py:423, :426, :663 | W | | Same as Guidance → Markdown. |
| PracticeGuidance → MarkdownText | `MarkdownText(md_path.read_text()).fidelity_blocks()` re-reads the practice document | guidance.py:670 | W | | Owner PracticeGuidance's `Markdown` (composition 1): the held document answers its fidelity blocks. |
| PracticeGuidance → Guidance | `Guidance.instructions.fget(self)` | guidance.py:440 | — (not a relationship) | R | A call to its own base class's property, which is inheritance, not a runtime dependency between two objects. Drop from the runtime list. |
| PracticeGuidance → AgentToolSetAnnotation | `annotates(type(content))` | guidance.py:586 | R | | Annotation. |
| PracticeGuidance → Session | `work_in(session_output)` keeps `session_output.session`; reads `session.root`, `session.document_named` | guidance.py:388, :332, :525 | R | new | The session is handed in and held (association 1). |
| FidelityGuidance → Format | `Format(served.format).is_code`, `Format(first word).name` | guidance.py:798, :814 | W | | Owner FidelityGuidance, composition 1: hold a `Format` instead of a name string. |
| FidelityGuidance → PracticeCatalogue | `PracticeCatalogue.create("clean_engineering").fidelities[name]` builds a whole new Clean Engineering practice per fidelity that names a companion | guidance.py:836 | W | | Looks the companion up by two strings and builds a private practice for it. Owner the session's (or catalogue's) CleanEngineering practice: the fidelity holds an association 0..1 to the Clean Engineering `FidelityGuidance`, handed to it when its practice is built in the same session, so the session has one Clean Engineering practice. |
| FidelityGuidance → Name | `Name(first word).snake` in the `clean_engineering` setter; `Name(self.name).kebab` in `slug` | guidance.py:844, :850 | W | | Setter: part of the companion lookup above (goes with it). `slug`: owner FidelityGuidance, composition 1 (hold its `Name`). |
| FidelityGuidance → PracticeGuidance | `practice_guidance` walks `parent`; reads `slug`, `domain_markdown_path`, `schema_guide` | guidance.py:785-790, :849 | R | | The practice owns its fidelities (composition); the fidelity reads its owner. |
| FidelityGuidance → Markdown | `Markdown.from_label` for scaffold, practice guidance, templates (per format) | guidance.py:864, :896, :926 | W | | Same as Guidance → Markdown. |
| FidelityGuidance → MarkdownText | `MarkdownText(path.read_text()).fidelity_block(self.name)` in `section` | guidance.py:875 | W | | Re-reads the practice document. Owner PracticeGuidance's `Markdown`, composition 1. |
| FidelityGuidance → Rules | annotated `@rules` | guidance.py:878 | R | | Annotation. |
| FidelityGuidance → FidelitySessionOutput | `work_in` keeps it; `output_paths`, `files`, `reports_folder` | guidance.py:748-783 | R | new | Handed in by the session and held (association 0..1). |
| FidelityGuidance → FidelityWithoutSessionError | raises | guidance.py:777 | R | new | Named failure. |
| FidelityGuidance → ApproachStage | none: `stage` is a bare string, so every reader looks it up again (`STAGE_COLUMNS.of(fidelity.stage)`, `STAGES.of`, `child_for_stage(stage)`) | guidance.py:716, :190-195; catalog_generator.py:140, approach_page.py:291, project_approach.py:85, :144 | W | new (missing) | Owner FidelityGuidance, association 1 to the `ApproachStage` its `Stage:` field names, resolved once when the fidelity is read; readers ask `fidelity.approach_stage`. |
| Rule → Name | `Name(body).title_slug` when a bullet has no slug | rule.py:134 | R | W | Runs once inside the `from_bullet` factory and the slug is kept; a value made at creation, not rebuilt per call. |
| RulesCollection → MarkdownText | `MarkdownText(text).without_yaml` in `from_markdown` | rule.py:343 | R | W | The factory parses its own source text once while building the collection, which keeps the text (`collection.markdown`). |
| RulesCollection → Rule | `Rule.from_bullet` per bullet | rule.py:347 | R | W | The collection creates its rules once at construction and holds them: composition 0..*, which is the right shape. |
| RulesCollection → AppliesTo | `AppliesTo.from_markdown(text)` once; held as `_applies_to` | rule.py:341, :147 | R | new | Composition 1, made once. |
| AppliesTo → MarkdownText | `MarkdownText(text).yaml_fields` in its factory | rule.py:74 | R | new | Parses its source once. |
| RulesCollection → ToolCall | `ToolCall(payload.tool_input, payload.project).session` builds a call from the hook payload to find the session | rule.py:174 | W | (redesign) | The collection's own practice already holds its session (`self._owner_practice().session`, the field `work_in` sets). Owner PracticeGuidance (association 1 to Session): read the session there. Where no practice works in a session, the hook payload is the owner: `HookPayload` should expose the `ToolCall` it reports (association 1, built once by the hook server), not every hook handler faking one. The earlier "RulesCollection owns its ToolCall" is wrong: a ToolCall is not a part of a rules collection. |
| RulesCollection → HookPayload | `edited_path()`, `get(...)` | rule.py:158, :167 | R | | Handed in per hook. |
| RulesCollection → Hook | `Hook.disabled_on` | rule.py:163 | R | | Annotation. |
| ActionCatalogue → Action | `actions()` builds a new tuple of `Action(name, toolset)` on every call; `names()`, `has()`, `action()` each call it again | action_catalogue.py:184-202 | W | | Owner ActionCatalogue, composition 0..*: build the actions once (as `_toolsets` already is, :172-179) and keep them. (The class-level cache is global state; see section 2.) |
| ActionCatalogue → Name | `Name(folder).title_pascal` turns a folder name into the class name | action_catalogue.py:105 | R | W | Runs once per folder while the catalogue discovers its toolsets, and the result is cached in `_toolsets`. A naming convention applied at discovery, not a per-call rebuild. |
| ActionCatalogue → annotation_kinds | `publishes(InstallDestination.SKILL, member)` | action_catalogue.py:79 | R | new | Asks the annotation registry. |
| ActionCatalogue → InstallDestination | constant | action_catalogue.py:79 | R | | |
| PracticeCatalogue → PracticeGuidance | imports each practice class from a `module:Class` string and keeps one shared instance per key in the class dict `_shared`; `create` builds a fresh one | practice_catalogue.py:31-72 | R | new | It is the one registry of practices, and a registry that builds what it lists is right. Its class-level `_shared` instances are global state that every caller shares; see the redesign note on FidelityGuidance → PracticeCatalogue. |
| PracticeCatalogue → UnknownPractice | raises | practice_catalogue.py:70 | R | new | |
| StageColumn → ApproachStage | holds its stage | stage_columns.py:19 | R | new | Composition 1, made once at import. |

### harness/guidance_actions

| from → to | interaction | file:line | verdict | changed from | reason; for W: owner, relationship, redesign |
|---|---|---|---|---|---|
| GuidanceAction → ToolCall | `for_call(call)`: `call.arguments`, `call.session_named(named)`, `call.session` | guidance_actions.py:164-166 | R | | The call is handed in. |
| GuidanceAction → ToolCall | `inject_rules`: `ToolCall(payload.tool_input, payload.project)` built from the hook payload | guidance_actions.py:374 | W | (redesign) | Same as RulesCollection → ToolCall: owner HookPayload, association 1 (the payload exposes the call it reports, built once by the hook server). The earlier "GuidanceAction owns its ToolCall" is wrong. |
| GuidanceAction → GuidanceArgument | `GuidanceArgument(guidance)` built twice from the same raw argument: once in `for_call` for `session_named`, again in `_work_on` | guidance_actions.py:165, :216 | W | new | Owner GuidanceAction, composition 1: `_work_on` makes the argument once and keeps it; `for_call` reads `session_named` from it. |
| GuidanceArgument → PracticeCatalogue | `toolset_ref(text)` turns a slug a person typed into a toolset ref | guidance_actions.py:121 | R | new | A registry lookup of a name that arrives as text from outside. |
| GuidanceAction → AgentToolSet | `AgentToolSet.instantiate_all(items)` builds a new guidance object per listed ref, which the session's practice then adopts (`practice.guideline = item`) | guidance_actions.py:244, :273 | W | (redesign) | The session already holds its practices (`self._session.practice(key)`); building a second `PracticeGuidance` from a ref string and handing it to the first is a second object model. Owner Session, association 0..*: `listed()` resolves each ref to the session's own practice (and fidelity) and sets the fidelity and format on it. The earlier "GuidanceAction holds its AgentToolSet" does not describe a fix. |
| GuidanceAction → PracticeCatalogue | `PracticeCatalogue.has(item.key)` before `session.practice(item.key)` | guidance_actions.py:263 | W | | A second check of what the session holds. Owner Session: ask `session.practice(key)` alone, which answers none for a practice it does not hold. Goes away with the redesign above. |
| GuidanceAction → GuidanceAgentOperation | `_discover_operations` builds a new operation per member every time `operations` is read | guidance_actions.py:207; agent_tools.py:528-529 | W | | Owner GuidanceAction (via its AgentToolSet base, which has the same per-read build at agent_tools.py:561-565), composition 0..*: build the operations once per toolset instance. |
| GuidanceAction → Name | `Name(type(self).__name__).kebab` for the toast label | guidance_actions.py:378 | W | | Duplicates its own `slug` (used two lines later, :397). Read `self.slug`. |
| GuidanceAction → Session | held `_session`; `log.guidance_action`, `log.failure`, `practice(key)`, `document_named`, `path_named` | guidance_actions.py:152, :195, :200, :265, :302, :319 | R | new | Handed in at construction (association 1). |
| GuidanceAction → ActionWorksInNoSession | raises | guidance_actions.py:182 | R | | |
| GuidanceAction → AgentToolAnnotation | `annotates(member)` | guidance_actions.py:208 | R | | |
| GuidanceAction → HookPayload | `tool_input`, `project`, `tool_name` | guidance_actions.py:374, :395 | R | | Handed in per hook. |
| GuidanceAction → InstallDestination / annotation_kinds | `annotated_for(InstallDestination.MCP, member)` | guidance_actions.py:398 | R | | |
| GuidanceAction → Toast | annotated | guidance_actions.py:321, :368 | R | | |
| GuidanceAction → Guidance | `guidance.rules_after_edit(payload)` on each listed guidance | guidance_actions.py:386 | R | new | Asks the guidance it works on. |

### harness/graph (item-1 classes excluded)

| from → to | interaction | file:line | verdict | changed from | reason; for W: owner, relationship, redesign |
|---|---|---|---|---|---|
| Graph → PatternOverlays | `PatternOverlays(self.overlays)` built five times per load from the overlay strings, and `PatternOverlays()` twice more for `root_of` and `available` | graph.py:1052, :1080, :1112, :1242, :1253, :1270 | W | (cardinality) | Owner Graph, composition **1** (not 0..*): hold one `PatternOverlays` as its applied overlays in place of `self.overlays: list[str]`. Item 1's proposed shape (patterns as objects the session holds) replaces this; until then, hold it. |
| Graph → PracticeCatalogue | `practice_names` MCP tool returns `PracticeCatalogue.keys()` | graph.py:1264 | R | W | The tool answers "every practice the graph can load" by asking the one registry; there is nothing for the graph to hold. Under option A it reads the session's practices. |
| Graph → SavedGraph | `SavedGraph.from_graph(self)` in `write_json` and `save_json` | graph.py:1164, :1177 | R | W | A saved graph is a snapshot record of the graph at the moment it is written; making a new one per save is right. |
| Graph → SavedGraphFile | `_saved_file()` builds a `SavedGraphFile(self._folder, ...)` on every call | graph.py:1179-1180 | W | new | Owner Graph, composition 1: make it when the folder is set and keep it. |
| Graph → WorkingCopy | `WorkingCopy(self).fill()` | graph.py:1190-1192 | W | new | A doer class handed the graph to fill it. Owner Graph: the reading order and fill belong to the graph's load (under option A, each practice reads itself into the graph the graph aggregates). |
| Graph → PracticeChecks | `PracticeChecks(practice).run()` per practice per saved load | graph.py:1206-1210 | W | new | A doer built per practice from the practice's name (it re-finds the practice's `GraphPractice` by name, rules.py:18). Owner the practice (option A: `PracticeGuidance`), operation `check()` on the practice. |
| Graph → SchemaEdges | `SchemaEdges(self).sync()` per sync | graph.py:1218-1222 | W | new | A doer handed the graph. Owner Graph: the schema-edge sync is the graph's own operation, reading the relationship fields from each practice's `Schema` it aggregates. |
| Graph → Filter | holds `self.filter`; `filter_choices` builds a fresh offered `Filter(self)` as its answer | graph.py:1003, :1281 | R | new | Held part (composition 1); the offered filter is the tool's answer value. |
| Graph → Inventory / AppliedOverlays / GraphLoaded / GraphSaved / Overlay / NodeSource / FilteredNode | builds each as the answer of an MCP tool | graph.py:1069-1116, :1179, :1255-1257, :1270, :1291, :1306, :1336 | R | new | Answer values for the caller, published to TypeScript through the Graph's language adapter. |
| Graph → Node | `node.name`, `node.rules.chosen`, `node.children` | graph.py:1326-1332 | R | | |
| Graph → GraphFailure | raises | graph.py:1255 | R | new | |
| Graph → GraphPractices, PracticeGraph | | graph.py:1055, :1299 | item 1 | | |
| Node → Source | `place()` replaces `self.source` with a new `Source` at the declared lines | graph.py:640 | R | W | The node already holds its `Source` (composition 1, set in `__init__`, graph.py:553); `place` replaces the value when the node moves to its declaring lines. The earlier redesign ("hold `node.source`") describes what the code already does. |
| Node → GraphRulesCollection | `GraphRulesCollection.from_node(self)` once, cached in `_rules` | graph.py:604-607 | R | new | Composition 1, made once. |
| Node → ExplorerEntry | `serialize` builds the explorer entry | graph.py:694-714 | R | new | An answer value. |
| Node → Node | `_new_kind_node` makes a holder child once and keeps it in `children` | graph.py:653-660, :723 | R | new | |
| Node → PracticeGraph / GraphPractices | `practice.schema`, `edges_from`, `direct_parent`; `GraphPractices.named(practice.name)` | graph.py:600, :641, :666, :679 | item 1 | | |
| GraphRulesCollection → PracticeSchema | `PracticeSchema.load(node.practice.name, patterns)` per node | graph_rules_collection.py:107 | W | new | Looks the schema up again by the practice's name for every node, though the practice already answers `practice.schema` (graph.py:797). Owner the practice, composition 1 (its schema); the collection reads `node.practice.schema`. |
| GraphRulesCollection → GraphRule | builds one per schema rule of the node's type | graph_rules_collection.py:113 | R | new | Composition 0..*, made once per node. |
| GraphRule → Violation | `Violation.on_node(slug, message, node)` on `record`; kept in `_violations` | graph_rules_collection.py:76-78 | R | new | Composition 0..*: the rule on the node holds what it found. |
| PracticeChecks → RuleCheckContext | `RuleCheckContext(practice, source_root)` | rules.py:19 | W | new | A wrapper made to hand the practice's own edges to rules (`children`, `child_count` read `practice.edges`). Owner the practice: those queries are the practice's (or the node's) operations, and a rule is handed the practice. Absorbed by option A. |
| PracticeChecks → PracticeSchema / GraphPractices | `PracticeSchema.load(name, patterns)`, `GraphPractices.named(name)` | rules.py:18, :22, :55, :62 | W / item 1 | new | Lookups by the practice's name; goes with option A. |
| PracticeGraphRule → RuleCheckContext | `check(node, context)` | practice_rule.py:15 | R | | Handed in. Under option A the context becomes the practice itself. |
| WorkingCopy → PracticeSchema | `PracticeSchema.load(name, patterns)` per practice | working_copy.py:49 | W | new | Same as GraphRulesCollection → PracticeSchema. |
| WorkingCopy → EdgeType | `EdgeType(...)`, `EdgeType.from_kind` | working_copy.py:54 | R | new | Value factory. |
| PracticeSchema → Schema | `Schema.load(_PRACTICES_ROOT / practice / "model" / "schema.yaml")` and each overlay's `schema.yaml` / `rules.yaml` by path | schema_rules.py:124-132 | W | new | The second reader of the practice's schema file (PracticeGuidance builds a third, `SchemaFields` a fourth). Owner PracticeGuidance, composition 1: the practice holds its `Schema`; the pattern overlay holds its own. |
| PracticeSchema → PracticeCatalogue | `PracticeCatalogue.practice(self.practice).schema_node_fidelities()` and the rule prose of the practice named by string | schema_rules.py:111-113, :159-163 | W | new | Owner PracticeGuidance: PracticeSchema should be the practice's schema part (composition 1), so it reads its practice instead of finding it by name. |
| PracticeSchema → GraphPractices / GraphOverlay | `named`, `overlay(pattern).guidance()` | schema_rules.py:33, :75, :114, :174 | item 1 | | |
| SchemaEdges → SchemaFields | `SchemaFields.load()` (process cache) re-reads every practice and pattern `schema.yaml` by path, practices found through `PracticeCatalogue.keys()` | schema_edges.py:119-126, :225 | W | new | A fourth reader of the schema files. Owner each PracticeGuidance's `Schema` (composition 1): the relationship fields come from the schemas the graph's practices hold. |
| SchemaEdges → NodeEvidence | `NodeEvidence(owner)` built per match and per member node | schema_edges.py:176, :251, :275, :279 | W | new | A wrapper that reads a node's own source text (`mentions`, `calls`, `reads`, `module`). Owner Node (the model object): these are the node's operations; at most a part made once (composition 1). |
| SchemaEdges → EdgeType / PracticeGraph | `EdgeType.from_kind`, `practice.record` | schema_edges.py:245-248 | R / item 1 | new | |
| SchemaFields → SchemaField / SchemaKey | builds them while reading | schema_edges.py:145 | R | new | Parts made once by the factory. |
| ModelNode → Graph | `graph or Graph()`: a model object made without a graph builds a private one | model_node.py:86 | W | | Each top-level model object made without a graph silently gets its own. Owner the session's graph (or the practice the object is read into): association 1, required; the caller hands the graph. |
| ModelNode → Graph.practice | `graph.practice(type(self)._graph_practice)` by class string | model_node.py:87 | item 1 | | |
| ModelNode → Source | `Source(NO_SOURCE_FILE, order, order)` once in `__init__` | model_node.py:98 | R | | Composition 1. |
| ModelNode → Graph | `batch_schema_sync` → `self.graph.schema_sync_held()` | model_node.py:205 | R | (split) | Asks the graph it belongs to. |
| ModelChildren → ModelNode | `_link`, `_unlink`, `_refill` on the owner it holds | model_node.py:29-49 | R | | |
| ModelNode → ModelChildren | owns its child lists | model_node.py:91, :149-152 | R | | Composition. |
| ModelNode → ModelWithoutPractice | raises | model_node.py:85 | R | new | |
| SavedGraph → Graph | `restored_graph()` builds a `Graph()` and calls `graph.practice(name).restore(...)`, `restore_links(...)` | saved_graph.py:225-235 | W | (redesign) | It duplicates `Graph._load_saved` (graph.py:1197-1212) from the outside, reaching into the graph's practices. Owner Graph: a factory `Graph.from_saved(saved)` that reuses `_load_saved`; SavedGraph stays a record. The earlier "SavedGraph owns the Graph objects it makes (composition 0..*)" is the wrong fix. Only caller: cdd_guidance/practices/bdd/model/graph_bdd_model.py:32. |
| SavedGraph → SavedPractice → SavedNode / SavedEdge / Violation | records built from and into the graph's data | saved_graph.py:68-160 | R | new | Composition of a saved record. |
| Violation → SourceFile | annotated field | violation.py:117 | R | | |
| Violation → SourceLine | holds the source lines | violation.py:16-60 | R | new | Composition 0..*. |
| ClaudeDesignStoryModel → DesignCanvas | `canvas()` builds a `DesignCanvas` from the story model on each render | cdd_guidance/practices/ux/model/claude_design/story_canvas.py:177-179 | R | (was "should hold its canvas") | The canvas is the render output of the story model; a renderer builds its output each time it renders. Holding it would show a stale canvas after the model changes. |

### harness/diagnostics (with ServerHealth)

| from → to | interaction | file:line | verdict | changed from | reason; for W: owner, relationship, redesign |
|---|---|---|---|---|---|
| AgentToolsDiagnostics → ToolCall | `call or ToolCall()`; `for_call(call)` makes the diagnostics for each call | agent_tools_diagnostics.py:16-20 | R | W | The call is handed in by `for_call`, the MCP host's per-call protocol; the bare `ToolCall()` is only the empty call an instance listed for install holds. Nothing to change. |
| AgentToolsDiagnostics → Installer | `Installer(repo=self._call.project)` built per run to read what the project's install published | agent_tools_diagnostics.py:36 | W | | Builds the whole installer to read its diagnostics record and toolset list. Owner the project's install (reached through the call's `McpHost`/project), association 1: hand the probe the install record it reads. |
| AgentToolsDiagnostics → AgentToolsProbe | `AgentToolsProbe(installer, guidance, mcp_host, project).run()` per run | agent_tools_diagnostics.py:37 | R | W | A probe is one run with its own outcomes and temporary arguments; making a fresh one per diagnostics call is right. |
| AgentToolsProbe → McpHost | `McpHost.from_refs(...)` only when no host was handed in, then kept in `_mcp_host` | agent_tools_probe.py:71-78 | R | W | The host is handed in by the diagnostics call (`self._call.mcp_host`); the fallback is built once and held. Not a per-call lookup. |
| AgentToolsProbe → Installer | held; `diagnostics.installed_items`, `write_section`, `toolsets.collect` | agent_tools_probe.py:65, :80-91, :107 | R | new | Handed in. |
| AgentToolsProbe → ProbeArguments / ProbeSection / ProbeOutcome | builds per phase | agent_tools_probe.py:106-134 | R | new | Per-run working objects and results. |
| AgentToolsProbe → ProbeCallTimedOut | raises | agent_tools_probe.py:192 | R | new | |
| GuidanceDiagnostics → ToolCall | same as AgentToolsDiagnostics | guidance_diagnostics.py:16-20 | R | W | |
| GuidanceDiagnostics → Installer | `Installer(repo=...)` per run | guidance_diagnostics.py:36 | W | | Same owner and redesign as AgentToolsDiagnostics → Installer. |
| GuidanceDiagnostics → GuidanceProbe | `GuidanceProbe.from_filter(...)`, then `instructions()`, `actions()` | guidance_diagnostics.py:36-37 | R | W | One probe per run. |
| GuidanceProbe → PracticeCatalogue | `practice_named(slug)`, `toolset_ref(slug)` for slugs a person typed or MCP names the install published | guidance_probe.py:40-41, :82 | R | W | Registry lookups of names that arrive from outside; there is nothing to hold. |
| GuidanceProbe → AgentToolSet | `AgentToolSet.instantiate(ref)` for each installed ref | guidance_probe.py:86, :96-99 | R | W | Making each installed toolset from its published ref is what the probe exists to test. |
| GuidanceProbe → ProbeArguments | made once in `__init__`, held | guidance_probe.py:25 | R | new | Composition 1. |
| ProbeArguments → ToolCall | `ToolCall(project=self._temp_dir()).session` builds a call to open a session in a temp folder | probe_arguments.py:64 | W | new | Fakes a call to reach the session opener space/session registered with ToolCall. Owner ToolCall's registered session opener: expose it as its own operation (open the session for a project) so callers stop building calls they never send. |
| ProbeArguments → CddDiagnosticFixtures | made once, held | probe_arguments.py:24 | R | new | |
| ProbeArguments → _OperationParameters | per operation | probe_arguments.py:49 | R | new | Reads one operation's signature. |
| CddDiagnosticFixtures → WorkspaceFixtures (cdd-diagnostic package) | `WorkspaceFixtures(self.repo)` | cdd_diagnostic_bridge.py:35 | R | new | External package. |
| ServerHealth → HookDaemon | constructor takes a `hook_daemon`, or makes one for its project root | server_health.py:106-111 | R | W | The parameter exists, so it can be swapped. `HookDaemon` is the handle to an external process (the project's hook server), and `ServerHealth` is made per call for one project (`load(project)`), so building the handle for that project in its constructor is like building `Git(root)`. |

### harness/catalog_generator

| from → to | interaction | file:line | verdict | changed from | reason; for W: owner, relationship, redesign |
|---|---|---|---|---|---|
| Catalog → CatalogPractice | `CatalogPractice.load_all()` on first read, kept in `_practices` | catalog_generator.py:935-939 | R | W | Loaded once and held: aggregation 0..*. |
| Catalog → Utility / LifecycleAction / ApproachCopy | loaded on first read and held | catalog_generator.py:941-958 | R | new | Aggregation, held. |
| Catalog → GitCitation | made in `__init__`, held as `citation` | catalog_generator.py:903-904 | R | new | Composition 1. |
| Catalog → CatalogProject | `project` builds a `CatalogProject(self._project_folder)` on every read | catalog_generator.py:922-924 | W | new | Owner Catalog, composition 1: make it in `__init__`. |
| Catalog → Brand | `Brand()` in `__init__`, then `Brand(collection=self.brands_root)` again in `brands`, `generate_catalog`, `apply_brand`, `_render_catalog` | catalog_generator.py:908, :966, :983, :995, :1071 | W | new | Owner Catalog, composition 1: hold one `Brand` for its collection and ask it. |
| Catalog → HubBoard | `board` builds a new `HubBoard` per read | catalog_generator.py:961-962 | R | new | The board is rendered from held parts once per render (`_render_catalog` reads it once). |
| Catalog → CatalogPage | `CatalogPage(self.out_root).write(...)` per page written | catalog_generator.py:1065-1066 | W | new | A one-method file writer rebuilt per page from the catalog's own folder. Owner Catalog: writing a page under `out_root` is the catalog's operation (or hold one `CatalogPage`, composition 1). |
| Catalog → PracticePage / FidelityPage / ActionPage / UtilityPage / PageShell / MarkdownHtml / ApproachPage / PracticeExamples | builds each page as it renders | catalog_generator.py:1073-1210 | R | new | A renderer builds each page it writes. |
| Catalog → ProjectApproach | `ProjectApproach.for_project(...)` per call | catalog_generator.py:995-997 | R | new | Made for the project the call names. |
| CatalogPractice → PracticeCatalogue | `load_all` lists `PracticeCatalogue.practices()` | catalog_generator.py:84 | R | W | The catalog wraps every practice of the one registry, once (Catalog holds the result). |
| CatalogPractice → Name | `Name(practice_class.__name__)`, `Name(card["name"])` in `_card_of` | catalog_generator.py:90-91 | R | W | Runs once in the constructor; the card is kept. |
| CatalogPractice → MarkdownText | `shared_markdown` re-reads the practice guide from `domain_markdown_path()` and slices its `##` sections | catalog_generator.py:157-166 | W | (owner) | The practice document belongs to the PracticeGuidance, not to CatalogPractice. Owner PracticeGuidance's `Markdown` (composition 1): the practice answers its shared sections and CatalogPractice asks it. |
| CatalogPractice → PracticeGuidance | held `practice`; `key`, `fidelities`, `domain_markdown_path` | catalog_generator.py:76, :97, :137, :159 | R | | |
| CatalogPractice → FidelityGuidance | `stage`, `name` | catalog_generator.py:140, :152 | R | | |
| CatalogPractice → StageColumns | `STAGE_COLUMNS.of(fidelity.stage)` by string | catalog_generator.py:140 | W | new | See FidelityGuidance → ApproachStage: owner FidelityGuidance, association 1 to its stage; the column is found from the stage object. |
| CatalogPractice → SkillSlashName | held, default made once | catalog_generator.py:77 | R | new | |
| CatalogPractice → NoCatalog | annotation | catalog_generator.py:84, :137 | R | | |
| SkillSlashName → deployed SKILL.md files | reads the installer's output files back to learn a skill's slash name | catalog_generator.py:460-500 | W | new | Re-reads what the installer wrote. Owner the practice's `AgentTool` (its Skill annotation knows the skill name it installs as): association 1, ask it. |
| FidelityPage / ApproachGrids / CatalogPractice pages → CatalogFidelity | `CatalogFidelity(fidelity)` built at each use: `.opening`, `.label`, `.panel_example_files`, `.examples_html` | catalog_generator.py:590, :626, :638, :665; approach_page.py:301, :312, :328, :352 | W | new | The catalog's view of one fidelity is rebuilt at every read. Owner CatalogPractice, composition 0..* (one `CatalogFidelity` per shown fidelity, made once); pages read `catalog_practice.fidelities`. |
| ApproachGrids → PracticeCatalogue | `keys()` to order the practices; `practice("stories")` to find the Stories fidelity at a stage | approach_page.py:185-187, :327 | W | new | The grids are handed the catalog's practices, then look Stories up again by name. Owner Catalog (its CatalogPractice list, aggregation): order and find Stories among the practices it was handed. |
| ApproachGrids → StageExample / ExampleFile / RefineBoard / PrincipleBullets | builds them while rendering | approach_page.py:104-107, :230-252, :281-295, :409-438 | R | new | Render-time views of values it holds. |
| FidelityPage → FidelityTemplate | `FidelityTemplate(self.fidelity)` finds the template file by scoring file names, settings, stage, and folder | catalog_generator.py:680; :244-405 | W | new | A second way to find a fidelity's template; `FidelityGuidance._template` already reads it through `Markdown.from_label(practice, "templates", fidelity, format)` (guidance.py:921-929). Owner FidelityGuidance: the page asks the fidelity for its template file. |
| CatalogFidelity → BoardLabel / ExampleFile | builds the label and file views | catalog_examples.py:271, :324, :336 | R | new | Values. |
| PracticeExamples → practices folder | walks `cdd_guidance/practices/*/catalog-examples` by path to copy every practice's examples | catalog_examples.py:345-366 | W | new | A second way to find a practice's examples beside `CatalogFidelity.examples_folder`. Owner CatalogPractice (its CatalogFidelity objects know their examples folder): copy from the practices the catalog holds. |
| ExampleFile → DrawioDiagram / SourceFolds / ExampleMarkdown / MonacoViewer / MarkdownHtml | builds the view for its file | catalog_examples.py:81, :110-203 | R | new | Render-time views of the file it holds. |
| SourceFolds → _BraceScanner | per scan | source_folds.py:131-140 | R | new | Internal parser. |
| MarkdownHtml → _MarkdownReading | per render | markdown_html.py:42 | R | new | Internal parser. |
| Utility → RepositoryToolsets | `RepositoryToolsets(_REPO_ROOT).collect()` and imports each `module:Class` ref | catalog_generator.py:184-186 | R | new | Asks the installer's discovery once; the Catalog holds the result. |
| LifecycleAction → ActionCatalogue / Action / AgentToolSet | `ActionCatalogue.actions()`; builds its toolset once and keeps it; reads `toolset.tools` | catalog_generator.py:211, :226-229, :234 | R | new | |
| GitCitation → Git | `Git(root).run(...)` in `from_checkout` | catalog_generator.py:419-421 | R | new | External system. |
| ProjectApproach → CatalogPractice / Brand / ApproachCopy / ApproachPage / PageShell / CatalogPage | `generate` loads every practice again, builds a brand, reads the approach copy, and writes the page itself | project_approach.py:209-228 | W | new | It repeats `Catalog._write_approach_pages` outside the Catalog that already holds the practices, brand, and approach copy and calls it (`Catalog.generate_project_approach`). Owner Catalog, association 0..1 to the ProjectApproach it renders: the Catalog renders the project's approach page with its held parts; ProjectApproach holds only the project's title, repository, and examples. |
| ProjectApproach → ProjectFiles | `ProjectFiles(project_root)` built in `for_project` and again in `save_examples` | project_approach.py:176, :200 | W | new | Owner ProjectApproach, composition 1. |
| ProjectApproach → PracticeCatalogue | `PracticeCatalogue.keys()`, `has(practice)`, `practice(practice)` with the example's practice key string | project_approach.py:202, :246 | W | new | Its examples are keyed by `(practice key, stage)` strings (the `PracticeStage` pair), then the practice is looked up again by name. Owner FidelityGuidance: key the examples by the board fidelity they show. |
| ExampleClassifier → PracticeCatalogue / DeclaredFile | walks every practice's fidelities and turns each declared output into a regular expression to classify a file | project_approach.py:72-104 | W | new | A second implementation of the session's declared-file matching ("As in the session", project_approach.py:43). Owner FidelityGuidance (its declared outputs, through FidelitySessionOutput): the fidelity answers whether it declares a path. |
| ProjectFiles → GitCitation | `GitCitation.from_checkout(root)` | project_approach.py:151 | R | new | External system. |
| ApproachCopy → _ApproachMarkdown | `load` parses the approach markdown | approach_copy.py:55 | R | new | Factory. Note: `_ApproachMarkdown` is a hand-written `##` / `###` section reader beside harness/markdown's `MarkdownText` (`section_child_blocks`); reading through `MarkdownText` would keep one markdown reader. |
| _ApproachMarkdown → STAGES / StageScope / StageCopy / PrincipleCopy / Name | `STAGES.of(id)` for a CDD stage's scope, else a `StageScope` from the page's settings; builds the copy records | approach_copy.py:87-114 | R | new | Parsing factory; the stage id comes from the document. |
| ApproachCopy → StageColumns | `STAGE_COLUMNS.of(stage.id)` | approach_copy.py:60 | R | new | The id comes from the approach document, not from an object that could hold its stage. |
| HubBoard → BoardLabel / StageCopy / StageExample | builds labels and views while rendering | hub_board.py:82-158 | R | new | |
| StageColumns → StageColumn | holds the columns | stage_columns.py:59-60 | R | new | Composition, made once at import. |
| generate_cdd_catalog script → Catalog / GitCitation | entry point | generate_cdd_catalog.py:55-60 | R | new | |

### harness/design_canvas

| from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|
| FixtureScreen → ScenarioSource | holds its source; `html` reads it | fixture_bar.py:138, :155 | R | new | Composition 1. Both classes are unused (section 2). |
| CanvasVersions → PublishedVersion | raises | versions.py | R | new | Unused (section 2). |

### harness/chat

| from → to | interaction | file:line | verdict | changed from | reason; for W: owner, relationship, redesign |
|---|---|---|---|---|---|
| Chat → ChatPointer | `ChatPointer.from_claude_chat(self.id)` globs the Claude projects folder for the chat's transcript every time its title is due to be read | chat.py:308-310 (title read every 30 s, :277-281) | W | | The transcript belongs to the chat. Owner Chat, composition 0..1: find the pointer once (when it is first there) and keep it. |
| Chat → ChatCommand / ChatMessage | builds them from the command files in its folder | chat.py:262, :305 | R | new | Records it reads from its own folder and hands back. |
| Chat → ChatNotConnectedError | raises | chat.py:141 | R | new | |

## 2. Every class has a use

137 production classes (Python; the `class Component extends DCLogic` lines in harness/design_canvas are JavaScript inside strings). Inbound uses were found by a word search for each class name across every tracked `.py`, `.ts`, `.tsx`, `.md`, and `.json` file outside `.sessions/`, `.context/`, and the installed `.claude/` / `.cursor/` folders, specs counted separately, then read. "Build time" names the annotations the installer reads (`@agent_toolset`, `@agent_tool`, `@mcp`, `@skill`, `@command`, `@hook`, `@rules`, `@language_adapter`, `@toolset_collection`) and the module-level registrations.

### harness/guidance

| class | used by | uses | build time |
|---|---|---|---|
| Action | ActionCatalogue.actions (action_catalogue.py:76); LifecycleAction (catalog_generator.py:205); space/session/session_log.py:126; tools/prompt_notify/prompt_notify.py:77 | its toolset class | |
| ActionCatalogue | catalog_generator.py:211; space/session/session_log.py:126; tools/prompt_notify/prompt_notify.py:79 | Action, Name, annotation_kinds | |
| RenderRequest | PracticeGuidance.render, render_files, _render, _kept_wording, _call_render (guidance.py:531-559) | | |
| FidelityWithoutSessionError | FidelityGuidance.new_report_path (guidance.py:777) | | |
| Guidance | base of PracticeGuidance, FidelityGuidance, GuidanceCollection; cdd_guidance/builders/builder.py:9; guidance_actions.py:386 | Name, Markdown, Hook, RulesCollection | `@agent_toolset`; `rules` `@rules @agent_tool`; `instructions` `@skill @mcp @agent_instructions` |
| GuidanceCollection | PracticeGuidance.fidelities (guidance.py:488) | FidelityGuidance | `@toolset_collection` |
| PracticeGuidance | every practice class (cdd_guidance/practices/*/*.py); PracticeCatalogue; space/session; catalog | Format, Schema, Markdown, MarkdownText, Name, RulesCollection, ProjectRulesets, Session, format adapters | `@identity("key")`; `render @agent_tool`; `instructions @mcp @skill` |
| FidelityGuidance | GuidanceCollection.child; catalog; space/session; validate | Format, Markdown, MarkdownText, Name, PracticeCatalogue, FidelitySessionOutput | `@identity("slug") @agent_toolset`; `rules @rules`; `instructions @mcp @skill` |
| UnknownPractice | PracticeCatalogue.practice_class (practice_catalogue.py:70) | | |
| PracticeCatalogue | 55 production references (graph, session, catalog, diagnostics, guidance_actions) | PracticeGuidance classes | |
| ProjectRulesets | PracticeGuidance.project_rules only (guidance.py:306-313) | | — see D below |
| AppliesTo | RulesCollection (rule.py:143-152, :341); re-exported by harness/guidance/__init__.py:2 | MarkdownText | |
| Rule | RulesCollection; GraphRule (subclass); validate | Name | |
| RulesCollection | Guidance.rules; GraphRulesCollection (subclass); validate | AppliesTo, Rule, MarkdownText, ToolCall, HookPayload | `@agent_toolset`; `inject_rules @hook("postToolUse")` |
| SchemaType | Schema._read (schema.py:76) | | |
| Schema | PracticeGuidance (guidance.py:470); schema_rules.py:124-132; schema_edges.py:126 | SchemaType | |
| StageScope | ApproachStage; approach_copy.py:105; stage_columns.py:29; space/kanban/board.py:18 | | data fields reach TypeScript as `StageScopeData` through the Board language adapter |
| ApproachStage | STAGES; stage_columns.py:19; space/kanban/board.py:223 | StageScope | as above |
| ApproachStages | the module value `STAGES` (stages.py:137), read by approach_copy.py:102, stage_columns.py:60, space/kanban/board.py:223 | ApproachStage | |

### harness/guidance_actions

| class | used by | uses | build time |
|---|---|---|---|
| GuidanceRef | the `GuidanceArg` type of every action's `guidance` parameter (guidance_actions.py:34) | | parameter schema the MCP channel publishes |
| GuidanceArgument | GuidanceAction.for_call, _work_on (:165, :216) | PracticeCatalogue | |
| ActionWorksInNoSession | GuidanceAction.session (:182); 2 production references in cdd_guidance/actions | | |
| GuidanceAction | base of every action in cdd_guidance/actions (29 references) | ToolCall, Session, GuidanceArgument, AgentToolSet, PracticeCatalogue, GuidanceAgentOperation, Name, HookPayload | `@agent_toolset`; `begin @Toast @agent_instructions`; `inject_rules @Toast @hook("postToolUse")` |

### harness/graph

| class | used by | uses | build time |
|---|---|---|---|
| GraphLoaded, GraphSaved, Overlay, FilteredNode, NodeSource, ExplorerEntry | Graph's MCP tools and Node.serialize (graph.py:694-1336) | Node | return types of `@mcp` operations, generated into TypeScript by Graph's `@language_adapter` |
| NodeAnswer | base of ExplorerEntry, FilteredNode, NodeSource | | |
| GraphFailure | Graph.overlay_of (graph.py:1255) | | |
| EdgeType, Edge | PracticeGraph, Node, SchemaEdges, WorkingCopy, ModelNode, practices' graph readers | | |
| Call | Source.calls (graph.py:336) | | |
| _BracketDepth | Source (graph.py) | | |
| Source | Node, ModelNode, practices' readers (141 references) | Call, _BracketDepth | |
| Filter | Graph.filter, filter_choices (graph.py:1003, :1281) | Graph | |
| Node | everything in the graph (292 references) | Source, GraphRulesCollection, ExplorerEntry, PracticeGraph (item 1) | |
| PracticeGraph | item 1 | | |
| Inventory, AppliedOverlays | Graph.inventory, set_overlays | | `@mcp` return types → TypeScript |
| Graph | session, validate, practices, kanban report | PatternOverlays, SavedGraph, SavedGraphFile, WorkingCopy, PracticeChecks, SchemaEdges, Filter | `@language_adapter(typescript) @agent_toolset`; `@mcp` tools; `return_nodes @skill("read-graph")`; `load_files @command("load-files")` |
| GraphPractice, GraphOverlay, GraphPractices | item 1 | | |
| GraphRule | GraphRulesCollection.from_node (graph_rules_collection.py:113) | Violation | |
| GraphRulesCollection | Node.rules (graph.py:604-607) | PracticeSchema, GraphPractices, GraphRule | |
| ModelChildren | ModelNode and the practices' model classes (38 references) | ModelNode | |
| ModelWithoutPractice | ModelNode.__init__ (model_node.py:85) | | |
| ModelNode | base of BddModel, BehaviorNode, OoadNode, StoryNode, UxNode | Graph, Source, ModelChildren, EdgeType | |
| PatternOverlays | Graph (6 places); space/kanban/report.py:221-224 | | |
| PracticeGraphRule | base of every graph rule in the practices (143 references) | RuleCheckContext | |
| PracticeChecks | Graph._load_saved, WorkingCopy.fill | RuleCheckContext, PracticeSchema, GraphPractices | |
| RuleCheckContext | PracticeChecks; every rule's `check` signature (120 references) | | |
| SavedGraphOutdated, SavedNode, SavedEdge, SavedPractice, SavedGraph, SavedGraphFile | Graph; graph_bdd_model.py:32; validate's graph_json_reader; space/kanban/session_board_examples.py | Violation, Graph | |
| SchemaKey, SchemaField, SchemaFields, NodeEvidence, SchemaEdges | Graph.sync_schema_edges → SchemaEdges (graph.py:1218-1222); the rest inside schema_edges.py | Schema, PracticeCatalogue, EdgeType, Name | |
| PracticeSchema | GraphRulesCollection, PracticeChecks, WorkingCopy, PracticeGraph.schema, GraphPractice | Schema, PracticeCatalogue, GraphPractices | |
| SourceLine | Violation (violation.py:16-60) | | |
| Violation | GraphRule; SavedPractice; validate reports; kanban (71 references) | SourceLine | `SourceFile` annotation on its location |
| WorkingCopy | Graph._build_working_copy (graph.py:1190-1192) | GraphPractices, PracticeChecks, PracticeSchema, EdgeType | |

### harness/diagnostics

| class | used by | uses | build time |
|---|---|---|---|
| AgentToolsDiagnostics | no Python caller | ToolCall, Installer, AgentToolsProbe | `@agent_toolset`; `agent_tools_diagnostics @mcp @long_call @skill @command("agent-tools-diagnostics")` (installed skill `harness-diagnostics-agent-tools-diagnostics`) |
| ProbeCallTimedOut | AgentToolsProbe (agent_tools_probe.py:192) | | |
| AgentToolsProbe | AgentToolsDiagnostics (:37); scripts/agent-tools-diagnostics-heavy.py:17; scripts/agent_tools_probe_off_host.py:29 | Installer, McpHost, ProbeArguments, ProbeSection | |
| CddDiagnosticFixtures | ProbeArguments (probe_arguments.py:24) | WorkspaceFixtures | |
| GuidanceDiagnostics | no Python caller | ToolCall, Installer, GuidanceProbe | `@agent_toolset`; `guidance_diagnostics @mcp @long_call @skill @command("guidance-diagnostics")` |
| GuidanceProbe | GuidanceDiagnostics (:36); scripts/guidance-diagnostics.py:27 | PracticeCatalogue, AgentToolSet, ProbeArguments, ProbeSection, ProbeOutcome | |
| ProbeArguments | AgentToolsProbe, GuidanceProbe | CddDiagnosticFixtures, ToolCall, _OperationParameters | |
| _OperationParameters | ProbeArguments.for_operation (probe_arguments.py:49) | | |
| ProbeOutcome, ProbeSection | AgentToolsProbe, GuidanceProbe | | |
| ServerHealth | TypeScript: harness/chat-ui/pane/hooks/health/server-health-client.ts:4 (`ServerHealthData`) | HookDaemon | `@language_adapter(typescript) @agent_toolset`; `load @tool_subject`; `report @mcp @agent_tool @noSessionLog` |

### harness/catalog_generator

| class | used by | uses | build time |
|---|---|---|---|
| StageCopy, PrincipleCopy, ApproachCopy, _ApproachMarkdown | Catalog.approach_copy; ProjectApproach.generate; HubBoard; ApproachPage | STAGES, StageScope, StageColumns, Name | |
| PrincipleBullets, RefineBoard, ApproachGrids | ApproachPage (approach_page.py:104-370) | | |
| ApproachPage | Catalog._write_approach_pages (catalog_generator.py:1137); ProjectApproach.generate (project_approach.py:214) | ApproachGrids, StageExample, ExampleFile, CatalogFidelity, PageShell | |
| UnknownBrand, Brand | Catalog; ProjectApproach (41 references) | | |
| ExampleMarkdown, MonacoViewer | ExampleFile (catalog_examples.py:164-198) | MarkdownHtml, SourceFolds | |
| ExampleFile | ApproachGrids, CatalogFidelity | DrawioDiagram, SourceFolds, ExampleMarkdown, MonacoViewer | |
| CatalogFidelity | FidelityPage, PracticePage, ApproachGrids (10 places) | BoardLabel, ExampleFile | |
| PracticeExamples | Catalog._write_approach_pages (catalog_generator.py:1136) | | |
| ProjectExampleSources, StageExample | ApproachGrids, ApproachPage, HubBoard, ProjectApproach | | |
| CatalogPractice | Catalog.practices; ProjectApproach.generate | PracticeCatalogue, PracticeGuidance, MarkdownText, Name, SkillSlashName, StageColumns | |
| Utility, LifecycleAction | Catalog.utilities, lifecycle_actions | RepositoryToolsets, ActionCatalogue, Action | |
| FidelityTemplate | FidelityPage (catalog_generator.py:680) | | |
| GitCitation | Catalog; ProjectFiles; generate_cdd_catalog.py:55 | Git | |
| CatalogPage | Catalog.write_page; ProjectApproach.generate | | |
| SkillSlashName | CatalogPractice | deployed SKILL.md files | |
| DetailPage, PracticePage, FidelityPage, ActionPage, UtilityPage | Catalog._render_catalog | CatalogFidelity, FidelityTemplate, MarkdownHtml | |
| CatalogNotGenerated, CatalogProject | Catalog.project, generate_catalog | | |
| _SourceDocument | the module value `_SOURCE_DOCUMENTS`, read by Catalog._write_source_document | | |
| Catalog | generate_cdd_catalog.py:60 (175 references, most the word in prose) | everything above | `@agent_toolset`; `generate_catalog`, `apply_brand`, `generate_project_approach`, `configure_project_approach` `@mcp @skill` (installed skills `harness-catalog-generator-*`); `load @tool_subject` |
| DrawioDiagram | ExampleFile (catalog_examples.py:157, :203) | | |
| HubBoard | Catalog.board | BoardLabel, StageCopy, StageExample | |
| MarkdownHtml, _MarkdownReading | Catalog, DetailPage, ApproachGrids, ExampleMarkdown | | |
| PageShell | Catalog, ApproachPage, ProjectApproach | | |
| PracticeStage, DeclaredFile, ExampleClassifier, ProjectFiles, ProjectApproach | Catalog.generate_project_approach / configure_project_approach (catalog_generator.py:995-997) | PracticeCatalogue, StageColumns, GitCitation, CatalogPractice, Brand, ApproachPage, CatalogPage | |
| SourceFolds, _BraceScanner | ExampleFile | | |
| StageColumn, StageColumns, BoardLabel | the module value `STAGE_COLUMNS` (16 references); HubBoard; CatalogFidelity | ApproachStage, Name | |

### harness/design_canvas

| class | used by | uses | build time |
|---|---|---|---|
| DesignCanvas | ClaudeDesignStoryModel.canvas (cdd_guidance/practices/ux/model/claude_design/story_canvas.py:177-179) | | |
| ScenarioSource | **none** | | **none** — D |
| FixtureScreen | **none** | ScenarioSource | **none** — D |
| PublishedVersion | CanvasVersions only | | **none** — D |
| CanvasVersions | **none** | PublishedVersion | **none** — D |

### harness/chat

| class | used by | uses | build time |
|---|---|---|---|
| ChatCommand | Chat.check_in (chat.py:262) | | return type of `@mcp` `check_in` → TypeScript |
| ChatMessage | Chat.messages (chat.py:305) | | return type of `@mcp` `messages` → TypeScript |
| ChatNotConnectedError | Chat.send (chat.py:141); space/kanban/.../send_tile_action_to_chat_story.test.py:36 | | |
| Chat | space/kanban board, chat-ui pane, tools; 44 production references | ChatPointer, ChatCommand, ChatMessage | `@identity("id") @language_adapter(typescript) @agent_toolset`; `list`, `send`, `check_in`, … `@mcp @agent_tool @noSessionLog` |

### D — no use, delete

| class | checks |
|---|---|
| FixtureScreen (harness/design_canvas/fixture_bar.py:128) and ScenarioSource (:118), with the module's `bar()` and `methods()` | Python: no import of `harness.design_canvas.fixture_bar` and no `FixtureScreen(` / `ScenarioSource(` outside the module and fixture_bar_spec.py. TypeScript: none. Markdown: only cdd_guidance/practices/ux/model/claude_design/story_canvas.md:45-47 tells an agent to build screens on them, and no code or installer loads that file: `git grep story_canvas -- '*.py'` finds only the module beside it, and the installed `.claude/` and `.cursor/` hold no copy of the text. Installer discovery: not a toolset, no annotation. `.sessions/`: named only in validation reports, never used in a script. Delete with fixture_bar_spec.py and the story_canvas.md lines, or wire it into the UX prototype-screen generation if those screens are still wanted. |
| CanvasVersions (harness/design_canvas/versions.py:28) and PublishedVersion (:24) | Python: no import of `harness.design_canvas.versions` outside versions_spec.py; nothing calls `in_session_folder` or `working()`. TypeScript: none. Markdown: story_canvas.md:5, :13 says a regeneration goes through `CanvasVersions.working()` (rule `never-overwrite-a-published-canvas`), but `ClaudeDesignStoryModel.files()` renders straight from `canvas()` without it, so the rule is not enforced by code. No annotation, no registration. Delete with versions_spec.py and the story_canvas.md lines, or call it from the canvas generation so the rule holds. |
| ProjectRulesets (harness/guidance/project_rules.py:18), with `PracticeGuidance.project_rules` and `_project_rules_in` | Its one caller is `PracticeGuidance.project_rules` (guidance.py:306-313), and `git grep project_rules` finds no caller of that operation outside harness/guidance/project_rules_spec.py; nothing reads `.context/rules/{practice}/rules.md` anywhere else (`git grep "context/rules"`). No annotation on the operation, so it is not published. The class is used only on a path nothing reaches. Delete the class, the two operations, the spec, and its process-wide `_found` cache. |

## 3. Disconnected classes, verified

| class | earlier | verdict | reason; for B: owner and redesign |
|---|---|---|---|
| PracticeGraphRule | A (GraphPractice loads and runs it) | A, confirmed | graph_practice.py:88 and every practice's rule module subclass it. The owner moves to the practice under option A. |
| RuleCheckContext | A (PracticeGraphRule checks a node within it) | A, confirmed, with a redesign note | It is handed to every rule (practice_rule.py:15, built at rules.py:19). It wraps the practice and answers queries the practice should answer itself (`children`, `child_count` over `practice.edges`); under option A, a rule is handed the practice and RuleCheckContext goes. |
| Violation | B (the node should hold its violations) | **A, overturned** | The node already holds them: `Node.rules` (a `GraphRulesCollection`, made once, graph.py:604-607) holds a `GraphRule` per rule, and each `GraphRule` keeps its `Violation` objects in `_violations` (graph_rules_collection.py:33, :74-78). That is composition Node → GraphRulesCollection → GraphRule → Violation 0..*. The violation copies the node's location on purpose, because it outlives the node in the saved graph, the validation report, and the board. Draw GraphRule → Violation (composition 0..*). |
| DesignCanvas | A outside the seam; "ClaudeDesignStoryModel should hold its canvas (composition 1)" | A, confirmed; redesign withdrawn | The canvas is the story model's render output, rebuilt each render (section 1). Draw it when ClaudeDesignStoryModel is on the UX page. |
| SourceFile (used by Violation) | A | A, confirmed | violation.py:117. |
| FrontMatter, Format (harness/markdown; the Format half is in this area) | B | B, confirmed for Format | guidance.py builds `Format(name)` at :359, :379, :508, :557, :571, :574, :589, :590, :650, :798, :814 (eleven places). Owner FidelityGuidance (composition 1, the format it works in); the practice reads its current fidelity's format, and a render request carries a `Format`. |
| Builder, CreateAgentToolset, CreatePracticeGuidance (cdd_guidance/builders; the evidence cites harness/guidance/practice_catalogue.py:72) | B, "found only by PracticeCatalogue's module path lookup; PracticeCatalogue should hold the builders" | evidence wrong (outside this area) | `PracticeCatalogue._REFS` (practice_catalogue.py:31-37) lists only the five practices; it never finds the builders. They are found by the installer's toolset discovery (harness/installation/repository_toolsets.py:51, harness/agent_tools/agent_tools.py:237) and installed as skills (`builders-create-agent-toolset`, `builders-create-practice-guidance`), which is a build-time use. The owner of that entry should re-judge it. |

## 4. Summary

- Relationship entries checked: 164. R: 101. W: 56. Item 1: 6 (four left to item 1, two split between a judged part and item 1). One entry (PracticeGuidance → Guidance) is not a relationship: it is a call to its own base class.
- Overturned verdicts: 20. W → R: 19 (GuidanceCollection → FidelityGuidance, Rule → Name, RulesCollection → MarkdownText, RulesCollection → Rule, ActionCatalogue → Name, Graph → PracticeCatalogue, Graph → SavedGraph, Node → Source, AgentToolsDiagnostics → ToolCall, AgentToolsDiagnostics → AgentToolsProbe, AgentToolsProbe → McpHost, GuidanceDiagnostics → ToolCall, GuidanceDiagnostics → GuidanceProbe, GuidanceProbe → PracticeCatalogue, GuidanceProbe → AgentToolSet, ServerHealth → HookDaemon, Catalog → CatalogPractice, CatalogPractice → PracticeCatalogue, CatalogPractice → Name). R → not a relationship: 1. W kept but with a different owner, cardinality, or redesign: 7 (RulesCollection → ToolCall, GuidanceAction → ToolCall, GuidanceAction → AgentToolSet, SavedGraph → Graph, CatalogPractice → MarkdownText, PracticeGuidance → Schema, Graph → PatternOverlays). One disconnected class overturned B → A (Violation); one redesign withdrawn (DesignCanvas); one B entry's evidence is wrong (builders).
- New relationships the earlier files missed: 87, of which 29 are W (one of them split with item 1).
- Classes checked: 137. D: 5 classes (FixtureScreen, ScenarioSource, CanvasVersions, PublishedVersion, ProjectRulesets), plus the dead operations `PracticeGuidance.project_rules` / `_project_rules_in` and fixture_bar's `bar()` / `methods()`.
