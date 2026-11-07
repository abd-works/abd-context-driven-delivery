# Clean Engineering validation after the domain-orientation refactor

Branch `ensure-domain-orientation-refactor`, validated at `d6c41b23`; module cards fixed in `784b4f31`. The full suite passes (2703 examples).

Validate ran through the CDD MCP host at the modules, model, and code fidelities across `harness/`, `space/`, `tools/`, and `cdd_guidance/`. For each call, an AI judge reviewed every rule and appended its judgment to the saved report. A separate cross-file pass looked for problems that show only across files, using the mistakes the corrections logs record. The 63 reports are in `validation-reports/` beside this file.

**The short answer:** the refactor did what it set out to do. The six dicts on Ticket are gone, actions read their call's session, practices answer their own roots and files, and the board and stage do their own work. The repository still has more open issues than hoped for, and they cluster in a few places:
- the MCP host itself
- a handful of second object models
- global "current" objects
- two very large classes, Session and Repo
- one big dependency cycle

Several findings are real bugs and should be fixed first.

Severity: **high** means wrong behaviour or a second object model, **medium** means a rule plainly broken, and **low** means naming or documentation.

---

## 1. Bugs: wrong behaviour today

| # | Where | What goes wrong | Sev |
|---|---|---|---|
| B1 | `harness/mcp/mcp_server.py:703` | The 10-second timeout around `to_thread.run_sync` cannot stop the thread. The tool runs to the end and writes its files, but the caller is told `TimeoutError`. Callers then retry work that already finished. That pile-up dropped the host twice during this validation. | high |
| B2 | MCP host accept loop (`~/.cdd/server.log`) | After `OSError: [WinError 64]` the asyncio accept loop dies. The port stays open, every connection is refused, and the host never recovers on its own. | high |
| B3 | `cdd_guidance/actions/validate/validate.py:55` | `_unchecked_files` is per-call state kept on the shared action object; all other per-call state is thread-local. Concurrent validates overwrite each other's filter and drop the wrong hits from a report. | high |
| B4 | `space/session/session.py:938`, `harness/hooks/session_logs.py`, `hook_server.py:642/733/817` | The current session is saved twice: in `.sessions/session.json` through WorkState and in `.sessions/_active` through SessionLogs. The hooks read only `_active`, which a switch to main does not update and a close never clears. So after either, hooks keep logging into the old session. | high |
| B5 | `stories.py:44`, `ux.py:40`, `generate.py:10` and 9 more | Modules are imported under two names (`validate.validate` and `cdd_guidance.actions.validate.validate`). Python loads such a file twice, so classes, `isinstance` checks, and class-level state split into two copies. | high |
| B6 | `space/context_config.py:35` | A malformed `config.json` loads as `{}`, and the next `update` saves that over the file, erasing the project's guidelines and practice folders. | high |
| B7 | `harness/agent_tools/agent_tools.py:1796` (and 1830, 1911, 1968, 1984) | `except Exception` hides failures while a recipe line in `@agent_instructions` is evaluated. An `if` silently takes its `else`, or a return's source text goes to the agent as instructions. `tools/granola/granola.py:116` relies on this: it calls `format_filing_plan()` without its required argument. | high |
| B8 | `space/repo/repo.py:471` `CliAgentBinding.write_tag` | Sets `repo._annotated_tag_target` for one call and never restores it, so every later `write_annotated_tag` on that Repo tags the last branch instead of HEAD. | high |
| B9 | `cdd_guidance/practices/clean_engineering/clean_engineering.py:71` | `generate_output` calls `self.drawio.render()`, but `drawio` defaults to None and no caller passes it, so it raises AttributeError. | high |
| B10 | `harness/chat-ui/pane/hooks/chat-bar/session-client.ts:25, :49`, `chat-bar-client.ts:98`, `fidelity-client.ts:145` | The chat bar calls `board.activate` and `board.workspace`, which are now `ticket.activate` and `ticket.workspace`. It reads `column.fidelities[slug]`, which Stage never sends, so every fidelity name is empty. It builds `/actions-*` commands without `session=`, so validate and render act on the chat's session. The test stub still answers `board.activate`, so its tests pass. | high |
| B11 | `space/session/session.py:655, :710, :715`, `harness/guidance_actions/guidance_actions.py:394`, `session.py:376/384` vs `:429` | "The folder the session works in" is worked out four ways, each with a different last fallback. One session can get two roots: practice folders use one, and sketches and grill answers the other. Declared outputs and the file manager disagree for pattern practices. | high |
| B12 | `cdd_guidance/actions/partition/partition.py:162` | `on` ignores the item and drops `out_root` and `paths`. The index and segments are written under the session root while the reply names `out_root`. | medium |
| B13 | `tools/prompt_log/prompt_log.py:34` | It logs into the CDD checkout, not the project, and its docstring names `.context/sessions/`. | medium |
| B14 | `harness/hooks/hook_daemon.py:172` vs `harness/mcp/mcp_daemon.py:150` | Two copies of `_end_process` have drifted. The hook copy has no guard against pid 0 or its own pid. | medium |
| B15 | `cdd_guidance/practices/ddd/model/vocabulary.py:18` | Importing it sets the process-wide `socket.setdefaulttimeout(2)` and downloads NLTK data inside the shared MCP host. | medium |
| B16 | `harness/graph/rules.py:39` | `attach_rules` records each violation, then `apply_rules` records it again. Only a de-duplication check hides the double count. | medium |
| B17 | Swallowed failures: `installation/files.py:163`, `markdown.py:984`, `stories/model/json/nodes.py:136`, `agent_bdd_common.py:540`, `catalog_generator.py:1253`, `repo.py:2286/:2218` | A wrong slash command is installed, a corrupt story graph reads as an absent one, catalog pages silently go missing, a failed fetch returns as though it worked. | medium |
| B18 | `agent_cli_bdd.py:329` | The `timeout_seconds` argument is silently discarded. | medium |

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

## 11. Not validated yet: the MCP host went down

- Model fidelity for the six practice folders: stories, ddd, ux, clean_engineering, bdd, agent_bdd.
- Code fidelity for `ux/model`, `bdd/model`, and the drawio, markdown, and sketch folders of `ddd/model`.
- Validation of the module cards rewritten and created in `784b4f31` (the space, tools, and handoff cards passed their graph rules; the rest were not run).
- Catalog generation.

---

# Task list

Ordered so each step unblocks the next. **Decide** marks a choice that is yours.

1. **Make the MCP host survive load:** cancel the tool when the timeout fires (B1); recover the accept loop or restart on WinError 64 (B2); keep Validate's per-call state per call (B3); write each call's graph to its own file. Then restart the host. Without this step nothing below can be validated.
2. **Finish validation:** §11, one call at a time; then generate the catalog.
3. **Fix the bugs B4–B18,** each with a spec: the two session-current files, the double imports, config.json, recipe exceptions, `write_tag`, `generate_output`, the session root, partition, prompt_log, `_end_process`, vocabulary, the double-recorded violations, and the swallowed failures.
4. **Update the chat bar (B10) to the new MCP operations:**
   - `ticket.activate`, `ticket.workspace`, `ticket.open_worktree`
   - `stage.set_wip_limit`, `board.help(slug)`
   - repo tools without `repo_path`, `session` on handoff and record-decisions
   - the new sketch and grill parameters, `session.files` without `stage`

   Also fix its test stub. Coordinate with the cdd-chat-ui session.
5. **One Violation class** owned by the graph's rules, replacing the five shapes.
6. **One registry of practices and actions:** `PracticeCatalogue` and the action folders. Delete GuidanceCatalog's second catalogue, the catalog registry, `UTILITY_REGISTRY`, prompt_notify's scraped catalogue, and the six action lists; TypeScript receives the lists as data.
7. **Session state has one owner:** fold SessionLogs into Repo/Session (fixes B4 and one cycle); give a fidelity's session state its own object so `*_of(fidelity)` goes; give PracticeGuidance one session reference.
8. **Remove global "current" objects:** an action is made for its call's session (P-1, P-15, P-21); make `Session.switch`, `mark_loop`, `read_loop`, and `append_log` instance operations; remove `Graph.current`, `Board.current`, and `FileManager.current`.
9. **Decide P-2/P-3:** whether Python builds every command and chooses the format, which needs new MCP operations, or whether the TypeScript keeps those rules. Then remove the other copy.
10. **Kanban copies:** remove `Workspace`, the `*_name`/`*_slug` copies, and the dicts keyed by slug; Stage sends objects; generate the TypeScript types instead of hand-writing them.
11. **Delete the ProjectTicket family** (K-F13) or merge it with Ticket. **Decide:** whether GitHub project issues are needed.
12. **Break the dependency cycles** per `.sessions/_backlog/break-module-dependency-cycles.md`: the practices register their graph models instead of `harness/graph` importing them (this is 1.4 Mode B); move the shared marks below agent_tools, installation, hooks, and mcp; `space/session` stops importing harness.
13. **Split Session and Repo** along the jobs in §5: registry, log and loops, files; git, GitHub, and the session registry.
14. **Delete legacy names and dead code** (§7), updating every caller in the same change.
15. **Rewrite or delete the out-of-date model documents** (§8) once steps 5–13 settle the classes. Fix the prose that names fidelities that do not exist.
16. **Rename banned-word names** (§9). **Decide:** renaming the published MCP operation `iterate.mark_iterate_tick`.
17. **Small module decisions.** **Decide:**
    - Fold guidance_actions into guidance?
    - Fold handoff and record_decisions into space/session?
    - Does the board stay at the top of harness or move into space?
    - Move `output_folder.py` beside the specs that use it?
18. **Validate improvements** (§10): at graph-backed fidelities, the reply tells the judge to judge the graph it built; extend the exception rules to production code; update the runtime after the merge.
