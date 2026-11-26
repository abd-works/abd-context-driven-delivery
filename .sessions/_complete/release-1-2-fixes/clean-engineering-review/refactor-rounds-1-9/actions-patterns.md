# Relationship review: actions, patterns, builders, context setup

Area: `cdd_guidance/actions`, `cdd_guidance/patterns` (LERN, MERN, cdd_web_domain_access, cdd_claude_mod, their graph overlays and pattern rules), `cdd_guidance/builders`, `cdd_guidance/context_setup`. Every entry below was checked by reading the code as it is in the worktree on 2026-11-07. Line numbers are the current ones.

One reading applies to every action. The cdd server makes a new `GuidanceAction` for each tool call (`GuidanceAction.for_call`, harness/guidance_actions/guidance_actions.py:160), and `_inside(ActionType)` (guidance_actions.py:277) starts another action for the same session working on the same listed Guidance objects. An action started this way is a collaborator made for the same call from objects the caller already holds, not an object rebuilt from strings, so those relationships are judged **R**.

# 1. Runtime relationships, verified

| # | from → to | interaction | file:line | verdict | changed from | reason |
|---|---|---|---|---|---|---|
| 1 | Generate → PracticeGuidance | reads `fidelities`, `format`, `output_paths()` of each listed practice | cdd_guidance/actions/generate/generate.py:60, :61, :96 | R | | Generate acts on the practices its call listed. |
| 2 | Generate → FidelityGuidance | reads `current`, `outputs`, `files()`, `slug`; reads `FileEntry.exists` | generate.py:60, :63, :70, :83 | R | (not listed) | Asks the fidelity the listed practice holds. |
| 3 | Generate → Format | creates `Format(practice.format)`, `Format(label)` for every output label | generate.py:61, :63, :65 | W | W, redesign changed | Generate normalizes format labels it pulls out of the practice and fidelity by building throwaway `Format`s. |
| 4 | Generate → Render | starts render inside generate | generate.py:50 | R | | Sub-action for the same call. |
| 5 | Generate → Validate | reads `listed_rules()`; hands validate over as a tool | generate.py:38, :42 | R | (not listed) | Sub-action for the same call. Builds two Validates per call (rules, tool); harmless, since `listed_rules` keeps no state. |
| 6 | Render → PracticeGuidance | `render_files`, `render` | cdd_guidance/actions/render/render.py:37, :38 | R | (not listed) | Asks the listed practice to convert its own output. |
| 7 | Satisfy → AgentInstructions | `AgentInstructions.for_callable(Generate.generate_fixes_from_validate, generate)` then `.expand({})` | cdd_guidance/actions/satisfy/satisfy.py:34-36 | W | W, redesign changed | Satisfy reaches past the Generate it just made into the framework to rebuild that Generate's recipe from the class function. |
| 8 | Satisfy → Generate | starts generate inside satisfy | satisfy.py:35 | R | | Sub-action for the same call. |
| 9 | Satisfy → Validate | `validate(worked_on)` | satisfy.py:33 | R | (not listed) | Sub-action for the same call. |
| 10 | Iterate → GrillContext | `grill_with_context`, `generate_each` | cdd_guidance/actions/iterate/iterate.py:35-38 | R | | Sub-action per listed item. |
| 11 | Sketch → GrillContext | `grill_with_context`, `generate_each` | cdd_guidance/actions/sketch/sketch.py:48, :120, :124 | R | | Sub-action for the same call. `_grill_context()` is called twice, so the grill and the generate run on two GrillContexts; one held per call would do. |
| 12 | GrillContext → Generate | `generate(...)` per listed item | cdd_guidance/actions/grill_context/grill_context.py:123 | R | (not listed) | Sub-action for the same call. |
| 13 | GrillContext → ContextFileNotFound | raises | grill_context.py:88 | R | (not listed) | Its named failure. |
| 14 | Diagnose → Validate | `listed_rules()` | cdd_guidance/actions/diagnose/diagnose.py:137 | R | (not listed) | Sub-action for the same call. |
| 15 | Diagnose → SubAgentAnnotation | annotated `@subAgent` | diagnose.py:20 | R | | Annotation the author typed. |
| 16 | Document → Skill | annotated | cdd_guidance/actions/document/document.py:18 | R | | Annotation. |
| 17 | Document → PracticeGuidance | reads `templates`, `generate_output()`; probes `getattr(item, "scanner")` | document.py:27-31 | R | (not listed) | Acts on the listed practice. The `scanner` branch is dead: no PracticeGuidance has a `scanner` (grep `scanner` across harness and cdd_guidance finds none). |
| 18 | Improvement → Mcp | annotated | cdd_guidance/actions/improvement/improvement.py:20 | R | | Annotation. |
| 19 | Validate → Rule | `rule.validate()` | cdd_guidance/actions/validate/validate.py:73 | R | | The call hands it the Rule. |
| 20 | Validate → NoDeploy | annotated on `create_rule` | validate.py:192 | R | | Annotation. |
| 21 | Validate → Skill | annotated | validate.py:36, :194 | R | | Annotation. |
| 22 | Validate → PracticeCatalogue | `PracticeCatalogue.has(practice.key)` to turn listed practices into key strings | validate.py:148 | W | W, redesign changed | Validate already holds the practice objects (and `_listed_practices` resolves them through the session); it converts them to name strings only so CheckedGraph can filter violations by name. |
| 23 | Validate → CheckedGraph | creates with the session, `(guidance, outputs-dict)` tuples, and practice key strings | validate.py:56-57, :103-110 | W | (not listed) | Passes the owner's data (each guidance's `output_paths()` and key) into a helper beside the guidance it came from. |
| 24 | Validate → ReportFiles | creates with the session and the listed fidelities | validate.py:59 | R | (not listed) | Built once per call from objects held; ReportFiles asks each fidelity for its report path. |
| 25 | Validate → ValidationReport | creates; hands violations, rules, graph source strings, and a `slug → body` dict | validate.py:156-161 | W | (not listed) | The dict copies rule bodies out of the same guidance whose rules it also hands over. |
| 26 | Validate → PracticeGuidance (the session's) | `log_validation`, `checked_rules`, `every_rule`, `checked_rule_collections` | validate.py:158, :160, :173, :190, :218 | R | (not listed) | Asks the practices the session holds. |
| 27 | CheckedGraph → Graph | creates `Graph()`, `load_files(root, PracticeCatalogue.keys(), edited)`, `write_json`, then reads the written file back for violations | cdd_guidance/actions/validate/checked_graph.py:75-77, :63 | W | (not listed) | It builds the graph, writes it to disk, and re-reads the file to get the violations the Graph object it just held already had. |
| 28 | CheckedGraph → PracticeCatalogue | `PracticeCatalogue.keys()` to load every practice by name | checked_graph.py:76 | W | (not listed) | Practices named by strings, not the session's practice objects (the §1 PracticeGraph refactor's subject). |
| 29 | CheckedGraph → Violation | rebuilt from JSON dicts by `graph_json_reader` (`Violation.from_data`) | checked_graph.py:63; graph_json_reader.py:62 | W | (not listed) | Violations that lived on the graph's nodes are re-created from the file it wrote (see 27). |
| 30 | CheckedGraph → SavedGraph | `SavedGraph.from_document(raw, path).violations(practices)` for a graph file the call names | graph_json_reader.py:29 | R | (not listed) | A saved graph the caller names is an outside document. |
| 31 | CheckedGraph → ReportFiles | `reports.graph_file()` | checked_graph.py:55 | R | (not listed) | Collaborator handed in. |
| 32 | CheckedGraph → PathsNotFoundError | raises | checked_graph.py:90 | R | (not listed) | Its named failure. |
| 33 | ReportFiles → FidelityGuidance | `new_report_path()` | cdd_guidance/actions/validate/report_files.py:20 | R | (not listed) | Asks the fidelity it is handed. |
| 34 | ReportFiles → Violation | `save_checked_graph` re-reads graph files and rebuilds violations to merge them | report_files.py:39; graph_json_reader.py:47-49 | W | (not listed) | Same re-read of files the call itself just wrote. |
| 35 | ValidationReport → ValidationReportFormatter | builds a new formatter on every access of `_formatter` from `session.root` and `session.session_path` | cdd_guidance/actions/validate/validation_report.py:58-60 | W | (not listed) | A helper handed the session's folders per access; nothing else uses it. |
| 36 | ValidationReport → Rule | creates `Rule(slug=..., body=rule_bodies.get(slug))` for a graph hit with no listed rule | validation_report.py:84 | W | (not listed) | Rebuilds a Rule from a slug and a body copied out of the practice. |
| 37 | ValidationReport → Violation | groups and reads | validation_report.py:31, :107-111 | R | (not listed) | Reads the violations it is handed. |
| 38 | ValidationReportFormatter → Violation | reads `location`, `line`, `severity`, `described` | validation_report_formatter.py:22-27 | R | (not listed) | Reads the violation it is handed. |
| 39 | SketchLens → PracticeCatalogue | `PracticeCatalogue.practice_class(key).sketch_titles`; `keys()` | cdd_guidance/actions/sketch/sketch_outline.py:17, :24 | W | W, redesign changed | A lens is built from a practice's key string and the class's `sketch_titles`, on every call. |
| 40 | SketchOutline → SketchLens | `SketchLens.every()` inside heading loops | sketch_outline.py:72, :109 | W | W, redesign changed | Rebuilds every lens from the catalogue on each heading it tests. |
| 41 | SketchOutline → SketchLens | `lens.opens(title)` on the lens the caller hands | sketch_outline.py:95 | R | split from 40 | Acts on the lens it is handed. |
| 42 | SketchOutline → _Section | creates its own section records | sketch_outline.py:66, :101 | R | (not listed) | Its own parts, made from its own lines. |
| 43 | practice sketch models → SketchLens | `SketchLens.of("stories")`, `of("ddd")`, `of("clean_engineering")`, `of("bdd")` | practices/stories/model/sketch/sketch_story_model.py:39; practices/ddd/model/sketch/sketch_ddd_model.py:70; practices/clean_engineering/model/sketch/sketch_class_model.py:58, :134; practices/bdd/model/sketch/sketch_bdd_model.py:15-16 | W | (not listed; outside this area, touches SketchLens) | Each practice names itself by a string to get back its own lens. |
| 44 | Partition → PartitionIndex | resolves a path, reads its text, hands path and text to `PartitionIndex.from_text` | cdd_guidance/actions/partition/partition.py:77-90 | W | (not listed) | Partition reads the file PartitionIndex stands for and passes its text in. |
| 45 | Partition → Segment | reads the segment file and hands path, text, and config to `Segment.from_text` | partition.py:53-58 | W | (not listed) | Same: reads the file the Segment stands for. |
| 46 | Partition → SegmentCompletenessConfig | builds one from the `min_body_chars` argument when no index is found | partition.py:48-52 | W | (not listed) | The config belongs to the index; Partition chooses between the index's and a fresh one. |
| 47 | PartitionIndex → SegmentCompletenessConfig | parsed from its own text | partition_index.py:34-41 | R | (not listed) | Its own part. |
| 48 | Segment → SegmentEntry | builds one per expected name from its own text | segment.py:128-130, :180-186 | R | (not listed) | Its own parts. |
| 49 | Segment → SegmentCompletenessConfig | holds | segment.py:78 | R | (not listed) | Held collaborator. |
| 50 | SegmentEntry → SegmentCompletenessConfig | holds the segment's config | segment.py:39 | R | (not listed) | Handed by its owner at creation. |
| 51 | DomainDrivenStack → Stories | `_stories()` creates a Stories companion | cdd_guidance/patterns/domain_driven_stack.py:24-31 | W | W, reason changed | Nothing calls `_stories()`: grep for `_stories(` in Python finds only the definition; `lern_domain_driven.md` and `mern_domain_driven.md` say generate calls it, but DomainDrivenStack overrides no generate. Dead operation. |
| 52 | LernOverlay → LernDomainDriven | `guidance()` creates a new pattern guidance on each call | cdd_guidance/patterns/lern_domain_driven/graph_overlay.py:37-40 | W | (named in §1 text) | The overlay builds its owner; the direction is backwards. |
| 53 | WebDomainAccessOverlay → CddWebDomainAccess | same | cdd_guidance/patterns/cdd_web_domain_access/graph_overlay.py:14-17 | W | (named in §1 text) | Same. |
| 54 | ClaudeModOverlay → CddClaudeMod | same | cdd_guidance/patterns/cdd_claude_mod/graph_overlay.py:9-12 | W | (named in §1 text) | Same. |
| 55 | LernOverlay → GraphPractices | `register_overlay` at import, looked up by name (`GraphPractices.overlay(pattern)`, harness/graph/graph_practice.py:171) | lern_domain_driven/graph_overlay.py:260 | W | (named in §1 text) | Name-keyed class registry; the overlay is reached by a folder-name string. |
| 56 | WebDomainAccessOverlay → GraphPractices | same | cdd_web_domain_access/graph_overlay.py:49 | W | (named in §1 text) | Same. |
| 57 | ClaudeModOverlay → GraphPractices | same | cdd_claude_mod/graph_overlay.py:15 | W | (named in §1 text) | Same. |
| 58 | GraphOverlay → pattern rule modules | `rules_for(practice)` imports `cdd_guidance.patterns.<pattern>.practices.<practice>.rules` by a built module path and reads `BY_SLUG` | harness/graph/graph_practice.py:145-146, :25-37 | W | (not listed) | Pattern rules are found by a string path instead of being held by the pattern that declares them. |
| 59 | LernOverlay → _LernReading | one reading object per `read` | lern_domain_driven/graph_overlay.py:45 | R | (not listed) | A method object for one read, made from the graph it is handed. |
| 60 | _LernReading → Graph | reads `practices`, `folder` of the graph handed to `read` | graph_overlay.py:43, :72, :87 | R | (not listed) | Collaborator handed in. |
| 61 | _LernReading → PracticeGraph | `graph.practice("ddd")`, `("bdd")`, `("stories")` | graph_overlay.py:74, :89, :209 | W | (not listed) | Practices reached by name string (the §1 refactor removes this). |
| 62 | WebDomainAccessOverlay → PracticeGraph | `graph.practice("ddd")` | cdd_web_domain_access/graph_overlay.py:22 | W | (not listed) | Same. |
| 63 | _LernReading → PracticeGraph / Node | `add_named`, `link`, `by_id`, `set_fact` | graph_overlay.py:54, :66, :95, :103, :149, :190 | R | (not listed) | Adds to and asks the practice graph it reached. |
| 64 | WebDomainAccessOverlay → Node | `add_named`, `set_fact` | cdd_web_domain_access/graph_overlay.py:30-32 | R | (not listed) | Same. |
| 65 | overlays → Source | `Source.whole_file(...)`, `Source(folder, 1, 1, root)` handed to `add_named` | lern graph_overlay.py:54, :103, :190; web graph_overlay.py:30 | R | (not listed) | A value the new node keeps as its location. |
| 66 | _LernReading (through tier_facts) → SourceText | every fact function wraps the same text in a new `SourceText(text)`; `node_root_facts` builds one per repository body and per match | cdd_guidance/patterns/lern_domain_driven/tier_facts.py:55, :60, :73, :77, :81, :95, :126-129, :139-145, :158 | W | (not listed) | The overlay reads a file's text and hands the string to module functions, each of which rebuilds the file's SourceText. |
| 67 | WebDomainAccessOverlay (through access_facts) → SourceText | same | cdd_guidance/patterns/cdd_web_domain_access/access_facts.py:23, :27 | W | (not listed) | Same. |
| 68 | tier_facts → LernDomainDriven | reads class constant `story_test_folder` | tier_facts.py:110-114 | R | (not listed) | Reads the pattern's own setting. The same string is copied again in `LernCanvasFixtures.story_test_folder` (fixtures.py:24). |
| 69 | pattern rules → Node | every rule's `check(node, context)` reads `node.get_fact(...)` (17 rules in 4 modules) | lern_domain_driven/practices/{bdd,ddd,stories}/rules/*.py; cdd_web_domain_access/practices/ddd/rules/access_rules.py | R | (not listed) | Acts on the node it is handed. |
| 70 | ContextSetup → Stories | constructor default `Stories()`; only `_apply_tool_modes` touches it | cdd_guidance/context_setup/context_setup.py:72, :101 | W | W, reason overturned | Not "cannot be swapped": the constructor already takes it as a parameter. It is held and never used; no operation or recipe reads `self.stories`. |
| 71 | ContextSetup → CleanEngineering | same | context_setup.py:73, :101 | W | W, reason overturned | Same: held, unused. |
| 72 | ContextSetup → Ddd | same | context_setup.py:74, :101 | W | W, reason overturned | Same. |
| 73 | ContextSetup → Ux | same | context_setup.py:75, :101 | W | W, reason overturned | Same. |
| 74 | ContextSetup → Partition | held, passed in or defaulted; made for the call's session in `for_call`; recipe hands `partition.partition` as a tool | context_setup.py:65, :76, :83, :306 | R | **W → R** | The constructor takes it as a parameter (`partition: Optional[Partition]`), and `for_call` re-makes it for the call's session. A held collaborator. |
| 75 | ContextSetup → Partition | `self.partition.path_named(...)` to resolve the call's folders | context_setup.py:96-97, :118 | W | (not listed) | ContextSetup holds its own session (`self.session`) but borrows Partition's to resolve paths. |
| 76 | ContextSetup → ContextIndex | held, passed in or defaulted; recipes hand `context_index.embed` | context_setup.py:66, :77, :272, :311 | R | **W → R** | Constructor parameter (`context_index: Optional[ContextIndex]`); a held collaborator. |
| 77 | ContextSetup → LiveAppCapture | creates one per capture call from the call's repo, surface, base URL, paths | context_setup.py:93-98 | R | (not listed) | Each call names a different running application; nothing holds it between calls. |
| 78 | ContextSetup → StructureNote, ConversionResult | creates its own results | context_setup.py:123, :319 | R | (not listed) | Its own result values. |
| 79 | ContextSetup → ToolCall | reads `call.session` | context_setup.py:84 | R | | Handed in. |
| 80 | ContextSetup → ActionWorksInNoSession | raises | context_setup.py:90 | R | | Named failure. |
| 81 | ContextIndex → OpenAIEmbeddingProvider | made lazily when no provider was passed in | cdd_guidance/context_setup/context_index.py:77-83 | R | (not listed) | An outside system behind an injectable provider. |
| 82 | ContextIndex → RankedChunk | built from `meta.json` dicts it re-reads on each search | context_index.py:143-165 | W | (not listed) | ContextIndex is a service handed a folder path each call; the on-disk index (index.faiss + meta.json) has no object, so its chunks are rebuilt from dicts. |
| 83 | ContextIndex → EmbedResult, SearchResult | creates its results | context_index.py:115, :125, :165 | R | (not listed) | Its own result values. |
| 84 | LiveAppCapture → ScreenResult, SmokeTestResult, PageCapture, FailedPage, ScoutResult, CaptureResult | creates its results | live_app_capture.py:119, :130, :144, :194-204, :242, :260 | R | (not listed) | Its own result values. |
| 85 | LiveAppCapture → CaptureFailed | raises | live_app_capture.py:202 | R | (not listed) | Named failure. |

## Redesign for each W

| # | owner | relationship it should be | redesign |
|---|---|---|---|
| 3 | FidelityGuidance (and PracticeGuidance through its current fidelity) | composition 1 (a fidelity owns its Format) | The earlier entry made Generate the owner; the format is the fidelity's, not the action's. `practice.format` and each fidelity's declared outputs return `Format` objects, so Generate compares `fidelity.format` with the earlier fidelity's output formats and builds none. |
| 7 | Generate | composition 1 (Generate owns the recipe of its operation) | Satisfy asks the Generate it started for the fix instructions through a public operation on that Generate (for example `generate.fix_instructions()`), instead of rebuilding `AgentInstructions` from the class function. |
| 22, 23 | Session (it holds the practices); CheckedGraph aggregates the listed practices | aggregation 0..* (CheckedGraph holds the listed PracticeGuidance) | Hand CheckedGraph the listed practices Validate already resolves through the session. CheckedGraph asks each for `format` and `output_paths()` and filters the graph's violations by practice object; the key strings, the `(item, outputs)` tuples, and `PracticeCatalogue.has` go. |
| 25, 36 | Validate's listed PracticeGuidance | association 0..* (ValidationReport reads the listed practices' rules) | Hand ValidationReport the listed practices (or their `every_rule()`), so a graph hit's rule is the practice's own Rule; drop the `rule_bodies` dict and the `Rule(slug, body)` rebuild. |
| 27, 28, 29, 34 | CheckedGraph | composition 1 (CheckedGraph owns the Graph it builds for the call) | Keep the built Graph on CheckedGraph, load it with the session's practices (not `PracticeCatalogue.keys()`), and ask it for the listed practices' violations. Write the JSON only for the saved report; ReportFiles copies that file and no longer merges by re-reading. |
| 35 | ValidationReport | composition 1 | Make the formatter once in ValidationReport's constructor from the session it already holds, or move its two operations onto ValidationReport; nothing else uses it. |
| 39, 40, 43 | PracticeGuidance | composition 1 (a practice owns its SketchLens); SketchOutline aggregation 0..* of the lenses it splits by | The earlier redesign ("SketchLens holds its PracticeCatalogue") keeps the name lookup. Each practice makes its lens once from its own `sketch_titles` (`practice.sketch_lens`); the practice's sketch model asks its practice for it; SketchOutline is given the session's lenses when made, so `SketchLens.of`, `SketchLens.every`, and the catalogue import go. |
| 44, 45, 46 | PartitionIndex owns its file and config; Segment holds its PartitionIndex | Segment association 0..1 to PartitionIndex; PartitionIndex composition 1 of SegmentCompletenessConfig | PartitionIndex and Segment load from their own path (`PartitionIndex.near(segment_path)`, `Segment.at(path, index)`), and a segment reads its config from its index, defaulting when it has none. Partition stops reading file text and choosing configs. |
| 51 | DomainDrivenStack | none | Delete `_stories()` (and the Stories import) and correct `lern_domain_driven.md` / `mern_domain_driven.md`, or give the stack the generate override the markdown describes. As the code stands it is dead. |
| 52-58 | The pattern's guidance (LernDomainDriven, CddWebDomainAccess, CddClaudeMod) | composition 1 (pattern owns its overlay); association 0..* (a practice holds the patterns that add rules to it) | Confirms the §1 GraphOverlay judgement: the pattern guidance makes its overlay and holds the rules under `<pattern>/practices/<practice>/rules`; the graph is given the pattern objects the session applies, so `register_overlay`, `GraphPractices.overlay(name)`, `rules_for` by module path, and `guidance()` building a new pattern go. MernDomainDriven has no overlay and is unaffected. |
| 61, 62 | Graph (aggregates the session's practices, per §1) | association 1 to each practice it reads | The overlay receives the DDD, BDD, and Stories practice graphs from the graph as objects (`graph.ddd` or the practice instances), not by `graph.practice("ddd")`. |
| 66, 67 | The file the overlay reads (SourceText as the text part of that file) | composition 1 (one SourceText per file read) | The overlay builds one SourceText per file it reads and the fact functions become its operations (or operations of a tier-file subclass), so the text is wrapped once; today `node_root_facts` alone wraps the same text once per repository and per match. |
| 70-73 | none | none | Delete the four practice fields and constructor parameters and `_apply_tool_modes`. The recipe tells the agent to call `partition` with the chosen guidance; ContextSetup never asks a practice anything. |
| 75 | ContextSetup | association 1 (its own session) | Resolve the call's folders with `self.session.path_named(...)`; ContextSetup already holds the session (`for_call` passes `call.session`). |
| 82 | A segment index object (index.faiss + meta.json) | composition 0..* of RankedChunk entries | Give the on-disk index its own class that ContextIndex creates in `embed` and opens in `search`; it owns its metadata and answers ranked chunks. `_extract_view` also re-parses front matter by hand where `harness/markdown`'s FrontMatter already does. |

# 2. Every class has a use

Production classes in the area: 72 (spec files, `_examples/`, and the builders' `templates/*.py` scaffolds left out). Build-time paths checked for each: `RepositoryToolsets` discovery (harness/installation/repository_toolsets.py:46-52 lists `cdd_guidance/actions`, `patterns`, `builders`; the installer publishes every `@agent_toolset` with `@skill`/`@mcp` members, visible as `.claude/skills/actions-*`, `patterns-*`, `builders-*`, `context-setup-*`), `ActionCatalogue._toolset_in` (harness/guidance/action_catalogue.py:69, :103, imports every action folder's class), `GraphPractices.overlay` import of `<pattern>.graph_overlay` (graph_practice.py:171-173), and `rules_in` for pattern `RULES`/`BY_SLUG` (graph_practice.py:25-37). Grep covered Python, TypeScript, and markdown outside `.sessions/` and `.venv/`.

## cdd_guidance/actions

| class | used by (inbound) | uses (outbound) | build time |
|---|---|---|---|
| Generate | Satisfy satisfy.py:35; GrillContext grill_context.py:123; kanban stories (generate_fidelity_output_story.test.py:47) | PracticeGuidance, FidelityGuidance, Format, Render, Validate | ActionCatalogue; skill `actions-generate`, MCP |
| Render | Generate generate.py:50 | PracticeGuidance | ActionCatalogue; skill `actions-render` |
| Satisfy | (none in process) | Validate, Generate, AgentInstructions | ActionCatalogue; skill `actions-satisfy` |
| Iterate | (none in process) | GrillContext | ActionCatalogue; skill `actions-iterate` |
| Sketch | (none in process) | GrillContext | ActionCatalogue; skill `actions-sketch` |
| GrillContext | Sketch sketch.py:48; Iterate iterate.py:35 | Generate, ContextFileNotFound | ActionCatalogue (action_catalogue.py:57 names it); skill `actions-grill-context-grill` |
| ContextFileNotFound | raised by GrillContext grill_context.py:88 | - | - |
| Diagnose | (none in process) | Validate, SubAgentAnnotation | ActionCatalogue; skill `actions-diagnose`; `@noCatalog` keeps it off the catalog |
| Document | (none in process) | PracticeGuidance, Skill | ActionCatalogue; skill `actions-document` |
| Improvement | (none in process) | Mcp | ActionCatalogue; skills `actions-improvement-repair`, `-verify-fix` |
| Partition | ContextSetup context_setup.py:76, :83 | PartitionIndex, Segment, SegmentCompletenessConfig | ActionCatalogue; skill `actions-partition`; MCP tools `partition.index`, `.segment`, `.verify_segment_completeness` (probed by harness/diagnostics/probe_arguments.py:90) |
| PartitionIndex | Partition partition.py:83, :87 | SegmentCompletenessConfig | - |
| Segment | Partition partition.py:53 | SegmentEntry, SegmentCompletenessConfig | - |
| SegmentEntry | Segment segment.py:184, :186 | SegmentCompletenessConfig | - |
| SegmentCompletenessConfig | PartitionIndex partition_index.py:61; Partition partition.py:51; Segment, SegmentEntry | - | - |
| Validate | Generate generate.py:38, :42; Satisfy satisfy.py:33; Diagnose diagnose.py:137; kanban stories (validate_fidelity_story.test.py:27) | Rule, PracticeCatalogue, CheckedGraph, ReportFiles, ValidationReport, PracticeGuidance | ActionCatalogue; skill `actions-validate` |
| CheckedGraph | Validate validate.py:57 | Graph, PracticeCatalogue, Violation, SavedGraph, ReportFiles, PathsNotFoundError | - |
| PathsNotFoundError | raised by CheckedGraph checked_graph.py:90 | - | - |
| ReportFiles | Validate validate.py:59; CheckedGraph checked_graph.py:51 | FidelityGuidance, Violation (through the reader) | - |
| ValidationReport | Validate validate.py:156 | ValidationReportFormatter, Rule, Violation | - |
| ValidationReportFormatter | ValidationReport validation_report.py:60 | Violation | - |
| SketchLens | SketchOutline sketch_outline.py:72, :109; the four practice sketch models (row 43) | PracticeCatalogue | - |
| SketchOutline | sketch_story_model.py:39; sketch_ddd_model.py:70; sketch_class_model.py:58; sketch_bdd_model.py:14 | SketchLens, _Section | - |
| _Section | SketchOutline sketch_outline.py:66, :101 | - | - |

## cdd_guidance/patterns

| class | used by (inbound) | uses (outbound) | build time |
|---|---|---|---|
| DomainDrivenStack | base of LernDomainDriven, MernDomainDriven | Stories (dead `_stories`) | through its subclasses |
| LernDomainDriven | LernOverlay graph_overlay.py:40; tier_facts.py:114 | - | skill `patterns-lern-domain-driven`; `pattern` read by HookServer (harness/hooks/hook_server.py:265) |
| MernDomainDriven | (none in process) | - | skill `patterns-mern-domain-driven` |
| CddWebDomainAccess | WebDomainAccessOverlay graph_overlay.py:17 | - | skill `patterns-cdd-web-domain-access` |
| CddClaudeMod | ClaudeModOverlay graph_overlay.py:12 | - | skill `patterns-cdd-claude-mod` |
| LernOverlay | GraphPractices (registered graph_overlay.py:260; read graph_practice.py:171, schema_rules.py:114) | LernDomainDriven, _LernReading, GraphPractices | imported by GraphPractices.overlay |
| _LernReading | LernOverlay graph_overlay.py:45 | Graph, PracticeGraph, Node, Source, tier_facts/SourceText | - |
| WebDomainAccessOverlay | GraphPractices (graph_overlay.py:49) | CddWebDomainAccess, Graph, PracticeGraph, Node, Source, access_facts/SourceText | imported by GraphPractices.overlay |
| ClaudeModOverlay | GraphPractices (graph_overlay.py:15) | CddClaudeMod | imported by GraphPractices.overlay |
| SourceText | tier_facts.py (13 sites); access_facts.py:23, :27 | - | - |
| OneClassPerObject, StateLivesBehindTheTool, AdapterIsGenerated, AnnotateWhatTypeScriptReads | `RULES` in cdd_web_domain_access/practices/ddd/rules/__init__.py:10 | Node | loaded by `rules_in` |
| SharedBehaviorStaysTierFree, TierRunsSharedBehavior, ServerTierCallsTheRealThing, E2eRunsTheWholeStack | `RULES` in lern_domain_driven/practices/bdd/rules/__init__.py:10 | Node | loaded by `rules_in` |
| NodeRepositoryParsesOnRead, PostedBodyParsedInNode, ThrowHttpExceptions, OneHomeForWebPaths, ResetEveryRepository | `RULES` in lern_domain_driven/practices/ddd/rules/__init__.py:11 | Node | loaded by `rules_in` |
| TierBoundRepositoryAccessor, NoExpectInGiven, DomainOperationsInlineInSteps, OutlineEntriesLoopOverExamples | `RULES` in lern_domain_driven/practices/stories/rules/__init__.py:10 | Node | loaded by `rules_in` |
| LernCanvasFixtures | **none** | - | **none** → **D** (below) |

## cdd_guidance/builders

| class | used by (inbound) | uses (outbound) | build time |
|---|---|---|---|
| Builder | base of CreateAgentToolset, CreatePracticeGuidance | - | through its subclasses |
| CreateAgentToolset | (none in process) | - | skill `builders-create-agent-toolset` (RepositoryToolsets, repository_toolsets.py:51) |
| CreatePracticeGuidance | (none in process) | - | skill `builders-create-practice-guidance` |

## cdd_guidance/context_setup

| class | used by (inbound) | uses (outbound) | build time |
|---|---|---|---|
| ContextSetup | (none in process) | Stories, CleanEngineering, Ddd, Ux (unused), Partition, ContextIndex, LiveAppCapture, StructureNote, ConversionResult, ToolCall | skills `context-setup-convert`, `-smoke-test`, `-scout-app`, `-complete-capture`, `-capture-from-live-app`, `-capture-from-documents`; `.claude/agents/context.md` |
| ContextIndex | ContextSetup context_setup.py:77 | OpenAIEmbeddingProvider, RankedChunk, EmbedResult, SearchResult | skills `context-setup-embed`, `-search`, `-ask` |
| EmbeddingProvider (Protocol) | ContextIndex type of `embedding_provider` context_index.py:77; spec fake | - | - |
| OpenAIEmbeddingProvider | ContextIndex context_index.py:82 | OpenAI (outside) | - |
| RankedChunk, EmbedResult, SearchResult | ContextIndex results | - | MCP return types |
| StructureNote, ConversionResult | ContextSetup.convert results | - | MCP return types |
| LiveAppCapture | ContextSetup context_setup.py:98 | result records, CaptureFailed | - |
| ScreenResult, SmokeTestResult, PageCapture, FailedPage, ScoutResult, CaptureResult | LiveAppCapture results; ContextSetup return types | - | MCP return types |
| CaptureFailed | raised by LiveAppCapture live_app_capture.py:202 | - | - |

## D — no use, delete

**LernCanvasFixtures** (cdd_guidance/patterns/lern_domain_driven/practices/stories/model/claude_design/fixtures.py:21), with its spec, `build-canvas-fixtures.mjs`, `canvas-fixtures.ts`, and `claude_design.md`.
- Python: `LernCanvasFixtures` appears only in its own module and `fixtures_spec.py`.
- TypeScript / mjs: no import of `fixtures.py` or the class; `build-canvas-fixtures.mjs` is called only by `LernCanvasFixtures.build`.
- Markdown recipes: only its own `claude_design.md`, which no installer or practice loads (PracticeGuidance reads a practice's own `model/`, guidance.py:451; pattern folders are read only for `practices/<practice>/rules` and schema; nothing under `.claude/` or `.cursor/` names it). `harness/design_canvas/fixture_bar.py` consumes a `canvas-fixtures.js` bundle but never builds it.
- Installer discovery: not a toolset, no annotations, and RepositoryToolsets skips folders named `fixtures` anyway.
- Its `story_test_folder` copies `LernDomainDriven.story_test_folder`.
Delete it, or, if the Claude Design canvas is to load LERN fixtures, give it a caller in harness/design_canvas and take the folder from the LERN pattern instead of copying it. Today it has neither.

Dead members of classes that are themselves in use (delete with the class's next change): `DomainDrivenStack._stories` (row 51); `Partition.partition_corpus` (partition.py:117, `@agent_instructions` with no publishing annotation and no caller); Document's `scanner` branch (row 17); ContextSetup's four practice fields (rows 70-73).

# 3. Disconnected classes, verified

| entry in repo-model-disconnected.md | verdict | reason |
|---|---|---|
| Document, Improvement (A) | **confirmed A** | Published action toolsets (skills `actions-document`, `actions-improvement-*`) that ActionCatalogue imports by folder (action_catalogue.py:103); nothing calls them in process. |
| Render (A) | **confirmed A** | Generate starts it (generate.py:50). |
| Sketch, Iterate, GrillContext (A) | **confirmed A** | Sketch and Iterate start GrillContext (sketch.py:48, iterate.py:35); GrillContext also starts Generate (grill_context.py:123), which the model did not draw. |
| LernDomainDriven, MernDomainDriven, CddWebDomainAccess, CddClaudeMod (B) | **B confirmed, evidence corrected** | The cited evidence is wrong: PracticeCatalogue does not find patterns (its `_REFS`, practice_catalogue.py:31-37, holds only the five practices; :72 is `practice_class`'s import for those). Patterns are found by RepositoryToolsets at install (repository_toolsets.py:50) and by `GraphPractices.overlay(pattern)` importing `<pattern>.graph_overlay` (graph_practice.py:171-173), whose `guidance()` builds a new pattern guidance per call (rows 52-54). The B judgement stands: the pattern guidance should own its overlay and rules (composition 1), and the graph should be given the patterns the session applies, instead of the overlay building its owner and being looked up by folder name. MernDomainDriven has no overlay or rules, so for it only the install path applies (A, published skill). |
| Builder, CreateAgentToolset, CreatePracticeGuidance (B) | **overturned → A (build time); Builder is Base** | PracticeCatalogue does not import them; the cited "module path lookup" does not exist. RepositoryToolsets publishes the two subclasses as skills (repository_toolsets.py:51; `.claude/skills/builders-*`). They are guidance a person runs, not practices on the board, so PracticeCatalogue should not hold them; no redesign is needed. Builder is the base that sets `default_workspace_folder = "."`. |

Classes in this area the disconnected list did not name but that the model should show as connected: SketchOutline (used by every practice's sketch model), Partition with PartitionIndex/Segment/SegmentEntry, CheckedGraph/ReportFiles/ValidationReport/ValidationReportFormatter, SourceText, the pattern rule classes, ContextIndex and LiveAppCapture with their result records.

# 4. Summary

- Relationships checked: **85** (25 were in the earlier files for this area; 60 added).
- **R: 50. W: 35.**
- Verdicts overturned: **2** (ContextSetup → Partition and ContextSetup → ContextIndex, W → R). W kept with the reason or redesign changed: **10** (Generate → Format, Satisfy → AgentInstructions, Validate → PracticeCatalogue, SketchLens → PracticeCatalogue, SketchOutline → SketchLens, DomainDrivenStack → Stories, ContextSetup → Stories/CleanEngineering/Ddd/Ux).
- Classes checked: **72**. **D: 1** (LernCanvasFixtures).
- Disconnected entries checked: 5; confirmed 3, evidence corrected 1 (patterns), overturned 1 (builders, B → A).
