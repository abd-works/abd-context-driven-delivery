# Clean Engineering validation after the domain-orientation refactor

Branch `ensure-domain-orientation-refactor`, validated at `d6c41b23`; module cards fixed in `784b4f31` and `fd5266a7`. The full suite passes (2703 examples).

Validate ran through the CDD MCP host at the modules, model, and code fidelities across `harness/`, `space/`, `tools/`, and `cdd_guidance/`. For each call, an AI judge reviewed every rule and appended its judgment to the saved report. A separate cross-file pass looked for problems that show only across files, using the mistakes the corrections logs record. The 116 reports are in `validation-reports/` beside this file: 63 from the first round, and 53 from the second round, which covered the six practice folders (§12) and the rewritten module cards.

**The short answer:** the refactor did what it set out to do. The six dicts on Ticket are gone, actions read their call's session, practices answer their own roots and files, and the board and stage do their own work. The repository still has more open issues than hoped for, and they cluster in a few places:
- the MCP host itself
- a handful of second object models
- global "current" objects
- two very large classes, Session and Repo
- one big dependency cycle

Several findings are real bugs and should be fixed first.

Severity: **high** means wrong behaviour or a second object model, **medium** means a rule plainly broken, and **low** means naming or documentation.

## Progress (2026-11-07, 03:30)

✅ done · ◐ in progress. Commits b642e9f2 … bfcc3fb0 on this branch.

- **Bugs:** all 34 fixed, each with a spec.
- **§2 second object models:** done — one Violation, one graph node model, one registry of practices and of actions, stages defined once, ProjectTicket deleted, kanban sends objects (Workspace, slug dicts and name copies gone), CE members kept once, DDD stereotypes as data.
- **§3 globals:** done — every call carries its own project and session (ToolCall); Graph/Board/FileManager/Session current are gone. Remaining: `working_on` and `ChatPointer.serving` move onto ToolCall (in progress).
- **§5:** Session and Repo split into objects with one job each.
- **§6 cycles:** no two harness modules import each other; the remaining cross-folder cycles are in progress.
- **Still to do:** catalog regeneration and reinstall, then a full re-validation and a fix pass on what it finds.
- **Decisions** are logged at the end of this file.

---

## 1. Bugs: wrong behaviour today

| # | Where | What goes wrong | Sev |
|---|---|---|---|
| ✅ B1 | `harness/mcp/mcp_server.py:703` | The 10-second timeout around `to_thread.run_sync` cannot stop the thread. The tool runs to the end and writes its files, but the caller is told `TimeoutError`. Callers then retry work that already finished. That pile-up dropped the host twice during this validation. | high |
| ✅ B2 | MCP host accept loop (`~/.cdd/server.log`) | After `OSError: [WinError 64]` the asyncio accept loop dies. The port stays open, every connection is refused, and the host never recovers on its own. | high |
| ✅ B3 | `cdd_guidance/actions/validate/validate.py:55` | `_unchecked_files` is per-call state kept on the shared action object; all other per-call state is thread-local. Concurrent validates overwrite each other's filter and drop the wrong hits from a report. | high |
| ✅ B4 | `space/session/session.py:938`, `harness/hooks/session_logs.py`, `hook_server.py:642/733/817` | The current session is saved twice: in `.sessions/session.json` through WorkState and in `.sessions/_active` through SessionLogs. The hooks read only `_active`, which a switch to main does not update and a close never clears. So after either, hooks keep logging into the old session. | high |
| ✅ B5 | `stories.py:44`, `ux.py:40`, `generate.py:10` and 9 more | Modules are imported under two names (`validate.validate` and `cdd_guidance.actions.validate.validate`). Python loads such a file twice, so classes, `isinstance` checks, and class-level state split into two copies. | high |
| ✅ B6 | `space/context_config.py:35` | A malformed `config.json` loads as `{}`, and the next `update` saves that over the file, erasing the project's guidelines and practice folders. | high |
| ✅ B7 | `harness/agent_tools/agent_tools.py:1796` (and 1830, 1911, 1968, 1984) | `except Exception` hides failures while a recipe line in `@agent_instructions` is evaluated. An `if` silently takes its `else`, or a return's source text goes to the agent as instructions. `tools/granola/granola.py:116` relies on this: it calls `format_filing_plan()` without its required argument. | high |
| ✅ B8 | `space/repo/repo.py:471` `CliAgentBinding.write_tag` | Sets `repo._annotated_tag_target` for one call and never restores it, so every later `write_annotated_tag` on that Repo tags the last branch instead of HEAD. | high |
| ✅ B9 | `cdd_guidance/practices/clean_engineering/clean_engineering.py:71` | `generate_output` calls `self.drawio.render()`, but `drawio` defaults to None and no caller passes it, so it raises AttributeError. | high |
| ✅ B10 | `harness/chat-ui/pane/hooks/chat-bar/session-client.ts:25, :49`, `chat-bar-client.ts:98`, `fidelity-client.ts:145` | The chat bar calls `board.activate` and `board.workspace`, which are now `ticket.activate` and `ticket.workspace`. It reads `column.fidelities[slug]`, which Stage never sends, so every fidelity name is empty. It builds `/actions-*` commands without `session=`, so validate and render act on the chat's session. The test stub still answers `board.activate`, so its tests pass. | high |
| ✅ B11 | `space/session/session.py:655, :710, :715`, `harness/guidance_actions/guidance_actions.py:394`, `session.py:376/384` vs `:429` | "The folder the session works in" is worked out four ways, each with a different last fallback. One session can get two roots: practice folders use one, and sketches and grill answers the other. Declared outputs and the file manager disagree for pattern practices. | high |
| ✅ B12 | `cdd_guidance/actions/partition/partition.py:162` | `on` ignores the item and drops `out_root` and `paths`. The index and segments are written under the session root while the reply names `out_root`. | medium |
| ✅ B13 | `tools/prompt_log/prompt_log.py:34` | It logs into the CDD checkout, not the project, and its docstring names `.context/sessions/`. | medium |
| ✅ B14 | `harness/hooks/hook_daemon.py:172` vs `harness/mcp/mcp_daemon.py:150` | Two copies of `_end_process` have drifted. The hook copy has no guard against pid 0 or its own pid. | medium |
| ✅ B15 | `cdd_guidance/practices/ddd/model/vocabulary.py:18` | Importing it sets the process-wide `socket.setdefaulttimeout(2)` and downloads NLTK data inside the shared MCP host. | medium |
| ✅ B16 | `harness/graph/rules.py:39` | `attach_rules` records each violation, then `apply_rules` records it again. Only a de-duplication check hides the double count. | medium |
| ✅ B17 | Swallowed failures: `installation/files.py:163`, `markdown.py:984`, `stories/model/json/nodes.py:136`, `agent_bdd_common.py:540`, `catalog_generator.py:1253`, `repo.py:2286/:2218` | A wrong slash command is installed, a corrupt story graph reads as an absent one, catalog pages silently go missing, a failed fetch returns as though it worked. | medium |
| ✅ B18 | `agent_cli_bdd.py:329` | The `timeout_seconds` argument is silently discarded. | medium |
| ✅ B19 | `agent_bdd/agent_bdd_common.py:290, :322, :332`, `agent_cli_bdd.py:456` | Imports `cli_agent.cli_agent.CursorCli`, which exists nowhere, live or retired. Every agent spec outside chat fails with ModuleNotFoundError at its first `instruct`. | high |
| ✅ B20 | `bdd/spec_helpers.py:11` | Imports `clean_engineering.specifications...._scan_base`; that folder is gone. `expect_scan_fails` / `expect_scan_passes` are on the BDD card's seam and `templates/bdd.py` tells agents to use them. | high |
| ✅ B21 | `bdd/model/sketch/sketch_bdd_model.py:22` | Imports the removed `_render_sketch` from `bdd_model`, so rendering BDD to sketch raises ImportError. No spec covers it. | high |
| ✅ B22 | `clean_engineering/model/sketch/sketch_class_model.py:33` | `clean_engineering.py:54` lists sketch as a format, but neither the sketch model nor its base has `render`, so rendering a CE model to sketch raises AttributeError. | high |
| ✅ B23 | `bdd/model/code_spec_model.py:191` | A `SyntaxError` in the existing spec file reads as an empty model, so a re-render replaces every hand-written test body with scaffold comments, with no warning. | high |
| ✅ B24 | Format adapters in Stories, DDD, UX | **Round trips lose data.** Stories sketch writes each sub-epic's stories twice (`sketch_story_model.py:167`); JSON drops every scenario and background step (`json/nodes.py:179`); `story_type` is lost through miro, markdown and sketch; a top-level epic's own stories are never drawn (`drawio/nodes.py:253`). DDD `DrawIOBoundedContextMap` inherits the markdown `parse`, so a draw.io map parses to 0 contexts (`drawio_bounded_context_map.py:64`). UX markdown `parse` cannot read what `render` writes (`markdown/nodes.py:15`); HTML `parse` returns an empty map. No adapter has a round-trip spec. | high |
| ✅ B25 | Stories `drawio/nodes.py:406`, DDD drawio render, `ddd/model/clean_engineering_bridge.py:34` | Draw.io writes markdown, parses it back, then draws, so the drawing gets whatever markdown loses: every story comes back `USER`. The DDD bridge writes stereotypes into the intent as `<<…>>` text and parses them back with a regex. | high |
| ✅ B26 | `ux/model/nodes.py:181`, `collections.py:22`, `ux_node.py:40` | Regions, controls, interactions and transitions are built with `graph=None`, so each gets its own `Graph()`; `region.graph is map.graph` is False and graph rules never see them. | high |
| ✅ B27 | `ux/rules/screen_rules.py:14` | `ScreenStoryBudget` counts a `stories` edge that screens never record (they keep `story_names` strings), so the rule can never fire. | high |
| ✅ B28 | `stories/model/story_model.py:621`, `:918` | The copy constructor and `clone()` disagree: epic-level and map-level examples are dropped. In drawio and miro, `clone()` returns an XML or SVG string, not a node. | high |
| ✅ B29 | Stories typescript/python/java/javascript `nodes.py`, `story_model.py:1012` | Four different name-cleanup rules, and scenarios merge by name, so stories are dropped silently. | high |
| ✅ B30 | `clean_engineering/model/rules_shared/operation_checks.py:41` | `_STATIC_FACTORY_EXTRA_NAMES` exempts `current`, so `Session.current`, `Graph.current` and `Board.current` pass the rule meant to catch them (§3). | high |
| ✅ B31 | `stories/stories.py:69` | `read_paths` names node paths from `Path.cwd()`, the MCP host's folder, not the session root. | medium |
| ✅ B32 | `ux/model/drawio/nodes.py:45` | The `node` subprocess has no timeout; a hang blocks an MCP thread that B1 cannot stop. | medium |
| ✅ B33 | `agent_bdd/conf.py:71` via `agent_bdd.py:5` | Importing the practice loads `.secrets` into the MCP host's environment and edits its import path. | medium |
| ✅ B34 | `harness/catalog_generator/catalog_generator.py:1176` | `catalog.generate_catalog` writes to `_REPO_ROOT/cdd_guidance/catalog`, the checkout the MCP host runs from (the pinned `~/.cdd/runtime`), never the project's. A project or branch cannot regenerate its own catalog through MCP. | medium |

## 2. Second object models (`do-not-invent-parallel-object-models`)

- **One rule hit, five shapes (high):**
  - the 10-key dict in `validate/graph_json_reader.py:191`
  - `RuleHit` in `graph/explorer.py:39`
  - kanban's `Violation` in `report.py:44`, whose `identity` turns clean-engineering into `clean`
  - `[slug, node_id, message]` lists in `graph/rules.py`
  - `DrawioViolation` in `drawio/scanners/_drawio_base.py:20`

  Keep one Violation class owned by the graph's rules (A-F14).
- **Practice and action registries (high):**
  - Practices are registered again beside `PracticeCatalogue` by `GuidanceCatalog` (`guidance_actions.py:491`, which swallows import errors and registers each fidelity under up to four names), the catalog generator's registry (`catalog_generator.py:165/178`), `UTILITY_REGISTRY`, and the catalogue that `tools/prompt_notify` scrapes from installed skills (TL-1).
  - Actions are listed by hand six times: chat-ui `BUILDER_ACTIONS`, board `TILE_ACTIONS`, `STAGE_ACTIONS`, `_KNOWN_ACTIONS`, `_FALLBACK_ACTIONS`, `LIFECYCLE_ACTIONS`.
  - Practices are listed again in TypeScript in `PRACTICES` and `PRACTICE_COLOURS`.
- **The graph's own node (high):**
  - `graph.py:650` still builds its own `Node` with a facts dict beside the parsed object (1.4 Mode B).
  - The explorer's `*Entry` family re-exposes Node fields.
  - `practice_rules_registry.py:34` keys the rules by practice name.
- **Kanban copies (high):**
  - `Workspace` (`board.py:473`), the bag of answers the rule names as its example.
  - String copies: `active_name`, `column_name`, `next_slug`, `fidelity_slug`, `FidelityProgress.ticket: str` (K-F21).
  - Dicts keyed by slug: `Stage.formats`, `default_formats`, `work_required_slugs`, `Ticket.progress_by_fidelity`. Because of them, TicketClient (34 members) looks everything up by slug.
  - `Help` and `HelpRule` copy the guidance (K-F20).
  - The hand-written TypeScript `TicketFiles` type keeps the deleted helper's name.
- **Stage modelled twice (medium):** `Stage` and `StageColumn` (`foundry_chrome.py:68`), and the stage order and scope text are copied into `board-brand.ts` and `chat-bar-client.ts`.
- **ProjectTicket (high):** `space/repo` still has a second ticket model (`ProjectTicket`, `Project`, `ProjectTicketState`, `Repo._tickets`) beside kanban's Ticket, and nothing in production calls it (K-F13).
- **PracticeGuidance holds its session three ways (high):** `session` (a name), `workspace` (the Session), and `session_output` (`guidance.py:345, :213, :683, :701`). The practice key is also computed three ways (`key`, `context_index_key`, `context_config.py:75`).
- **Smaller copies (medium):**
  - `OoadClass` keeps its members twice, `properties` and `property_nodes`, synced by `sync_*_legacy`.
  - `FileEntry` sits beside `FolderEntry` (K-F17).
  - The chat bar's `FidelityJson` and its invented `validated` state.
  - `SketchLens` copies `sketch_titles`.
  - `SegmentCompletenessConfig` is held in three places.
  - The hook handlers take a raw `dict` instead of `HookPayload`.

## 3. State passed as parameters, and global "current" objects (`hold-state-on-the-object-not-in-parameters`)

- **Global current objects (high), about 12 entry points:**
  - `Session.current` and `_current_by_project`.
  - `Session.switch`, `mark_loop`, `read_loop`, and `append_log`, which are classmethods acting on that current session.
  - `Graph.current`, `Board.current`, `FileManager.current`, and the shared `PracticeCatalogue._shared`.
  - The MCP host sets `working_on(project)` around every call and refreshes the current session.
  - `handoff.py:40`, `record_decisions.py:39`, and `file_manager.py:147` fall back to `Session.current()`, so a call made for a ticket's session can still write into the chat's open session. This is what is left of bug 10.
- **Actions are not made for their session (high, P-1, P-15):**
  - Every action operation still takes a `guidance` slug or dict and parses `session=` and `format=` out of its text.
  - One `GuidanceAction` serves every call, with per-call state in thread-locals.
  - Inner actions are made with `_inside(X, worked_on)` and handed `worked_on` again.
- **P-2, P-3, P-4 (high, need a decision):**
  - `Ticket.generate_commands(fidelities, formats)` and `FidelityCommands._in_session` write `session=` into command text.
  - TypeScript `actionCommand` and `tile-actions-client.ts:110-118` build the commands again; its render command already differs from Python's (no `source=`).
  - `tile-formats.ts:17` chooses the format.
- **Other parameters (medium):**
  - `PracticeSessionOutput.output_paths_of`, `files_of`, and `has_output_of` take a fidelity. A fidelity's session state has no object of its own.
  - `Session.current(repo_path)` is still on MCP.
  - Chat strings are passed although `ChatPointer` exists (P-24).
  - `repo` is passed to Installer and HookDaemon methods that hold it.
  - `Repo.git(root)` takes a root; branches are passed as name strings beside Branch objects.
  - `render(format)` takes the format on every call.
  - Each action overwrites the shared practice's guideline (P-21).
- **Free functions that take their owner first (medium):**
  - I-F16: `data_fields_of`, `omitted_from_catalog`, `omitted_from_deploy`.
  - P-19: `refresh_stale_limit_operation_parameter_messages`, a 58-line shim that re-parses source.
  - `working_copy.py` has 71 free functions and `schema_rules.py` 27.
  - The drawio and DDD helpers: `drawio_bounded_context_map` 35, `operation_metrics` 28, `tier_facts` 20, `stereotypes` 17.

## 4. Duplicated behaviour (`eliminate-duplication`)

- Session root rules (B11). `session.json` is spelled out in 8 places beside `Session.session_file`, and the `session.log` fallback is written out by hand.
- Fidelity log lines are written in three places in two modules. Two name the practice by class and one by key.
- Process liveness is checked a third time (`repo.py:445`) beside `RunningProcess`. `_end_process` exists twice (B14), and so does `ensure_import_path`.
- The two transcript lookups (`chat_pointer.py:192` and `tools/chat/chat.py:303`) read different environment variables.
- Slug helpers: `name_of`, `_camel`, `_slug`, and `_words` copy `Name` in `session.py:68`, `drawio_class_model.py:706`, `story_test.py:48`, `links.py:45`, and `spec_file.py:162`. The suffix tables copy `Format.from_extension`.
- Validate assembles "shared plus current-fidelity rules" three times (A-F1) and re-parses rule bodies (A-F2).
- `instruct_run` and the agent BDD runners are copied between `agent_chat_bdd.py` and `agent_cli_bdd.py`.
- The forge page link is built in `board.py:448` and `catalog_generator.py:111`.
- `for_session` and `_session_or_current` are identical in handoff and record_decisions.
- The process runners (`repo.py:926/1000`) and trailer parsing (K-F12) are duplicated.

## 5. Classes with too many jobs (`keep-classes-single-responsibility`, 1.11)

| Class | Size | Jobs mixed |
|---|---|---|
| Session `session.py:477` | 97 methods, 44 public operations | current-session registry, folder lifecycle, log and loop parsing, chat pointers, practices.json, file listing, agent prose |
| Repo `repo.py:853` | 111 methods, 65 public operations | git, GitHub issues and projects, notes, tags, session registry, MCP tools, an in-memory test double in every operation |
| Installer `installer.py:30` | 82 methods, 23 public | — |
| FidelityProgress `ticket.py:593` | 36 members | works out which report answers which rule, which is the fidelity's job (P-22) |
| TicketClient (TS) | 34 public members | lookups by slug (see §2) |
| Ticket `ticket.py:60` | 14 operations, 19 properties (down from 73 members) | — |
| PromptNotify `prompt_notify.py:69` | — | catalogue, toasts, a sqlite read of Cursor's database, echo detection, extension install |
| Graph, AgentInstructions | 47 and 71 methods | — |

## 6. Module structure (modules fidelity)

- **Dependency cycles (high).** Following every import, 25 modules form one strongly connected group. The harness framework modules import each other, harness and `space/session` import each other, `harness/graph` imports every practice and pattern while they import it back, clean_engineering and ddd import each other, so do stories and ux, and `space/repo` and `space/session` import each other. Every import that causes a cycle is listed by module in `.sessions/_backlog/break-module-dependency-cycles.md`.
- **deep-module, over 40% public (medium):** markdown (60%), hooks (43–50%), installation (42%), catalog_generator (48%), space/repo (47%), context_setup (about 78%), tools/chat, tools/file_manager, the space root.
- **One class per module (medium):** harness/health, space/handoff, space/record_decisions, and harness/guidance_actions, which is effectively `GuidanceAction` and imports guidance while guidance imports it back. `harness/output_folder.py` is one class at the harness root, used only by specs.
- **Board placement:** `harness/kanban` imports space, tools, and the practices. Its card now says it is an application at the top of the stack; whether it belongs there or in space is open.
- **Fixed in `784b4f31`:**
  - The 25 module cards that cited removed APIs are rewritten to the current code.
  - Cards for modules that no longer exist are deleted.
  - These modules now have cards: `harness/graph`, `design_canvas`, `guidance`, `guidance_actions`, `space`, `space/session`, `tools/chat`, `echo`, `file_manager`, `granola`.
  - The root card is `.context/module-context.md`.
  - The modules fidelity gained `seam-names-current-code`.

## 7. Legacy names and dead code (`no-legacy-api-after-refactor`)

- **Aliases:**
  - Decorators with two names: `mcp = Mcp`, `skill = Skill`, `hook = Hook` (about 160 vs 37 uses).
  - `echo = Echo`.
  - `instruct_run` "back-compat alias" (6 callers), `RunResponse.stdout`, OoadClass `classes` and `sync_*_legacy`.
  - `LEGACY_ACTIVE`, `LEGACY_LOG_PATHS`, `LEGACY_SESSIONS_FOLDER`, `_FORMER_VERBS`.
- **Old builder:** `CreateContextTool` is the old `CreatePracticeGuidance`, still deployed. Its markdown and the installed builder skills describe `BaseContextTool`, `practices/base/`, `utilities/...`, and `@instruction` slots, none of which exist.
- **Dead code:**
  - `Ticket._folder`, `Board.practice`, `find_mistakes`, `workflow_commit_message`, `cursor_path`, `ticket_rows`, `write_text_field`.
  - `format_violation_message`, which returns its argument unchanged.
  - Dead parameters: `expand(context)`, `ensure_mcp_server(payload)`, `iterate(tools)`.
  - Commented-out retired code.
  - `verify_fix` is a stub.
  - `verify_report_links` has only a spec caller.

## 8. Documents and prose (secondary)

- **Model documents out of date with the code:**
  - `kanban-model.md` and `.drawio` still show the Ticket copies, `PracticeRoot`, `TicketFiles`, and `Board.activate`, and the two disagree.
  - `graph-populate-model.md` models a CodeQL design that does not exist.
  - `bdd-model.md` names classes that do not exist.
  - Also out of date: `practice-guidance-model.md`, `agent-tools-model.md`, `hooks-runtime-model.md` (which holds an old `# harness/hooks` card), and `prompt-notify-model.md`.
  - About 60 channel subtypes in the DDD, Stories, and UX models do not exist.
  - Model documents redeclare classes other modules own: kanban-model about 14, prompt-notify-model 4.
- **Prose naming fidelities that do not exist:** `stories-scaffold` (`actions/sketch/agents/sketcher.md:20`, `agents/discovery.md:22`) and `bdd-modules` (`agents/discovery.md:26`).
- **`clean_engineering.md:330`:** `session=` still holds, but the format is no longer read back from session.log.
- **`harness/chat-ui/.context/story-map.md:10/:64`:** still names `board.activate`.

## 9. Names and wording

- **Banned words in names:**
  - `_slot`, `_bind_new`, `CliAgentBinding`, `bind_repo`, `MarkdownSlot`, `YamlBinder`, `ApproachExampleSlot`, `bind_rule`, `rule_rows`.
  - `mark_iterate_tick`, a published MCP operation.
  - A `hosts` local and `FidelityGuidance.host`.
  - In prose: "prove-read", "kit", "hydrates".
- **Name clash:** two classes are named `Echo`, the toolset and the `@echo` mark.
- **Other wording:** "release" is a third name for the session folder (`work_state.py:117`), and some numbers are unnamed (`repo.py:2210`, `granola.py:175`, `validate.py:282`).

## 10. Problems with validation itself

- **Host load:** the host fails under concurrent calls (B1, B2), and one whole-`cdd_guidance` call is too big for its 10-second limit. Run validate one module folder per call, one call at a time, until B1 and B2 are fixed.
- **Shared graph file:** every call overwrites the session's one `edited-graph.json`, so concurrent callers read each other's graph. Name it per call, or beside the report.
- **Old guidance:** the host runs the pinned runtime at `~/.cdd/runtime` (main at `e78d00b5`), so its rule list leaves out `hold-state-on-the-object-not-in-parameters`. The judges applied that rule by hand. After this branch merges, update the runtime.
- **Graph-backed fidelities:** validate's reply tells the judge to "judge the checked format's files". At the model fidelity, the AI judge has to judge the graph validate just built — its classes, operations, parameters, properties, relationships — against the rules (see `corrections.log`). The reply should say so.
- **Scanner gap:** the `never-swallow-exceptions` and `use-exceptions-properly` graph rules flag only the deliberately faulty `_examples`. They miss every production `except Exception` that returns or substitutes a fallback.
- **Project folder:** the desktop app started this chat in an empty spare folder, so validate refused every repository path. The work-around set that spare session's `workpath` to the worktree.

- **Scanners that pass what they should catch:**
  - `coupling_rules.py:35, :50, :69`: one rule flags CE's own class names (`Module`, `OoadClass`), which is where the false `shape-classes-around-resources` hits come from.
  - The parallel-model scanner compares classes in one file only, so it finds none of the copies in §2.
  - `layer-separation` fires only on "Facade".
  - `practice_wide_rules.py:24` `OneWayDeps` returns inside its first loop, so it reports one import pair of the 25-module cycle.
  - `DeepModule` does not measure the 40%-public rule.
  - Free functions escape the size and nesting rules (`bdd_model.py:147 _parse_sketch` is 63 lines, four levels deep).
  - 11 drawio scanner operations pack real parameters into an untyped `_rest` tuple, so `limit-operation-parameters` passes them.
- **Report names collide:** names have one-second resolution, so two calls in the same second write one report and one graph file (`…T034343.md` holds only one of two calls).

## 11. Not validated

- `ddd/model/python`, `ddd/model/typescript`, and the `*.feature.py` channel files.
- Catalog generation: not run, because the MCP operation writes into the host's own checkout (B34).

## 12. Practice folders (second round)

Model fidelity on stories, ddd, ux, clean_engineering, bdd and agent_bdd; code fidelity on `ux/model`, `bdd/model`, and `ddd/model` drawio, markdown, sketch. The bugs are B19–B33 above. The design findings:

- **Second object models (high):**
  - UX screens hold links as name strings: `story_names`, `scenario_names`, `step_names`, `chrome_of`, `from_screen`/`to_screen`, `destinations` (`ux/model/nodes.py:259, :250, :365, :131`). `StoryDemoControl.story_steps` copies Stories' Step as dicts, normalised in 10 places. As a result `harness/graph/bound_node.py:206` hard-codes UX field names, and a renamed story or screen silently drops its links.
  - `ddd/model/nodes.py:102` `TacticalBuildingBlock.load_tactical_facts` copies every `graph_facts` value onto itself with `setattr` and re-scans the source with regexes.
  - `clean_engineering/model/model_descriptions.py:45` `model_members`, keyed by `"Class.member"`, plus `Operation.owner`, `interactions` and `described_by`: three paths to an operation's documented calls. `bdd/model/graph_bdd_model.py:29` reads the graph JSON by position.
  - `_drawio_base.py:1350`, writer :922–1190: about 480 lines of a second drawio writer and a second markdown class-model parser, called from nowhere.
  - `agent_bdd_common.py:772` `AgentSpecRunbook` parses mamba specs again, beside `PythonBddModel`.
  - `module_context_files.py:137` and `responsibilities.py:21` re-implement four card rules as `{name, message, contributor}` dicts, a sixth rule-hit shape (§2). Both are dead.
  - `diagram/class_layout.py:59, :79`: `DiagramCard` copies `DiagramClass.geometry` and `DiagramArrow` copies `Relationship`. There are three placement systems and two `Page` classes.
  - `ddd/model/nodes.py:449` `DDDModelFactory`: a second format registry beside `formats=`, called only from specs.
  - `bdd/model/nodes.py:37` `BehaviorNode` subclasses Stories' `StoryNode`.
- **Hidden fields shared between adapters:** the DDD sketch adapter sets `_preamble`, `_group` and other fields on markdown objects, and the markdown adapter reads them back with `getattr` (`ddd/model/markdown/nodes.py:319`, `sketch_ddd_model.py:104`).
- **State held for one call (medium):**
  - `drawio_class_model.py:85` has about 30 scratch fields (`_cell_x`, `_edge_src_id`, ...).
  - `_drawio_base.py:35` keeps a class-level `_explicit_paths` shared by every scanner in the host.
  - The same habit appears as `_links`, `_on_node`, `_body` set and restored in `finally`, `_id_to_screen`, `_kept`, and `_lines`.
  - `ux.py:49` `ensure_javascript(generator: str)` chooses a practice by string and builds it with no session.
- **Rules written twice:** `stories/rules/scenarios.py:47, :90, :125, :168` check once against the graph and once against `node.model`, and the two disagree. This is 1.4 Mode B. `scenarios.py:190` finds aggregate roots by matching the words `cart|order|account`.
- **Duplicated behaviour (medium):**
  - Stories: 5+ tree walks and 5 verb lists.
  - DDD: 4 tree walks, 4 stereotype parsers, 3 card orderings.
  - UX: 4 copies of "find the model file", and each node field listed 6 times.
  - Clean Engineering: `sync` ×5 and `class_open` ×4, brace matching ×7, `sys.path.insert` in 8 files. Java and Python `load_class` skip the `update_self` that TS and JS do.
- **Subtypes that change meaning:** base `load(path)` against drawio/miro `load(text)`; drawio `clone()` returns `str`.
- **Dead code:**
  - Stories: `load_epic`/`load_story`, `story_file.py` ×4, `spec_file.py`, `dot_path.py`, `verb_noun.py`, the Miro REST client.
  - DDD: `technical_names.py` and `vocabulary.py`; deleting the second also removes B15.
  - Clean Engineering: the module `__getattr__` re-exports, "backward compat" `classes`, and identity `to_field`.
- **Names:**
  - `_hydrate_*` (code_story_model), `Region.slot`, and `rows` (ddd drawio/sketch, ux `cli_state.py:74`) use banned words.
  - `StoryScenariosOneToFour` enforces 7.
  - `drawio.py` says "kit".
  - Miro writes mojibake `â€¦` into board headers.
  - A second `Echo` class lives in `tools/prompt_notify/prompt_notify.py:32`, beside `tools/echo`.

Good news: DDD and Stories nodes extend `BoundNode` and none copies the graph's own `Node`; the drawio and Miro class models share one node base.

---

# Task list

Ordered so each step unblocks the next. **Decide** marks a choice that is yours.

1. ✅ **Make the MCP host survive load:** cancel the tool when the timeout fires (B1); recover the accept loop or restart on WinError 64 (B2); keep Validate's per-call state per call (B3); write each call's graph to its own file. Then restart the host. Without this step nothing below can be validated.
2. ◐ **Finish validation:** the folders in §11. Make `catalog.generate_catalog` write into the project (B34), then generate the catalog.
3. ✅ **Fix the bugs B4–B33,** each with a spec. First the imports that do not exist (B19–B22) and the silent data loss (B23–B29). Then:
   - the two session-current files, the double imports, and config.json
   - the recipe exceptions, `write_tag`, and `generate_output`
   - the session root, partition, prompt_log, `_end_process`, and vocabulary
   - the double-recorded violations and the swallowed failures
   - the `current` exemption, `Path.cwd()`, the subprocess timeout, and `.secrets`

   Add a round-trip spec for every format adapter (render then parse gives the same model).
4. ✅ **Update the chat bar (B10) to the new MCP operations:**
   - `ticket.activate`, `ticket.workspace`, `ticket.open_worktree`
   - `stage.set_wip_limit`, `board.help(slug)`
   - repo tools without `repo_path`, `session` on handoff and record-decisions
   - the new sketch and grill parameters, `session.files` without `stage`

   Also fix its test stub. Coordinate with the cdd-chat-ui session.
5. ✅ **One Violation class** owned by the graph's rules, replacing the five shapes.
6. ✅ **One registry of practices and actions:** `PracticeCatalogue` and the action folders. Delete GuidanceCatalog's second catalogue, the catalog registry, `UTILITY_REGISTRY`, prompt_notify's scraped catalogue, and the six action lists; TypeScript receives the lists as data.
7. ✅ **Session state has one owner:** fold SessionLogs into Repo/Session (fixes B4 and one cycle); give a fidelity's session state its own object so `*_of(fidelity)` goes; give PracticeGuidance one session reference.
8. ✅ **Remove global "current" objects:** an action is made for its call's session (P-1, P-15, P-21); make `Session.switch`, `mark_loop`, `read_loop`, and `append_log` instance operations; remove `Graph.current`, `Board.current`, and `FileManager.current`.
9. ✅ **Decide P-2/P-3:** whether Python builds every command and chooses the format, which needs new MCP operations, or whether the TypeScript keeps those rules. Then remove the other copy.
10. ✅ **Kanban copies:** remove `Workspace`, the `*_name`/`*_slug` copies, and the dicts keyed by slug; Stage sends objects; generate the TypeScript types instead of hand-writing them.
11. ✅ **Delete the ProjectTicket family** (K-F13) or merge it with Ticket. **Decide:** whether GitHub project issues are needed.
12. ◐ **Break the dependency cycles** per `.sessions/_backlog/break-module-dependency-cycles.md`: the practices register their graph models instead of `harness/graph` importing them (this is 1.4 Mode B); move the shared marks below agent_tools, installation, hooks, and mcp; `space/session` stops importing harness.
13. ✅ **Split Session and Repo** along the jobs in §5: registry, log and loops, files; git, GitHub, and the session registry.
14. ✅ **Delete legacy names and dead code** (§7), updating every caller in the same change.
15. ◐ **Rewrite or delete the out-of-date model documents** (§8) once steps 5–13 settle the classes. Fix the prose that names fidelities that do not exist.
16. ✅ **Rename banned-word names** (§9). **Decide:** renaming the published MCP operation `iterate.mark_iterate_tick`.
17. ✅ **Small module decisions.** **Decide:**
    - Fold guidance_actions into guidance?
    - Fold handoff and record_decisions into space/session?
    - Does the board stay at the top of harness or move into space?
    - Move `output_folder.py` beside the specs that use it?
18. ✅ **Validate improvements** (§10): at graph-backed fidelities, the reply tells the judge to judge the graph it built; extend the exception rules to production code; fix the scanners that pass what they should catch; give each call a unique report name; update the runtime after the merge.
19. ✅ **Practice adapters on one model** (§12): UX links become references to Stories' nodes, not name strings; draw.io renders from the model, not via markdown; each practice keeps one parser per format and deletes the second writers and dead adapters; rules check the graph only (with step 12).

---

# Decisions

| # | Decision | Chosen | Why |
|---|---|---|---|
| 1 | Who builds the slash commands (P-2/P-3) | The button in TypeScript builds a command it puts in the chat box; server-side rules stay in Python | A command string is presentation; the only real rule (render the earlier fidelity first) moved into the generate action, so no MCP round trip builds a string |
| 2 | ProjectTicket (K-F13) | Deleted | Nothing used GitHub project issues; it was a second ticket model |
| 3 | `iterate.mark_iterate_tick` | Renamed `mark_iterate_round` | Banned word |
| 4 | Fold guidance_actions into guidance | Kept separate | Actions and practices are different concepts |
| 5 | Fold handoff and record_decisions | Into `space/session` | Both write into a session's folder; removed two tiny modules and their duplicated session lookup |
| 6 | Board home | `space/kanban` | The board tracks the work, beside session and repo |
| 7 | `output_folder.py` | `cdd_guidance/practices/` | Test-only helper leaves the framework; nearest folder above both channel specs |
| 8 | Rule slug `story-scenarios-one-to-four` | Renamed `story-scenarios-at-most-seven` | Name matches the limit it enforces |
| 9 | Chat bar handoff button | Plain prompt | User decision |
| 10 | `skill = Skill` alias | Kept | Matches `agent_tool`, `data_field` lowercase decorators |
| 11 | Dead `CodeStoryModel.save`/`load` | Port its spec to a real language, delete the dead code | Dead code kept alive only by a spec |
| 12 | Validate's graph file | Written beside each report | Concurrent calls overwrote one shared `edited-graph.json` |
| 13 | MCP time limit (B1) | Calls keep running; identical calls join; the caller is told it is still running | A worker thread cannot be stopped; reporting failure caused retries |
| 14 | Practice and action registries | `PracticeCatalogue` plus a separate `ActionCatalogue` | Practices are a fixed ordered list; actions are found from their folders, one kit can publish several |
| 15 | Stage definitions | `ApproachStage`/`STAGES` in `stages.py`, read by the catalog and the board | One definition of each stage's scope and actions |
| 16 | Graph node model | The parsed practice object is the node; practices register a `GraphPractice` | The framework no longer imports the practices |
| 17 | Rule hits | One `Violation` class in `harness/graph/violation.py` | Five shapes became one |
| 18 | Per-call state | A `ToolCall` holds the call's project and session; a fresh session object per call; a new action per call | Removes the global "current" objects and stops actions replacing another call's guideline |
| 19 | References in data | `@identity` mark and `@data_field(reference=True)` per field | An owner still sends its children in full; a reference sends only the identity |
| 20 | Board home | `space/kanban` (decision 6) | The board tracks the work |
| 21 | Session/Repo split | Sessions, SessionLog, SessionFiles, Handoffs; Repo, Branch, Commit, Git, Worktrees; `current`/`switch` on a `sessions` toolset | Each object does one job; dead code deleted rather than split |
| 22 | Harness layering | `harness/name` and `harness/marks` at the bottom; publishers register their Destination kinds; Installer moved up to `harness/installer` | Breaks every harness-internal cycle without moving ~60 concrete mark imports |
| 23 | DDD stereotypes | A decorator with no arguments (or a `<<Mark>>` doc comment) is a stereotype | Clean Engineering keeps no list of DDD's words |
| 24 | LERN slug `outline-rows-loop-over-examples` | Renamed `outline-entries-loop-over-examples` | Banned word |
| 25 | `.secrets` | Untracked and ignored | It held a `CURSOR_API_KEY`; the key is still in history and must be rotated |
