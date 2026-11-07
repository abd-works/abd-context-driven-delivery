# Cross-file pass, round 3 — Clean Engineering

Branch `ensure-domain-orientation-refactor` at 42ab935c, worktree `C:/Users/jeffa/.cdd/runtime-ensure-domain-orientatio`.
Scope: `harness/`, `space/`, `tools/`, `cdd_guidance/`, `scripts/` (not `retired/`, `node_modules/`, `_examples/`, `examples/`, specs).
No MCP call: this pass reads code across files, against this branch's `clean_engineering.md` rules, `.claude/rules/coding.md`,
`.claude/rules/writing-guidelines.md`, the corrections logs, and the decisions log at the end of `clean-engineering-validation.md`.

Each finding says **new** or **left** (left from rounds 1–2, with the section of `clean-engineering-validation.md`).
Decisions in that log (1 TypeScript builds command strings, 10 the `skill = Skill` alias, 14 PracticeCatalogue plus ActionCatalogue,
15 stages in `stages.py`, 18 ToolCall, 22 harness seams) are not re-reported; findings below are places where the code does not do
what a decision says.

## Corrections logs re-read — recorded mistakes that came back

- `cdd_guidance/patterns/cdd_claude_mod/corrections.log` and rule `contract-comes-from-the-adapter`: the chat bar again writes its own
  copies of the generated data (`FidelityJson`, `StageJson`), and names a client after the bar (`FidelityClient`) rather than the Python
  object it mirrors (`FidelityProgress`).
- `cdd_guidance/patterns/cdd_web_domain_access/corrections.log` ("the folder each practice works in, as `session.json` records it or by
  the practice's default"): a practice's folder is now also kept in `.context/practices.json` and `.context/config.json`, and worked out
  four ways — the B11 pattern one level down.
- `space/kanban/corrections.log` (Ticket copying its collaborators' fields): `FidelityProgress` still sends `ticket`, `practice`, and
  `fidelity_slug` as strings beside the objects, and `ReportRule` copies a Rule's name and text.
- `space/session/corrections.log` / `.sessions/.../corrections.log` (hold state on the owner): Guidance still holds its session as a name,
  as `workspace`, and as `session_output`; `output_overrides(fidelity)` takes the fidelity's name.
- `.sessions/session-board/validation-reports/corrections.log`: not recurred (this report uses project-root paths and single lines).

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/fidelity-client.ts`

### `do-not-invent-parallel-object-models` — Fail
- fidelity-client.ts:24 `FidelityJson` is a hand-written copy of `FidelityProgressData` (slug, practice, name, state renamed `progress`, violation_count, actions, default_format, next_action), filled field by field in chat-bar-client.ts:100; the adapter's own type is imported on line 4 and only used inside it. Breaks `contract-comes-from-the-adapter` and repeats the cdd_claude_mod correction. Left (§2 "FidelityJson and its invented validated state").
- fidelity-client.ts:62 `status` still invents a `validated` state the Python `FidelityProgress.state` never sends. Left (§2).
- fidelity-client.ts:38 `FidelityClient` is named after the bar, not after `FidelityProgress`, the Python object it mirrors (cdd_claude_mod correction: `{Object}Client`). New.

### `eliminate-duplication` — Fail
- fidelity-client.ts:22 `ACTION_ICONS` lists nine action names by hand (generate … document, advance) beside `Stage.actions`, which the board already sends (chat-bar-client.ts:88 reads it). New.

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/stage-client.ts`

### `do-not-invent-parallel-object-models` — Fail
- stage-client.ts:12 `StageJson` is a hand-written type with fields no Python `Stage` has (`status: done|in_progress|not_reached`, `isShown`, `canShow`), worked out in chat-bar-client.ts:77 from column order. New.
- stage-client.ts:8 `STAGE_ICONS` keys the five column names by hand beside `stages.py`. New.

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts`

### `hold-state-on-the-object-not-in-parameters` — Fail
- chat-bar-client.ts:111 the practice colour is found with `board.practices.find(practice => practice.key === progress.practice)` because `FidelityProgress.practice` is a string, not the practice; every reader of the board repeats this lookup. Left (K-F21 family).

## Judgment — `space/kanban/ticket.py`

### `do-not-invent-parallel-object-models` — Fail
- ticket.py:399 `FidelityProgress.ticket` is a `str` data field, a `*_name` copy of its Ticket, sent beside the `@identity` the class already declares. Left (§2 "FidelityProgress.ticket: str", K-F21).
- ticket.py:405 `fidelity_slug` (sent as `slug`) copies `fidelity.slug` beside the `fidelity` data field that sends the whole fidelity. Left (§2).
- ticket.py:423 `practice` sends the practice key string beside the fidelity that holds its practice, which is why the chat bar and the board look practices up by key. New.
- ticket.py:559 `rule_descriptions` is a dict of rule text keyed by slug, scraped from the practice's Rule objects; `ReportRule` (report.py:194) then copies text out of it. The owner, `Rule`, already holds slug and body. Left (P-22).

### `eliminate-duplication` — Fail
- ticket.py:552 `rules_answered_by` / :559 `rule_descriptions` assemble "the practice's shared rules, every fidelity's, and this one's", which Validate assembles again in validate.py:303 and :317. Left (A-F1, now in two modules).
- ticket.py:523 `finish_review` names the practice by class name in the log line; session_log.py:370 names it by key; session_log.py:75 `LogEntry.names` accepts either. Left (§4 "fidelity log lines").

## Judgment — `space/kanban/report.py`

### `do-not-invent-parallel-object-models` — Fail
- report.py:27 `ReportRule` copies a Rule's name and description and a fidelity's slug as strings (`fidelity: str`, `name: str`, `description: str`) instead of holding the `Rule` and the `FidelityProgress`. New.

## Judgment — `space/kanban/board.py`

### `do-not-invent-parallel-object-models` — Fail
- board.py:399 `Help` re-exposes `overview`, `guidance`, and `rules` of the practice or fidelity it also sends whole. Left (§2, K-F20).

### `eliminate-duplication` — Fail
- board.py:446 `Help.href` builds the forge page path that catalog_generator.py:115 and :140 build for the same pages. Left (§4).
- board.py:38 `FIDELITIES_WITHOUT_PAGE = ("ddd-model", "bdd-realization")` keeps by hand which fidelities the catalog has no page for; the catalog decides that, so a new or removed page silently breaks the board's link. New.

## Judgment — `space/kanban/app/src/kanban/ticket/tile-actions-client.ts`

### `eliminate-duplication` — Fail
- tile-actions-client.ts:9 `ACTIONS_WITH_FORMATS = ['generate', 'render']` copies `Stage.producing_actions`, which action-bar-view.tsx:36 already reads from the board. Two answers to one question in one app. New.

### `hold-state-on-the-object-not-in-parameters` — Fail
- tile-actions-client.ts:29 `ticket.progressNamed(slug)`, `stateOf(slug)`, `violationCountOf(slugs)`, `allows(slug, action)`: TicketClient still looks up progress by slug in 12 operations (ticket-client.tsx:86–191), and board-store.ts:15/38/39 keep `stage: string`, `fidelity: string`, `slugs: string[]` in place of the objects. Left (§2 "TicketClient looks everything up by slug").

## Judgment — `harness/guidance/guidance.py`

### `do-not-invent-parallel-object-models` — Fail
- guidance.py:89 a Guidance still holds its session three ways: `session` (a name string), `workspace` (the Session, typed `Any`, under a second word), and each fidelity's `session_output`. Task 7 is ticked ("give PracticeGuidance one session reference") but the code keeps all three; agent_bdd.py:20 passes the name on, ux.py:65 copies both onto a companion, practice_session_output.py:127 sets `workspace` through the private `_attach_workspace`. Left (§2).
- guidance.py:217 `practice_slug` (sent as `slug`) repeats `slug`; guidance.py:233 `fidelity_slugs` (sent as `fidelities`) sends slugs in place of the fidelities. New.

### `use-consistent-naming` — Fail
- guidance.py:343 `_attach_workspace` / `workspace`: the Session is called `workspace` here, `session` on actions, `_session` on PracticeSessionOutput; the Workspace class was deleted, its name was not. New.

## Judgment — `space/session/practice_session_output.py`

### `eliminate-duplication` — Fail
- practice_session_output.py:245 a practice's folder is kept in three files — `session.json` (`outputs.root`, :235), `.context/practices.json` (`RememberedFolders`, :42), and `.context/config.json` `practice_folders` (`ContextConfig`, :247) — and worked out four ways: `folder` (:257), `output_root` (:264), `folders`/`_folders` (:151/:142), and FidelitySessionOutput's own root (:336). Each has a different last fallback. This is B11's "four roots" at practice level and repeats the cdd_web_domain_access correction. New.

### `hold-state-on-the-object-not-in-parameters` — Fail
- practice_session_output.py:309 `output_overrides(fidelity: str)` is handed a fidelity name by FidelitySessionOutput (:335), which holds the fidelity: the `*_of(fidelity)` shape reshaped, not removed. Left (§3 `output_paths_of`).
- practice_session_output.py:49 `RememberedFolders.of(practice)` / :53 `remember(practice, folders)`: a class keyed by the practice's name, a dict keyed by a member's name. New.

### `use-consistent-naming` — Fail
- practice_session_output.py:232 the validate log line names the practice by `type(self.guideline).__name__`, while the action line names it by key (session_log.py:370). Left (§4).

## Judgment — `space/session/session.py`

### `eliminate-duplication` — Fail
- session.py:41 `name_of` is `Name(text).title_slug` written again (`re.sub("[^a-z0-9]+", "-", …)`). About 25 other sites convert case by hand instead of through `Name`: context_config.py:92/:99, practice_catalogue.py:97, catalog_generator.py:361/:849/:895, foundry_chrome.py:179/:1778, markdown.py:339–348/:652, installer.py:223, prompt_notify.py:308/:417/:433, agent_tools.py:921, _drawio_base.py:141, lern graph_overlay.py:248. Left (§4 slug helpers) plus new sites.

### `hold-state-on-the-object-not-in-parameters` — Fail
- session.py:406 `handoff_session(next_focus, session: str)` and :496 `record_decisions_session(session: str)` take the session's own session.json as a parameter on the Session the call was made for. New (low).

### `use-consistent-naming` — Fail
- session.py:121 `repo_from_session()` returns `repo_path`, beside `repo.root`: three names for one folder (validate.py:198/:214/:252 use the operation). New (low).

## Judgment — `space/session/session_log.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- session_log.py:366 `_line_chat` falls back to `ChatPointer.from_environment()` (chat_pointer.py:78), so a log line written for a call that named no chat points at whatever chat the server process's environment names — the "falls back to a global" case the rule describes. chat_pointer.py:78 also reads two names for one variable (`CDD_CONVERSATION_ID`, `CDD_CHAT_ID`). New.

### `no-legacy-api-after-refactor` — Fail
- session_log.py:27 `_FORMER_VERBS = {"pull": "move"}` still reads old log verbs. Left (§7).
- session_log.py:412 the agent instructions say "when bound" (also :421) (banned word). New (low).

## Judgment — `space/work_state.py`

### `no-legacy-api-after-refactor` — Fail
- work_state.py:12 `_LEGACY_SESSION_KEY = "current"` and :74 read a `current` key written before the branch and worktree keys. New.

### `use-consistent-naming` — Fail
- work_state.py:59 `release` / `release_folder` is a third name for the session folder (latest_release.py:56 and :78 then spell `.sessions/{release}` by hand). Left (§9).

## Judgment — `harness/installation/context_config.py`

### `no-legacy-api-after-refactor` — Fail
- context_config.py:10 `_LEGACY_GUIDELINES` / `_LEGACY_PRACTICE_FOLDERS` and the readers at :37, :48, :51 keep the old `guidelines.config` / `practice-folders.config` files alive. New.

## Judgment — `harness/hooks/hooks.py`

### `never-swallow-exceptions` — Fail
- hooks.py:176 `_existing_hooks` reads a malformed `hooks.json` as `{}`; `write_hooks_manifest` (:165) then writes the file back with only CDD's dispatch command, erasing the person's own hooks. The same mistake as B6 (config.json). New, high.

## Judgment — `harness/installer/installer.py`

### `never-swallow-exceptions` — Fail
- installer.py:115 `_load_state` reads a corrupt install record as `{}`; `_save_state` (:124) then overwrites it, so the list of installed files is lost and a later clean (:295) leaves them behind. New.

### `no-legacy-api-after-refactor` — Fail
- installer.py:216 `_remove_legacy_underscore_skills` still runs on every install for a layout no longer written. New (low).

## Judgment — `cdd_guidance/practices/clean_engineering/model/python/python_class_model.py`

### `never-swallow-exceptions` — Fail
- python_class_model.py:135 a `SyntaxError` falls through to `_parse_regex`, a second parser, and its partial model is returned as though it were the file's; :150 `parse_file` returns None on `SyntaxError`, so a broken file reads as an absent one. The class of mistake B23 fixed in the BDD model. New.

## Judgment — `harness/agent_tools/agent_tools.py`

### `use-exceptions-properly` — Fail
- agent_tools.py:879 `except Exception: if skip_errors: continue` drops any failure while listing members; :1663 and :1704 turn any failure resolving a provider into a prompt line and keep the tool. New.

### `use-consistent-naming` — Fail
- agent_tools.py:171 and :550 `_bound_callable` (banned word "bind"). New (low).

## Judgment — `harness/mcp/mcp_server.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- mcp_server.py:56 `_SERVING_MCP_HOST` and :59 `serving_mcp_host()` are a process-wide "current host"; agent_tools_probe.py:105–139 and installer.py:774 read it, and `restart` (:915) writes it through `sys.modules[__name__]`. New.

### `eliminate-duplication` — Fail
- mcp_server.py:37 `_SYNC_DISPATCH_TOOLS` and :44 `_LONG_CALL_TIMEOUT_SECONDS` list published tool names by hand (`repo.switch_branch`, `graph.set_overlays`, …); a renamed operation silently falls back to the 10-second limit. The operation should declare it. New.

### `use-exceptions-properly` — Fail
- mcp_server.py:489, :497, :807 skip any toolset or tool that raises anything at start-up (recorded as a skip, the host still serves); hook_server.py:361, :411, :650, :810 do the same for hooks. New.

### `use-consistent-naming` — Fail
- mcp_server.py:660 `_unbind_as_serving` (banned word). New (low).

## Judgment — `harness/agent_tools/tool_call.py`

### `use-explicit-dependencies` — Fail
- tool_call.py:37 `_sessions: ClassVar[SessionOpener]` is filled at import time by sessions.py:181 `ToolCall.open_sessions_with(CallSessions())`, so whether a call has a session depends on whether some module imported `space.session.sessions` first (commit 84c8e137 had to register it in a spec). The seam is documented in the root card; the import-time registration is the problem. New (medium).

## Judgment — `harness/graph/violation.py`

### `eliminate-duplication` — Fail
- violation.py:84 `Violation.from_saved` reads saved node rows by position (`node[1]`, `node[2]`, `node[4..6]`); graph.py:735 `Node.fact` and :190 `Edge.fact` read the same rows by position again, and node_data.py:12 reads `row[8]`. The saved-graph row layout has no one named record. New.

## Judgment — `cdd_guidance/actions/validate/graph_json_reader.py`

### `do-not-invent-parallel-object-models` — Fail
- graph_json_reader.py:50 `_violating_node` invents a third graph shape (a node dict "in the shape return_nodes answers with") built from Violations, beside the saved document (:27) and the return_nodes list (:31); the module is free functions over those dicts. New.

## Judgment — `cdd_guidance/actions/validate/validate.py`

### `eliminate-duplication` — Fail
- validate.py:22 `_GRAPH_JUDGED_FIDELITIES = {"model", "code"}` decides by fidelity name which fidelities are graph-judged; that belongs on the fidelity. New.

### `no-legacy-api-after-refactor` — Fail
- validate.py:160 falls back to `clean-engineering-violations.json`, a file nothing writes now; :164 falls back to `.context/graph.json`, and the root `.context/graph.json` is a 26 MB graph last committed 2026-11-06 15:22, before the refactor, still holding `Session.current`, `ProjectTicket`, `GuidanceCatalog`, `RuleHit`, `CliAgentBinding`, `mark_iterate_tick`, `SessionLogs`. A `graph=true` validate checks deleted code. New.

## Judgment — `harness/graph/explorer.py`

### `do-not-invent-parallel-object-models` — Fail
- explorer.py:41 `ExplorerEntry`, :84 `FilteredNode`, :128 `Member`, :177 `NodeSource` each wrap a Node and re-expose `type`, `name`, `node_id`; `FilteredNode.ancestors`/`children` and `Member.owner` are id strings. Left (§2 "explorer's *Entry family").

## Judgment — `harness/catalog_generator/catalog_generator.py`

### `eliminate-duplication` — Fail
- catalog_generator.py:265 `HeadingSection` slices markdown sections although the same file reads sections through `MarkdownText` (:147); front matter is parsed three times (catalog_generator.py:247, foundry_chrome.py:878, installation/files.py:420). New.
- catalog_generator.py:312 `GitCitation.from_checkout` runs git directly with no timeout and an inherited stdin; cdd_home.py:197, :201, :211 run git a third way. git.py:61 records that an inherited stdin hangs git under the MCP host. New.

### `no-legacy-api-after-refactor` — Fail
- catalog_generator.py:2104 the hub links `harness/harness/harness.py`, which does not exist, so the catalog's install link is broken. New.
- catalog_generator.py:573 `dump_run_request_yaml` and :1503 `Catalog.write_raw_manifests` have no callers; foundry_chrome.py:559 `_cdd_tour_panel_html`, :732 `details_block`, :1578 `approach_stage_examples_html` (marked "Deprecated") have none either. New.

### `prefer-class-operations` — Fail
- foundry_chrome.py:1 holds 71 module-level functions (operation_metrics.py 32, schema_rules.py 27, schema_edges.py 22, ddd stereotypes.py 20, lern tier_facts.py 20). Left for schema_rules/operation_metrics/tier_facts/stereotypes (§3); new for foundry_chrome.

### `use-consistent-naming` — Fail
- catalog_generator.py:442 `kit` and action_catalogue.py:60 `_kits` (17 uses each): "kit" is the word writing-guidelines.md forbids. Left (§9, prose); now in identifiers.

## Judgment — `harness/guidance/schema_map.py`

### `eliminate-duplication` — Fail
- schema_map.py:27 `fidelity_order` re-parses `## Fidelities` from the practice markdown although `PracticeGuidance.fidelities` already holds the fidelities in order. New.

## Judgment — `cdd_guidance/practices/stories/stories.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- stories.py:76 `project_folder` falls back to `Path.cwd()` (the MCP host's folder) through `getattr(self.workspace, "repo_path", None)`: B31 fixed `read_paths`, but the fallback stayed. Same fallback at language_adapter.py:765, catalog_generator.py:1232, _drawio_base.py:153. Left (B31, partly).

## Judgment — `cdd_guidance/practices/agent_bdd/agent_bdd_common.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- agent_bdd_common.py:523 reads `CDD_PROJECT`, then `Path.cwd()`, outside the one documented place (mcp_server.py:828); harness/graph/app/server.ts:17 also reads `process.env.CDD_PROJECT`. New.

### `eliminate-duplication` — Fail
- agent_bdd_common.py:546 re-implements the main-session case `Sessions.named` (sessions.py:84) leaves out. New (low).

## Judgment — `cdd_guidance/context_setup/context_setup.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- context_setup.py:217 `smoke_test(repo_path, …)`, :247 `scout_app`, :277 `complete_capture` each write their `repo_path` argument onto the shared toolset (`self.repo_path = repo_path`) for that one call. New.

### `never-swallow-exceptions` — Fail
- context_setup.py:469, :484, :545, :567 `except Exception` turn a failed request into status 0, a failed capture into None, and a missing page into a fixed wait. New.

## Judgment — `cdd_guidance/practices/ux/ux.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- ux.py:57 `ensure_javascript(practice: str, …)` chooses a practice by name from a hand list (:54) and copies `session` and `workspace` onto a new one (:65–66). Left (§12).

## Judgment — `harness/hooks/hook_daemon.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- hook_daemon.py:75 `spawn(repo, path)`, :110 `repo_port(repo)`, :116 `serve(repo)`, :150, :161 all take the repository. Left (§3).

## Judgment — `harness/graph/bound_node.py`

### `use-consistent-naming` — Fail
- bound_node.py:53 `BoundNode`, :19 `BoundChildren`, schema_edges.py:124 `_bound_nodes`, markdown.py:740 `_is_bindable` use the banned word "bind". "rows" in names: graph.py:1346 `_node_row`, :1361 `_edge_row`, approach_copy.py:36 `so_what_row`, catalog_generator.py:593 `IllustratedExampleRow`, :1058 `_fidelity_row`, foundry_chrome.py:1440 `refine_stage_row`, stories json/nodes.py:220 `_example_rows`, markdown/nodes.py:449/:467/:818, drawio/nodes.py:269 `_story_row`, `LeafNodesNotInHorizontalRowScanner`; App.tsx:75 `tick`; call-expansion.ts:248/:338 `bindings`/`bind`; guidance.py:654 "the yaml binder". New (§9 listed others, now renamed).

## Judgment — `harness/installation/files.py`

### `no-legacy-api-after-refactor` — Fail
- files.py:39 the mark aliases are used both ways: `@Hook` 34 times beside `@hook` 2; `@Mcp` 50 beside `@mcp` 91; `@Skill` 17 beside `@skill` 40. Decision 10 kept the lowercase alias as the convention; 101 decorators still use the class name, so one mark has two spellings. Left (§7).

## Judgment — `space/session/throwaway_project.py`

### `eliminate-duplication` — Fail
- throwaway_project.py:11 `ThrowawayProject` and session_board_examples.py:203 `SessionsProject` both make a temporary project and set and restore `CDD_PROJECT`; the second also writes `session.json` and `session.log` by hand (:225, :231, :240) instead of through `Sessions`. New (low).

## Judgment — `space/session/handoffs.py`

### `eliminate-duplication` — Fail
- handoffs.py:9 `_HANDOFF_STAMP` repeats `REPORT_DATE_FORMAT` (guidance.py:38); `"%Y-%m-%dT%H:%M:%SZ"` is written inline at hook_server.py:871, prompt_log.py:75, prompt_notify.py:147/:239/:261 beside `SessionLog.timestamp` (session_log.py:146). New (low).

## Judgment — `cdd_guidance/practices/stories/model/markdown/nodes.py`

### `no-legacy-api-after-refactor` — Fail
- nodes.py:925 `load_epic` and :928 `load_increment` have no callers. Left (§12). Also uncalled: markdown_class_model.py:717/:722/:734, miro_class_model.py:442 `_extract_mermaid`, ddd stereotypes.py:164 `tactical_tags`, code_story_model.py:116 `background_lines`, markdown.py:271 `_extract_fidelity_file`, project_approach.py:44/:68, design_canvas/fixture_bar.py:107, agent_bdd/__init__.py:141, agent_cli_bdd.py:478, the empty stories/model/typescript/rules/__init__.py:6 registry. Spec-only: verify_report_links.py (left §7), `Catalog.from_registry`, `McpServer.enroll_from`, `ContextConfig.set_guidelines`/`set_practice_folders`, `GuidanceAction.guidance_text`, call_graph.py:67/:76, `CanvasVersions.record_link`. New except where marked.

## Judgment — `cdd_guidance/builders/create_context_tool/create_context_tool.md`

### `no-legacy-api-after-refactor` — Fail
- create_context_tool.md:13 still names `BaseContextTool`, `@instruction` slots, `utilities/workspace/workspace_session.md`, `practices/base/`; create_practice_guidance.md:15 names `utilities/...` and `@instruction`. These are deployed as builder skills. Left (§7 "Old builder").

## Judgment — `harness/guidance_actions/guidance_actions.py`

### `limit-operation-parameters` — Fail
- guidance_actions.py:106 `session_for(call)` ignores `call` and returns the action's own session. New (low).

## Dismissed leads

- `mcp_server.py:830` reading `CDD_PROJECT`: the documented place for an in-process call.
- `throwaway_project.py` / `session_board_examples.py` setting `CDD_PROJECT`: spec support (only the duplication is reported).
- Diagnostics probes (`agent_tools_probe.py:275/363`, `guidance_probe.py:182/191/213`, `session_probe.py:72`) catching `Exception`: a probe's job is to report the failure as a red result.
- Hook handlers the dead-code scan flagged (`Installer.ensure_mcp_server_*`, `PromptLog.after_agent_response`): dispatched by their `@Hook` event. `_LabelText.handle_data`: an HTMLParser override.
- `harness/kanban` in `space/kanban/.context/story-map.md` and `cdd_claude_mod.md`: they name the `retired/` copy on purpose.
- `TicketFiles` in `clean_engineering.md`: the rule's own example.
- `session=` parsed in guidance_actions.py:122 and `session=` written by ticket-client.tsx:275 / fidelity-client.ts:147: decision 1.
- `skill = Skill` alias itself: decision 10 (only the mixed use is reported).
- `space` importing `cdd_guidance` (report.py:168, session_probe.py:40): documented in the root card.
- `Repo.current(project)` (repo.py:102): a factory from a project, not a global accessor; only the name `current` is misleading (low, not listed).
- `PracticeCatalogue._shared` (practice_catalogue.py:28): documented read-only shared instances; no caller found that changes one. Left as a watch item (§3), not a Fail.
