# Judgment, round 2: space/kanban and space/repo

**Area:** `kanban-repo`: the production files of `space/kanban` (Python, the CDD Kanban app's `app/`, and the board's story-test support kept beside the code) and `space/repo` changed since 2026-11-21 (base `66f410de3`), judged at `5d16245ff` on branch release-1-2-fixes.

**Read:** every one of the 59 files in `kanban-repo.txt`, in full, at its current content; the module cards and models of `space/kanban` and `space/repo`; the first round's `judge-round/judgment-kanban-repo.md`; the Clean Engineering code and model rules, `.claude/rules/coding.md`, and the refactor guardrails. Specs were read only to see how a class is used.

**Method:** each file was judged whole, not only its changed lines, as the first round did. Every "unused", "only used inside", and "no caller" claim was checked with a repository-wide grep. A finding the first round also made (same file, same rule, same problem) ends in "(still open from round 1)"; where the first round's problem is smaller now, the finding says what is left. `oss_portal_domain_driven` was left out. Nothing was changed.

Theme tags: **[1]** module boundaries, **[2]** the same work in different shapes, **[3]** resource orientation, **[4]** domain orientation.

What the fixes since round 1 ended, so it is not repeated below: `Leaving` models the close's choices and refuses an unknown step; `Work` is the one base of `FidelityProgress` and `StageWork`, and the page no longer adds `format=`; `FidelityProgress` keeps no doubled fields, takes no `entries`, and its inner steps are private; `TicketPrompts` and `ViolationPrompts` carry the prompts the page used to write; `Stage.ticket_count` gives the head its count; `can_edit` and `parent_choices` come from Python; `BacklogFolder` and `IdeaPlace` own most of the Backlog's layout; the board's own file panel is gone and every file opens in the Files app; `Board(sessions)` takes its sessions; `Card.move_after`, `BoardFile.set_sends_fixes_directly`, the renamed `…Error` failures and the four lookup failures that keep their rejected name; in `space/repo`, `Worktree` is gone (each checkout is a `Repo`), `default_branch` is a `Branch`, `Branch.is_checked_out` means any checkout, `linked_worktree`, `save(push=)`, `commit_all`, `GitFacts` behind `repo.checkout`, `MadeRepository`, `SiblingRepo` holding a `Repo`, `keep_session_logs_by_union`, and `switch_to` and `marked_checkout` deleted.

## Counts

- **Files read:** 59
- **Findings:** 68
- **Still open from round 1:** 38 (30 new)
- **Design proposals:** 7

| Rule | Findings |
|---|---|
| eliminate-duplication | 11 |
| single-boundary | 11 |
| hold-state-on-the-object-not-in-parameters | 4 |
| use-typed-signatures | 4 |
| use-intention-revealing-names | 4 |
| hide-inner-details | 4 |
| prefer-class-operations | 4 |
| use-consistent-naming | 3 |
| keep-classes-single-responsibility | 2 |
| keep-operations-single-responsibility | 2 |
| temporal-independence | 2 |
| use-explicit-dependencies | 2 |
| build once, keep it (guardrail 1) | 2 |
| high-cohesion | 2 |
| layer-separation | 1 |
| do-not-invent-parallel-object-models | 1 |
| prefer-instance-operations | 1 |
| one-way-deps | 1 |
| deep-module | 1 |
| domain-exception-carries-context | 1 |
| class-not-property-instance-or-subtype | 1 |
| delete-unused-operations | 1 |
| never-swallow-exceptions | 1 |
| low-coupling | 1 |
| shape-classes-around-resources | 1 |

**Count by theme:** [1] 20, [2] 13, [3] 22, [4] 13 — 68 findings.

## Findings

### space/kanban/ticket.py

- ticket.py:408 `Ticket` — keep-classes-single-responsibility, shape-classes-around-resources — [3] A ticket is still spread over six mixed-in bases and five parts. `TicketMoves` (:748), `StageMarks` (:914), `TicketTree` (ticket_tree.py:438), and `TicketCheckout` (ticket_checkout.py:95) hold nothing but `_ticket` (and the checkout a `_repo` taken from it) and do their work by reaching through `self._ticket.session…` and `self._ticket.board…`. The branch, worktree, and chat now belong to `session.checkout`, which is the right owner; the stage marks and the tree are still doers acting on the ticket. (still open from round 1)
- ticket.py:168 `TicketCheckoutTools`, ticket.py:219 `TicketMoveTools` — layer-separation — [1] `branch`, `work_branch`, `close_choices` (:181-205) and `move_next`, `move_previous`, `move_to` (:229-245) only forward to `self.checkout` and `self.moves`, so a signature change is still made in two places. (still open from round 1)
- ticket.py:173-176, :262-267, :306-310, :380-382 mixed-in bases — hide-inner-details — [1] Each base declares the attributes of the class it is mixed into and reads them freely. `TicketTextTools` now declares `_refuse_main: Callable` (:382), a private operation of another base (`TicketEnding._refuse_main`, :312), which is itself a one-line forward to `session.refuse_if_main`. `TicketMoveTools.move_before` (:252) still works only because `Card` comes later in `Ticket`'s base order. (still open from round 1)
- ticket.py:434 `_remember`, :440 `forget_reads`; board.py:339 `CardPlacement.reread`; ticket_checkout.py:175, :266, :279 `sessions.worktrees.forget()` — temporal-independence — [3] Every operation that writes must still remember to drop what was worked out before: 20 production call sites now (ticket.py:197, :215, :285, :296, :364, :391, :401, :911, :1261; backlog_item.py:183, :263; board.py:387, :393; ticket_checkout.py:166, :175, :266, :267, :279; ticket_choices.py:99). The kept answers are still named by strings (`"parent"`, `"column"`, `"is_done"`, `"is_active"`). (still open from round 1)
- ticket.py:1259 `FidelityProgress._report_read_again` — temporal-independence — [3] `FidelityProgress` keeps four answers in `cached_property`s (`latest_report` :1195, `_has_files` :1146, `_violation_count` :1207, `_accepted_count` :1214) that `forget_reads` does not reach, so after an acceptance the only way to read the report again is to build a copy of itself from its own fields. A second kept-answers mechanism beside `_remember`, with its own way to be forgotten.
- ticket.py:50 `GRAPH_RULE_VIOLATION` — single-boundary — [1] The board still decides a validate failed by finding the word `graph-rule` in a log line (:1058); the Validate action writes it as its own literal (`cdd_guidance/actions/validate/validate.py:201`). (still open from round 1)
- ticket.py:51 `MOVED_INTO`, :54 `StageMark` — use-intention-revealing-names — [4] Done and in progress are now a `StageMark` enum, but entering a stage is still the bare string `"move"`, passed as `None` to `_write(None, stage)` (:953, :966, :971-972), and `latest_in` searches the log for `MOVED_INTO` beside the enum's values (:942-943). The closed set of three is now two kinds of value. (still open from round 1)
- ticket.py:98 `TicketPrompts._in_session`; report.py:61 `_in_session` — eliminate-duplication — [2] How a prompt names its session (`session=<file>`) is written in ticket.py:107, report.py:64, `space/session/practices/guidance_selection.py:266`, `space/session/files/file_comments.py:253`, the board page (`board-page.ts:120`), and the chat bar (`harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts:360`, which also writes `TicketPrompts.handoff`'s text again word for word). Six places know how a session is named in a prompt, and the session is written into a string for the chat to parse back. (still open from round 1)
- ticket.py:87 `_ticket_stage_of`, :95 `GuidanceSelection.start_on_ticket_stage_with(...)` — prefer-class-operations — [3] A module function that loads a whole board (`Board.load(session.sessions.root)`) and makes a `Ticket` to answer one session's stage, registered with `space/session` as a side effect of importing `ticket.py`. Every guidance selection that asks builds a board for it, and whether the hook is set depends on `ticket.py` having been imported.
- ticket.py:72-84 `_generate`, `_validate`, `_needing_output` — prefer-class-operations — [3] Three module functions that ask the global `ACTION_CATALOGUE` for a step's name, called 15 times in the file; `Stage.steps` (board.py:612) already answers the same steps from the same catalogue, so the stage a fidelity is required by is the object that should answer them.
- ticket.py:505 `_read_parent`, board.py:261 `Board.active`, ticket_tree.py:463-466 — hold-state-on-the-object-not-in-parameters (a name passed so the receiver looks up an object) — [3] `placement.ticket(name)` still makes a new `Ticket` on each call (board.py:347), so one board read holds several `Ticket` objects for one session, each with its own kept answers, and `parent_choices` compares by name because "its parent is a ticket of its own, never one of the board's ticket objects" (ticket_tree.py:463). (still open from round 1)
- ticket.py:1069 `FidelityProgress.load` — hold-state-on-the-object-not-in-parameters — [3] It takes no `call` and reads its ticket with `Ticket.load(ticket, project=project)`, so every `fidelity-progress.*` tool reads the board for no chat: `board.chat` is empty and `Chats.load` gets no call. This is the case the rule names, a call started inside another that nobody hands the value to. `Ticket.load` and `Stage.load` both take `call`.
- ticket.py:579 `parent_choices -> list[str]`, :586 `drop_targets -> list[str]`; backlog_item.py:125 `ticket -> str`, :132 `parent -> str`, :154 `parent_choices -> list[str]` — use-typed-signatures — [4] These answer names where the object exists; `@data_field(reference=True)` sends an object by its name and is used beside them (:543, :1077). `BacklogItem.parent_choices` is new since round 1 and repeats the shape. (still open from round 1)
- ticket.py:647 `Ticket.worktree -> str`, ticket_checkout.py:117 `TicketCheckout.worktree -> str` — use-typed-signatures — [4] A ticket's worktree is a `Repo` in `space/repo` (`Board.worktrees: dict[Branch, Repo]`), but the checkout turns it into a string, `is_open` tests `bool(self.worktree)` (:575), and `_chat_in_worktree` builds a `Path` from it again (ticket_checkout.py:140). The published field can stay a path; the operations inside the board should hold the `Repo`.
- ticket.py:735 `OverviewTicket`; board.py:845 `BoardOverview`, :895 `BoardPractice`, :925 `ColumnOverview` — do-not-invent-parallel-object-models — [2] `OverviewTicket` is now a subclass of `Ticket`, which is the right shape, but `BoardOverview` and `ColumnOverview` still declare `project`, `practices`, `fidelities`, `columns`, `active`, `name`, `kind`, `scope`, `actions`, `work_required`, and `tickets` again, only so the chat bar gets a smaller answer. (still open from round 1)
- ticket.py:1313 `ActionStates.taken_together` — prefer-instance-operations — [3] A `@classmethod` whose name is none of the factory names the rule allows (`from_*`, `create`, `load`, `every`, …); it combines instances, which `_with` (:1324) already does on the instance.
- ticket.py:1183, :1318, :1331, :1171 `ActionStates`, `FidelityProgress.state` — use-intention-revealing-names — [4] An action's standing is the bare strings `"to_do"`, `"in_progress"`, `"done"`, and a fidelity's state another closed set of strings (`"done"`, `"violations"`, `"in_progress"`, `"not_started"`), compared by string in `_state_with` and in the page (`tile-actions-client.ts:346`, `ticket-work.ts:276`), in the same file that just made `StageMark` an enum for the same reason.

### space/kanban/ticket_checkout.py

- ticket_checkout.py:182 `keep_landing_release` — keep-operations-single-responsibility — [1] Closing a ticket with a merge still publishes end-to-end screenshots and deletes older releases' results (`LatestRelease(...).keep()`), the ticket's name standing for "the release". (still open from round 1)
- ticket_checkout.py:275-277 `_delete_branch`, :281-290 `return_to_default_branch` — eliminate-duplication — [2] Both decide "this branch is checked out here and this checkout is not a linked worktree, so check out the default branch" and do it, each written out with its own comment.
- ticket_checkout.py:199 `refuse_edits_merge_would_overwrite` — eliminate-duplication — [2] `checkout.root.resolve() == clone.root.resolve()` asks whether the branch's checkout is the main clone, which `Repo.is_main_clone` (repo.py:222) answers. Round 1's two copies (:272, :283) are gone; this one was added since. (still open from round 1)

### space/kanban/board.py

- board.py:314 `CardKinds`, :328 `CARD_KINDS`, `__init__.py` — one-way-deps — [1] `board.py` still makes tickets and backlog items through a registry filled at package import, while `ticket.py` and `backlog_item.py` import `board.py`; the two-way dependency is out of sight, not gone. (still open from round 1)
- board.py:331 `CardPlacement`, :131 `Board.shared`, :185 `Board.reads` — use-intention-revealing-names — [4] The seam names still say how the board is built (`shared`, `reads`, `placement`) rather than what a caller gets (the board's file, this read's cards). (still open from round 1)
- board.py:189-238 `Board.worktrees`, `chats`, `tickets`, `backlog_items` — deep-module — [1] Four public properties that forward to `self.reads`; in production only the board's own classes and `ticket_checkout.py` read them. Two of round 1's six (`branches`, `ticket_names`) are gone. (still open from round 1)
- board.py:240 `Board.backlog_folder` — build once, keep it (guardrail 1) — [3] Each access builds a new `BacklogFolder`, and `BacklogItem.__init__` asks it once for every item of every read (backlog_item.py:63). Beside it the board still hands out the bare path, `sessions.backlog_folder`, which `BacklogItem.create` and `from_ticket` use (backlog_item.py:79, :93), so the Backlog's folder has two names.
- board.py:411 `BoardFile._held -> dict` — use-typed-signatures — [4] The fix-sending choice has its named operation now, but the file's content is still an untyped dict read by the string keys `"wip_limits"`, `"order"`, and `"sends_fixes_directly"` in six places (:416, :424, :428, :432, :436). (still open from round 1)
- board.py:43 `FORGE`, :788 `Help.href` — single-boundary — [1] Where the catalog is published is still a constant of the board, which only links to it; the catalog generator names each page. (still open from round 1)
- board.py:487 `BoardReads.chats` — use-explicit-dependencies — [3] `Chats.load()` is called with no call, while the board holds its `call` (:123) and `Ticket.new_chat_link` (ticket.py:671) loads `Chats.load(self._board.call)`. The board lists chats as no caller, and opens new ones as its caller.

### space/kanban/backlog_item.py and backlog_folder.py

- backlog_item.py:79-82 `create`, :93 `from_ticket`, :150 `children` — eliminate-duplication — [2] `BacklogFolder` and `IdeaPlace` now own most of the layout, but `create` still builds the new file's path and tests "a file, or a folder of its name" itself, `from_ticket` writes `<backlog>/<name>/<name>.md` by hand, and `children` decides siblinghood by comparing parent folders. The layout is still decoded outside its owner. (still open from round 1)
- backlog_item.py:132 `BacklogItem.parent`, :240 `_idea` — build once, keep it (guardrail 1) — [3] `parent` makes a whole `BacklogItem` (`placement.make_backlog_item(parent_file)`, which builds a `BacklogFolder` and an `IdeaPlace`) to read one title, on every read of every child; `_idea` builds a new `IdeaFile` on every access, three times for a `title`, `text`, `edit_text` sequence.
- backlog_item.py:173 `start` — keep-operations-single-responsibility — [3] One operation still chooses between bringing a ticket back and opening one, moves the idea file, starts each child and reassigns its parent, removes the emptied folder, and starts a new board read. (still open from round 1)
- backlog_item.py:25 `BacklogNestingError`; ticket_tree.py:417 `ParentMovesWithChildrenError`, :424 `NotAChildError`, :431 `ParentLoopError`; ticket_choices.py:418 `FormatNotOfferedError`; repos.py:311 `UnknownVisibilityError`, :316 `PublishFailedError`, :320 `InstallFailedError` — domain-exception-carries-context — [4] Each keeps only its message: the child, parent, ticket, chip label, or visibility it rejected is in the text and nowhere a caller can read it, while `ColumnNotFoundError`, `TicketWorktreeBlockedError`, and `IdeaHeldError` keep theirs as fields.
- backlog_folder.py:304 `BacklogFolder.folder`, :330 `IdeaPlace.file` — hide-inner-details — [3] Public, writable attributes; `IdeaPlace._move_into` reassigns `file` (:402) and `BacklogItem` reads it as its own path (backlog_item.py:236), so the class that is "the only mover" of the file lets every caller set where it is.

### space/kanban/ticket_choices.py and format_choice.py

- ticket_choices.py:427 `TicketChoices` — use-intention-revealing-names — [4] Two of its six tools still list files (`fidelity_files` :439, `root_files` :451) and choose nothing. (still open from round 1)
- format_choice.py:535 `FormatChoice.offered_by(read: list[tuple[FidelityGuidance, dict[str, list[FileEntry]]]])` — use-typed-signatures — [4] A bare list of pairs on the seam, unpacked again into a dict keyed by slug (:537) and a fidelity list (:538); and a `@classmethod` not named as the factories `prefer-instance-operations` allows.

### space/kanban/report.py

- report.py:215 `Report.leaving_out` — hide-inner-details — [3] Still a setter that returns `self`, called straight after construction at both places a report is made (:213, :355). (still open from round 1)
- report.py:176 `ReportSource`, :184 `SavedGraphStanding` — class-not-property-instance-or-subtype — [2] Still two classes with no behaviour, taken apart again in the constructor (:198-205). (still open from round 1)
- report.py:282 `ReportFile` — single-boundary — [1] The class that reads a session's saved report and decides which rules it answers for still sits in the board, while the session owns the reports folder, the accepted violations, and the judgment's format. (still open from round 1)
- report.py:67 `_error_lines(violation)` — prefer-class-operations — [3] A module function that reads only the violation it is handed (its location, line, message, and source); where a violation is and what surrounds it is the violation's to say.
- report.py:160 `ReportRule.violation_prompts`; report-client.ts:447 `promptsOf` — hide-inner-details — [4] The prompts are sent as a second list beside `violations`, matched by position, and the page pairs them back with `rule.violations.indexOf(violation)`. Two lists kept in step by order are the storage leaking to the caller; each violation as shown could carry its own prompts.
- report.py:166 `ReportRule.fix_prompt`, :242 `Report.fix_prompt` — eliminate-duplication — [2] The same sentence ("Fix all violations … found in this report: {path}. {_EVERY_FORMAT} {_KEEP_BEHAVIOUR}") written twice, one with the rule's name.

### space/kanban/progress_cache.py

- progress_cache.py:67 `ProgressCache.kept`, :72 `keep` — hold-state-on-the-object-not-in-parameters — [3] Both take the fidelity that `FidelityAnswers` (:114) already holds, and `FidelityAnswers.answer` is their only caller; the answer is kept as an untyped `{"key": …, "value": …}` dict built in one class and taken apart in the other.
- progress_cache.py:156 `SessionSaves.leave_out(...)`; ticket.py:1157, :1225 `PROGRESS_CACHES.of(...)` — use-explicit-dependencies — [3] `FidelityProgress` reaches the process-wide cache registry from inside two operations rather than holding its session's cache, and the cache file is left out of session saves as a side effect of importing the module.

### space/kanban/board_app.py

- board_app.py:522 `Stories.editor = STORY_UI_APP` — single-boundary — [1] Importing the board still sets a class attribute on a practice of `cdd_guidance`, so `BoardFidelity.editor` and `BoardPractice.editor` answer only once `space.kanban` has been imported. (still open from round 1)

### space/kanban story-test support (`*_examples.py`, `*_tiers.py`, `story_test.py`) and `app/test-utils`

- graph_view_examples.py, graph_view_rule_examples.py, knowledge_graph_examples.py, editor_apps_examples.py, editor_apps_tiers.py, story_test.py — high-cohesion — [1] The story-test support of the Files app, the Graph app, and the editor apps lives in the board's module (14 story-test folders outside the board import it), and `cdd_guidance/practices/stories/model/python/shared_story_file.py:7` names `space.kanban.session_board_examples`. The card's "No Python module imports the board" holds only because these are counted as spec support. (still open from round 1)
- session_board_examples.py:1-20 and app/test-utils/fixture-repo.ts:15-83 — eliminate-duplication — [2] The same seed (ticket names, titles, log lines, the story map, its saved graph and report) is written twice, in Python and in TypeScript, kept in step only by a docstring that says they match.

### space/repo/repo.py

- repo.py:131 `Repo.is_linked_worktree`, :222 `Repo.is_main_clone` — use-consistent-naming — [4] Two names for one question, each a one-line forward to `Checkout`; callers pick either (`ticket_checkout.py:276`, `:288`, `open_sessions.py:124` use one, `repo.py:497` and `repos.py:409` the other). Round 1's proposal named one to keep.
- repo.py:87 `Repo.checkout`, :518 `Branch.checkout` — use-consistent-naming — [4] `repo.checkout` is the harness `Checkout` that reads git's facts; `branch.checkout` is the `Repo` that has the branch out; `repos.py:393` reads `repo.checkout.branch`, a string, where `repo.current_branch` is the `Branch`. One word for two types on the two classes callers hold together. (still open from round 1)
- repo.py:126 `Repo.checkout_folder` — delete-unused-operations — [1] No caller in production or specs; only `repo-model.md` and `space/session/session-sketch.md` name it.
- repo.py:367 `WorkingTree.is_merging` — single-boundary (one owner per file) — [1] It reads `<root>/.git/MERGE_HEAD` itself while `Checkout` and its `GitFacts` own reading `.git`. In a linked worktree `.git` is a file, so this answers false in every ticket's worktree, and `commit` (:376) then names paths during a merge instead of concluding it. `MockWorkingTree` overrides it, so no quick spec sees this.
- repo.py:405 `Publishing.push_commit`, :422-429 `take_work_to_main`; repo.py:542 `Branch.save` — eliminate-duplication — [2] Round 1's four ways to commit and push a checkout are down to three: `push_work` and `Repo.close` use `Branch.save`, but `push_commit` still passes `[str(repo.root)]` to `commit` and pushes on its own, and `take_work_to_main` commits with `commit_all` and pushes with its own conditions. (still open from round 1)
- repo.py:227 `Repo.catch_up_with_origin` — never-swallow-exceptions — [3] A failed fetch or merge is logged and the checkout is answered as if opened up to date; `Worktrees.open` (worktree.py:108, :111) and `_added_from_origin` (:123, :127) return it and no caller learns it is behind origin. Round 1's `sync_failure` was deleted rather than given a reader, so the failure now goes nowhere a person sees.
- repo.py:24 `_RUNTIME_LOG`; origin.py:170 `_UNION_MERGED_LOGS`; new_repository.py:286 `CDD_WRITTEN_PATTERNS` — single-boundary — [1] The repository module still holds the names of files other modules own: the hook server's `events.log`, the sessions' `session.log` and `session.err`, and every path CDD writes into a project, including `progress-cache.json` and `graph.json`. (still open from round 1)

### space/repo/worktree.py

- worktree.py:181-257 `Worktrees.remove` and five helpers — keep-classes-single-responsibility — [3] About 75 of the class's lines still delete a folder Windows holds locked (`takeown`, `icacls`, long paths, PowerShell), and `remove` builds its `HookDaemon` inside (:189). (still open from round 1)

### space/repo/new_repository.py

- new_repository.py:394-411 `_commit_first`, `ignore_as_cdd_does` — eliminate-duplication — [2] Both run `git add` and `git commit` through `repo.git.run` beside `WorkingTree.commit` and `commit_all`, which every other commit goes through and which hold the repository's `writing_index` lock; these two commit without it.
- new_repository.py:281 `DEFAULT_BRANCH = "main"`; repos.py:487 — eliminate-duplication — [2] A second default-branch name beside `_DEFAULT_BRANCH_NAMES` (repo.py:26) and `repo.default_branch`; `Repos.open` also uses it as the new repository's main session's name. (still open from round 1)

### space/repo/repos.py

- repos.py:355 `CddConfig` — high-cohesion — [1] A general reader and writer of `~/.cdd/config.json` by string key still lives in the repository module, which uses one key of it. (still open from round 1)
- repos.py:402 `SiblingRepo.has_cdd` — single-boundary — [1] Whether CDD is installed is decided by the repository module testing for `.claude/commands`, a folder the installer owns and names.
- repos.py:337 `RepositoryChat.first_prompt`, ticket.py:135 `TicketPrompts.new_chat` — eliminate-duplication — [2] Both now open their chat through `Chats.new_chat`, which ends round 1's three mechanisms, but both still word the same instruction ("call sessions.switch with name X") separately. (still open from round 1)

### space/kanban/app/src/kanban (the page)

- board/board-page.ts:34-53 — low-coupling — [1] Clients are still given the whole `BoardPage` (`TileClient`, `TileActionsClient`, `OpenCardClient`, `ActivationClient`, `RootChoiceClient`, `BacklogDraftClient`, `PageLinks`, `BoardReader`, and every `TicketClient` part) and reach `page.store`, `page.chat`, `page.board`, `page.reader`, and each other through it. (still open from round 1)
- ticket/ticket-client.tsx:164-171 — shape-classes-around-resources — [3] `TicketClient` still makes eight helper objects per ticket per read, each given the ticket and the whole page; `chat` (:220) makes a new `TicketChat` on every access. (still open from round 1)
- board/board-page.ts:118-121 `openNewTicket` — single-boundary — [1] The one agent prompt the page still writes itself, with the tool name `ticket.create` and the `session=` word in it; every other prompt now comes from `TicketPrompts` or `ViolationPrompts`. (still open from round 1)
- ticket/ticket-work.ts:269 `TicketWork` — use-consistent-naming — [4] The page's `TicketWork` and Python's `TicketWork` (ticket.py:829) are still different things under one name across the generated adapter. (still open from round 1)
- ticket/tile-actions-client.ts:312, :327-349 `BarWork`, `reportOf`, `chipFaceOf`, `stepFaceOf`, `validateFaceOf` — prefer-class-operations — [3] Module functions that take the record they work on; `chipFaceOf(tile, choice)` takes a `tile` it never reads. `BarWork` still joins two generated types by hand where Python now has their `Work` base. (still open from round 1)
- ticket/tile-actions-client.ts:425-428 `commandOf` — hold-state-on-the-object-not-in-parameters — [3] The tile holds its `TicketClient`, but that client is the read the tile was opened on, so `commandOf` finds the ticket again by address in the current board. A tile that holds a stale ticket and a lookup that corrects it are the service-and-record pair round 1 named for `Tile`.
- board/editor-app-client.ts:269-280 — eliminate-duplication — [2] The Files app's query words (`files`, `fidelity`, `session-folder`, `workpath-folder`, `session`, `file`, `line`) are copied here with a comment pointing at `harness/files_app/app/files/files-paths.ts`, which exports each of them; a rename there leaves this link silently wrong.
- board/column-client.ts:160-163 `limitFrom` — single-boundary — [1] "A WIP limit is a whole number of at least one" is a rule only the page keeps; `Stage.set_wip_limit` (board.py:689) and `BoardFile.set_wip_limit` take any integer, so an agent can set 0 or a negative limit.
- ticket/card-upkeep-view.tsx:402 `AddChildView` — single-boundary — [1] Round 1's main-only rules now come from `can_edit`, except this one: the page turns off Add child for main, and `TicketTreeTools.add_child` (ticket.py:272) does not refuse main. (still open from round 1)
- ticket/card-upkeep-view.tsx:438-439 `TicketTextView` — single-boundary — [1] The page finds a ticket's idea file by replacing `session.json` with `<name>.md` in the session file's path, decoding the session folder's layout, which `space/session` owns (`Session.keep_text`, `Session.text`).

## Design proposals

1. **One way a prompt names its session.** A session answers `session.prompt(text)`, the one place `session=<file>` is written; `TicketPrompts`, `ViolationPrompts`, `ReportRule`/`Report.fix_prompt`, `GuidanceSelection.commands_on`, and `FileComments` call it; the board sends a `new_ticket` prompt with the board's active ticket, and `RepositoryChat` and `TicketPrompts.new_chat` share one "open the session" sentence. Ends: ticket.py `_in_session` (session= in six places), report.py `fix_prompt` copies, repos.py `RepositoryChat.first_prompt`, board-page.ts `openNewTicket`.
2. **One read object per board read.** `CardPlacement` makes each ticket once per read and answers the same object by name; a ticket's worked-out answers, and its `FidelityProgress`'s, live in that read and go with it when a write starts a new read, so `_remember`/`forget_reads`, the `cached_property`s, and the copy in `_report_read_again` go. Ends: ticket.py `_remember` (temporal-independence), `_report_read_again`, `_read_parent` (name lookups), and the `parent_choices` name comparison.
3. **`Repo` answers each checkout question once.** Keep `is_main_clone` and delete `is_linked_worktree`; rename `Branch.checkout` to say it is the `Repo` that has the branch out; move `is_merging` onto `GitFacts`; route `Publishing.push_commit`, `take_work_to_main`, and `NewRepository`'s commits through `WorkingTree.commit_all` and `Branch.save`; delete `checkout_folder`; give `TicketCheckout` one "leave this branch for the default" operation. Ends: repo.py `is_linked_worktree`/`is_main_clone`, `Repo.checkout`/`Branch.checkout`, `checkout_folder`, `is_merging`, the commit-and-push shapes, new_repository.py raw commits, ticket_checkout.py `_delete_branch`/`return_to_default_branch` and the root comparison at :199.
4. **The Backlog owns its whole layout.** `Board` holds one `BacklogFolder`; it answers `new_idea(title)` (the taken check included), `idea_of(ticket)` for a ticket shelved with its folder, and each `IdeaPlace` answers its children and holds its `IdeaFile`; `IdeaPlace.file` becomes read-only. Ends: board.py `backlog_folder`, backlog_item.py `create`/`from_ticket`/`children`, `parent`/`_idea`, backlog_folder.py public attributes.
5. **A report sends each violation whole.** Each violation shown carries its prompts and where it is (`_error_lines` moves onto `Violation`); `Report` takes its path, text, standing, and accepted rules in its constructor, and `ReportSource`, `SavedGraphStanding`, and `leaving_out` go. Ends: report.py `leaving_out`, `ReportSource`/`SavedGraphStanding`, `_error_lines`, `violation_prompts` with the page's `indexOf`, and the doubled `fix_prompt`.
6. **The last page rules move to Python.** `Stage.set_wip_limit` refuses a limit under one with a named failure; `Ticket` sends `can_add_child` and its idea file's path, and `add_child` refuses main; `editor-app-client.ts` imports the Files app's query words. Ends: column-client.ts `limitFrom`, card-upkeep-view.tsx `AddChildView` and `TicketTextView`, editor-app-client.ts query copies.
7. **Story-test support lives with what it tests.** The Files app's, Graph app's, and editor apps' examples and tiers move to `harness/files_app` and `harness/apps`; the board's seed is written once, as data both `session_board_examples.py` and `fixture-repo.ts` read. Ends: the high-cohesion finding on the example files and the doubled fixture seed.
