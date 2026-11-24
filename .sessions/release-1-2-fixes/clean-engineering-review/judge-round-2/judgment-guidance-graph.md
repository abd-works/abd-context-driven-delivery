# Design judgment, round 2: harness/guidance, harness/guidance_actions, harness/graph

**Area:** guidance-graph: the 69 production files of harness/guidance, harness/guidance_actions, harness/graph and harness/graph/app changed since base `66f410de3`, judged at `5d16245ff` on branch release-1-2-fixes.

**Read:** read only; no code, test or document was changed and no spec was run. Every file in the list was read in full at its current content and judged whole, not only the changed lines: harness/guidance and harness/guidance_actions (16 files) by the lead judge, harness/graph Python in two halves and the TypeScript under harness/graph/app by three sub-judges, each briefed with the same rules, the first round's judgment and the module card. The lead re-checked claims where two sub-judges met; one was corrected (Python's published filter is now a *FilterRequest*; it is the generated TypeScript adapter that still takes `Record<string, unknown>`).

**Method:** rules from `.claude/rules/practices/clean-engineering/clean-engineering-code.md` and `clean-engineering-model.md`, `.claude/rules/coding.md`, and the refactor guardrails. Every "unused", "no caller" or "only used inside" claim was checked with a word-boundary search of harness, space, tools, cdd_guidance, scripts and story_tests (TypeScript also across the generated adapters in `.claude/language-adapters/typescript`), without oss_portal_domain_driven, with specs and tests counted apart. A finding the first round also made (same file, same rule, same problem) ends with "(still open from round 1)"; a round-1 finding that moved file with its code (practice_reading.py, the stage traits) counts as the same finding. Theme tags: [1] module boundaries, [2] the same work in different shapes, [3] resource orientation, [4] domain orientation.

## Counts

- Files read: 69 (16 harness/guidance and harness/guidance_actions, 25 harness/graph Python, 28 harness/graph/app).
- Findings: 167 (harness/guidance and guidance_actions 59, graph core 42, graph rules and schema 36, graph app 30). Round 1 made 166 findings in this area.
- Findings still open from round 1: 85 (41, 17, 19, 8).
- Round-1 findings fixed: 83, listed under "Fixed since round 1".
- Design proposals: 24.

| Rule | Findings |
|---|---|
| eliminate-duplication | 26 |
| hide-inner-details | 21 |
| use-typed-signatures | 18 |
| use-consistent-naming | 13 |
| hold-state-on-the-object-not-in-parameters | 12 |
| extensions-live-with-the-domain | 6 |
| deep-module | 5 |
| make-module-only-operations-private | 5 |
| prefer-class-operations | 5 |
| high-cohesion | 4 |
| keep-classes-single-responsibility | 4 |
| do-not-invent-parallel-object-models | 3 |
| provide-meaningful-context | 3 |
| put-logic-on-the-owning-resource | 3 |
| shape-classes-around-resources | 3 |
| use-explicit-dependencies | 3 |
| use-intention-revealing-names | 3 |
| class-not-property-instance-or-subtype | 2 |
| layer-separation | 2 |
| limit-function-lines | 2 |
| limit-operation-parameters | 2 |
| limit-paths-through-a-function | 2 |
| seam-names-current-code | 2 |
| single-boundary | 2 |
| the module's Constraint (no `getattr` with a default) | 2 |
| domain-exception-carries-context | 1 |
| errors-out-of-existence | 1 |
| keep-operations-single-responsibility | 1 |
| limit-module-file-lines | 1 |
| low-coupling | 1 |
| no-legacy-api-after-refactor | 1 |
| no-use-delete | 1 |
| one-way-deps | 1 |
| prefer-instance-operations | 1 |
| public-seam-only | 1 |
| refactor guardrail: build once, keep it | 1 |
| refuse-unreadable-input | 1 |
| temporal-independence | 1 |
| use-exceptions-properly | 1 |

## Findings

### harness/guidance/guidance.py

- guidance.py:622 `FidelityGuidance` — keep-classes-single-responsibility — about 38 public members: the fidelity's settings from its yaml block (`stage`, `outputs`, `judged_on`, `example`, `leaves_out`, `reviews_files_of`), its format held in the session (`format`, `default_format`), its install names (`published_name`, `installed_as`, `install_folder`, `slug`), its words (`instructions`, `own_instructions`, `process`, `templates`, `template_file`, `examples`, `scaffold`, `section`), its rules (`rules`, `checked_rule_collections`, `every_rule`, `supplements`, `supplement_records`), its companion, its actions, and rendering. A render is still said several ways: `FidelityGuidance.render` (950), `render_files` (956), `PracticeGuidance.render` (601) and `RenderRequest.render` (practice_formats.py:309); the round-1 `files_to_render` and `render_request` are gone. (still open from round 1) [3]
- guidance.py:290 `format_adapters: ClassVar[dict[str, Any]]`, 308 `editor: ClassVar[Any]`, 297/428 `reading_type: type | None` with `reading -> Any` — use-typed-signatures — `session` and `supplements` are now typed, but the practice's graph reading, read 92 times in production as `practice.reading.in_graph`, is typed `Any`, so no caller of the practice's busiest part is checked; *FormatAdapter* exists for the adapters' type. (still open from round 1) [3]
- guidance.py:20, 670, 822-850 `COMPANION_PRACTICE` and `clean_engineering` — extensions-live-with-the-domain — the framework still names one practice by its folder name and gives every fidelity a property named after it, against the card's "the framework names no practice"; the concept is the companion, which *WorkingSet* already calls `companion`. (still open from round 1) [1][4]
- guidance.py:827-850 `_clean_engineering` — hold-state-on-the-object-not-in-parameters — one field holds either the companion's name from the yaml block or the companion fidelity, told apart with `isinstance` on every read and resolved by name on first read. (still open from round 1) [3]
- guidance.py:758-763 `practice_guidance` — use-consistent-naming — the practice is found by walking `parent` with `getattr` on every read (70 production uses), and named `practice_guidance` here, `practice` on *NamedGuidance* and *PracticeReading*, `owner_practice` on *RulesCollection* (rule.py:178). (still open from round 1) [4]
- guidance.py:77 `domain_slug`, 581 `domain_markdown_path`, 80 `module_dir` — use-consistent-naming — "domain" and "module" stand for the practice and its folder (24 production uses); `document` (443) is the same file as `domain_markdown_path`. (still open from round 1) [4]
- guidance.py:608 `scoped_markdown`, 837 `companion_instructions` — deep-module — public with no production caller outside guidance.py (specs: 5 files and 1). (still open from round 1) [1]
- guidance.py:397-402 `_current_fidelity` — hide-inner-details — reads `vars(self).get("fidelities")` so as not to trigger the markdown collection; the practice works around its own storage. (still open from round 1) [3]
- guidance.py:563, 615 `_guidance_parts`, `_titled_section` — hide-inner-details — round 1's fix made these private by renaming them, but *PracticeGuidance* still calls them on a *FidelityGuidance* (`current._guidance_parts()`, `fidelity._titled_section`): a private name crossed by another class is a public seam with a name that says otherwise, and a search for callers of the private member misses it. [1]
- guidance.py:217-229 `Guidance.instructions` with 1025-1052 `FidelityGuidance._instructions_in` and `_practice_parts` — eliminate-duplication — both join the same parts in the same order (schema guide, overview, guidance, `rules.markdown`, template), each with its own `(x or "").strip()` filter; the fidelity's version adds its practice's parts and its companion. A change to the order of an agent's instructions has to be made twice. [2]
- guidance.py:463, 920 with rule.py:293-302 — eliminate-duplication — "list these rule collections once each, by identity" is written three times (`{id(c): c for c in ...}.values()` twice, a `seen` set in `RuleInjection._unique_collections`); `PracticeGuidance.every_rule` (465-470) builds the same shared-plus-every-fidelity list `checked_rule_collections` builds at 462. [2]
- guidance.py:547-564 `PracticeGuidance.guidance` — keep-operations-single-responsibility — a `@data_field` property that pushes the scoped markdown, the examples and the templates into the running recipe through `instructions(...)` as a side effect, then returns other text (the Guidance section and the current fidelity's parts); reading it for help data and reading it in a recipe do different things. [3]

### harness/guidance/declared_outputs.py

- declared_outputs.py:121, 260 `DeclaredFile._is_written_in` — hide-inner-details — made private by round 1's fix, and called from *DeclaredOutputs* (`declared._is_written_in(written)`): a private name crossed by another class. [1]
- declared_outputs.py:65 `named_with(parts)`, 105 `filled_with(names)`, 399 `place_for_scope` — eliminate-duplication — three ways to write a declared path with its named parts filled: by a dict of parts (with `_group` renaming), by a list in order, and a bare `_NAMED_PART.sub(scope, ...)` that fills every part with one value. Each refuses a different case (a glob, a missing part, a count that does not match), so the same declared path can be named by one and refused by another. [2]
- declared_outputs.py:126 `start_of`, 135 `folder_holding`, 233 `is_in_code_folder` — make-module-only-operations-private — public on classes the card lists, and called only inside declared_outputs.py (no spec either). [1]
- declared_outputs.py:237-264 `_holding`, `_held_in_code_folders`, `_path_beside` — use-typed-signatures — the outputs a source belongs to travel as `list[tuple[str, str, dict[str, str]]]` unpacked by position (`holding[0][1]`, `for _, _, read in holding`); `file_beside` (229-230) works the same list out twice, once itself and once through `_path_beside`. A small record (label, start, parts) would say what each position is. [3]
- declared_outputs.py:22 `_CONTEXT_FOLDER`, guidance_actions/patterns_file.py:7 `_CONTEXT`, and harness/installation's `CONTEXT_FOLDER` (imported by guidance.py:33) — eliminate-duplication — the name of the `.context` folder is defined three times in these files. [2]

### harness/guidance/worked_session.py

- worked_session.py:55 `_SessionLog.by -> object`, 63 `_SessionRecord.fields -> object`, 131 `WorkedSession.graph -> object` — use-typed-signatures — the protocol now replaces round 1's *ActionSession*, but it types as `object` exactly the members the guidance actions call into: `log.by(...).failure` and `.guidance_action` (guidance_actions.py:817, 832), `record.fields.as_dict()` (662), `graph.refresh` and `graph.applied_patterns` (585, 611). So *GuidanceAction* answers `log -> Any` and `graph -> Any` (741-750), and `SessionBrief._story_scope` still reads `getattr(works_in, "stories", None)` (622) though `stories` is declared. (still open from round 1) [3][1]

### harness/guidance/documents.py

- documents.py:14-51 `document_in`, `load_document`, `files_read_from`, `is_text` — prefer-class-operations — a file of module functions; `document_in(session, ...)` takes the session to call `session.paths.document_named`, which itself calls `load_document`. The read belongs on the session's paths, with one reader of files for no session. (still open from round 1) [3]

### harness/guidance/practice_formats.py

- practice_formats.py:378 `adapter_class`, 389 `adapter`, 415 `for_file` — use-consistent-naming — three ways to an adapter (its class or instance as named, the kept instance, a new instance per file), and `_made_adapter` (526-540) inspects constructors to decide how to make one. (still open from round 1) [4][3]
- practice_formats.py:386 `importlib.import_module(named[0])` — one-way-deps — the framework imports a practice's adapter by a `(module, class)` string pair from `format_adapters`. (still open from round 1) [1][3]
- practice_formats.py:406, 426, 474, 501, 519, 533-547 — hide-inner-details — *FormatAdapter* is now a base class with eight operations, yet the rest of the contract is still read by reflection: `suffixes`, `holds_classes_only`, `semantic_type`, `LEAF_EXTENSION`, `create` by `getattr`, and the constructor's parameters by `inspect.signature`. A format that misspells one of them is silently read as having none. (still open from round 1) [3][4]
- practice_formats.py:428 `read(paths, request)` — hold-state-on-the-object-not-in-parameters — `request` is still unused; the body reads `self._practice.session`. (still open from round 1) [3]
- practice_formats.py:22 `TextOrData = ... dict[str, Any] | list[Any]`, 58 `FormatAdapter.render -> Any`, 92 `keeping(rendered: Any) -> Any`, 134 `Rendered.content -> Any` — use-typed-signatures — the result of a render is now *Rendered*, but what it holds is still untyped. (still open from round 1) [3]
- practice_formats.py:315, 446 `RenderRequest._keeping_sketch_wording` — hide-inner-details — made private by round 1's fix, and called from *PracticeFormats*: a private name crossed by another class. The request could answer the `written` it is rendered onto with the sketch's wording already in it. [1]
- practice_formats.py:482-487 `_companion_render` — errors-out-of-existence — a practice with no adapters whose fidelity has no companion answers `Rendered(source or request.format, request.content)`: the input unchanged, labelled with its own format, or with the target format when none was named. When no content was sent, `content` is the practice object itself (439). The caller saves it as a finished render. The call cannot do what was asked and should refuse by name. [3]
- practice_formats.py:97 `named_from`, 236 `lead_of`, 556 `_folder_holding` — prefer-class-operations — module functions: `_folder_holding(paths, session)` serves only `RenderRequest.from_files` and is handed the session the fidelity's practice holds; both outside callers of `lead_of` (cdd_guidance/actions/render/reshaped_code.py:99, bdd/model/spec_reshape.py:68) pass their own `self.lines`, so it is an operation of the outlined text. [3]

### harness/guidance/rule.py

- rule.py:235-365 `RuleInjection` — shape-classes-around-resources — the `getattr` reads of the practice are gone, but the injection still works out the order of the practice's fidelities itself (`_upstream_of`, 304-318, from `fidelities.entries` names matched with `getattr(collection.parent, "name", None)`) and reads `getattr(parent, "slug", None)` (348). Which collections come before a fidelity is the fidelities collection's question. (still open from round 1) [3]
- rule.py:160-194 `practice_key`, `fidelity_name`, `owner_practice` — put-logic-on-the-owning-resource — a rules collection still works out its practice and fidelity by walking `parent` with `getattr` and reading `fidelities.current`; its holder knows both. (still open from round 1) [3]
- rule.py:58-74 `AppliesTo.from_value(fence_fields: AppliesTo | dict | None)` — use-typed-signatures — accepts three shapes and both `alwaysApply` and `always_apply`. (still open from round 1) [3]

### harness/guidance/schema.py

- schema.py:76-81 `SchemaType.fields`, `optional`, `relationships`, `rules` — hide-inner-details — public mutable lists; `Schema._read_block_item` appends to another object's `current.rules` (193-194). `fields` and `optional` have no reader outside schema.py now that *SchemaRelationship* models the relationships, so the raw written value is public for nothing. (still open from round 1) [3]
- schema.py:122 `_loaded: ClassVar[dict[Path, Schema]]` — use-explicit-dependencies — a process-wide cache on the class; a schema file edited while the server runs is never read again. (still open from round 1) [3]

### harness/guidance/action_catalogue.py

- action_catalogue.py:18-39 `STEP`, `TAKES_FORMATS`, `CHECKS`, `CONVERTS`, `OnStage(rank, *traits: str)` — provide-meaningful-context — traits are bare strings and the order is a hand-kept integer across action folders (moved here from stages.py). (still open from round 1) [4]
- action_catalogue.py:65-166 `WorkedFidelity`, `ActionRunner`, `Action`, `FidelityAction`, `FidelityActions` — class-not-property-instance-or-subtype — five types to say `fidelity.actions.generate(...)`; `FidelityAction` only pairs an *Action* with a fidelity and `Action._run_on` only forwards to the catalogue's runner. (still open from round 1) [2][3]
- action_catalogue.py:155 `FidelityActions.__getattr__` — use-typed-signatures — an action is looked up by attribute name at run time, so `fidelity.actions.generate` has no type. (still open from round 1) [3]
- action_catalogue.py:105 `Action.operation` — hide-inner-details — hands out the raw function from `vars(toolset_class)`, which guidance_actions.py:897 and 903 inspect for its parameters. (still open from round 1) [3]
- action_catalogue.py:119/146, 193/121, 200/153 `_run_on`, `_registered_runner`, `_fidelity_actions` — hide-inner-details — made private by round 1's fix, and each is called from another class of the file (*FidelityAction*, *Action*, *FidelityActions*): three private names crossed between classes. [1]

### harness/guidance/practice_supplement.py

- practice_supplement.py:417-424, 441-445, 426-430, 452-456 `rules_for`, `checked_rule_collections`, `_sections_of`, `_fidelity_sections` — eliminate-duplication — each call parses the sections into a new *RulesCollection*, and each scans the document's level-2 headings again; `FidelityGuidance.checked_rule_collections` calls `rules_for` every time a fidelity's rules are read. (still open from round 1) [2][3]
- practice_supplement.py:377 `hold_supplemented`, 392 `supplemented_practices`, 403 `text_for` — deep-module — public on a class on the card's seam, called only from other files of harness/guidance (practice_supplement.py, working_set.py, guidance.py). (still open from round 1) [1]

### harness/guidance/format_trip.py

- format_trip.py:102, 157, 166 `FORMAT_FAILURES` — use-exceptions-properly — the trip catches `LookupError` and `ValueError` and reports them as the format's outcome ("fails on the way"); `KeyError` and `IndexError` are the usual shape of a bug in an adapter, so a bug becomes an ordinary outcome, against the module's own word that "any other failure is a bug ... and is raised". [3]
- format_trip.py:25-35, 50 `TripOutcome.status: str` — use-typed-signatures — the five outcomes are module string constants compared by `in`; an enumeration would let `passes` and the spec name them by type. [4]
- format_trip.py:175 `_declared_for` — put-logic-on-the-owning-resource — finds the format a fidelity declares files of an ending in by reading `declared.outputs` and `declared.paths_in`; it is the inverse of `DeclaredOutputs.formats_written_in` and belongs beside it on *DeclaredOutputs*. `_text_of` (185) is a second module function with one using class. [3]

### harness/guidance_actions/guidance_actions.py

- guidance_actions.py:741-750, 768-787 `log -> Any`, `graph -> Any`, `session_practice -> Any`, `_worked_fidelities -> list[Any]`, `_worked_output -> Any` — use-typed-signatures — the action's session parts are all `Any`, because *WorkedSession* types them as `object` (see worked_session.py). (still open from round 1) [3]
- guidance_actions.py:342 `worked_on: Any`, 67 `_NOTHING_WORKED_ON` — use-typed-signatures — holds a string, a list, a command's written guidance or a fidelity, and is compared with the next guidance (760) to decide whether to read it again. (still open from round 1) [3]
- guidance_actions.py:585, 611-616 `self._action.graph.refresh`, `graph.applied_patterns`, `patterns.pattern_named`, `patterns.names` — low-coupling — calls harness/graph's *Graph* and *PatternOverlays* through an `Any`. (still open from round 1) [1]
- guidance_actions.py:725, 730, 735, 697 `session_for`, `works_in`, `session`, `_session` — use-consistent-naming — four ways to the action's session; `works_in` (15 production uses) answers none and `session` raises, and *ActionFiles* and *SessionBrief* use one, *GuidanceAction* the others. (still open from round 1) [4][3]
- guidance_actions.py:165, 362 `GuidanceArgument(command, practices: Callable[[], PracticeSet], session_name)` — hold-state-on-the-object-not-in-parameters — made by `WorkList.take` from the list's own `practice_set` and `_session_name`, used for two reads (`text`, `items`) and dropped. (still open from round 1) [3]
- guidance_actions.py:314 `PRACTICE_CATALOGUE.create_all()` in `_refuse_turned_off` — hold-state-on-the-object-not-in-parameters — builds every practice of the catalogue to word one refusal. (still open from round 1) [3]
- guidance_actions.py:331 `WorkList` — keep-classes-single-responsibility — five parallel pieces of state (`_items`, `_listed`, `_worked_at`, `_formats` by list position, `text`) and three ways in (`take`, `_take_listed`, `take_fidelity`); `_entry` (400-407) sets `writer.format` as a side effect of reading an entry. (still open from round 1) [3]
- guidance_actions.py:38-47, 124 `GuidanceEntry`, `GuidanceArg`, `ListedGuidance`, `WorkedGuidance`, `ArgumentEntry` — use-intention-revealing-names — five union aliases for "guidance at some stage of being read", three including `str`; operations then test `isinstance` (431, 440-446, 482-487, 492, 513, 669, 779, 878). (still open from round 1) [4][2]
- guidance_actions.py:505, 768-773 `self._session.practice(practice.key)`, `session_practice` — hold-state-on-the-object-not-in-parameters — the practice object is in hand and its key is passed for the lookup's side effect; `session_practice` does the reverse search by identity over every practice output. (still open from round 1) [3]
- guidance_actions.py:544 `source_label` — prefer-class-operations — a module function taking `content, paths`, the pair `ActionFiles.read` takes. (still open from round 1) [3]
- guidance_actions.py:844-847 `session_context` — layer-separation — forwards to `self.brief.session_context`. (still open from round 1) [1]
- guidance_actions.py:807 `inner.mode = "tool"` — hide-inner-details — a field of the toolset set from outside after construction. (still open from round 1) [3]
- guidance_actions.py:891-906 `FidelityActionRunner` — shape-classes-around-resources — a stateless doer that inspects the operation's signature twice (897, 903) and makes the action with no call, so a graph build it starts never runs in a worker. (still open from round 1) [3]
- guidance_actions.py:368, 799 `WorkList._take_listed` — hide-inner-details — private by name and called from *GuidanceAction._inside* on another object (`inner.work._take_listed(...)`). [1]

### harness/guidance_actions/generated_patterns.py

- generated_patterns.py:39 `instructions` — make-module-only-operations-private — public, called only by `record_content` in the same class (no spec). *GeneratedPatterns* is also made anew from `graph.applied_patterns` on each call, in generate.py:50 and guidance_actions.py:613, where the graph could hold it once. [1][3]

### Module cards

- harness/guidance_actions/.context/module-context.md (Seam) — public-seam-only — the seam still lists `_made_for` and `_tool_inside`, private by name, as what subclasses call; cdd_guidance calls `_work_on`, `_made_for` and `_tool_inside` 20 times. (still open from round 1) [1]
- harness/guidance/.context/module-context.md (Seam) — deep-module — the card still accepts "wider than 40% public by design"; the round-1 renames moved members behind underscores, but several of those are crossed by other classes (guidance.py:563, declared_outputs.py:260, practice_formats.py:446, action_catalogue.py:121/146/153), so the public count fell without the seam narrowing. (still open from round 1) [1]

### harness/graph/graph.py

- graph.py (module harness/graph) — limit-module-file-lines / keep-module-files-maintainable — graph.py holds 927 lines of code (lizard NLOC; limit 800) and has a maintainability index of 0.00 (radon; least 20); saved_graph.py is at 13.17. graph.py holds eleven classes with separate jobs: Source and _BracketDepth (finding source text), Node and NodeTree, Inventory, GraphExplorer, PracticeNodes, PracticeLoading, PracticeRuleRun, PracticeRestore, GraphEdges, Graph. [1]
- graph.py:693 `GraphExplorer` / graph.py:1273 `Graph` — deep-module — Graph's public surface is still wide: its own `for_call`, `folder`, `overlays`, `node`, the five load and refresh tools, `save_json`, `saved_file`, plus 11 operations inherited from GraphExplorer (`practice_names`, `inventory`, `overlay_of`, `filter_choices`, `source`, `correction_prompt`, `fix_prompt`, `source_members`, `return_nodes`, `explorer_trees`, `explorer_branch`) and 8 public fields (`build`, `practices`, `scope`, `kept_in`, `applied_patterns`, `schema_edges`, `edges`, `reads`). GraphExplorer has one subclass, Graph, and declares Graph's fields (698-700) so it type-checks; it is a base class with no state of its own, so the split moved methods without making a part. `practice(key)` and `restored_from` are gone. (still open from round 1) [1][2]
- graph.py:1361, 1396 `load_working_copy`, `load_files` — hide-inner-details / temporal-independence — Graph takes GraphReads' public lock (`reads.changing`, graph_reads.py:29; no other user) and sets `scope`, `practices.choose(...)` and `overlays` itself, in that order, before handing over to the read. GraphReads.practice_roots does the same choosing inside GraphReads (graph_reads.py:93-94), and GraphBuild.carry_out a third time (graph_build.py:356-359). `graph.scope` is assigned in 9 places across Graph, GraphReads and GraphBuild. The card's "GraphReads ... so each load tool is one line" is not true of these two tools. [3][1]
- graph.py:1442 `_builds_apart` — eliminate-duplication / prefer-class-operations — `call is not None and call.request.answers_a_chat` is written here, at cdd_guidance/actions/render/render.py:170 and at cdd_guidance/actions/validate/checked_graph.py:253, each reaching through the call's `request`; a module function with one using class. The ToolCall can answer whether its work runs apart. [2][1]
- graph.py:1302 `kept_in` — use-explicit-dependencies — a public field set after construction by its one production writer, space/session/session_graph.py:119, just before `reads.open_saved`; `saved_file` (1428) depends on that order. It belongs in the constructor. (still open from round 1) [3]
- graph.py:162, 177, 187, 198, 218 `Source.align_to_label`, `align_to_table_row`, `widen_to_call_close`, `align_to_example_export`, `align_to_declaration`, and graph.py:105 `as_code_writes` — extensions-live-with-the-domain — Stories knowledge (step labels, `+` underline marks in table cells, `export const` fixtures, escaped quotes in step strings) in the framework; every production caller is cdd_guidance/practices/stories/model/story_recording.py (248-256, and 17/330 for `as_code_writes`). (still open from round 1) [1][3]
- graph.py:117 `Source.__init__(path, line_start, line_end)` — use-consistent-naming — stored as `file`, `start_line`, `end_line`, while *Location* says `file`, `line`, `end_line` and *SavedNode* the same; three vocabularies for one place in a file. (still open from round 1) [2][4]
- graph.py:476, 935 with saved_graph.py:121-129 — eliminate-duplication — Source has no `location`, so `Node.places`, `PracticeNodes.add_file` and `SavedNode.from_node` each rebuild a Location from `source.file`, `source.start_line`, `source.end_line`, while `Source.from_root` (126) takes a Location in. [2]
- graph.py:1034-1043, 1143, 1158 with node_filter.py:199-207, saved_graph.py:388-395, 410 and explorer.py:161 — eliminate-duplication — "is this file one of these folders or under one" is written three times (`PracticeLoading._under_any`, `Filter._under_paths`, `SavedFiles.reads`), and "this path with forward slashes" (`replace("\\", "/")`) six more times. (still open from round 1) [2]
- graph.py:634, 653 with node_filter.py:147 and space/session/files/node_spans.py:125, 142 — eliminate-duplication / hide-inner-details — "a relationship group is a node whose type equals its name" is a convention written in five places across three files; NodeTree._holder_for (602-611) makes such nodes, and nothing on Node says so. A reader of `node.type == node.name` cannot tell it means "group". [2][4]
- graph.py:368-375 `Node.merge_fact` and graph.py:1179, 1196 — temporal-independence — whether the worker's last answer still stands for the graph depends on every change calling `build.changed()`; `merge_fact`'s `setattr` path (373, used by cdd_guidance/practices/clean_engineering/reading/graph_reading.py:142) and `PracticeRestore`'s writes to `root.data` change the graph without it. (still open from round 1) [3]
- graph.py:338 `Node.data` — hide-inner-details — a public dict beside `set_fact`/`get_fact`: replaced from outside at 1196 and 1214, updated at 1179, and read by key at cdd_guidance/practices/clean_engineering/rules/code_measure_limits.py:59; `Node.passing_rules` is gone. (still open from round 1) [1][3]
- graph.py:716-721 `GraphExplorer.overlay_of` — put-logic-on-the-owning-resource — "a folder is an overlay root when it holds practices/" is *PatternOverlays*' rule, which already answers `root_of`. (still open from round 1) [3]
- graph.py:1217 `PracticeRestore.links(saved: SavedPractice | PracticeChanges)` — class-not-property-instance-or-subtype — relies on two unrelated classes happening to share `edges` and `violations_by_node`. (still open from round 1) [2]
- graph.py:526 `NodeTree.serialize(seen, via, stack, label)` — hold-state-on-the-object-not-in-parameters — `seen` and `stack` are one walk's state, defaulted from None and handed through `_written_at_home` (639, 644) into every recursive call; node_filter.py:241 `_FilterWalk` already holds the same kind of state on a walk object. [3]
- graph.py:918, 983-986 `PracticeNodes.add`, `_release_from_its_practice` — hide-inner-details — `getattr(parent, "node_id", "")`, `getattr(node, "practice", None)` and `isinstance(part, PracticeNodes)` on a typed *Node*, against the card's constraint "never ... `getattr` with a default". [3]
- graph.py:829-841 `source_root_path` / `source_root` — use-consistent-naming — one folder answered two ways: `Path | None` (11 production reads) and `str`, with `""` for none (25 production reads). [4]
- graph.py:855, 937, 943, 962 `hold_root`, `hold`, `release`, `forget_all` — make-module-only-operations-private — no production caller outside graph.py (`in_graph.hold(` appears only in 10 spec lines); they are the mutations PracticeLoading and PracticeRestore use. [1]
- graph.py:1099 `PracticeRuleRun.check` — use-consistent-naming — asks `practice.reading.checks()`, which answers `in_graph.rule_run.checks` (practice_reading.py:142), its own `checks` (1075), under a second name and a second return type (`dict[str, PracticeGraphRule]` against `GraphChecks`). [2]
- graph.py:745-747 `correction_prompt` — hide-inner-details — reads `node.rules.entries.get(rule)`, the rules collection's storage dict, instead of asking the collection for the rule. [3]
- graph.py:65-102 `_BracketDepth` — eliminate-duplication — two ways of counting depth in one class: parentheses and braces through the `_OPENING` table with `setattr`/`getattr` by attribute name (100), brackets by `line.count` (84), which counts brackets inside strings, against the class docstring ("brackets inside a string do not count"). [2]
- graph.py:758 `GraphExplorer.source_members` — limit-paths-through-a-function — 11 paths (lizard). [3]

### harness/graph/graph_build.py

- graph_build.py:280, 351, 389 — use-consistent-naming — `WorkerBuild.carry_out` (make an order and run a worker), `GraphBuild.carry_out` (carry out an order in this process) and `GraphBuild._carry_out` (run one step) mean three different things; the graph before the step is `before` (156), `state` (340, 365, 382) and `saved` (372), and `_hold` (372) is a one-line wrapper of `graph.practices.hold`. (still open from round 1) [4]
- graph_build.py:360, 399 `schema_edges.syncs = False` — hold-state-on-the-object-not-in-parameters — a field set on the shared graph for one build and never restored, set twice on the worker path (carry_out, then `_carry_out`). (still open from round 1) [3][2]

### harness/graph/graph_reads.py

- graph_reads.py:57, 111, 129 `load(force: bool, apart: bool)` — provide-meaningful-context — two positional booleans; the calls read `self.load(False, apart)`. [4]
- graph_reads.py:31 `GraphReads.open` — make-module-only-operations-private — its only production caller is `open_saved` in the same class. [1]

### harness/graph/graph_practices.py

- graph_practices.py:30-34 `held`, `opened`, `chosen` — hide-inner-details — public mutable dict and list, read directly 14, 23 and 5 times in production code outside the class (graph_build.py, graph_reads.py, node_filter.py, schema_edges.py, schema_rules.py, space/kanban/knowledge_graph_examples.py ...). (still open from round 1) [1][4]
- graph_practices.py:80, 88, 94 `reopen`, `restore`, `hold` — use-consistent-naming — three names for taking a saved graph; `restore` adds only `overlays =` to `hold` and has one production caller (cdd_guidance/practices/bdd/model/graph_bdd_model.py:43), `reopen` one (graph_reads.py:53). [4]
- graph_practices.py:44, 51 `of(kind: type)`, `loaded(kind: type)` — use-typed-signatures — the parameter is any `type` and the answer a plain *PracticeGuidance*, not `type[P] -> P`, so each caller casts or reads untyped. [3]

### harness/graph/node_filter.py

- node_filter.py:209-229 `_fails_selected_rule`, `failing_rules` with graph_rules_collection.py:192 `chosen` (called at node_filter.py:257 and graph_rules_collection.py:190) — eliminate-duplication — three ways to pick the rules a filter chooses that a node fails. `Filter` matches a chosen rule by slug or by `practice.node.rule` label; `chosen` matches only `rule.slug in selected`. A filter with `rules: ["stories.Story.verb-noun-format"]` and `violations: true` keeps the node (`matches`) yet shows none of its rules under it (`chosen`). Choosing rules is the filter's job. [2][3]
- node_filter.py:144 `Filter.matches` — limit-paths-through-a-function — 15 paths (lizard); it also reaches `node.parent.parent` (151) on the assumption that a metric sits under a group under its node. [3]

### harness/graph/explorer.py

- explorer.py:74 `ExplorerEntry.__init__(children: list | None)` — use-typed-signatures — an untyped list on the constructor, while the property (90) is typed `list[ExplorerEntry | GraphRulesCollection]`. [3]

### harness/graph/saved_graph.py

- saved_graph.py:423-432 `SavedGraphFile.read` — refuse-unreadable-input — catches `JsonFileUnreadable` and answers `None`; `save` (434-436) then merges over `None` and writes over the file nobody could read, dropping every practice it held, though `JsonFileUnreadable`'s own contract says "Nothing is written over it". [3]
- saved_graph.py:35 `FactValue: TypeAlias = Any` — use-typed-signatures — the type of `Node.get_fact`, `set_fact` and `NodeFacts`, the most called seam of the graph, is `Any`; the comment says "plain JSON data", which a JSON type alias can say. [3]
- saved_graph.py:447 `PracticeChanges` against 149 `SavedPractice` — eliminate-duplication — both hold nodes, edges, violations and root facts and parse the same records; `violations` is a list on one and `violations_by_node` a dict on the other. (still open from round 1) [2]
- saved_graph.py:162, 461 `from_fields` — limit-operation-parameters — six parameters each, set as public fields after an empty constructor. (still open from round 1) [3]
- saved_graph.py:98 `SavedNode` — eliminate-duplication — flat `file`, `line`, `end_line` while *Node* holds a *Source*; the mapping is hand-written both ways (116-131, graph.py:1205, 1212), and the nine-key record is written out twice in the class (122-132, 136-146). (still open from round 1) [2]
- saved_graph.py:292-309 `SavedGraph.from_text` — single-boundary — a second parser of the `graph.return_nodes` answer shape, reading `rules`, `status` and `violations` by key. (still open from round 1) [2]
- saved_graph.py:521 `RecordChanges` — use-typed-signatures — `Any` on every member. (still open from round 1) [3]
- saved_graph.py:363 `SavedGraph.scope_name` and 201-223 `held_under`, `outside` — high-cohesion / put-logic-on-the-owning-resource — the name a render gives its output (kebab names, *RenderPlacement* from harness/guidance) and the work scope a validate keeps by story names sit on the saved graph; each has one production caller, cdd_guidance/actions/render/rendered_file.py:163 and cdd_guidance/actions/validate/checked_graph.py:158. `scope_name` has 12 paths and `PracticeChanges.from_record` (495) 12 (limit-paths-through-a-function). [1]
- saved_graph.py:153, 106, 363 — use-consistent-naming — the practice's key is `name` on *SavedPractice*, `practice` on *SavedNode*, and `practice_key` on `scope_name`. [4]

### harness/graph/graph_app.py

- graph_app.py:16 `GRAPH_APP` with graph.py:22 — seam-names-current-code — the module card says both that harness/diagnostics makes and registers the Graph app (module-context.md, line 7) and that graph_app.py does (line 11); the code registers it here, as a side effect of graph.py's import (line 22, `noqa: F401`), so every importer of the graph, the worker process included, registers an app. [1]

### harness/graph/edge.py

- edge.py:102-118 `Edge.saved` / `key` / `record` — keep-classes-single-responsibility — one generic class holds two shapes. `saved` works only when the ends are nodes, because it reads `.node_id` on them. `key` and `record` work only when the ends are ids, because they put the ends into `graph.json` as strings. `from_record` (83) builds the id shape. (still open from round 1) [2]
- edge.py:34 `Display = str` — provide-meaningful-context — `"direct"`, `"grouped"`, and `"relationship"` are still bare literals: 21 production lines in 8 files (edge.py:65, 163, 200; graph.py:1123; model_node.py:121, 256; pattern_overlays.py:52; schema_edges.py:34, 206; three Clean Engineering model files). An alias of `str` gives these values no type to check against. (still open from round 1) [4]
- edge.py:131 `EdgeIndex.types` — hide-inner-details — a public mutable dict that sits beside `offer()` and `clear()`, which write it. It is read directly from explorer.py:194, graph.py:563 and 1122, node_filter.py:83, and rule_context.py:122. (still open from round 1) [3]

### harness/graph/model_node.py

- model_node.py:176 `_schema_edge_fields` and model_node.py:301-305 `subtree()` — extensions-live-with-the-domain — the base class still names Clean Engineering attributes (`collaborators`, `dependencies`, `type_hint`, `return_type`, `callees`). It also reads Stories' `examples` dict through `getattr(self, "examples", None)`. The practices already give their child lists through *PracticeNodeTypes*, so these attributes could come from there too. (still open from round 1) [1]
- model_node.py:333-348 `_SCHEMA_SYNC_PAUSED` / `schema_sync_paused` — eliminate-duplication; guardrail §1, "No global current objects" — a counter for the whole process pauses schema syncs on every graph. One graph's sync is guarded four ways: this global counter, the graph's own `SchemaEdges.held()` (schema_edges.py:151, used by `batch_schema_sync` and 8 model files), the public flag `SchemaEdges.syncs` (set from outside at graph_build.py:360 and 399), and `_syncing`. Four practice readings import the global pause (bdd, clean_engineering, ddd, and ux `graph_reading.py`). The cdd server holds a graph per session, so a load on one session's graph also pauses syncs on another session's graph. [2][3]
- model_node.py:224 `has_source_file` and model_node.py:326 `_sync_schema_edges` — the module's Constraint ("never `getattr` with a default") — `getattr(self.source, "file", "")` and `getattr(self, "practice", None)` read members that every *ModelNode* already has (`Node.__init__` sets `source` and `practice`). [3]

### harness/graph/pattern_overlays.py

- pattern_overlays.py:48 `GraphOverlay.name` — use-typed-signatures — `getattr(self.pattern, "pattern", None) or self.pattern.key` still leaves "guidance that has a pattern name" without a type. The registry keys patterns by `pattern_class.pattern` (100), so patterns declare the attribute and supplements do not. (still open from round 1: the supplement `graph_overlay` getattr is fixed, this one is not) [3][4]
- pattern_overlays.py:62 `practice_file(practice_key, name)` with schema_rules.py:289 `SchemaOverlays.__init__(key, ...)` — hold-state-on-the-object-not-in-parameters — both callers hold the practice. schema_edges.py:105 passes `practice.key`. schema_rules.py:336 passes `self._key`, a copy made only to rebuild this path, although the *PracticeSchema* that makes it holds `self.practice` (34). (still open from round 1) [3]
- pattern_overlays.py:67 `roles` — high-cohesion — it parses the `| Layer |` table in the pattern's Overview markdown. Its only production readers are harness/guidance_actions/generated_patterns.py:54 and patterns_file.py:66 and 70, which record the patterns content was generated with; round 1 moved that work out of this module, and no graph code reads `roles`. (still open from round 1, the part that did not move) [1]

### harness/graph/practice_reading.py

- practice_reading.py:145-157 `rules_in` with each rules package's `BY_SLUG` — eliminate-duplication — `rules_in` accepts two shapes, `BY_SLUG` or else `RULES`. All 10 production rules packages (6 practices, 4 pattern practices) write both, with the same line `BY_SLUG = {rule.slug: rule for rule in RULES}`. Only the spec fixture `harness/graph/fixtures/graph_checked_supplement/rules/__init__.py` writes `RULES` alone. Reading `RULES` only would delete ten copies of that line and one branch here; `getattr(rule, "slug", "")` reads a member every *PracticeGraphRule* declares. [2]
- practice_reading.py:131-133 `_package` with pattern_overlays.py:86 — eliminate-duplication / prefer-class-operations — both compute the package as `type(x).__module__.rsplit(".", 1)[0]`, then hand a dotted string to the module function `rules_in`, which imports it. The rules package of an owner could be one operation on the owner instead of a string built in two places. [2][3]
- practice_reading.py:72, 74 `in_graph` / `held_in` — use-intention-revealing-names — the object is a *PracticeNodes*, which the card calls "the practice's part", and the code reaches it as `in_graph` through `held_in`. `reading.in_graph.` is still written 92 times in production code. (still open from round 1) [4]
- practice_reading.py:125-142 `graph_checks`, `own_graph_checks`, `checks()` — use-consistent-naming — there are five names for "the rules a practice checks". `graph_checks` is a cached `own_graph_checks()`. `checks()` answers `in_graph.rule_run.checks`, or else a copy of `graph_checks`. `PatternOverlays.checks_of` (pattern_overlays.py:153) and `PracticeRuleRun.checks` are the other two. The one override, ddd/reading/graph_reading.py:201, is typed `-> dict`. Callers mix them: graph.py:1099 and 1159 and graph_rules_collection.py:155 call `checks()`, while pattern_overlays.py:159 and the DDD override read `graph_checks`. [2][4]

### harness/graph/practice_node_types.py

- practice_node_types.py:100-129 `NodeTypeTables._join` — guardrail §1, "Build once, keep it" — every lookup runs `_join`, and `_join` rebuilds `given` by asking every source for its node types. For the practices that means walking the catalogue's practice classes (practice_reading.py:176). `order_of` runs on every `EdgeType.from_kind` (edge.py:63), so this happens for every edge recorded (model_node.py:121, 254, 256; schema_edges.py:206; graph.py:1126). The tables could join again when a source registers, not on every read. [3]
- practice_node_types.py:62-64 `NodeTypeTablesDisagree` — domain-exception-carries-context — it keeps only `name`, and drops `table`, `held`, and `given`, the values that make the failure clear. They appear only in the message text. [4]

### harness/graph/rule_fixture.py

- rule_fixture.py:48 `SchemaRuleRun` — use-consistent-naming — it is still a second "rule run" beside *PracticeRuleRun*, and specs and rule examples in 6+ files construct it. Its docstring (50) names `InGraph.check`, a class that no longer exists; the check is `PracticeRuleRun.check`, graph.py:1094. (still open from round 1) [2][4]
- rule_fixture.py:43, 56, 65, 70, 78 `hits(self, rule)`, `SchemaRuleRun.__init__(self, rule, ...)`, `node_hits(self, node)`, `_recorded_on(self, node)`, `RulePair.__init__(self, rule, ...)` — use-typed-signatures — the parameters are untyped, though `PracticeGraphRule` and `Node` are the types every caller passes. `getattr(entry, "violations", [])` (72) reads a member that *GraphRule* declares. [3]

### harness/graph/schema_edges.py

- schema_edges.py:32 `_PHASES`, schema_edges.py:34 `_DISPLAY = {"demonstrates": "grouped"}`, schema_edges.py:70-74 `SchemaKey.phase` — extensions-live-with-the-domain — the framework still names the Stories and BDD step phases (`given`, `when`, `then`) and how a Stories/BDD edge kind is shown. *PracticeNodeTypes* already carries the practices' `edge_order` and `child_lists` and could carry these too. (still open from round 1, the part not moved to the node type tables) [1]
- schema_edges.py:43 `SchemaKey` — single-boundary — the mapping from schema key to node type still lives outside *Schema*. Every reader wraps `schema.types` keys again: schema_rules.py:98, 155, 192, 267, 272, 344, 351, 356, and schema_conformance.py:38. (still open from round 1) [2]
- schema_edges.py:177, 198-201 `_read_nodes`, `_linked_targets` — hide-inner-details — the code tells model objects apart with `hasattr(node, "semantic_type") and hasattr(node, "subtree")` instead of their type. It reaches a relationship by reflection, `getattr(owner, Name(field.kind).snake, None)`, so the contract is "keep a list attribute named after the snake-case kind". *ModelNode* already holds its lists with their kinds (`_child_lists`, `_reference_lists`, each `.kind`, model_node.py:193-194), so the owner could answer its targets for a kind itself. [3]
- schema_edges.py:138 `SchemaEdges.nodes` — hide-inner-details — a public mutable list that nothing outside the class reads. [3]

### harness/graph/schema_rules.py

- schema_rules.py:27 `PracticeSchema` — keep-classes-single-responsibility — it has 12 public members and four jobs. (1) Rule tables: `types`, `slugs_for`, `applicable`, `anchor_type`, `fidelities_for`. (2) Rule prose read from guidance: `rule_prose`, `_prose_collections`, `_longest_prose`. (3) Required relationships with fidelity stages: `requirements`, `current_stage`, `_stage_of`, `_earliest_stage`, `_fidelity_named`; only schema_conformance.py reads `requirements` and `current_stage`. (4) Explorer filter labels: `rule_label`, `rule_labels`. Prose changes with the guidance documents, and requirements change with fidelity order. [3]
- schema_rules.py:170-178 `_stage_of` — hold-state-on-the-object-not-in-parameters — it still splits `practice.type` strings and looks the other practice up by key (`graph.practices.held.get(practice_key)`). (still open from round 1) [3]
- schema_rules.py:140-146, 274-281 `_prose_collections`, `_longest_prose` — the module's Constraint — nested `getattr(..., None)` still reads guidance, fidelities, `RulesCollection.entries`, and `Rule.slug` / `body`, whose members are declared. (still open from round 1) [3]
- schema_rules.py:340-356 `_rules_of`, `_supertypes_of`, `_type_names` — prefer-class-operations — they are private now, but they are still module functions that take a *Schema* and wrap each key in *SchemaKey*. They belong on the schema, with its keys. (still open from round 1) [3]

### harness/graph/schema_conformance.py

- schema_conformance.py:86 `ConformsToSchema.rule` — do-not-invent-parallel-object-models — it is still the only check that holds its *Rule*, with prose written in Python. Every other check's prose comes from a practice document, joined by slug; schema_rules.py:134 special-cases `FRAMEWORK_RULES` to read `check.rule.body`. (still open from round 1) [2]

### harness/graph/violation.py

- violation.py:198 `Violation.by_rule` — prefer-instance-operations — it is still a static grouping function, not a factory. Production callers: space/kanban/report.py (5) and cdd_guidance/actions/validate/report_text.py (2). (still open from round 1) [3]
- violation.py:269-273 `NodeViolation.__init__` — hide-inner-details — it still passes a dummy `FoundBy("")` to the base, then overrides `rule`, `practice`, `node_id`, `subject`, `scope`, and `is_candidate`. It keeps a public `found_by` (a *GraphRule*) beside the base's private `_found_by` (a dummy *FoundBy*): two fields of one name and two meanings. (still open from round 1) [2]
- violation.py:63, 75 `FoundOn`, `FoundBy` — shape-classes-around-resources — records with no behaviour, built nested as `FoundBy(rule, practice, FoundOn(...), ...)` at 9 production sites: space/session/validation (4), space/kanban/ticket.py, the drawio scanners (2), and violation.py (2). (still open from round 1) [3]
- violation.py:48-60 `ViolationData` — use-typed-signatures — it has no `scope` key, though `scope` is a `data_field` (171-175) sent with every violation, and `from_data` reads `sent.get("scope")` (115). The typed shape of the saved graph's violation does not match what is written and read. [3]
- violation.py:142, 217 `location` / `in_file(location: str, file)` — use-consistent-naming — `location` here is a file path string, while `_location` beside it, the module's import, and every other use in harness/graph mean a *Location* (file and lines). *GraphRule.restore* (graph_rules_collection.py:119) has to rebuild a *Location* from the `location`, `line`, and `end_line` strings. [4]

### harness/graph/violation_correction.py

- violation_correction.py:18, 44 `CorrectedPlace`, `ViolationCorrection(rule: str, message: str, place, guidance: str)` — do-not-invent-parallel-object-models — a correction copies a node's name, type, file, lines, and text, and a rule's slug and messages, into strings. Both of its makers hold the real objects: `GraphRule.correction` (graph_rules_collection.py:124-133) holds its node, its violations, and its slug, and space/session/files/session_file.py:179 holds a *Violation*. [2]

### harness/graph/graph_rules_collection.py

- graph_rules_collection.py:28, 133, 155-156, 229 `GraphRule.__init__`, `correction`, `from_node`, `record` — do-not-invent-parallel-object-models — a rule's text, its check, and its rule on a node are still joined by slug, now in four places: `rule_prose.get(slug)`, `guidance_stating(self._slug)`, `checks.get(slug)`, and `self.entries.get(check.slug)`. graph.py:1106 holds the check and hands it back to be found again by its slug. (still open from round 1) [2]
- graph_rules_collection.py:192-196 `chosen` with node_filter.py:218-220 `Filter.failing_rules` — eliminate-duplication, and a likely defect — two functions answer "the failing rules of the chosen rules". `failing_rules` matches each chosen entry as a slug or as a `practice.node.rule` label (`_label_hits`). `chosen` matches the slug only (`rule.slug in selected`). The filter offers labels (explorer.py:201 `rule_labels`, built by schema_rules.py:115). So a filter chosen by label keeps a node (node_filter.py:215), but `kept_by` (190) shows an empty rules list under it. The spec (rule_category_spec.py:69) uses only the slug form. [2]
- graph_rules_collection.py:198-214 `slugs`, `passing_slugs` — no-use-delete — nothing in production reads `passing_slugs`; only harness/graph/graph_view_spec.py reads it (2 lines). `slugs` is read only by `passing_slugs` and by specs (graph_spec.py 4, schema_rules_spec 1, schema_conformance_spec 1). [1]
- graph_rules_collection.py:145, 216-224 `entries`, `__iter__`, `__getitem__`, `graph_rules` — hide-inner-details — there are four ways to reach the same rules. Callers outside read the public dict `entries.get(...)` directly: graph.py:746, rule_fixture.py:71, and stories/model/fixtures/bookshop_project.py:89. `__getitem__` has no production caller. [3]

### harness/graph/app/GraphPage.tsx

- GraphPage.tsx:42-43 `onError` / `onRejection` — eliminate-duplication — the base `ChatToldFailures` already has `failWith(failure: unknown, context)` (= `fail(reasonOf(failure), context)`, cdd-page-failures.ts:33), and the session board uses it (space/kanban/app/packages/session-board/main.tsx:14), yet this app writes `failures.fail(reasonOf(...), ...)` by hand here and in explorer/explorer-filter.ts:70, explorer/graph-load.ts:71, explorer/source-pane.ts:56, explorer/load-status.ts:70. Five copies of the one call the base names. [2]

### harness/graph/app/explorer/explorer-filter.ts

- explorer-filter.ts:6, graph-load.ts:8, load-status.ts:6, overlays.ts:3, page-folder.ts:3, source-pane.ts:5 — use-explicit-dependencies — every explorer class still reads the module singletons `graphs`, `failures`, `api` from graph/graph-page.ts instead of taking them in its constructor; `api` is exported only so graph-load.ts:82, 125, 129 and page-folder.ts:29, 39 can read `api.project`. (still open from round 1) [3]

### harness/graph/app/explorer/graph-load.ts

- graph-load.ts:90-104 `showLoaded` against overlays.ts:86-93 `showApplied` — eliminate-duplication — the same sequence twice: `normalizeInventoryBundle(...)`, `overlays.offer(bundle.available_overlays ?? [])`, `bundle.overlays?.length ? bundle.overlays : X`, `filter.offerChoices`, `filter.show`, `overlays.keep(bundle.overlays)`. (still open from round 1) [2][3]

### harness/graph/app/explorer/inventory-bundle.ts

- inventory-bundle.ts:4 `normalizeInventoryBundle(raw: unknown)` — use-typed-signatures — the generated client answers `InventoryData | null` (`inventory`) and `AppliedOverlaysData | null` (`setOverlays`, graph.ts:183, 219), both with required `overlays` and `available_overlays`; taking `unknown` and casting to `Partial<InventoryData>` throws that typing away, and the callers then default the same fields again (graph-load.ts:96-97 `bundle.overlays?.length`, `bundle.available_overlays ?? []`; overlays.ts:88, 90). All that is left to do is answer `{}` for `null`. [2][3]

### harness/graph/app/explorer/load-status.ts

- load-status.ts:97-105 `readProgress` — eliminate-duplication / hide-inner-details — reaches through the client to its transport (`graphs.api.post`) and writes the route `'/cdd/progress'` by hand; the same poll of the same route is written a third time in harness/files_app/app/files/files-graph.ts:155 and a fourth in the generated `ProgressViewGenerated` (cdd-views.tsx:110), while cdd-shared.ts:31 owns the route (`cddProgressRoutes`). [2][3]
- load-status.ts:62 `logLine(line, labels: boolean)` — use-intention-revealing-names — a bare boolean flag whose name does not say what it switches (whether the line may become the pane's label); the two callers pass `true` and `false` (103, 105). [4]

### harness/graph/app/explorer/overlays.ts

- overlays.ts:42 `Overlays.keep` against overlays.ts:102 `readSavedOverlays` — prefer-class-operations — the `cdd-graph-overlays` key is written by a method of *Overlays* and read by a free function that graph-load.ts:86 (its one caller) calls beside it; one stored value has two owners, so the format check at 108-110 is on the free function and not on the object that writes it. [3]

### harness/graph/app/explorer/page-folder.ts

- page-folder.ts:37 `openedFolder` and graph-load.ts:114 — hold-state-on-the-object-not-in-parameters — the *PageFolder* is made from `useState(openedFolder)` (34), yet `useGraphLoad` calls `openedFolder()` a second time to decide what to load first instead of reading the `PageFolder` it already holds (`this.state.folder.value`); `openedFolder` is exported only for that call. Like overlays.ts, the `cdd-graph-folder` key is written by `PageFolder.remember` (28) and read by the free function. [3]

### harness/graph/app/explorer/source-pane.ts

- source-pane.ts:61, 70 `rulesIn(trees)`, `chooseRule(trees, name)` — hold-state-on-the-object-not-in-parameters — App.tsx:87, 89 hands `filter.trees` to both on every render; the pane is made per render and could be given the trees once. (still open from round 1) [3]
- source-pane.ts:8 imports `SourceRule` from the view `source/SourceView.tsx`, and source/call-expansion.ts:3 (the call catalogue) imports `SourceCallout` from `source/source-callouts.ts`, the file of React hooks and DOM drawing — layer-separation — the state and catalogue files depend on view files for plain data types. (still open from round 1; the call-expansion import moved from SourceView.tsx to source-callouts.ts) [1]

### harness/graph/app/filter/FilterView.tsx

- FilterView.tsx:99 `OverlayItems` — extensions-live-with-the-domain — the hint names one pattern ("Click **Lern domain driven** above"), in harness code that the card says names no practice or pattern; the overlays the graph offers are already in `availableOverlays`, so a page without that pattern shows a button that is not there. [1][4]

### harness/graph/app/filter/filter-selection.ts

- filter-selection.ts:13 `nodeFilter(...) : Record<string, unknown>` — use-typed-signatures — still untyped and still renames `node_types` to `types`; Python's published operations now take a *FilterRequest* (graph.py:769, 781, 790), but the generated `explorerTrees` / `explorerBranch` still take `filter?: Record<string, unknown>` (.claude/language-adapters/typescript/harness/graph/graph.ts:171, 175), so the typing stops at the adapter. (still open from round 1) [2][4]

### harness/graph/app/filter_choices_record.py

- filter_choices_record.py:48-50 `FixtureSchema._rules`, 65 `part.rule_run.schema_with = lambda ...` — hide-inner-details — the recorder overrides *PracticeSchema*'s private cached property `_rules` (schema_rules.py:49) and replaces a method of the live *PracticeRuleRun* (graph.py:1067) with a lambda; it works only while those private names keep their shape, and a rename breaks the recorder with only filter_choices_spec.py to notice. A schema a practice can be given (or a constructor taking the rule table) would be the seam. [3]

### harness/graph/app/graph/GraphView.tsx

- GraphView.tsx:43-130 `TreeNode` — limit-function-lines — 88 lines (limit 50): row state, rule status and hint text, the twist button, the row button with its class list, and the recursive children in one component. [3]
- GraphView.tsx:73-76 against graph/graph-selection.ts:36-39, 46 and explorer/source-pane.ts:65 — eliminate-duplication — "is the rule a candidate, does it count as broken (`violating` or candidate, with hits), and its hit messages" is written three times: the tree's hover hint, `selectionForRule`, and `SourcePane.rulesIn` (`ruleHits(rule).map(hit => hit.message).filter(Boolean)`). [2]

### harness/graph/app/graph/explorer-trees.ts

- explorer-trees.ts:37 against 53, GraphView.tsx:69-70, 123 — eliminate-duplication / use-consistent-naming — the rules holder is found by `child.type === 'rules'` in `rulesOf` (37) and GraphView (70, 123), and by `child.name === 'rules'` in `holdsRuleWith` (53); a rule is found by `node.type === 'Rule'` (GraphView 69, 123) and by `isRule` (`'status' in item`, 7) in the same component (73-75, 106 uses both at once). *ExplorerTrees* now exists but the two tests of each stayed. (still open from round 1) [2][3]

### harness/graph/app/graph/graph-api.ts

- graph-api.ts:17 `GraphApi` — eliminate-duplication — near copy of harness/files_app/app/files/files-api.ts:16 `FilesApi`: the same `post` (fetch to `API_ROOT`, the project header, read text, parse, throw on `!ok`) and the same private `parsed` with the same "Invalid JSON from ... (HTTP ...)" message (the only two files holding it); the only differences are the Files header, the empty-body policy, and the error class. [2]

### harness/graph/app/graph/graph-failures.ts

- graph-failures.ts:9, 80-84 `TOAST_MILLISECONDS`, `toast` — eliminate-duplication — the toast rule (skip a text already showing, add it, remove it after 8 000 ms) is word for word `FilesNotices.toast` with its own `TOAST_MILLISECONDS = 8_000` (harness/files_app/app/files/files-notices.ts:8, 38-41). Both are pages of one `ChatToldFailures` family; the base is where `show` by toast would go once. [2]
- graph-failures.ts:80 `toast` — make-module-only-operations-private — public, called only by `show` (71) and `notTold` (76) in the same class; no other caller in production or tests. [1]
- graph-failures.ts:46 `fixOne` against harness/graph/.context/module-context.md — seam-names-current-code — the card says a correction goes "through `GraphFailures.correct`" and that the error boundary is in `app/main.tsx`; no `correct` exists (the operation is `fixOne`), and the boundary is `ExplorerErrorBoundary` in GraphPage.tsx:9 (main.tsx only renders `GraphPage`). [1]

### harness/graph/app/graph/query-progress.ts

- query-progress.ts:66-101 `readCompiled`, `readPlan`, `readQueued`, `readStarted` — no-legacy-api-after-refactor / no-use-delete — they parse CodeQL's log lines ("[n/m] Compiled", "Compiling query plan for", "Starting evaluation of", "query: n/m name"); nothing in the repository writes such a line (no match outside this file, `.context/graph.json`, and a built dist bundle), and query-progress.test.ts tests only `load:` lines. With them go `QueryStep.phase`, `steps`, `uniqueSteps`, `STEPS_KEPT`, and the "query" naming of a graph load's progress (`QueryProgress`, `queryProgress`, `queryName`). [2]

### harness/graph/app/serve-port.ts

- serve-port.ts — high-cohesion — not explorer code: imported by harness/files_app/app/serve.ts and space/kanban/app/packages/session-board/serve.ts as well as this app's start.ts; it belongs with the shared app runtime (the generated cdd-shared or harness/apps), not inside the Graph app's folder. (still open from round 1) [1]

### harness/graph/app/source/SourceView.tsx

- SourceView.tsx:88-139 `SourceEditor` — limit-function-lines — 52 lines (limit 50), most of it the Monaco options literal, which could be a named constant built from `wordWrap`, `origin`, and the glyph margin. [3]
- SourceView.tsx:234 `languageFor` — eliminate-duplication — a second, smaller mapping from a file's extension to Monaco's language beside the generated `languageOf` (cdd-files.tsx:24, which knows js, json, yaml, html, css); this one shows every file that is not `.py` or `.md` as TypeScript, `.js` and `.json` included. [2]

### harness/graph/app/source/call-expansion.ts

- call-expansion.ts:41-51 `CLASS_KINDS`, 198 `MODULE_OWNER = "_module"` — extensions-live-with-the-domain — the shared source view names Clean Engineering's and DDD's node types (`OoadClass`, `Entity`, `EntityRoot`, `ValueObject`, `Aggregate`, `Repository`, ...) and copies Clean Engineering's `MODULE_FUNCTION_HOLDER` (cdd_guidance/practices/clean_engineering/model/base_class_model.py:29); each practice already declares its class types (`PracticeReading.class_types`, read at graph.py:761), so a practice's new class type opens nothing here until this list is edited by hand. [1][4]
- call-expansion.ts:65 `Body` — eliminate-duplication — `FoldMember` is gone, but one member is still reshaped twice after the adapter's `NodeSourceData`: into `Body` (`start`/`end`/`label`, 190-195) and then into `SourceCallout` (`startLine`/`endLine`/`title`/`path`, 221-223). (still open from round 1) [2]
- call-expansion.ts:198 `MODULE_OWNER`, 226 `codeOf` — deep-module — exported with no importer anywhere (production or tests). [1]
- call-expansion.ts:93 `callsOn(line, bindings, at)`, 115 `classesAt` — hold-state-on-the-object-not-in-parameters / make-module-only-operations-private — public on the exported *CallCatalog* but called only by *CalloutScan* in this file (178-179); `callsOn` takes `bindings`, which is the scan's own state, so the catalogue answers a question about the scan's variables. [3]

### harness/graph/app/source/source-callouts.ts

- source-callouts.ts:41 `useCallouts(editor, callouts, within, editorLineOf, expand, goTo)` — limit-operation-parameters — six parameters; `callouts`, `within`, `expand`, and `goTo` describe one set of callouts and what opening them does, the shape `OpenCallouts` (143) already holds three of. [3]

### harness/graph/app/source/source-folding.ts

- source-folding.ts:90-164 `VS_CODE_FOLD_KEYS`, `FoldKeys`, `keybindingOf`, `chordPartOf`, `keyCodeOf` — high-cohesion — about 75 lines the Graph app's own page never runs: production users are only harness/files_app (files-fold-keys.ts, files-page.ts, file-source-view.tsx); in the Graph app they are read only by app.test.tsx (742-754). They belong with the Files app's fold keys. [1]

## Design proposals

1. **Private names that cross classes become real seams, or the work moves.** Round 1's "make private" fix renamed members another class calls. Either name each publicly with its reason on the card, or move the work: *RenderRequest* answers its `written` with the sketch's wording already in it; *DeclaredOutputs* asks a public question of *DeclaredFile*; *FidelityActions* holds the catalogue's runner and its actions; *WorkList* gets a constructor for a list made inside another; the fidelity offers *PracticeGuidance* public `guidance_parts` and `titled_section`. Ends guidance.py:563/615, declared_outputs.py:121, practice_formats.py:315, action_catalogue.py:119/193/200, guidance_actions.py:368, and the harness/guidance card finding.
2. **Type the session the framework sees.** *WorkedSession* declares typed protocols for its log as one chat writes it (`failure`, `guidance_action`), its record's fields (`as_dict`) and its graph (`refresh`, `applied_patterns`); *GuidanceAction* then answers typed `log`, `graph`, `session_practice`, and reads `stories` directly. Ends worked_session.py:55/63/131, guidance_actions.py:741-787 and 585/611-616.
3. **A fidelity holds its practice and its companion; the framework names a companion, not Clean Engineering.** The fidelities collection hands each fidelity its practice when it makes it; the working set hands the companion fidelity when the set is held; `clean_engineering` and `COMPANION_PRACTICE` become `companion`. A rules collection is handed its practice and fidelity by its holder, and the fidelities collection answers which fidelities come before one. Ends guidance.py:20/670/822, 827 and 758, rule.py:160-194 and rule.py:235-365.
4. **The format adapter contract is declared, and the practice holds adapter classes.** *FormatAdapter* declares `suffixes`, `holds_classes_only`, a leaf extension and a factory taking the settings; `format_adapters` holds classes typed `type[FormatAdapter]`; one kept `adapter(format)`, and `for_file` named for the new model it makes. Ends practice_formats.py:378/389/415, 386 and 406-547, guidance.py:290, and helps practice_formats.py:22.
5. **One assembler of a guidance's instructions.** `Guidance.instructions` takes its parts in order from one operation that the fidelity extends with its practice's parts and its companion. Ends guidance.py:217/1025 and lightens guidance.py:622.
6. **An action runs on a fidelity through one held object.** *FidelityActions* holds each *Action* with the runner; an *Action* answers whether its operation takes a parameter, so nobody inspects the raw function; the runner is made with the call it works for. Ends action_catalogue.py:65-166, 155, 105 and 119/193/200, and guidance_actions.py:891-906.
7. **The guidance argument is read once into a typed list.** *WorkList* holds one list of entries, each with its guidance, the fidelity worked at and the format, made by `take` from the command with the set and session the list already holds; `worked_on`, the five unions and the parallel lists go. Ends guidance_actions.py:331, 342, 38-47, 165/362, 505/768 and 314.
8. **One way to fill a declared path, and one name for `.context`.** *DeclaredFile* fills its named parts one way, and the `.context` folder name is imported from harness/installation everywhere. Ends declared_outputs.py:65/105/399 and 22, and the patterns_file.py constant.
9. **Source owns its Location** (graph core). Source is made from a *Location* and answers `location`; *SavedNode* keeps one. Ends graph.py:117, graph.py:476/935 and saved_graph.py:98.
10. **Split graph.py by job and make the explorer a part** (graph core; round 1's P4). `source.py`, `node.py`, `practice_nodes.py`, with *GraphExplorer* held rather than a base class. Ends graph.py's file-lines and maintainability finding, graph.py:693/1273 and graph.py:855/937/943/962.
11. **One place chooses a read** (graph core). *GraphReads* takes scope, roots and overlays in one operation and keeps its lock private; `kept_in` comes through Graph's constructor. Ends graph.py:1361/1396, graph.py:1302 and graph_reads.py:31/57.
12. **Stories aligns its own nodes** (graph core). The `align_to_*`, `widen_to_call_close` and `as_code_writes` move to a Stories subclass of Source. Ends graph.py:162-228/105.
13. **One path test, and groups are a kind of node** (graph core). One "file under these folders" with one forward-slash normaliser; `Node.is_group` made by `NodeTree._holder_for`. Ends graph.py:1034 and graph.py:634/653.
14. **One rule: text, check and findings held together** (graph rules; round 1's P1, narrowed). Each *PracticeGraphRule* holds its *Rule*; *GraphRule* reads its prose there; *ViolationCorrection* and *NodeViolation* are made from the real objects. Ends graph_rules_collection.py:28/133/155/229, schema_conformance.py:86, schema_rules.py:134/140-146/274-281, violation_correction.py:18/44 and violation.py:63/75/269-273.
15. **The filter chooses rules** (graph core and graph rules). `Filter.failing_rules(node)` is the one answer; `GraphRulesCollection.chosen`, `slugs` and `passing_slugs` go, and `entries` becomes private. Ends node_filter.py:209-229, graph_rules_collection.py:192-196/198-214/145/216-224 and graph.py:745.
16. **The node type tables own the remaining practice words and join when a practice registers** (graph rules). Ends schema_edges.py:32/34/70-74, model_node.py:176/301-305, practice_node_types.py:100-129 and edge.py:34.
17. **The schema owns its keys, and PracticeSchema splits by job** (graph rules). Ends schema_edges.py:43, schema_rules.py:27/170-178/289/340-356 and pattern_overlays.py:62.
18. **One way to pause schema syncs, on the graph** (graph rules). Ends model_node.py:333-348, schema_edges.py:138 and graph_build.py:360/399.
19. **A rules package lists RULES, and its owner reads it** (graph rules). Ends practice_reading.py:125-157 and pattern_overlays.py:86.
20. **One saved practice record** (graph core). *PracticeChanges* becomes a *SavedPractice* plus what was dropped. Ends saved_graph.py:447/162/461 and graph.py:1217.
21. **One page runtime for the three apps** (graph app). A shared page API, a toasting failures base, the progress read, the serve port and one `languageOf` in the generated runtime. Ends GraphPage.tsx:42-43, graph-api.ts:17, graph-failures.ts:9/80-84, load-status.ts:97-105, serve-port.ts and SourceView.tsx:234.
22. **The explorer page objects take their collaborators** (graph app). One page object handed to each hook; *PageFolder* and *Overlays* own their stored keys; one `showAnswered` for loads and overlays. Ends explorer-filter.ts:6 and its siblings, page-folder.ts:37, overlays.ts:42/102, inventory-bundle.ts:4 and graph-load.ts:90-104.
23. **A rule entry answers for itself** (graph app). *ExplorerTrees* holds the one test of a rules holder and of a rule; a rule view is shared by the tree, the selection and the source pane. Ends explorer-trees.ts:37/53, GraphView.tsx:43-130/69-76, graph-selection.ts:36-39 and source-pane.ts:61/70.
24. **The source view reads class types from the graph** (graph app). Ends call-expansion.ts:41-51/93/198/226, source-folding.ts:90-164, source-pane.ts:8 and source-callouts.ts:41.

## Fixed since round 1

**harness/guidance and harness/guidance_actions**

- guidance.py `files_to_render` / `render_request`: gone; a *RenderRequest* renders itself.
- guidance.py `render -> dict`: renders answer *Rendered*.
- guidance.py `session: Any`, `supplements -> list[Any]`: typed *WorkedSession* and *PracticeSupplement*.
- guidance.py `is_part_of_practice` duplicating `is_served_on_mcp`: deleted.
- guidance.py `titled_section`, `guidance_parts`, `EXAMPLES_PREAMBLE` public: private (two are now crossed by another class, listed above).
- guidance.py `SketchLens` placement: the card now records it beside the practice by design.
- declared_outputs.py pass-throughs to the session's written files: gone; *DeclaredOutputs* holds the patterns alone.
- declared_outputs.py `DeclaredOutputs` mixing the patterns with the session's files: the session's files moved to *WrittenOutput*.
- declared_outputs.py / worked_session.py `FidelityOutput` not declaring `written`: declared.
- declared_outputs.py `files() -> dict[str, list]`: typed with *SessionFile*.
- declared_outputs.py `is_written_in`, `file_beside` public: `is_written_in` private (crossed, listed above); `file_beside` now has a production caller (space/session/practices/practice_session_output.py:577).
- worked_session.py `WorkedSession` declaring `document_named` on the session and not `log`: now `paths` and `log`.
- worked_session.py / guidance_actions.py / graph.py three descriptions of the session: *ActionSession* deleted, and `Graph.for_call` reads `session.graph`.
- practice_formats.py `keeping_sketch_wording` public: private (crossed, listed above).
- practice_formats.py `ObjectModel`, `FormatAdapter`, `RenderContent`, `NoFormatReads`, `SourceFormatNotSet` named by nothing outside: *FormatAdapter* is now the base every adapter extends, and the card names the others as its contract.
- practice_reading.py moved to harness/graph (counted by the graph rules sub-judge).
- rule.py `bags` naming: now `collections`, and the `getattr(practice, ...)` reads of the practice are direct.
- rule.py `Rule.practice`, `pattern`, `shared` filled from outside: gone; `from_bullet` private.
- schema.py three definitions of a relationship field: one *SchemaRelationship*, read by schema_edges.py and schema_rules.py.
- schema.py `fidelity_errors`: deleted; `fidelities` private.
- stages.py `ApproachStage._placed` answering the catalogue's lists on every stage: moved to `ACTION_CATALOGUE`.
- stages.py `GENERATE`, `VALIDATE`, `RENDER` constants: deleted; the catalogue answers `writing_step` and `checking_step`.
- stages.py `covering` / `_CoveredScope`: the constructor takes `covers`.
- action_catalogue.py `has`, `action(name)`: deleted; `runner`, `fidelity_actions`, `run_on` private (crossed, listed above).
- guidance_actions.py `PATHS_NOTE`, `practice_slugs`: deleted.
- guidance_actions/__init__.py star re-export: explicit names with `__all__`.

**harness/graph core**

- graph.py `Filter` doing two jobs: split into *FilterChoices* and a per-request *Filter* (node_filter.py).
- graph.py `GraphExplorer.filter` kept on the graph for specs only: deleted; each query makes its own Filter.
- graph.py `filter: dict | None` on the published operations: now `FilterRequest`.
- graph.py `Graph.practice(key)` duplicating `practices.named`: deleted; `restored_from` moved to `practices.restore`.
- graph.py `for_call`'s `getattr(session, "graph", None)`: now reads `session.graph`.
- graph.py `call` handed through four layers: the toolset decides `apart` (`BuildTask.apart`).
- graph.py `root` parameter on `align_to_example_export` / `align_to_declaration`: gone, read from the source.
- graph.py `Source.contents` and `Call.order` with no reader: deleted.
- graph.py `load_calls`, `insert_calls` public: now private.
- graph.py `_under_any`, `_decorated_end`, `_where_it_sits` module functions: now methods of their classes.
- graph.py `_HeldNodes` / `PracticeNodes` / `PracticeLoading` forwarding: `_HeldNodes` deleted, PracticeNodes holds its nodes.
- graph.py `Node.schema` and `PracticeRuleRun.checks` untyped; `Node.passing_rules` used only by a spec: typed and deleted.
- graph.py `explorer.explorer_trees` / `explorer_branch` repeating their owner's name: the explorer part is gone.
- graph_build.py in-process `run` and `carry_out(order)` repeating three steps: both call `_build`.
- graph_build.py `HeldAnswer`, `WorkerBuild`, `WORKER_MODULE` on the seam: `_WORKER_MODULE` private, both classes off the card's seam list.
- graph_build.py importing `GraphLoaded` from explorer.py: no longer.
- graph_reads.py `WorkingCopyRead`, `FilesRead` data bags: deleted.
- graph_practices.py `reopen(saved, folder)`, `hold(saved, folder)`: read `graph.scope.folder` themselves.
- explorer.py `PracticeInventory(graph, practice)` unused `graph` parameter: removed.

**harness/graph rules, schema and reading**

- practice_reading.py: *PracticeReading* moved from harness/guidance to harness/graph (round 1 P2).
- practice_reading.py: the protocols `HoldingGraph`, `HeldRuleRun`, and `HeldNodes` are deleted.
- practice_reading.py: `rules_in`, `graph_checks`, `own_graph_checks`, and `checks` are typed `dict[str, PracticeGraphRule]`, not `dict[str, Any]`.
- practice_reading.py: `reads_after` names practices by class, not by key.
- practice_reading.py: `package` is private (`_package`).
- schema_edges.py: `_NODE_TYPES`, `CHILD_LISTS`, and `_EVIDENCE_KINDS` moved to the practices' *PracticeNodeTypes* through `NODE_TYPE_TABLES`.
- schema_edges.py: the edge-kind switch `_matches` / `_epic_uses` is replaced by `PracticeNodeTypes.links`.
- schema_edges.py: `NodeEvidence` is deleted.
- schema_rules.py: `for_node(node)` is typed `Node`.
- schema_conformance.py: `getattr(node, "phase", "")` became `node.get_fact("phase", "")` (the likely defect on worker-refreshed nodes is fixed).
- practice_rule.py: `check_practice` returns `list[Finding]` naming the node, not `(node_id, message)` pairs.
- practice_rule.py / violation.py: `check` returns `list[Finding]`; *Finding* is no longer a `str` subclass.
- graph_rules_collection.py: *GraphRulesCollection* no longer extends *RulesCollection*, and the `isinstance` filters are gone.
- graph_rules_collection.py: `record_violation(slug, message)` is replaced by `record(check, finding)`; the slug join remains (see Findings).
- graph_rules_collection.py: `clear_violations` is deleted.
- rule_context.py: `children` / `child_count`, which duplicated `targets`, are deleted.
- rule_context.py: `source_root` and `node()`, which nothing used, are deleted.
- pattern_overlays.py: `adds_rules_to(node: Any)` is typed `Node`, and the missing `Any` import no longer matters.
- pattern_overlays.py: `getattr(supplement, "graph_overlay", None)` is replaced by the declared attribute.
- pattern_overlays.py: the `pattern_named` wrapper over `_pattern` is now the one operation.
- pattern_overlays.py: `record_in`, `record_content`, `_recorded_in`, `_recording_instructions`, and `recorded_for` moved out to harness/guidance_actions (only `roles` remains).
- edge.py: `EDGE_ORDER` is replaced by `NODE_TYPE_TABLES.order_of`, which each practice fills from its own `edge_order`.
- model_node.py: `finish_building`, `keeps_list`, and `record_all` are private.

**harness/graph/app**

- graph/graph-failures.ts `GraphFailures` re-implemented `ChatToldFailures`: it now extends it, and `reasonOf` / `chatOfPage` come from the shared modules.
- graph/graph-failures.ts `api`, `chat` public for `correctInChat`: violation-chat.ts is deleted and `api` is private.
- graph/graph-selection.ts `ruleHits` accepted `violation?: string`: the branch is gone.
- explorer/*.ts `Held<T>` declared five times: one declaration in explorer/held.ts.
- explorer/overlays.ts:82 `addNamed` and filter/FilterView.tsx:54 compared a label with an overlay id: both compare `overlayId(item) === name`.
- explorer/inventory-bundle.ts bare practices-map branch: removed.
- filter/FilterView.tsx `overlayLabel` copied `overlayPathLabel`: deleted.
- source/call-expansion.ts `FoldMember` re-declared `NodeSourceData`: deleted (the `Body` reshape remains, listed above).
- source/call-expansion.ts `calloutsIn` five parameters and `calloutsOn` scan state: `SourceSpan` and `CalloutScan`.
- source/source-callouts.ts `Opening` state bag with `calloutsBlock` / `calloutSection` / `calloutRow`: the class `OpenCallouts`.
- Exported with no importer (`CALLOUT_MARK`, `CALLOUT_LABEL`, `CALLOUT_MENU`, `SourceHostProps`, `headingRanges`, `QueryStep`, `GraphCallFailure`, `PORT_ARGUMENT`, `CDD_HOME_ARGUMENT`): all now module-private.
- `'Loading the graph…'` written three times: one `LOADING_GRAPH` in graph/query-progress.ts.
- source/violation-prompt.ts `input` and graph/graph-selection.ts `node` naming: the parameters are now the rule and the fix asked.
- graph-selection.ts / source-pane.ts / GraphView.tsx bare `ExplorerEntryData[]` acted on by free functions: the class `ExplorerTrees` (the two tests of the rules holder remain, listed above).
- filter_choices_record.py:61 used `Graph.practice(key)` (round-1 fix 30): it calls `graph.practices.named(key)`.
