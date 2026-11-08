# Round 6: harness core, after the round-5 fixes

Area for round 6: `harness/annotations`, `harness/agent_tools`, `harness/markdown`, `harness/guidance`, `harness/guidance_actions`, `harness/installation`, `harness/process` (production code; specs, `_examples/` and generated files only where noted). Code read at b91a73eb on `ensure-domain-orientation-refactor`, 2026-11-08.

**The area changed between rounds.** Round 5's harness core held `harness/hooks` and `harness/mcp` and not `harness/guidance` or `harness/guidance_actions`; round 6's holds the reverse. To keep the counts comparable:
- Every round-5 harness-core finding is checked below, wherever its code now lives. The ones in `harness/hooks` and `harness/mcp` are all fixed, so they appear only in "Fixed since round 5" and add nothing to the table.
- The round-5 **harness-upper** findings whose code is in `harness/guidance` or `harness/guidance_actions` (H1, H3, M2, M3, M8, M9, M10, M11, M14, M15, M16, M19, L2, L4) are checked here too, and the open ones are rows of the table, marked "(upper Hn)". If the harness-upper validator also reports them, count them once.

Checks used:
- **Graph**: `validate` with `graph: true`, guidance `clean-engineering-modules`, `paths` the seven folders above (absolute, forward slashes). The MCP host answered "still running", then dropped the connection; the run finished on the host and saved its report, which I read from the file: `clean-engineering-modules-20261108T081311_2.md` / `.json` under `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\` (343 graph hits, 17 rules). See "Validate runs" at the end: the code and model runs were not made, because the host stopped answering.
- **AI**: each file read beside the files it imports and the files that import it, call sites checked with grep across `harness/`, `space/`, `tools/`, `cdd_guidance/` and `scripts/`, and every module's imports (top level, inside functions, and under `TYPE_CHECKING`) mapped with a small AST script so file cycles are seen too.

Status words as the round-6 brief sets them: **left** (round-5 finding still true, completely or partly; "known skip" kept in brackets where `pending-skipped-reshaping.md` lists it), **new** (code that existed at round 5), **new scope** (seen only because this round reads file cycles), **regression**, **decided**.

## Fixed since round 5

Round-5 harness-core findings:
- **#1** Hook server reads `.cursor` whatever the IDE: `HookServer.from_repository` (hook_server.py:425) reads `InstalledHookHandlers`, the handlers of every IDE's hook install; the daemon's state is in `.hook-server/`, which belongs to no IDE (hook_daemon.py:159-178).
- **#2** Three import-folder lists: one `RepositoryToolsets.IMPORT_FOLDERS` (repository_toolsets.py:56); CddHome and the catalog read `pythonpath()`.
- **#3** Two skipped-failure classes: one `SkippedTool` / `SkippedTools` (installation/destination.py:333-379), used by hook_server.py:421 and mcp_server.py:335.
- **#4** `module:Class` by hand: no `f"{cls.__module__}:{cls.__name__}"` is left; callers use `ToolsetReference.of`.
- **#5** "This checkout" from `parents[2]`: the area has one, `RepositoryToolsets.of_running_checkout` (repository_toolsets.py:76). The others left are outside the area (catalog_generator, `mcp/spec_support.py`) or the hook daemon's own `sys.path` line before any import (hook_daemon.py:14).
- **#6** Two port claims: one `ExclusivePort` in `harness/process/process.py:25`.
- **#7** Two temporary-folder tests: one `is_temporary` (destination.py:275).
- **#8** `server_environment` copy: CddHome asks `RepositoryToolsets(self.source).pythonpath()` (cdd_home.py:175).
- **#10** The invoke line: AgentTool owns `INVOKE_PREFIX`, `invoked_names` and `is_invoke_line` (agent_tools.py:821-832); files.py asks it.
- **#11** postToolUse also serving afterFileEdit: decided once, `Hook.events_served` (hooks.py:104-107).
- **#12** `inject_rules` named in the framework: replaced by the `PublishedWhereHeld` annotation (agent_tools.py:670, :1212).
- **#13** Two `key: value` readers: one `FlatSettings` (front_matter.py:11), used by `FrontMatter.fields` and `YamlFields.mapping`.
- **#14** Two property builders: one `OperationProperty` (markdown.py:793), used by `Collect`.
- **#15** Two `_TOOLSET_LOAD_FAILURES`: one `AgentToolSet.LOAD_FAILURES` (agent_tools.py:479).
- **#16** No use: `instantiate_all`, `AgentTool.response`, `ContextConfig.set_guidelines` / `set_practice_folders` / `guidelines` and `Format.is_known` are deleted.
- **#17** Rebuilt per call: `InstallChannels.toolsets` is made once in its constructor; the hook server keeps one `ContextConfig` per root; `Markdown.as_property` is gone; `DataClass.of` is read once per class.
- **#19** `ToolSubjectLoader(type(toolset))`: language_adapter.py:607 reads `ToolsetMembers.of(...).subject_loader`.
- **#22** Stamp list naming higher modules: the daemon stamps the toolsets its installs list.
- **#24** TypeScript reading `server.json`: `cdd-connection.ts:89-97` runs `connect.py --address` and reads only what it prints. It still works out `CDD_HOME` / `~/.cdd` to find that script (:32), which a bootstrap needs.
- **#25** Cycles inside `harness/hooks`: none left, at run time or under `TYPE_CHECKING`.
- **#28** `sub_agent/` one-class package: `SubAgentAnnotation` is in agent_tools.py:1222.
- **#29** `running_process.py` / `stoppable_process.py`: folded into `process.py`.
- **#30** `bootstrap.py`: deleted; callers use `RepositoryToolsets`.
- **#31** `_project_root` and `mcpServers`: mcp asks `IdeLayout.folder_name` (mcp_server.py:269) and `mcp_servers_key` for the user-level entry.
- **#32** Stand-in `Markdown.from_label(None, ...)`: `markdown()` builds through `_labelled` and `OperationProperty`.
- **#33** `ToolSetCollection` repeating `AgentToolSetOrigin`: it derives from it (agent_tools.py:123).

Round-5 harness-upper findings in this area's folders:
- **H1** Practices, actions and patterns named by module string: they register with `PracticeCatalogue.register` / `ActionCatalogue`; `harness/guidance` holds no `cdd_guidance` module string or path.
- **M10** `read_paths` and `document_named` with one body: both call `document_in` (guidance/documents.py:13). (The diagnostics half of M10 is harness upper's.)
- **M11** `session_context` reading `session.json` from disk: it shows `session.fields` (guidance_actions.py:452).
- **L4** `practice._section(...)` from FidelityGuidance: gone; no area file calls another class's private member.

## Findings, most severe first

No high finding is left in this area.

| # | Where | Concern | Found by | Status | Fix | Severity |
|---|---|---|---|---|---|---|
| 1 | `harness/guidance/guidance.py:436` `companion_practice`, `:1098` `accompanying` | 2 | AI | left (upper H3, partly) | The fidelity asks its practice's set for the companion fidelity and hands it the format per request, instead of copying it | medium |
| 2 | `harness/guidance_actions/guidance_actions.py:121` `_slug_ref`, `:125-146` `_NamedPractice`, `:325` | 5 | AI | left (upper M2) | Resolve a slug once to the session's practice and fidelity objects | medium |
| 3 | `harness/guidance/practice_catalogue.py:43-44` `_classes` / `_shared`, `action_catalogue.py:110` | 5 | both (`prefer-instance-operations`, 24 hits on the two catalogues) | left (upper M8) | One catalogue instance the MCP host holds and hands to its callers | medium |
| 4 | `harness/installation/language_adapter.py:437-452` `_hint_type` and `:611-626` `result_of` / `_text_type` | 1 | AI | left (round-5 #9, partly) | Type results from the return hint through `_hint_type`, as fields are typed; delete `_text_type` | medium |
| 5 | `harness/guidance/guidance.py:99-120` `Guidance.slug` / `install_folder` / `class_folder` and `agent_tools.py:86-95` `AgentToolSetOrigin.slug` / `install_folder` | 1 | AI | new | Guidance keeps only what differs (the fidelity's folder) and inherits the rest from AgentToolSetOrigin | medium |
| 6 | `harness/installation/repository_toolsets.py:66-68` `ANNOTATIONS` | 2 | AI | new | Read the names of the annotation kinds from `annotation_kinds` (each kind knows its snake-case name) | medium |
| 7 | Toolset attribute probes: `files.py:140, :187, :207-218, :246, :311-315`, `agent_tools.py:952` (`parameter_notes`), `:1023` (`hasattr(..., "instructions")`), `hook_server.py:287` (`pattern`) | 5, 6 | AI | left (round-5 #18, known skip) | The toolset answers named properties | medium |
| 8 | `repository_toolsets.py:129` `collect` returns `module:Class` strings that `classes` (:121) parses back; read as strings by `catalog_generator.py:221`, `agent_tools_probe.py:76, :86`, `prompt_notify.py:126`, two scripts | 5 | AI | left (round-5 #20, known skip) | Callers take `classes()`; strings only at the process boundary | medium |
| 9 | `harness/guidance_actions/guidance_actions.py:82` `session_named` (the `session=` word) | 5 | AI | left (upper M3, known skip) | The board's call carries the ticket, and the call opens the ticket's session | medium |
| 10 | `space/session/practice_session_output.py:264-266` builds `DeclaredFile` per call from `harness/guidance/declared_file.py` | 2, 6 | AI | left (upper M9, known skip) | The session output asks `fidelity.declares(path)` | medium |
| 11 | `harness/guidance/guidance.py` format kept as a string and parsed with `Format(...)` at :538, :565, :696, :760, :774, :777, :792, :793, :833, :861, :1049, :1070 | 5 | AI | left (upper M15, known skip) | The fidelity holds a `Format`; a render request carries one | medium |
| 12 | `harness/guidance/guidance.py:525-556` `_activate` / `_activate_fidelity` / `_make_current` / `work_at(fidelity: str)` with the `_activating` flag | 5, 11 | AI | left (upper M16, known skip) | `work_at(fidelity: FidelityGuidance)`; delete the activate hooks | medium |
| 13 | `harness/guidance` exposes 15 of 25 classes (60%) | 6 | both (`deep-module`) | left (upper M14) | Move SketchLens, DeclaredFile and GuidanceCollection behind PracticeGuidance and FidelityGuidance | medium |
| 14 | `harness/installation/destination.py` holds 13 classes for four jobs (annotation kinds, `DataClass`, `Installation` and its base, `SkippedTools`); `SourceFile` (:267) is still a bare marker class used by `harness/graph` | 8, 2 | AI | left (round-5 #21, partly) | Make `SourceFile` an Annotation; move the annotation kinds and `DataClass` into their own file, keep the installation bases here | medium |
| 15 | `guidance.py` ↔ `practice_catalogue.py` and `guidance.py` ↔ `action_catalogue.py`, closed by imports under `TYPE_CHECKING` (practice_catalogue.py:10, action_catalogue.py:14) | 7 | graph (`one-way-deps`) + AI | new scope | Pass the catalogue into the practice set (row 3) so `guidance.py` no longer calls `PracticeCatalogue.create`; then the catalogue alone knows the practice type | medium |
| 16 | `harness/guidance/rule.py:332-335` `_just_edited` decides which IDE event and tool names mean "a file was edited" | 1, 6 | AI | new | `HookPayload` answers `is_edit`, beside `edited_path` and the event table in `hooks.py` | low |
| 17 | `harness/agent_tools/agent_tools.py:980` `GuidanceAgentOperation` is used only by `guidance_actions.py:257` | 7 | AI | new | Move it beside GuidanceAction | low |
| 18 | `harness/installation/install_record.py:12` `_KEPT_FILES` spells `mcp.json` and `diagnostics.json`, files other classes own | 9 | AI | new | Read `InstallDiagnostics.NAME` and the MCP installation's file name | low |
| 19 | `harness/markdown` exposes 8 of 15 classes (53%); `harness/process` 8 of 8 | 6 | graph (`deep-module`) | new (markdown), left (process, round-5 graph note) | Keep `OperationProperty`, `MarkdownScope` and `MarkdownFile` behind `Markdown`; `process` states its seam as a toolkit in its card | low |
| 20 | Folder names of `cdd_guidance` in the installer: `installer.py:233, :245`, `files.py:265`, `destination.py:321` | 7 | AI | left (round-5 #23) | The repository hands its agents, rules and references folders to the Installer | low |
| 21 | `harness/installation/context_config.py`: installation never uses it; readers are `hook_server.py:334`, `space/session/session.py:75`, `practice_session_output.py`, `tools/granola/granola.py` | 8 | AI | left (round-5 #26) | Move ContextConfig to the module that owns the project's `.context/` | low |
| 22 | `harness/annotations/name.py` `Name` in the annotations package (one of its 7 public classes) | 8, 10 | both | left (round-5 #27) | Its own small module or `markdown` | low |
| 23 | `harness/agent_tools/tool_call.py:97` `ToolCall.session_in`, a class-level lookup; now also called by `space/session/file_manager.py:140` | 5 | both (`prefer-instance-operations`) | left (round-5 #34, known skip), one more caller | SessionOpener answers "the session open in this project" | low |
| 24 | `harness/guidance/sketch_lens.py` (16 lines, one class), `declared_file.py` (one class), `documents.py` (two functions) | 8 | AI | left (upper M19) | Fold SketchLens and DeclaredFile into guidance.py, `document_in` into the session | low |
| 25 | No use: `GuidanceCollection.at_stage` (guidance.py:244), `FidelityGuidance.default_output` (:1079), `Rule.attribute_to` (rule.py:106), `GuidanceAction.guidance_text` (guidance_actions.py:305) | 3 | AI | left (upper L2) | Delete them with their spec lines and `practice-guidance-model.md:51, :141, :204` | low |
| 26 | `AGENTS.md` "From the bottom up" lists agent_tools below markdown and guidance / guidance_actions below installation, hooks and mcp; the code runs annotations ← markdown ← agent_tools ← installation ← hooks ← mcp ← guidance ← guidance_actions | 11 | AI | new | Rewrite the order from the imports | low |
| 27 | `.context/repo-model.md:277` still names `instantiate_all` | 11 | AI | left (round-5 #35, partly) | Delete the line | low |

### Details

**1. The Clean Engineering companion (H3).** The round-5 fix made a practice of a set hold that set's Clean Engineering practice (`hold_set`, guidance.py:429-434), which removes the second practice for sessions. Two copies remain:
- `companion_practice` (:436-444) still makes a whole new Clean Engineering practice with `PracticeCatalogue.create` for any practice made outside a set.
- `FidelityGuidance.clean_engineering` (:1084-1098) answers `accompanying(self)` (:1098-1109), a new `FidelityGuidance` whose `outputs`, `judged_on`, `parent` and `session_output` are copied from the real one by hand.

That is a second fidelity object for one fidelity, so a field added to FidelityGuidance later is silently missing on the copy. Its only difference is the code format it works in, which a render request can carry (row 11).

**2, 9. Guidance named by strings.** A slug still makes a round trip:
1. `PracticeCatalogue.toolset_ref` turns the slug into a `module:Class` string.
2. `_NamedPractice` turns that string back into a key with `key_of`.
3. `self._session.practice(named.key)` finds the practice again.

The `session=` word is the same kind of thing: state written into the guidance string and parsed back.

**4. Two TypeScript type translators in one file.** `_hint_type` turns a typing hint into TypeScript (Union, list, dict, Literal, scalar, shape). `result_of` turns the return annotation into **text** (`str(annotation).replace("typing.", "")`), and `_text_type` parses that text with the same cases. So a field and a result of the same type are typed by two functions, which can disagree. AgentTool's copy is gone (round-5 #9 is fixed there).

**5. Guidance repeats AgentToolSetOrigin.** `@agent_toolset` joins a practice class with `AgentToolSet`, whose `AgentToolSetOrigin` already answers `slug` (`Name(domain_slug or class name).kebab`) and `install_folder` (the class's file's folder). `Guidance` defines both again, plus `_own_name` and a cached `class_folder`; only `FidelityGuidance.install_folder` (:1137) differs. Two definitions of a toolset's slug mean a change to one (for example the round-5 caching) reaches only half the toolsets.

**6. A second list of annotation kinds.** `annotation_kinds` (annotation.py:7-77) is "the one list of annotations". `RepositoryToolsets.ANNOTATIONS` is a hand-kept set of their snake-case names, which install uses to decide whether a class is a toolset without importing it. A new annotation kind must be added to both, or install will not find classes that use only that kind.

**15. Type-only file cycles.** No file in the area imports another in a cycle at run time; this was checked with every import, including those inside functions. The graph's two `guidance` cycles close through `TYPE_CHECKING` imports, but the dependency they show is real. The catalogue makes `PracticeGuidance` objects, and `PracticeGuidance.companion_practice` calls back into `PracticeCatalogue.create`, so each file needs the other to change. The `agent_tools.py` ↔ `recipe.py` cycle is only a type hint (`AgentInstructions` in a signature), so it is dismissed below.

**16. Edit events.** `hooks.py` holds the IDE event table, and `HookPayload` holds `edited_path`, `tool_name` and `hook_event_name`. `RulesCollection._just_edited` reads the raw payload fields and keeps its own list (`afterFileEdit`; `Write`, `StrReplace`, `EditNotebook`). A new IDE whose edit tool has another name needs a change in `harness/guidance`, not in `harness/hooks`.

## Graph hits: confirmed and dismissed

The report has 343 hits in 17 rules. The cross-file scanners found:
- `one-way-deps`: 6, all file cycles in this round's new scope (row 15 and the dismissed `recipe.py` pair).
- `deep-module`: 4 (rows 13, 19, 22).
- `eliminate-duplication` (copies across the graph): 0.
- `low-coupling`: 0.
- `missing-module-context`: 0.
- `domain-nouns-only` / `no-module-per-class`: 0.

The AI found every concern-1 and concern-2 row above, so the copies scanner still misses near copies under other names (rows 4, 5, 6).

Confirmed:
- `keep-classes-single-responsibility`: `PracticeGuidance` 32 public operations, `FidelityGuidance` 22, `GuidanceAction` 21, `Installer` 14, `PracticeCatalogue` 12, `Markdown` 11, `ToolsetMembers` 10, `AgentTool` 10. These are wide classes. `PracticeGuidance` mixes markdown reading, rendering, schema, session work and the companion; rows 1, 11 and 12 would each take a slice out of it.
- `keep-operations-small-focused`: `Installer._install_run` (29 lines), `_remove_skills_naming_missing_mcp` (23), `language_adapter._base_class` (38), `_view` (26), `markdown._locate_under` (29), `_blocks_under` (23), `schema._read` (25), `chat_pointer._event_text` (23).
- `simplify-control-flow`: `recipe._walk` 6 levels deep, `GuidanceAction.__init__` 4.
- `prefer-instance-operations`: confirmed for the two catalogues (row 3) and `ToolCall.session_in` (row 23). The annotation classmethods (`annotates`, `disabled_on`, `companion_flags`), the registration seams (`Installer.installs_through`, `ToolCall.open_sessions_with`, `ActionCatalogue.run_actions_with`, `PracticeCatalogue.register`), `Guidance.class_folder` / `class_key`, `IdeLayout.every` and `RepositoryToolsets.of_running_checkout` are the class-level seams AGENTS.md asks for, so they are dismissed.
- `limit-operation-parameters`: 18 hits. Real for `ToolCall.__init__` (5) and `FileInstallation.__init__` (5); the rest are 4-parameter constructors of value objects.

Dismissed:
- `errors-out-of-existence`:
  - `practice_class` raising `UnknownPractice` is a misspelt key, a real failure.
  - `Git._executable`: git missing is a real failure.
  - `new_report_path` and `_to_object_model` raise on bad input.
  - `at_stage` has no use (row 25).
- `never-swallow-exceptions` / `use-exceptions-properly`:
  - `RepositoryToolsets.classes` records each failure in `unloadable` with its cause, and the installer then stops on it.
  - `ToolsetMembers.of` catches `TypeError` only for a built-in type, as its comment says.
- `use-explicit-dependencies`: Installer makes `IdeLayout`, `InstallChannels` its installations, `FidelityActions` its `FidelityAction`s, `RulesCollection` its `AppliesTo`, and `TypeScriptOperation` its `Name`. Each is a part made once from the owner's own fields, or a value.
- `avoid-vague-parameter-names`: `item` in `GuidanceAction` (7 hits) is real. It is "a ref, a ref mapping, a practice or a fidelity", and would go with row 2. `value` on setters and in `data_of` is the setter's value, so it is dismissed.
- `use-typed-signatures` (the large group): `cls` on classmethods and `Any` on framework parameters that take any toolset or callable. Dismissed as in round 5.

## Scanner false positives

- **Several code-rule scanners still read spec files** (left from round 5; the round-5 scanner fix moved only some rules onto `ProductionCodeRule`). These classes derive from `PracticeGraphRule` rather than `ProductionCodeRule`, so specs are checked:
  - `OperationMeasureRule` (`cdd_guidance/practices/clean_engineering/model/rules_shared/operation_checks.py:128`), which `KeepOperationsSmall` (:152) and `SimplifyControlFlow` (:163) inherit.
  - `ProvideMeaningfulContext` (:200).
  - `PreferInstanceOperations` (:284).
  - `KeepOperationsSingleResponsibility` (`operation_semantics.py:33`).

  The resulting hits: `recipe_tools_spec._bare_tool_calls` (twice), `guidance_spec._read_together`, `agent_tools_spec.receive` / `pack`, and the number 2024 in `agent_tools_spec.__new__`.
- **The file-cycle reader counts imports under `if TYPE_CHECKING:` as imports** (`cdd_guidance/practices/clean_engineering/model/graph_reading.py:80-82` records `module.dependencies` with no check for type-only imports). So `agent_tools.py` ↔ `recipe.py` is reported as a cycle, although `recipe.py:21` imports `AgentInstructions` only for a signature. The guidance cycles are confirmed for a different reason (row 15). The rule should either report type-only cycles in their own words or drop them.
- `keep-classes-single-responsibility`, `keep-operations-single-responsibility`, `limit-operation-parameters`, `keep-operations-small-focused` and `avoid-vague-parameter-names` read the TypeScript **templates** under `harness/installation/templates/typescript/` (`CddConnection`, `start`, `request`, `messageIn`, `SourceViewGenerated`, `FileListViewGenerated`, `id`, `value`). These are copied into a project as the starting point of its adapter, not run here. Judged as code they are passable, so they were not counted.

## Goal-class counts

Rows of the table above by goal class and status. A row naming two goal concerns counts once in each.

| Goal class | Concerns | left | of which known skip | new | new scope | regression | Total |
|---|---|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 8 | 6 | 1 | 0 | 0 | 9 |
| Shadow models | 2 | 3 | 1 | 1 | 0 | 0 | 4 |
| Duplicated functions | 1, 12 | 1 | 0 | 2 | 0 | 0 | 3 |
| **Goal total** | | 12 | 7 | 4 | 0 | 0 | **16** |

How the 16 split between the two round-5 areas:
- **Round-5 harness-core scope** (rows 4, 5, 6, 7, 8, 14, 16, 18, 23) gives **9**, against **31** in `round5-harness-core.md` (11 + 3 + 17). That is a fall of 71%.
- **The guidance rows that came from round-5 harness upper** (rows 1, 2, 3, 9, 10, 11, 12) give **7**. Six of those 7 are skipped items still open.

## What would make the next round cheaper

- **Skipped reshaping is now most of what is left.** Seven of the 16 goal-class rows are listed in `pending-skipped-reshaping.md`:
  - `Format` as a string (row 11)
  - `work_at(str)` (row 12)
  - the `session=` word (row 9)
  - toolset attribute probes (row 7)
  - `module:Class` strings (row 8)
  - `DeclaredFile` per call (row 10)
  - `session_in` (row 23)

  By the trend file's rule ("a finding the fix agents skip twice goes into a decision record"), each needs either a named task with a failing spec, or a decision record that takes it out of the count. Fixing them again without a decision record will only cycle.
- **Fix agents remove the copy they were shown, not the pattern.** Round 5 named `_format_type` in AgentTool, and AgentTool's copy was deleted, but the same translator lives on twice inside `language_adapter.py` (row 4). The import-folder lists were merged, but a hand-kept annotation-name list stayed beside `annotation_kinds` (row 6). Before committing, a fix brief should grep for the duplicated **job** (in these cases: a Python type turned into TypeScript, a list of annotation names, slug from a class name), not only for the named function.

## Validate runs

- `clean-engineering-modules`, graph, the seven folders: report `clean-engineering-modules-20261108T081311_2.md` / `.json` (saved 08:15:55 UTC). The MCP reply was lost. The call answered "still running after 10 seconds", then the connection dropped (`ECONNREFUSED`). An identical call then failed with `MCP server "plugin:cdd:cdd" is not connected`.
- Following `.claude/rules/mcp-fail-loud.md`, I stopped there and ran validate no other way. The `clean-engineering-model` and `clean-engineering-code` runs were not made.
  - At 08:21 UTC the cdd server process (pid 10400, `~/.cdd/runtime`, 551 MB) was alive but did not answer on 127.0.0.1:47800 within 5 s.
  - Its log shows repeated `ClientDisconnect` and `WinError 64` accept failures while other agents' graph builds ran. This matches the lead's note that graph builds still block the server's other calls.
- As in round 5, the graph section covers the whole Clean Engineering practice whichever fidelity is named, so the modules report above already holds the code and model rules' graph hits for these folders (it lists `keep-operations-*`, `limit-operation-parameters`, `use-explicit-dependencies` and the rest).
