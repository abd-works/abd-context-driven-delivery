# Round 9: space and tools, after the round-8 fixes

Area: `space/session`, `space/repo`, `space/work_state.py`, `space/kanban` (Python and the hand-written TypeScript in `space/kanban/app/src`), `tools/*`. Code read at 5f36e6a2 on `ensure-domain-orientation-refactor`. The CDD MCP host serves the same commit. Checked against `round8-space-tools.md` and the decision records in the area: `space/kanban/.context/cdr/0001`–`0003` (0002 and 0003 updated in round 8), `space/session/.context/cdr/0001`, `tools/.context/cdr/0001`.

Status words: **fixed** (listed below, not in the table), **left**, **regression**, **new** (not in round 8, in code that existed at round 8, including a pattern a round-8 fix put in), **new scope** (found only because this round uses the code metrics as evidence for the first time), **decided** (not counted).

## Graph check

Both calls ran and answered, one at a time.

| Call | Result |
|---|---|
| `validate.validate`, `clean-engineering-code`, `graph: true`, absolute paths for `space/session`, `space/repo`, `space/work_state.py`, `space/kanban`, `tools` | One "still running" reply, then the report. 150 graph hits on 14 rules (203 on 19 in round 8). Report: `C:\Users\jeffa\.cdd\runtime\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-code-20261109T014510.md` (graph JSON beside it). |
| `validate.validate`, `clean-engineering-modules`, same paths | Four "still running" replies, then the same 150 hits. The module-level scanners (`one-way-deps`, `deep-module`, `no-module-per-class`, `low-coupling`, missing module context, module naming) found nothing. Report: `...\clean-engineering-modules-20261109T014554.md`. |

### Hits judged against the twelve concerns

| Rule | Hits now (round 8) | Confirmed | Where it went |
|---|---|---|---|
| `one-way-deps` | 0 (28) | 0 | The board page's run-time package cycle is gone (round-8 #1 fixed), and the 20 `import type` false positives are gone: the TypeScript reader now blanks erased imports (`base_class_model.py:25-58`, `_without_type_imports`). |
| `eliminate-duplication` | 0 (2) | 0 | Round-8 #6 and #7 fixed. |
| `do-not-invent-parallel-object-models` | 0 (2) | 0 | Round-8 #5 fixed; the `BoardReads` false positive no longer fires. |
| `hide-inner-details` | 3 (9) | 0 | All three read a private member of another object of the operation's own class (last section). Round 8's other five false positives are gone. |
| `prefer-instance-operations` | 4 (4) | 0 | Same four as round 8, same reasons: `Board.places_cards` is the registration that keeps board and ticket one-way; `ActionStates._together`, `Repo._marked_checkout` and `ThrowawayProject.close_all` are small pure helpers or test support. |
| `use-explicit-dependencies` | 1 (1) | 0 | `BoardPage` builds `BoardApi`: it is the page's composition root. |
| `errors-out-of-existence` | 0 (6) | 0 | The scanner now leaves a named refusal alone (`operation_semantics.py:53-66`). |

### Hits outside the twelve concerns (not counted)

`avoid-vague-parameter-names` 46, `use-typed-signatures` 38, `keep-classes-single-responsibility` 15, `limit-operation-parameters` 11, `keep-operations-small-focused` 10, `keep-operations-single-responsibility` 6, `domain-exception-carries-context` 5, `use-intention-revealing-names` 4, `never-swallow-exceptions` 3, `provide-meaningful-context` 3, `use-exceptions-properly` 1. The three swallow hits and the one `use-exceptions-properly` hit are the deliberate fallbacks round 8 named (`session_probe.py:29`, `board-store.ts:136`, `watch_notice.js:6`). The five `domain-exception-carries-context` hits are a scanner false positive (last section). The large-class counts match the metrics: `Session` 31 public operations, `TicketClient` 30, `Repo` 28, `Ticket` 21, `Board` 19.

## Code metrics as evidence

Measured with `measure_revision.measure` at 5f36e6a2. In this area, the classes above 100 total complexity or 30 methods are `Ticket` (143, 48 methods, 3 unrelated groups), `PromptNotify` (104, 30), `Session` (78, 51), `Repo` (83, 40), `Board` (59, 36, 6 unrelated groups) and `FidelityProgress` (71, 30). No function in the area has more than 20 paths; the hardest to read are `PromptNotify._catalog_match` (19), `story_test._scenario_group` (18) and `FidelityProgress.from_log` (17). The duplicated helper names in the area are `_slug` and `names_in` in `space/kanban/story_test.py`, and the class names `Scenario` and `Step` there.

What each large class's size comes from:
- **`Ticket`:** three jobs, two of them in the wrong place (finding 1).
- **`Board`:** the catalog view of its practices, searched on every call (finding 2).
- **`PromptNotify`:** reading a hook payload and classifying installed guidance paths (findings 4 and 5), plus the toast matching that `tools/.context/cdr/0001` decides.
- **`Session`:** no finding. Its 51 methods are mostly thin MCP tools (`session.write_handoff`, `session.list_cdrs` and others) that hand the work to the parts it holds (`handoffs`, `decision_records`, `log`, `session_files`). The tools stay on `Session` so their published names do not change.
- **`Repo`:** no finding counted. 13 of its 40 methods are its MCP tools and the slash-command instructions beside them. Watch `_checkout_tools_act_in` (`repo.py:283-290`): the repo tools act in another `Repo`, the open worktree's, which suggests the tool surface could be a part of its own.
- **`FidelityProgress`:** one job, how far one fidelity has got.

The duplicated helper names: `story_test._slug` is a real copy of `Name.title_snake` (finding 8). `names_in` and `Scenario`/`Step` share only a name with `class_graph.py` and the Stories model (a runner registering steps, not a story graph node), so they are not findings.

Did a round-8 fix make a metric worse? Comparing method counts and AST size at 4359b907 and 5f36e6a2, `Board` gained one method (35 to 36, `make_backlog_item`) and shrank in size. `Worktree`, `PracticeSessionOutput`, `FidelitySessionOutput`, `WorkState` and `ToastFile` all shrank. No regression.

## Fixed since round 8

- **#1 the board page's packages imported each other at run time.** The shared kit moved to `app/src/kanban/shared/` (`board-context`, `board-brand`, `board-store`, `icons`, `stage-head-view`), which imports only types from the others. `package-direction.spec.ts` checks that every run-time import goes down the layers board, ticket, chat and backlog-item, shared. A grep confirms that every upward import left is `import type`.
- **#2 the catalog's view rebuilt per call.** `Sessions.board_practices` now holds `CatalogPractice.of_practices(...)` once per checkout, with one `skill_install` (`sessions.py:64-71`), and `Board.load` hands it in (`board.py:113-117`). The board-built spec was replaced by `kanban_tools_spec.py:693-707`, which makes two `board.help` calls, a `board.show` and a `fidelity-progress.help` through `self.project.call`, and counts one `skill_install` (fix rule 9 kept).
- **#3 two classes answering a log line.** `FidelitySessionOutput` answers only `practice` and `fidelity`. `ChatLog.validation`, `action` and `guidance_action` take only `FidelitySessionOutput` (`session_log.py:347-377`), and `working_fidelity`, `working_format`, `name`, `guidance` and `folder` are gone from both classes. See finding 6 for what is left over.
- **#4 the fidelities sent twice.** `PracticeGuidance` no longer sends its fidelity slugs. `BoardFidelity` sends its `practice` (`board.py:585-589`), `PracticeClient` filters `board.fidelities` by practice key, and `practiceOf` is deleted. Specs: `kanban_tools_spec.py:657-664`.
- **#5 `Worktree._branch_name`.** `Worktree` holds its `Branch` from listing (`worktree.py:45-62`) and compares by it.
- **#6 three icons with one frame.** One `ShapeIcon` (`shared/icons.tsx:42-48`).
- **#7 `resend` and `remove`.** One `actOnTarget`, with the target chat's client held per target (`chat-client.tsx:83-112`).
- **#8 `BoardReads` reading the Board's card classes.** It now makes cards through `Board.make_ticket` and `make_backlog_item` (`board.py:205-211`, `:311`, `:324`).
- **#9 the story tier's second Sessions.** `DomainTier` uses `Sessions.of_project` (`session_board_tiers.py:57-66`), and `session_board_tiers_spec.py` checks that `Validate` acts on the session the board reads.

## Decided (not counted)

- **Round-6 #5, second half** (`space/kanban/.context/cdr/0001`): unchanged, and I still agree.
- **Round-6 #7, two file managers** (`space/session/.context/cdr/0001`): I still agree. Step 1 in `harness/installation` has still not landed: `SessionFiles` holds two `FileManager`s, and `Sessions.file_manager` is a third.
- **Round-6 #8, the board's practices against each session's** (`space/kanban/.context/cdr/0002`, updated in round 8): I agree, and the record now names where the catalog view is held.
- **Round-6 #10, #11 and #12, the prompt notifier's names and toasts** (`tools/.context/cdr/0001`): I still agree with the reason and the order of steps. This is the third round in which none of the harness steps has landed: `AgentTool` has no `toast` or `mcp_names`. The matching it leaves in `PromptNotify` (`_echo_on_toolset`, `_mcp_aliases`, `_name_matches`, `_inherited_toast`) is a large part of that class's 104 total complexity. `GuidanceAction._payload_is_this_action` (`guidance_actions.py:609-620`) matches a published name across IDE prefixes in its own way, which is the same job step 1 would give one owner.

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix in one line | severity |
|---|---|---|---|---|---|---|---|
| 1 | space/kanban/ticket.py:102-120, :243-249, :280-356, :446-466 | 5 | AI (metrics: `Ticket` total complexity 143, 48 methods, 3 unrelated groups, depends on 21 classes) | new scope | **`Ticket` does the job of its checkout and of its stage marks, beside its progress.** (a) **Its git checkout:** `branch`, `work_branch`, `worktree`, `_checked_out_work_branch`, `close_choices`, `leave_choices`, `open_choices`, `open_worktree`, `leave`, and the branch and worktree half of `activate` all reach through `self._board.repo` and `self._board.worktrees` to act on the branch named after the ticket. `branch()` builds the `Branch` again on every call, and `worktree`, `chat` and `open_choices` each call it again. (b) **Its stage marks:** `_moved_into`, `_latest_mark`, `_mark`, `_enter` and `record` read and write `moved-into`, `marked-done` and `marked-in-progress` lines by scanning `session.log.entries`. That is what the session log, or a stage-history part, should answer. | Give the ticket a held part for its checkout (its `Branch`, worktree, choices and `leave`), made once per ticket, and let a stage-marks part over the session log answer the latest move and mark. Spec it through `ticket.leave_choices` and `ticket.activate` served twice. | medium |
| 2 | space/kanban/board.py:157-182, :278-296; space/session/sessions.py:64-71 | 5 | AI (metrics: `Board` 36 methods, 6 unrelated groups) | new scope | **`Board` searches the catalog's view of its practices on every call.** `practices`, `fidelities`, `catalogued(practice)` (a search by class), `works_through` (by class), `practice(key)` (by key) and `help` each walk the list `Sessions.board_practices` holds. `FidelityProgress.help` finds its catalog practice again through `board.catalogued(self._practice)` (`ticket.py:662`). The list is held once per checkout, but nothing holds the answers, and `space/session` now imports `harness/catalog_generator` only to keep a board's list. | Hold one `BoardPractices` part per checkout, with lookups by class and by key, that the sessions keep and the board delegates to, so `Board` loses its six practice methods. | low |
| 3 | space/kanban/app/src/kanban/board/board-page.ts:63-65; board/board-client.tsx:28-43; ticket/ticket-client.tsx:54-71, :110-116 | 5 | AI | new | **The page rebuilds its client tree on every access.** `BoardPage.board` builds a new `BoardClient` each time it is read, and the code reads it in 41 places. Each `BoardClient` builds new `ColumnClient`s, `TicketClient`s and `PracticeClient`s on every getter call (`shownColumns`, `shownPractices`). `TicketClient.fidelityProgress` builds every `FidelityProgressClient` again for each `progressNamed` lookup, so `progressOn` builds the list once per fidelity it is asked for. `practiceNamed`, called per tile, builds every practice. | Have `BoardPage` hold the `BoardClient` for the current board read, made again only when `store.state.board` changes, and hold each client's children once. | low |
| 4 | harness/hooks/hook_server.py:144-150; space/session/session_log.py:31, :311-317; tools/prompt_notify/prompt_notify.py:221-243; tools/prompt_log/prompt_log.py:101 | 1 | AI (grep for the job) | new | **Four readers of "the files a tool call's input names", each with its own keys.** `HookPayload.edited_path` reads `file_path`, `path`, `uri`, `target_notebook`. `SessionLog.paths_named_by` reads six keys and `paths`. `PromptNotify._paths` reads `path`, `file_path`, `command`. `PromptLogEntry.with_tool_call` reads `path` or `file_path`. `PromptNotify._mcp_tool_name` also unwraps the tool a `CallMcpTool` wrapper names, which is another reading of the payload. A key one reader learns, the others miss. | Make the tool call (`HookPayload` or `ToolCall`) the one reader of the paths and the invoked tool its input names, and have the log, the notifier and the prompt log ask it. | low |
| 5 | tools/prompt_log/prompt_log.py:36-61; tools/prompt_notify/prompt_notify.py:34-35, :168-177, :245-247 | 1 | AI | new | **Two classifiers of installed skill and rule paths, with different IDE lists.** `LoggedFile.kind` knows `.cursor/rules`, `.cursor/skills`, `.cursor/agents` and `.agents/skills`, but not `.claude`. `PromptNotify` keeps `_SKILL_DIRS` and `_RULE_DIRS` for `.cursor` and `.claude`, and also matches `"/rules/"` anywhere in a path. `IdeLayout` (`harness/installation/ide_layout.py`) already knows each IDE's folder and where it installs skills and rules. | Let `IdeLayout` say what kind of installed guidance a path is, and have both tools ask it. | low |
| 6 | space/session/practice_session_output.py:113-118 | 3 | AI | new (put in by the round-8 fix for #3) | **`PracticeSessionOutput.working` has no production caller.** Production hands the log the fidelity's own `FidelitySessionOutput` (`GuidanceAction._worked_fidelities`, `Validate`). `working` is read only by `session_spec.py:472`, `:606` and `validate-fidelity-outputs.story.shared.py:67`, and `space/session/.context/module-context.md` describes it as API. | Have the spec and the story use `fidelity.session_output` as production does, delete `working`, and drop it from the card. | low |
| 7 | space/kanban/app/src/kanban/ticket/ticket-client.tsx:85-87; ticket/ticket-card-view.tsx:77 | 12 | AI | new | **TypeScript works out whether a stage's work has violations.** `hasViolationsIn(stage)` checks each progress's `state === 'violations'` in that stage, including practices the session does not work on. Python already answers the same question for enabled fidelities as `StageWork.has_violations` (`ticket.py:799-803`), which the page receives in `stage_work` and reads in `workIn`. The two answers can differ for a disabled practice, and for a fidelity whose state is `done` but whose latest validate left violations. | Read `ticket.workIn(stage)?.hasViolations` and delete `hasViolationsIn`. | low |
| 8 | space/kanban/story_test.py:309-310 | 1 | AI (metrics: duplicated helper name `_slug`) | new | `_slug` lower-cases a story or scenario title and joins its words with underscores. That is `Name(value).title_snake`, the conversion every published name goes through. | Use `Name(value).title_snake or "step"` and delete `_slug`. | low |
| 9 | space/session/session_probe.py:77-79 | 9 | AI | new | `SessionProbe._log_text` reads `session.log` itself, through `session.log.path`, while `SessionLog` is that file's reader (`entries`, `_lines`, `session_log.py:222-231`). | Read the log through `session.log` (its entries, or a public read of its lines). | low |

## Round-9 specifics

- **Grep the whole repository for a removed name.**
  - Kept: `BoardAppPorts`, `practiceOf`, `fidelityNameOf`, `skillOf`, `working_fidelity`, `working_format`, `_branch_name`, `_written_by_generate`, `graph_json_reader`, `TAB_GROUPS`, `FormatGroup` and the old `board/icons`, `board/board-store`, `board/board-context`, `board/board-brand` and `board/stage-head-view` paths are gone from code, specs, `.context` cards and AGENTS text in `harness`, `space`, `tools` and `cdd_guidance`. The remaining hits are:
    - `.retired/`
    - the git-ignored `space/kanban/app/.context/graph.json`
    - `harness/chat-ui/pane/test/examples/chat-bar.examples.ts:28`, a local `practiceOf` in harness upper's area
    - the off-limits `.context/repo-model.md:2180-2181`, `repo-model.drawio` and `.context/repo-runtime.md:1276-1278`, which still name `working_fidelity`, `working_format` and `_current_fidelity` on `PracticeSessionOutput`. These are for the lead and are not counted.
  - Missed: finding 6. The fix removed the old fields but left an accessor that only specs use.
- **Fixes carried to every sibling.**
  - Kept: the fidelity-list fix updated the Python data, both TypeScript readers (`PracticeClient`, `BoardClient`), the spec and `kanban-model.md`.
  - Missed: the `JsonFile` move covered `Board`, `Session`, `WorkState` and `ToastFile`, but the job of finding 4 (reading a tool input's paths) was not looked for across `tools/` and `harness/hooks`.
- **Two served calls in a row give the same answer.** Kept for #2 (`kanban_tools_spec.py:693-707`) and #9 (`session_board_tiers_spec.py`). Finding 3 is the TypeScript side of the same rule: the page has no one held client to answer twice.
- **Spec code.** The round-8 note about swapping class attributes in specs is better now: `kanban_tools_spec` uses `patch.object` as a context manager, which restores the attribute even when the spec fails.

## Counts

By concern (a finding with two concerns counts under both):

| Concern number | high | medium | low | total |
|---|---|---|---|---|
| 1 duplicated functionality | 0 | 0 | 3 | 3 |
| 2 duplicated shapes | 0 | 0 | 0 | 0 |
| 3 no use | 0 | 0 | 1 | 1 |
| 4 disconnected classes | 0 | 0 | 0 | 0 |
| 5 wrong-shape relationships | 0 | 1 | 2 | 3 |
| 6 seams that leak | 0 | 0 | 0 | 0 |
| 7 dependency direction / cycles | 0 | 0 | 0 | 0 |
| 8 one-class packages | 0 | 0 | 0 | 0 |
| 9 one file, several owners | 0 | 0 | 1 | 1 |
| 10 inconsistent names | 0 | 0 | 0 | 0 |
| 11 legacy and stale docs | 0 | 0 | 0 | 0 |
| 12 Python/TypeScript duplication | 0 | 0 | 1 | 1 |

By severity: high 0, medium 1, low 8 (9 findings, the same number as round 8, and none of them carried over).

By status, out of round 8's 9 findings:

| Status | Count | Findings |
|---|---|---|
| fixed | 9 | round-8 #1 to #9 |
| left | 0 | |
| decided | 4 records, unchanged | round-6 #5 second half, #7, #8, #10–#12 |
| regression | 0 | |
| new | 7 | findings 3 to 9 (6 put in by a round-8 fix) |
| new scope | 2 | findings 1 and 2 (the metrics used as evidence for the first time) |

### Goal-class counts

| Goal class | Concerns | Round 8 total | Round 9 left | Round 9 new | Round 9 new scope | Round 9 regression | Round 9 total |
|---|---|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 2 | 0 | 2 (findings 3, 9) | 2 (findings 1, 2) | 0 | 4 |
| Shadow models | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| Duplicated functions | 1, 12 | 3 | 0 | 4 (findings 4, 5, 7, 8) | 0 | 0 | 4 |
| **Goal total** | | **7** | **0** | **6** | **2** | **0** | **8** |

Every round-8 goal-class finding is fixed, and none came back. The total rises from 7 to 8 because this round looked in two new ways: the metrics named the large classes, and a grep for the job crossed into `tools/` and `harness/hooks`. Leaving out new scope, the comparable figure is 6, all new and all low, in code that the round-8 graph rules do not see: TypeScript getters, hook payload readers and path classifiers. No high finding remains in the three classes, and the one medium (finding 1) is new scope.

## What would make the next round cheaper

1. **When the metrics name a large class, split it by job, not by finding.** `Ticket` and `PromptNotify` have been the largest classes in the area for several rounds, and each round's fixes changed one method of them. Before a fix is closed, list the class's method groups that share no data (`classes_with_unrelated_jobs` in the metrics) and ask which group belongs to a part the class should hold.
2. **Grep for the job in `tools/`, `harness/hooks` and the TypeScript clients, and check that every new accessor has a production caller.** Findings 4, 5 and 7 are jobs done in two or more places that a search for the literal keys (`"file_path"`, `"/skills/"`, `'violations'`) finds at once. Finding 6 is an accessor that a fix added only for its own spec.

## Scanner false positives

- **`hide-inner-details`, 3 hits:**
  - `ticket.py:394` (`moved._enter`)
  - `ticket.py:427` (`reopened._enter`)
  - `ticket.py:749` (`states._states` in a classmethod over `every: list[ActionStates]`)

  Each reads a private member of another object of the operation's own class. Round 8's fix taught the Python reader the class itself, its parameters typed as it, and locals it builds. It still misses a local assigned from a call whose return type is the own class (`self._board.ticket_of(...) -> Ticket`) and a loop variable over a `list[OwnClass]` parameter. Scanner: `cdd_guidance/practices/clean_engineering/model/operation_metrics.py:418` (`self._own.names()`).
- **`domain-exception-carries-context`, 5 hits:** `repo.py:213`, `:292`, `:356`, `:407` and `sessions.py:207`. Each raises a named refusal, such as `CommitPathsRequiredError()`, whose own `__init__` passes the message to `super().__init__`, and a missing argument has no rejected value to carry. The fact `exception_without_message` looks only at the arguments at the `raise`, not at the exception class's constructor. Scanner: `cdd_guidance/practices/clean_engineering/rules/operation_semantics.py:86-88`. It should pass a named exception whose class gives its own message.
- **Metrics `shadow_models`:** `Scenario` and `Step` in `space/kanban/story_test.py` share only a name with the Stories practice's model: one registers a scenario's steps to replay, the other is a story graph node. **Metrics `function_clones`:** `names_in` in `story_test.py` and in `clean_engineering/rules/class_graph.py` share only a name. In `.context/repo-review/measure_revision.py:487-493` and `:505-510`, a name repeated across modules is counted as a copy without comparing what the two do.
