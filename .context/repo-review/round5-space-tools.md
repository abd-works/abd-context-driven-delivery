# Round 5: space and tools, concerns that span files

Area: `space/session`, `space/repo`, `space/work_state.py`, `space/kanban` (Python and the hand-written TypeScript in `space/kanban/app/src` and `app/packages`), `tools/*`. Code read at d71e0b20 on `ensure-domain-orientation-refactor`.

## The graph check did not run: the CDD MCP host kept dropping

The graph-rule check, the first of this round's two checks, did not run. Under `.claude/rules/mcp-fail-loud.md` I stopped after these failures and did not run validate any other way:

| Call | Result |
|---|---|
| `validate.validate` (`clean-engineering-modules`, `graph: true`, all four area folders) | `MCP server "plugin:cdd:cdd" connection closed before the tool call was answered` |
| same, `space/session` only | `MCP server "plugin:cdd:cdd" is not connected` |
| `cdd_ping` | first `not connected`; after the host reconnected, `pong` |
| same, `space/repo` only (the smallest module), three times | "still running", then `The operation timed out.`, then `ECONNREFUSED` |
| same, `space/repo`, after a second reconnect | "still running", then `connection closed before the tool call was answered` |

`~/.cdd/server.log` shows a run of `ClientDisconnect` and `WinError 64` errors in the listening loop at those times. The validation-reports folder has zero-byte modules and code reports from 20:37 to 20:45, mine and other agents' together, which points to the other validation agents' graph runs loading the host at the same moment. The host needs a restart, or the six agents' graph calls need to take turns, before the graph check can run on this area. The saved graph JSON files in the reports folder are from round 4 (before the refactor) or cover other areas, so I did not use them.

Every finding below comes from the **AI check**: I read the files side by side, together with what they import and what imports them. "Graph rule" appears in no row. The "Scanner false positives" section at the end is empty because no hits came back.

Status: **new** = not in `repo-review/space-tools.md`; **left** = in that review and still true; **known skip** = listed in `.sessions/ensure-domain-orientation-refactor/pending-skipped-reshaping.md`.

## What the refactor fixed (checked, not findings)

- Repo holds `git` and `worktrees` (repo.py:111-113). `main_clone` and `work_state` are found once (repo.py:243-256). LatestRelease reads `repository.work_state` (latest_release.py:35). Worktree keeps the Worktrees that listed it and closes through it (worktree.py:92-97). Review entries 1, 2, 5, 6, 7, 16 and 22.
- Session holds `handoffs`, `decision_records` and `context_config`. `_move_folder_to` returns `self`. Entries 38, 39, 40 and 56.
- Board caches `tickets`, `backlog_items` and `worktrees`, and `reread()` forgets them. Stage asks `board.wip_limit` / `set_wip_limit`, and the board is now the only reader and writer of `_board.json`. Ticket caches `_progress`. FidelityProgress reads `ReportFile.from_fidelity(fidelity)`. Entries 73, 74, 82, 86, 88, 98 and 105.
- `LogTimestamp` is a value type; Card, PromptLogEntry, PromptNotify and ToastFile no longer touch SessionLog (entries 83, 117, 124, 126). PromptLog writes through `payload.session` (entry 114).
- `Report.violation_count` and `Column.kind` are data fields, and the TypeScript reads them (entries 130 and 131).
- ActionInspector is deleted. The sub-agent fixtures moved to `tools/sub_agent/fixtures/`. `Loop.inject` and `SessionLog.append_chat` are gone.
- `harness/` imports nothing from `space/`, `tools/` or `cdd_guidance/` (grep of every non-spec file).

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix in one line | severity |
|---|---|---|---|---|---|---|---|
| 1 | space/repo/worktree.py:236 ↔ repo.py:15; space/session/session.py:112,136 ↔ sessions.py:16; practice_session_output.py:56 ↔ session.py:226; file_manager.py:140 ↔ sessions.py:15; kanban/board.py:155,161,175,205 ↔ ticket.py:14; backlog_item.py:12-13 ↔ ticket.py:350 | 7 | AI | new | **7 import cycles between files inside these modules**, each kept alive by an import inside a function with a `# WHY:` comment instead of a one-way design. Examples: repo↔worktree, session↔sessions, board↔ticket↔backlog_item. | Put each pair's shared types in the lower file, or have the owner hand the object in (Sessions hands Session its Sessions; Board hands Ticket its factory), so neither file imports the other back. | high |
| 2 | space/session/session_probe.py:311-312, kanban/report.py:237 ↔ cdd_guidance/practices/agent_bdd/agent_bdd_common.py:543 | 7 | AI | new | **space and cdd_guidance import each other.** Space imports Generate, Validate and `graph_json_reader`, and agent BDD imports `space.session.sessions`. The root module card says this outright ("space and cdd_guidance depend on each other"), but it is still a cycle between two areas. | Move `violations_by_rule`/`violations_from_graph_json_files` onto `SavedGraph` in harness. Have SessionProbe receive its actions from the installer instead of importing them, or have agent BDD receive its Sessions. | high |
| 3 | space/session/session.py:271-272, :391-396, :408-415, :540 | 5, 2 | AI | new | `Session._held` is a process-wide ClassVar dict that stands in for an owner, because a Session is read again on every call. `_new_graph` wraps each practice in `PracticeSessionOutput(practice, kept)` around **a second Session object** (`_unopened`), and `Session.practices` wraps the same guidance again in `PracticeSessionOutput(guidance, self)`. Each practice gets two PracticeSessionOutputs on two Sessions, and the copy built without `sessions` builds its own `Repo` (session.py:280). | Let `Sessions` (or the ToolCall's session opener) hold the graph per session folder, and make one PracticeSessionOutput per practice that the graph and the session both read. Drop `_unopened`. | medium |
| 4 | space/kanban/board.py:96 vs session.py:400; ticket.py:144-147 | 5, 2 | AI | new | **The board and the session hold two sets of practice instances.** The board holds `PracticeCatalogue.practices()` (the process-shared set) and the session's graph holds `create_all()`. Every fidelity a Stage requires has to be looked up again in the ticket's session by key and name string (`Ticket._own`), and the same lookup runs for every progress read. | Have the board's stages require fidelities by stage alone and let each ticket read its own session's fidelities, or hold one practice set per board and session. | medium |
| 5 | space/session/sessions.py:49 vs space/repo/repo.py:251-256 | 9 | AI | left (shared finding, narrowed) | **Two `WorkState` objects on one `.sessions/session.json`** in the main clone: `Sessions._state` writes `session`, and `repo.work_state` writes `branch` and `worktree`. The repo card promises "the repository's state has one owner". In a linked worktree the split is intended. | Have `Sessions` use `repo.work_state` when the checkout is the main clone and keep its own WorkState only for a linked worktree, or give WorkState one owner that hands both views out. | medium |
| 6 | space/kanban/board.py:102-105; session.py:280, :314; sessions.py:185; session/file_manager.py:142 | 5 | AI | left (entries 23, 33, 72) / known skip (FileManager.load) | **Objects rebuilt from a path that a caller already holds**, 5 places. `Board.sessions` builds `Sessions(self._repo.root)`, which runs `Repo.of_project` again (two more Repos) although the board holds its Repo. `Session.from_file` and `CallSessions.saved_in` build Sessions per call. `FileManager.load` builds `Sessions(project).saved` instead of using the call's session, so that session has no chat. | Add `Sessions(repo)`, pass the held Repo from Board and Session, and make the file manager reachable from the served call's session. | medium |
| 7 | space/session/session_diagnostics.py:23, :39 | 5 | AI | left (entries 66, 67) | `call or ToolCall()` gives `Installer(repo=None)` when no call is passed, and a whole Installer is built only to reach `.diagnostics`. | Require the call, and pass in the project's `InstallDiagnostics`. | medium |
| 8 | space/kanban/report.py:247-250 and :242 (via graph_json_reader.py:27-29); report.py:221-224 | 1, 5 | AI | new | **ReportFile parses its saved graph twice per read**: once with `SavedGraph.from_text` in `_scanned_rules`, and once with `SavedGraph.from_document` inside `violations_from_graph_json_files`, which repeats the same "a list means violating nodes" check. `_has_newer_report` also lists and opens every earlier fidelity's reports again on each read. | Hold one `SavedGraph` per ReportFile and ask it for hits and checks. Let FidelityGuidance hold its latest report. | medium |
| 9 | space/kanban/report.py:250 | 5 | AI | known skip (graph.practice by name) | `restored_graph().practice(self._practice.key)` finds the practice by its key string. | Have the restored graph answer for the PracticeGuidance it is handed. | medium |
| 10 | space/kanban/board.py:461-469 | 5, 6 | AI | left (entry 84) | `Help.href` builds a `CatalogPractice` (from the catalog generator) on every read to work out a page address. | PracticeGuidance and FidelityGuidance answer their catalog page, or the catalog publishes its page index. | medium |
| 11 | tools/prompt_notify/prompt_notify.py:52-79, :182-304 | 2, 5 | AI | known skip (second registry; toast/mcp_names on AgentTool) | Still a ClassVar `_catalog` of practice, fidelity and action names (a second registry), and toast and MCP-alias facts rebuilt from `tool.callable`, the MRO and `toolset.slug`. | PracticeCatalogue and ActionCatalogue answer which name a text mentions; AgentTool answers `toast` and `mcp_names`. | medium |
| 12 | tools/prompt_notify/prompt_notify.py:120-128 | 1 | AI | left (entries 120, 121; narrowed) | The notifier loads every toolset of the checkout itself with `RepositoryToolsets(_CDD_CHECKOUT).collect()`, although the hook server has already loaded them. It no longer builds an Installer. | Hand the notifier the hook server's loaded toolsets when it registers. | medium |
| 13 | tools/prompt_notify/prompt_notify.py:347-374 ↔ harness/hooks/hook_server.py (`rules_toast`, `TOAST_ARROW`) | 1, 6 | AI | new | ToastFile takes apart the toast text that `rules_toast` builds (arrow split, `rules :` prefix, ` rules` suffix), so the toast's format is decided in two files. | Make a toast a value (source and guidance names) that joins itself, kept beside `rules_toast`. | medium |
| 14 | space/session/session_files.py:37-62 | 2 | AI | left (entry 64, reshaped) | **One session reads files through three FileManagers**: the session-roots one, `_from_project` (repository root plus roots) and `sessions.file_manager` for `find`. | Give the session one FileManager whose roots include the repository root, and name paths from one top. | medium |
| 15 | space/kanban/app/src/kanban/ticket/tile-formats.ts:19-52; board/board-brand.ts:29-33; ticket/files-panel-client.ts:6-8 | 12, 2 | AI | new (open item P-3) | **TypeScript decides formats.** `FORMAT_GROUPS` is a TypeScript-only registry of formats into diagram, markdown and code. `chipFormat` picks each fidelity's format ("its default when the group holds it"), and `defaultPicks` decides that a tile opens on the defaults unless that output already exists. | Python sends each fidelity's format groups and the formats a tile starts with; TypeScript shows them. | medium |
| 16 | space/kanban/app/src/kanban/ticket/tile-actions-client.ts:27-37, :55-61, :87-91 | 12 | AI | new | **TypeScript decides tile standing.** `standingOf` says an action is done on a tile only when every fidelity has it done. `validateFaceOf` sums the violations. `canRun` refuses render until some output exists, a rule Python's `allowed_actions` does not hold. | Add render to `FidelityProgress.allowed_actions`, and have Python answer a tile's combined standing (or one progress per tile). | medium |
| 17 | space/kanban/app/src/kanban/chat/chat-client.tsx:13-20, :65-68; board/board-page.ts:72-74 | 12 | AI | new | Which chat works on which ticket (worktree folder prefix, then chat name equals ticket name) is decided only in TypeScript; Python has no such rule (harness/chat). | Have Ticket (or Chat) answer the ticket's chat in Python and send it as a data field. | medium |
| 18 | space/kanban/app/src/session-board/board-update.ts:47-74 | 12, 1 | AI | new | The board server runs `git pull --ff-only` and `scripts/install.py --pin-runtime` itself. That repeats `Repo.pull` and the installer's pin outside Python, finds the repository as `appFolder/../../..`, and skips the RepoConnectError path. | Expose one Python operation (Repo plus installer) for "update to latest" and have the board server call it through cdd. | medium |
| 19 | space/kanban/app/src/kanban/board/board-client.tsx:9-17, :93-113 | 12 | AI | new | `announcementsSince` and `returnsSince` work out moves, done fidelities and returns to the Backlog by comparing two board reads and **matching a backlog item to a ticket by title**. The session log already records each move. | Have Python send the recent log events (moves, reviews, returns) and let the page announce them. | medium |
| 20 | space/kanban/app/src/kanban/ticket/open-card-client.ts:48-50 | 12, 1 | AI | new | `followBars` picks "the first fidelity in the stage that is not done", a near copy of `Ticket.next_fidelity` with a different rule: it ignores earlier stages and reads disabled practices from a filtered list. | Open the bar on `ticket.next`. | medium |
| 21 | space/session/session.py:343-345, :552-555 | 3 | AI | new | `Session.active_practices` and `Session.reset` have no production caller; only session_spec.py and the session sketch use them. | Delete both with their specs. | low |
| 22 | space/kanban/board.py:356 | 5 | AI | new | `Stage.work_required` compares `fidelity.stage == self._approach.name`, a stage name string, although the stage holds its ApproachStage. | FidelityGuidance holds its ApproachStage (also a known skip for CatalogFidelity); compare the objects. | low |
| 23 | space/kanban/app/src/kanban/board/practice-client.ts:24-31; ticket/ticket-client.tsx:164-166, :289 | 12, 10 | AI | new | `fidelityNameOf` cuts a fidelity's name out of its slug, and `skillOf` rebuilds the installer's skill-naming rule (`/practices-{practice}-{slug}`). `isEnabled` repeats Python's `enabled` default (`?? true`). `RUN_NEXT_COMMANDS` maps only validate, so any other next step would send `undefined`. | Python sends each fidelity's name and skill command, and its next-step command. | low |
| 24 | space/kanban/.context/kanban-model.md:589 | 11 | AI | new | Says the board reads `checkout_folder` and `primary_root()`. It now reads `Repo.of_project(project).main_clone`. | Update the card. | low |
| 25 | tools/.context/module-context.md (whole card) | 11 | AI | new | `tools/drawio_viewer` is not on the card, though `cdd_guidance/rules/drawio-viewer.md:10` runs it. Its `DrawioFiles` is also a one-class module with no `.context`. | Add it to the card (purpose, seam, the rule that starts it). | low |
| 26 | space/session/session.py:377-381 vs repo.py:108, sessions.py:45; sessions.py:116-148 | 10 | AI | new | Two words for one thing in two places. `root` is the workpath on Session but the checkout's top on Repo and Sessions. `Sessions.saved` and `Sessions.current` return the same session. | Rename `Session.root` to `work_root` (or similar) and keep one of `saved`/`current`. | low |
| 27 | tools/prompt_notify/prompt_notify.py:72, :173-178 | 10 | AI | new | "guideline" names a practice's rule file, where the rest of the repository says rule. | Say rule. | low |
| 28 | space/session/session_log.py:319-326 | 1 | AI | left (entry 43) | `_lines_of_loop` parses every line into a LogEntry again instead of reading `entries`. | Read `entries`. | low |
| 29 | space/repo/repo.py:117-122; space/kanban/board.py:180-183 | 5 | AI | new | `Repo.of_project` builds two Repos to find the checkout. `Board.reread` forgets its cached reads by popping attribute name strings from `__dict__`. | Find the checkout before building one Repo; keep the board's reads in one held object that `reread` replaces. | low |

## Counts

By concern (a finding with two concerns counts under both):

| Concern | high | medium | low | total |
|---|---|---|---|---|
| 1 duplicated functionality | 0 | 5 | 1 | 6 |
| 2 duplicated shapes | 0 | 5 | 0 | 5 |
| 3 no use | 0 | 0 | 1 | 1 |
| 4 disconnected classes | 0 | 0 | 0 | 0 |
| 5 wrong-shape relationships | 0 | 9 | 2 | 11 |
| 6 seams that leak | 0 | 2 | 0 | 2 |
| 7 dependency direction / cycles | 2 | 0 | 0 | 2 |
| 8 one-class packages | 0 | 0 | 0 | 0 (drawio_viewer noted in #25) |
| 9 one file, several owners | 0 | 1 | 0 | 1 |
| 10 inconsistent names | 0 | 0 | 3 | 3 |
| 11 legacy and stale docs | 0 | 0 | 2 | 2 |
| 12 Python/TypeScript duplication | 0 | 6 | 1 | 7 |

By severity: high 2, medium 18, low 9 (29 findings). By status: new 20, left 7, known skip 2 (#9 and #11; the FileManager.load part of #6 is also a known skip, but #6 is counted as left).

## Scanner false positives

None to report. The graph check did not run (see the first section), so no scanner hits came back to confirm or dismiss.

## Graph check (run after the round)

Run one call at a time on the same CDD MCP host, after the round, with `graph: true` and absolute paths for `space/session`, `space/repo`, `space/kanban` and `tools`. Reports, under `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\`:
- `clean-engineering-modules-20261108T020718.md` (with its `.json`)
- `clean-engineering-model-20261108T021057.md`

Both reports hold the same 285 graph hits, with the same count for every rule. The graph section is built from the whole Clean Engineering practice, not from the fidelity, so `clean-engineering-code` was not run: it would repeat the same scan.

### Hit counts per cross-file rule

| Rule | Hits | Confirmed |
|---|---|---|
| `one-way-deps` | 3 | 0 |
| `low-coupling` | 0 | – |
| `deep-module` | 0 | – |
| `eliminate-duplication` | 0 | – |
| `missing-module-context` | 0 | – |
| module naming (`domain-nouns-only`, `no-module-per-class`, `use-consistent-naming`) | 0 | – |
| `do-not-invent-parallel-object-models` | 0 (AI-only rule, no scanner) | – |
| `use-explicit-dependencies` | 19 | 2 |

The other 263 hits are per-file code rules (`use-typed-signatures` 83, `avoid-vague-parameter-names` 48, and so on). They are outside this round's cross-file scope and were not judged.

### Findings now marked both

- **#5 (two WorkStates on one `session.json`): both.** `use-explicit-dependencies` hit `space/session/sessions.py:35`: `Sessions` builds `WorkState(self.root)` (sessions.py:49) instead of being handed the repository's `work_state`.
- **#7 (`call or ToolCall()` in SessionDiagnostics): both.** `use-explicit-dependencies` hit `space/session/session_diagnostics.py:17`: it builds a `ToolCall` inside its constructor (:22).

### Confirmed new findings

None. The graph found nothing in this area that the AI check had missed. The graph also missed the AI's findings #1 (seven cycles between files inside a module) and #2 (space ↔ cdd_guidance). It measures cycles between folders, and it counts specs in the same way as production code, so these real cycles disappear among the spec-made ones.

### Dismissed hits and scanner false positives

- **`one-way-deps`, 3 hits on `space/repo`** ("repo imports agent_tools / installation / mcp, which imports back through a cycle of 47 modules"). This is a false positive. No production file in `harness/` imports `space/`, `tools/` or `cdd_guidance/`. The way back runs only through harness specs (`harness/hooks/hook_spec.py:35`, `harness/guidance_actions/guidance_actions_spec.py:47` and others). Scanner: `cdd_guidance/practices/clean_engineering/model/graph_reading.py:52` adds `dependsOn` edges for spec files, and `cdd_guidance/practices/clean_engineering/rules/practice_wide_rules.py:30` reports the cycle.
- **`use-explicit-dependencies`, 17 dismissed:**
  - **9 for building a `Path`** (Worktree, DecisionRecords, FileManager, Handoffs, SessionProbe, ThrowawayProject, DrawioFiles, Granola, ToastFile). A `Path` is a value, not a collaborator. Scanner: `cdd_guidance/practices/clean_engineering/model/rules_shared/operation_checks.py:97-104`.
  - **3 in spec or test support:** `kanban_spec.py:25` SessionsFolder, `kanban_tools_spec.py:119` ProjectTools, `app/test-utils/behavior-test/cdd-project.ts:15` CddProject. The rule runs on test code.
  - **1 in a behaviour-test tier:** `session_board_tiers.py:113` CddTools builds `McpServer`. This is the test tier's own server. Same cause as the test-code hits.
  - **4 parts the owner composes from its own fields:**
    - `Repo` builds `Git(self.root)` (repo.py:111)
    - `Session` builds `ContextConfig` (session.py:82)
    - `SessionLog` builds `InjectedRules(self)` (session_log.py:184)
    - `BoardPage` builds `BoardApi` from its own store (board-page.ts:56, the page's composition root)

    A held part made from the owner's own fields is the shape the round asks for, not a hidden dependency.
- No other hits. The 285 total matches the sum of the rule sections.
