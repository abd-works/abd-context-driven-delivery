# Cross-file second pass — ensure-domain-orientation-refactor

Worktree `C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio`, commit d6c41b23. Read against
`clean_engineering.md` (shared rules and the code fidelity), `.claude/rules/coding.md`, `.claude/rules/writing-guidelines.md`,
every corrections log in the brief, and `domain-orientation-analysis.md`. This pass looks only for problems that show
when two or more files are read together. Validate was not run for this report, so there are no graph hits to judge;
every finding below is an AI judgment and names each place involved.

Searches made from the corrections logs: copies of a collaborator's fields (`*_name`, dicts by slug, `*Json` types),
helper classes doing an owner's job, operations taking state the object holds (`session=`, `repo_path`, slugs and
formats as parameters), retired MCP operation names, stale module and class names in prose, and session-folder facts
(`session.json`, `session.log`, `.sessions`, report names) outside Session.

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/session-client.ts`

### `no-legacy-api-after-refactor` — Fail
- session-client.ts:25 `activateSession`: calls the MCP operation `board.activate`, which no longer exists; activation moved to `Ticket.activate` (harness/kanban/ticket.py:226, published as `ticket.activate`). Opening a session from the chat bar fails on a real server.
- session-client.ts:49 `openClose`: calls `board.workspace`, which moved to `Ticket.workspace` (harness/kanban/ticket.py:251, `ticket.workspace`). The close dialog can never open on a real server.
- session-client.ts:3 imports `WorkspaceData` from `@cdd/harness/kanban/board`; the language adapter now generates it in `.claude/language-adapters/typescript/harness/kanban/ticket.ts:15`, so the import names a type that the board module does not export.
- cdd-stub.ts:93 (harness/chat-ui/pane/test/cdd-stub.ts) answers `board.activate`, and close_active_session_story.test.ts:18 and open_session_story.test.ts:30 assert on `board.activate`/`board.workspace`, so the chat-bar story tests keep passing against operations the Python server removed.

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts`

### `do-not-invent-parallel-object-models` — Fail
- chat-bar-client.ts:98 `fidelities`: reads `column.fidelities?.[slug]` for each fidelity's name, but Stage sends no `fidelities` field (harness/kanban/board.py:293-306 sends `work_required`, `formats`, `default_formats`; the generated `ColumnData` in `.claude/language-adapters/typescript/harness/kanban/board.ts:38` has none). Every fidelity name in the chat bar is empty. The chat bar builds its own `FidelityJson` (fidelity-client.ts:25) from three dicts keyed by slug instead of holding the `FidelityProgressData` the ticket already sends.
- chat-bar-client.ts:101: the default `{ generate: 'to_do', validate: 'to_do', review: 'to_do' }` copies `ActionStates` (harness/kanban/ticket.py:662) a fourth time.
- fidelity-client.ts:64 `status`: invents a `validated` state that `FidelityProgress.state` (harness/kanban/ticket.py:513) does not have (known CU-1, still open).

### `eliminate-duplication` — Fail
- chat-bar-client.ts:17 `STAGES`: the column order is written again here, in harness/chat-ui/pane/test/examples/chat-bar.examples.ts:19 (`STAGE_ORDER`, used by cdd-stub.ts:59), in harness/kanban/board.py:223 `_build_columns`, and in harness/catalog_generator/foundry_chrome.py:68 `STAGE_COLUMNS`. `stages` (chat-bar-client.ts:72) also works out stage status itself (known CU-2).
- fidelity-client.ts:14 `PRACTICE_COLOURS` repeats `PracticeGuidance.COLOUR`, which Board already sends as `practices[].colour` (harness/guidance/guidance.py:230); harness/graph/app/App.tsx:16 keeps a third practice list.
- fidelity-client.ts:22 `BUILDER_ACTIONS` and harness/kanban/app/src/kanban/board/board-brand.ts:33 `TILE_ACTIONS` are two TypeScript action lists; Python keeps `STAGE_ACTIONS` (harness/kanban/board.py:36), `_KNOWN_ACTIONS` (space/session/session.py:49), `_FALLBACK_ACTIONS` (tools/prompt_notify/prompt_notify.py:40) and `LIFECYCLE_ACTIONS` (harness/catalog_generator/catalog_generator.py:472), while the action folders under cdd_guidance/actions are the real set.

## Judgment — `harness/kanban/ticket.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- ticket.py:338 `generate_commands(fidelities, formats)`: still takes fidelity slugs and formats and looks each progress up again by slug (`progress_of`, ticket.py:135). This is the exact shape the 2026-11-06 correction in harness/kanban/.context/corrections.log rejects; `PracticeSessionOutput.keep_format` (space/session/session.py:335) already exists to save a format on its fidelity but the command path does not use it (P-3, P-4 open).
- ticket.py:658 `FidelityCommands._in_session` writes `session=` into the command text, and harness/kanban/app/src/kanban/ticket/ticket-client.tsx:265 `actionCommand` writes it again for every other command; harness/guidance_actions/guidance_actions.py:36 parses it back. harness/chat-ui/pane/hooks/chat-bar/fidelity-client.ts:145 builds `/actions-{action}` without it, so the chat bar's validate and render act on the chat's current session, not the ticket's (P-2 open, bug 10).

### `eliminate-duplication` — Fail
- ticket.py:564 `finish_review` writes `review {PracticeClass} {fidelity}`; space/session/session.py:352 `log_validation` writes `validate {PracticeClass} {fidelity}`; space/session/session.py:1345 `_action_line` writes action lines naming the practice by its key. Three writers in two modules use two names for the practice, so space/session/session.py:199 `LogEntry.names` has to accept both. One owner (the session's practice and fidelity) should write every fidelity line.
- ticket.py:655 `render_earlier` builds `/actions-render ... format= source=`; harness/kanban/app/src/kanban/ticket/tile-actions-client.ts:110-118 builds `/actions-{action}`, `/actions-render` and `/actions-validate` by hand; harness/kanban/app/src/kanban/ticket/ticket-client.tsx:14 `RUN_NEXT_COMMANDS` holds a third table. Commands are built in four places across Python and TypeScript (known 1.3).

### `use-intention-revealing-names` — Fail
- ticket.py:157 `column_name`, :206 `next_slug`, :434 `FidelityProgress.ticket` (a name string), :464 `practice` (a key string): `*_name` copies of objects the ticket holds, the pattern harness/kanban/corrections.log (2026-11-05) names; harness/kanban/board.py:166 `active_name` and harness/kanban/board.py:407-417 `Help.practice`/`fidelity`/`stage` do the same (K-F20, K-F21 open).

## Judgment — `space/session/session.py`

### `do-not-invent-parallel-object-models` — Fail
- session.py:940 `saved_current_session` setter: records the current session twice, in `.sessions/session.json` through `WorkState` (space/work_state.py) and in `.sessions/_active` through `SessionLogs.write_active_session` (harness/hooks/session_logs.py:30). The hook server reads only `_active` (harness/hooks/hook_server.py:642, :733, :817). Switching to main skips the `_active` write, and `SessionLogs.clear_active_session`/`consolidate_logs_for_close` (session_logs.py:41, :104) have no callers, so after a switch to main or a close the hooks keep writing `last-chat-injected-rules.md`, `chat-injections/` and `dispatch.debug` into the old session's folder.
- harness/hooks/session_logs.py:57 `SessionLogs.session_folder` and :15 `MAIN_SESSION` repeat `Repo.session_folder` (space/repo/repo.py:1140) and `MAIN_SESSION_NAME` (session.py:44) without the primary-checkout and closed-session handling, so a hook in a ticket's worktree resolves a different folder than Session does. This also makes `space` import `harness.hooks`.

### `eliminate-duplication` — Fail
- session.py:655 `root` (workpath, else repo_path, else `project_checkout()`), session.py:710 `work_folder` (workpath, else repo_path, else `project_folder()`), harness/guidance_actions/guidance_actions.py:394 (workpath, else repo_path, else `project_checkout()`) and session.py:715 `_worked_on_files` (workpath, else `repo.root`): four answers to "the folder the session works in" with different last fallbacks, so a session with no workpath opened from a subfolder gets two different roots (practice folders use `work_folder`, sketches and grill answers use `root`).
- session.py:646, :811, :1296, :1300; space/repo/repo.py:1125, :1150; space/work_state.py:19 `STATE_NAME`; harness/guidance_actions/guidance_actions.py:393: the `session.json` file name is spelled in eight places although `Session.session_file` (session.py:644) owns it; session.py:919 and :1220 repeat the `"session.log"` fallback that `log_path` (session.py:1371) owns.
- session.py:68 `name_of` is a regex copy of `Name(text).title_slug` (harness/agent_tools/name.py:66); harness/chat-ui/pane/test/cdd-stub.ts:83 copies it again in TypeScript, and cdd_guidance/practices/clean_engineering/model/drawio/drawio_class_model.py:706 `_slug` and harness/kanban/story_test.py:294 `_slug` are two more hand-written slug regexes.

### `hold-state-on-the-object-not-in-parameters` — Fail
- session.py:424 `output_paths_of(fidelity)`, :436 `files_of(fidelity)`, :445 `has_output_of(fidelity)`: the practice is handed one of its own fidelities, and harness/guidance/guidance.py:663-680 `FidelityGuidance.output_paths/files/has_declared_output` hand themselves back to it; the fidelity should answer from state it holds (known open item).
- session.py:555 `current(repo_path)`, :797 `switch(name, workpath, repo_path, session_path)` → :818 `_repo_to_switch_in`: a published MCP operation still takes `repo_path`, and harness/kanban/ticket.py:236 passes `repo_path=repo.root` although the ticket's board holds the Repo (P-29 open).

## Judgment — `harness/guidance/guidance.py`

### `do-not-invent-parallel-object-models` — Fail
- guidance.py:345 `_attach_workspace` and :213 `session_output`: a practice holds its session three ways, `session` (a name string), `workspace` (the Session) and `session_output` (its PracticeSessionOutput), all set by space/session/session.py:244-248. guidance.py:683 `_session_output` reads one and guidance.py:701 `_reports_folder` reads another through `getattr(..., "workspace")`; they can name different sessions when an action replaces the shared practice (P-21 open).
- guidance.py:208 `key` (`inspect.getfile` folder) and guidance.py:253 `context_index_key` (`AssetLocator.class_file_directory().name`) compute the same practice key two ways; space/context_config.py:75-85 normalises the key a third way with `replace("-", "_").casefold()`.

### `eliminate-duplication` — Fail
- guidance.py:697 `new_report_path` writes `{slug}-{stamp}.md`; harness/kanban/report.py:178 `ReportFile.stamp` takes the name apart again with `rsplit("-", 1)`. The report file name has a writer in one module and a parser in another.

## Judgment — `harness/kanban/board.py`

### `eliminate-duplication` — Fail
- board.py:448 `Help.href` builds the forge page as `{practice.key}-{fidelity.name}` and keeps `FIDELITIES_WITHOUT_PAGE` (board.py:40) by hand; harness/catalog_generator/catalog_generator.py:111 and :136 build the same page names, and the catalog already knows which fidelities get no page (`omitted_from_catalog`, `on_board`). The two drift as soon as a page is added or dropped.
- board.py:223 `_build_columns` (`name.capitalize()`), board.py:312 `Stage.work_required` (`self.name.lower()`), board.py:429 `Help.stage` (`capitalize()`) and harness/catalog_generator/foundry_chrome.py:68 `StageColumn(stage, key, title, scope_name, ...)` are two models of a stage; harness/kanban/app/src/kanban/board/board-brand.ts:21 `STAGE_SCOPES` copies the catalog's scope names and descriptions word for word.

### `do-not-invent-parallel-object-models` — Fail
- board.py:293-306 `Stage.work_required_slugs`, `formats`, `default_formats`: three dicts keyed by slug flatten `FidelityGuidance` for the clients (T-PY1 open); harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts:90-104 then rebuilds a fidelity from them.

## Judgment — `harness/kanban/report.py`

### `do-not-invent-parallel-object-models` — Fail
- report.py:251 `_violation_of(hit: dict)`: reads the ten-key violation dict built by cdd_guidance/actions/validate/graph_json_reader.py:191 `_record` (`location`, `line_number`, `violation_message`, ...), and turns it into report.py:44 `Violation`; harness/graph/explorer.py:39 `RuleHit` is a third shape of the same hit (A-F14 open).
- report.py:220 imports `validate.graph_json_reader` as a top-level module rather than `cdd_guidance.actions.validate.graph_json_reader`, so one file loads under two module names.

## Judgment — `harness/guidance_actions/guidance_actions.py`

### `do-not-invent-parallel-object-models` — Fail
- guidance_actions.py:17 `GuidanceRef` TypedDict and :26 `GuidanceArg`: guidance still travels as dicts and strings and is loaded again in :198 `_bind_guidance` (A-F4, P-1 open), while space/session/session.py:954 `Session.practices` holds the practice objects.

## Judgment — `harness/kanban/app/src/kanban/ticket/ticket.ts`

### `no-legacy-api-after-refactor` — Fail
- ticket.ts:4 `TicketFiles`: a hand-written type named after the deleted Python helper `TicketFiles`, used in board-store.ts:16, tile-formats.ts:28, files-panel-client.ts:11 and tile-client.ts:56. It copies the shape of `FidelityProgress.files` (harness/kanban/ticket.py:578) instead of importing it from the language adapter.

## Judgment — `harness/kanban/.context/kanban-model.md`

### `no-legacy-api-after-refactor` — Fail
- kanban-model.md:58, :277, :473, :637: the model still declares `TicketFiles`, `PracticeRoot` and `practice_roots`, which the code deleted.
- kanban-model.md:373: the model keeps `ticket.generate_commands(fidelities, formats)`, the operation the 2026-11-06 correction (harness/kanban/.context/corrections.log) and the `hold-state-on-the-object-not-in-parameters` rule in cdd_guidance/practices/clean_engineering/clean_engineering.md:230 reject.
- kanban-model.drawio:43: the diagram still draws `Board.activate(ticket: str, ...)`, `open_worktree`, `workspace(ticket)`, `set_wip_limit(stage, limit)`, `worktree_of` and `help(practice, fidelity)`, which moved to Ticket and Stage; kanban-model.md:66 says the diagram draws exactly what the markdown says.

## Judgment — `harness/chat-ui/.context/story-map.md`

### `no-legacy-api-after-refactor` — Fail
- story-map.md:64: says the session list calls `board.activate`; the operation is `ticket.activate` (harness/kanban/ticket.py:226). story-map.md:10 names `harness/kanban/board.py` (`board.activate`) as a source.

## Judgment — `cdd_guidance/builders/create_context_tool/create_context_tool.md`

### `no-legacy-api-after-refactor` — Fail
- create_context_tool.md:13: tells agents to subclass `BaseContextTool` in `practices/base/` and points at `utilities/workspace/workspace_session.md` and `utilities/partition_pipeline/partition_pipeline.md`; none of these exist (cdd_guidance has no `utilities/` and no `practices/base/`). create_context_tool.md:45 also names `@toolset-manifest` and `python -m harness manifest`, removed with `ToolsetManifest`. cdd_guidance/builders/create_practice_guidance/create_practice_guidance.md:15 repeats the `utilities/` paths. Both are installed skills, so agents are sent to files that are gone.

## Judgment — `space/repo/.context/repo-modules.md`

### `no-legacy-api-after-refactor` — Fail
- repo-modules.md:1 and :59 describe `space/git/git.py`, which no longer exists; space/session/legacy/workspace_session.md:67 still tells agents to retarget `WorkSession.git`, and harness/markdown/markdown.py:423 names `WorkSession` in a docstring.
- cdd_guidance/agents/discovery.md:26 names a `bdd-modules` fidelity; BDD's fidelities are behavior, realization and development.

## Judgment — `tools/prompt_notify/prompt_notify.py`

### `do-not-invent-parallel-object-models` — Fail
- prompt_notify.py:403-460 `_walk_skill_tree`, `_walk_practice_leaves`, `_walk_rule_tree`: build a second catalogue of actions, practices and fidelities by scraping install folder names, while harness/guidance/practice_catalogue.py `PracticeCatalogue` holds the live practices and fidelities (TL-1 open). prompt_notify.py:401 `_compact` uses `Name(text).kebab`, and the walkers beside it convert with `replace("_", "-")` by hand.
