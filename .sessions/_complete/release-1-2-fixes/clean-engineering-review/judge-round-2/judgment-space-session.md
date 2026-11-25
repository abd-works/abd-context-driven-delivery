# Judgment, round 2: space/session

**Area:** `space-session`: the 41 production files of `space/session` (with its packages `files`, `practices`, `validation` and `spec_support`) and `space/work_state.py` changed since 2026-11-21 (base `66f410de3`), judged at `5d16245ff` on branch release-1-2-fixes. The area holds no TypeScript.

**Read:** every file in `space-session.txt`, in full, at its current content; the module card `space/session/.context/module-context.md` and the model `space/session/.context/session-model.md`; the first round's `judge-round/judgment-space-session.md`; the Clean Engineering code and model rules, `.claude/rules/coding.md`, and the refactor guardrails. Specs were read only to see how a class is used. Nothing was changed.

**Method:** each file was judged whole, not only its changed lines, as the first round did. A script listed every public class, method, and module function of the 41 files and counted whole-word references in every tracked `.py`, `.ts`, `.tsx`, `.js`, and `.md` file outside the defining file, split into production code outside `space/session`, production code inside it, specs (spec files, story tests, `spec_support`, `*_examples.py`), and markdown; each "unused", "no caller", and "only used inside" claim below was then checked again with a repository-wide grep. A finding the first round also made (same file, or the file its code moved to, same rule, same problem) ends in "(still open from round 1)": `session_roots.py` is now `session_checkout.py` and `checkout_worktrees.py`, `file_graphs.py` and `practice_outputs.py` are now `session_graph.py` and `practices/session_practices.py`, and the files of `files/`, `practices/`, `validation/` and `spec_support/` moved there from the module's top folder. Round-1 findings on files not in this list (format alignment, violation history, progress cache, answer reads, the session probe) are not counted. `oss_portal_domain_driven` is left out.

Themes: **[1]** module boundaries, **[2]** the same work in different shapes, **[3]** resource orientation, **[4]** domain orientation.

## Counts

| | Count |
|---|---|
| Files read | 41 (plus the module card and model) |
| Findings | 104 |
| Findings still open from round 1 | 68 |
| New findings | 36 |
| Round-1 findings in these files now fixed | about 40 (the session made whole and placing itself, `SessionCheckout` and `CheckoutWorktrees` in place of `SessionRoots`, typed session.json fields, `OpenSessions` taking its chat and answering a `SwitchedSession`, the prompt queue registering instead of being imported, `SessionGraph` and `DocumentGraph`, `GuidanceVersion` and `FormatSelection` folded into `GuidanceSelection`, practices no longer imported by the viewer or the output, `LogLine`, `ValidationReport`, fidelity outputs held once, the harness contracts naming what is called) |
| Design proposals | 7 |

Findings by rule:

| Rule | Findings | Still open from round 1 |
|---|---|---|
| eliminate-duplication | 17 | 7 |
| hold-state-on-the-object-not-in-parameters | 8 | 7 |
| prefer-instance-operations | 7 | 1 |
| keep-classes-single-responsibility | 7 | 6 |
| use-consistent-naming | 6 | 6 |
| prefer-class-operations | 5 | 2 |
| use-typed-signatures | 5 | 3 |
| hide-inner-details | 5 | 3 |
| put-logic-on-the-owning-resource | 5 | 3 |
| keep-operations-single-responsibility | 4 | 3 |
| use-explicit-dependencies | 4 | 4 |
| use-intention-revealing-names | 4 | 4 |
| errors-out-of-existence | 3 | 1 |
| limit-operation-parameters | 3 | 2 |
| make-module-only-operations-private | 2 | 1 |
| write-interactions | 2 | 2 |
| seam-names-current-code | 2 | 1 |
| one-way-deps | 2 | 1 |
| class-not-property-instance-or-subtype | 2 | 2 |
| public-seam-only | 1 | 1 |
| low-coupling | 1 | 1 |
| shape-classes-around-resources | 1 | 1 |
| layer-separation | 1 | 1 |
| avoid-vague-parameter-names | 1 | 1 |
| never-swallow-exceptions | 1 | 1 |
| temporal-independence | 1 | 1 |
| no-legacy-api-after-refactor | 1 | 1 |
| limit-comments | 1 | 1 |
| delete-unused-operations | 1 | 0 |
| provide-meaningful-context | 1 | 0 |
| **Total** | **104** | **68** |

## Findings

### space/session/.context/module-context.md and session-model.md

- module-context.md:195 `Seam (terms)` — public-seam-only — The seam still names about 90 terms, among them classes no module outside `space/session` uses: `HeldSessions`, `SessionListing`, `ServedAnswers`, `InjectedRules`, `ChatLog`, `LogLine`, `DocumentGraph`, `CheckoutWorktrees` (the script finds no production reference outside the module for `HeldSessions`, `SessionListing`, `InjectedRules`, `ChatLog`). Promising them to callers hides which few classes other modules really use. [1] (still open from round 1)
- module-context.md:196 `Dependencies (one-way)` — seam-names-current-code — The list leaves out `harness/design_canvas` (`CanvasVersions`, practices/practice_session_output.py:13), `harness/whiteboard` (`Whiteboard`, line 17), `harness/markdown` (`Format`, `MarkdownText`; practice_session_output.py:19, files/file_manager.py:20, files/session_file.py:20), and `harness/guidance` beyond `PracticeCatalogue` (`DeclaredFile`, `ACTION_CATALOGUE`, `STAGES`, `load_document`); and line 198 says the module "imports no practice" while spec_support/session_roots_examples.py:9 imports `cdd_guidance.practices`. A reader of the card believes the module is less coupled than it is. [1] (still open from round 1)
- session-model.md:144 `Session` — seam-names-current-code — The model has no `SessionTestTierTools` or `TestTiers`, though `Session` mixes in `SessionTestTierTools` (session.py:371) and holds `test_tiers` (session.py:407), and no `SessionPaths`, `SessionSaves`, or `CheckoutWorktrees`, which the card names as parts of the seam. The model and the code describe two different sessions. [1]

### space/session/__init__.py

- __init__.py:7 `import harness.files_app.files_app` — low-coupling — Importing the session package still starts the Files app's registration, an unrelated application, as a side effect; registration belongs where the server's toolsets are discovered. [1] (still open from round 1)

### space/session/session.py

- session.py:387 `Session.repo` and session.py:403 `Session.checkout.repo` — use-consistent-naming — The session still holds two projects: `repo`, the checkout whose sessions loaded it, and `checkout.repo`, its own worktree. `SessionPaths.from_project` (session_paths.py:79), `SessionFiles.in_folder`, `in_workpath`, `under_root` (files/session_files.py:100, 108, 120), `WrittenFiles` (practices/practice_session_output.py:546, 604, 615, 622, 655, 664) and `ProposedRoots.holding` (practices/proposed_roots.py:47) name paths from the first, while `path_named` and `in_project` (session_paths.py:68, 84) read them from the second, so a path named from a ticket's worktree does not round-trip, and `root_named` (practice_session_output.py:220) has to accept either. [4] (still open from round 1)
- session.py:399 `Session._make_parts` — hide-inner-details — Fourteen parts are public attributes, and other modules chain through them: `session.folder.move_to_closed()` and four more moves in space/kanban/ticket.py:338-816, `session.folder.violation_history` in cdd_guidance/actions/validate/checked_graph.py:87, and spec_support/session_roots_examples.py:73 replaces `session.session_files.branch_changes` from outside. Every part's whole interface is therefore part of the module's seam. [1] (still open from round 1)
- session.py:401-415 `SessionPaths(self)` … `DecisionRecords(self.work_root / …)`, `Handoffs(folder)` — shape-classes-around-resources — Most parts take the whole `Session` and call back into its other parts, while `DecisionRecords` and `Handoffs` take only the folder they own and are rebuilt by the `workpath` and `work_folder` setters (lines 484, 516). Two conventions for "a part of a session" means neither can be relied on. [3] (still open from round 1)
- session.py:409, 494, 506, 516 `handoffs: Handoffs | None`, `work_folder -> Path | None`, "None for a session not yet kept in one" — use-typed-signatures — Since the constructor takes the record folder and sets the work folder at once (lines 393-397), neither folder can be None, yet the types, docstrings, and guards still say they can: `Handoffs(folder) if folder is not None else None`, `SessionRecord.kept_in(None)` (session_record.py:327), `save()`'s `record_folder is None` return (session_record.py:407), `SessionLog.path`'s None (session_log.py:219). Every reader guards a case that no longer happens, and a type checker cannot tell them it does not. [3]
- session.py:371 `Session(SessionFileTools, SessionExplorer, SessionGuidanceTools, SessionTestTierTools, SessionLogTools, SessionDecisionTools)` — layer-separation — Six base classes, one more than round 1 (`SessionTestTierTools`), exist to forward a published tool to a part and restate in annotations what they need from `Session`, while `FileComments`, `FileManager`, and `PracticeSessionOutput` publish toolsets of their own. Two publishing shapes sit side by side. [1] (still open from round 1)
- session.py:138 `SessionFileTools.file(..., node_filter: dict | None)` — use-typed-signatures — `SessionExplorer` now takes `FilterRequest` (files/session_explorer.py:45), but the viewer's own read still takes a bare dict for the same filter and hands it to `FileViewFilter`, which is typed `FilterRequest` (files/file_view_filter.py:30). [3] (still open from round 1)
- session.py:145 `SessionFileTools.add_to_chat_context` — keep-operations-single-responsibility — To quote some lines it builds a whole `SessionFile` (which reads the file, counts its lines, refuses a long one, and builds a `FileViewFilter`), then loads a chat by its id and queues a `"fill"` on its mailbox, which `FileComments._sent` (files/file_comments.py:254) does again. [3] (still open from round 1)
- session.py:176 `SessionGuidanceTools.set_up_roots` — keep-classes-single-responsibility — The eight-step instructions for setting a session's roots sit in the class that reads and changes the guidance selection; they are about each fidelity's roots and belong with `fidelity-session-output.propose_roots`. [4] (still open from round 1)
- session.py:271-273 `SessionLogTools.write_handoff` — errors-out-of-existence — An empty document is answered with the sentence "Nothing written: …" where a path is answered on success, so a caller cannot tell a refusal from a written file; `ChatLog.append_note` (session_log.py:425) does the same with "nothing appended". [3] (still open from round 1)
- session.py:330 `SessionDecisionTools.list_cdrs -> str` — use-typed-signatures — A list of paths is joined into one newline-separated string for the caller to split again; the operation holds a `list[Path]`. [3] (still open from round 1)
- session.py:301 `SessionLogTools.debug_session` — keep-classes-single-responsibility — A six-step debugging and release procedure (lanes, pull requests, a maintainer's email address) is published from the session log's tools; it is neither about the log nor about a session's state. [4] (still open from round 1)
- session.py:703-725 `practice(name)`, `practices`, `own_practices`, `session_practices.every` — use-intention-revealing-names — Four ways to reach a session's practices: `practices` (only those turned on, and it opens the graph), `own_practices` (every practice, published under the key `practices`), `practice(name)` (either), and `session_practices.every`. "Own" says nothing about the difference, and the published `practices` is not the Python `practices`. [4] (still open from round 1)
- session.py:703 `Session.practice(name)` — hold-state-on-the-object-not-in-parameters — harness/guidance_actions/guidance_actions.py:505 still holds the practice's guidance and passes its key back (`self._session.practice(practice.key)`) to find it again, the lookup by name the guardrails rule out. [3] (still open from round 1)
- session.py:586 `Session.root` — use-consistent-naming — `root` is a string of the work root here, a `Path` of the project on `SessionCheckout.root` (session_checkout.py:96), a `Path` of the loading checkout on `Sessions.root` (sessions.py:45), a path-from-project string on `PracticeSessionOutput.root` (practice_session_output.py:186), and the first folder on `FidelitySessionOutput.root` (line 477); beside them stand `workpath`, `work_root`, `record_folder`, `work_folder`, `output_root`, and `folder`. [4] (still open from round 1)
- session.py:404 `Session.folder` — use-consistent-naming — `session.folder` is a `SessionFolder` object, `sessions.folder` the `.sessions` `Path` (sessions.py:68), `ThrowawayProject.folder` a temporary `Path` (spec_support/throwaway_project.py:142), and `PracticeSessionOutput.folder` the practice's `Path`; one attribute name gives four kinds of thing on neighbouring objects. [4] (still open from round 1)
- session.py:620, 690, 770 `idea_file`, `accepted_violations`, `file_comments` — use-explicit-dependencies — Each is built again on every access, and `session.folder.violation_history` (session_folder.py:51) builds a new `ViolationHistory` with `Repo.of_project(...)` each time; the guardrail is "build once, keep it". [3] (still open from round 1)
- session.py:770-774 `from space.session.files.file_comments import FileComments` inside `file_comments` — one-way-deps — The import is hidden in a function because "a toolset the module holds at run time would be published again as this toolset's tools" (line 45), yet line 30 imports the `PracticeSessionOutput` toolset at module level and it is published once. Either the reason no longer holds or line 30 has the problem; as it stands the dependency is only hidden. [1] (still open from round 1)
- session.py:748 `Session.choose_workpath` — keep-operations-single-responsibility — It collects each practice's chosen root, moves the workpath, saves, then writes each root back against the new workpath, because roots are saved relative to a folder that can move; the practice should keep its root in a form that survives the move. [3] (still open from round 1)

### space/session/sessions.py

- sessions.py:56 `Sessions.of_project` — prefer-instance-operations — A class method that hands every caller the object kept in the process-wide `SERVED_SESSIONS`; the rule names a global accessor as the case to avoid. Six production call sites use it. [3] (still open from round 1)
- sessions.py:62 `Sessions.file_manager` — eliminate-duplication — A third `FileManager`, beside the two `SessionFiles` holds (`file_manager` and `_from_project`, files/session_files.py:54, 66), each with its own roots. [2] (still open from round 1)
- sessions.py:130 `Sessions.with_file(session_file)` — avoid-vague-parameter-names — The parameter is a path to a session.json, an absolute path, or a bare session name (`_is_bare_name`, line 145), so one string means three things and `named(name)` is reached through a parameter called `session_file`. [4] (still open from round 1)
- sessions.py:154 `Sessions.create(..., parent: str)` — hold-state-on-the-object-not-in-parameters — The parent is passed as its name although the only production caller, `SessionHierarchy.open_child` (session_hierarchy.py:44), holds the parent session and passes `session.name`. [3] (still open from round 1)
- sessions.py:197 `SessionsRead` — hide-inner-details — A result with two public mutable lists that `read_apart` fills from outside (lines 108, 110). [3] (still open from round 1)
- sessions.py:312 `CallSessions.saved_in` — use-intention-revealing-names — "Saved in project" answers the session a project has open (`current()`); the name comes from harness's `SESSION_OPENING` contract (harness/agent_tools/tool_call.py:41) and says nothing about opening. [4] (still open from round 1)

### space/session/open_sessions.py

- open_sessions.py:22 `_switch_note(heading)` — prefer-class-operations — A module function used only by `SwitchedSession.instructions`, which reads and splits SESSION-SWITCH.md again for each note of each switch; it belongs on `SwitchedSession`, which can read the file once. [3]
- open_sessions.py:70 `OpenSessions.on_session_opened` — prefer-instance-operations — A class method that appends to class-level state (`_opened_listeners`, shared by every checkout's sessions in the process); it is neither a creation factory nor `every`. space/session has three of these: `SessionSaves.leave_out` (session_saves.py:58) and `GuidanceSelection.start_on_ticket_stage_with` (practices/guidance_selection.py:172) are reported in their files. [3]
- open_sessions.py:65 `_opened_listeners: ClassVar[list[...]]` — eliminate-duplication — Three home-made class-level registries let other modules register with the session: this listener list, `SessionSaves._left_out` (session_saves.py:56), and `GuidanceSelection._ticket_stage` (practices/guidance_selection.py:165), each with its own registration verb (`on_session_opened`, `leave_out`, `start_on_ticket_stage_with`) and storage. AGENTS.md describes one *ClassRegistry* mechanism the process holds once for exactly this; three more shapes mean a reader cannot find who registered what in one place. [2]

### space/session/session_checkout.py

- session_checkout.py:17 `_MAIN = "main"` — eliminate-duplication — Main's name is spelt again beside `MAIN_SESSION_NAME` (session.py:49), and a third time as the literal `'main'` in `SessionPaths._sketch_name` (session_paths.py:62); a rename of the default session misses two of them. [2]
- session_checkout.py:20 `names_ticket(branch, ticket)` — put-logic-on-the-owning-resource — The regex duplication round 1 found is gone, but the one copy is a module function that three classes import (`SessionCheckout`, `CheckoutWorktrees.of_branch` at checkout_worktrees.py:34, `OpenSessions._ticket_of_worktree` at open_sessions.py:132), each passing a branch name string; whether a branch names a ticket is a question for the `Branch` (space/repo) they already hold. [3]

### space/session/checkout_worktrees.py

- checkout_worktrees.py:67 `except (RuntimeError, OSError)` — never-swallow-exceptions — Any runtime or operating-system failure of the worktree and branch listing still becomes "no worktrees and no branches", which then places every ticket in the main checkout and claims no branch; only "this folder is in no repository" is the ordinary case. [3] (still open from round 1)

### space/session/session_record.py

- session_record.py:159 `SessionFields.raw` — hide-inner-details — The record's storage is a public attribute: `_Field` reads and writes it, and `OwnedFields.get` / `save` (lines 274, 280) reach `self._record.fields.raw` and update it with free keyword values. The typed fields hide the dict from the session's parts, but any caller can still write any key through `raw`. [3]
- session_record.py:210-262 `_kept`, `_upgraded`, `_merge_formats`, `_merge_outputs`, `_merge_fidelity_output`, `_fidelity_of` — prefer-class-operations — Six module functions used only by `SessionFields` (its constructor and `as_dict`), each handed the raw dict and reaching into it; they are the fields' own upgrade and writing rules. [3]
- session_record.py:186-192 `SessionFields._tiers_of` and test_tiers.py:58-63 `TestTiers.record` — eliminate-duplication — Whether a tier is one of `TEST_TIERS` and has a non-empty tool is checked twice, with different failures: on read as `MisshapenTestTiersError`, on write as `UnknownTestTierError` / `TestToolRequiredError`. A new tier, or a new rule for a tool, has two places to change. [2]
- session_record.py:417 `SessionRecord.saved(change)` — put-logic-on-the-owning-resource — `update` queues its own save, but `Session.keep_text` (session.py:639), `SessionFolder.keep_file`, `remove`, and `_move_to` (session_folder.py:59, 84, 111) each still have to remember to call `record.saved(...)` after writing; a write to the record folder that forgets it is never committed on main. [3] (still open from round 1)
- session_record.py:369 `ANSWER_READS.begin()` — use-explicit-dependencies — The record reaches the module-level global although its session holds `sessions.answers`, the `ServedAnswers` made for this purpose. [3] (still open from round 1)

### space/session/session_folder.py

- session_folder.py:41, 47 `SessionFolder.hook_log`, `violation_history` — keep-classes-single-responsibility — The class that moves a record folder among open, closed, archived, and backlog sessions also names a hook's log and builds the violation history; both are files of the work folder and nothing to do with moving the record. [3] (still open from round 1)
- session_folder.py:107-110 `session.record_folder = …`, `session.work_folder = …`, `session.sessions.held.moved(session, moved_from)` — write-interactions — The folder sets two of the session's fields from outside through their setters and reaches three objects deep to tell the held sessions what it did (also `held.removed` at line 83); the move should be asked of the session and its sessions, which own both. [3] (still open from round 1)

### space/session/session_paths.py

- session_paths.py:45-49, 58 `".context"`, `".sessions"` — eliminate-duplication — `context_folder` and `is_sketch` spell the two folder names as literals although `CONTEXT_FOLDER` (harness/installation/context_config.py, imported by session.py:18) and `SESSIONS_FOLDER` (space/work_state.py:14, imported by session.py:42) exist and the rest of the module uses them. [2]
- session_paths.py:15 `SessionPaths` — keep-classes-single-responsibility — One class resolves and caches paths, names paths from the project, finds the `.context` folder, names the sketch, and loads documents; and "is this path under one of these roots" is still written in five other places (files/session_files.py:166, files/file_manager.py:443, practices/practice_session_output.py:554 and 653, files/node_spans.py:109). [3] (still open from round 1)

### space/session/session_log.py

- session_log.py:381 `ChatLog.validation` — use-consistent-naming — A validate line still names the practice by its class (`type(worked.practice.guidance).__name__`, `CleanEngineering`) and an action line by its key (line 390, `clean_engineering`); `LogLine.names` (line 129) accepts both to compensate, and the docstring at line 379 records the mismatch instead of removing it. [2] (still open from round 1)
- session_log.py:88 `LogLine.read` — hold-state-on-the-object-not-in-parameters — Writing and reading are now one class, but a line read back keeps only its verb, one subject string, and its time: its paths, practices, fidelities, formats, rules, and chat are lost, and `words`, `stage`, and `names` split the written string again. The board decides what work was done from that split (space/kanban/ticket.py:642, 846), so a path with a space or a new part still changes what the board shows. [3] (still open from round 1)
- session_log.py:221, 283, 300, 326, 340 `error_path`, `append_trace`, `last_loop_number`, `latest_loop_with_entries`, `loop_to_note` — make-module-only-operations-private — Public on `SessionLog`, used only by `ChatLog` and `SessionLog` in this file (no production reference elsewhere, no spec); `seed_first_loop` and `ChatLog.append_note` are used only inside the module. [1] (still open from round 1)
- session_log.py:88 `LogLine.read` — prefer-instance-operations — A class method named `read`, which is none of the factory names the rule allows (`from_*`, `load`, `create`, …); `LogLine.from_text` or `load` would say it makes a line. [3]
- session_log.py:74 `LogLine.__init__` — limit-operation-parameters — Ten parameters (`verb`, `subject`, `paths`, `practices`, `fidelities`, `formats`, `detail`, `rules`, `chat`, `time`); `practices`, `fidelities`, and `formats` are always made together from one list of `FidelitySessionOutput` (line 390-392) and are one value, what the action worked on. [3]

### space/session/session_saves.py

- session_saves.py:139 `SessionSaves._save` returning while `current_branch != default_branch` — errors-out-of-existence — `_save_queued` has already taken the queued changes off `_pending` (line 120) when `_save` returns because the repository's own folder is not on the default branch: nothing is committed, no `SaveFailure` is kept, and the changes are never queued again, so the board shows no failure and offers no retry while the records stay uncommitted until some later save happens to sweep them up. A save that could not do what was asked answers as if it did. [3]
- session_saves.py:58 `SessionSaves.leave_out` — prefer-instance-operations — A class method that appends to class-level state (`_left_out`); it is no factory. [3]
- session_saves.py:179 `SERVED_SAVES` — use-explicit-dependencies — Module-level state that `Sessions.saves` reaches (sessions.py:77); with `SERVED_SESSIONS` (sessions.py:326), `_GUIDANCE_CHANGED` (practices/guidance_selection.py:32), `_FILES_UNDER` (files/file_manager.py:489), and `ANSWER_READS`, the area still keeps five pieces of state at module level, against the guardrail "no global current objects". [3] (still open from round 1)

### space/session/session_graph.py

- session_graph.py:38 `DocumentGraph.of_practices` — prefer-instance-operations — A class method named `of_practices`, none of the allowed factory names, which also makes its own practices from `PRACTICE_CATALOGUE` rather than being handed them. [3]
- session_graph.py:92, 96 `_alone: tuple[list[str], DocumentGraph]`, `_held_reads: tuple[Graph | None, dict[Path, float]]` — use-intention-revealing-names — State is still kept as positional tuples that each method unpacks (`self._alone[0]`, `held, reads = self._held_reads`); the same shape is `DocumentGraph._read` (line 33), `CheckoutWorktrees._listing` (checkout_worktrees.py:26), and `BranchChanges._held` (files/session_files.py:186). Each is a missing small object ("the graph read for these practices", "when each file was read into which graph"). [3] (still open from round 1)
- session_graph.py:159 `SessionGraph.holding(path, is_held)` — hold-state-on-the-object-not-in-parameters — The caller still works out `is_held` by scanning the session's whole graph into a `SavedGraph` (files/session_file.py:439) and hands it to the object that holds that graph. [3] (still open from round 1)
- session_graph.py:178 `SessionGraph.listed(paths)` — temporal-independence — A notification `SessionExplorer._read_listed` must remember to send after loading (files/session_explorer.py:59), or `as_it_is_now` compares against stale times; the graph does not know when it read those files itself. [3] (still open from round 1)

### space/session/handoffs.py

- handoffs.py:68 `datetime.now(timezone.utc).strftime(REPORT_DATE_FORMAT)` — eliminate-duplication — A file name's stamp is written by hand here and again in validation/validation_report.py:134, while `LogTimestamp` (harness/process), which owns `REPORT_DATE_FORMAT`, is the one time format; a change to how a stamp is written has two places to go. [2]

### space/session/chat_injections.py

- chat_injections.py:91 `_retire_shared_inject` — no-legacy-api-after-refactor — On every hook result the session still deletes `.cursor/rules/practices/chat-inject.mdc`, a file older installs wrote and nothing in the repository writes now, and the session module knows an IDE's install path. [1] (still open from round 1)
- chat_injections.py:51, 61 `payload.chat_id`, `payload.conversation_id` — use-consistent-naming — The two operations of one class read the chat's id from two different fields of the payload and take their parameters in opposite orders (`keep(result, payload)`, `replay(payload, result)`). [4] (still open from round 1)
- chat_injections.py:42 `ChatInjections.path_for` — make-module-only-operations-private — Public, used by `keep` and `replay` in this class and by harness/hooks/hook_spec.py only; no production code outside asks for it. [1]

### space/work_state.py

- work_state.py:48-52 `WorkState.load` — errors-out-of-existence — A chat's entry in `open-sessions.json` that is not an object is read as `{}`, "nothing open", rather than refused by name; `_store` (line 61) then does `dict(everything.get(self.key) or {})`, which raises a bare `TypeError` or `ValueError` for a list or a string. A file of the wrong shape is read as empty in one place and fails unnamed in the other. [3]
- work_state.py:22, 59 `_WRITING = threading.Lock()` — eliminate-duplication — The read-change-write of `open-sessions.json` is serialised by a lock of this process alone, while `JsonFile.held()` (the operating system's lock that `SessionRecord.update` uses, session_record.py:378) already serialises a read-change-write of a JSON file across processes. Two ways to do one job, and the weaker one guards a file under `~/.cdd` that every lane's server and the hook daemon can reach. [2]

### space/session/files/file_manager.py

- file_manager.py:281-297 `LANGUAGES`, `RENDERED_FORMS` — eliminate-duplication — Two tables from file suffix to a viewer's language and to its rendered form sit beside `Format.from_extension`, which `FileEntry.format` uses (line 223); one file gets its `format` from one table, its `language` from another, and its `rendered_form` from a third. [2] (still open from round 1)
- file_manager.py:465-468 `FileManager.search_again` — hold-state-on-the-object-not-in-parameters — An instance operation clears `_FILES_UNDER`, a process-wide walk cache shared by every file manager of every session; the object neither owns the state nor limits the effect to itself. [3] (still open from round 1)
- file_manager.py:30, 90 `holds_work`, `version_of` — prefer-class-operations — Module functions used only in this file (`holds_work` by `Folder.folders` and `FileManager._files_under`; `version_of` by `FileManager.read` and `write`). [3] (still open from round 1)
- file_manager.py:102, 173, 300 `FolderEntry`, `FileEntry`, `FileText` (with `SessionFile` and `Range`) — class-not-property-instance-or-subtype — Five shapes of "a file of the session" (an entry of a folder; a declared file with its listing; a file's text; the viewer's file; lines of a file), and `SessionFile` still wraps a `FileText` and repeats its `path`, `text`, `language`, and now `rendered_form` (files/session_file.py:241-259). [2] (still open from round 1)

### space/session/files/session_files.py

- session_files.py:40 `SessionFiles` — keep-classes-single-responsibility — It holds two file managers and the branch's changes, lists three folders (`in_folder`, `in_workpath`, `under_root`), reads, writes, finds (`find`, `find_each`), and checks named paths (`existing`, `from_root`, `in_root`): twelve public members for four jobs. [2] (still open from round 1)
- session_files.py:53-63 `SessionFiles.file_manager` — use-explicit-dependencies — Every `read`, `write`, and `find` works out the roots again from every practice's `folder`, `output_root`, and `output_folders` (each of which walks every fidelity's declared paths, practice_session_output.py:170) only to compare them with the held manager's roots. [3] (still open from round 1)
- session_files.py:166 `in_root` — eliminate-duplication — "Is this path under one of these roots" is written here, in file_manager.py:443, practice_session_output.py:554 and 653, and node_spans.py:109. [2] (still open from round 1)
- session_files.py:169-176 stranded comment and `UNREAD_FOLDERS` — limit-comments — A comment at line 169 describes a constant that is not below it (the one at 175 says it again), and `UNREAD_FOLDERS` here and `UNWORKED_FOLDERS` / `holds_work` in file_manager.py:26-33 are still two lists of "folders that hold no one's work" with different members. [4] (still open from round 1)
- session_files.py:200 `BranchChanges.files` — `repo.branch_named(self._session.name)` — eliminate-duplication — The branch whose changes a page filters on is found again by the session's name alone, while `SessionCheckout.branch` (session_checkout.py:49) is the one place that finds it (recorded branch, else named as the session, else the one branch holding the name as a whole word). A ticket whose branch is `claude/checkout-flow-cef4bc`, which the checkout finds, gets no branch here, so its changed-files filter reads the changes of a branch that does not exist. [2]

### space/session/files/session_file.py

- session_file.py:215 `SessionFile` — keep-classes-single-responsibility — One class reads the text, lists comments, diffs what a chat changed, folds classes, finds story steps and their callouts, opens callouts from links, and gathers violations from three graphs; the constructor reads the file and raises two refusals. [3] (still open from round 1)
- session_file.py:224-230 `SessionFile.__init__` — limit-operation-parameters — `RuleReads` is still passed in and taken apart into three fields on the next lines, an object made to pass fewer parameters and never held. [3] (still open from round 1)
- session_file.py:446 `_last_validate` — `Path(self._session.work_folder) / GRAPH_FILE_NAME` — eliminate-duplication — `SessionGraph` is documented as "the one owner of the graph file" and has `saved_file` (session_graph.py:138), but the viewer still builds the same path itself. [2] (still open from round 1)
- session_file.py:43-180 `Fold`, `FileCallout`, `FileChange`, `FileViolation` (with `StepCallout`, `FileStep` in file_steps.py) — eliminate-duplication — Six classes that are each "something on lines of the file" with the same read-only property layout; each new annotation adds a class, a regex or graph walk in `SessionFile`, and a property. [2] (still open from round 1)
- session_file.py:331, 454 `_holds(source)`, `_is_this_file(named, folder)` — eliminate-duplication — Two private methods both resolve a file a graph names, from a root or the work root, and compare it with `paths.path_named(self._path)`; one takes a `Source`, the other its parts. [2]

### space/session/files/file_steps.py

- file_steps.py:16-23, 30 `_TRIPLE_QUOTES`, `_LINE_COMMENT`, `_HASH_COMMENT`, `_BLOCK_COMMENT`, `_HASH_COMMENTED = "python"` — put-logic-on-the-owning-resource — The session's viewer knows each code language's comment and string syntax, and the literal `"python"`, while the formats (harness/markdown `Format`) and the practices' readings own the languages; and a class named `StoryTestCode` names Stories' concept in a module whose card says each practice's reading names its own steps. A new language, or a new practice with steps, changes the session module. [1]

### space/session/files/file_comments.py

- file_comments.py:110 `FileComment.state` — `Chat.load(sending.chat).mailbox.message(...)` — put-logic-on-the-owning-resource — A data property still loads a chat by id on every read of `state`, which `clear_processed`, `send_open`, and `SessionFile.changes` read for every comment; the comment reaches two objects into harness/chat to learn whether its message is done. [3] (still open from round 1)
- file_comments.py:253 `f"session={self.session_file}"` — hold-state-on-the-object-not-in-parameters — The session is written into the prompt as `session=<path>` for the agent to pass back, the "state written into a string and parsed back" the rule names; `GuidanceSelection.commands_on` does the same (practices/guidance_selection.py:266). [3] (still open from round 1)
- file_comments.py:278 `_fixes_by_lines(broken)` — prefer-class-operations — A module function used only by `FileComments.fix`, handed the broken places and building comments from them; it is the comments' own grouping rule. [3]

### space/session/files/file_range.py

- file_range.py:10 `LineSpan` — class-not-property-instance-or-subtype — `Range` now holds it instead of copying it out, but it remains a class with two public integers whose only job is to keep `Range.__init__` at three parameters, and every caller builds one only to hand it over (`LineSpan(*lines)`, `LineSpan(0, 0)`). [3] (still open from round 1)
- file_range.py:27 `Range.of_text` — prefer-instance-operations — A class method named `of_text`, none of the factory names the rule allows. [3]

### space/session/files/file_view_filter.py

- file_view_filter.py:80 `fidelity.session_output.written.holds(file) for output in outputs for fidelity in output.fidelities` — write-interactions — To ask whether any practice declares a file it still walks every practice's guidance's fidelities, back to each fidelity's session output and its written files, although `PracticeSessionOutput.holds(file)` (practices/practice_session_output.py:90) answers exactly that for a practice and nothing calls it. [3] (still open from round 1)

### space/session/files/node_spans.py

- node_spans.py:18 `NodeSpans(graph, request, root)` — hold-state-on-the-object-not-in-parameters — Made per call from the session's graph and work root by `SessionExplorer.graph_node_ranges` (files/session_explorer.py:99), then asked `file_of`, then `collect(...).spans`, in an order the caller must know; and `_kept` reads the request's `"paths"` key out of the dict again. [3] (still open from round 1)

### space/session/files/session_explorer.py

- session_explorer.py:104 `graph_node_ranges` — `self.file(...).range(start, end)` — keep-operations-single-responsibility — For each file a node covers it builds a whole `SessionFile` (a read of the file, a count of its lines, a refusal of a long one, a `FileViewFilter`) only to cut a `Range` from its text, as `add_to_chat_context` does (session.py:147); a file longer than the viewer shows makes the node's ranges fail, though no viewer draws them. [3]

### space/session/practices/practice_session_output.py

- practice_session_output.py:36, 294 `PracticeSessionOutput`, `FidelitySessionOutput` — use-intention-revealing-names — The card speaks of "the practice in the session" (`session.practice("stories")`): whether it is on, its colour, its root, its design view, its fields. "Output" names one of its jobs. [4] (still open from round 1)
- practice_session_output.py:90 `PracticeSessionOutput.holds` — delete-unused-operations — No caller in production or specs (grep of `.holds(` over the repository: space/kanban/ticket.py:1086 and files/file_view_filter.py:80 ask each fidelity's `written.holds` instead). Delete it, or make file_view_filter.py ask it. [2]
- practice_session_output.py:130, 137, 441 `enabled`, `enable(is_enabled)`, `is_enabled` — use-consistent-naming — One concept still has several words: `enabled` / `enable` here, `is_enabled` on `FidelitySessionOutput`, `PracticeFields.enabled`, `is_selected` on `PracticeSelection` (guidance_selection.py:96), `working` on `SessionPractices` (session_practices.py:37), and "on" in every docstring and the card. [4] (still open from round 1)
- practice_session_output.py:170, 590 `self.fidelities.entries.values()`, `practice.fidelities.entries.get(name)` — hide-inner-details — The practice output reads the guidance collection's storage (`entries`) instead of iterating it or asking `called(name)`; practices/guidance_selection.py:249 and spec_support/session_roots_examples.py:78 do the same. [3] (still open from round 1)
- practice_session_output.py:627 `_declared_files(label, path, changed, searched)` — limit-operation-parameters — `changed` and `searched` are the state of one listing, threaded through `files`, `_declared_files`, `_worked_on_code`, and `_found`; the missing object is the listing. [3] (still open from round 1)
- practice_session_output.py:521-608 `files`, `every_file`, `has_named_output`, `has_found_output`, `files_to_review` — keep-operations-single-responsibility — Five listings of the same declared paths, each pairing `_listed_paths` / `_listed` / `_declared` / `_found_by_pattern` / `_found` slightly differently. [2] (still open from round 1)
- practice_session_output.py:30, 670 `_OUTPUT_PATTERN_MARKS = {"*", "{"}` — eliminate-duplication — `_output_names` decides "this declared output names one file" with its own set of pattern marks, while `DeclaredFile.names_one_path` (used at lines 536, 598, 606, 636) already answers it; the fixed-folder copies round 1 found are gone, this one remains. [2] (still open from round 1)
- practice_session_output.py:688, 700 `latest_version`, `publication_of` — prefer-class-operations — Module functions that take a file and know a whiteboard's version names, its `whiteboards.json`, and a design canvas's `version-N/project/canvas.json` layout; `publication_of` is imported by space/kanban/ticket_choices.py:15. They belong on the whiteboard and the canvas that own those layouts, or on `FileEntry`. [3] (still open from round 1)
- practice_session_output.py:230, 467 `Path(os.path.relpath(Path(root).resolve(), self._session.work_root)).as_posix()` — eliminate-duplication — "A root as session.json keeps it, from the work root" is written in `PracticeSessionOutput.keep_root` and again in `FidelitySessionOutput._relative`. [2]
- practice_session_output.py:551-556, 645-655 `_writes_code_to`, `_worked_on_code` — eliminate-duplication — Both decide "a production file in a code format this fidelity writes as a folder per module, under one of its roots", with the same three tests (under a root, `_is_production_code`, suffix in `code_extensions`) written twice in different orders. [2]

### space/session/practices/guidance_selection.py

- guidance_selection.py:255 `GuidanceSelection.commands_on` — keep-classes-single-responsibility — The selection, whose job is which stages, practices, and formats are chosen, also writes each action's slash command (`/actions-{name} … session=… format=…`) from the action catalogue; the command line is the actions' knowledge, and a new command syntax changes the selection. [4]
- guidance_selection.py:172 `GuidanceSelection.start_on_ticket_stage_with` — prefer-instance-operations — A class method that replaces class-level state (`_ticket_stage`); it is no factory. [3]
- guidance_selection.py:293, 324 `def selected(fields)`, `def raised(fields)` — use-typed-signatures — The changes handed to `record.update` take an untyped `fields`, where `SessionFields` is the type every other change names (session.py:612, sessions.py:163, test_tiers.py:65); session_checkout.py:116 `opened(fields)` is the same. [3]

### space/session/practices/proposed_roots.py

- proposed_roots.py:18, 140 `_CODE_EXTENSIONS`, `code_extensions(label)` — put-logic-on-the-owning-resource — Which extensions a code format writes is knowledge of `Format` (harness/markdown), kept here as a module function that practice_session_output.py imports (lines 22, 556, 651). [3] (still open from round 1)
- proposed_roots.py:121 `_declared_files` — eliminate-duplication — Flattens `fidelity.outputs` into declared paths again, which harness's `DeclaredOutputs` already holds as `DeclaredFile` objects; lines 78, 87, and 119 then make a new `DeclaredFile(template)` for each use. [2] (still open from round 1)
- proposed_roots.py:34 `ProposedRoots._session` — use-typed-signatures — An untyped property. [3] (still open from round 1)

### space/session/practices/file_listing.py

- file_listing.py:24 `FileListing(selection, linked, is_repository, paths)` — hold-state-on-the-object-not-in-parameters — `is_repository` and `paths` are the session's own state, handed in by `GuidanceSelection.listing` (guidance_selection.py:272), which holds the session; the listing could ask the selection's session for both, and its constructor would take the selection and the link's fidelities alone. [3]

### space/session/spec_support/session_roots_examples.py and throwaway_project.py

- session_roots_examples.py:9, 16 `import cdd_guidance.practices`, `PRACTICE_CATALOGUE.create_all()` — one-way-deps — A package of `space/session` imports the practices and makes every practice as a side effect of being imported; the card says the module imports no practice (module-context.md:198). Spec support can register the practices from the spec that needs them, or live beside the specs. [1]
- session_roots_examples.py:73 `self.session.session_files.branch_changes = ChangedOnBranch(...)` — hide-inner-details — The example replaces a session part's collaborator by assigning to its public attribute after construction, which only works because `SessionFiles.branch_changes` is a public mutable field; the seam that lets a spec give a fake is the attribute itself. [3]
- throwaway_project.py:137-155 `"CDD_PROJECT"` — provide-meaningful-context — The environment variable's name is written four times as a literal here, and again in harness/mcp/mcp_server.py:898, while its sibling has a named constant (`CDD_HOME_ENV`, imported at line 14). [2]

## Design proposals

1. **One project and one branch per session.** Delete `Session.repo` and name every path from the session's own checkout (`session.checkout.repo`); `SessionPaths.from_project`, `SessionFiles`, `WrittenFiles`, and `ProposedRoots` use it, and `root_named` checks one project. `BranchChanges` asks `session.checkout.branch` instead of finding a branch by name, and `names_ticket` becomes `Branch.names_ticket(name)` in space/repo, with main's name read from one constant. Ends: `Session.repo` / `checkout.repo` (session.py:387), `BranchChanges` (session_files.py:200), `_MAIN` (session_checkout.py:17), `names_ticket` (session_checkout.py:20), and most of `Session.root` (session.py:586).
2. **Registrations through the one ClassRegistry.** The prompt queue's opening listener, the board's left-out patterns, and the board's ticket stage register through *ClassRegistry* instances held by the session module, as practices and actions do. Ends: `_opened_listeners` (open_sessions.py:65), `on_session_opened` (open_sessions.py:70), `leave_out` (session_saves.py:58), `start_on_ticket_stage_with` (guidance_selection.py:172).
3. **A file's kind and roots each answered in one place.** `Format` (harness/markdown) answers a suffix's viewer language, rendered form, code extensions, and comment syntax; a `Roots` value the session holds answers "is this path under them", "this path as kept from the work root", and is made once when the practices' roots change. `FileManager`, `SessionFiles`, `WrittenFiles`, `NodeSpans`, and `StoryTestCode` ask them. Ends: `LANGUAGES` (file_manager.py:281), `in_root` (session_files.py:166), `file_manager` roots (session_files.py:53), `code_extensions` (proposed_roots.py:140), `_writes_code_to` / `_worked_on_code` (practice_session_output.py:551), the relpath copies (practice_session_output.py:230), the comment syntax (file_steps.py:16), and the two folder lists (session_files.py:169).
4. **The session graph decides what it holds and when it read it.** `SessionGraph.holding(path)` works out whether the graph holds the file itself, `last_validated` reads `saved_file`, `load_listed(paths)` loads and records the read times in one call, and its tuples become small named objects. Ends: `holding(path, is_held)` (session_graph.py:159), `listed` (session_graph.py:178), the tuples (session_graph.py:92), `_last_validate` (session_file.py:446), and `DocumentGraph.of_practices` (session_graph.py:38, by handing it the session's practice classes).
5. **A file's lines without the viewer.** `FileText.range(start, end)` (or `SessionFiles.range(path, start, end)`) cuts a `Range` from a file's text; `add_to_chat_context` and `graph_node_ranges` use it instead of building a `SessionFile`, and the "fill a chat's prompt" call is one operation of harness/chat used by both tools and `FileComments`. Ends: `add_to_chat_context` (session.py:145), `graph_node_ranges` (session_explorer.py:104), and with `LineSpan` held as a value of `Range` alone, `LineSpan` (file_range.py:10).
6. **The session's parts are private and its folders are never None.** The session publishes named operations for what other modules do today through its parts (`session.close_record()`, `session.archive()`, `session.keep_file(file)`, `session.violation_history`), its folder moves happen on the session, which tells its sessions, and every write to the record folder goes through the record, which queues its save. With the record folder given at construction, the `| None` types and guards go. Ends: `_make_parts` (session.py:399), the two part conventions (session.py:401), the optional folders (session.py:409), `record.saved` (session_record.py:417), `_move_to` (session_folder.py:107), and the spec's attribute swap (session_roots_examples.py:73, by a constructor argument for the branch changes).
7. **Process state held by the served sessions.** `CallSessions` holds each checkout's `Sessions`, which hold their saves, their answers, their file walk cache, and their guidance-changed condition; `Sessions.of_project` becomes an instance operation of `SERVED_SESSIONS`. Ends: `ANSWER_READS` in the record (session_record.py:369), `SERVED_SAVES` and the other module-level state (session_saves.py:179), `search_again` (file_manager.py:465), and `Sessions.of_project` (sessions.py:56).
