# Round 8: space and tools, after the round-7 fixes

Area: `space/session`, `space/repo`, `space/work_state.py`, `space/kanban` (Python and the hand-written TypeScript in `space/kanban/app/src`), `tools/*`. Code read at 4359b907 on `ensure-domain-orientation-refactor`. The CDD MCP host serves the same commit. Checked against `round7-space-tools.md` and the decision records in the area: `space/kanban/.context/cdr/0001`–`0003` (0002 and 0003 rewritten in round 7), `space/session/.context/cdr/0001`, `tools/.context/cdr/0001`.

Status words: **fixed** (listed below, not in the table), **left**, **regression**, **new** (not in round 7, in code that existed at round 7, including a pattern a round-7 fix put in), **new scope** (found only because the graph check ran here for the first time with every Clean Engineering rule switched on), **decided** (not counted).

## Graph check

Both calls ran and answered. This is the first round in which the graph rules judged this area since round 5.

| Call | Result |
|---|---|
| `validate.validate`, `clean-engineering-code`, `graph: true`, absolute paths for `space/session`, `space/repo`, `space/work_state.py`, `space/kanban`, `tools` | Four "still running" replies, then the report. 203 graph hits on 19 rules. Report: `C:\Users\jeffa\.cdd\runtime\.sessions\ensure-domain-orientation-refactor\validation-reports\clean-engineering-code-20261108T163937.md` (graph JSON beside it). |
| `validate.validate`, `clean-engineering-modules`, same paths | Eight "still running" replies, then the same 203 hits: the graph report is per practice, so the module-level scanners (`deep-module`, `no-module-per-class`, `low-coupling`, missing module context, module naming) ran and found nothing. Report: `...\clean-engineering-modules-20261108T164530.md`. |

No spec file was hit; the round-6 spec-reading false positive stays fixed.

### Hits judged against the twelve concerns

| Rule | Hits | Confirmed | Where it went |
|---|---|---|---|
| `one-way-deps` | 28 | 8 (package cycles in the board page) | Finding 1. The 20 file cycles inside `board/` and `ticket/` are false positives (last section). |
| `eliminate-duplication` | 2 | 2 | Findings 6 and 7 |
| `do-not-invent-parallel-object-models` | 2 | 1 | Finding 5. `BoardReads` "copies `_board` of `Card`" is a false positive. |
| `hide-inner-details` | 9 | 1 | Finding 8. The other 8 read a private member of an object of the operation's own class (false positive, last section). |
| `prefer-instance-operations` | 4 | 0 | `Board.places_cards` is the package registration that keeps board and ticket one-way (decided in round 6); `ActionStates._together`, `Repo._marked_checkout` and `ThrowawayProject.close_all` are small pure helpers or test support. |
| `use-explicit-dependencies` | 1 | 0 | `BoardPage` builds `BoardApi` in its constructor: it is the page's composition root, the one place that wires the page. |

### Hits outside the twelve concerns (not counted)

`use-typed-signatures` 47, `avoid-vague-parameter-names` 46, `keep-classes-single-responsibility` 16, `limit-operation-parameters` 11, `keep-operations-small-focused` 10, `keep-operations-single-responsibility` 6, `errors-out-of-existence` 6, `domain-exception-carries-context` 5, `use-intention-revealing-names` 4, `never-swallow-exceptions` 3, and one each of `use-exceptions-properly`, `state-change-returns-record-or-named-failure`, `provide-meaningful-context`. These are clean-code hits on single functions. The large-class counts are the ones to watch: `Session` 31 public operations, `TicketClient` 30, `Repo` 28, `Ticket` 21, `Board` 17. The three swallow hits are deliberate fallbacks, each saying why: the session probe reports a failure red rather than raising (`session_probe.py:28`), saved layout in browser storage (`board-store.ts:136`), and a half-written toast file (`watch_notice.js:6`). The six `errors-out-of-existence` hits are named domain errors for a missing tool argument (`CommitPathsRequiredError` and others), which `domain-exception-carries-context` asks for. The two rules pull opposite ways on the same `raise` (see last section).

## Fixed since round 7

- **#1 two owners for a nested generate.** `FidelityProgress._written_by_generate` and `LogEntry.tool_called` are deleted with their four examples (`ticket.py:483-497`, `session_log.py`). A comment points at the one owner, `GuidanceAction.log_running`. A grep of `space`, `tools`, `harness` and `cdd_guidance` finds no copy left.
- **#2 "a list is a node list, a dict is a saved graph" in two files.** `cdd_guidance/actions/validate/graph_json_reader.py` is deleted. `SavedGraph.from_file` (`harness/graph/saved_graph.py:185-194`) is the one reader of both shapes. `ReportFile._checked_graph` now answers a `SavedGraph`, and its three `isinstance(checked, list)` branches are gone (`report.py:234-252`). `Violation.by_rule` is the one grouping.
- **#4 `fidelityNameOf` and `skillOf`.** Both are deleted from `practice-client.ts`. `Board.fidelities` sends one `BoardFidelity` per fidelity with its `label` (`CatalogFidelity.label`) and `skill` (`CatalogPractice.skill_of`, which uses the installer's own naming) (`board.py:168-187`, `:567-591`). The tile, card and help views show those fields. Specs: `kanban_spec` "sent with UX chosen" and `ticket-client.spec.ts` "should name a fidelity's tile as the catalog names it". `cdr/0003` is now marked done.
- **#5 file order decided in both languages.** `TAB_GROUPS`, `tabOrderOf` and `FormatGroup` are deleted. `offeredTabs` follows the order Python sends. `kanban_tools_spec` checks that order through the served tool `fidelity-progress.files`.
- **#6 one Session per project folder, not per checkout.** `CallSessions.of_project` keys by `Repo.of_project(project).root` (`sessions.py:231-240`). Three specs drive it through `ToolCall.sent`: a subfolder, a `session.json` with no project, and `Sessions.of_project` from a subfolder (`session_log_spec.py:61-79`). This is the second-name check the round-7 advice asked for. Session also gained a lock so two chats asking at once make one graph, with a spec (`session_spec.py:1160-1197`).
- **#7 stale session sketch.** `session-sketch.md:479-485` now says "one object for every call, from any chat" and adds the subfolder example.

## Decided (not counted)

- **Round-6 #5 second half** (`space/kanban/.context/cdr/0001`): unchanged, and I still agree. Another process can write a newer report at any time.
- **Round-6 #7 two file managers** (`space/session/.context/cdr/0001`): I still agree. Step 1 belongs to `harness/installation` and has not landed: `SessionFiles` still holds two `FileManager`s, and `Sessions.file_manager` is a third (`session_files.py:26-43`, `sessions.py:72-74`). The record still gives the right order.
- **Round-6 #8 the board's practices against each session's** (`space/kanban/.context/cdr/0002`, rewritten): I agree. Round 7 deleted the catalogue's shared instances, so the board's set is now made once per checkout (`Sessions.board_practices`, `sessions.py:64-69`), and `kanban_spec` checks that it is not a session's. See finding 2 for where it is held.
- **Round-6 #10, #11 and #12, prompt notifier names and toasts** (`tools/.context/cdr/0001`): I still agree. None of the three harness steps has landed: `PracticeCatalogue` and `ActionCatalogue` publish no "names a text mentions", `AgentTool` has no `toast` or `mcp_names`, and `rules_toast` is still text. So `PromptNotify._practice_names` still joins `{practice.slug}-{fidelity.slug}` itself (`prompt_notify.py:57-68`). Round 7 changed it to `PracticeCatalogue.create_all()`, held once per process in the `_catalog` class variable, which is fine.

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix in one line | severity |
|---|---|---|---|---|---|---|---|
| 1 | space/kanban/app/src/kanban/board/* ↔ ticket/*, chat/*, backlog-item/* (e.g. `board/board-page.ts` imports `ticket/ticket-client`, `ticket/tile-view.tsx` imports `board/board-context`, `board/icons`) | 7 | graph (`one-way-deps`, 8 package hits) | new scope | **The board page's packages import each other at run time.** `board/` is both the page's composition root and the shared kit. `board-page.ts` and `board-view` wire every ticket, chat and backlog-item client and view. Every other package imports `useBoard`, `icons`, `board-brand` and `board-store` back from `board/`. These are value imports, not `import type`, so they are real cycles of 4 packages. No run-time fault follows; it is a structural cycle. | Move the shared kit (`board-context`, `board-brand`, `icons`, `board-store`'s types and `EMPTY_DRAFT`) into a lower package that imports none of the others, so `board/` only composes. | high |
| 2 | space/kanban/board.py:110-115, :182-187; space/kanban/ticket.py:662; space/kanban/kanban_spec.py:229-251 | 5 | AI | left (round-7 #3, narrowed; the fix rule "specs take the live path" was missed) | `Help` now gets a held `CatalogPractice`, but it is held on a `Board`, and `Board.load` makes a new Board for every tool call. So each `board.show`, `board.help` and `fidelity-progress.help` still builds one `CatalogPractice` per practice, a `CatalogFidelity` per fidelity, and a new `FileInstallation` from `skill_install()`. `board.show` now does this every time, because `Board.fidelities` is a data field. The spec "asked for help on its practices several times" counts `skill_install` on one Board built directly, so it passes while the served path builds them per call. The practices were moved to `Sessions.board_practices` so that something held them, but the catalog's view of them was not moved with them. | Hold the catalog's view with the board's practices: one list of `CatalogPractice` per checkout, beside `board_practices`, or a board held per checkout. Rewrite the spec to call `board.help` twice through `McpServer.answer_tool` and count one `skill_install`. | low |
| 3 | space/session/practice_session_output.py:117-127 and :211-238; space/session/session_log.py:347-370 | 1 | AI | new (put in by the round-7 harness-core fix "the fidelity a call works at off the shared practice") | **Two classes answer "what did this action work on" for a log line.** `FidelitySessionOutput` gained `name`, `guidance`, `folder`, `working_fidelity` and `working_format` so that it can stand in for a `PracticeSessionOutput` in `ChatLog.validation`, `action` and `guidance_action`, whose parameters are now `PracticeSessionOutput \| FidelitySessionOutput`. The two classes compute `working_format` differently (`self._guidance.format` against `self._fidelity.format`). | Let `PracticeSessionOutput` answer through its current fidelity's `FidelitySessionOutput` (or log a practice worked at no fidelity as none), so one class answers the five questions and `ChatLog` takes one type. | low |
| 4 | space/kanban/board.py:168-172, :567-591; app/src/kanban/board/board-client.tsx:32-44, practice-client.ts:24-26 | 2 | AI | new (put in by the round-7 fix for #4) | **The board sends its fidelities twice.** `practices[].fidelities` sends each practice's fidelity slugs, and the new `fidelities[]` sends each fidelity's slug, label and skill but not its practice. The page joins the two lists by slug: `practiceOf(slug)` searches the first and `fidelityShown(slug)` the second. | Send `BoardFidelity` inside each practice's data (or give it its practice), and delete the slug list and one of the two lookups. | low |
| 5 | space/repo/worktree.py:44-61, :73-77 | 2 | graph (`do-not-invent-parallel-object-models`) | new scope | `Worktree` holds `_branch_name` and also, made lazily, the `Branch` named by it. Equality and hashing use the name, and `branch` makes the `Branch` through the checkout's own `Repo`. A branch is its name in every checkout of one repository (`repo.py:454-456`), so the Branch could be made from the listing repository at once. | Hold the `Branch` from construction (`Branch(worktrees.repo, name)`), compare by it, and delete `_branch_name`. | low |
| 6 | space/kanban/app/src/kanban/board/icons.tsx:42-80 | 1 | graph (`eliminate-duplication`, 86%) | new scope | `FileViewIcon`, `SessionActionIcon` and `FormatIcon` each repeat the same `<svg>` frame around one path looked up in their own shape table. | One `ShapeIcon({ shape, size })` that the three call with their table's path. | low |
| 7 | space/kanban/app/src/kanban/chat/chat-client.tsx:87-98 | 1 | both (`eliminate-duplication`, 86%) | new scope | `resend` and `remove` are the same function except for the method they call. Together with `readMessages`, they also build `ChatClientGenerated.named(this.api, targetChat)` again on each call. | One private `actOnTarget(act)` that holds the target chat's client once and reads the messages after. | low |
| 8 | space/kanban/board.py:305, :310 | 6 | graph (`hide-inner-details`) | new scope | `BoardReads.tickets` and `backlog_items` read `board._ticket_kind` and `board._backlog_item_kind`, the Board's private class variables, to make cards. The Board already answers `ticket_of` and `backlog_item_of`. | Make cards through `board.ticket_of(session)` and a Board method for an item path, so only `Board` reads its card classes. | low |
| 9 | space/kanban/session_board_tiers.py:58-64 | 5 | AI | new (the fix rule "specs take the live path" was missed) | The story tests' domain tier builds `Sessions(project.root)` directly, and its `Validate` and `Generate` act on that second Sessions' session. Meanwhile `Board.load` and the served tools in the same world use `Sessions.of_project`, which round 7 made the one object per checkout. So the story tests' actions and the board work on two Session objects for one folder, the case the round-7 #6 fix exists to prevent. | Use `Sessions.of_project(project.root)` in the tier. | low |

## Round-8 specifics

- **Specs take the live path.**
  - Kept: #5 (file order) and #6 (one Sessions per checkout) are checked through the served tools (`self.project.call`, `ToolCall.sent`).
  - Missed: finding 2's spec counts on a Board it builds itself, and finding 9's story tier bypasses `Sessions.of_project`.
  - Two new specs swap a class attribute for the process while they run: `session_spec.py:1167-1176` replaces `Graph.open_saved`, and `kanban_spec.py:233-245` replaces `CatalogPractice.skill_install`. Both restore it in `after.each`. This is the `no-prototype-swapping` pattern, and it would leak into another spec running at the same time. Not counted, because it is spec code.
- **Each fix applied to every sibling format, reader and table.**
  - Kept: the file-order fix removed the TypeScript copy and the `FormatGroup` data class with it. The label and skill fix updated all four TypeScript readers (`tile-view`, `ticket-card-view`, `help-panel-view`, the spec) and `kanban-model.md`.
  - Missed, outside this area: the round-6 scanner fix that leaves `if TYPE_CHECKING:` imports out of `one-way-deps` was made only in the Python reader. The TypeScript reader still counts `import type` (last section), so this area shows 20 false file cycles.
- **One owner per finding.** #1 and #2 now have one owner each (`GuidanceAction.log_running`, `SavedGraph.from_file`). Findings 3 and 4 are new second owners that a round-7 fix put in.
- **Decision records.** All five records in the area were reread. I agree with each, and 0003 is now done (see "Decided").

## Counts

By concern (a finding with two concerns counts under both):

| Concern number | high | medium | low | total |
|---|---|---|---|---|
| 1 duplicated functionality | 0 | 0 | 3 | 3 |
| 2 duplicated shapes | 0 | 0 | 2 | 2 |
| 3 no use | 0 | 0 | 0 | 0 |
| 4 disconnected classes | 0 | 0 | 0 | 0 |
| 5 wrong-shape relationships | 0 | 0 | 2 | 2 |
| 6 seams that leak | 0 | 0 | 1 | 1 |
| 7 dependency direction / cycles | 1 | 0 | 0 | 1 |
| 8 one-class packages | 0 | 0 | 0 | 0 |
| 9 one file, several owners | 0 | 0 | 0 | 0 |
| 10 inconsistent names | 0 | 0 | 0 | 0 |
| 11 legacy and stale docs | 0 | 0 | 0 | 0 |
| 12 Python/TypeScript duplication | 0 | 0 | 0 | 0 |

By severity: high 1, medium 0, low 8 (9 findings, against 7 in round 7).

By status, out of round 7's 7 findings:

| Status | Count | Findings |
|---|---|---|
| fixed | 6 | round-7 #1, #2, #4, #5, #6, #7 |
| left | 1 | round-7 #3 (finding 2) |
| decided | 5 records, unchanged | round-6 #5 second half, #7, #8, #10–#12 |
| regression | 0 | |
| new | 3 | findings 3, 4, 9 (3 and 4 put in by round-7 fixes) |
| new scope | 5 | findings 1, 5, 6, 7, 8 (the first full graph run here) |

### Goal-class counts

| Goal class | Concerns | Round 7 total | Round 8 left | Round 8 new | Round 8 new scope | Round 8 regression | Round 8 total |
|---|---|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 3 | 1 (finding 2) | 1 (finding 9) | 0 | 0 | 2 |
| Shadow models | 2 | 1 | 0 | 1 (finding 4) | 1 (finding 5) | 0 | 2 |
| Duplicated functions | 1, 12 | 4 | 0 | 1 (finding 3) | 2 (findings 6, 7) | 0 | 3 |
| **Goal total** | | **8** | **1** | **3** | **3** | **0** | **7** |

The area's goal total went from 8 to 7. Leaving out new scope, which only the first graph run here could find, the comparable figure is 4, half of round 7's. All goal-class findings are low, and no high or medium is left in the three classes. The one high (finding 1) is concern 7, outside the goal classes. The graph check ran with every Clean Engineering rule on, and its goal-class hits came to three small TypeScript and value-class items.

## What would make the next round cheaper

1. **Hold the per-call object where the process holds things, and spec it through the served tool.** Round 7 fixed "a part rebuilt per call" by holding it on a `Board` or `Help`, but `Board.load` makes a Board per call, so the part is still rebuilt per call. The spec built one object directly and passed. For a concern-5 fix, the spec should make two served calls (`McpServer.answer_tool` or `self.project.call`) and count one construction. The holder should be one the process keeps: `Sessions`, `ServedCheckouts`, or a board held per checkout.
2. **A fix that adds a second answer should delete the first in the same change.** Findings 3 and 4 came from fixes that added a new way to answer an old question (a second log-protocol class, a second fidelity list) without folding the old one into it. A fix brief for a shape change should ask: which old field or class now answers the same thing, and is it gone?

## Scanner false positives

- **`one-way-deps`, 20 file-cycle hits inside `board/` (18) and `ticket/` (2).** Every cycle closes through an `import type`: the clients name `BoardPage`, `BoardStore` or `TicketClient` for an annotation, and only `board-page.ts` imports them as values. TypeScript erases these imports. This is the TypeScript twin of round 6's `if TYPE_CHECKING:` false positive, which was fixed only for Python (`model/python/python_class_model.py:201`, `:354-369`). Scanner: `cdd_guidance/practices/clean_engineering/model/base_class_model.py:24` (`_SCRIPT_IMPORT` matches `import type … from './x'`) through `import_targets` at `:475`. It should skip `import type` and `import { type X }`-only imports. The 8 package-level hits are real (finding 1).
- **`hide-inner-details`, 8 of 9 hits.** Each reads a private member of an object of the operation's own class: a new instance in a classmethod (`backlog_item.py:50` `item._write`), another card from the same board (`ticket.py:386`, `:423` `reopened._enter`, `moved._enter`), the instance a classmethod just made (`ticket.py:482` `read._is_judged_failing`, `report.py:289` `current._add_finding_from`), siblings in a class's own fold (`ticket.py:746` `states._states`), and `__eq__`'s `other` (`worktree.py:55`). Privacy in Python is per class. Scanner: `cdd_guidance/practices/clean_engineering/model/operation_metrics.py:401-414` (`PythonFunctionBody.reaches_peer_private`) treats only `self`, `cls` and a classmethod's first parameter as its own. It should also allow a name whose type or constructor is the operation's own class, and `other` in `__eq__`.
- **`do-not-invent-parallel-object-models`, `BoardReads` "copies the fields ['_board'] of 'Card'" (`board.py:297`).** Two classes that each hold the board they belong to share no model. Scanner: `cdd_guidance/practices/clean_engineering/rules/coupling_rules.py:111`. The same-file clause `other.source.file == node.source.file and own == theirs` fires on a single shared field and so skips `_MIN_COPIED_FIELDS = 3`. It should need the minimum too.
- **`errors-out-of-existence` against `domain-exception-carries-context`, the same 5 raises in `repo.py` and `sessions.py`.** One rule says to return a quiet result, and the other says to raise a named error with context. For a required tool argument that is missing, a named refusal is right. Scanner: `cdd_guidance/practices/clean_engineering/rules/operation_semantics.py:58` should leave alone a raise of a named domain error.
