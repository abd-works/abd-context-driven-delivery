# Skipped W items that wait for the option A follow-up (guidance / session / tool_call)
From harness-upper agent (4c82368f):
- ProbeArguments builds a fake ToolCall to find a session: SessionOpener needs "open a session for a project" (tool_call.py + space/session).
- ExampleClassifier duplicates the session's declared-file matching: FidelityGuidance should answer "do you declare this path".
- CatalogFidelity column lookup by string: FidelityGuidance should hold its ApproachStage.
- CatalogPractice re-reads the practice markdown: PracticeGuidance should hold its Markdown.
- FidelityTemplate second way to find template: FidelityGuidance should expose its template file.
- SkillSlashName re-reads deployed SKILL.md: FileInstallation (installation/files.py) should give the skill name (after the installation agent lands).
From space/repo + tools agent (16109f17):
- FileManager.load builds a ToolCall (agent_tools.py; with the file_manager move into space/session).
- PromptLog -> Sessions needs HookPayload.session (hooks/hook_server.py; matches harness-core W HookServer -> ToolCall).
- SessionLog.timestamp value type (space/session/session_log.py).
- PromptNotify second registry of names: match on PracticeCatalogue / ActionCatalogue (harness/guidance).
- PromptNotify -> AgentTool: toast and mcp_names belong on AgentTool (agent_tools.py; after harness-core lands).
- Callers that can now use repo.main_clone / repo.work_state: space/kanban/board.py:97, space/session/sessions.py:41,68.
From harness core agent (d53037a8):
- GuidanceAgentOperation -> GuidanceAction._log_running_action: needs a public log_running (guidance_actions.py).
- Markdown -> YamlFields writes settings onto the owner: guidance classes should apply their own settings (guidance.py).
- AssetLocator probes owner attributes: guidance classes and AgentToolSetOrigin hand folder/slug/fidelity to their Markdown (guidance.py).
- FrontMatter owned by MarkdownFile: readers in installation/files.py, installer.py, catalog generator (after installation agent lands).
- installation/language_adapter.py:606 builds its own ToolSubjectLoader; should read ToolsetMembers.of(type(toolset)).subject_loader (installation agent / after).
- AgentToolSet -> ToolsetReference: owner is RepositoryToolsets (installation).
From installation agent (26c9aa13):
- FileInstallation -> Name (agent_tools.py); FileInstallation -> MarkdownText (guidance RulesCollection); FrontMatter owned by MarkdownFile (markdown);
  FileInstallation probes toolset attributes (agent_tools + guidance); HOSTED_ONLY_CLASS_NAMES (guidance + markdown);
  HookServer stand-in ToolCall (tool_call.py); ChatInjections (space/session); McpServer practice_guidance probe (FidelityGuidance);
  HookHandler pattern probe (agent_tools / patterns base). Catalog html not regenerated.

From practices agent (49eb3653), about 45 of 169 done:
- Skipped, need the practice main class files or graph_reading.py (now free to change): CE 20, 23-30, 31/37, 34/39, 38, 57/58, _language_model, PythonModule re-parse, _DrawioScannerRule per node; StoriesGraph/_StoryLinks/GraphStoryModel record; DddGraph/_DddReading/_tactical_block/tactical_facts/_text, DDD tactical_helpers and rule_examples; BDD 42, 45, 46; stories.py Format x2, adapter per render, StoryModel.load/_story_map_file/story_test_type, SketchLens.of("stories"); ddd.py Format, second markdown parse, clean_engineering_bridge pair and _take_integrations, _python_generics; clean_engineering.py Drawio second format table; ux.py (UX 1); bdd.py SketchLens.of("bdd"), 56; agent_bdd.py 63.
- Skipped, need harness: CE 33 ModelChildren reconcile, CE 54 RuleCheckContext ClassGraph, CE 56 edges not ids, UX 4/48, 13/34/45/61 graph lookups by name, UX 27 render convention, UX 86 SpecServer/UserHome, Stories rule looking up DDD by name, Increment.stories needs an association collection in harness; ModelNode._copies_on_graph now unused - delete.
- Not reached: CE language part subclasses spell their own lines, Operation.from_python_function, DrawioPage second reader; Stories _StoryMapWriter/render_scenarios/_StepLines/MarkdownScenario parser onto nodes, load_scenarios by name, StoryMapLinks per render keyed by id, DrawIO/Miro increments, CallGraph, Brace/PythonStoryReader second pass, Example names in graph recording; DDD ClassCard building-block subclasses, sketch/drawio readers and writers, copy constructor dropping aggregates, take_root_card stand-ins; UX cli_state, HTML control subclass, Claude Design 28/29/31.

From actions/patterns agent (6b27b7d2):
- Generate -> Format: FidelityGuidance.format/outputs and PracticeGuidance.format return Format objects (guidance.py).
- SketchLens by name: PracticeGuidance.sketch_lens; practice sketch models pass their lens in; then delete SketchLens.of / every.
- Overlays build their pattern and are found by name (#52-58): graph is given pattern objects (pattern_overlays.py).
- graph.practice("ddd") by name in overlays (#61, 62): graph hands overlays the practice objects (graph.py).
- Graph.saved(files) taking the _changing lock, for CheckedGraph (graph.py).
- Violation.practice stored as a string; violations name rules by slug: hold references.
- context_setup and builders (#70-82): not assigned to any agent yet.

From session agent (0e435a9a):
- Board.open_ticket should pass the title and let Sessions.create slug it (space/kanban/board.py) - review entry 26.
- harness/guidance/rule.py:174 and harness/guidance_actions/guidance_actions.py:413 build a ToolCall from a hook payload: use payload.session.
- ChatPointer.in_chat_file has no caller now: delete (harness/agent_tools).
- validate_spec.py:75 mutates repo_path after the session is made: fix the spec.
- Declared-file matching in FidelitySessionOutput: replace with FidelityGuidance.declares after the guidance merge.
- Regenerate the catalog HTML and reinstall after the merges.

From guidance agent (4b6076e9) - lead does these after the merges:
- Actions still read the practice's current fidelity: generate.py:90 item.instructions; document.py:27, improvement.py:34, validate.py:215 item.templates; validate.py:167,169,227 checked_rules/every_rule/checked_rule_collections; validate.py:114 item.format -> self.fidelity_of(item).<x>.
- ddd.py overrides _skip_inactive_fidelity; stories.py and ddd.py call _activate(stage=...): move them onto held fidelities and delete the hooks.
- FidelitySessionOutput declared-file matching -> FidelityGuidance.declares(path).
- Format as a Format object (11 places) - public string read by cdd_guidance and space.
- Clean Engineering companion per fidelity - one CE practice per session needs a design.
- McpServer practice_guidance probe and FileInstallation probing toolset attributes - belong on AgentToolSet (agent_tools).
- Lead tried `self.fidelity_of(item).templates` in the action recipes and reverted it: recipe expansion is AST-based and only expands `item.member` on the loop's item, so the text silently disappears (no spec caught it). The fix is for `each` to hand the recipe the held FidelityGuidance as its item (the fidelity answers instructions, templates, examples, generate_output), plus a spec that asserts the expanded text holds the fidelity's templates and instructions.

From DDD + overlays agent (73ca30e1):
- DDD draw.io output rebuilt on CE's diagram base classes (DiagramModule, DiagramClass), replacing DrawIOAggregateModel, _DiagramWriter, ContextLayout and the arrow_style mismatch: about 850 lines, its own pass.
- CE TypeScript parser drops comments on constructor parameters, so `// foreign Name` can't be recorded by the CE parser yet (c_family_parse.py).
- DDD arcs ride in the first class's doc comment; a typed part needs Python/TypeScript adapters to know DDD.
- SketchLens.of("ddd") still by name (with the other SketchLens items).
- Stale comment naming Graph.write_json in space/kanban save_validation_report_story.test.py:21.

From CE + BDD agent (e880d325):
- CE `folder` fact held as a node id because ddd/model/graph_reading.py:94 copies it; DDD should read the belongsTo edge, then CE stops writing it.
- spec_model_for (Bdd) and code_model_for (CE) are the same suffix lookup: one method on PracticeGuidance.
- Behaviour change: a draw.io edge with no UML marks now reads as association (scanners used to say unknown).
- Catalog and install not regenerated.

From DDD draw.io agent (c297c34e):
- DDD still copies its map into CE modules and classes per render; the review's ideal (practices.md:520) is DDD nodes that are BoundedContext/Aggregate and DiagramModule at once. Needs CE's ContainmentForest and cell ids to nest through .modules, not "/" paths in names.
