# Round 7: harness core, after the round-6 fixes

Area for round 7, the same as round 6: `harness/annotations`, `harness/agent_tools`, `harness/markdown`, `harness/guidance`, `harness/guidance_actions`, `harness/installation`, `harness/process` (production code; specs, `_examples/` and generated files only where noted). Code read at c8921451 on `ensure-domain-orientation-refactor`, 2026-11-08. The CDD MCP host served the same commit (`~/.cdd/runtime.json`).

Checks used:
- **Graph**: `validate` with `graph: true` and `paths` the seven folders (absolute, forward slashes), once for `clean-engineering-modules` and once for `clean-engineering-code`, one call at a time. The code run is the one the counts below use: report `clean-engineering-code-20261108T113659.md` / `.json` under `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\` (431 Clean Engineering hits in 21 rules). The modules run answered "No graph rule violations"; see "Validate runs" at the end, which also records a failed call.
- **AI**: each file read beside the files it imports and the files that import it; call sites checked with grep across `harness/`, `space/`, `tools/`, `cdd_guidance/` and `scripts/`; the diff since b91a73eb (round 6) read file by file; the four decision records the fix agents wrote read and judged.

Status words as the round-7 brief sets them: **left**, **new**, **new scope**, **regression**, **decided**.

## Fixed since round 6

- **1** Clean Engineering companion copied: `companion_practice` and `accompanying` are gone. `FidelityGuidance.clean_engineering` (guidance.py:1096) answers the companion fidelity of the practice's own set, held once, and the code format travels as a parameter of `instructions_in(format)` (:1118). Spec: `practice_guidance_behavior_spec` "should hold the Clean Engineering fidelity of its own set as that companion".
- **2** Slug round trip through `module:Class` text: `_slug_ref`, `_NamedPractice`, `toolset_ref` and `key_of` are deleted. `GuidanceArgument` reads a slug once into the action's own practice or fidelity (`answers_to`, `fidelity_called`; guidance_actions.py:151-159). Spec: "should work at the session's own fidelity that the slug names".
- **4** Two TypeScript type translators: `_text_type` is gone; `result_of` types the return hint through `_hint_type` (language_adapter.py:598-600).
- **5** Guidance repeating AgentToolSetOrigin: `slug`, `install_folder` and `class_folder` live once on `AgentToolSetOrigin` (agent_tools.py:88-115); only `FidelityGuidance` keeps its own slug and install folder, which differ. (Other copies of the class-folder lookup remain: row 11.)
- **6** Hand-kept annotation names: `RepositoryToolsets.ANNOTATIONS` is gone; install reads `annotation_kinds.installing_names` (annotation.py), and a spec defines a new `Ledger` kind to prove it.
- **7** Toolset attribute probes: `parameter_notes`, `schema_guide` and `pattern` are declared on `AgentToolSetOrigin`; files.py reads `PublishedRules` and `child_toolsets()` instead of `getattr` chains. The probes left in `Collect._bundled` and `_rehost_collection_tools` read collections generically and are not counted.
- **8** `module:Class` strings: `collect` is replaced by `references()`, which returns `ToolsetReference` objects. Text is made only where a process is started or compared with the install record (`agent_tools_probe.py:76, :86`).
- **12** `work_at(str)` and the activate hooks: `work_at(fidelity: FidelityGuidance)` (guidance.py:567) refuses another practice's fidelity; `_activate`, `_activate_fidelity`, `_make_current` and `_activating` are gone. Spec: "should refuse a fidelity of another practice".
- **14** `destination.py` holding four jobs: the data-class annotations and `DataClass` moved to `data_class.py`; `SourceFile` is an `Annotation` (data_class.py:236).
- **15** `guidance.py` ↔ catalogue file cycles: `guidance.py` no longer imports `practice_catalogue.py`, and `action_catalogue.py` names the fidelity through the `WorkedFidelity` protocol. The graph reports no `one-way-deps` hit in the area.
- **16** Edit events decided in `rule.py`: `RulesCollection` asks `payload.is_edit` (rule.py:160, :281); the event and tool table is in `HookPayload` (hook_server.py:136-140).
- **17** `GuidanceAgentOperation` in agent_tools: moved beside `GuidanceAction` (guidance_actions.py:171).
- **18** `_KEPT_FILES` spelling other classes' files: it reads `IdeLayout.MCP_CONFIG_NAME` and `InstallDiagnostics.NAME` (install_record.py:15).
- **20** `cdd_guidance` folder names in the installer: `RepositoryToolsets` owns `GUIDANCE_FOLDER`, `agents_folder`, `standing_rules_folder` and `references_folder`; the installer and files.py ask it. Only docstrings name the folder now.
- **24 (part)** `sketch_lens.py` and `declared_file.py` are folded into guidance.py. `documents.py` remains (row 9).
- **25** No use: `at_stage`, `default_output`, `Rule.attribute_to` and `GuidanceAction.guidance_text` are deleted with their spec lines.
- **Round-6 scanner false positives**: specs are no longer read by the code rules (0 hits on `*_spec.py`), the TypeScript templates are no longer read (0 hits), and `one-way-deps` now leaves out imports under `TYPE_CHECKING`, so the `agent_tools.py` ↔ `recipe.py` false cycle is gone.

### Decided (not counted)

- **3, class half** The catalogues as registries of classes (`harness/guidance/.context/cdr/0001-the-catalogues-are-registries-of-classes.md`). I agree for `_classes`: the hook daemon, the catalog command, the installer and the probes all need the list, and the framework cannot import `cdd_guidance`, so a registration seam held by the class is right. I do **not** agree for the shared instances; see row 1.
- **9** The `session=` word (`harness/guidance_actions/.context/cdr/0001-the-session-word-is-read-at-the-call.md`). Agreed: the word comes from outside the process, `session_file_named` reads it once in `for_call`, and nothing below holds the text. The rule's ban on `session=...` is about text passed inside the process.
- **10** `DeclaredFile` per call in the session output (`harness/guidance/.context/cdr/0002-a-declared-file-is-a-value-of-the-current-root.md`). Agreed: matching has one owner (`FidelityGuidance.declares`), and a joined path under a root that moves is a value, like a `Path`.
- **23** `ToolCall.session_in` (`harness/agent_tools/.context/cdr/0001-a-tool-is-handed-the-call-it-serves.md`). Agreed: tools now take `call` (`TakesFromCall`), and the two callers left serve no call, so a call built for them would be the stand-in the space review rejected.

## Findings, most severe first

No high finding is in the area's code. Two validate and graph failures outside the area are reported under "Validate runs".

| # | Where | Concern | Found by | Status | Fix | Severity |
|---|---|---|---|---|---|---|
| 1 | `harness/guidance/practice_catalogue.py:41` `_shared`, `:59` `practices()`, `:66` `practice()`, `:108` `practice_named()`; 8 callers (`board.py:113`, `prompt_notify.py:65`, `catalog_practice.py:63`, `guidance_probe.py:47, :89`, `probe_arguments.py:34, :43, :132`) | 5 | both (`prefer-instance-operations`) | left (round-6 row 3, shared-instance half; no spec) | Each reader makes its own set with `create_all()` (about 30 ms, the docstring says), or the process that needs one holds it; delete `_shared` | medium |
| 2 | `harness/guidance_actions/guidance_actions.py:365` and `:392` call `practice.work_at(...)` and set `fidelity.format` on the **session's shared** practice; `:226` `_worked_at`, keyed by `id(practice)`, keeps a second answer to "which fidelity"; the class docstring (:196-198) says calls "never see each other's", which `ToolCall.session` (tool_call.py:85-88, "one object its sessions hold") contradicts | 5, 2 | AI | new | An action holds the fidelity it works at and never moves its practice's current fidelity; `PracticeGuidance.format` and every reader of `fidelities.current` take the fidelity they work at | medium |
| 3 | `harness/guidance_actions/guidance_actions.py:288` `_discover_operations` copies `AgentToolSet._discover_operations` (agent_tools.py:660), changing only the operation class, and has already diverged: it calls `callable_on` directly and skips `_operation_callable`, so a guidance action's `@agent_tool` never gets `given_the_call` or a subject loader | 1 | both (`eliminate-duplication`, 76%) | new scope | `AgentToolSet` names its operation class (`operation_type: ClassVar`), `GuidanceAction` sets it to `GuidanceAgentOperation`; delete the override | medium |
| 4 | "The folder a class is defined in", four copies beside `AgentToolSetOrigin.class_folder` (agent_tools.py:103): `action_catalogue.py:57` `Action.folder`, `guidance.py:238-240` `_sketch_template_folder` (which also probes `getattr(self, "practice_guidance", None)`), `markdown.py:408`, and `catalog_generator.py:445` outside the area | 1 | AI | left (round-6 row 5; the fix removed the copy it was shown, the twins stayed) | One `class_folder(cls)` low enough for markdown to use (annotations), and every caller asks it | medium |
| 5 | `harness/guidance` exposes 15 of 26 classes (58%) | 6 | both (`deep-module`) | left (round-6 row 13; skipped, no decision record) | Keep `GuidanceCollection`, `DeclaredFile`, `SketchLens`, `RenderRequest`, `Action` behind the practice, fidelity and catalogues; drop the `__getattr__` re-export of everything in `guidance/__init__.py` | medium |
| 6 | `harness/installation/data_class.py:43` `Identity`, `:77` `Edits`, and the new `agent_tools.py:1307` `TakesFromCall` each repeat one body (`__new__`, `__init__` keeping a tuple of names, `annotate` setting it on the target) | 1 | both (`do-not-invent-parallel-object-models` on Edits/Identity) + AI (TakesFromCall) | new (TakesFromCall was added by a round-6 fix as a third copy) | One `NamesAnnotation` base in `harness/annotations`; the three name their flag | low |
| 7 | `harness/guidance/guidance.py:796-797` `_to_object_model` and `:882` `_incoming` turn a format back into a `Format`, because `story_code_render_spec.py:132` calls the private `_to_object_model(..., "typescript")` with text | 5 | AI | left (round-6 row 11, partly) | The spec renders through `render_files` or passes a `Format`; delete the rewrap and its comment | low |
| 8 | `harness/markdown` exposes 8 of 15 classes (53%); `harness/process` 9 of 9 (`ListeningPorts` added) | 6 | graph (`deep-module`) | left (round-6 row 19; no decision record) | Keep `OperationProperty`, `MarkdownScope`, `MarkdownFile` behind `Markdown`; `process` states its seam as a toolkit in its card | low |
| 9 | `harness/guidance/documents.py:13` `document_in(session, ...)`, a free function handed the session; `load_document` is also read by `space/session/session.py:202` | 8 | AI | left (round-6 row 24, part) | `GuidanceAction` and `PracticeGuidance` ask `session.document_named`; `load_document` moves to the session | low |
| 10 | `harness/installation/context_config.py`: installation never uses it; readers are `hook_server.py`, `space/session/session.py`, `practice_session_output.py`, `tools/granola/granola.py` | 8 | AI | left (round-6 row 21, round-5 #26; skipped twice, no decision record) | Move ContextConfig to the module that owns the project's `.context/`, or write the record that keeps it | low |
| 11 | `harness/annotations/name.py` `Name` in the annotations package; the graph now counts 7 of its 8 classes public | 8, 10 | both (`deep-module`) | left (round-6 row 22, round-5 #27; skipped twice, no decision record) | Its own small module, or a decision record | low |
| 12 | `harness/installation/install_diagnostics.py:124` `_write` and `context_config.py:49` `save` write a JSON file the same way | 1 | graph (`eliminate-duplication`, 76%) | new scope | One JSON-file writer that both hold | low |
| 13 | `harness/guidance/action_catalogue.py:14` says "guidance.py's *WorkedFidelity* answers it"; guidance.py has no such class | 11 | AI | new | Say that `FidelityGuidance` answers it | low |
| 14 | `AGENTS.md` "From the bottom up" still lists agent_tools below markdown and guidance / guidance_actions below installation, hooks and mcp; the code runs annotations ← markdown ← agent_tools ← installation ← hooks ← mcp ← guidance ← guidance_actions | 11 | AI | left (round-6 row 26) | Rewrite the order from the imports. The fix agents may not do it: `.claude/rules/learning-from-corrections.md` forbids agents to update any `AGENTS.md`, so the user has to, or the order moves to `.context/module-context.md` | low |
| 15 | `.context/repo-model.md:277`, `.context/repo-model.drawio:195` and `.context/repo-runtime.md:86` still name the deleted `instantiate_all` | 11 | AI | left (round-6 row 27) | Delete the lines and the diagram text | low |

### Details

**2. One current fidelity for every call.** Round 6 for space/session made one `Session` per folder, so every call in a session now shares its practices. `_worked_on` still moves the shared practice's current fidelity (`practice.work_at`) and sets the format on the shared fidelity, which also writes it into the session output. The code then guards against that move in three places: the action keeps `_worked_at`; `RenderRequest` carries its own format ("practices are shared between callers", guidance.py:765); and validate's `CheckedGraph` reads each format once "so another call changing a fidelity's format mid-way never changes which files this call checks". Anything that still reads `practice.fidelities.current` or `practice.format` reads whatever the last call set. That includes `_render`'s companion lookup (guidance.py:768), `_to_object_model`'s default source (:797), `scoped_markdown`, `checked_rule_collections` and `markdown_scope`. That is a second copy of state the fidelity already is (concern 2), kept because the owner is mutated per call (concern 5). If two calls in one session ever run at once, the guards cover only the paths someone thought of.

**3. A copy that has already drifted.** `AgentToolSet._discover_operations` builds each `AgentOperation` through `_operation_callable`, which hands a tool that takes `project` or `call` its argument from the call (`given_the_call`) and wraps a subject loader. `GuidanceAction`'s copy builds `GuidanceAgentOperation` from `members.callable_on` and does neither. No guidance action takes `call` today, so nothing fails yet. The first one that does will be handed nothing.

**4. Fix the pattern, not the copy.** Round 6 named `Guidance.class_folder` beside `AgentToolSetOrigin`, and the fix moved it there and cached it. The same `Path(inspect.getfile(cls)).resolve().parent` is still written out in the action catalogue, in `Guidance._sketch_template_folder`, and in markdown's scope reader, so the cache reaches one caller in four.

## Graph hits: confirmed and dismissed

The code run has 431 Clean Engineering hits in 21 rules. The `one-way-deps`, `low-coupling` and `missing-module-context` scanners report nothing in the area.

| Rule | Hits | Judgment |
|---|---|---|
| `use-typed-signatures` | 175 | Dismissed as in rounds 5 and 6: `cls`, and `Any` on framework parameters that take any toolset or callable. |
| `hide-inner-details` | 61 | Almost all dismissed as a scanner false positive (below): `cls._registered()`, `Installer._servers`, `cls.__dict__`. The real reaches are into another instance **of the same class** (`for_call` → `action._take`, `_inside` → `inner._outer`, `language_adapter.py:465` → `peer._data_shape`, `guidance.py:772` → `owner._render`), which the rule allows. |
| `put-logic-on-the-owning-resource` | 43 | The same 43 operations and the same false positive. None is real. |
| `prefer-instance-operations` | 50 | Confirmed for `PracticeCatalogue.practices` / `practice` / `practice_named` (row 1). The registration seams and annotation classmethods are dismissed as in round 6. |
| `use-intention-revealing-names`, `avoid-vague-parameter-names` | 23, 15 | `item` in `GuidanceAction` is still real (it is "a ref, a mapping, a practice or a fidelity"); the rest are setter `value`s and short loop names. Not counted. |
| `limit-operation-parameters` | 17 | Real for `ToolCall.__init__` and `FileInstallation.__init__` (5 each), as in round 6; the rest are value-object constructors. |
| `keep-operations-small-focused` | 13 | Confirmed: `language_adapter._base_class` (38 lines), `markdown._locate_under` (29), `Installer._install_run` (29), `instructions_in` (28), `process.alive` (27), `on_subject` (26, new this round), `_view` (26), `session_context` (25), `schema._read` (25). |
| `keep-classes-single-responsibility` | 7 | Confirmed: `PracticeGuidance` 34 public operations (32 in round 6, so it grew), `FidelityGuidance` 23, `GuidanceAction` 20, `Installer` 14, `Markdown` 11, `ToolsetMembers` 10, `AgentTool` 10. |
| `deep-module` | 4 | Confirmed (rows 5, 8, 11). |
| `do-not-invent-parallel-object-models` | 4 | `Edits`/`Identity` confirmed as copied code (row 6). Dismissed: `AgentToolValidationError.action_name` and `_RecipeLinesValidator._action_name` (a recipe's name in an error message, not a copy of the catalogue's `Action`), and `PracticeGuidance.rule_types`, which is keyed by node type, not by rule. |
| `eliminate-duplication` | 2 | Both confirmed (rows 3, 12). |
| `prefer-class-operations` | 3 | Confirmed, low, not in a goal class: `_folder_of` (guidance.py:903) belongs on `PracticeGuidance` (or on `RenderRequest`), `schema._loaded` on `Schema`, `_markdown_to_html` on `HTML`. |
| `use-explicit-dependencies` | 3 | Dismissed: `PracticeGuidance` makes a `Format` value; `InstallChannels` and `Installer` make parts from their own fields. |
| `never-swallow-exceptions`, `use-exceptions-properly` | 3, 1 | Dismissed as in round 6: `ToolsetMembers.of` and `DataClass.of` catch `TypeError` for built-in types only, and `RepositoryToolsets.classes` records each failure in `unloadable`. |
| `errors-out-of-existence` | 2 | Dismissed: `format_for` and `_to_object_model` raise on a format no adapter reads, which is a real failure. |
| `keep-operations-single-responsibility`, `simplify-control-flow`, `limit-comments`, `provide-meaningful-context` | 2, 1, 1, 1 | Confirmed: `recipe._walk` is 6 levels deep (left from round 6); `_toolset_refs_in_file` reads and parses; the 30-second timeout in `ListeningPorts._output` (process.py:67) needs a name. |

## Scanner false positives

- **`hide-inner-details` and `put-logic-on-the-owning-resource` count `cls` as a collaborator.** `PythonFunctionBody.reaches_peer_private` (`cdd_guidance/practices/clean_engineering/model/operation_metrics.py:408`) leaves out only `self` (`a.arg != "self"`), so `cls._registered()` in a classmethod is "another object's private state". Line 413 also takes a dunder (`cls.__dict__`, `cls.__subclasses__`) for a private field, although `private_reach` (:280-285) already leaves out `cls` and dunders. Together these produce nearly all of the 104 hits on the two rules in this area (for example `PracticeCatalogue.keys`, `ActionCatalogue.register`, `Format.__new__`, `Annotation.written_as`, `IdeLayout.every`). The fix: exclude the first parameter of a classmethod, and names that end with `__`.
- **The name-copy check matches any `*_name` to a class of that name.** `_NAME_COPY` (`cdd_guidance/practices/clean_engineering/rules/coupling_rules.py:23`) reads `action_name` in `AgentToolValidationError` as a copy of the catalogue's `Action`. It is the name of the recipe that failed, which the error message prints.

## Rule-versus-schema gaps

This area holds no practice, so it has no BDD, Stories or DDD schema to check. Note only that the code run's graph also holds 833 BDD violations on these seven folders, where BDD reads Python files as specs. That belongs to the BDD validator's area.

## Did the fix agents follow the round-6 fix rules?

- **A concern-5 fix has a spec on the effect.** Yes, for rows 2, 11 and 12 and for the companion (row 1). No for the catalogue's shared instances (row 1 of this round): the record keeps them with no spec showing that nothing changes a shared practice.
- **A duplicate has one owner and its twins are gone.** No for the class-folder lookup (row 4). The rule missed is "grep for the job, not the function". Row 6 is the same pattern in reverse: the fix that added `TakesFromCall` copied an existing body instead of reusing it.
- **A skip has a decision record.** Yes for rows 3, 9, 10 and 23 of round 6. No for rows 13, 19, 21, 22, 24 and 27 of round 6 (rows 5, 8, 9, 10, 11 and 15 here). Rows 10 and 11 have now been skipped in rounds 5, 6 and 7 with no record.

## Goal-class counts

Rows of the table above by goal class and status. A row naming two goal concerns counts once in each.

| Goal class | Concerns | left | new | new scope | regression | Total |
|---|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 2 (rows 1, 7) | 1 (row 2) | 0 | 0 | 3 |
| Shadow models | 2 | 0 | 1 (row 2) | 0 | 0 | 1 |
| Duplicated functions | 1, 12 | 1 (row 4) | 1 (row 6) | 2 (rows 3, 12) | 0 | 4 |
| **Goal total** | | 3 | 3 | 2 | 0 | **8** |

Round 6 had 16 goal-class counts in this area. Round 7 has 8, of which 2 are new scope. Leaving those out, the comparable figure is 6, a fall of 63%. Four round-6 goal rows are now decided (rows 3 class half, 9, 10, 23) and are not counted.

## What would make the next round cheaper

- **Grep for the job before closing a duplicate.** The class-folder lookup (row 4) and the names-carrying annotation (row 6) are the same miss as round 6's `_hint_type`: a fix removes or caches the copy it is shown, or writes a new class by copying a neighbour, and the same body lives on beside it. A fix brief should name the job ("the folder a class is defined in", "an annotation holding a tuple of names") and require a grep for its body text.
- **The session is now shared, so per-call state on a practice is a bug.** Round 6 made one `Session` per folder in space, and harness core still moves `fidelities.current` and `format` on the session's practices per call, then adds a guard wherever someone noticed (row 2). A fix should take "the fidelity this call works at" off the practice altogether. Otherwise every round finds another reader of `fidelities.current`.
- **Write the decision records for the skips.** Six left rows (5, 8, 9, 10, 11, 15) are skipped reshaping with no record. Rows 10 and 11 have been skipped for three rounds.

## Validate runs

- `clean-engineering-code`, graph, the seven folders: report `clean-engineering-code-20261108T113659.md` / `.json`, 431 Clean Engineering hits. The counts above use this run.
- `clean-engineering-modules`, graph, the seven folders: report `clean-engineering-modules-20261108T113159.md` / `.json`. It answered **"No graph rule violations"**, and the saved JSON holds 2403 Clean Engineering nodes and **0 violations for every practice**, BDD included. That is not true of these files. The code run on the same paths minutes later saved 431 Clean Engineering and 833 BDD violations, and an in-process `Graph.load_files` plus `refresh` on `harness/guidance` and `harness/guidance_actions` (with `is_answering_a_chat` forced on, so the worker process ran) gave 128. So a validate through the MCP host can report a clean graph that is not clean. The likely place is the session graph that every chat shares (`CheckedGraph._built_at` → `graph.refresh` → `graph.saved`) while other validators' calls refresh it. I could not confirm that, because the repeat call failed (next point). This belongs to harness upper and the validate action. It is **high**: a clean validate that is not clean.
- A second `clean-engineering-modules` call, on `harness/process` alone, **failed**, so per `.claude/rules/mcp-fail-loud.md` I stopped and made no further validate call:
  - Error: `RecipeLineFailed: Validate.validate recipe line ...\cdd_guidance\actions\validate\validate.py:57 graph_paths = self._graph.check_beside(self._reports) failed: GraphBuildFailed: the graph build's worker process exited with 1`.
  - Cause in the worker: `cdd_guidance/practices/ddd/model/stereotypes.py:98` `kind_named_by(self.oclass.stereotypes)` raises `AttributeError: 'Node' object has no attribute 'stereotypes'`, called from `ddd/model/graph_reading.py:203` `_members_by_folder`.
  - The same traceback appears at the end of `~/.cdd/server.log` for other agents' calls. In a worker, Clean Engineering nodes restored from the saved graph are plain `Node`s, not `OoadClass` objects, and DDD's reading expects the latter.
  - The MCP host itself stayed up and answering. This is outside harness core (harness/graph and DDD) and is **high**: once the session's graph holds restored nodes, every graph validate fails.
