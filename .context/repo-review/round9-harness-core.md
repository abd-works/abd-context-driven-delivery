# Round 9: harness core, after the round-8 fixes

The area is the same as in rounds 6 to 8: `harness/annotations`, `harness/agent_tools`, `harness/markdown`, `harness/guidance`, `harness/guidance_actions`, `harness/installation` and `harness/process`. It covers production code, and specs, `_examples/` and generated files only where noted. I read the code at 5f36e6a2 on `ensure-domain-orientation-refactor`, 2026-11-08. The CDD MCP host served the same commit.

Checks used:
- **Graph:** `validate` with `graph: true` and `paths` set to the seven folders (absolute, forward slashes), one call at a time. Both runs answered, and both gave the same 334 Clean Engineering hits in 19 rules (see "Validate runs").
  - `clean-engineering-code`: `clean-engineering-code-20261109T014645.md` / `.json`
  - `clean-engineering-modules`: `clean-engineering-modules-20261109T014847.md`
  - Both are under `C:\Users\jeffa\.cdd\runtime\.sessions\ensure-domain-orientation-refactor\validation-reports\`.
  - This is the first round in which the modules run finished in this area. Its modules-only scanners (`one-way-deps`, `low-coupling`, `layer-separation`, missing module context, module naming) found nothing.
- **Code metrics:** `measure_revision.measure` on the worktree (r9), and on `metrics-runs-r8/src-r8` (the round-8 code before the fixes), so each class could be compared before and after the fixes.
- **AI:** I read the diff since 4359b907 (round 8) file by file. The main commit was 90fc4298 "Round 8 harness core and actions", together with `AppPorts` and `JsonFile` from 2bb7a24c. I read each changed file beside its importers. I grepped every removed name (`clean_engineering_companion`, `work_at`, `render_at`, `result_template`, `text_of`, `_part_text`, `_listed_practices`, `instantiate_all`, `self._chat`, `chat=` on an action) over `harness`, `space`, `tools`, `cdd_guidance`, `scripts`, `.context` and AGENTS.md, in `.py`, `.md`, `.ts` and `.drawio`. I read every member of the eight area classes above 100 total complexity or 30 methods.

No fix agent wrote a decision record in this area since round 8. The five records judged in round 8 still hold.

Status words follow the round-9 brief: **left**, **new**, **new scope**, **regression**, **decided**.

## Fixed since round 8

- **1** The guidance a fix agent reads names the current API.
  - `harness/guidance/AGENTS.md` names `FidelityGuidance.clean_engineering`, `RenderRequest.companion`, and `FidelityGuidance.render` / `render_files`.
  - `practice-guidance-model.md:11` says the current fidelity is fixed at construction.
  - `practice-guidance-sketch.md` traces the render through the fidelity.
  - `module-context.md` names the same.
  - The removed names `clean_engineering_companion`, `work_at` and `render_at` are gone from the code, the specs, the cards and AGENTS.md. The only exception is the repo model files, which no fix agent may touch (row 13).
- **2** An action is made from its call alone. `GuidanceAction.__init__(session, call)` (guidance_actions.py:236) has no `chat` parameter, and the log points at `self.call.chat`.
  - `_inside` passes `call=self.call`. The inner action holds its outer action and asks it for the practice set (`_practice_set`, :381) and the fidelity it works at (`fidelity_of`, :436), instead of copying `_practices` and `_worked_at`.
  - The spec takes the live path: "an action started inside another that wrote files … should refresh the graph for the call the outer action was made for" (guidance_actions_spec.py).
  - No caller anywhere constructs an action with `chat=`.
- **3 (mostly)** JSON object files now go through `JsonFile` in `cdd_home`, `mcp_daemon`, `mcp_server`, `project_approach`, `design_canvas/versions`, `hook_daemon`, `saved_graph` (`compact=True`), `claude_plugins`, `chat`, `board`, `session`, `work_state` and `prompt_notify`. `AppPorts` (installation/app_ports.py) reads an app's `ports.json` through it once. `JsonFile.write` now writes a staged file and renames it over the target, so a reader never meets half a file. One sibling is left: row 10.
  - `harness/mcp/scripts/connect.py:19` reads `runtime.json` by hand, and I dismiss it: it runs before the checkout is on the import path, and reads that file to find the checkout.
- **Round-8 scanner false positives fixed:**
  - `hide-inner-details` now counts the class's own name as itself: 21 hits in round 8, 7 now.
  - Near copies have the same floor as exact copies: `eliminate-duplication` went from 1 hit to 0.
  - DDD no longer makes building blocks in folders with no DDD model: 110 hits in round 8, 0 now.
  - BDD no longer applies the signature-marker check to finished specs: `framework-syntax` went from 28 hits to 0, and `no-implementation` from 788 to 38. The 38 left are a new false positive, listed under "Scanner false positives".
- **The recipe's result line.** `RecipeSource.result_template`, `text_of` and `_part_text` re-read the recipe's `return` as placeholder text beside the expansion that already evaluates it. They are deleted, and `RecipeExpansion.result` (recipe.py:288) is the one place a recipe's return is read. The spec covers a clause only some calls fill, and a parent's and a child's result.

### Decided (not counted)

These are unchanged from round 8, and I still agree with each:
- the guidance seam, 15 of 26 classes (`harness/guidance/.context/cdr/0003`)
- the markdown seam and process as a toolkit (`harness/markdown/.context/cdr/0001`)
- `document_in(session, …)` (guidance cdr 0003)
- `ContextConfig` in installation (`harness/installation/.context/cdr/0001`)
- `Name` in annotations (`harness/annotations/.context/cdr/0001`)

## Findings, most severe first

No high finding is in the area. Most of the rows below are **new scope**. This round names, for the first time, the jobs held by the area's oversized classes, using the metrics as evidence. Round 8 confirmed the `keep-classes-single-responsibility` hits but did not count them.

| # | Where | Concern | Found by | Status | Fix | Severity |
|---|---|---|---|---|---|---|
| 1 | Matching the tool name an IDE sends to a published MCP tool is done twice, by different rules. `GuidanceAction._payload_is_this_action` / `_comparable` (`harness/guidance_actions/guidance_actions.py:609-620`) takes the part after `__`, casefolds it, and maps both `.` and `-` to `_`. `McpServer.resolve_call_name` (`harness/mcp/mcp_server.py:433-446`) maps `_` back to `.` without casefolding or treating hyphens, and tries the first-dot form. The two can disagree on one name, so a rules hook can miss an action that the server resolved. | 1 | AI | new | `AgentTool` (which owns `mcp_name`) answers whether a client's spelling names it, and both callers ask it | medium |
| 2 | `PracticeGuidance` (`harness/guidance/guidance.py:321`, 70 methods, total complexity 199, 12 unrelated groups, depends on 44 classes, 34 public operations) holds four jobs that should be parts it holds. The format adapters and render, the knowledge-graph reading, and the schema each live under its own section comment, at :707 "## format integration", :415 "## the knowledge graph", and :576 "## workspace integration to move". See "PracticeGuidance: the jobs that should be parts". | 5, 9 | graph (`keep-classes-single-responsibility`) + metrics + AI | new scope | Hold a format-adapters part, a graph-reading part and the `Schema`; leave identity, text and fidelities on the practice | medium |
| 3 | `AgentToolSet` (`harness/agent_tools/agent_tools.py:679-741`, 32 methods, 7 unrelated groups) works out which members of **another** class hold tool collections. `_collections_on(instance)` calls `ToolsetMembers.of(type(instance))` and then reads that class's annotations through `_return_type(member, owner)`, `_is_collection_type` and `_is_tool_collection`. `ToolsetMembers` already owns "the members of one toolset class and which of them its annotations make tools". | 5 | metrics + AI | new scope | `ToolsetMembers.collections_on(instance)`, with the return-type reading moved there; `AgentToolSet` keeps only rehosting | medium |
| 4 | `TypeScriptToolset` (`harness/installation/language_adapter.py:413-470`, 39 methods, total complexity 105) builds a new `_DataShape` on every `_shape(shape)` call. That happens once for each field line, each reference and each peer check, and `_hint_type` makes `_FieldHint(hint)` three times in a row. Turning a Python hint into TypeScript type text (`_field_line`, `_hint_type`, `_reference_type`, `_identity_type`, `_shape_lines`) is the data shape's job, written on the toolset writer instead. | 5 | metrics + AI | new scope | Hold each shape's `_DataShape` once (by shape), and give it the hint-to-type writing; the toolset asks its shapes for their lines | medium |
| 5 | `FidelityGuidance` (`harness/guidance/guidance.py:1012-1043`, 54 methods, total complexity 138) does its session output's work. `reports()` globs `{slug}-*.md` in `session_output.reports_folder`, and `new_report_path()` makes that folder and dates the file name. `output_paths`, `files` and `has_declared_output` only forward to the same `session_output`. The fidelity reads its session output's folder and does that object's job beside it. | 5 | metrics + AI | new scope | `FidelitySessionOutput` answers `reports()` and `new_report_path()`; callers ask `fidelity.session_output` | medium |
| 6 | `GuidanceAction` (`harness/guidance_actions/guidance_actions.py:217`, 43 methods, total complexity 131, 4 unrelated groups) keeps its work list in loose fields beside its session, log and hook jobs: `_listed_items`, `_worked_at`, `_practices`, `_guidance_worked_on`, `_tool_items`, with `_outer` fall-backs in `_practice_set` and `fidelity_of`. Round 8's fix added two more fall-backs (+2 complexity). | 5 | metrics + AI | new scope | One held work-list part, made from the `GuidanceArgument`, answers `listed`, `fidelity_of` and `practice_of`; an inner action holds its outer action's list | low |
| 7 | `Installer` (`harness/installation/installer.py:303-336`, 30 methods, 7 unrelated groups) diagnoses the install it ran: `diagnose_after_install`, `diagnose_install`, `_deployed_channels`, `_published` and `_runtime_status_report`. It already holds `InstallDiagnostics` (`diagnostics`), which writes that result. | 5 | metrics + AI | new scope | `InstallDiagnostics` diagnoses from the record and channels it is handed; `Installer` asks it | low |
| 8 | `RulesCollection` (`harness/guidance/rule.py:157-330`, 27 methods, total complexity 102, 7 unrelated groups) holds rule injection after an edit: `inject_rules`, `_note_session_injected_rules`, `_bags_for_path`, `_matched_globs`, `_inject_echo_instruction`, `_read_only_notice`, `_chat_lines`, `_edited_label` and `_inject_context`. That job sits beside being a collection of rules. | 5 | metrics + AI | new scope | A held rule-injection part, which the hook is published from (`@published_where_held` already allows that) | low |
| 9 | `PracticeGuidance.render` (guidance.py:759) and `FidelityGuidance.render` (:1219) each build the same `RenderRequest` with the same four parameters. The practice's render differs only in passing `fidelities.current`. Round 8's `render_at` was replaced by a second public render, not folded into one. | 1 | graph (`limit-operation-parameters`, both) + AI | new | `PracticeGuidance.render` asks its current fidelity to render (a practice with no current fidelity renders as now), so one operation builds the request | low |
| 10 | `harness/graph/app/filter_choices_record.py:63, :67` reads and writes `filter-choices.json` by hand. This file was **added by a round-8 fix** (abd3f10f), after `JsonFile` existed. | 1 | AI | left (row 3 of round 8, partly; fix rule 7, "grep for the pattern before you close a finding", was missed for a new file) | Read and write it through `JsonFile` | low |
| 11 | `PracticeGuidance.read_paths(paths, source)` (guidance.py:753) never reads `source`, and `FidelityGuidance.render_files` passes it in all the same. | 3 | AI | new | Drop the parameter | low |
| 12 | Two classes are called `TypeScriptOperation` for two concepts. `harness/installation/language_adapter.py:223` writes one MCP tool as an adapter method; `cdd_guidance/practices/clean_engineering/model/typescript/typescript_class_model.py:31` is an operation of a parsed TypeScript class model. | 10 | metrics (`class_names_in_several_modules`) | new scope | Name the adapter's `AdapterMethod` (it writes a method that calls a tool) | low |
| 13 | The repo model files name deleted API: `.context/repo-model.md:277`, `repo-model.drawio:195` and `repo-model-disconnected.md:145` (`instantiate_all`). Round 8 wrongly counted `.context/repo-runtime.md` as fixed: it still names `instantiate_all` at :86 and :737. The files also name API this round's fixes removed: `clean_engineering_companion` (repo-model.md:1067, drawio:516, :537), `result_template` (repo-model.md:355, drawio:183) and `GuidanceAction(session…)` (repo-model.md:1289). | 11 | AI | left (round-8 row 4; no owner, because the fix briefs forbid fix agents to touch these files) | The lead regenerates the repo model and runtime files | low |

### Details

**1. Two rules for one tool name.** The hook's check decides whether the action's rules are injected after its own tool runs. The server's check decides which tool a call reaches. A client that sends `Generate-generate`, or a toolset slug with a hyphen, matches in one and not the other. The published name belongs to `AgentTool`, so the comparison belongs there too.

**4. A shape made per call.** `_shape(shape)` is `_DataShape(shape, self.peer_classes)`. `_shape_lines`, `_reference_type` and `_shape_reference` each make a fresh one for the same class, and `_DataShape.fields` walks `DataClass.of(...)` and every subclass again each time. This is the "part rebuilt on every call instead of held" pattern of concern 5.

**10. The pattern came back in a new file.** Round 8 named this exact job, and the fix moved thirteen places onto `JsonFile`. Then a new recording script in the same fix wrote the job by hand.

## PracticeGuidance: the jobs that should be parts

`PracticeGuidance` (guidance.py:321-907) is the area's largest class. It has 70 methods, total complexity 199 and 44 classes it depends on. The metric finds 12 groups of methods that share no data, and the graph rule counts 34 public operations (35 in round 8). The class's own section comments already mark where its jobs divide. Five jobs, of which four should be parts it holds:

1. **Format adapters and rendering (about 25 members), section ":707 ## format integration".**
   - **Members:** `formats`, `_format_adapter`, `format_reading`, `format_reading_with`, `format_for`, `readable_suffixes`, `supported_formats`, `_check_format`, `_live_adapter`, `_made_adapter`, `_takes_no_arguments`, `rendered`, `_render`, `_kept_wording`, `_model_for`, `_to_object_model`, `_is_object_model`, `_is_tool`, `_instantiate_from_tool`, `_context_root`, `_code_tree`, `_parse_content`, `_call_render`, `_incoming`, `read_paths`.
   - **What is wrong:**
     - `_live_adapter` keeps a cache hidden in `vars(self).setdefault("_live_adapters", {})`.
     - `_code_tree` walks the session's folder from disk (`rglob`) inside the practice.
     - `_made_adapter` inspects constructor signatures to decide how to make an adapter.
   - **Part:** one *practice formats* object the practice holds, made with the adapters it is constructed with. It makes each adapter once, picks the format for a file, and turns a `RenderRequest` into output. The practice keeps `render` as its published tool and hands the request to that part. `RenderRequest` already carries everything the render reads.
2. **Taking part in the knowledge graph (about 18 members), section ":415 ## the knowledge graph".**
   - **Members:** `graph`, `in_graph`, `reads_after`, `node_types`, `class_types`, `member_types`, `class_node_type`, `source_ordered_types`, `extends`, `anchor_types`, `rule_types`, `package`, `align_node`, `read_working_copy`, `link_to_other_practices`, `graph_checks`, `own_graph_checks`, `checks`.
   - **What is wrong:**
     - `graph_checks` caches in a `_graph_checks` field it creates with `getattr`.
     - The graph sets `graph` and `in_graph` on the practice, so each holds the other.
     - `rule_types` is the dict the `do-not-invent-parallel-object-models` scanner flags.
   - **Part:** every practice already keeps its graph reader in `model/graph_reading.py` (`StoriesReading`, `DddReading`, …). The metrics find that `DddReading` and `StoriesReading` have identical field sets, a sign that the reading base belongs in one place. The practice should hold one graph-reading object, made from its class's declarations, and the graph should talk to that object.
3. **The schema (6 members).**
   - **Members:** `schema` (the file's text), `_schema_path`, `schema_types` (the parsed `Schema`), `schema_guide`, `schema_node_fidelities`, `schema_fidelity_errors`.
   - **What is wrong:** `schema` and `schema_types` each read `model/schema.yaml`, one as text and one through `Schema.load`. That is one file with two readers (concern 9).
   - **Part:** `Schema` (schema.py) answers its text, its guide, its node fidelities against a list of fidelity names, and its errors. The practice holds one `Schema`.
4. **The session workspace, section ":576 ## workspace integration to move".**
   - **Members:** `work_in`, `files`, `output_paths`, `default_workspace_folder`, `session`.
   - **What is wrong:** each fidelity already holds its own session output (`FidelityGuidance.session_output`), so `files` and `output_paths` on the practice only forward to its fidelities. The comment says the job is waiting to move.
   - **Part:** the practice's session output, the `PracticeSessionOutput` it is handed in `work_in`. The practice holds it and callers ask it.
5. **The job the practice should keep:**
   - its identity: `key`, `slug`, `short_name`, `colour`, `answers_to`, `fidelity_called`, `fidelity_slugs`
   - its text: `document`, `guidance`, `instructions`, `scoped_markdown`, `examples`, `rules`, `every_rule`, `checked_rule_collections`
   - its fidelities
   - its set: `companion`, `extended`, `set_keys`, `hold_set`

Taking out parts 1 to 4 would leave about 25 members on the practice. Those members describe one practice and its words, and the module card already says that is the practice's purpose.

### Large, but one job (not counted)

`RecipeExpansion` (recipe.py:250, 45 methods, total complexity 192, the second highest in the area) has a single connected group of methods: it interprets one recipe body. It is large because recipes are a small language. Its loop-walking (`_walk_loop*`, `_loop_item_*`, `_reads_missing_loop_item`) and provider lookup (`_provider`, `_attribute_chain`, `_roots_at`, `_expand_cross_arg`) could become helper parts, but no job sits in the wrong class. `FileInstallation` (files.py:73, 30 methods, total complexity 129) is also one group: it writes one destination's files.

## Did a fix make a metric worse?

I compared the area's classes in the round-8 code before the fixes (`src-r8`) with this commit. No regression, but three classes grew:

| Class | Before → after | Why |
|---|---|---|
| `RecipeExpansion` | total complexity 188 → 192, methods 44 → 45 | it took the result line from `RecipeSource`, which fell 64 → 49 and 14 → 12 methods; net better |
| `GuidanceArgument` | 57 → 64 | `UnknownGuidance`, a new refusal |
| `GuidanceAction` | 129 → 131 | the `_outer` fall-backs (row 6) |
| `FidelityGuidance` | 136 → 138, methods 52 → 54 | it took `render` and `render_files` from `PracticeGuidance`, which fell 202 → 199 and 71 → 70; net better |

`JsonFile` now has 20 classes coupled to it, against none before: that is the intended effect of round 8's row 3, many owners using one writer.

## Graph hits: confirmed and dismissed

There are 334 Clean Engineering hits in 19 rules, down from 347 in 20.

| Rule | Hits | Judgment |
|---|---|---|
| `use-typed-signatures` | 175 | Dismissed, as in rounds 5–8: `cls`, and `Any` on framework parameters that take any toolset or callable. |
| `prefer-instance-operations` | 46 | Dismissed: registration seams and annotation classmethods, as in round 8. |
| `use-intention-revealing-names`, `avoid-vague-parameter-names` | 25, 15 | `item` in `GuidanceAction` (8 hits) is still real and not counted, as in round 8. The rest are setter `value`s, `fn`, the hook `payload` and `JsonFile.write(data)`. |
| `limit-operation-parameters` | 18 | Not counted, as in round 8. `PracticeGuidance.render` and `FidelityGuidance.render` (4 each) are row 9. `ToolCall.__init__` still takes 6, and `ToolCall.sent` takes 5; the measured `functions_over_5_parameters` list names only `ToolCall.__init__` in the area. |
| `keep-operations-small-focused` | 14 | Confirmed, the same list as round 8, plus `instructions_in` (28 lines) and `on_subject` (26). |
| `keep-classes-single-responsibility` | 7 | Confirmed. `PracticeGuidance` 34 (row 2), `FidelityGuidance` 25, up from 23 (row 5), `GuidanceAction` 20 (row 6), `Installer` 14 (row 7), `Markdown` 11, `ToolsetMembers` 10, `AgentTool` 10. |
| `hide-inner-details` | 7 | Dismissed: each is a reach into another instance of the **same** class, which the rule allows. The 7 are `AgentTool.answer` (2), `_render` → `owner._render`, `for_call` → `action._take`, `_inside` → `inner._outer`, `inject_rules` → `action._listed_inject_parts`, and `_shape_reference` → `peer._data_shape`. Scanner false positive (below). |
| `use-explicit-dependencies` | 5 | Dismissed, as in round 8. |
| `do-not-invent-parallel-object-models` | 4 | `PracticeGuidance.rule_types` is part of row 2. The other three are dismissed: `_RecipeLinesValidator._action_name` (as in rounds 7 and 8), `TypeScriptOperation.mcp_name` (it names an MCP tool, not the `Mcp` annotation class), and `ExpansionResult` "copying" `RunResponse` (see below). |
| `deep-module` | 4 | Decided (round 8): annotations 8 of 9, guidance 15 of 26, markdown 7 of 15, process 9 of 9. |
| `prefer-class-operations` | 3 | Left from round 7, low, and not in a goal class: `_folder_of`, `schema._loaded` and `_markdown_to_html`. |
| `never-swallow-exceptions`, `use-exceptions-properly`, `errors-out-of-existence` | 3, 1, 2 | Dismissed, as in round 8. |
| `keep-operations-single-responsibility`, `simplify-control-flow`, `limit-comments`, `provide-meaningful-context` | 2, 1, 1, 1 | Confirmed, as in round 8: `_toolset_refs_in_file`, `markdown.read_into`, `recipe._walk` 6 levels deep, the comment in `_base_class`, and the unnamed 30 in `ListeningPorts._output`. |
| `eliminate-duplication` | 0 | It was 1 in round 8, a false positive now fixed. |
| Modules-only scanners | 0 | `one-way-deps`, `low-coupling`, `layer-separation`, missing module context and module naming: no hits in the area. |

**Other practices on this area:**
- **DDD:** 0 hits, down from 110: the false positive is fixed.
- **BDD:** 186 hits on the area's specs, down from 962.
  - 38 `no-implementation` hits are false positives (below).
  - The rest are real spec-style findings, new scope for the BDD owner: `one-assertion-per-test` 110, `state-not-when` 16, `observable-behavior` 11 (guidance_actions_spec.py:149, :155, :344; installer_heavy_spec.py:742, :833, :837, :841, :880, :1335), `describe-is-plain-english` 8 and `shared-describe-subject` 3.
- These are not counted in the concern table, as in round 8.

**Duplicated helper names (metrics):** `_folder_of` is defined in both `harness/guidance/guidance.py:910` and `cdd_guidance/practices/ddd/model/graph_reading.py:276`. I dismiss it: they do different jobs. One finds the folder of a list of paths on disk; the other takes the parent of a project-relative string. No other repeated free-function name or clone group touches the area.

## Scanner false positives

- **BDD treats a finished spec that holds a sample spec as a behavior sketch.** `is_developed` and `has_signature_marker` (`cdd_guidance/practices/bdd/model/spec_source.py:15, :19`) search the whole file's text. `harness/guidance/practice_guidance_behavior_spec.py:72` holds `# BDD: SIGNATURE` inside a string that is a sample spec, so the finished spec counts as not developed. `NoImplementation` (`bdd/rules/tree_rules.py:63`) then flags all 38 of its blocks. The fix is to read the marker only in comments of the file's own `it` bodies, not in string literals.
- **`hide-inner-details` flags a reach into another instance of the same class.** `PythonFunctionBody.reaches_peer_private` (`cdd_guidance/practices/clean_engineering/model/operation_metrics.py:405`) now counts the class's own name, but not a local or parameter typed as, or known to be, the same class (`tool`, `owner`, `action`, `inner`, `peer`). Round 8 judged these allowed, and all 7 remaining hits are of this kind.
- **`_NAME_COPY` reads any `{word}_name` field as a copy of a class called `Word`.** `coupling_rules.py:24` matched `TypeScriptOperation.mcp_name` to the `Mcp` destination annotation. The name is the published tool's name, which `Mcp` does not own. `_action_name` is the same case, as in round 7.
- **`_copied_fields` counts three common words as a copied model.** `coupling_rules.py:95-114` reports `ExpansionResult` (`instructions`, `tools`, `result`) as a copy of the agent-BDD `RunResponse`. `RunResponse` is a nine-field record parsed from another process's output, and harness cannot import it. Three generic field names, with no type check, are a weak signal; the floor should require matching field types as well.

## Did the fix agents follow the round-8 fix rules?

- **Rule 7 (grep for the pattern before closing).** Followed for the deleted API in code, specs, cards and AGENTS.md (round-8 row 1). Missed in two places:
  - The new file `filter_choices_record.py` (row 10).
  - `.context/repo-runtime.md`, which no fix agent may touch, still names `instantiate_all`, and round 8 wrongly called it fixed (row 13).
- **Rule 8 (action specs at a non-first fidelity).** Followed in the area: "the scenarios fidelity renders while its practice was made at the story map" (practice_guidance_behavior_spec.py).
- **Rule 9 (two served calls through the live path).** The row-2 spec drives the inner action through a call that answers a chat and checks the graph refresh is made for that call. My two graph validate calls in a row (code, then modules) gave the same 334 hits.
- **Metrics gate.** The merged code passed it. No class in the area grew without a matching fall elsewhere (see "Did a fix make a metric worse?").

## Goal-class counts

These count the rows of the table above by goal class and status. A row naming two goal concerns counts once in each.

| Goal class | Concerns | left | new | new scope | regression | Total |
|---|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 0 | 0 | 7 (rows 2–8) | 0 | 7 |
| Shadow models | 2 | 0 | 0 | 0 | 0 | 0 |
| Duplicated functions | 1, 12 | 1 (row 10) | 2 (rows 1, 9) | 0 | 0 | 3 |
| **Goal total** | | 1 | 2 | 7 | 0 | **10** |

In the scope round 8 checked, the area has 3 goal findings, against 2 in round 8. Both round-8 goal rows are gone, apart from one file added during the fix (row 10). The other 7 come from reading the oversized classes job by job for the first time, as the round-9 brief asks. No high finding is in any goal class.

## What would make the next round cheaper

- **Split the large classes along the lines they already mark.** `PracticeGuidance` names its own misplaced jobs in section comments (":415 the knowledge graph", ":576 workspace integration to move", ":707 format integration"). A fix brief that takes one section per pass, with a spec on the part made once, would remove most of row 2 without a design debate. The same holds for each class in rows 3 to 8: in every one, the part to move the job onto already exists (`ToolsetMembers`, `_DataShape`, `FidelitySessionOutput`, `InstallDiagnostics`, `Schema`).
- **Grep for the owner before writing a new file.** Round 8 moved thirteen hand-written JSON readers onto `JsonFile`, and the same round added a fourteenth. Rule 7 asks for a grep before closing a finding. It should also ask for a grep for the finding's owner (`JsonFile`, `class_folder`, `Name`) before adding a new file that does the same job.
- **Give the repo model an owner.** Every round's renames pile up in `.context/repo-model.md`, `.drawio`, `repo-model-disconnected.md` and `repo-runtime.md`, because the fix briefs forbid touching them. Either the lead regenerates them at each merge, or the validators stop counting them.

## Validate runs

- **`clean-engineering-code`, graph, the seven folders.** Report `clean-engineering-code-20261109T014645.md` / `.json`. The build ran in the worker. The first two calls answered "still running", and the third returned the result. The saved graph holds CE 334, BDD 186, DDD 0 and Stories 0.
- **`clean-engineering-modules`, graph, the same seven folders.** Report `clean-engineering-modules-20261109T014847.md`, with the same 334 hits. It ran without error; in round 8 it failed in the Stories reader. The MCP host stayed up throughout.
