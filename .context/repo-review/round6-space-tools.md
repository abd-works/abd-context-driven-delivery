# Round 6: space and tools, after the round-5 fixes

Area: `space/session`, `space/repo`, `space/work_state.py`, `space/kanban` (Python and the hand-written TypeScript in `space/kanban/app/src` and `app/packages`), `tools/*`. Code read at b91a73eb on `ensure-domain-orientation-refactor`; the CDD MCP host served 8a91c49f, which has the same code. Checked against `round5-space-tools.md`.

Status words: **fixed** (round-5 finding gone, listed below, not in the table), **left** (round-5 finding still true, completely or partly), **regression**, **new** (not in round 5, in code that existed at round 5, including a pattern a round-5 fix put in place of the old one), **new scope**. No round-5 finding in this area was overturned by a fix agent with a reason, so nothing is marked **decided**.

## Graph check

One call ran and one failed.

| Call | Result |
|---|---|
| `validate.validate`, `clean-engineering-modules`, `graph: true`, absolute paths for `space/session`, `space/repo`, `space/work_state.py`, `space/kanban`, `tools` | Answered (after one "still running" reply). Report: `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-modules-20261108T081311_2.md`, graph `...081311_2.json`. 294 graph hits on 17 rules. |
| `validate.validate`, `clean-engineering-code`, same arguments, called after the first had answered | `MCP server "plugin:cdd:cdd" connection closed before the tool call was answered`. The host then reported `ECONNREFUSED`. `~/.cdd/server.log` shows `WinError 64` in the listening loop at that moment, and a zero-byte `clean-engineering-modules-20261108T081631.md` appeared in the reports folder. |

Under `.claude/rules/mcp-fail-loud.md` I stopped there and did not run validate any other way. The host needs a restart before the code call can run. What this costs: the modules report holds no `eliminate-duplication` section, so the new near-copy scanner (round-5 commit c0c7f1c8) did not run on this area. The concern 1 findings below come from the AI check alone.

### Hit counts per cross-file rule

| Rule | Hits | Confirmed |
|---|---|---|
| `one-way-deps` (file cycles inside a module) | 23 (kanban 8, repo 4, session 11) | 0, every one a false positive (see the last section) |
| `low-coupling` | 0 | – |
| `deep-module` | 0 | – |
| `missing-module-context` | 0 | – |
| module naming (`domain-nouns-only`, `no-module-per-class`) | 0 | – |
| `use-explicit-dependencies` | 8 | 0 (3 in test code, 5 parts an owner builds from its own fields, as in round 5) |
| `shape-classes-around-resources` | 1 | 0 (`BoardUpdate` and `Step`: a `Step` is one command line to run, a value, not a data bag split from its rule) |
| `prefer-instance-operations` | 10 | 0 cross-file. `Board.places_cards` is the package-import registration that breaks the board/ticket cycle, the same shape as `ToolCall.open_sessions_with`; `LogTimestamp.now` and `FormatGroup.every` are factories |
| `eliminate-duplication` (near copies) | not run: the code call failed | – |

The other hits are per-file code rules (`use-typed-signatures` 83, `avoid-vague-parameter-names` 48, `keep-classes-single-responsibility` 22, and so on), outside this round's cross-file scope, and not judged.

Two round-5 graph hits are gone, which confirms two fixes: `use-explicit-dependencies` no longer hits `Sessions` building `WorkState` (round-5 #5) or `SessionDiagnostics` building a `ToolCall` (part of round-5 #7). The three round-5 module-cycle hits on `space/repo`, which ran through harness specs, are gone too: the scanner now leaves specs out of module cycles.

## Fixed since round 5

- **#1 seven file cycles inside space modules.** Every back-import that was a function-level import is now an `if TYPE_CHECKING:` type reference or gone. repo↔worktree uses `Repo.checkout_at`; Session is made with its Sessions; the kanban package hands Board its card classes (`space/kanban/__init__.py:9`). No file in session, repo or kanban imports a sibling back at run time.
- **#2 space ↔ cdd_guidance.** `cdd_guidance` imports nothing from `space` outside specs (agent BDD reaches sessions through `ToolCall.session_in`). `space` → `cdd_guidance` runs one way (`report.py:11`, `session_probe.py:45-46`).
- **#5 two WorkStates on one `session.json`.** `Sessions._state` is `repo.own_work_state`, which in the main clone is the same object as `repo.work_state` (repo.py:261-273). Graph hit gone.
- **#6 objects rebuilt from a path the caller holds.** `CallSessions` holds one `Sessions` per project (sessions.py:221-228); `Board` asks `Sessions.of_project` (board.py:96); `FileManager.load` reads the open session's file manager (file_manager.py:136-140). The `Session.from_file` part was replaced by a `ToolCall` stand-in, reported as new finding 1.
- **#9 practice found by key string in ReportFile.** It now asks `practice_of(type(self._practice))`. The way it reaches that is new finding 4.
- **#15 TypeScript decides formats.** `FormatGroup` and `FormatChoice` (format_choice.py) answer groups, each fidelity's format and the starting picks; `tile-formats.ts` only joins what is picked.
- **#16 TypeScript decides tile standing.** `ActionStates.taken_together`, `StageWork` and `FidelityProgress.allowed_actions` (now holding Render) answer it; `tile-actions-client.ts` shows them.
- **#17 which chat works on a ticket.** `Ticket.chat` (ticket.py:268-282) decides it and sends `working_chat`.
- **#18 board server runs git and the pin itself.** `board-update.ts` runs `scripts/install.py --update`, so the pull and the pin are Python's. It still finds the repository as `appFolder/../../..`, which is minor.
- **#19 matching a backlog item to a ticket by title.** Backlog items now carry their `ticket`; the toast diff in `board-client.tsx` only shows two reads side by side.
- **#20 `followBars`.** Opens on `ticket.next` (open-card-client.ts:48-55).
- **#21** `Session.active_practices` and `Session.reset` are deleted. **#22** `Stage.requires` compares `approach_stage is self._approach`. **#24** the kanban model card names `Sessions.of_project(project).repo.main_clone`. **#25** `tools/.context/module-context.md:14` describes the draw.io viewer. **#26** `Session.work_root`; `Sessions.saved` deleted. **#27** "guideline" is "rule". **#28** `_lines_of_loop` reads `entries`. **#29** `Repo.of_project` builds one Repo; `BoardReads` replaces popping `__dict__` on Board.

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix in one line | severity |
|---|---|---|---|---|---|---|---|
| 1 | space/session/session.py:98; space/session/practice_session_output.py:56 (via harness/agent_tools/agent_tools.py:743) | 5 | AI, confirmed by an in-process run | new (the round-5 fix swapped `Sessions(project)` for a `ToolCall` stand-in; the round-5 code also lost the chat, so this is not a regression) | **Every session tool named by `session=` writes its log lines without the calling chat.** The `@tool_subject` loaders `Session.from_file` and `PracticeSessionOutput.load` build `ToolCall(project=project)` only to reach `CallSessions.named_in`, and that stand-in has no chat, so `session.chat` is None. Run through `ToolCall.sent` with `conversation_id`, `transcript_path` and `transcript_lines`, `session.mark_loop` wrote `--- 1 no-chat`, although its docstring promises the marker carries the chat's pointer. `append_log` notes lose it the same way. | Have `ToolSubjectLoader.on_subject` hand the served call to a loader that takes it, as it hands `project`, and open the session with `call.session_named(session)`; add a spec on the marker's chat pointer. | high |
| 2 | space/kanban/app/src/kanban/ticket/activation-client.ts:47, :51 vs space/kanban/ticket.py:354 | 12 | AI | new | **The switch dialog decides what leaving and opening offer, and disagrees with Python.** TypeScript offers merge whenever the leaving work has a branch (`leavingBranch !== ''`). Python's `close_choices` names the default branch when it is checked out, and `Ticket.leave` never merges the default branch. So leaving work on main offers "merge"; if picked, nothing is merged but the toast reports "merged to main" (`LEFT_STEPS`). The opening filter (branch only when missing, worktree only when none) is also TypeScript's. | Let Python answer the leave and open choices offered now, as `CloseChoices` does for closing, and have the dialog show them. | medium |
| 3 | space/session/sessions.py:131-146, :233-242; space/session/session.py:180-190, :321-325 | 5, 2 | AI | left (#3, narrowed) | `_held` and `_unopened` are gone, but one session folder still has **two Session objects**: the kept one in `Sessions.kept`, which holds the graph and practices, and the per-call one, whose chat is set by assignment after it is made. Every practice's `session` is the kept one, never the session the call opened, so code that reaches the log through a practice writes with no chat. | Keep one Session per folder in `Sessions`, and let the call carry its chat to the log line (the call, or `SessionLog.note_chat`), not a second Session object. | medium |
| 4 | space/kanban/report.py:258-263 | 5 | AI | new (from the #9 fix) | `_scanned_rules` rebuilds a whole graph from the saved graph on each report read (`restored_graph()`), or an empty one for a node list, only to ask that graph's copy of the practice which rules it checks. The report already holds its PracticeGuidance. | Ask `self._practice.checks()` and take the overlays' rules from the `SavedGraph` without restoring a graph. | medium |
| 5 | space/kanban/report.py:236-244 vs cdd_guidance/actions/validate/graph_json_reader.py:14-22; report.py:223-226 | 1, 5 | AI | left (#8, narrowed) | The graph is parsed once now, but "a list is a node list, a dict is a saved graph" is still decided in both files. `_has_newer_report` still lists and opens every earlier fidelity's reports for each ReportFile read. | One reader answers both shapes (the graph JSON reader or `SavedGraph`); let FidelityGuidance hold its latest report. | medium |
| 6 | space/session/session_diagnostics.py:21-39 | 5 | AI | left (#7, narrowed) | The `ToolCall()` fallback is gone, but a whole `Installer` is still built to reach `.diagnostics`. `call` stays optional, and `session_diagnostics` fails on the installer-listed instance, which has none. | Make the call required and hand in the project's `InstallDiagnostics`. | medium |
| 7 | space/session/session_files.py:24-45; space/session/sessions.py:62-65 | 2 | AI | left (#14, narrowed) | One session still reads files through two FileManagers named from two tops (`file_manager` from the workpath, `_from_project` from the repository), and the board lists folders through a third, `Sessions.file_manager`. | Give the session one FileManager whose roots include the repository root, and name paths from one top. | medium |
| 8 | space/kanban/board.py:97, :112, :262-265; space/kanban/ticket.py:536 | 2, 5 | AI | left (#4, narrowed) | Name lookups across the two sets are gone, but the board still holds the process-shared `PracticeCatalogue.practices()` while every session holds its own `create_all()`. `Board.practices` sends the shared ones, tickets send the session's, `works_through` matches them by `type()`, and `FidelityProgress.is_enabled` finds its practice again with `practices[self._practice.key]`. | Have the board read its practices' order and colour from the classes or one held set, and let `FidelityProgress` ask its own practice's session output. | medium |
| 9 | space/kanban/board.py:528-537 | 5, 6 | AI | left (#10) | `Help.href` still builds a `CatalogPractice` on every read, importing the catalog generator inside the function, to work out a page address. | PracticeGuidance and FidelityGuidance answer their catalog page, or the catalog publishes its page index. | medium |
| 10 | tools/prompt_notify/prompt_notify.py:43-76, :180-302 | 2, 5 | AI | left (#11, a known skip in round 5) | Still a ClassVar `_catalog` of practice, fidelity, rule and action names (a second registry), and the toast and MCP aliases still rebuilt from `tool.callable`, the MRO and `toolset.slug`. | PracticeCatalogue and ActionCatalogue answer which name a text mentions; AgentTool answers `toast` and `mcp_names`. | medium |
| 11 | tools/prompt_notify/prompt_notify.py:117-126 | 1 | AI | left (#12) | The notifier still loads every toolset itself (`RepositoryToolsets.of_running_checkout().collect()`), although the hook server has already loaded them. | Hand the notifier the hook server's loaded toolsets when it registers. | medium |
| 12 | tools/prompt_notify/prompt_notify.py:345-372 ↔ harness/hooks/hook_server.py (`rules_toast`, `TOAST_ARROW`) | 1, 6 | AI | left (#13) | `ToastFile` still takes apart the text `rules_toast` builds (arrow split, `rules :` prefix, ` rules` suffix), so the toast's format is decided in two files. | Make a toast a value (source and guidance names) that joins itself, kept beside `rules_toast`. | medium |
| 13 | space/kanban/app/src/kanban/board/practice-client.ts:28-36; ticket/tile-view.tsx:25-33; ticket/ticket-card-view.tsx:40 | 12, 10 | AI | left (#23, narrowed) | `isEnabled` and `RUN_NEXT_COMMANDS` are fixed, but `fidelityNameOf` still cuts a fidelity's name out of its slug, and `skillOf` still rebuilds the installer's skill naming (`/practices-{practice}-{slug}`). | Python sends each fidelity's display name and its skill command. | low |
| 14 | space/kanban/app/src/kanban/board/board-client.tsx:9; ticket/ticket-card-view.tsx:15; backlog-item/backlog-item-client.tsx:7; ticket/ticket-client.tsx:166 | 12 | AI | new | The page knows columns by their names ('Complete', 'Backlog', 'Implementation'), although every column sends its `kind`. | Compare `column.kind`, and let Python say which columns a card opens towards. | low |
| 15 | space/kanban/ticket.py:146-149 | 5 | AI | new | `Ticket.record` forgets its progress by popping the attribute name `"_progress"` from `__dict__`, the pattern round 5 #29 removed from Board. | Keep the ticket's reads in one held object that `record` replaces, as `BoardReads` does. | low |
| 16 | space/kanban/board.py:96, :112 | 5 | AI | new | In a linked worktree, `Board.load` passes the main clone Repo made by `checkout_at`, and `Board.__init__` then asks `Sessions.of_project(repo.root)`, which holds its own Repo for the same checkout: one board, two Repo objects for one clone. | Take the main clone's `Sessions` first and use its `repo`. | low |
| 17 | space/repo/repo.py:115-120 | 5 | AI | new | `Repo.of_project`, the subject of every repo tool, builds a new Repo (with Git, Worktrees and its own WorkState) on each call, while `CallSessions` already holds one Repo per project. In one process two WorkState objects then read and write the same `session.json`. | Hold one Repo per project in the process (as `CallSessions` holds Sessions) and let the repo tools load it. | low |
| 18 | tools/prompt_log/prompt_log.py:151-162 vs space/session/session.py:268-278 | 9, 1 | AI | new | `Session.hook_log` hands out a path in the session's `logs` folder, and `PromptLog` opens and appends to it itself, beside `Session.append_hook_log`, which does the same for `dispatch.debug`. That gives the folder two writers and two append routines. | Have the session (or a HookLog it holds) append an entry's text, and have PromptLog call it. | low |
| 19 | space/kanban/.context/session-board-scenario-realization.md:2166-2452 | 11 | AI | new | 16 lines still name `Sessions.saved` and `Session.load(session_path, repo_path)`, which the round-5 fix deleted. | Rewrite those call graphs with `Sessions.of_project(...).current()` and `Sessions.load(folder)`. | low |

## Counts

By concern (a finding with two concerns counts under both):

| Concern number | high | medium | low | total |
|---|---|---|---|---|
| 1 duplicated functionality | 0 | 3 | 1 | 4 |
| 2 duplicated shapes | 0 | 4 | 0 | 4 |
| 3 no use | 0 | 0 | 0 | 0 |
| 4 disconnected classes | 0 | 0 | 0 | 0 |
| 5 wrong-shape relationships | 1 | 7 | 3 | 11 |
| 6 seams that leak | 0 | 2 | 0 | 2 |
| 7 dependency direction / cycles | 0 | 0 | 0 | 0 |
| 8 one-class packages | 0 | 0 | 0 | 0 |
| 9 one file, several owners | 0 | 0 | 1 | 1 |
| 10 inconsistent names | 0 | 0 | 1 | 1 |
| 11 legacy and stale docs | 0 | 0 | 1 | 1 |
| 12 Python/TypeScript duplication | 0 | 1 | 2 | 3 |

By severity: high 1, medium 11, low 7 (19 findings, against 29 in round 5).

By status: fixed 19 of round 5's 29 (#1, #2, #5, #6, #9, #15-#22, #24-#29); left 10 (#3, #4, #7, #8, #10, #11, #12, #13, #14, #23); new 9; regression 0; new scope 0. The new findings that the round-5 fixes put in place of the old ones are 1 (stand-in ToolCall for `Sessions(project)`) and 4 (a restored graph to find the practice by class).

### Goal-class counts

| Goal class | Concerns | Round 5 (this area, by `concern_counts.py`) | Round 6 left | Round 6 new | Round 6 total |
|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 11 (10 + 1) | 6 | 6 | 12 |
| Shadow models | 2 | 5 | 4 | 0 | 4 |
| Duplicated functions | 1, 12 | 13 (6 + 7) | 4 | 3 | 7 |
| **Goal total** | | **29** | **14** | **9** | **23** |

The area's goal total fell from 29 to 23, a cut of 21%, just over the 20% the loop asks for. Resource orientation did not fall (11 to 12): six round-5 findings were fixed, and six new ones were found, two of them put in place by the fixes. One high finding remains in the goal classes (finding 1, concern 5).

## What would make the next round cheaper

1. **A fix that replaces one stand-in with another.** Round 5 asked to stop building `Sessions(project)` per call. The fix built `ToolCall(project=project)` instead, and the session still loses the call's chat. Neither version had a spec on the effect, the chat pointer on the log line, so nothing failed. A fix brief for a concern 5 finding should name the observable effect and require a spec that fails first on it (here: `session.mark_loop` through `ToolCall.sent` writes the chat's id).
2. **Rules moved to Python only as far as their lists.** Python now sends `leave_choices` and `open_choices`, but the page still filters them by the branch and worktree state, and that filter disagrees with `Ticket.leave`. When a rule moves out of TypeScript, Python should send what is offered now, the way `CloseChoices` does, not the full list for the page to filter. A grep of `app/src` for `.filter(choice =>` and for column names in quotes finds the remaining cases.

## Scanner false positives

- **`one-way-deps`, all 23 file-cycle hits** (kanban: backlog_item/board/ticket/leaving_handoff; repo: repo/worktree/latest_release; session: session/sessions/session_log/session_files/chat_injections/practice_session_output). Every back-edge is an `if TYPE_CHECKING:` import, which never runs: a part naming its owner's type for an annotation (SessionLog its Session, Worktree its Repo). No file imports a sibling back at run time. Scanner: `cdd_guidance/practices/clean_engineering/model/python/python_class_model.py:184`, where `import_targets` walks the whole tree with `ast.walk` and so counts imports under `if TYPE_CHECKING:`. It should skip that block, as it already must keep counting imports inside functions.
- **Test code read as production code**, across four rules:
  - `cdd_guidance/practices/clean_engineering/model/production_code.py:18-19`: `is_test_code` misses `test-utils/` folders, `*_test.py` (`story_test.py`), `*_spec.js` (`watch_notice_spec.js`), and test-support modules such as `session_board_examples.py` and `session_board_tiers.py`. So even a production-only rule, `use-exceptions-properly`, hits `story_test.py` twice.
  - These rules do not derive from `ProductionCodeRule`, so they also judge files `is_test_code` does recognise: `KeepClassesSingleResponsibility` (`model/rules_shared/class_rules.py:36`, which hits `side-panel-client.spec.ts` and `ticket-client.spec.ts`), `ProvideMeaningfulContext` (`model/rules_shared/operation_checks.py:200`, which hits `tests/support.ts` and `*.story.ui.spec.ts`), `UseExplicitDependencies` (`operation_checks.py:112`, which hits `kanban_tools_spec.py`) and `PreferInstanceOperations` (`operation_checks.py:284`, which hits four in `test-utils/`).
- **`prefer-instance-operations` on factories:** `LogTimestamp.now` makes a timestamp and `FormatGroup.every` lists the groups; both are creation factories the rule allows. Scanner: `operation_checks.py:50`, where `_STATIC_FACTORY_EXTRA_NAMES` holds only `fromRequest`.
