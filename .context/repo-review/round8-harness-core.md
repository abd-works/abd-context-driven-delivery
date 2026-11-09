# Round 8: harness core, after the round-7 fixes

The area is the same as in rounds 6 and 7: `harness/annotations`, `harness/agent_tools`, `harness/markdown`, `harness/guidance`, `harness/guidance_actions`, `harness/installation` and `harness/process`. It covers production code, and specs, `_examples/` and generated files only where noted. I read the code at 4359b907 on `ensure-domain-orientation-refactor`, 2026-11-08. The CDD MCP host served 2c30c2f7 (`~/.cdd/runtime.json`, pinned), which has the same code in this area.

Checks used:
- **Graph:** `validate` with `graph: true` and `paths` set to the seven folders (absolute, forward slashes), one call at a time.
  - The `clean-engineering-code` run answered. Its report is `clean-engineering-code-20261108T163929.md` / `.json` under `C:\Users\jeffa\.cdd\runtime\.sessions\ensure-domain-orientation-refactor\validation-reports\`. It holds 347 Clean Engineering hits in 20 rules, 962 BDD hits and 110 DDD hits.
  - The `clean-engineering-modules` run **failed** in the graph worker, so I made no further validate call (see "Validate runs").
  - In place of `one-way-deps`, I scanned the area's top-level imports by hand.
- **AI:** I read the diff since c8921451 (round 7) file by file, mainly commit 802640f2 "Round 7 harness core". Each changed file was read beside its importers. I grepped call sites across `harness/`, `space/`, `tools/`, `cdd_guidance/` and `scripts/`, and grepped each job a round-7 fix named for its siblings. I read the five decision records the fix agents wrote and judged each one.

Status words follow the round-8 brief: **left**, **new**, **new scope**, **regression**, **decided**.

## Fixed since round 7

- **1** Shared practice instances. `PracticeCatalogue` holds classes only, and `_shared`, `practices()`, `practice()` and `practice_named()` are deleted (practice_catalogue.py). Each reader now makes its set once and holds it:
  - the board: `Sessions.board_practices`, a `cached_property`
  - a probe: `ProbeArguments.practices`
  - the notifier: once per class
  - the catalog: once per run

  No caller of the deleted operations is left anywhere.
- **2** One current fidelity for every call. `work_at` and `clean_engineering_companion` are deleted, and a practice's current fidelity is set once, in its constructor (guidance.py:349-354).
  - The action holds the fidelity it works at (`_worked_at`, now keyed by the practice) and hands it to render (`render_at`, `render_files(..., fidelity=)`; render.py:37-38), to generate (`fidelity_of`, generate.py:52) and to log lines (`_worked_output`).
  - `RenderRequest` carries the fidelity and answers its companion and source format.
  - Spec on the effect: guidance_actions_spec.py:474-502, "should leave the practice at the fidelity it was made at" and five more on each call's own rules, template and log line.
  - Setting `fidelity.format` is kept on purpose: the format is written to the session (`keep_format`) as the session's choice, which every chat of the session reads. The comment at guidance_actions.py:372 says so. I agree, and do not count it.
- **3** Copied `_discover_operations`. `AgentToolSet.operation_type` (agent_tools.py:646) names the operation class, and `GuidanceAction` overrides only that property (guidance_actions.py:292). An action's tools now go through `_operation_callable`.
- **4** The folder a class is defined in. `class_folder(cls)` in `harness/annotations/class_folder.py` is the one owner. Its callers are `AgentToolSetOrigin`, `Guidance.module_dir`, `PracticeGuidance.class_key`, `Action.folder`, `MarkdownScope`, `catalog_generator.py:446`, `pattern_overlays.py:133` and the reporter example.
  - `_sketch_template_folder` reads `module_dir`, which `FidelityGuidance` answers through its practice.
  - The only `inspect.getfile` left is inside `class_folder`.
- **6** Three copies of one names annotation. `NamesAnnotation` (annotation.py:135) is the one body, and `Identity`, `Edits` and `TakesFromCall` name only their flag.
- **7** The `_to_object_model` rewrap is gone: it takes a `Format`, and `story_code_render_spec.py:133` passes `Format("typescript")`.
- **12 (in the area)** The JSON-file writer: `JsonFile` (installation/json_file.py) owns reading and writing a JSON object file for `ContextConfig`, `InstallDiagnostics`, `InstallRecord` and the hook files. It has a spec, json_file_spec.py. The same job outside the area is still done by hand: see row 3.
- **13** The action_catalogue.py docstring now names `FidelityGuidance`.
- **14** The layer order in `AGENTS.md` now runs as the imports do, and the layers are written out in `harness/.context/module-context.md`.
- **15 (part)** `.context/repo-runtime.md` no longer names `instantiate_all`. The rest is row 4.
- **Round-7 scanner false positive, `cls` as a collaborator.** The scanner now leaves out the first parameter of a classmethod and dunders (operation_metrics.py:405-419). `put-logic-on-the-owning-resource` went from 43 hits to 0, and `hide-inner-details` from 61 to 21.

### Decided (not counted)

- **5** guidance exposes 15 of 26 classes (`harness/guidance/.context/cdr/0003-the-guidance-seam.md`). I agree.
  - The `__getattr__` re-export of everything is gone.
  - Every class the scanner names is either the seam itself (practice, fidelity, rules, stages, catalogues) or reached through it: `GuidanceCollection` is `fidelities`, `RenderRequest` passes between practices, and `Action` is what `fidelity.actions` holds.
  - The two exceptions are made outside the module for a stated reason: `SketchLens`, which each practice sets, and `DeclaredFile`, which the session needs because the framework cannot reach into it.
- **8** The markdown seam, and process as a toolkit (`harness/markdown/.context/cdr/0001-the-markdown-seam.md`; `harness/process/.context/module-context.md:9`). I agree. `__all__` names the seam, `MarkdownFile` is no longer used outside the module, and `MarkdownScope` and `OperationProperty` have reasons to stay public. Process is a set of small tools its callers use directly.
- **9** `document_in(session, ...)` (the same guidance record). I agree. The framework cannot name space's *Session*, the session answers its own half (`session.document_named`), and the folder reading has one owner, `load_document`.
- **10** `ContextConfig` stays in installation (`harness/installation/.context/cdr/0001-context-config-stays-in-installation.md`). I agree. Its readers include `harness/hooks`, so it has to sit at or below hooks, and installation is the module there that owns project JSON files, now through `JsonFile`. This closes a skip that ran through rounds 5, 6 and 7.
- **11** `Name` in annotations (`harness/annotations/.context/cdr/0001-name-lives-in-annotations.md`). I agree. `Annotation.written_as` reads `Name`, and nothing may sit below annotations. This also closes a three-round skip.

## Findings, most severe first

No high finding is in the area's code. One high failure outside the area is reported under "Validate runs": a graph worker crash in Stories that blocks every graph validate.

| # | Where | Concern | Found by | Status | Fix | Severity |
|---|---|---|---|---|---|---|
| 1 | `harness/guidance/AGENTS.md:3` tells agents to join companion text from **`PracticeGuidance.clean_engineering_companion.instructions`**, which round 7 deleted. `harness/guidance/.context/practice-guidance-model.md:11` still says "`work_at` makes one current" and "a practice with none renders through its current fidelity's Clean Engineering companion". | 11 | AI | new (left behind by the round-7 fix: `no-legacy-api-after-refactor`, which requires updating every doc and AGENTS.md mention in the same change) | Name `FidelityGuidance.clean_engineering` and `RenderRequest.companion`, and say the practice's current fidelity is fixed at construction and an action holds its own | low |
| 2 | `harness/guidance_actions/guidance_actions.py:440` `_inside` makes the inner action with `chat=self._chat` and no `call`. `GuidanceAction.__init__` (:211) takes both `chat` and `call`, and works out the chat from the call. An inner action's `self.call` is therefore `None`, so a graph refresh it starts (`wrote` → `graph.refresh(paths, self.call)`, :273) would run in the server's interpreter instead of a worker. No inner action writes today (`wrote` is called only from MCP tools made by `for_call`), so nothing fails yet. | 5, 10 | AI | new | `_inside` passes `call=self.call`; delete the `chat` parameter, so an action is made from its call alone | low |
| 3 | The same JSON-object file read and write done by hand, beside `JsonFile`: `harness/mcp/cdd_home.py:145, :252`, `mcp_daemon.py:150, :159`, `mcp_server.py:171, :191, :217, :265`, `catalog_generator/project_approach.py:82, :177`, `design_canvas/versions.py:103`, `hooks/hook_daemon.py:157` | 1 | AI | left (round-7 row 12, partly; fix rule 5, "fix every sibling", was missed: the fix moved the two files it was shown and the hook files, and left the rest of harness) | Every module at or above installation reads and writes its JSON object files through `JsonFile`; the code is in harness upper, the owner in harness core | low |
| 4 | `.context/repo-model.md:277`, `.context/repo-model.drawio:195` and `.context/repo-model-disconnected.md:145` still name the deleted `instantiate_all` | 11 | AI | left (round-7 row 15; the round-7 fix brief forbade fix agents to touch `repo-model.md` and `.drawio` files, so the finding has no owner) | The lead deletes the lines and the diagram text, or regenerates the model | low |

### Details

**1. The guidance a fix agent reads still names the deleted API.** `harness/guidance/AGENTS.md` is the first thing an agent reads before changing a practice. It tells that agent to use a property that no longer exists, so the next practice change will either fail or bring back a companion lookup on the shared practice, which is exactly what row 2 of round 7 removed. The fix brief allowed AGENTS.md edits this round.

**2. The call is the action's context, so hand it whole.** Round 7 added `call` to the action so a graph build knows to run in a worker, and kept `chat` beside it for `_inside`. Two parameters for one thing let a nested action keep the chat and lose the call, which is the same partial stand-in the round-6 rules ban. It is low only because no nested action writes a file today.

## Graph hits: confirmed and dismissed

The code run has 347 Clean Engineering hits in 20 rules, down from 431 in 21. The modules-only scanners (`one-way-deps`, `low-coupling`, `missing-module-context`, module naming) did not run, because the modules call failed. My hand scan of the area's top-level imports found no upward import. The only `harness.mcp` import in installation is in `_examples/note.py`.

| Rule | Hits | Judgment |
|---|---|---|
| `use-typed-signatures` | 174 | Dismissed, as in rounds 5–7: `cls`, and `Any` on framework parameters that take any toolset or callable. |
| `prefer-instance-operations` | 46 | Dismissed. These are the registration seams and annotation classmethods that the catalogue record and AGENTS.md ask for. The `PracticeCatalogue` instance operations confirmed in round 7 are deleted. |
| `use-intention-revealing-names`, `avoid-vague-parameter-names` | 24, 15 | `item` in `GuidanceAction` is still real, as in round 7. The rest are setter `value`s, `fn`, the hook `payload` and `JsonFile.write(data)`. Not counted, as in round 7. |
| `hide-inner-details` | 21 | All dismissed. About 12 hits are a class reaching its **own** private class field by name (`ActionCatalogue._runner`, `ToolCall._sessions`, `Installer._servers`, `PracticeCatalogue._classes`), which is a scanner false positive (below). The rest reach into another instance **of the same class**, which the rule allows: `AgentTool.answer` → `tool._from_the_call`, `AgentInstructions.answer` → `tool._expanded_reply`, `ToolsetMembers.of` → `held._owner`, `RecipeExpansion._merge` → `other._tools`, `_render` → `owner._render`, `for_call` → `action._take`, `_inside` → `inner._outer`, `inject_rules` → `action._listed_inject_parts`, `_shape_reference` → `peer._data_shape`. |
| `limit-operation-parameters` | 19 | Real, but not counted (round 7 did not count it either). `ToolCall.__init__` grew from 5 parameters to 6 with `answers_a_chat`, and `FileInstallation.__init__` takes 5. `PracticeGuidance.render_at` (5) is new, and it repeats `render` and `render_files` with one more argument. |
| `keep-operations-small-focused` | 14 | Confirmed, the same list as round 7, plus `PracticeGuidance.__init__` (22 lines), `_blocks_under` (23), `_event_text` (23) and `_remove_skills_naming_missing_mcp` (23). |
| `keep-classes-single-responsibility` | 7 | Confirmed. `PracticeGuidance` has 35 public operations: 34 in round 7, and 32 in round 6. Round 7 deleted 2 and added `render_at` and `format_reading_with`, so it keeps growing. Also `FidelityGuidance` 23, `GuidanceAction` 20, `Installer` 14, `Markdown` 11, `ToolsetMembers` 10 and `AgentTool` 10. |
| `use-explicit-dependencies` | 5 | Dismissed. `ContextConfig` and `InstallRecord` make their `JsonFile` from their own path, `PracticeGuidance` makes a `Format` value, and `InstallChannels` and `Installer` make parts from their own fields. |
| `deep-module` | 4 | All decided (rows 5, 8 and 11 of round 7). annotations counts 8 of 9, now with `NamesAnnotation`; markdown 7 of 15, down from 8; process 9 of 9; guidance 15 of 26. |
| `do-not-invent-parallel-object-models` | 3 | Dismissed. `_RecipeLinesValidator._action_name` is a recipe's name in an error, as in round 7. `PracticeGuidance.rule_types` is keyed by node type, as in round 7. `RecipeExpansion._loop_item_modes` is keyed by `id(loop.item)`, not by a name: it keeps the mode a recipe line gave a loop item on the expansion, so the shared toolset is not changed. That is the right shape. |
| `prefer-class-operations` | 3 | Left from round 7, low, and not in a goal class: `_folder_of`, `schema._loaded` and `_markdown_to_html`. |
| `never-swallow-exceptions`, `use-exceptions-properly` | 3, 1 | Dismissed, as in round 7. |
| `errors-out-of-existence` | 2 | Dismissed, as in round 7: `format_for` and `_to_object_model` raise on a format nothing reads. |
| `eliminate-duplication` | 1 | Dismissed. `FrontMatter.of_file` "nearly duplicates" `schema._loaded`, but both are the one-expression idiom `path.read_text(...) if path.is_file() else ""`, which five places use. A function for that would hide nothing. Scanner false positive (below). |
| `keep-operations-single-responsibility`, `simplify-control-flow`, `limit-comments`, `provide-meaningful-context` | 2, 1, 1, 1 | Confirmed, as in round 7: `recipe._walk` is 6 levels deep, `_toolset_refs_in_file`, `markdown.read_into`, and the unnamed 30 in `ListeningPorts._output`. |

### DDD and BDD rules on this area (first full run)

These are not counted in the concern table: harness core holds no practice, and specs are outside the rubric. I report them so that the BDD and DDD owners see them.

- **DDD, 110 hits of `every-class-carries-ddd-stereotype`** on `harness/installation` (45), `harness/agent_tools` (43), `harness/markdown` (15) and `harness/guidance_actions` (7). All are false positives. DDD makes an aggregate of any folder where a class's *name* follows a building-block convention:
  - `AgentOperation`, `GuidanceAgentOperation` and `TypeScriptOperation` count as value objects, because "Operation" is in `_VALUE_OBJECT_SUFFIXES`.
  - `Markdown` counts as an entity root, because some peer is named `MarkdownRepository`.

  It then flags every other class in that folder. These folders have no DDD model: the aggregate facts read `has_bounded_context: false` and `model_blocks: []`.
- **BDD, 962 hits on the area's specs.**
  - **816 are false positives:** `no-implementation` (788) and `framework-syntax` (28, "missing a BDD: SIGNATURE marker") apply behavior-fidelity rules to finished, development-fidelity specs.
  - **The rest are real, against the repo's spec style.** These are spec-style findings, new scope, for the BDD owner.
    - `state-not-when` (16): `agent_tools_spec.py:231, :451, :490, …`. AGENTS.md says "never `when`".
    - `one-assertion-per-test` (110).
    - `describe-is-plain-english` (8): `agent_tools_spec.py:376` 'AgentToolSet', and `markdown_spec.py:96`.
    - `shared-describe-subject` (3, in `agent_tools_spec.py`).
    - `observable-behavior` (9): assertions on private members in `action_catalogue_spec.py:27, :42`, `guidance_actions_spec.py:330` and six in `installer_heavy_spec.py`.

## Scanner false positives

- **`hide-inner-details` does not count a class's own name as itself.** `PythonFunctionBody.reaches_peer_private` (`cdd_guidance/practices/clean_engineering/model/operation_metrics.py:405`) builds the set of own receivers from `self`, the fixed class receivers, and a classmethod's first parameter. It leaves out the enclosing class's own name, so `ActionCatalogue._runner = runner` inside `ActionCatalogue.run_actions_with` is "another object's private state". The fix is to add the name of the class the operation is defined on to `own`. This accounts for about 12 of the 21 hits.
- **Near copies have no minimum size in practice.** `NearCopies` (`cdd_guidance/practices/clean_engineering/rules/near_copies.py:18`, `MIN_TOKENS = 24`) counts a one-expression body as long enough. `EliminateDuplication` (`operation_checks.py:322`) requires 3 lines for an exact copy, but `near_copies.py:50` applies no such floor. Use the same 3-line floor for near copies.
- **`do-not-invent-parallel-object-models` reads a dict keyed by `id()` as "keyed by its name".** `_member_keyed_by_name` (`cdd_guidance/practices/clean_engineering/rules/coupling_rules.py:142`) matched `RecipeExpansion._loop_item_modes: dict[int, str]` to a member class from the field's name. A key of type `int` is not a name. `_NAME_COPY` (coupling_rules.py:23) still reads `_action_name` as a copy of `Action`, as in round 7.
- **DDD infers building blocks from class-name endings in folders with no DDD model.** See `cdd_guidance/practices/ddd/model/stereotypes.py:39`, where "Operation" is a value-object suffix, and `:121`, where a class is a root when any peer is named `{Name}Repository`. They are used by `ddd/model/graph_reading.py:191`. The reader should make blocks only in folders a bounded context or a DDD model covers.
- **BDD applies behavior-fidelity rules to development-fidelity specs.** `NoImplementation.check` (`cdd_guidance/practices/bdd/rules/tree_rules.py:60`) and the SIGNATURE check (`cdd_guidance/practices/bdd/rules/spec_rules.py:44`) ignore the fidelity a spec is at.

## Did the fix agents follow the round-7 fix rules?

- **Specs take the live path.** Yes in this area:
  - The row-2 effect is specified end to end through `for_call` on one session, with two calls (guidance_actions_spec.py:474-502).
  - `JsonFile` has its own spec.
  - The graph-reading rule (rule 4) belongs to the graph and practice agents, and was missed there: see "Validate runs".
- **Every sibling fixed.** Yes for the class-folder lookup (seven callers, including the catalog and pattern overlays outside the area) and for the names annotation. No for the JSON file (row 3): the fix took the four files the finding and the hooks named, and left nine places in mcp, catalog_generator, design_canvas and hook_daemon. No for the docs of a deleted API (row 1).
- **One owner per finding.** Yes, with one gap. Row 4 has no owner, because the fix brief forbids fix agents to touch the repo model, so it can only close if the lead takes it.
- **Decision records for skips.** Yes. Every skip that round 7 found without a record (rows 5, 8, 9, 10 and 11) now has one, and I agree with each.

## Goal-class counts

These count the rows of the table above by goal class and status. A row naming two goal concerns counts once in each.

| Goal class | Concerns | left | new | new scope | regression | Total |
|---|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 0 | 1 (row 2) | 0 | 0 | 1 |
| Shadow models | 2 | 0 | 0 | 0 | 0 | 0 |
| Duplicated functions | 1, 12 | 1 (row 3) | 0 | 0 | 0 | 1 |
| **Goal total** | | 1 | 1 | 0 | 0 | **2** |

Round 7 had 8 goal-class counts in this area, of which 2 were new scope. Round 8 has 2, with no new scope. All of round 7's goal rows are gone or decided except the JSON-file siblings (row 3), which are now harness upper's code.

## What would make the next round cheaper

- **A deleted name must be grepped for in docs, not only in code.** The fix ran its grep for `work_at` and `clean_engineering_companion` over the code and specs, and missed `harness/guidance/AGENTS.md` and the module's own model card (row 1). A fix brief should require `grep -rn <deleted name> --include=*.md` over the module's `.context/` and AGENTS.md before commit.
- **Name the job across the whole of harness, not the files in the finding.** Round 7 named "one JSON-file writer that both hold" with two examples, and the fix gave that job one owner for those two and the hook files only. Thirteen places in harness upper still read and write JSON object files by hand (row 3). The same happened to the class-folder lookup in round 7 and to `_hint_type` in round 6.

## Validate runs

- **`clean-engineering-code`, graph, the seven folders.** Report `clean-engineering-code-20261108T163929.md` / `.json`, with 347 Clean Engineering, 962 BDD and 110 DDD hits. The build ran in the worker. The counts above use this run. Round 7's "clean validate that is not clean" did not recur here: the run returned hits that match the code.
- **`clean-engineering-modules`, graph, the same seven folders, failed.** Per `.claude/rules/mcp-fail-loud.md`, I made no further validate call.
  - **Error:** `RecipeLineFailed: Validate.validate recipe line ...\cdd_guidance\actions\validate\validate.py:57 graph_paths = self._graph.check_beside(self._reports) failed: GraphBuildFailed: the graph build's worker process exited with 1`.
  - **Cause in the worker:** `cdd_guidance/practices/stories/model/graph_reading.py:147`, `StoryLinks._step_body`, reads `step.body.text`, and fails with `AttributeError: 'Node' object has no attribute 'body'`. The call comes from `stories.py:129` `link_to_other_practices` ← `graph.py:1530` `_read_working_copy`.
  - **Other callers:** `~/.cdd/server.log` (lines 62650-62893) shows the same traceback for other agents' validate calls.
  - **MCP host:** it stayed up and answering.
  - **Diagnosis:** this is the round-7 high failure in a sibling reader. Round 7 found DDD's reading expecting a full `OoadClass` where a worker build holds restored plain `Node`s, and the round-7 graph fix repaired DDD's reader (`c07e1a21`, "DDD reads the classes a build read"). Stories' reading of story steps does the same thing. The fix rules missed are rule 4 (a graph-reading spec builds through the worker on a restored graph holding several practices) and rule 5 (fix every sibling reader).
  - **Severity:** **high**, outside this area (Stories practice and harness/graph). Once a session's graph holds restored Stories steps, every graph validate in that session fails.
