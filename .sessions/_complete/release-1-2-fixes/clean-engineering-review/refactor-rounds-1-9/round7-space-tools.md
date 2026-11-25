# Round 7: space and tools, after the round-6 fixes

Area: `space/session`, `space/repo`, `space/work_state.py`, `space/kanban` (Python and the hand-written TypeScript in `space/kanban/app/src`), `tools/*`. Code read at c8921451 on `ensure-domain-orientation-refactor`; the CDD MCP host (`~/.cdd/runtime`) is at the same commit. Checked against `round6-space-tools.md` and the decision records the round-6 fix agents wrote: `space/kanban/.context/cdr/0001`–`0003`, `space/session/.context/cdr/0001`, `tools/.context/cdr/0001`.

Status words: **fixed** (listed below, not in the table), **left**, **regression**, **new** (not in round 6, in code that existed at round 6, including a pattern a round-6 fix put in place of the old one), **new scope**, **decided** (a fix agent decided it with a reason I agree with; it does not count).

## Graph check

The call failed, so this round's findings come from the AI check alone.

| Call | Result |
|---|---|
| `validate.validate`, `clean-engineering-code`, `graph: true`, absolute paths for `space/session`, `space/repo`, `space/work_state.py`, `space/kanban`, `tools` | Seven "still running" replies, then `RecipeLineFailed: Validate.validate recipe line cdd_guidance/actions/validate/validate.py:57 graph_paths = self._graph.check_beside(self._reports) failed: GraphBuildFailed: the graph build's worker process exited with 1`. The worker's trace ends in `AttributeError: 'Node' object has no attribute 'stereotypes'` at `cdd_guidance/practices/ddd/model/stereotypes.py:98` (`TacticalClass.kind` reads `self.oclass.stereotypes`). |

I followed `.claude/rules/mcp-fail-loud.md`: I stopped and did not run validate another way. The MCP host is running and answering. The failure is in the graph build, not in the connection. `~/.cdd/server.log` shows the same failure on every validate the other round-7 agents made around 06:31–06:36. Their reports in the validation-reports folder are zero bytes (`clean-engineering-code-20261108T113205.md`, `...T113337.md`, `clean-engineering-modules-20261108T113458.md` and others).

**Cause (for the lead, outside this area; high, wrong behaviour):** `DddReading._members_by_folder` (`cdd_guidance/practices/ddd/model/graph_reading.py:197-201`) takes the Clean Engineering practice's graph nodes (`clean.in_graph.nodes("OoadClass")`). It hands each one to `TacticalClass(cls)`, which expects a class-model class carrying `.stereotypes`. Every graph that holds DDD therefore fails to build, whatever paths it is asked for. This came in with f02b6485, "DDD reads a class model through the practice it extends". No graph rule ran on this area in round 7, and in round 6 only the modules call ran. So the near-copy scanner (`eliminate-duplication`) and the ten newly switched-on Clean Engineering rules have still not run here. There are no **new scope** findings because nothing could produce them.

## Fixed since round 6

- **#1 session tools lose the calling chat.** `Session.from_file` and `PracticeSessionOutput.load` take the served `call` (`session.py:91`, `practice_session_output.py:53`). `mark_loop` and `append_log` write through `self.log.by(call.chat)`. A spec drives `session.mark_loop` and `session.append_log` through `McpServer.answer_tool` with the session named, and checks the chat pointer on the line (`session_log_spec.py:70-104`). This is an effect spec, as the fix rule asks.
- **#2 the switch dialog decides leave and open choices.** `Ticket.leave_choices`, `close_choices` and `open_choices` answer `LeaveChoices` and `OpenChoices` with what is offered now. There is no merge on the default branch and none when closing (`ticket.py:285-309`, `:699-744`). `activation-client.ts:45-56` only shows them, and the `.filter(choice =>` cases are gone.
- **#3 two Session objects per folder.** `Sessions._held_at` keeps one per folder (`sessions.py:133-142`), and a move re-keys it (`moved`). The chat lives on `ChatLog`, never on the session. Specs check one object for two chats, and that the practice's session is the call's session (`session_log_spec.py:52-67`).
- **#4 a restored graph to ask for the scanned rules.** `ReportFile._scanned_rules` asks `SavedGraph.checks_of(self._practice)`, which reads the overlays without restoring a graph (`report.py:258-263`, `saved_graph.py:219-223`).
- **#6 an Installer built through the session diagnostics.** `SessionDiagnostics` now derives from `harness/diagnostics/call_diagnostics.py:CallDiagnostics`, shared by every diagnostics toolset. That class holds the call, raises `DiagnosticsNeedACall` without one, and holds its Installer once per call. One owner replaced the per-toolset copies.
- **#14 columns known by name in the page.** `isClosed`, `isBacklog` and `BoardClient.opensLeft` replace the 'Complete', 'Backlog' and 'Implementation' literals. A grep of `app/src` for column names in quotes finds none outside specs.
- **#15 `Ticket.record` pops `__dict__`.** It now resets a held `_progress_read` (`ticket.py:138-149`).
- **#16 two Repos for one board** and **#17 `Repo.of_project` builds a Repo per call.** `ServedCheckouts` holds one Repo per checkout root (`repo.py:587-606`), and `checkout_at` and `of_project` go through it. Specs: `clone_spec.py` ("one repository for both", "the repository the checkout's sessions work in") and `kanban_spec.py:64-67`.
- **#18 two writers of a session's hook logs.** `HookLog` (`session_log.py:63-79`) is the one writer. `Session.hook_log` returns it, and `PromptLog._append` calls `append`. A spec covers both kinds of entry.
- **#19 stale `Sessions.saved` and `Session.load` in the scenario realization.** No mention is left in `space` or `tools`.

## Decided by a fix agent (not counted)

- **#5, second half (`_has_newer_report` lists the reports folder on each read):** `space/kanban/.context/cdr/0001`. I agree. Another chat or process can write a newer report at any time, so a latest report held on the fidelity would answer stale. The listing runs once per report read.
- **#7 two FileManagers and two path tops:** `space/session/.context/cdr/0001`. I agree. The reader that still names paths from the workpath is the page's file views in `harness/installation`, so the first step is the harness area's. The three steps are named.
- **#8 the board's practices against each session's:** `space/kanban/.context/cdr/0002`. I agree. The board shows closed and backlog sessions too, so no one session's instances can stand for it. `FidelityProgress.is_enabled` now asks `self._fidelity.session_output.is_enabled` instead of looking the practice up by key (`ticket.py:545-550`), so the lookup half of #8 is fixed.
- **#10 `_catalog` registry and toast aliases**, **#11 the notifier loads every toolset**, **#12 `ToastFile` parses `rules_toast`:** `tools/.context/cdr/0001`. I agree. The owners are `PracticeCatalogue`, `ActionCatalogue`, `AgentTool` and the hook server, all in `harness`, and the record names three ordered steps. For #11 the reason is sound: the hook server's `HandlerCatalog` holds only the toolsets whose hooks are installed (`hook_server.py:433-440`), and a toast can sit on any toolset's MCP tool.

## Findings, most severe first

| # | file:line | concern | check | status | finding | fix in one line | severity |
|---|---|---|---|---|---|---|---|
| 1 | space/kanban/ticket.py:486, :498-510 vs harness/guidance_actions/guidance_actions.py:485 | 1, 5 | AI | new (from the round-6 fix for the Sketch generate line, 1a14109f) | **Two owners for one job: a generate expanded inside another tool must not count as done.** The actions area made a nested action log nothing (`log_running` returns when `self._outer is not None`). The kanban fix also added `FidelityProgress._written_by_generate`, which walks the log and drops a generate line that follows a `tool` line for another tool. It works out which call a line belongs to from `entry.tool_called.split(".")[0] == GENERATE`. Now that nested actions write no generate line, the reader filters lines that no longer appear (only logs written before 6450c7e8 hold them). It also reads the call a line belongs to out of the text, a decision that belongs to the log (`SessionLog` or `LogEntry`). | Keep the rule in one place: nested actions log nothing. Delete `_written_by_generate` and its four examples, or, if old logs must still read right, let `SessionLog` answer each line's call (a `LogEntry.call` read once) and have `FidelityProgress` ask it. | medium |
| 2 | space/kanban/report.py:243, :252, :262 vs cdd_guidance/actions/validate/graph_json_reader.py:18-21 | 1 | AI | left (#5, first half; the second half has a record, see above) | "A list is a node list, a dict is a saved graph" is still decided in two files. `ReportFile` also branches on `isinstance(checked, list)` three times: when it reads the graph, when it finds the hits, and when it finds the scanned rules. The fix agent wrote no record for this half, so the fix rule "one owner of the job" was missed. | Let one reader return a checked graph object with `violations(practices)` and `checks_of(practice)` for both shapes (a saved graph, or a node list with no overlays), and have `ReportFile` and `graph_json_reader` use it. | medium |
| 3 | space/kanban/board.py:511, :261; space/kanban/ticket.py:675 | 5 | AI | left (#9, narrowed) | The function-level import is gone and `Help` holds its `CatalogPractice`. But a `Help` is made on every `board.help` and `fidelity-progress.help` call, so a `CatalogPractice` (its card read, and a new `FileInstallation` from `skill_install()`) is still built per call just to name one page address. | Hold one `CatalogPractice` per board practice on the board (or let the catalog publish its page index), and hand `Help` that held one. | low |
| 4 | space/kanban/app/src/kanban/board/practice-client.ts:28-36; ticket/tile-view.tsx:25-33; ticket/ticket-card-view.tsx:38; board/help-panel-view.tsx:63 | 12, 10 | AI | left (#13; I disagree with `space/kanban/.context/cdr/0003`) | `fidelityNameOf` still cuts a label out of the slug, and `skillOf` rebuilds the installer's skill naming. The record's reason is that the naming is the installer's and this module may change the harness only to follow a rename. The answers are already public in the harness, though, and the board already imports their class: `CatalogFidelity.label` (`BoardLabel`, `catalog_examples.py:286`) and the skill path from `FileInstallation.relative_path`, which `CatalogPractice.skill_name` uses (`catalog_practice.py:128-134`). `board.py` imports `CatalogPractice` for `Help`. So the board can send both without changing the harness, and the item is not blocked. | Have the board's practice data send each fidelity's `CatalogFidelity.label` and skill command, read through the held `CatalogPractice`, and delete `fidelityNameOf` and `skillOf`. | low |
| 5 | space/kanban/app/src/kanban/ticket/files-panel-client.ts:7-10 vs space/kanban/ticket.py:683 (`Format.file_order`, harness/markdown/format.py:73) | 12 | AI | new (the round-6 fix put the order in Python; the TypeScript copy was not removed) | **The order of a fidelity's files is decided in both languages.** `FidelityProgress.files` now sends formats sorted by `Format.file_order` (markdown, code, diagrams). The page still keeps `TAB_GROUPS = ['markdown', 'code', 'diagram']` and `tabOrderOf` to order tabs by group. | Let the tabs follow the order Python sends, and delete `TAB_GROUPS` and `tabOrderOf`. | low |
| 6 | space/session/sessions.py:223-231, :238-240 vs space/repo/repo.py:587-606 | 5, 2 | AI | new | **One Session per folder holds only per project folder, not per checkout.** `CallSessions` keys its `Sessions` by the project folder as given, while `ServedCheckouts` keys Repos by checkout root. A call naming a subfolder, or `named_in` with no project (which keys by `Path(session_file).resolve().parent`, the session's own folder), gets a second `Sessions` for the same checkout. That second `Sessions` holds a second Session for the folder, with its own graph and practices. `clone_spec.py` checks that `Repo.of_project(root)` and `Repo.of_project(root / "docs")` are one object; the same check on `Sessions.of_project` would fail. | Key `CallSessions` by `Repo.of_project(project).root` (or let the held Repo hold its Sessions), and add the subfolder example to `session_log_spec`. | low |
| 7 | space/session/session-sketch.md:477-484 | 11 | AI | new | The session sketch, edited in round 6, still says a tool call's session is "its own copy, so one call's practices never reach another" (`expect(ToolCall(project).session).not_to be session`). This is the opposite of what round 6 built and specced: one Session per folder for every call. | Rewrite the example as "one object for every call, from any chat", as `session_log_spec.py:52-58` asserts. | low |

## Round-7 specifics

- **Rule-versus-schema gaps:** this area holds no practice code (no BDD, Stories or DDD scanners or `schema.yaml`), so there is nothing to check here. The story tests under `space/kanban` are artifacts the graph would read, but no graph could be built this round.
- **The round-6 fix rules:**
  - Concern-5 fixes with an effect spec: #1, #3, #16, #17 and #18 each have one (cited above). Finding 1 above, a concern-5 change made by a fix, has specs, but they specify the duplicate filter rather than one owner.
  - One owner per duplicate: missed for #5's first half (finding 2), with no record. Also missed where a fix added a second owner, findings 1 and 5. In each case the fix agent's grep for the job did not cover the other area's change landing at the same time (nested actions log nothing; `Format.file_order`).
  - A decision record for every skip: written for #5's second half, #7, #8, #10, #11, #12 and #13. I disagree only with #13's (finding 4).

## Counts

By concern (a finding with two concerns counts under both):

| Concern number | high | medium | low | total |
|---|---|---|---|---|
| 1 duplicated functionality | 0 | 2 | 0 | 2 |
| 2 duplicated shapes | 0 | 0 | 1 | 1 |
| 3 no use | 0 | 0 | 0 | 0 |
| 4 disconnected classes | 0 | 0 | 0 | 0 |
| 5 wrong-shape relationships | 0 | 1 | 2 | 3 |
| 6 seams that leak | 0 | 0 | 0 | 0 |
| 7 dependency direction / cycles | 0 | 0 | 0 | 0 |
| 8 one-class packages | 0 | 0 | 0 | 0 |
| 9 one file, several owners | 0 | 0 | 0 | 0 |
| 10 inconsistent names | 0 | 0 | 1 | 1 |
| 11 legacy and stale docs | 0 | 0 | 1 | 1 |
| 12 Python/TypeScript duplication | 0 | 0 | 2 | 2 |

By severity: high 0, medium 2, low 5 (7 findings, against 19 in round 6).

By status, out of round 6's 19 findings:

| Status | Count | Findings |
|---|---|---|
| fixed | 11 | #1, #2, #3, #4, #6, #14, #15, #16, #17, #18, #19 |
| left | 3 | #5 first half, #9, #13 |
| decided | 5 | #7, #8, #10, #11, #12, plus #5's second half |
| regression | 0 | |
| new | 4 | findings 1, 5, 6, 7 |
| new scope | 0 | the graph check could not run |

Of the new findings, two were put in place by round-6 fixes (1 and 5).

### Goal-class counts

| Goal class | Concerns | Round 6 (this area) | Round 7 left | Round 7 new | Round 7 new scope | Round 7 total |
|---|---|---|---|---|---|---|
| Bad resource orientation | 5, 9 | 12 | 1 (#9) | 2 (findings 1, 6) | 0 | 3 |
| Shadow models | 2 | 4 | 0 | 1 (finding 6) | 0 | 1 |
| Duplicated functions | 1, 12 | 7 | 2 (#5, #13) | 2 (findings 1, 5) | 0 | 4 |
| **Goal total** | | **23** | **3** | **5** | **0** | **8** |

The area's goal total fell from 23 to 8, a cut of 65%. No high finding is left in the area. Five items that round 6 counted now leave the count as decided. Without them the total would be 8 plus up to 9 concern entries (#7: 2; #8: 2, 5; #10: 2, 5; #11: 1; #12: 1), so 17. A caveat on comparing rounds: no graph rule ran on this area in rounds 6 and 7, so the near-copy scanner and the newly switched-on Clean Engineering rules have never judged it. Once the DDD graph build is fixed, expect **new scope** findings here.

## What would make the next round cheaper

1. **Grep for the job across the areas landing at the same time, not only in the area's own files.** Both new duplicates came from two fix agents solving one problem at once: the Sketch generate line was solved in `harness/guidance_actions` and again in `space/kanban`, and the file order in `Format` and again in the page. A fix brief for a concern-1 or concern-12 finding should ask the agent to grep the integration branch after merging the tip, and delete its own copy when another area's change already does the job.
2. **A one-object-per-thing guarantee needs one key.** Round 6 made one Repo per checkout root and one Session per folder, but `CallSessions` still keys by whatever folder the call names. When a fix holds one object per resource in a process registry, the spec should also try a second name for the same resource (a subfolder, the session's own folder), as `clone_spec` does for Repo.

## Scanner false positives

None to report: the graph build failed before any scanner ran. The round-6 false positives (the `one-way-deps` counting of `if TYPE_CHECKING:` imports at `python_class_model.py:184`, and `is_test_code` missing test-support files) could not be re-checked this round.
