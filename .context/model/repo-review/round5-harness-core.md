# Round 5: harness core, concerns that span code files

Area: `harness/annotations`, `harness/process`, `harness/markdown`, `harness/agent_tools`, `harness/installation`, `harness/hooks`, `harness/mcp` (production code; specs, `_examples/`, and generated files only where noted). Read on branch `ensure-domain-orientation-refactor` at d71e0b20, 2026-11-07.

Checks used:
- **Graph**: `validate` with `graph: true` over the seven module folders. The `clean-engineering-modules` run returned 408 graph hits in 19 rules (report `clean-engineering-modules-20261108T013650.md` under `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\`). The graph report for a guidance covers the whole Clean Engineering practice, so the module, model and code rules are all in it. The `clean-engineering-code` run was still running when this file was written (see the end of this file).
- **AI**: I read each file side by side with the files it imports and the files that import it, and checked call sites with grep across `harness/`, `space/`, `tools/`, `cdd_guidance/` and `scripts/`.

Status:
- **new**: not in `repo-review/harness-core.md`.
- **left**: listed there and still true.
- **known skip**: listed in `.sessions/ensure-domain-orientation-refactor/pending-skipped-reshaping.md`.

Many items from round 4 are fixed and are not repeated here. Fixed: AgentToolSet keeps its tools; AgentTool keeps its ParameterSchema; RecipeSource is read once; HookServer reads `payload.session` and `session.chat_injections` instead of a fake ToolCall; HookInstallation keeps its interpreter, files and daemon; Hooks is an Annotation; `@hosted_only` replaced `HOSTED_ONLY_CLASS_NAMES`; UserMcpConfig was folded into IdeLayout; McpHost holds Claude's settings folder; CddHome keeps its Git and PythonInterpreter; HookDaemonAddress and RunningServer keep a StoppableProcess; InstallChannels makes each FileInstallation once; the FileManager-by-name lookup became `shares_file_views`; GuidanceAgentOperation calls a public `log_running`; `Agent` and `AgentGuidance` were deleted.

## Findings, most severe first

| # | Where | Concern | Found by | Status | Fix | Severity |
|---|---|---|---|---|---|---|
| 1 | `harness/hooks/hook_server.py:446` `HookServer.from_repository` | 9, 5 | AI | new | Ask the install for its folder (IdeLayout / HookInstallation.handlers_file) rather than `.cursor` | **high** |
| 2 | `harness/mcp/cdd_home.py:27` `IMPORT_FOLDERS`, `harness/installation/repository_toolsets.py:51` `_CATALOG_DIRS`, `harness/agent_tools/agent_tools.py:257` `ToolsetReference._SEARCH_FOLDERS` | 2, 1 | AI | new | One list on RepositoryToolsets; CddHome and ToolsetReference read it | **high** |
| 3 | `harness/hooks/hook_server.py:410` `HookIllegitimateHandler` and `harness/mcp/mcp_server.py:100` `_SkippedTool` | 2, 1 | AI | new | One "skipped toolset" class with one `skip`/`notice`/`notify_exceptions` | medium |
| 4 | `module:Class` spelled by hand, 7 places | 1, 11 | AI | new | Every caller reads `registration_name` | medium |
| 5 | "this checkout" computed from `Path(__file__).parents[2]`, 9 places in the area | 1, 5 | AI | new | One owner (RepositoryToolsets or CddHome) holds the checkout; others are handed it | medium |
| 6 | `harness/hooks/hook_daemon.py:291` `_claim_port` and `harness/mcp/mcp_daemon.py:142` `claim_port` | 1 | AI | new | One port claim in `harness/process` | medium |
| 7 | `harness/installation/installer.py:344` `_is_temporary` and `harness/mcp/mcp_server.py:154` `_is_temp_path` | 1 | AI | new | One `is_temporary` (Installation base or IdeLayout) | medium |
| 8 | `harness/mcp/cdd_home.py:179` `server_environment` and `harness/installation/repository_toolsets.py:76-87` `pythonpath` / `pycache_prefix` | 1 | AI | new | CddHome asks `RepositoryToolsets(source).pythonpath()` | medium |
| 9 | Python types turned into text three ways: `agent_tools.py:965-1002` `AgentTool._format_type*`, `parameter_schema.py:103-164` `ParameterSchema`, `language_adapter.py:610-626` `_text_type` | 1, 3 | AI | new | Delete `_format_type*` and `response`; have results go through ParameterSchema as arguments already do | medium |
| 10 | "Use MCP tool:" line written in one place and parsed in two | 1 | AI | new | AgentTool owns the line and its pattern; `files.py` and `installer.py` ask it | medium |
| 11 | postToolUse also serves afterFileEdit, decided twice: `hook_server.py:402-407` and `hooks.py:316-318` | 1, 7 | AI | new | One rule on `Hook` (events an annotation serves) | medium |
| 12 | `inject_rules` named in the framework: `agent_tools.py:657`, `hook_server.py:405` | 7, 5 | AI | new | The rule-injection annotation says which events it serves and whether it is rehosted | medium |
| 13 | `harness/markdown/front_matter.py:41` `FrontMatter.fields` and `harness/markdown/markdown.py:601` `YamlFields.pairs` | 1 | AI | new | One `key: value` reader | medium |
| 14 | `harness/agent_tools/agent_tools.py:108-126` `Collect._property` and `harness/markdown/markdown.py:852-868` `MarkdownProperty.reading` | 1 | AI | new | Collect builds its property through MarkdownProperty (or a shared property builder) | medium |
| 15 | `_TOOLSET_LOAD_FAILURES` twice with different members: `hook_server.py:32`, `mcp_server.py:48` | 1, 10 | AI | new | One tuple on the toolset loader (AgentToolSet/RepositoryToolsets) | low |
| 16 | No use: `AgentToolSet.instantiate_all` (agent_tools.py:513), `AgentTool.response` (:959), `ContextConfig.set_guidelines` / `set_practice_folders` / `guidelines` (context_config.py:64-82, spec only), `Format.is_known` used only by `templates_path_map` | 3 | AI + graph (instantiate_all as classmethod) | new | Delete them with their specs | medium |
| 17 | Rebuilt per call: `Installer.InstallChannels.toolsets` (installer.py:93) instantiates server toolsets on each read; `HookHandler` builds `ContextConfig(root)` per event (hook_server.py:330, :335); `Markdown.as_property` makes a new Markdown on every property read (markdown.py:834-841); `DataClass(type(...))` rebuilt per value (destination.py:203, :210) | 5 | AI | left (Markdown), new (others) | Hold the part once | medium |
| 18 | Toolset attribute probes: `files.py:166, :186, :206-212, :244-254, :277, :314-318`, `destination.py:257-259`, `agent_tools.py:939-943` (`overview`), `agent_tools.py:1068` (`session_context`), `hook_server.py:292` (`pattern`) | 5, 6 | AI | known skip | The toolset answers named properties | medium |
| 19 | `language_adapter.py:605` builds `ToolSubjectLoader(type(toolset))` | 5 | AI | known skip | Read `ToolsetMembers.of(type(toolset)).subject_loader` | low |
| 20 | Toolsets still travel as `module:Class` strings: `RepositoryToolsets.collect` (repository_toolsets.py:121) re-parsed by `classes`, catalog_generator.py:210, agent_tools_probe.py:76/86, prompt_notify.py:128; `McpServer.restarted` (mcp_server.py:445) | 5 | AI | left / known skip | Callers take `classes()`; strings only at the process boundary | medium |
| 21 | Annotation kinds outside `harness/annotations`: `LanguageAdapter`, `Identity`, `Edits`, `SourceFile` are bare classes in `installation/destination.py:40-111, :228`; `DataField`, `NoCatalog`, `NoDeploy` also live there | 2, 8 | AI | left | Make the four Annotations; move the annotation kinds next to `annotation.py` or keep only the installation in `destination.py` | medium |
| 22 | `harness/hooks/hook_daemon.py:37-44` `_SOURCE_STAMP_FILES` names `harness/guidance/rule.py` and `harness/guidance_actions/guidance_actions.py` | 7 | AI | new | Stamp the files of the hook toolsets the server loaded, not a fixed list naming higher modules | medium |
| 23 | Folder names of `cdd_guidance` inside the framework: `destination.py:273`, `files.py:268`, `installer.py:239, :251`, plus #2's lists | 7 | AI | new | The repository hands its guidance folders to the Installer through registration | low |
| 24 | `~/.cdd/server.json` read by TypeScript too: `installation/templates/typescript/cdd-connection.ts:76`, which also spells `CDD_HOME` and `~/.cdd` itself (:33) beside `CddHome` | 9, 12 | AI | new | The connect script prints the URL with the project header; the adapter reads only what it prints | medium |
| 25 | Intra-package import cycles hidden by deferred imports: `hook_daemon.py:22, :248` ↔ `hook_server.py:570`; `hooks.py:19, :328` ↔ `hook_server.py:24` | 7 | AI (graph misses, it measures packages) | new | Pass the HookServer class or factory into HookDaemon and HookInstallation, or move `main` and `from_repository` beside the daemon | medium |
| 26 | `harness/installation/context_config.py` lives in installation but installation never uses it; its readers are `hook_server.py` and `space/session/session.py` | 8 | AI | new | Move ContextConfig to the module that owns the project's `.context/` (session) and register its guideline reader with hooks | low |
| 27 | `harness/annotations/name.py` `Name` (case conversion) sits in the annotations package | 8, 10 | graph (deep-module) + AI | new | Its own small module or `markdown`; annotations keeps only annotation kinds | low |
| 28 | `harness/agent_tools/sub_agent/` is a one-class package (SubAgentAnnotation) | 8 | AI | new | Fold into `agent_tools.py` beside the other annotations | low |
| 29 | `harness/process/running_process.py` and `stoppable_process.py`, one class each | 8 | graph (deep-module 7/7) + AI | new | Fold into `process.py` | low |
| 30 | `harness/installation/bootstrap.py` `repo_root` / `ensure_import_path` free functions wrap `RepositoryToolsets.ensure_import_path` | 1, 11 | AI | new | Callers (`space/session/session_probe.py:32`, two scripts) use RepositoryToolsets | low |
| 31 | `harness/mcp/mcp_server.py:289-291` `_project_root` knows only `.cursor` and `.claude`; `_drop_cdd_entry` hard-codes `mcpServers` (:229) | 10, 1 | AI | new | Ask IdeLayout (`folder_name`, `mcp_servers_key`) | low |
| 32 | `harness/markdown/markdown.py:871-881` `markdown()` makes `Markdown.from_label(None, ...)`, a stand-in Markdown only to build a property | 5 | AI | new | A small property factory that holds the label | low |
| 33 | `ToolSetCollection.name/slug/registration_name` (agent_tools.py:78-89) repeat `AgentToolSetOrigin` (:425-450) | 1 | AI | new | ToolSetCollection derives from AgentToolSetOrigin | low |
| 34 | `ToolCall.session_in` (tool_call.py:97) is a class-level lookup for a project with no call, used only by `harness/diagnostics/probe_arguments.py:64` | 5 | graph (classmethod) + AI | known skip (ProbeArguments) | SessionOpener answers "the session open in this project" | low |
| 35 | `.context/hooks-runtime-model.md`, `agent-tools-model.md` and the cards name no deleted class; `harness/guidance/.context/practice-guidance-sketch.md:113` still names `AgentToolSet.instantiate_all` (another area) | 11 | AI | new | Delete `instantiate_all` and that sketch line together | low |

### Details

**1. Hook server reads `.cursor` whatever the IDE.** `HookInstallation` writes `hook-handlers.json` into the install folder (`hooks.py:228`, `self.path`), which is `.github` for VS Code and `.kilo` for Kilo; both run hooks (`IdeLayout.runs_hooks` is false only for Claude). `HookServer.from_repository` reads `toolsets.root / ".cursor" / HookHandlersFile.NAME`. For those IDEs the server finds no file and falls back to every toolset in the repository, so hooks the install left out (for example `@Hooks(deploy=False)`) run anyway. `HookDaemon.state_path` hard-codes `.cursor` too (`hook_daemon.py:162`), so a VS Code-only checkout gets a `.cursor` folder. This is wrong behaviour, so high.

**2. Three registries of the import folders.** `IMPORT_FOLDERS` (cdd_home.py:27), `_CATALOG_DIRS` (repository_toolsets.py:51) and `_SEARCH_FOLDERS` (agent_tools.py:257) list the same folders. `_SEARCH_FOLDERS` already differs: it has `harness` and lacks `cdd_guidance/patterns`. So a toolset under `patterns/` in a hyphenated folder is found by the installer and not by `ToolsetReference`. Adding a folder means three edits, and missing one breaks only one of the server, the installer or the reference loader.

**3, 4, 5. Copies of one job.**
- 3: HookServer and McpServer/McpHost each have a skipped-failure class with `tool`, `reason` and `cause`, plus `skip`, `notice` and `notify_exceptions`. The code is word for word, with "hook" and "MCP" swapped.
- 4: `f"{cls.__module__}:{cls.__name__}"` is written by hand at `agent_tools.py:89`, `:450`, `hook_server.py:378`, `files.py:231`, `mcp_server.py:448`, and outside the area at `guidance.py:94` and `action_catalogue.py:54`.
- 5: `Path(__file__).resolve().parents[2]` appears at `agent_tools.py:291`, `hook_server.py:13`, `:572`, `bootstrap.py:11`, `files.py:267`, `mcp_server.py:337`, `:350`, `server_hooks.py:17`, `spec_support.py:16`.

**9. Three type translators.** `AgentTool.parameters` and `.response` exist only to feed `_format_type`, `_format_type_from_string`, `_format_list_type` and `_format_builtin_type`. The only production reader is `RecipePlaceholders(arguments, set(self.parameters), ...)` (`agent_tools.py:1089`), which needs the names alone. `response` has no reader. Meanwhile the TypeScript adapter types arguments from ParameterSchema's JSON Schema but types results by parsing the annotation as text (`_TypeText`). So a result type and an argument type of the same class can come out differently.

**10. The invoke line.** `AgentTool.invoke_line` writes `Use MCP tool: \`name(...)\``. `FileInstallation._without_mcp_invoke` (files.py:286-298) and `Installer._SKILL_MCP_NAME` (installer.py:111) parse it back with their own text. `_fidelity_invoke_parts` (files.py:250) writes a fourth variant by hand.

**13, 14.** Two readers of `key: value` settings in one package: `FrontMatter.fields` for file headers, and `YamlFields.pairs` as the fallback when PyYAML is missing. Each quotes and comments differently. Two property builders copy `__doc__`, `__name__`, `__annotations__` and `copy_annotations` the same way.

**22, 23, 25. Direction.**
- At package level the area is one-way: annotations ← markdown ← agent_tools ← installation ← hooks ← mcp. `harness/` imports nothing from `space/`, `tools/` or `cdd_guidance/`.
- The framework still knows higher layers by file path and folder name (22, 23).
- Two cycles inside `harness/hooks` are kept alive by imports placed inside functions or under `TYPE_CHECKING` (25).

**24. Python and TypeScript.** No domain rule is decided in the TypeScript templates. `readArguments` in `cdd-shared.ts` checks types against the published schema, which is transport checking. The overlap is in where the server is found: `cdd-connection.ts` resolves `CDD_HOME` and reads `server.json` itself. `CddHome` and `McpDaemon.publish` own that file.

## Graph hits: confirmed and dismissed

Confirmed (each folded into the findings above, or real and minor):
- `deep-module` annotations 6/8 and process 7/7: real in shape (#27, #29). Annotations is a vocabulary package that every module imports by design, so its share being high is expected. The real finding is that `Name` does not belong there.
- `keep-classes-single-responsibility`: `Installer` 14 public operations, `McpInstallation` 14, `McpDaemon` 13, `Markdown` 12, `McpServer` 12, `McpHost` 12. Confirmed as wide classes. McpInstallation mixes the manifest writer with Claude settings editing (`allow_cdd_tools`, `drop_*_cdd_server`), which would be a class of its own.
- `keep-operations-small-focused`: `Installer._install_run` (29 lines), `language_adapter._base_class` (38), `_locate_under` (29). Confirmed.
- `simplify-control-flow`: `recipe.py` `_walk`, 6 levels deep. Confirmed.
- `never-swallow-exceptions` / `use-exceptions-properly`: `hook_server._invoke_enabled`, `repository_toolsets.classes`, `mcp_server._answer_chat` and `tool_calls._start` catch `Exception`. Each records the failure (skip list, `unloadable`, error result) with a written reason. Confirmed as the rule's letter. The handling is deliberate, and each one records the failure rather than dropping it.
- `prefer-instance-operations`: `instantiate_all` (no use, #16), `ToolCall.session_in` (#34), `Hooks._on` / `disabled_on` / `deploys`, `Installer.installs_through`, `HookServer.show_toasts_with`. The last two are the registration seams AGENTS.md asks for. Confirmed only for the first two.
- `use-explicit-dependencies`: confirmed for `Installer` → `IdeLayout`, `McpInstallation` → `McpDaemon`, `CddServerHooks` → `McpDaemon`, `ClaudePlugins` → `IdeLayout`, `HookDaemon` → `RepositoryToolsets`. They are parts made once and kept, which the guardrails allow, but #1 shows the cost of each owner making its own layout.

Dismissed: see the list below.

## Scanner false positives

- `cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py:29-31` (`OneWayDeps`): it builds each module's imports from `dependsOn` edges without dropping spec files or `_examples/` folders. All 14 cycle hits come from these:
  - `agent_tools_spec.py:34-35` imports hooks and mcp;
  - `installation/_examples/note.py:13` imports `harness.mcp`;
  - `mcp/_examples/*` are read as modules named `_examples`, `super_delegation`, `illegitimate_name` and `parameter_types`.

  No production import closes a cycle between these packages. DeepModule (the same file, `:86`) filters `is_test_code`; OneWayDeps should do the same and should skip `_examples`.
- The same reading counts `_spec.py` and `_examples` files for the code rules. Examples: `restart_gate_spec._hold`, `hook_spec._dispatch_work_session_inject`, `recipe_tools_spec._bare_tool_calls`, `agent_tools_spec.receive/pack`, `parameter_types.echo` (22 parameters on purpose), `ParameterTypes` data bag, `TwoWorktrees`. The brief excludes those files.
- `OneWayDeps` measures packages only. So it misses the real cycles inside `harness/hooks` (#25), which are held together by imports placed inside functions.
- The TypeScript reader (`cdd-connection.ts`):
  - reports a class called `names`, which does not exist in that file;
  - reports `start`, `request` and `messageIn` twice each, so the file is read twice.
- `use-typed-signatures` (165 hits): `cls` "missing a type annotation" on `__new__` / classmethods is Python convention. `Any` on framework parameters that genuinely take any toolset or callable (`member`, `target`, `annotation`, `owner`) has no narrower domain type. Dismissed as a group.
- `use-explicit-dependencies` flags constructing value objects (`Path`, `PurePosixPath`, `ValueError`, `ToolCallStopped`, `StoppableProcess` from a pid). A value made from the object's own fields is not a collaborator. Dismissed.
- `errors-out-of-existence` on `Hook.__new__` (an unknown IDE event is a real authoring error), `_Wire._received` (a closed socket) and `Git._executable` (git missing). These are real failures, not ordinary empty cases. Dismissed.
- `avoid-vague-parameter-names` on `fn`, `value`, `item` in generic framework code: mostly dismissed. `HandlerCatalog.ref_label(item)` and `McpServer._loaded(item)` are real: the item is "a toolset reference, class or instance", and a named type would remove the guessing (#20).

## Validate runs

- `clean-engineering-modules`, graph: report `clean-engineering-modules-20261108T013650.md` / `.json`. MCP dropped the connection twice before the run completed; the third identical call collected it.
- `clean-engineering-code`, graph: started with identical arguments. It answered "still running" six times, and then the call failed with `ECONNREFUSED: Unable to connect`: the cdd server at 127.0.0.1:47800 stopped answering, and its log showed repeated `ClientDisconnect` errors from parallel clients. Following the MCP fail-loud rule, I did not rerun it another way. The code report has to be collected once the cdd server is up again. Its graph section runs the same practice-wide rule set as the modules run.
- `clean-engineering-model`: not run separately for the same reason. The graph report already includes the model rules.

## Graph check (run after the round)

The `clean-engineering-code` and `clean-engineering-model` runs on the seven folders were not made in this pass. The CDD MCP host dropped (`ECONNREFUSED`, then `not connected`, with three retries) on the call made just before them, for the stories, UX and DDD area.

They would most likely add nothing. The graph section covers the whole Clean Engineering practice whichever fidelity is named: the space-tools modules and model runs returned the same 285 hits rule for rule, and the earlier `clean-engineering-model-20261108T015854.md` and `clean-engineering-code-20261108T015456.md` runs returned 637 each. The `clean-engineering-modules-20261108T013650.md` hits judged above therefore already cover this area's graph rules.
