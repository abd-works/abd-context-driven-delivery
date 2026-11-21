# Design judgment: harness/guidance, harness/guidance_actions, harness/graph

Read only; no code, test, or document was changed and no spec was run. Every production file in the three folders was read: `harness/guidance` and `harness/guidance_actions` by the lead judge, `harness/graph` Python and the TypeScript under `harness/graph/app` by three sub-judges whose findings the lead spot-checked against the code (about twenty of them, all confirmed). Caller counts come from a word-boundary search of `harness`, `space`, `tools`, `cdd_guidance`, `scripts`, and `story_tests` (without `oss_portal_domain_driven`), with specs and fixtures counted apart. Theme tags: [1] module boundaries, [2] the same work in different shapes, [3] resource orientation, [4] domain orientation.

## Findings

### harness/guidance/guidance.py

- guidance.py:535 `FidelityGuidance` — keep-classes-single-responsibility — 10 public operations and 29 public properties. Four of the operations are one render said four ways (`render` 827, `render_files` 833, `files_to_render` 840, `render_request` 847), each forwarding to `practice_guidance.formats.render` with `fidelity=self`; `PracticeGuidance.render` (513) is a fifth. [3]
- guidance.py:840 `files_to_render` / guidance.py:847 `render_request` — hold-state-on-the-object-not-in-parameters — a `RenderRequest` already holds its fidelity, yet the caller hands the request back to the fidelity, which copies it with `fidelity=self` and forwards. The request could render itself (proposal P7). [3]
- guidance.py:513, 827, 833 `render(...) -> dict` — use-typed-signatures — the published result of a render is a bare `dict` (`{"format", "content"}`), built at practice_formats.py:212 and 232. [3]
- guidance.py:89 `session: Any`, 270 `editor: ClassVar[Any]`, 254 `format_adapters: dict[str, Any]`, 800 `supplements -> list[Any]` — use-typed-signatures — `WorkedSession`, `FormatAdapter`, and `PracticeSupplement` exist and are not used on these signatures. [3]
- guidance.py:574, 701, 726 `clean_engineering` and working_set.py:15 `COMPANION_PRACTICE = "clean_engineering"` — extensions-live-with-the-domain — the framework names one practice by its folder name and gives every fidelity a property named after it, against the card's "the framework names no practice". The concept is the *companion*; `WorkingSet.companion` already says so. [1][4]
- guidance.py:701-713, 728 `_clean_engineering` — hold-state-on-the-object-not-in-parameters — one field holds either the companion's name (a string from the yaml) or the companion fidelity, told apart with `isinstance` on every read and resolved by name on first use. [3]
- guidance.py:648 `practice_guidance` — use-consistent-naming — the practice a thing belongs to is `practice_guidance` here, `practice` on `NamedGuidance`, `PracticeReading`, and `GraphOverlay`, and `owner_practice` on `RulesCollection` (rule.py:181). It is found by walking `parent` with `getattr` rather than held. [4]
- guidance.py:64 `domain_slug`, 494 `domain_markdown_path`, 67 `module_dir` — use-consistent-naming — "domain" and "module" stand for the practice and its folder; the card's words are practice, document, and folder (`document` at 365 is the same file as `domain_markdown_path`). [4]
- guidance.py:637 `is_part_of_practice` / 642 `is_served_on_mcp` — eliminate-duplication — two properties with the same body (`self.practice_guidance is not None`). Both answer hooks `AgentToolSet` declares (agent_tools.py:671, 678), so the duplicate question sits in agent_tools; noted, no fix proposed here. [2]
- guidance.py:522 `scoped_markdown`, 716 `companion_instructions`, 778 `titled_section`, 862 `guidance_parts`, 501 `EXAMPLES_PREAMBLE` — deep-module — public, with no production caller outside guidance.py (`scoped_markdown` is read by 20 spec lines, `companion_instructions` by 1). [1]
- guidance.py:345 `_current_fidelity` — hide-inner-details — reads `vars(self).get("fidelities")` to avoid triggering the markdown collection; the practice works around its own storage. Noted as a symptom of `format` being reachable before the fidelities are read. [3]
- guidance.py:47 `SketchLens` — high-cohesion — a sketch's section reader sits in the practice file; 14 outside uses are all sketch formats. Small; it would sit better beside the sketch document practice, with the practice class holding its lens as now. [1]

### harness/guidance/declared_outputs.py

- declared_outputs.py:182, 188, 194 `output_paths`, `files`, `has_output` — single-boundary / layer-separation — pure pass-throughs to `session_output.written` (space/session's *WrittenFiles*), which in turn reads `fidelity.outputs` and `fidelity.declared.code_folders()` / `.includes()` (practice_session_output.py:471, 499, 592) and builds its own `DeclaredFile` objects from the raw `outputs` (545-557). Two objects each call the other to answer "the files this fidelity declares". [2][1]
- declared_outputs.py:182-198 against worked_session.py:39-61 — seam-names-current-code — the code calls `session_output.written.output_paths()`, but the `FidelityOutput` protocol declares `output_paths()`, `files()`, and `has_output()` on the output itself and no `written`. The protocol does not describe the object used. [1]
- declared_outputs.py:97 `DeclaredOutputs` — keep-classes-single-responsibility — one class is the declared path patterns (`includes`, `file_beside`, `code_folders`) and a view of the session's files (`saved_beside`, `files`, `files_to_review`). [3]
- declared_outputs.py:188, 200 `files() -> dict[str, list]`, `files_to_review` — use-typed-signatures — untyped lists of space/session's `FileEntry`. [3]
- declared_outputs.py:63 `is_written_in`, 139 `file_beside` — deep-module — public; `is_written_in` has no caller outside the file, `file_beside` only specs. [1]

### harness/guidance/worked_session.py and harness/guidance/documents.py

- worked_session.py:23 `WorkedSession` — seam-names-current-code — declares `document_named` on the session; every use goes through `session.paths.document_named` (documents.py:17, practice_formats.py:270), and rule.py:271-275 reads `session.log.injected_rules`, which the protocol does not declare. [1]
- worked_session.py:23 `WorkedSession` against guidance_actions.py:47 `ActionSession` and graph.py:1552 `getattr(session, "graph", None)` — eliminate-duplication — three descriptions of space/session's one *Session* in three framework modules, none complete and two out of step with the code (proposal P9). [2]
- documents.py:14, 20 `document_in`, `load_document` — prefer-class-operations — a file of module functions; `document_in(session, ...)` takes the session as a parameter to call `session.paths.document_named`, which itself calls `load_document` (space/session/session_paths.py). The read belongs on the session's paths, with `load_document` as the one function for no session. [3]

### harness/guidance/practice_formats.py

- practice_formats.py:145, 156, 182 `adapter_class`, `adapter`, `for_file` — use-consistent-naming — three ways to an adapter: its class (or instance), the kept instance, and a new instance per file; `_made_adapter` (285-299) then inspects constructors to decide how to make one. A caller cannot tell which it needs without reading the bodies. [4][3]
- practice_formats.py:153 `importlib.import_module(named[0])` — one-way-deps — the framework imports a practice's adapter module by a `(module, class)` string pair from `format_adapters`; a lookup by name where the practice could hold the class or a factory. [1][3]
- practice_formats.py:173, 193, 220, 247, 265, 292 — hide-inner-details — the adapter contract is read by `getattr` (`suffixes`, `holds_classes_only`, `semantic_type`, `LEAF_EXTENSION`, `create`) and `inspect.signature` (272-283, `previous`, `workspace`), while the `FormatAdapter` protocol (31) declares only `parse` and `render`. The real contract is in the reflection. [3][4]
- practice_formats.py:195 `read(paths, request)` — hold-state-on-the-object-not-in-parameters — `request` is unused; the body reads `self._practice.session`. [3]
- practice_formats.py:201 `render -> dict`; 20 `TextOrData = ... dict[str, Any] | list[Any]` — use-typed-signatures. [3]
- practice_formats.py:43 `Reshaped` against cdd_guidance/actions/render/reshaped_code.py:251 `_FileEdit` — eliminate-duplication — `_FileEdit` keeps `kept`, `added`, `changed` and its caller copies them into a `Reshaped`. Real but small: the edit could hold the `Reshaped` it is building. [2]
- practice_formats.py:106 `keeping_sketch_wording` — deep-module — public, one caller in the file. [1]
- practice_formats.py:23, 31, 60, 63, 72 `ObjectModel`, `FormatAdapter`, `RenderContent`, `NoFormatReads`, `SourceFormatNotSet` — public-seam-only — listed on the card, named by no production code outside the folder (0 uses each). [1]

### harness/guidance/practice_reading.py

- practice_reading.py:57 `PracticeReading` — single-boundary / extensions-live-with-the-domain — the practice's part in the knowledge graph is kept in harness/guidance, which only constructs it (guidance.py:298); harness/graph and the practices read `.reading`. Guidance holds a graph concept (proposal P4). [1]
- practice_reading.py:15, 25, 32 `HoldingGraph`, `HeldRuleRun`, `HeldNodes` — use-typed-signatures — three protocols exist only to avoid the import and understate the type: `in_graph` is typed with two members, while callers use `.nodes`, `.edge_index`, `.add`, `.source_root`, `.holds`. [1][3]
- practice_reading.py:42, 130, 139, 143 `rules_in`, `graph_checks`, `own_graph_checks`, `checks` — use-typed-signatures — all `dict[str, Any]`, because *PracticeGraphRule* lives in harness/graph. `rules_in` is a module function that imports a rules package by a string path. [3]
- practice_reading.py:68 `reads_after: tuple[str, ...]` — hold-state-on-the-object-not-in-parameters — practices named by key and looked up at graph_build.py:460, where the card says a practice is reached by its class. [3]
- practice_reading.py:102 `held_in`, 100 `in_graph` — use-intention-revealing-names — the same object is *PracticeNodes*, `in_graph`, `HeldNodes`, and "the practice's part"; `practice.reading.in_graph.` is written 115 times in production code. [4]
- practice_reading.py:135 `package` — deep-module — public, one caller in the file. [1]

### harness/guidance/rule.py

- rule.py:238 `RuleInjection` — shape-classes-around-resources — a doer over a practice it does not trust the type of: `getattr(practice, "rules")`, `getattr(practice, "fidelities")`, `getattr(fidelities, "entries")`, `getattr(bag.parent, "name")`, `getattr(parent, "slug")` (282-331, 361-369), although it is constructed with a `PracticeGuidance`. The questions (which collections apply to this path, which come before) belong to the practice and its fidelities. [3]
- rule.py:253-331 `bags`, `_rule_bags`, `_bags_for_path`, `_unique_bags` — use-intention-revealing-names — "bag" stands for *RulesCollection*, the name the card and every other file use. [4]
- rule.py:164, 171, 181 `practice_key`, `fidelity_name`, `owner_practice` — put-logic-on-the-owning-resource — a rules collection works out its practice and fidelity by walking `parent` with `getattr` and by reading the practice's `fidelities.current` (176); its holder knows both and could hand them over. [3]
- rule.py:82-88 `Rule.fidelity`, `practice`, `pattern`, `shared` — hide-inner-details — public mutable fields filled in after construction by the graph (`practice`, `pattern`, `shared` are assigned nowhere in harness/guidance), so a `Rule` means two things: a line of a practice document, and a graph rule's provenance (proposal P5). [2]
- rule.py:58, 76 `AppliesTo.from_value(fence_fields: AppliesTo | dict | None)` — use-typed-signatures — accepts three shapes and both `alwaysApply` and `always_apply` spellings. [3]
- rule.py:110 `from_bullet` — deep-module — public, one caller in the file. [1]

### harness/guidance/schema.py

- schema.py:47 `required_relationships` with 27 `_DESCRIBING` — eliminate-duplication — one of three definitions of "a field that is a relationship"; the others are schema_edges.py:158 and schema_rules.py:317 with `_TYPE_FIELDS` (23), each parsing the raw `fields: list[tuple[str, str]]` again with a different exclusion list (proposal P6). [2]
- schema.py:38 `SchemaType.fields: list[tuple[str, str]]`, 86 `Schema.types` — hide-inner-details — the raw written value of every field is the public contract, which is why three readers parse it. [3]
- schema.py:114 `fidelity_errors` — no-use-delete — only caller is practice_schema_spec.py. `fidelities()` (103) is then used only by `node_fidelities`. [1]
- schema.py:83 `_loaded: ClassVar[dict[Path, Schema]]` — use-explicit-dependencies — a process-wide cache on the class; a schema file edited while the server runs is never read again. [3]

### harness/guidance/stages.py

- stages.py:131 `ApproachStage._placed` — put-logic-on-the-owning-resource — reads every action of the catalogue and never uses the stage's name, so `steps`, `actions`, `producing_actions`, and `actions_with_formats` (155-178) answer the same lists on all three stages and are recomputed on every read. They are the catalogue's answers, sent three times. [3][2]
- stages.py:18-21 `GENERATE`, `VALIDATE`, `RENDER` — single-boundary — action names as framework constants beside a catalogue whose card says "no list of action names is kept beside the catalogue"; space/kanban/ticket.py uses them 18 times to find actions by name. [1][3]
- stages.py:27-29, 42 `on_stage(rank, *traits: str)` — provide-meaningful-context — traits are bare strings and the order is a hand-kept integer across action folders. [4]
- stages.py:82, 112 `covering` / `_CoveredScope` — class-not-property-instance-or-subtype — a subclass made only to set one field that the constructor could take. [2]

### harness/guidance/action_catalogue.py

- action_catalogue.py:33, 77, 92, 22, 14 `Action`, `FidelityAction`, `FidelityActions`, `ActionRunner`, `WorkedFidelity` — class-not-property-instance-or-subtype — five types to say `fidelity.actions.generate(...)`. `FidelityAction` only binds an `Action` to a fidelity, and `Action.run_on` (62) only forwards to `catalogue.runner.run(action, fidelity, arguments)`. [2][3]
- action_catalogue.py:98 `FidelityActions.__getattr__` — use-typed-signatures — an action is looked up by attribute name at run time, so `fidelity.actions.generate` has no type and a misspelt name fails only when called. [3]
- action_catalogue.py:54 `Action.operation` — hide-inner-details — hands out the raw function from `vars(toolset_class)`; stages.py:133 and guidance_actions.py:905, 911 inspect it. [3]
- action_catalogue.py:168, 171 `has`, `action(name)` — no-use-delete — no production caller (specs only). `runner` (134), `fidelity_actions` (141), `run_on` (62) have none outside the file. [1]

### harness/guidance/practice_catalogue.py, working_set.py, practice_supplement.py

- practice_catalogue.py:52, 57, 62 `answering`, `practice_answering`, `named` — use-consistent-naming — three lookups by slug whose difference (exact slug; the practice of a slug; slug or bare fidelity name) the names do not say. [4]
- practice_catalogue.py:124-139 `create` — keep-operations-single-responsibility — makes a practice and then walks `working_set.names` to make the practices it works with, a second way to build a set beside `create_all` (141). [2]
- working_set.py:37 `names`, 43 `hold(practices: Mapping[str, PracticeGuidance], ...)` — hold-state-on-the-object-not-in-parameters — the set is handed over as a mapping by key and each practice looks its partners up by name (`extends`, `COMPANION_PRACTICE`). [3]
- practice_supplement.py:77, 92, 103 `hold_supplemented`, `supplemented_practices`, `text_for` — deep-module — public on a public class, called only from other files of harness/guidance. [1]
- practice_supplement.py:111-118, 136-139 — eliminate-duplication — `rules_for` and `checked_rule_collections` parse the same sections into a new `RulesCollection` on every call (guidance.py:795 calls `rules_for` each time a fidelity's rules are read). [2][3]

### harness/guidance_actions/guidance_actions.py

- guidance_actions.py:47 `ActionSession` — use-typed-signatures / seam-names-current-code — `log`, `graph`, `paths`, `session_files` are `Any` and `practices` is `Mapping[str, Any]`; the code reads `session.record.fields` (665) and `getattr(works_in, "stories", None)` (625), neither of which the protocol declares (`fields` is declared instead). [3][1]
- guidance_actions.py:614-619, 588 `self._action.graph.applied_patterns...`, `graph.refresh` — low-coupling — guidance_actions calls harness/graph's *PatternOverlays* (`recorded_for`, `pattern_named`, `names`) and `Graph.refresh` through an `Any`, a dependency its card does not list. [1]
- guidance_actions.py:728, 733, 738 and `_session` — use-consistent-naming — four ways to the action's session: `session_for(call)` (takes a call and ignores it), `works_in` (may be none), `session` (raises), and `_session`. `works_in` has no caller outside the file. [4][3]
- guidance_actions.py:178 `GuidanceArgument(command, practices: Callable[[], PracticeSet], session_name)` — hold-state-on-the-object-not-in-parameters — made by `WorkList.take` (375) from the work list's own `practice_set` and `session_name`, used for two reads, and dropped; it parses `command.guidance` again on each of `text` and `items`. [3]
- guidance_actions.py:327 `PRACTICE_CATALOGUE.create_all()` in `_refuse_turned_off` — hold-state-on-the-object-not-in-parameters — builds every practice of the catalogue to word one refusal; `PRACTICE_CATALOGUE.practice_classes` or a held set would answer it. [3]
- guidance_actions.py:344 `WorkList` — keep-classes-single-responsibility — 9 public operations and five parallel pieces of state (`_items`, `_listed`, `_worked_at`, `_formats` by list position, `text`), with three ways in (`take`, `take_listed`, `take_fidelity`). `_entry(index)` (413) sets `writer.format` as a side effect of reading an entry. [3]
- guidance_actions.py:355 `worked_on: Any`, 86 `_NOTHING_WORKED_ON` — use-typed-signatures — holds a string, a list, or a fidelity, and is compared with the next guidance at 763 to decide whether to read it again. [3]
- guidance_actions.py:37-44, 147 `GuidanceEntry`, `GuidanceArg`, `ListedGuidance`, `WorkedGuidance`, `ArgumentEntry` — use-intention-revealing-names — five union aliases for "guidance at some stage of being read", three of which include `str`; operations then test `isinstance` (441-465, 482, 672, 787, 886). [4][2]
- guidance_actions.py:508 `self._session.practice(practice.key)` — hold-state-on-the-object-not-in-parameters — the practice object is in hand and its key is passed so the session can look it up (for the lookup's side effect). `session_practice` (776-781) does the reverse search by identity. [3]
- guidance_actions.py:547 `source_label` — prefer-class-operations — a module function taking `content, paths`, the same pair `ActionFiles.read` takes. [3]
- guidance_actions.py:87 `PATHS_NOTE` — no-use-delete — referenced nowhere. `practice_slugs` (772) has one spec caller and no production caller. [1]
- guidance_actions.py:853 `session_context` — layer-separation — forwards to `self.brief.session_context`; kept because agent_tools reads it by name. [1]
- guidance_actions.py:815 `inner.mode = "tool"` — hide-inner-details — a field of the toolset set from outside after construction. [3]
- guidance_actions.py:899 `FidelityActionRunner` — shape-classes-around-resources — a stateless doer (`run(action, fidelity, arguments: dict)`) that inspects the operation's signature twice (905, 911) and makes the action with no call, so a build it starts never runs in a worker. [3]
- harness/guidance_actions/__init__.py:2 `from .guidance_actions import *` — no-legacy-api-after-refactor — a star re-export with no `__all__`: 71 imports use the package path and 6 the module path, and every module-level name (the aliases, `NamedGuidance`, `GuidanceArgument`) is importable. harness/guidance's `__init__` says "import each from its own module". [1]
- card `harness/guidance_actions/.context/module-context.md` — public-seam-only — the seam lists `_made_for` and `_tool_inside`, private by name, as what subclasses call; cdd_guidance calls `_work_on` 14 times and `_made_for`, `_tool_inside` twice each. A subclass seam that is underscore-named is counted as hidden while being the most-used entry. [1]

### harness/graph/graph.py

- graph.py:341 `Filter` — keep-classes-single-responsibility — two jobs: the choices the explorer offers (`select_*`, `change_practices`, `offered_node_types`) and the match test built from a request (`narrowed_by`, `matches`, `lists`, `collect`). [3][4]
- graph.py:921 `GraphExplorer.filter` — no-use-delete — production never selects on the graph's own filter; `select_violations` and `select_relationships` are called only from specs, so the "chosen here hold over the request" branches (478-481) live for specs. [1][3]
- graph.py:1724, 1735, 1741 `filter: dict | None` — use-typed-signatures — `FilterRequest` (324) models this and the three published operations take a bare `dict`; the TypeScript side therefore builds `Record<string, unknown>` (app/filter/filter-selection.ts:13). [2][3]
- graph.py:1514 `Graph` — deep-module — 18 public operations, 14 of them one-line forwards to `self.reads` or `self.explorer`; `practice(key)` (1574) duplicates `practices.named(key)` (graph_practices.py:36). [1][2]
- graph.py:1548-1552 `Graph.for_call` — low-coupling — `getattr(session, "graph", None)` reaches into space/session's *Session* by attribute name. [1]
- graph.py:1540 `kept_in` — use-explicit-dependencies — a public field set after construction by space/session/practice_outputs.py:61, just before `reads.open_saved`; `saved_file` depends on that order. [3]
- graph.py:1597-1656 `call` — hold-state-on-the-object-not-in-parameters — `call` passes Graph → GraphReads (9 methods) → `GraphBuild.load/refresh` → `GraphBuild.run`, where its only use is `call.request.answers_a_chat` (graph_build.py:380). [3]
- graph.py:125 `Source.align_to_label`, `align_to_table_row`, `align_to_example_export`, `align_to_declaration` — extensions-live-with-the-domain — Stories knowledge (step labels, `+` underline marks, `export const` fixtures) in the framework; only caller is stories/model/story_recording.py:259-267. [1][3]
- graph.py:216, 236 `root` parameter — hold-state-on-the-object-not-in-parameters — the caller passes the folder `Node.place` already gave the source. [3]
- graph.py:131 `Source.__init__(path, line_start, line_end)` — use-consistent-naming — stored as `file`, `start_line`, `end_line`; `Location` and `SavedNode` say `file`, `line`, `end_line`. Three vocabularies for one place in a file. [2][4]
- graph.py:163 `Source.contents`, 49 `Call.order` — no-use-delete — no reader anywhere. [1]
- graph.py:166, 171 `load_calls`, `insert_calls` — hide-inner-details — public, called only from `Source.text`. [1]
- graph.py:57 `_under_any`, 62 `_decorated_end`, 1507 `_where_it_sits` — prefer-class-operations — module functions each with one caller in one class. [3]
- graph.py:57, 534, 540, 1380, 1395 and saved_graph.py:369-376 — eliminate-duplication — "is this file under one of these folders" is written four times. [2]
- graph.py:991 `_HeldNodes`, 1087 `PracticeNodes`, 1206 `PracticeLoading` — shape-classes-around-resources — `_HeldNodes` is the resource; `PracticeNodes` forwards 8 one-liners to it and `PracticeLoading` 4 more, handed the same private collection. [2][3]
- graph.py:630, 1100, 1219, 1349, 1452 with graph_build.py:431 `build.changed()` — temporal-independence — whether the worker's last answer is stale depends on every mutator remembering this call; `merge_fact`'s `setattr` path (655) and `root.data` assignments (1416, 1433) change the graph without it. [3]
- graph.py:620 `Node.data` — hide-inner-details — a public dict assigned from outside beside `set_fact`; `Node.passing_rules` (723) is used only by a spec. [1]
- graph.py:679 `Node.schema`, 1310 `PracticeRuleRun.checks -> dict` — use-typed-signatures. [3]
- graph.py:943 `GraphExplorer.overlay_of` — put-logic-on-the-owning-resource — "is this an overlay root" is *PatternOverlays*' rule, which already owns `root_of`. [3]
- graph.py:971, 980 `explorer.explorer_trees`, `explorer.explorer_branch` — use-intention-revealing-names — the name repeats its owner. [4]
- graph.py:1454 `PracticeRestore.links(saved: SavedPractice | PracticeChanges)` — class-not-property-instance-or-subtype — relies on two classes happening to share `.edges` and `.violations_by_node`. [2]

### harness/graph/graph_build.py, graph_worker.py, graph_reads.py, graph_practices.py

- graph_build.py:385-389, 402-405 — eliminate-duplication — the in-process branch of `run` and `carry_out(order)` are the same three steps. [2]
- graph_build.py:279, 391, 425 — use-consistent-naming — three `carry_out`s mean different things; the graph before the step is `before`, `state`, and `saved`. [4]
- graph_build.py:232 `HeldAnswer` — use-intention-revealing-names — the file of the worker's last answer plus a change counter; used at one place, yet on the card's seam. [1][4]
- graph_build.py:271 `WorkerBuild`, 38 `WORKER_MODULE` — deep-module — used only inside the file. [1]
- graph_build.py:26 imports `GraphLoaded` from explorer.py — high-cohesion — the build depends on the explorer's file for a load's result. [1]
- graph_build.py:398-400, 435 `schema_edges.syncs = False` — hold-state-on-the-object-not-in-parameters — a field set on the shared graph for one job and never restored, beside two other pause mechanisms (model_node.py:333 `_SCHEMA_SYNC_PAUSED`, `SchemaEdges.held()`). [3][2]
- graph_worker.py:29 `importlib.import_module(module)` — one-way-deps — the one place these files load cdd_guidance code, by module names the order carries; no static import of space, tools, or cdd_guidance exists in harness/graph. Accepted by CDR 0001; noted. [1]
- graph_reads.py:21, 34 `WorkingCopyRead`, `FilesRead` — shape-classes-around-resources — frozen data bags, each built at one call site and unpacked by one method, on the card's seam with no other user. [2][3]
- graph_practices.py:80, 87 `reopen(saved, folder)`, `hold(saved, folder)` — hold-state-on-the-object-not-in-parameters — every caller passes `graph.scope.folder`, which the object can read. [3]
- graph_practices.py:30-34 `held`, `opened`, `chosen` — hide-inner-details — public mutable dicts read directly 36 times in production code. [1][4]

### harness/graph/saved_graph.py, explorer.py, skipped_folders.py

- saved_graph.py:423 `PracticeChanges` against 144 `SavedPractice` — eliminate-duplication — both hold nodes, edges, violations, and root facts and parse the same records; `violations` is a list in one record and a dict in the other. [2]
- saved_graph.py:157, 437 `from_fields` — limit-operation-parameters — six parameters each, set as public fields after an empty constructor. [3]
- saved_graph.py:93 `SavedNode` — eliminate-duplication — flat `file`, `line`, `end_line` while `Node` holds a `Source`; the mapping is hand-written both ways (116-127, graph.py:1442-1451). [2]
- saved_graph.py:294-301 `SavedGraph.from_text` — single-boundary — a second parser of the `return_nodes` data shape. [2]
- saved_graph.py:497 `RecordChanges` — use-typed-signatures — `Any` on every member. [3]
- explorer.py:114 `PracticeInventory(graph, practice)` — the `graph` parameter is never read. [3]
- skipped_folders.py:48, 55 `skips_folder`, `scanned_files` — prefer-class-operations — module functions; two practices repeat the `os.walk` loop around `skips_folder` instead of calling `scanned_files`. [2][3]

### harness/graph/schema_edges.py, schema_rules.py, schema_conformance.py

- schema_edges.py:55, 30, 76, 71 `_NODE_TYPES`, `CHILD_LISTS`, `_EVIDENCE_KINDS`, `_PHASES` — extensions-live-with-the-domain — the framework lists practices' types and edge kinds (`OoadClass`, `PlaywrightSpec`, `NodeRoot`, `scenarios`), against the card's "the graph names no practice's types". [1]
- schema_edges.py:298, 319 `_matches`, `_epic_uses` — extensions-live-with-the-domain — a switch on edge kind that reads Clean Engineering and Stories attributes through `getattr`. [1][3]
- schema_edges.py:168 `NodeEvidence` — shape-classes-around-resources — a doer over a `ModelNode`, read through `getattr(..., default)` and `source.__dict__`. [3]
- schema_edges.py:82 `SchemaKey` — single-boundary — the key-to-node-type mapping of `Schema.types` lives outside `Schema`, so every reader wraps keys again. [2]
- schema_rules.py:70 `for_node(self, node)` — use-typed-signatures — untyped public parameter. [3]
- schema_rules.py:341-360 `rules_of`, `supertypes_of`, `type_names`, `merged` — prefer-class-operations — public module functions taking a `Schema`, called only in the file. [3]
- schema_rules.py:176 `_stage_of` — hold-state-on-the-object-not-in-parameters — parses `practice.type` strings and looks the practice up by key. [3]
- schema_rules.py:139, 273 `_prose_collections`, `_longest_prose` — the module's own Constraint — nested `getattr(..., None)` duck-typing of guidance, supplements, and `Rule`, whose members are declared. [3]
- schema_rules.py:288 `SchemaOverlays.__init__(key, ...)` with pattern_overlays.py:63 `practice_file(practice_key, name)` — hold-state-on-the-object-not-in-parameters — a practice key is kept to rebuild a path when both callers hold the practice. [3]
- schema_conformance.py:64 `getattr(node, "phase", "")` — the module's Constraint and CDR 0002 — `phase` is a saved fact, so on a plain node from a worker refresh this answers `""` and the phase-keyed requirement skips that step silently. A likely defect. [3]
- schema_conformance.py:84 `ConformsToSchema.rule` — do-not-invent-parallel-object-models — the only check that holds its `Rule`; every other check is joined to its text by slug. [2]

### harness/graph/practice_rule.py, graph_rules_collection.py, rule_context.py, rule_fixture.py, violation.py

- practice_rule.py:22 `check_practice -> list[(node_id, message)]` — hold-state-on-the-object-not-in-parameters — all ten implementations hold the node, and graph.py:1341 looks it up again by id. [3]
- practice_rule.py:19 `check -> list[str]` with violation.py:211 `Finding(str)` — use-typed-signatures — a finding is a string subclass carrying lines, detected with `isinstance`. [3][4]
- graph_rules_collection.py:99 `GraphRulesCollection(RulesCollection)` — class-not-property-instance-or-subtype — inherits an `@agent_toolset` markdown collection (`inject_rules`, `applies_to`, `from_markdown`) to reuse a dict, then filters with `isinstance` (178, 181) because the base allows nesting. [2][4]
- graph_rules_collection.py:114 `from_node` — do-not-invent-parallel-object-models — a rule's text, its check, and where it applies are three objects joined per node by slug string. [2]
- graph_rules_collection.py:181 `record_violation(slug, message)` — hold-state-on-the-object-not-in-parameters — graph.py:1376 holds the `GraphRule` and passes its slug back for lookup. [3]
- graph_rules_collection.py:91, 193 `clear_violations` — no-use-delete — no caller, specs included. [1]
- rule_context.py:60, 57 `children`, `child_count` — eliminate-duplication — the same answer as `targets` (35), found by scanning every edge of the kind per call. [2]
- rule_context.py:25, 53 `source_root`, `node()` — no-use-delete — no rule reads either. [1]
- rule_fixture.py:48 `SchemaRuleRun` — use-consistent-naming — a second "rule run" beside `PracticeRuleRun`; about 20 specs write `SchemaRuleRun(rule, RuleCheckContext(practice, None))`. [2][4]
- violation.py:162 `Violation.by_rule` — prefer-instance-operations — a static grouping function, not a factory. [3]
- violation.py:227 `NodeViolation.__init__` — hide-inner-details — passes a dummy `FoundBy("")` to the base and overrides all four properties. [2]
- violation.py:61, 73 `FoundOn`, `FoundBy` — shape-classes-around-resources — behaviour-free records built nested at every site. [3]

### harness/graph/pattern_overlays.py, patterns_file.py, edge.py, model_node.py

- pattern_overlays.py:58 `adds_rules_to(node: Any)` — use-typed-signatures — and `Any` is not imported (line 14 imports only `TYPE_CHECKING`); it parses only because annotations are deferred. [3]
- pattern_overlays.py:49, 183 `getattr(self.pattern, "pattern", None)`, `getattr(supplement, "graph_overlay", None)` — use-typed-signatures — "guidance that owns a graph overlay" has no type. [3][4]
- pattern_overlays.py:253 `pattern_named` — no-legacy-api-after-refactor — a public wrapper returning `self._pattern(name)`. [2]
- pattern_overlays.py:69, 83, 188-221 `roles`, `record_in`, `record_content`, `_recorded_in`, `_recording_instructions`, `recorded_for`; patterns_file.py:17 `PatternsFile` — high-cohesion — recording which patterns content was generated with is Generate's job; callers are generate.py:49 and guidance_actions.py:616 only, and no graph build uses it. [1]
- edge.py:125, 130, 135 `Edge.saved`, `key`, `record` — keep-classes-single-responsibility — one class for two shapes: `saved` works only with node ends, `key` and `record` only with id ends. [2]
- edge.py:32 `EDGE_ORDER` — extensions-live-with-the-domain — public, used only in the file, and lists every practice's edge kinds. [1]
- edge.py:28 `Display = str` — provide-meaningful-context — `"direct"`, `"grouped"`, `"relationship"` are bare literals across four files. [4]
- edge.py:150 `EdgeIndex.types` — hide-inner-details — a public mutable dict read from four other files. [3]
- model_node.py:176, 301 `_schema_edge_fields`, `subtree()` — extensions-live-with-the-domain — the base names Clean Engineering attributes and Stories' `examples` dict. [1]
- model_node.py:207, 234, 123 `finish_building`, `keeps_list`, `record_all` — deep-module — public, called only inside the file. [1]

### harness/graph/app (TypeScript)

- graph/graph-failures.ts:21 `GraphFailures` — eliminate-duplication — re-implements the generated `ChatToldFailures` (`@cdd/cdd-page-failures`): the same told-chat set, send, and fallback. The kanban and story-map pages extend the base; only this app copies it. `reasonOf` (9) and `chatOfPage` (12) are copies too. [2]
- graph/graph-failures.ts:27-28 `api`, `chat` — hide-inner-details — public only so `correctInChat` (source/violation-chat.ts:13, 18) can build its own chat client. [1][3]
- graph/graph-selection.ts:6-28, explorer/source-pane.ts:86-102, graph/GraphView.tsx:70-72 — shape-classes-around-resources — the explorer tree is a bare `ExplorerEntryData[]` acted on by free functions in three files, with two ways to find the rules holder (`child.name === 'rules'` and `child.type === 'rules'`). [3][2]
- graph/graph-selection.ts:44-50 `ruleHits` — no-legacy-api-after-refactor — accepts a single `violation?: string` that the data type does not have; only a test fixture sets it. [2]
- explorer/*.ts `Held<T>` — eliminate-duplication — declared five times and inline a sixth. [2]
- explorer/explorer-filter.ts:5, graph-load.ts:7, load-status.ts:4, overlays.ts:2, page-folder.ts:2, source-pane.ts:4 — use-explicit-dependencies — every explorer class reads the globals `graphs`, `failures`, `api` rather than taking them in its constructor. [3]
- explorer/graph-load.ts:91-104 `showLoaded` against overlays.ts:87-94 `showApplied` — eliminate-duplication — the same sequence twice. [2][3]
- explorer/source-pane.ts:61, 70 `rulesIn(trees)`, `chooseRule(trees, name)` — hold-state-on-the-object-not-in-parameters — App.tsx passes `filter.trees` on every call. [3]
- explorer/source-pane.ts:6 and source/call-expansion.ts:1 — layer-separation — state and catalogue files import types from the view file `SourceView.tsx`. [1]
- explorer/overlays.ts:82 `addNamed` and filter/FilterView.tsx:54 — likely defect — both compare a display label ("Lern domain driven") with an overlay id (`lern_domain_driven`); they never match, so an applied overlay stays in the catalogue. Read, not run. [2]
- explorer/inventory-bundle.ts:12-16 — no-legacy-api-after-refactor — handles an inventory answered as a bare practices map, a shape Python no longer answers. [2]
- filter/filter-selection.ts:13 `nodeFilter` — use-typed-signatures — returns `Record<string, unknown>` and renames `node_types` to `types`; the cause is the Python `filter: dict`. [2][4]
- filter/FilterView.tsx:150-158 `overlayLabel` — eliminate-duplication — exactly `overlayPathLabel` (labels/overlay-labels.ts:8). [2]
- source/call-expansion.ts:61 `FoldMember`, 73 `Body` — eliminate-duplication — `FoldMember` re-declares the adapter's `NodeSourceData`; one member is reshaped three times across `NodeSourceData`, `Body`, and `SourceCallout`. [2]
- source/call-expansion.ts:95 `calloutsIn` (5 parameters), 102 `calloutsOn` — hold-state-on-the-object-not-in-parameters — four of five parameters describe one span of source, and `bindings`, `stack`, `seen` are one scan's state handed down three layers. [3]
- source/source-callouts.ts:140-174, 234 `Opening` with `calloutsBlock`, `calloutSection`, `calloutRow` — shape-classes-around-resources — a state bag passed to every DOM-building function, with a module-level WeakMap (32). [3]
- source/source-callouts.ts:23, 24, 176; source/SourceView.tsx:34; source/source-folding.ts:21; graph/query-progress.ts:1; graph/graph-api.ts:7; serve-port.ts — deep-module — `CALLOUT_MARK`, `CALLOUT_LABEL`, `CALLOUT_MENU`, `SourceHostProps`, `headingRanges`, `QueryStep`, `GraphCallFailure`, `PORT_ARGUMENT`, `CDD_HOME_ARGUMENT` are exported with no importer. [1]
- serve-port.ts — high-cohesion — the Files app and the session board import it from this folder; it is not explorer code. [1]
- graph/query-progress.ts:50, LoadProgressView.tsx:61, explorer/load-status.ts:8 — provide-meaningful-context — `'Loading the graph…'` is written three times and compared against to decide a headline. [2]
- source/violation-prompt.ts:31, 51 `input`; graph/graph-selection.ts:44, 54 `node` — use-consistent-naming — the same value is `correction` elsewhere; the `node` parameter is a rule. [4]

### Module cards

- harness/graph/.context/module-context.md (Seam) — public-seam-only — about 45 terms, including ones no other module uses (`HeldAnswer`, `WorkerBuild`, `WorkingCopyRead`, `FilesRead`, `BuildTask`, `BuildStep`, `PracticeRestore`); it omits the published `graph.practice_names`. [1]
- harness/guidance/.context/module-context.md (Seam) — deep-module — the card accepts "wider than 40% public by design" (185 of 440 methods, 42%, against the rule's 35%). The private-by-name fixes in section B and proposals P4, P7, P8 are what would bring it under without that exception. [1]

## Fixes that change no design

Each is local: no class added or removed, no seam another module calls changed (except where a caller list is given).

**harness/guidance**

1. Make private (rename with a leading underscore): `FidelityGuidance.titled_section`, `guidance_parts`, `companion_instructions`; `PracticeGuidance.EXAMPLES_PREAMBLE`; `RenderRequest.keeping_sketch_wording`; `DeclaredFile.is_written_in`; `PracticeReading.package`; `Rule.from_bullet`; `Schema.fidelities`; `ActionCatalogue.runner`, `fidelity_actions`; `Action.run_on`. Callers: all inside harness/guidance (guidance.py, practice_formats.py, declared_outputs.py, practice_reading.py, rule.py, schema.py, action_catalogue.py). Specs: guidance_spec.py or practice_guidance_behavior_spec.py reads `companion_instructions` once. Risk: none. `scoped_markdown` is the same case in production but 20 spec lines read it; make it private only if those specs move to `instructions`.
2. Delete `Schema.fidelity_errors` (schema.py:114); move its check into practice_schema_spec.py as spec support. Risk: none.
3. Delete `ActionCatalogue.has` and `ActionCatalogue.action(name)` (action_catalogue.py:168, 171) with their examples in action_catalogue_spec.py (2 and 3 lines). Risk: none in production; confirm no TypeScript adapter publishes them.
4. Drop the unused `request` parameter of `PracticeFormats.read(paths, request)` (practice_formats.py:195). Callers: guidance.py:845; two spec lines. Subclasses in cdd_guidance (`stories_formats.py`, `clean_engineering_formats.py`, `ddd_formats.py`) must be checked for an override that uses it before removing. Risk: low.
5. Type `Guidance.session` as `WorkedSession | None`, `FidelityGuidance.supplements` as `list[PracticeSupplement]` (under `TYPE_CHECKING`), `DeclaredOutputs.files` and `files_to_review` with a small `Protocol` for the entry (`path`). Risk: none at run time.
6. Bring the protocols into step with the code: `WorkedSession` declares `paths` (with `document_named`) and `log`, and drops the unused top-level `document_named`; `FidelityOutput` declares `written` (with `output_paths`, `files`, `has_output`) and drops those three from itself. Files: worked_session.py only. Risk: none at run time; a type checker will then see the real shape.
7. Rename `bag`/`bags` to `collection`/`collections` in `RuleInjection` (rule.py:253-384), and replace the `getattr(practice, ...)` reads with direct attribute reads, since the constructor types it `PracticeGuidance | None`. Specs: rule_spec.py if it names `_bags_for_path`. Risk: low; the `getattr` defaults also cover fixture guidance that is not a practice, so run rule_spec and hook_spec.
8. `StageScope`: give the constructor a `covers: str = ""` parameter and delete `_CoveredScope` and `covering` (stages.py:82-117). Callers: stages.py:203-205 only (the card names `covering`; update it). Risk: none.

**harness/guidance_actions**

9. Delete `PATHS_NOTE` (guidance_actions.py:87). Risk: none.
10. Delete `GuidanceAction.practice_slugs` (772) and its one example in guidance_actions_spec.py. Risk: none.
11. Make `WorkList.take_listed`, `take_fidelity`'s only outside caller explicit: both are called only inside the file (`_inside`, `FidelityActionRunner.run`); the card names `take_fidelity`, so keep that and make `take_listed` and `session_name` private. Risk: none.
12. Merge `works_in` into `_session` reads inside the file, or the reverse: keep `works_in` and delete direct `_session` reads outside `GuidanceAction` itself (`ActionFiles`, `SessionBrief` already use `works_in`). Choose one word. Risk: none.
13. In `_refuse_turned_off` (327), replace `PRACTICE_CATALOGUE.create_all()` with a walk of `PRACTICE_CATALOGUE.practice_classes` made once per refusal, or keep the set on the `GuidanceArgument`. Risk: low; the message needs the practice's slug and its fidelities' slugs, so one set must still be made.
14. Replace `from .guidance_actions import *` with the explicit names the card's seam lists. Callers: none change if the list is complete (71 package-path imports name `GuidanceAction`, `GuidanceArg`, `WorkedGuidance`, `ActionSession`, `ActionWorksInNoSession`, `GuidanceCommand`, `WorkList`, `source_label`). Risk: low; run the unit tier to find a missed name.
15. Bring `ActionSession` into step: declare `record` (with `fields`) and `stories`, drop `fields`. Risk: none at run time.

**harness/graph (Python)**

16. Delete `Source.contents` and `Call.order` (graph.py:163, 49); delete `GraphRule.clear_violations` and `GraphRulesCollection.clear_violations` (graph_rules_collection.py:91, 193). No callers. Risk: none.
17. Make `Source.load_calls`, `insert_calls` private; move `_under_any` onto `PracticeLoading`, `_decorated_end` onto `Source`, `_where_it_sits` onto `_HeldNodes`. Risk: none.
18. Delete `Node.passing_rules`; graph_view_spec.py (2 uses) reads `node.rules.passing_slugs`. Risk: none.
19. Drop the unused `graph` parameter of `PracticeInventory` (explorer.py:114; caller graph.py:891). Risk: none.
20. Type `adds_rules_to(self, node: Node)` (pattern_overlays.py:58) and `for_node(self, node: Node)` (schema_rules.py:70), `Node.schema -> PracticeSchema`, `PracticeRuleRun.checks -> dict[str, PracticeGraphRule]`. Risk: none.
21. schema_conformance.py:64: read `node.get_fact("phase", "")`. Add an example on a restored graph to schema_conformance_spec.py. Risk: findings appear on refreshed graphs that were skipped; that is the fix.
22. `graph.py:1376`: call `rule.record(message)` on the rule in hand; delete `GraphRulesCollection.record_violation`. Risk: none.
23. Drop `folder` from `GraphPractices.hold` and `reopen`; read `self._graph.scope.folder`. Callers: graph.py:1590, graph_build.py:301 and 409, graph_reads.py:77. Risk: `reopen` must still run after `open` has set the scope, as today.
24. Delete `RuleCheckContext.node` and `source_root`; construct `RuleCheckContext(practice)`. Callers: graph.py:1337, rule_fixture.py:41, and about ten rule specs under cdd_guidance. Risk: low.
25. Merge `RuleCheckContext.children` into `targets`; drop `child_count`. Callers: stories/rules/scenarios.py, ddd/rules/tactical.py:46, ux/rules/screen_rules.py:23, clean_engineering/rules/module_naming_rules.py:73. Risk: `targets` reads graph-wide edges, so confirm the same hits in scenarios_spec and stories_rules_spec.
26. Rename `_pattern` to `pattern_named` and delete the wrapper (pattern_overlays.py:253). Risk: none.
27. Make private: `EDGE_ORDER`; `rules_of`, `supertypes_of`, `type_names`, `merged`; `finish_building`, `keeps_list`, `record_all`; `HeldAnswer`, `WorkerBuild`, `WORKER_MODULE` (graph_worker_heavy_spec.py imports and patches `WorkerBuild`); take the last three and `WorkingCopyRead`, `FilesRead` off the card's seam, and add `graph.practice_names`. Risk: none.
28. Merge the duplicate in `GraphBuild`: `run`'s in-process branch calls the private method `carry_out(order)` calls. Risk: none.
29. Move `GraphLoaded` and `GraphSaved` out of explorer.py into graph_reads.py. Imports change in graph.py, graph_build.py, graph_reads.py. Risk: none.
30. Delete `Graph.practice(key)`; callers use `graph.practices.named(key)`. Production: app/filter_choices_record.py:61, ddd/model/graph_reading.py (2), two fixture projects. Specs: about 40 files, a mechanical replace. Risk: wide but trivial.
31. One `rule_by_slug`: delete `ce_rule_by_slug`, `bdd_rule_by_slug`, `ddd_rule_by_slug`; specs read their package's `BY_SLUG[slug]`. Risk: none.

**harness/graph/app (TypeScript)**

32. Unexport `GraphCallFailure`, `CALLOUT_MARK`, `CALLOUT_LABEL`, `CALLOUT_MENU`, `headingRanges`, `SourceHostProps`, `QueryStep`, `PORT_ARGUMENT`, `CDD_HOME_ARGUMENT`; delete `FoldMember.classes`. Risk: none.
33. Delete `overlayLabel`; use `overlayPathLabel` (FilterView.tsx:54). Compare overlay ids, not labels, in FilterView.tsx:54 and overlays.ts:82, and add an app.test case that an applied overlay leaves the catalogue. Risk: low; it is a behaviour change that fixes the likely defect.
34. One `Held<T>` in a shared explorer file; one `LOADING_GRAPH` constant; export `LINE_HEIGHT` from source-callouts for SourceView. Risk: none.
35. Use `reasonOf` from `@cdd/cdd-page-failures` and `chatOfPage` from `@cdd/cdd-shared`; delete the local ones. Files: about 8 and graph-failures.test.ts. Risk: low; check a `?chat=` value with spaces.
36. Rename `input` to `correction` (violation-prompt.ts) and `node` to `rule` (`ruleHits`, `selectionForRule`); drop the `violation?: string` branch of `ruleHits` with the fixture line at app.test.tsx:244; drop the bare-map branch of `normalizeInventoryBundle` with inventory-bundle.test.ts lines 12-18. Risk: low.

## Proposed design changes

### P1. One rule: its text, its check, and its findings

**Problem.** A rule is three objects joined by slug string. `Rule` (harness/guidance/rule.py:81) is the text. `PracticeGraphRule` (harness/graph/practice_rule.py) is the check, found by `checks.get(slug)`. `GraphRule(Rule)` is the rule on one node, built in `GraphRulesCollection.from_node` (graph_rules_collection.py:114) by looking the text and the check up by slug again; schema_rules.py:133 and validate/validation_report.py:79 repeat the join. Checks return strings (`check -> list[str]`, with `Finding(str)` carrying lines) or `(node_id, message)` pairs that graph.py:1341 turns back into nodes. `Rule` carries `practice`, `pattern`, `shared` fields only the graph fills.

```
BEFORE
Rule(slug, body, fidelity)            harness/guidance   practice, pattern, shared: set from outside
PracticeGraphRule(slug, node_types)   harness/graph
   check(node, context) -> list[str | Finding(str)]
   check_practice(context) -> list[(node_id, message)]
GraphRule(Rule)(node, slug, check?)   record(message)
GraphRulesCollection(RulesCollection) record_violation(slug, message), graph_rules, from_node (joins by slug)
ConformsToSchema.rule = Rule(...)     the one check holding its text
PracticeRuleRun -> asks check by slug, looks node up by id

AFTER
Rule(slug, body, fidelity)            - practice  - pattern  - shared   (→ GraphRule.source)
PracticeGraphRule
   + rule: Rule                       set once by PracticeRuleRun from the practice's rules
   ~ check(node, context) -> list[Finding]
   ~ check_practice(context) -> list[Finding]
Finding(node, message, lines=None)    ~ no longer a str subclass
GraphRule                             ~ not a Rule: holds node, check, and where the rule came from
   + record(finding)                  prose is check.rule.body, or the prose handed in for a rule with no check
GraphRulesCollection                  ~ plain holder of dict[str, GraphRule]
   - record_violation  - graph_rules  - isinstance filters  - RulesCollection base
```

**Callers.** Every rule under `cdd_guidance/practices/*/rules` and `cdd_guidance/patterns/*/practices/*/rules` (return type of `check`; ten `check_practice`), graph.py:1337-1376, violation.py, explorer.py, graph_rules_collection.py, schema_rules.py:133, validate/validation_report.py:79, rule_fixture.py.
**Size.** About 40 files, mostly one-line returns; about 250 lines changed in harness/graph.
**What could go wrong.** Rules judged by an agent only have no check, so `GraphRule` must still take prose without one. The data `graph.return_nodes` and `graph.json` send for a rule must not change (graph_json_spec, the app tests, saved-graph shape 4). A rule that returns a plain string today and is missed fails only when it fires.

### P2. PracticeReading belongs to harness/graph

**Problem.** `PracticeReading` (harness/guidance/practice_reading.py) is how a practice takes part in the graph. harness/guidance only constructs it (guidance.py:298); harness/graph reads `.reading` about 95 times. To live in guidance it needs three protocols that understate the graph (`HoldingGraph`, `HeldRuleRun`, `HeldNodes`) and four `dict[str, Any]` signatures, and `reads_after` names practices by key. The mechanical hit "copies the fields of PracticeReading" is noise, but the misplacement is real.

```
BEFORE  harness/guidance/practice_reading.py
  HoldingGraph, HeldRuleRun, HeldNodes            (Protocols)
  rules_in(module_path) -> dict[str, Any]         (module function)
  PracticeReading(practice)
     graph: HoldingGraph | None   in_graph: HeldNodes | None
     reads_after: tuple[str, ...]
     graph_checks / own_graph_checks / checks -> dict[str, Any]
  PracticeGuidance.reading_type = PracticeReading ; self.reading = reading_type(self)

AFTER   harness/graph/practice_reading.py
  - HoldingGraph  - HeldRuleRun  - HeldNodes
  PracticeReading(practice)                       → moved from harness/guidance
     ~ graph: Graph | None   ~ in_graph: PracticeNodes | None
     ~ reads_after: tuple[type[PracticeGuidance], ...]
     ~ graph_checks / own_graph_checks / checks -> dict[str, PracticeGraphRule]
     + _rules_in(package)                         → from module function rules_in
  harness/guidance/guidance.py
     ~ reading_type: type | None = None           harness/graph sets the default when imported,
                                                   as space/kanban sets Stories.editor
```

**Callers.** guidance.py:15, 261, 298; pattern_overlays.py:21 (`rules_in`); the five `model/graph_reading.py` files under cdd_guidance/practices (import path, `reads_after`); graph_build.py:460; both module cards; practice-guidance-model.md.
**Size.** About 12 files; 150 lines moved, 40 changed.
**What could go wrong.** A process that makes practices without importing harness.graph gets no reading; every process that loads the toolsets imports it today, but a spec that makes a bare practice would need the import. A circular import unless the new file sits below graph.py. harness/graph's seam grows by one class while harness/guidance's shrinks by one class and three protocols.

### P3. Split Filter, and stop keeping a filter on the graph

**Problem.** `Filter` (graph.py:341, 10 public operations) is both the choices the explorer offers and the match test for one request. `GraphExplorer.filter` keeps a filter on the graph that production never selects on: its `select_violations` and `select_relationships` are called only by specs, and its only production reads are `clear()`, `narrowed_by` (space/session/file_view_filter.py:59, 65), and a read at graph_rules_collection.py:146 that is always empty. The tools take `filter: dict` although `FilterRequest` models it.

```
BEFORE
Filter(graph)
  practices, name, paths, violations, relationships_selected
  node_types, offered_node_types, relationships, rules          (data fields the explorer reads)
  clear() select_violations() select_relationships()
  select_practices() select_node_types() change_practices()
  narrowed_by(request) matches(node) lists(file) collect(roots)
GraphExplorer.filter: Filter
GraphExplorer.filter_choices(...) -> Filter
Graph.return_nodes / explorer_trees / explorer_branch (filter: dict | None)

AFTER
FilterChoices(graph, practices, node_types, practices_before)   + added
  node_types, offered_node_types, relationships, rules          → from Filter
  _select_practices, _select_node_types, _change_practices      → from Filter, private
Filter(graph, request: FilterRequest)                           ~ made for one request
  matches(node) lists(file) collect(roots)
  - narrowed_by  - clear  - select_violations  - select_relationships
GraphExplorer
  - filter
  ~ filter_choices(...) -> FilterChoices
Graph.return_nodes / explorer_trees / explorer_branch (filter: FilterRequest | None)   ~ typed
GraphRulesCollection.shown                                      ~ no graph-filter fallback
```

**Callers.** space/session/file_view_filter.py:59, 65; space/session/session_explorer.py:66; graph_rules_collection.py:146; explorer.py:98. The data type the TypeScript adapter calls `Filter` becomes `FilterChoices` with the same fields, which reaches harness/graph/app and harness/files_app; `nodeFilter` in app/filter/filter-selection.ts can then return the typed request.
**Size.** 5 production Python files, about 150 lines moved and 40 deleted; 4 spec files (graph_spec.py:331-388, graph_view_spec, rule_category_spec, app_smoke_spec); the regenerated adapter and its users.
**What could go wrong.** If a client relies on a filter that stays chosen on the server between calls, that behaviour goes; none was found. The MCP schema and the generated adapter must accept a `TypedDict` parameter; regenerate and compare before committing.

### P4. Bring Graph within its budget

**Problem.** `Graph` has 18 public operations. Four are not tools (`for_call`, `practice`, `node`, `restored_from`) and 14 forward one line to `self.reads` or `self.explorer`.

```
BEFORE
Graph [@agent_toolset]   14 tools, each → reads.* or explorer.*
  for_call  practice  node  restored_from
GraphReads     open open_saved working_copy(read, call) practice_roots(call) files(read, call) ...
GraphExplorer  inventory filter_choices overlay_of source source_members return_nodes explorer_trees explorer_branch

AFTER
Graph [@agent_toolset]
  for_call  node
  - practice                         (fix 30: practices.named)
  restored_from                      → GraphPractices.restore(saved)
  load_working_copy load_practice_roots load_files refresh save_json set_overlays     6 tools stay
  inventory, filter_choices, source, return_nodes, explorer_trees,
  explorer_branch, practice_names, overlay_of                                         → GraphExplorer, as tools
GraphExplorer [publishes its operations under the toolset name "graph"]
  + practice_names
  overlay_of                         → PatternOverlays.overlay_root(folder)
```

Graph ends at 8 public operations and GraphExplorer at 8, with no tool renamed.

**Callers.** `restored_from`: cdd_guidance/practices/bdd/model/graph_bdd_model.py:43 and 4 specs. Session code already calls `graph.explorer.*`.
**Size.** graph.py, about 120 lines moved; one change in the installer.
**What could go wrong.** It was not confirmed that `@agent_toolset` lets a part publish under its owner's toolset name with `for_call` resolved through the graph; that is the installer change. Without it the only route is a second toolset name, which renames 8 tools across harness/graph/app, harness/files_app, and Validate; that cost is not worth a count. In that case do fix 30 and the `restored_from` move, accept 16, and record the exception on the card.

### P5. One class for the nodes a practice holds

**Problem.** `_HeldNodes`, `PracticeNodes`, and `PracticeLoading` share one collection through 12 forwarding methods (graph.py:991-1257). The object has four names (`PracticeNodes`, `in_graph`, `HeldNodes`, "part").

```
BEFORE
PracticeNodes(graph, practice)   _held: _HeldNodes ; edge_index rule_run loading restore
  nodes node holds hold hold_group offer_node_types node_types add add_file unused_node_id   (each → _held)
_HeldNodes(changed)   get group hold_group of_type offer hold release drop sort clear unused_id
PracticeLoading(part, held)   open close release forget_files forget put_in_source_order nodes_read_now

AFTER
PracticeNodes(graph, practice)                ~ holds its nodes by id, by type, and by group itself
  nodes node holds add add_file unused_node_id node_types offer_node_types
  + nodes_read_now                            → from PracticeLoading
  _hold _release _drop _sort _clear _hold_group        private
- _HeldNodes
PracticeLoading(part)                         ~ open close forget_files put_in_source_order
  - release  - forget                         (PracticeRestore asks the part)
```

**Callers.** graph_build.py and graph_practices.py unchanged; cdd_guidance/practices/ddd/model/graph_reading.py (`nodes_read_now`). `in_graph.hold(node)` is used by about 8 specs; keep `hold` public or move them to `add`.
**Size.** graph.py only; about 100 lines fewer.
**What could go wrong.** `PracticeLoading` and `PracticeRestore` then call private members of `PracticeNodes` inside one file. Renaming `in_graph` itself (115 production and about 170 spec sites) is a separate decision and should not be bundled.

### P6. One relationship model on the schema; practices own their type tables

**Problem.** "Which fields of a schema type are relationships" is decided three times with two exclusion lists: `SchemaType.required_relationships` with `_DESCRIBING` (harness/guidance/schema.py:27, 47), `SchemaFields._fields_of` (harness/graph/schema_edges.py:158), and `SchemaOverlays.relationship_kinds` with `_TYPE_FIELDS` (schema_rules.py:23, 317), all parsing `SchemaType.fields: list[tuple[str, str]]`. The framework also lists practices' types and edge kinds in schema_edges.py (`_NODE_TYPES`, `CHILD_LISTS`, `_EVIDENCE_KINDS`, `_matches`), edge.py (`EDGE_ORDER`), and model_node.py.

```
BEFORE
SchemaType   fields: list[(name, written)] ; required_relationships -> dict
SchemaFields._fields_of (regex) -> SchemaField(owner, kind, targets, phase)
SchemaOverlays.relationship_kinds                       third definition
schema_edges: _NODE_TYPES, CHILD_LISTS, _EVIDENCE_KINDS, SchemaEdges._matches (switch on kind), NodeEvidence
edge: EDGE_ORDER

AFTER
SchemaType   + relationships: list[SchemaRelationship(name, targets, optional)]     read once in Schema._read
             ~ required_relationships derives from relationships
- SchemaFields._fields_of   - _TYPE_FIELDS   - _DESCRIBING outside schema.py
PracticeReading   + node_type_of: dict[str, str]         → from _NODE_TYPES
                  + child_lists, edge_order              → from CHILD_LISTS, EDGE_ORDER
                  + links(owner, kind, target) -> bool   → from SchemaEdges._matches
SchemaEdges       ~ asks owner.practice.reading.links(...)
- NodeEvidence                                           → each practice's model answers its own evidence
```

**Callers.** schema.py, schema_edges.py, schema_rules.py, schema_conformance.py, edge.py, the five practice `graph_reading.py` files, schema_spec.py, schema_rules_spec.py, schema_conformance_spec.py.
**Size.** About 14 files, about 350 lines.
**What could go wrong.** Edge order and inverse edges must stay byte-identical in `graph.json` (shape 4), or every saved graph is rebuilt. Pattern schemas add edge kinds no practice lists, so the practice tables need a place for a pattern's. Do after P2, so `PracticeReading` is already in harness/graph.

### P7. A render request renders itself

**Problem.** One render has five public entries: `PracticeGuidance.render`, and on `FidelityGuidance` `render`, `render_files`, `files_to_render`, `render_request` (guidance.py:513, 827-849). The last two exist because Render builds the request in the server and renders it in a worker, so the request goes out of the fidelity and back in, and the fidelity copies it with `fidelity=self`. `FidelityGuidance` is over its operation budget (10) for this reason alone. The result is a bare `dict`.

```
BEFORE
FidelityGuidance
  render(format, content, source) -> dict
  render_files(format, paths, source, previous) -> dict
  files_to_render(format, paths, source, previous) -> RenderRequest
  render_request(request) -> dict
  _folder_holding(paths)
RenderRequest (frozen)   format content source previous folder fidelity ; source_format companion keeping_sketch_wording()
PracticeFormats   read(paths, request)  render(request) -> dict
Render action     fidelity.files_to_render(...) in the server ; fidelity.render_request(request) in the worker

AFTER
RenderRequest
  + from_files(fidelity, format, paths, source, previous) -> RenderRequest     → from FidelityGuidance.files_to_render
  + render() -> Rendered                                                      → from FidelityGuidance.render_request
  _folder_holding(paths)                                                      → from FidelityGuidance
+ Rendered(format: Format, content)                                           replaces the bare dict
FidelityGuidance
  render(format, content, source) -> Rendered            ~ one line: RenderRequest(...).render()
  render_files(format, paths, source, previous)          ~ one line: RenderRequest.from_files(...).render()
  - files_to_render   - render_request
PracticeFormats   ~ read(paths)   ~ render(request) -> Rendered
```

FidelityGuidance ends at 8 public operations (7 with `guidance_parts` private, fix 1).

**Callers.** cdd_guidance/actions/render/render.py (6 lines), render_worker.py, worker_render.py; space/session/format_alignment.py; the practices' formats subclasses that build the result dict (stories_formats.py, clean_engineering_formats.py, ddd_formats.py, ux.py); callers that read `result["content"]` and `result["format"]`.
**Size.** About 10 files, about 120 lines. `Rendered` can keep `__getitem__` for one pass only if the change is split; the repository's rule against legacy APIs says change every reader in the same pass.
**What could go wrong.** A `RenderRequest` crosses to the render worker; whatever serialises it must still carry or rebuild the fidelity. `PracticeGuidance.render` is a published tool whose result goes to MCP as data, so `Rendered` must serialise to the same two fields.

### P8. Declared outputs are declarations; the session answers what is on disk

**Problem.** `DeclaredOutputs` (harness/guidance/declared_outputs.py:97) is both the fidelity's declared path patterns and a view of the session's files. Its `output_paths`, `files`, and `has_output` only forward to `session_output.written` (space/session's *WrittenFiles*), which reads `fidelity.outputs` and `fidelity.declared` back and builds its own `DeclaredFile`s from the raw outputs. Callers reach the same answer by either door: `fidelity.declared.output_paths()` (13 production uses) or the session output.

```
BEFORE
FidelityGuidance.declared: DeclaredOutputs(fidelity, outputs)
  includes  code_folders  file_name_beside  file_beside            (patterns only)
  saved_beside(source, format)                                      reads session_output.roots
  output_paths()  files()  has_output()                             → session_output.written.*
  files_to_review()                                                 walks reviews_files_of, calls files()
WrittenFiles(output)   output_paths files has_output ...            reads fidelity.outputs, fidelity.declared

AFTER
DeclaredOutputs(outputs)                         ~ no fidelity: declarations only
  includes  code_folders  file_name_beside  file_beside
  + declared_files(format) -> list[DeclaredFile]  so WrittenFiles stops rebuilding them from raw outputs
  - output_paths  - files  - has_output          callers ask fidelity.session_output.written
  saved_beside       → WrittenFiles.saved_beside(source, format)
  files_to_review    → WrittenFiles.files_to_review()   (the fidelity's reviews_files_of stays on the fidelity)
FidelityOutput (protocol)   + written: WrittenOutput (output_paths, files, has_output, saved_beside, files_to_review)
```

**Callers.** `declared.output_paths` 13 (validate/checked_graph.py 4, generate.py 3, kanban/ticket.py, story-test shared files 5), `declared.files` 3, `has_output` 4 (kanban/ticket.py 2, session 2), `files_to_review` 1, `saved_beside` 4 (format_alignment.py, render/rendered_file.py), plus about 40 spec lines.
**Size.** About 12 production files and 6 spec files; about 150 lines.
**What could go wrong.** Every caller must handle a fidelity that works in no session (`session_output is None`), which `DeclaredOutputs` hides today by answering empty; a small null output object for "no session" keeps callers flat. cdd_guidance cannot import space, so it reaches *WrittenFiles* only through the protocol.

### P9. One description of the session for the framework

**Problem.** The framework describes space/session's *Session* three times: `WorkedSession` with `FidelityOutput` and `PracticeOutput` (harness/guidance/worked_session.py), `ActionSession` (harness/guidance_actions/guidance_actions.py:47, mostly `Any`), and `getattr(session, "graph", None)` in `Graph.for_call` (graph.py:1552); `ToolCall.session` returns `Any` (agent_tools/tool_call.py:191). Two of the three are out of step with the code they type (see Findings), so a rename in space/session breaks the framework with no type to say so.

```
BEFORE
harness/guidance/worked_session.py          WorkedSession(work_root, session_files, document_named)
harness/guidance_actions/guidance_actions.py ActionSession(name, practices: Mapping[str, Any], overlays, fields,
                                                log: Any, graph: Any, work_root, repo_path, paths: Any,
                                                session_files: Any, record_folder, session_file, ...)
harness/graph/graph.py                      getattr(session, "graph", None)
harness/agent_tools/tool_call.py            ToolCall.session -> Any

AFTER
harness/agent_tools/tool_call.py (beside SessionOpener, which already names what opens a session)
  + WorkedSession (Protocol)                 → from harness/guidance, widened to what the three modules read:
       name, work_root, repo_path, session_file, record_folder, overlays, stories
       paths: SessionPaths(path_named, document_named)
       session_files: SessionFiles(find, from_root)
       log: SessionLog(by, guidance_action, failure, injected_rules)
       practices: Mapping[str, PracticeOutput]
       graph: object                         (typed as Graph only where harness/graph reads it)
       choose_overlays(overlays), practice(key)
  ~ ToolCall.session -> WorkedSession | None
- ActionSession                              (guidance_actions imports WorkedSession)
harness/graph/graph.py   ~ Graph.for_call reads call.session.graph
```

**Callers.** harness/guidance (worked_session.py, documents.py, practice_formats.py, guidance.py), harness/guidance_actions, harness/graph/graph.py, cdd_guidance actions that name `ActionSession` (partition.py 3, sketch.py 3), space/session unchanged (it already answers all of it).
**Size.** About 8 files, about 120 lines, almost all type declarations.
**What could go wrong.** A protocol this wide is a second copy of Session's surface that can itself fall out of step; a unit spec asserting that space/session's *Session* answers it (`isinstance` on a `runtime_checkable` protocol, in space) keeps it honest. harness/agent_tools sits below harness/guidance, so `PracticeOutput` must be named there without importing guidance (under `TYPE_CHECKING`).

### P10. The stage's actions are the catalogue's answer

**Problem.** `ApproachStage` takes the action catalogue and answers `steps`, `actions`, `producing_actions`, `actions_with_formats` (stages.py:131-178), but `_placed` never uses the stage, so all three stages answer the same lists, recomputed and sent three times. `GENERATE`, `VALIDATE`, `RENDER` are action names kept as framework constants.

```
BEFORE
ApproachStage(name, scope, catalogue)   steps actions producing_actions actions_with_formats   (same on every stage)
stages.py   GENERATE VALIDATE RENDER (strings) ; OnStage(rank, *traits: str)
ActionCatalogue   actions names

AFTER
ApproachStage(name, scope)              - catalogue  - steps  - actions  - producing_actions  - actions_with_formats
ActionCatalogue
  + steps  + on_fidelities  + producing  + taking_formats : tuple[Action, ...]     → from ApproachStage, made once
Action   + place: OnStage | None        read once from its operation
- GENERATE  - VALIDATE  - RENDER        space/kanban asks the catalogue for the step actions and the action taking formats
```

**Callers.** space/kanban/board.py (4), space/kanban/ticket.py (18 uses of the three constants), harness/chat-ui board and chat-bar clients (`producing_actions`, `actions_with_formats` arrive as stage data fields: 3 TypeScript files), harness/catalog_generator/stage_columns.py, stages_spec.py.
**Size.** About 9 files, about 100 lines.
**What could go wrong.** The board's data shape changes (the lists leave each stage), so the TypeScript clients and their tests change in the same pass. `stages.py` importing the catalogue goes away, but `OnStage` must then live where `ActionCatalogue` can read it without a cycle. ticket.py's uses of `VALIDATE` and `RENDER` mean "the checking action" and "the converting action"; `CHECKS` exists as a trait, but render has no trait of its own today, so one would be added.

### P11. `call` stops at the graph's seam

**Problem.** `call` passes through four layers (Graph → GraphReads → GraphBuild.load/refresh → GraphBuild.run) to answer one boolean, `call.request.answers_a_chat` (graph_build.py:380). `WorkingCopyRead` and `FilesRead` exist only to carry arguments across one of those layers.

```
BEFORE
Graph.load_*(…, call) → GraphReads.x(read | paths, call) → GraphBuild.load(force, call) / refresh(paths, call, checked) → run(task, call, state)
WorkingCopyRead, FilesRead        frozen bags, one builder and one reader each

AFTER
BuildTask(step, saves, checked, apart)   + apart: bool        (the worker never reads it)
GraphBuild.run(task, state)              ~ reads task.apart
GraphReads.x(…, apart: bool)             ~ one boolean; makes the BuildTask
Graph.load_*(…, call)                    ~ apart = call is not None and call.request.answers_a_chat
- WorkingCopyRead   - FilesRead
```

**Callers.** cdd_guidance/actions/validate/checked_graph.py:208-209, space/session/file_graphs.py:70, graph_worker_heavy_spec.py.
**Size.** 3 production files, about 60 lines.
**What could go wrong.** A value is still passed down, as the decision rather than the request. `GraphReads.working_copy` then takes more loose parameters unless `overlays` and `force` are applied to the graph first.

### P12. Recording generated patterns leaves the graph

**Problem.** `PatternOverlays.record_content`, `recorded_for`, `_recorded_in`, `_recording_instructions`, `GraphOverlay.record_in`, and `PatternsFile` (harness/graph/pattern_overlays.py, patterns_file.py) record which patterns content was generated with and word the agent's instructions. No graph build uses them; the callers are generate.py:49 and guidance_actions.py:616.

```
BEFORE  harness/graph   PatternOverlays: record_content, recorded_for, _recorded_in, _recording_instructions
                        GraphOverlay: roles, record_in ; patterns_file.py PatternsFile
AFTER   harness/guidance_actions
          + GeneratedPatterns(overlays: PatternOverlays)   → record_content, recorded_for, instructions
          PatternsFile                                     → moved here
        harness/graph   GraphOverlay: roles stays ; - record_in
```

**Callers.** generate.py:49, guidance_actions.py:616-619, pattern_overlay_spec.py:92-104, patterns_file_spec.py.
**Size.** 5 files, about 120 lines moved.
**What could go wrong.** It makes guidance_actions' dependency on harness/graph explicit (an import of `PatternOverlays`), which the card does not list today although the code already calls it through `Any`; the card's dependency line must change with it.

### P13. Explorer page (TypeScript): three objects that own what free functions pass around

**13a. GraphFailures extends ChatToldFailures.**
```
BEFORE  GraphFailures  api, chat (public) ; toldChat, toasts, listeners ; fail, toast, onChange, shown ; tellChat
        correctInChat(failures)   free function in source/violation-chat.ts
AFTER   GraphFailures extends ChatToldFailures
          - api  - toldChat  - tellChat (inherited)   ~ show(failure) = toast ; notTold = toast
          + correct(correction): Promise<CorrectionOutcome>     → from correctInChat
```
Callers: graph-page.ts, App.tsx, violation-chat.ts (deleted), two test files. Size: 4 files, about 60 lines out and 25 in. Risk: the base de-duplicates only the chat send, so a failure met every 400 ms would toast again unless `show` keeps its own shown set; the base constructor takes an api factory.

**13b. ExplorerTrees owns the tree.**
```
BEFORE  ExplorerFilter.trees: ExplorerEntryData[]
        graph-selection: withBranch, opening, childrenOf, childrenLeftOut, isRule    (free)
        source-pane: findNode, rulesUnder (free) ; SourcePane.rulesIn(trees), chooseRule(trees, name)
        GraphView.tsx 70-72: inline scan
AFTER   + ExplorerTrees(entries)   withBranch(branch), rulesOf(nodeId), isViolating(entry), entries
        ExplorerFilter.trees: ExplorerTrees        ~
        SourcePane(state, filter)                  ~ rules (property)  ~ chooseRule(name)
```
Callers: App.tsx, GraphView.tsx, and harness/files_app (files-graph.ts, files-graph-view.tsx use `childrenOf`). Size: 6 files, about 80 lines. Risk: the object is rebuilt each render, so identity-based memoisation breaks.

**13c. A source span and a callout scan replace the five-parameter chain.**
```
BEFORE  CallCatalog.calloutsIn(text, origin, language, stack, file) → calloutsOn(line, at, bindings, stack, seen)
        FoldMember (copy of NodeSourceData) ; Opening + calloutsBlock / calloutSection / calloutRow
AFTER   + SourceSpan {file, startLine, text, language}
        CallCatalog  ~ calloutsIn(span, stack)
        + CalloutScan(catalog, span, stack)   bindings, seen ; calloutsOn(line, number)
        + OpenCallouts(open, toggle, within, goTo)   block, section, row
        - FoldMember (use NodeSourceData)
```
Callers: SourceView.tsx, and harness/files_app (file-view.tsx, source-of-file.ts, call-expansion.spec.ts). Size: 5-6 files, about 150 lines. Risk: `useMemo` dependencies on the catalogue; nested callout keys must stay stable for the open state.

## Graph hits judged noise

| File:line | Rule | Why it is noise |
|---|---|---|
| harness/guidance/practice_reading.py:57 | `PracticeReading` copies the fields of `PracticeReading` | The only other `PracticeReading` is its own entry in a model document (practice-guidance-model.md), read as a class beside the code. No second code class exists. The real issue is where the class lives (P2). |
| harness/guidance/schema.py:32 | `SchemaType` copies the fields of `SchemaType` | Same: the match is the model document's entry for the same class. |
| harness/guidance/.context/practice-guidance-model.md:187 | `PracticeFormats` exposes 11 public operations | Counted from the model document, not the code; the code has 9 public operations (`adapter_class`, `adapter`, `reading`, `reading_with`, `for_file`, `read`, `render`, `parse`, `model_for`), which is on the budget. The three ways to an adapter are still a finding. |
| harness/guidance/.context/practice-guidance-model.md:15-379 (parameters `format`, `parent`, `fidelity`, `content`, `model`, `paths`, `target`, `name`, `stage`, `entries`, `always_apply`, `globs`) | parameter missing a type annotation / needs a domain-specific type | The scanner read the model document's class boxes as code. The code annotates these parameters; the untyped signatures that are real are listed in Findings. |
| harness/guidance/.context/practice-guidance-model.md:55 | `render` takes 4 parameters | A model-document hit; the code operation (`PracticeGuidance.render`, guidance.py:513) is a published tool, which the rule exempts. |
| harness/graph/.context/graph-populate-model.md:1-506 (parameters `call`, `force`, `overlays`, `message`, `seen`, `stack`, `via`, `child`, `kind`, `name`, `root`, `node`, `node_type`, `violation`, `file`, `location`) | parameter missing a type annotation | Model-document class boxes read as code; every parameter is annotated in the Python files. |
| harness/graph/graph.py:991 | `_HeldNodes` exposes 10 public operations | A private class used only inside graph.py, so it has no public surface. The real issue is the forwarding layers (P5). |
| harness/graph/graph.py:1514 | `Graph` exposes 18 public operations | Partly noise: 14 are the published tool list. The four non-tool operations and the forwarding are real (fix 30, P4). |
| harness/guidance/guidance.py:833, 840 | `render_files`, `files_to_render` take 4 parameters | Real as a symptom, not as a count: the four values are one render request (P7). |
| harness/graph/app/source/call-expansion.ts:102, 110, 124, 133, 189 | parameter `at` does not reveal intent | Typed `at: FileLine`, which the rule exempts; it reads as `holds(body, at)`. |
| harness/graph/app/source/call-expansion.ts:88 `owner`, 95 `file` | parameter missing a type annotation | `= ""` defaults infer `string`. |
| harness/graph/app/source/SourceView.tsx:143, 157 | `useSourceCallouts` 4 parameters, `useLineMarks` 5 | React hooks whose inputs are props; `useLineMarks` could take one `source` for `origin` and `text`, a minor point. |

Confirmed as real among the mechanical hits: graph.py:341 `Filter` (P3); guidance.py:535 `FidelityGuidance` (P7); graph.py:236 `align_to_declaration` (the `root` parameter and a `Location`); graph.py:57 `_under_any` and graph.py:62 `_decorated_end` (fix 17); practice_formats.py:43 `Reshaped` against `_FileEdit` (small); pattern_overlays.py:58 and schema_rules.py:70 `node` (fix 20); call-expansion.ts:95, 102 and source-callouts.ts:144, 156, 234 parameter counts (P13c).
