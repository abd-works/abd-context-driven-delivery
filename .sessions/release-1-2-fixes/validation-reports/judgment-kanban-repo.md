# Judgment: space/kanban and space/repo

Judged against the Clean Engineering rules (modules, model, code) and the refactor guardrails, on the worktree `C:\dev\abd-cdd-release-1-2-fixes` at `bba27fc5b`. Every production file of `space/kanban` (Python and `app/`) and `space/repo` was read; specs were read only to see how a class is used. Each finding was checked against the code at the line given. Nothing was changed.

Theme tags: **[1]** module boundaries, **[2]** the same work in different shapes, **[3]** resource orientation, **[4]** domain orientation.

What holds up, so it is not repeated below: the board's server mounts only generated routes (`app/packages/session-board/app.ts`); the page posts only through the generated clients and `BoardApi`; `allowed_actions`, `next_place`, `previous_place`, `drop_targets`, `parent_choices`, and the close choices are answered by Python and only drawn by the page; `Repo` makes its parts once; no production code outside `space/kanban` imports the board's domain classes.

## Findings

### space/kanban/ticket.py

- ticket.py:317 `Ticket` — keep-classes-single-responsibility, shape-classes-around-resources — [3] One ticket is spread over eleven helper classes: six mixed-in bases and five parts. Three of the parts hold no state except `_ticket` (`TicketMoves` :637, `StageMarks` :810, `TicketTree` ticket_tree.py:34) and do their work by reaching through `self._ticket.session…` and `self._ticket.board…`, so they are doers acting on a ticket, not objects that own state. The split lowered `Ticket`'s method count without finding who owns the state: the session's stage record, the session's hierarchy, and the branch's checkout.
- ticket.py:136 `TicketMoveTools`, ticket.py:88 `TicketCheckoutTools` — layer-separation — [1] `move_next`, `move_previous`, `move_to` (:145-161) and `branch`, `work_branch`, `close_choices` (:98-122) only forward to `self.moves` and `self.checkout`. CDR 0004 round 3 removed exactly this forwarding for three other bases ("no tool base that only forwards") and left these two, so a signature change is still made in three places.
- ticket.py:92, :140, :178-183, :222-226, :292-293 mixed-in bases — hide-inner-details — [1] Each base declares the attributes of the class it is mixed into (`checkout`, `forget_reads`, `board`, `session`, `tree`, `parent`, `moves`) and reads them freely. `TicketMoveTools.move_before` (:168) calls `super().move_before(other)` and only works because `Card` comes later in `Ticket`'s base order (:317). The bases cannot be read or tested apart from `Ticket`, so they are files of `Ticket`'s body, not units.
- ticket.py:343 `_remember`, :349 `forget_reads`, board.py:335 `CardPlacement.reread` — temporal-independence — [3] Every operation that writes must remember to drop what was worked out before: 14 call sites (ticket.py:114, :131, :201, :212, :277, :301, :310, :807, :1136; ticket_checkout.py:160, :257; ticket_choices.py:91; backlog_item.py:293, :301). A new tool that writes and leaves the call out answers a stale column, parent, or `is_done`. The kept answers are named by strings (`"parent"`, `"column"`, `"is_done"`, `"is_active"`).
- ticket.py:831, :839, :860 `StageMarks`; ticket_checkout.py:62, :117, :122, :161 — single-boundary — [1] The board reads and writes raw keys of the session's `session.json` (`stage`, `stage_mark`, `chat`, `branch`, `worktree`) through `record.fields.get(...)` and `record.save_fields(**{...})`. `space/session` reads `branch` (session.py:497) and `worktree` (session_roots.py:52) with literals of its own. Two modules own the same fields of one file, with no typed operation between them.
- ticket.py:795 `TicketWork.command(action, fidelities)` — hold-state-on-the-object-not-in-parameters — [3] It takes the action's name and the fidelities as parameters and writes the session into a string (`session=`), the shape the rule names and `space/kanban/.context/corrections.log` (2026-11-06) already corrected once. `StageWork.commands` (:1264) and `FidelityProgress.command` (:1010) both call it.
- ticket.py:800 command text — eliminate-duplication — [2] The `session=` word is written here, in `harness/guidance_actions/guidance_actions.py:82`, in `space/session/file_comments.py:239`, and in the page (`ticket-chat-prompts.ts:18`, `board-page.ts:123`); the `format=` word is added by the page (`tile-actions-client.ts:119`). Four places know how a command is spelled.
- ticket.py:46 `GRAPH_RULE_VIOLATION` — single-boundary — [1] The board decides a validate failed by finding the word `graph-rule` in a session log line (:921). The Validate action writes that word as its own literal (`cdd_guidance/actions/validate/validate.py:195`). The log line's wording is shared by two modules with no shared name.
- ticket.py:905-912 `FidelityProgress.__init__` — eliminate-duplication — [2] It keeps `_required` and also its `fidelity` and `stage` (`_fidelity`, `_stage`), and `_logged` and also its `done_actions` and `has_violations`. The same state is held twice in one object.
- ticket.py:915 `FidelityProgress.from_log(required, entries, ticket)` — hold-state-on-the-object-not-in-parameters — [3] Both callers (:748, :789) pass `ticket.work.entries`, which the ticket given as the third argument already holds.
- ticket.py:983 `done_actions`, :987 `remaining_actions`, :1123 `latest_report_or_refuse`, :1162 `with_violations`, :1166 `with_accepted_left_out` — deep-module — [1] Public, and called in production only from inside `FidelityProgress` (:929, :930, :996, :1042, :1112, :1120). Three specs read `done_actions` and `remaining_actions`, one story test calls `with_accepted_left_out`.
- ticket.py:1221 `StageWork` and ticket.py:898 `FidelityProgress` — do-not-invent-parallel-object-models — [2] Six members have the same name and meaning on both (`stage`, `action_states`, `has_violations`, `violation_count`, `commands`, `allowed_actions`) and Python gives them no shared type. The page already treats them as one (`type BarWork = StageWorkData | FidelityProgressData`, tile-actions-client.ts:14). The graph hit on this pair is real.
- ticket.py:562 `Ticket.new_chat_link` — eliminate-duplication — [2] The prompt that opens a ticket's chat is written here (:568-573), again almost word for word in the page (`app/src/kanban/chat/chat-opening.ts:10`), and a third shape of "a new chat on a folder with a first prompt" is `NewChat` in `space/repo/repos.py:64`. All three end at `links_of_run().link_to_new(...)` or `chats.open`.
- ticket.py:416 `_read_parent`, board.py:257 `Board.active`, ticket_tree.py:66-70 — hold-state-on-the-object-not-in-parameters (a name passed so the receiver looks up an object) — [3] `placement.ticket(name)` makes a new `Ticket` on every call (board.py:343, :372), so one board read holds several `Ticket` objects for one session, each with its own kept answers. The code then has to compare tickets by name; the comment at ticket_tree.py:65 says so.
- ticket.py:488 `parent_choices -> list[str]`, :495 `drop_targets -> list[str]`; backlog_item.py:144 `ticket -> str`, :151 `parent -> str` — use-typed-signatures — [4] These answer names where the object exists. `@data_field(reference=True)` is the mechanism the same classes use elsewhere to send an object by its name (ticket.py:452, :524).
- ticket.py:47-49 `MOVED_INTO`, `MARKED_DONE`, `MARKED_IN_PROGRESS`; :846 `StageMarks.mark(mark: str, stage)`; :852 `place(stage, mark: str)` — use-intention-revealing-names — [4] A stage mark is a closed set of three values passed as bare strings, and `mark("move", stage)` means "enter the stage". A caller cannot tell from the signature which strings are allowed.
- ticket.py:59, :865; report.py:22; ticket_choices.py:22 — use-consistent-naming — [4] `NoReportToAcceptIn`, `ViolationNotInReport`, and `FormatNotOffered` are the only failures in the two modules without the `Error` ending the other twenty carry.
- ticket.py:624 `OverviewTicket`; board.py:852 `BoardOverview`, :902 `BoardPractice`, :932 `ColumnOverview` — general-purpose-surface, do-not-invent-parallel-object-models — [2] A second set of classes declares `project`, `practices`, `fidelities`, `columns`, `active`, `name`, `kind`, `scope`, `actions`, `work_required`, and `tickets` again, only so one caller (the chat bar) gets a smaller answer. `Board.practices` answers `PracticeGuidance` and `BoardOverview.practices` answers `BoardPractice` for the same practices.

### space/kanban/ticket_checkout.py

- ticket_checkout.py:34 `own_worktree_of(branch)` — prefer-class-operations — [3] A module function that takes a `Branch` and reads `branch.worktree` and `branch.repo.main_clone`; it belongs on `Branch`. `space/session/session_roots.py:47` has a second `own_worktree_of(session)` that answers the same question from the session's record and its own listing.
- ticket_checkout.py:80 `candidate_branches` and space/session/session_roots.py:85 `worktree_of` — eliminate-duplication — [2] Both find "the one branch whose name holds the ticket's name as a whole word" with the same pattern, `(^|[/_-])name($|[/_-])`. The board and the session each decide which branch is a ticket's.
- ticket_checkout.py:89, :146, :229 — eliminate-duplication — [2] `branch.is_checked_out or branch.worktree is not None` is written twice, and :229 (`self._repo if branch.is_checked_out else branch.worktree.repository`) works out again what `Branch.checkout` (repo.py:501) already answers.
- ticket_checkout.py:91, :273, :285 (and repo.py:553) — hold-state-on-the-object-not-in-parameters — [3] `repo.branch_named(repo.default_branch)`: `Repo.default_branch` is a string (repo.py:185), so every caller that wants the default branch looks it up again by name.
- ticket_checkout.py:272, :283 — eliminate-duplication — [2] `self._repo.root == self._repo.main_clone.root` asks what `Repo.is_linked_worktree` (repo.py:135) already answers.
- ticket_checkout.py:259 `_work_from_main_clone` — shape-classes-around-resources — [3] After a worktree is deleted the checkout swaps its `_repo` and builds its `branch` again, because a `Branch` is tied to the checkout it was made from. The ticket carries a repair for a weakness of the repo model.
- ticket_checkout.py:175-248 `leaving: list[str]` — hold-state-on-the-object-not-in-parameters, limit-operation-parameters — [3] What the person chose when closing is a list of strings handed through nine methods (`keep_landing_release`, `write_handoff`, `save_work`, `leave_branch`, `_commit_and_push`, `_worktree_to_delete`, `_save_worktree_to_delete`, `_delete_worktree`, `_delete_branch`), each testing `LEAVE_X in leaving`. `LeaveChoices` (:310) models what is offered; nothing models what was chosen.
- ticket_checkout.py:175 `keep_landing_release` — keep-operations-single-responsibility — [1] Closing a ticket with a merge also publishes end-to-end screenshots to `e2e-latest` and deletes older releases' results (`LatestRelease.keep`). Release housekeeping is tied to the close of any ticket, by the ticket's name standing for "the release".
- ticket_checkout.py:227 `_commit_and_push`; repo.py:532 `Branch.save`; repo.py:398 `Publishing.push_work`; worktree.py:101 `Worktree.close` — eliminate-duplication — [2] Four operations commit everything in a checkout and push its branch, each with slightly different conditions (commit only when dirty; push only when origin is behind; push only when there is an origin; push whenever chosen).

### space/kanban/board.py

- board.py:310 `CardKinds`, :324 `CARD_KINDS`, `__init__.py:9` — one-way-deps — [1] `board.py` makes tickets and backlog items (`CardPlacement` :372-390, including `CARD_KINDS.backlog_item_kind.from_ticket` :390) while `ticket.py` and `backlog_item.py` import `board.py`. The registry filled at package import is an import made at run time, so the two-way dependency between the files is still there; it is only out of sight.
- board.py:327 `CardPlacement`, :122 `Board.shared`, :176 `Board.reads` — use-intention-revealing-names, abstraction-focus — [4] `CardPlacement` finds tickets, makes them, opens new ones, answers free names, and owns what the board has read; placing a card in an order is done elsewhere (`Column.place_before` :560). `board.shared` is the board's file and `board.reads` is a cache of one read. The seam names say how the board is built, not what a caller gets.
- board.py:180-243 `Board.worktrees`, `branches`, `chats`, `tickets`, `ticket_names`, `backlog_items` — deep-module — [1] Six public properties that forward to `self.reads`; in production only `ticket_checkout.py` (:66, :82, :98, :107) and the board's own classes read them.
- board.py:142 `Board.file` — deep-module — [1] Public, read only by `BoardFile` (:403, :429), which is the file's one owner.
- board.py:113-116 `Board.__init__` — use-explicit-dependencies — [3] `Board.load` holds the checkout's `Sessions` (:130) and passes only `sessions.repo` and `sessions.board_practices`; the constructor then fetches the `Sessions` again from the repo's root through `Sessions.of_project` (:116).
- board.py:401 `BoardFile._held -> dict`, :425 `keep(**values: object)` — use-typed-signatures — [4] The board file's content is an untyped dict, and `Board.set_sends_fixes_directly` writes it with a free keyword (`shared.keep(sends_fixes_directly=sends)`, :285) where WIP limits and order have named operations.
- board.py:472-486 `BoardReads.backlog_items` and backlog_item.py:241-261 — eliminate-duplication — [2] How the Backlog folder is laid out (a file; a folder holding a file of its own name; a folder that keeps a `session.json`; children beside the parent's file) is decoded twice: once to list the item paths, and again in each item (`_is_kept_in_own_folder`, `_holds_ticket`, `_parent_file`, `_held_ticket_folder`). The `Backlog` column class (:581) owns none of it.
- board.py:505 `BoardReads.backlog_item` — deep-module — [1] Public, called in production only by `backlog_item_called` (:511).
- board.py:740 `Card.move_before` and backlog_item.py:65 `BacklogOrderTools.move_after` — eliminate-duplication — [2] `Card` saves a move above another card; the move below is written out again in the backlog item's base, with its own save message.
- board.py:747 `Card._timestamp` — put-logic-on-the-owning-resource — [3] Uses nothing of `Card`; its one caller is `BacklogItem.last_activity` (backlog_item.py:180).
- board.py:44 `FORGE`, :799 `Help.href` — single-boundary — [1] The address the catalog is published at is a constant of the board. The catalog generator names each page (`catalogued.href`), but where the catalog lives is kept by a module that only links to it.
- board.py:73, :80, :55, :97 — domain-exception-carries-context — [4] `TicketNotFoundError`, `BacklogItemNotFoundError`, `NotAStageError`, and `CardNotInColumnError` keep only a message, while `ColumnNotFoundError` (:47) and `FidelityNotFoundError` (:63) keep the rejected name as a field.

### space/kanban/backlog_item.py

- backlog_item.py:75 `BacklogItem` — keep-classes-single-responsibility — [3] It is two things: an idea (its title and text, held by `IdeaFile`) and that idea's place in the Backlog folder (nine members, :241-301, that move files and folders and decide whether a folder is a ticket's work). The graph hit of 11 public operations is the smaller sign; the folder work is the second reason to change.
- backlog_item.py:30 `open_with_system` — prefer-class-operations, use-explicit-dependencies — [3] A module function called from one method (:218). The spec swaps the module attribute to stub it (kanban_spec.py:486-492), which is what a collaborator handed in would do without touching the module.
- backlog_item.py:185 `start` — keep-operations-single-responsibility — [3] One operation chooses between bringing a ticket back and opening one, moves the idea file, starts each child, reassigns their parent, removes the emptied folder, and starts a new board read.

### space/kanban/report.py

- report.py:176 `ReportFile` — single-boundary (one owner per file) — [1] The session owns the reports folder (`fidelity.session_output.validation_reports.listed()`, :193), the accepted violations (:287), and the judgment's format (`space/session/validation_judgment.py`). The class that reads a saved report and decides which rules it answers for sits in the board, so the meaning of a session's own file is kept by another module.
- report.py:125 `Report.leaving_out` — hide-inner-details — [3] A setter that returns `self`, called straight after construction at both places a report is made (:123, :251). The accepted violations are constructor state passed in a second step.
- report.py:86 `ReportSource`, :94 `SavedGraphStanding` — class-not-property-instance-or-subtype — [2] Two classes with no behaviour, taken apart again in the constructor (:110-115). They exist to bring `Report.__init__` to three parameters.

### space/kanban/ticket_choices.py

- ticket_choices.py:31 `TicketChoices` — use-intention-revealing-names — [4] Two of its six tools list files (`fidelity_files` :43, `root_files` :51) and choose nothing; the name fits the format chips and overlays only.

### space/kanban/board_app.py

- board_app.py:26 `Stories.editor = STORY_UI_APP` — single-boundary — [1] Importing the board sets a class attribute on a practice of `cdd_guidance`. `BoardFidelity.editor` (board.py:849) and `BoardPractice.editor` (board.py:929) then read it back, so the answer depends on `space.kanban` having been imported (`scripts/install.py:336` imports it for that effect).

### space/kanban/story_test.py and the tier files

- story_test.py:86 `SharedStories`, :123 `replay` — high-cohesion — [1] The Given/When/Then replay used by the story tests of the chat bar, the Files app, and the graph lives in the board's module, and `space/session/graph_view_examples.py:9` imports `space.kanban.session_board_examples`. The card says no Python module imports the board. These files and `space/repo/built_once.py` are spec support without the `mock_` or `fake_` prefix, so the deep-module measure counts them as production.

### space/kanban/.context/kanban-model.md

- kanban-model.md:624, :806, :852 — seam-names-current-code — [4] The model still gives `FidelityProgress(fidelity, stage, done_actions, has_violations, ticket)`, `Help(practice, fidelity, stage, catalogued)`, and `Report(path, text, rules, has_saved_graph)`. The code takes `(required, logged, ticket)` (ticket.py:905), `(practice, catalogued, required)` (board.py:763), and `(source, rules, standing)` (report.py:107).

### space/kanban/app/src/kanban (the page)

- shared/pending-changes.ts:150, :173-175 `withCard`, `TicketNewParent` — single-boundary — [1] To show a change before the server answers, the page decides which list a card belongs to and that a child is stacked unless its parent is closed. That is `TicketTree.is_stacked` (ticket_tree.py:49) and `Stage.in_progress`/`done` (board.py:689) written a second time. For Move next and Move previous Python sends the place (`next_place`); for a new parent and a pull-out it sends nothing, so the page works it out.
- backlog-item/backlog-item-client.tsx:47 `canTakeAsChild` — single-boundary — [1] Repeats the nesting rules of `BacklogItem._refuse_nesting_under` (backlog_item.py:263-272): not itself, no children of its own, the parent not a child, neither kept with a ticket's work. Tickets get `parent_choices` from Python; backlog items get nothing.
- ticket/card-upkeep-view.tsx:14-30 — single-boundary — [1] The page turns off add-child, edit text, tag, and delete for main. Python refuses only the delete (`MainStaysOpenError`, ticket.py:273); `edit_text` and `tag` (ticket.py:298-311) take main, so that rule exists only in the page.
- board/column-client.ts:101 `count` — single-boundary — [1] The count beside a stage leaves main out, while `Stage.is_over_limit` (board.py:685) counts every card including main. The number shown and the over-limit mark it is shown with (board-columns-view.tsx:29-30) are worked out by two rules.
- ticket/ticket-drops.ts:18, ticket/ticket-next-step.ts:25-32, board/board-client.tsx:109 — single-boundary — [1] Smaller rules kept in the page: a drop on Complete closes through the dialog only when the ticket is open; Run next sends Generate at once and puts every other action in the prompt; a closed ticket shows the last stage's fidelities.
- ticket/ticket-work.ts:38 `progressIn` — eliminate-duplication — [2] Filters a ticket's progress by stage and by enabled practice, which Python already answers as `stage_work` (`TicketWork.in_stage`, ticket.py:793); the page uses both (`workIn` :65).
- ticket/ticket-work.ts:17 `TicketWork` — use-consistent-naming — [4] The page's `TicketWork` and Python's `TicketWork` (ticket.py:711) are different things under one name on the two sides of the generated adapter.
- ticket/report-client.ts:19-53, ticket/ticket-chat-prompts.ts:5-46, chat/chat-opening.ts:10, board/board-page.ts:123 — single-boundary, eliminate-duplication — [2] The prompts an agent is sent (fix a violation, a violation is false, split a ticket, write a handoff, set up roots, open a new ticket, the first prompt of a ticket's chat) and the tool names in them are written in the page. The chat bar writes its own copies (`harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts:375`, `format-choices-client.ts:16`). Python sends the command for a fidelity's actions and nothing else.
- ticket/activation-client.ts:5 `LEFT_STEPS` — eliminate-duplication — [2] The page lists the leave steps by the same keys as `LEAVE_*` (ticket_checkout.py:22-27) to word its report; Python sends the keys with no wording.
- ticket/files-panel-client.ts:45, ticket/file-viewer-view.tsx, ticket/files-panel-view.tsx, ticket/open-file-comments.ts, ticket/file-views-view.tsx — do-not-invent-parallel-object-models — [2] About 620 lines that list, filter, show, edit, and comment on a session's files, beside the Files app (`harness/files_app/app/files/files-page.ts`, `file-comments-actions.ts`), which does the same through the same session tools. `packages/session-board/main.tsx:8` says files open in the Files app and never here, yet `details-view.tsx:49-67`, `card-upkeep-view.tsx:56`, and `report-rule-view.tsx:25` open the board's own panel.
- board/board-page.ts:128 `startFiles` — no-use-delete (guardrail 3) — [1] No caller in the app or its specs.
- ticket/tile-client.ts:63-80 `change`, `openOn`, `isOpen`, `close`, `pin` — hold-state-on-the-object-not-in-parameters — [3] Each takes `(ticket, place)` to find a `Tile` its caller already holds. The page's state is plain records in `BoardStore` (`Tile`, `Closing`, `RootChoice`, `FilesPanel`, board-store.ts:21-64) with a `…Client(page)` class acting on each: the service-and-record pair the rules warn about, eight times over.
- ticket/files-panel-client.ts:22-36, ticket/tile-actions-client.ts:29-51, board/board-client.tsx:9-17 — prefer-class-operations — [3] Module functions that take the record they work on (`offeredTabs(panel)`, `shownTabs(panel)`, `chipFaceOf(tile, choice)`, `validateFaceOf(work)`, `changesOf(was, ticket)`).
- board/board-client.tsx:9 `standingOf` and ticket/ticket-face.ts:8-20 `standing`, `stagePlace` — eliminate-duplication — [2] The same "column · Done / In progress" wording is built twice.
- ticket/ticket-client.tsx:31-38 — shape-classes-around-resources — [3] `TicketClient` makes eight helper objects per ticket, each given the ticket and the whole page; five of them are under 35 lines and hold no state.
- board/board-page.ts:49-55 — low-coupling — [1] Seven clients are given the whole `BoardPage` and reach `page.store`, `page.chat`, `page.board`, `page.reader`, and each other through it, so every client can depend on every other.

### space/repo/repo.py

- repo.py:79 `Repo` and worktree.py:53 `Worktree` — do-not-invent-parallel-object-models — [2] Both stand for one checkout. The card says the process holds one `Repo` per checkout; a `Worktree` is a path, that checkout's `Repo`, and the branch listed there. `Branch.checkout -> Repo | None` (:501) and `Branch.worktree -> Worktree | None` (:475) answer the same question in the two types.
- repo.py:79 `Repo` — use-consistent-naming — [4] One class is called the repository, the clone, and a checkout (`main_clone`, `is_linked_worktree`, `checkout_folder`, `ServedCheckouts`, `worktree.repository`). A reader cannot tell whether an operation is about the whole repository or about one folder of it.
- repo.py:161-181, :233, :330; worktree.py:138 — eliminate-duplication — [2] `folder = self.readable_folder; … if folder is not None else self.git…` is written eight times. There are two readers of the same facts (the `.git` files, and the git command line) and the choice between them is made again at each question.
- repo.py:224 `readable_folder` — guardrail 1 (build once, keep it) — [3] Each access builds a new `GitFolder` and walks up the folders again through `_marked_root` (:116), then reads `config` to test for a reftable (git_folder.py:35).
- repo.py:185 `default_branch -> str` — hold-state-on-the-object-not-in-parameters — [3] Answers a name; four callers turn it back into a `Branch` (see ticket_checkout.py above).
- repo.py:510 `check_out`, :522 `switch_to`, :501 `checkout`, :467 `is_checked_out` — use-consistent-naming — [4] `check_out()` and `switch_to()` both check the branch out; `checkout` is a property that answers a `Repo`. `switch_to` has one caller (:424).
- repo.py:362 `WorkingTree.commit(paths, …)` — hold-state-on-the-object-not-in-parameters — [3] Six of its seven production callers pass `[str(<the checkout's own root>)]` (repo.py:393, :402, :412, :419, :539; ticket_checkout.py:231). Only `session_saves.py:132` names a folder.
- repo.py:579 `ServedCheckouts.marked_checkout` — put-logic-on-the-owning-resource — [3] It reads nothing the registry holds; `Repo` reaches it through the global (:114, :117). Finding the top of a checkout is what `GitFolder` reads `.git` for.
- repo.py:20 `_RUNTIME_LOG`; origin.py:14 `_UNION_MERGED_LOGS`; new_repository.py:16-36 `CDD_WRITTEN_PATTERNS`; latest_release.py:17, :23 — single-boundary — [1] The repository module holds the names of files other modules own: the hook server's `events.log`, the sessions' `session.log` and `session.err`, every path CDD writes into a project, and a release's `e2e-test-results` and `story-map.html`. The card says the sessions are not the repository's concern.

### space/repo/worktree.py

- worktree.py:68, :81-99 `sync_failure`, `fetch_pull`, `pull_fetched` — deep-module, no-use-delete — [1] `sync_failure` is written here and read only by a spec (worktree_heavy_spec.py:56, :70); the docstring says the caller tells the user, and no caller does. `fetch_pull` and `pull_fetched` are public and called only by `Worktrees` (:179-199).
- worktree.py:150 `primary_root` and git_folder.py:113-129 — eliminate-duplication — [2] Both read a linked worktree's `.git` file, split it at `gitdir:`, and follow `commondir` to the main checkout.
- worktree.py:134 `listing() -> list[tuple[Path, str]]` — use-typed-signatures — [4] A bare pair is on the seam. `space/session/session_roots.py:95-103` takes the pairs and builds its own branch-to-folder table with its own two-second cache, though `Worktrees.of(branch)` (:168) answers the same.
- worktree.py:258-334 `Worktrees.remove` and six helpers — keep-classes-single-responsibility — [3] About 75 of the class's 230 lines delete a folder Windows holds locked (`takeown`, `icacls`, long paths, PowerShell). That is a job of its own on a class about git's checkouts, and it builds its `HookDaemon` inside (:266).

### space/repo/repos.py and new_repository.py

- repos.py:116 `SiblingRepo` — do-not-invent-parallel-object-models — [2] A second model of a repository: `branch`, `is_published`, and `is_repository` (:133-151) are `Repo.current_branch`, `Repo.has_origin`, and `Repo.is_clone`, each starting git through a new `Git(self.folder)` (two per `branch` read, :136). `Repos._publish` does the same (:244, :255). The card's constraint is to run git only through `repo.git`.
- new_repository.py:49 `NewRepository` — eliminate-duplication — [2] Has its own `Git` (:54), its own `is_repository` (:57), and its own `DEFAULT_BRANCH = "main"` (:11) beside `Repo.is_clone` and `_DEFAULT_BRANCH_NAMES` (repo.py:23).
- new_repository.py:61-96; repos.py:209 `open` — state-change-returns-record-or-named-failure — [4] `create`, `make_from_folder`, and `ignore_as_cdd_does` answer English sentences, which `Repos.open` joins into a list. A caller cannot tell "created" from "already there" without reading prose.
- repos.py:97 `CddConfig` — high-cohesion — [1] A general reader and writer of `~/.cdd/config.json` by string key lives in the repository module, which uses one key of it; `harness/mcp/cdd_home.py` owns the home folder it sits in.
- space/repo/.context/module-context.md — seam-names-current-code — [4] The Constraint says "there is no in-memory repository" while the Seam lists `MockGit` and `MockRepo`. The card does not name `Repos`, `SiblingRepo`, `NewChat`, or `CddConfig`, nor the dependencies they bring (`harness/chat`, `harness/mcp/cdd_home`, `scripts/install.py`, repos.py:15, :19, :26).

### space/repo/origin.py

- origin.py:101 `Merges.prepare` — use-intention-revealing-names — [4] It writes the union-merge attribute for session logs into the repository's attributes file; `Branch.check_out` calls it too (repo.py:513). The name says neither.

**Count by theme:** [1] 24, [2] 22, [3] 23, [4] 15 — 84 findings.

## Fixes that change no design

Each of these stays inside one class or one file's private surface. None adds or removes a class or changes a seam another module calls.

1. **Make `FidelityProgress`'s inner steps private.** Rename `done_actions`, `remaining_actions`, `latest_report_or_refuse`, `with_violations`, `with_accepted_left_out` (ticket.py:983-1171) with a leading underscore. Callers: only inside the class. Specs to change: `kanban_spec.py` (three reads each of `done_actions` and `remaining_actions`; assert on the published `actions` and `next_action` instead) and one story test under `story_tests/.../accept-report-violation/`. Risk: low. This takes the class from 12 public operations to 7.
2. **Drop the doubled fields in `FidelityProgress.__init__`** (ticket.py:905-912): keep `_required` and `_logged`; read `self._required.fidelity`, `.stage`, `self._logged.done_actions`, `.has_violations`. No caller changes. Risk: low.
3. **`FidelityProgress.from_log(required, ticket)`** (ticket.py:915): read `ticket.work.entries` inside. Callers: ticket.py:748, :789. Risk: low.
4. **Move `Board.file` into `BoardFile`** as a private property (board.py:142 → :398). Callers: board.py:403, :429. Risk: none.
5. **Fold `BoardReads.backlog_item` into `backlog_item_called`** (board.py:505-514). One story-test shared file calls `backlog_item(`; point it at `backlog_item_called` or at `backlog_items`. Risk: low.
6. **Pass the `Sessions` into `Board`** (board.py:113): `Board(sessions)` reads `sessions.repo` and `sessions.board_practices`; `Board.load` passes what it already holds. Specs to change: about eight constructions in `kanban_spec.py` (:86-317). Risk: low, but it is the constructor specs use, so do it in one pass.
7. **Add `Card.move_after`** beside `move_before` (board.py:740) and have `BacklogOrderTools.move_after` call it (backlog_item.py:65-69). Risk: none.
8. **Move `Card._timestamp` to `BacklogItem`** (board.py:747 → backlog_item.py:180). Risk: none.
9. **Give `BoardFile` a named operation for the fix-sending choice** (`set_sends_fixes_directly(sends)`) and make `keep` private (board.py:425; caller :285). Risk: none.
10. **Pass the accepted rules to `Report`'s constructor** and delete `leaving_out` (report.py:107, :125; callers :123, :251). Risk: low.
11. **Keep the rejected name on the four lookup failures** (board.py:55, :73, :80, :97), as `ColumnNotFoundError` does. Risk: none.
12. **Rename `NoReportToAcceptIn`, `ViolationNotInReport`, `FormatNotOffered`** to end in `Error`, in every caller, spec, docstring, and card in the same pass (`space/kanban/.context/module-context.md` names two of them). Risk: low; they reach the page only as message text.
13. **Use what `Branch` and `Repo` already answer in `TicketCheckout`:** replace ticket_checkout.py:229 with `branch.checkout`; replace `self._repo.root == self._repo.main_clone.root` (:272, :283) with `not self._repo.is_linked_worktree`. `MockRepo` overrides `is_linked_worktree` (mock_repo.py:229), so the quick specs keep working. Risk: low; run `ticket_work_heavy_spec.py` and `kanban_tools_git_heavy_spec.py`.
14. **Add `WorkingTree.commit_all(message)`** (repo.py:362) for "everything in this checkout, new files included" and use it at the six call sites that pass the root (repo.py:393, :402, :412, :419, :539; ticket_checkout.py:231). `MockWorkingTree` needs the same method. Risk: low.
15. **Move `marked_checkout` off `ServedCheckouts`** onto `GitFolder` as a creation helper (repo.py:579; callers :114, :117). Risk: low.
16. **Make `Worktree.fetch_pull` and `pull_fetched` private to the module, and delete `sync_failure`** unless a caller is to show it (worktree.py:68-99). Spec to change: `worktree_heavy_spec.py:56, :70`. Risk: low; decide first whether the board should tell the person a worktree opened behind origin, which is what the field was for.
17. **Have `Worktrees.primary_root` ask `GitFolder`** for the common folder (worktree.py:150; make `GitFolder._common_folder` a public `common_folder`). `MockWorktrees` overrides `primary_root`, so quick specs are unaffected. Risk: low.
18. **Delete `Branch.switch_to`** and call `check_out` from its one caller behind the same "already on it" test (repo.py:424, :522). Risk: none.
19. **Delete `BoardPage.startFiles`** (board-page.ts:128-133). No caller. Risk: none.
20. **One `standing` wording in the page:** have `standingOf` (board-client.tsx:9) use `ticket.face.stagePlace`. Risk: none.
21. **Bring the model document and the repo card up to date** (kanban-model.md:624, :806, :852; the "no in-memory repository" sentence and the missing `Repos` terms in `space/repo/.context/module-context.md`). Documentation only. This also clears three of the graph's parameter hits.
22. **Rename `Merges.prepare`** to say what it does, such as `keep_session_logs_by_union` (origin.py:101; callers origin.py:93, repo.py:513, mock_repo.py:377). Risk: none.

## Proposed design changes

### 1. The session keeps a ticket's stage, branch, worktree, and chat; the board asks it

**Problem.** The board stores five of its own facts in the session's `session.json` by raw key (ticket.py:831, :839, :860; ticket_checkout.py:62, :117, :122, :161) and `space/session` reads two of them back with its own literals (session.py:497, session_roots.py:52). Which branch is a ticket's is decided twice with the same pattern (ticket_checkout.py:80, session_roots.py:85), and "the ticket's own worktree" twice (ticket_checkout.py:34, session_roots.py:47). `StageMarks` and `TicketTree` hold no state of their own; they are views onto the session's record and the session's hierarchy.

**Before**

```
space/kanban
  StageMarks(ticket)                      -- no state; reads ticket.session.record.fields["stage"|"stage_mark"]
    moved_into, latest_in(stage), enter(stage), mark(mark: str, stage), place(stage, mark: str)
  TicketCheckout(ticket)
    branch (found by _found_branch, candidate_branches: name pattern)
    assigned_chat / assign_chat           -- record.fields["chat"]
    open()                                -- record.save_fields(branch=, worktree=)
  own_worktree_of(branch)                 -- module function
  TicketTree(ticket)                      -- no state
    ancestors, can_be_child_of(parent), is_stacked, parent_choices, furthest_back_child_stage
space/session
  Session.branch                          -- record.fields["branch"] or name
  SessionRoots.own_worktree_of(session)   -- record.fields["worktree"], else worktree_of(name): same pattern
  SessionHierarchy(session)               -- parent, is_pulled_out, set_parent, mark_pulled_out, open_child
```

**After**

```
space/session
  SessionStage(session)                   + new part, `session.stage`: the one reader and writer of "stage", "stage_mark"
    + entered: str | None                 → moved from StageMarks.moved_into (the name; the board maps it to its Stage)
    + mark_in(stage_name) -> StageMark | None
    + enter(stage_name), mark(stage_name, StageMark)
  StageMark                               + enum: DONE, IN_PROGRESS (replaces the bare strings)
  SessionCheckout(session)                + new part, `session.checkout`: the one reader and writer of "branch", "worktree", "chat"
    + branch: Branch                      → moved from TicketCheckout._found_branch + SessionRoots.worktree_of (one pattern)
    + candidate_branches                  → moved from TicketCheckout
    + worktree: Worktree | None           → replaces own_worktree_of in both modules
    + assigned_chat, assign_chat(chat)    → moved from TicketCheckout
    + record_opened()                     → replaces save_fields(branch=, worktree=)
  SessionHierarchy
    + ancestors, can_take_parent(other)   → moved from TicketTree
space/kanban
  StageMarks                              - removed; Ticket/TicketMoves call session.stage
  TicketTree                              ~ keeps is_stacked, parent_choices, furthest_back_child_stage (board questions)
  TicketCheckout                          ~ keeps work_branch, chat, close_choices, open, save_work, leave_branch; reads session.checkout
  own_worktree_of                         - removed
  Session.branch                          ~ answers session.checkout.branch.name
```

**Callers affected.** `ticket.py` (`_read_column`, `_read_is_done`, `TicketMoves`), `ticket_checkout.py`, `ticket_tree.py`, `space/session/session.py`, `session_roots.py`, `session_hierarchy.py`; the specs `kanban_spec.py`, `ticket_work_heavy_spec.py`, `kanban_tools_git_heavy_spec.py`, the session's root and open-session specs; `kanban-model.md` and both cards.

**Size.** About 8 production files, 250 to 350 lines moved, roughly 60 new. No published tool or data field changes.

**What could go wrong.** A ticket moved before `stage` was recorded is read from its log (ticket.py:823-834); that fallback must move with the part. `SessionRoots` caches the worktree listing for two seconds and the board reads it once per board read; one owner needs one caching rule, and a wrong one shows as a ticket whose worktree appears late. The session module grows by two parts; the metrics gate must show `Session` itself does not.

### 2. A branch answers where it is checked out, and the default branch is a `Branch`

**Problem.** `TicketCheckout` works out three times whether a branch is checked out anywhere (ticket_checkout.py:89, :146, :229), turns `repo.default_branch` back into a `Branch` three times (:91, :273, :285), swaps its repo after deleting a worktree (:259), and four places commit-and-push with different conditions (ticket_checkout.py:227; repo.py:532, :398; worktree.py:101). The cause is in `space/repo`: `Branch.is_checked_out` means "in the checkout this object was made from", `default_branch` is a string, and there is no single "save this checkout's work".

**Before**

```
Repo
  default_branch: str
  branch_named(name) -> Branch            -- a Branch tied to this checkout
Branch(repo, name)
  is_checked_out                          -- only in the checkout it was made from
  worktree -> Worktree | None             -- any checkout that has it
  checkout -> Repo | None                 -- this clone or the worktree's
  save(message)                           -- commit when dirty; push when not default and origin is behind
  land_on_default(), merge_into_default(), delete(unmerged)
Publishing.push_work()                    -- commit; push when there is an origin
Worktree.close(message)                   -- branch.save, then remove
kanban: own_worktree_of(branch), TicketCheckout._commit_and_push(branch, leaving), _work_from_main_clone()
```

**After**

```
Repo
  ~ default_branch: Branch                (name via .name; four callers shorten)
Branch
  ~ is_checked_out                        true when any checkout has it (was: this checkout only)
  + is_checked_out_here                   the old meaning, for the two callers that need it
  + linked_worktree -> Worktree | None    → moved from kanban own_worktree_of
  ~ checkout -> Repo | None               unchanged, now the one answer callers use
  ~ save(message, push=True)              the one "commit everything here and push"; Publishing.push_work and
                                          TicketCheckout call it
  (acts through repo.main_clone for land, merge, delete, as today)
Publishing.push_work                      ~ calls current_branch.save
TicketCheckout
  - _commit_and_push                      → Branch.save
  - _work_from_main_clone                 no longer needed: Branch operations already run in the main clone
  - _checked_out_work_branch              → branch.checkout is not None
```

**Callers affected.** `ticket_checkout.py` (most of it), `repo.py` (`Publishing`, `Branch`), `origin.py`, `session_saves.py:128` (compares `current_branch.name != default_branch`), `repos.py`, `mock_repo.py` (`MockRepo.default_branch`, `MockBranch`), the repo heavy specs and `ticket_work_heavy_spec.py`.

**Size.** 6 production files, about 150 lines changed, 60 removed from `ticket_checkout.py`.

**What could go wrong.** Changing what `is_checked_out` means changes `ticket.branch`'s published data field, which the chat bar and the Close dialog read; either keep the published field on the old meaning or check both readers. The four save operations differ on purpose in small ways (the default branch is committed and not pushed in `Branch.save`); merging them must keep each difference as a named argument or a test will pass while a close pushes main unexpectedly. This is the area CDR 0005 already flagged, so the gain is real, but it is the riskiest code in the two modules: run the heavy tier.

### 3. One checkout class in `space/repo`

**Problem.** `Repo` and `Worktree` both stand for one checkout (repo.py:79, worktree.py:53); `SiblingRepo` and `NewRepository` are a third and fourth partial model with their own `Git` (repos.py:116, new_repository.py:49). The names `repository`, `clone`, and `checkout` are used for the same object.

**Before**

```
Repo(root)            git, worktrees, refs, working_tree, origin, merges, publishing, main_clone, current_branch, is_linked_worktree
Worktree(worktrees, path, branch_name)   path, repository: Repo, branch, sync_failure; fetch_pull, pull_fetched, close
Worktrees(repo)       __iter__ -> Worktree, of(branch), at(folder), open(branch), add, remove, listing() -> [(Path, str)]
SiblingRepo(folder)   name, path, branch, is_published, has_cdd, is_repository   -- own Git
NewRepository(root)   is_repository, create, make_from_folder, ignore_as_cdd_does  -- own Git, answers sentences
```

**After**

```
Repo(root)                               ~ is the checkout (the card says so already)
  + is_main_clone                        (not is_linked_worktree)
  + catch_up_with_origin()               → moved from Worktree.fetch_pull / pull_fetched
  + close(message)                       → moved from Worktree.close (save the branch, then worktrees.remove(self))
Worktree                                 - removed; Worktrees yields Repo
Worktrees(repo)
  ~ __iter__ -> Repo, of(branch) -> Repo | None, open(branch) -> Repo
  - listing() from the seam              (private; session_roots asks of(branch))
SiblingRepo                              ~ holds a Repo; branch/is_published read repo.current_branch / repo.has_origin
NewRepository                            ~ takes a Repo, runs git through repo.git; answers a small record
                                           (created | already_there, branch, ignored_lines) the tool words
```

**Callers affected.** `board.py:525-529` (`BoardReads.worktrees`), `ticket_checkout.py`, `space/session/session_roots.py`, `session_files.py:187`, `repos.py`, `cdd_guidance/desktop_walk/desktop_walk.py:29`, `mock_repo.py` (`MockWorktrees`), every repo heavy spec, the repo card.

**Size.** 8 to 10 production files, 300 to 400 lines changed, about 80 removed.

**What could go wrong.** A `Worktree` today also covers a checkout whose folder is listed but whose branch is detached (`branch is None`); `Repo.current_branch` answers `HEAD` there, so every `tree.branch is not None` test needs a deliberate replacement. `ServedCheckouts` would hold a `Repo` for every listed worktree, including ones no chat works in; that is more held objects and must not start git for each. This is the largest change here and the one with least visible product gain: it is worth doing only with proposal 2, and after it.

### 4. One reader of git's facts

**Problem.** Eight questions each choose between the `.git` files and the git command line at the call site (repo.py:161-181, :233, :330; worktree.py:138), and `readable_folder` builds its `GitFolder` again on each (repo.py:224). `Worktrees.primary_root` reads the same files a third way (worktree.py:150).

**Before**

```
Repo.branches / current_branch / is_on_branch / current_commit / has_origin   each: folder = readable_folder; A if folder else git.run(B)
Refs.has(ref)                                                                  same choice
Worktrees.listing()                                                            same choice
GitFolder(checkout)        is_readable, head_branch, is_on_branch, head_commit, has_ref, branch_names, has_remote, worktrees
```

**After**

```
GitFacts (interface)       + head_branch, is_on_branch, head_commit, has_ref(ref), branch_names, has_remote(name), worktrees, common_folder
  GitFolder                ~ implements it from the .git files (as today)
  AskedOfGit(git)          + implements it with the commands now written inline in Repo, Refs, Worktrees
Repo
  + facts: GitFacts        chosen once (GitFolder when readable, else AskedOfGit), chosen again only when the folder becomes a repository
  ~ branches, current_branch, is_on_branch, current_commit, has_origin   one line each: self.facts.X
  - readable_folder        removed from the public surface
Refs                       - removed; repo.facts.has_ref  (or kept as one line)
MockRepo                   ~ supplies a GitFacts answered from MockGit, replacing eight overridden properties
```

**Callers affected.** Inside `space/repo` only, plus `mock_repo.py`. No caller outside the module changes if `Refs.has` stays as a one-line forward.

**Size.** 4 files, about 120 lines changed, one new class of about 40 lines.

**What could go wrong.** "Chosen once" must still notice a plain folder becoming a repository (`repo.make_repository`) and a repository switching to a reftable; `default_branch` already handles the first case by reading again until a ref is found (repo.py:185-195), and the same rule is needed here. The gain is mostly readability and one place to fix; the speed the files give is unchanged.

### 5. One type for work on a fidelity and work on a stage, and commands the work answers itself

**Problem.** `StageWork` repeats six members of `FidelityProgress` (ticket.py:1221, :898), the page already joins them as `BarWork` (tile-actions-client.ts:14) and also recomputes a stage's progress itself (ticket-work.ts:38). `TicketWork.command(action, fidelities)` takes what its callers hold (ticket.py:795), and the page adds `format=` to the result (tile-actions-client.ts:119).

**Before**

```
FidelityProgress   stage, action_states, has_violations, violation_count, commands, allowed_actions, + state, next_action, report_file, ...
StageWork(ticket, stage, progress)   stage, action_states, has_violations, violation_count, commands, allowed_actions
TicketWork.command(action: str, fidelities: list[FidelityGuidance]) -> str
page: BarWork = StageWorkData | FidelityProgressData; TicketWork.progressIn(stage); `${command} format=${formats}`
```

**After**

```
Work (base)                          + stage, action_states, has_violations, violation_count, commands, allowed_actions, fidelities
                                     + command(action) -> str      reads its own fidelities and its ticket's session file
                                     + command_in(action, formats) -> str   the one place `format=` is written
  FidelityProgress(Work)             ~ fidelities = [its own]; keeps what only one fidelity has
  StageWork(Work)                    ~ fidelities = each of its progress; + progress sent by reference, so the page stops filtering
TicketWork.command                   - removed
page: BarWork                        ~ becomes the generated WorkData; ticket-work.ts progressIn - removed; tile-actions run() sends work.commands
```

**Callers affected.** `ticket.py`, `leaving_handoff.py:61`, the generated TypeScript for `ticket` and `fidelity-progress`, `tile-actions-client.ts`, `ticket-work.ts`, the chat bar's `format-choices-client.ts` (it builds the same `format=` text), `kanban-model.md`.

**Size.** 2 Python files (about 60 lines), 3 to 4 TypeScript files in the board and 1 to 2 in the chat bar (about 80 lines), one reinstall to regenerate the adapters.

**What could go wrong.** Sending a command per chosen format set means either a tool call (`work.command_in`) where the page now joins a string locally, or sending commands for every format group up front, which grows `board.show`. The published key `actions` and the field names must not change, or the chat bar's stub chat breaks. The corrections log asked for commands to come from the session's practices and fidelities' actions; this proposal stops short of that and says so: it removes the parameters, and the next step is moving `command` onto the fidelity's action in `harness/guidance`.

### 6. What a person chose when closing is an object

**Problem.** `leaving: list[str]` goes through nine methods of `TicketCheckout`, each testing a string constant (ticket_checkout.py:175-274), and the page repeats the keys to word its report (activation-client.ts:5).

**Before**

```
LeaveChoices(branch, own_branch)     branch, own_branch, choices: list[str], chosen: list[str] (always empty)
Ticket.close(leaving: list[str] | None)
TicketCheckout.write_handoff(leaving), save_work(leaving), keep_landing_release(leaving), leave_branch(leaving), + 5 private (…, leaving)
```

**After**

```
Leaving                              + made from the published list of names; refuses a name that is no choice (LeaveChoiceUnknownError)
  + writes_handoff, commits, pushes, merges, deletes_branch, deletes_worktree: bool
  + saves_work, changes_branch       (the two set tests at :198 and :214)
  + done: list[str]                  what was done, worded once for the page's report
LeaveChoices                         ~ offered: Leaving (what can be done now); `choices` and `chosen` keep their published keys
Ticket.close(leaving)                ~ published argument unchanged; builds Leaving(leaving) once
TicketCheckout                       ~ each method takes the Leaving, or the close makes a `TicketClose(checkout, leaving)` that holds it
                                       and runs the steps in the order the card requires
```

**Callers affected.** `ticket.py:236-254`, `ticket_checkout.py`, `ticket_work_heavy_spec.py`, `kanban_tools_git_heavy_spec.py`; the page only if `done` replaces `LEFT_STEPS`.

**Size.** 2 Python files, about 90 lines changed, one class of about 40 lines.

**What could go wrong.** Today an unknown name in `leaving` is silently ignored; refusing it is a behaviour change for any agent that calls `ticket.close` with a misspelt step, which is the point, but it should be announced. The order of the close's steps is a documented constraint; moving them into one object must keep that order and the comment that explains it (ticket.py:242-245).

### 7. The Backlog owns its folder

**Problem.** The Backlog folder's layout is decoded in `BoardReads.backlog_items` (board.py:472-486) and again in nine private members of `BacklogItem` (backlog_item.py:241-301); the page repeats the nesting rules (backlog-item-client.tsx:47). `BacklogItem` holds two jobs.

**Before**

```
BoardReads.backlog_items             scans files, own-name folders, parents, children
Backlog(Column)                      items
BacklogItem(path, board)             title, text, parent: str, children, ticket: str, start, start_under, edit_text, open_file, nest_under, leave_parent
                                     _held_ticket_folder, _holds_ticket, _is_kept_in_own_folder, _parent_file, _refuse_nesting_under,
                                     _folder_for_children, _move_file_into, _remove_emptied_folder
```

**After**

```
BacklogFolder(folder)                + one owner of the layout (a part of the Backlog column)
  + idea_files() -> list[IdeaPlace]  → moved from BoardReads.backlog_items
IdeaPlace(file, backlog_folder)      + where one idea's file sits
  + parent_file, holds_ticket, ticket_folder, is_in_own_folder          → moved from BacklogItem's private properties
  + move_under(parent: IdeaPlace), move_out(), refuse_nesting_under(parent)   → moved from BacklogItem
BacklogItem(place: IdeaPlace, board) ~ keeps the idea and the published tools; nest_under / leave_parent / start ask its place
  + parent_choices                   sent to the page, as Ticket.parent_choices is, so canTakeAsChild in the page is deleted
```

**Callers affected.** `board.py` (`BoardReads`, `CardPlacement.make_backlog_item`), `backlog_item.py`, `kanban_spec.py`, the backlog story tests, `backlog-item-client.tsx`, the model document.

**Size.** 2 Python files and 1 TypeScript file, about 150 lines moved, 40 new.

**What could go wrong.** The card's rule "never delete or write over an idea's file" is kept today by code spread through these members; moving them is where a move could be turned into a copy-and-delete by mistake, so the move operations should be moved whole, not rewritten. `parent_choices` for every backlog item adds a list per item to `board.show`.

### 8. The page stops repeating rules and prompts Python can send

**Problem.** The page holds rules Python also holds or should hold (pending-changes.ts:173, backlog-item-client.tsx:47, card-upkeep-view.tsx:14-30, column-client.ts:101, ticket-drops.ts:18, ticket-next-step.ts:25) and writes agent prompts with tool names in them (report-client.ts:19-53, ticket-chat-prompts.ts, chat-opening.ts:10, board-page.ts:123), which the chat bar writes again (chat-bar-client.ts:375). One of the rules already disagrees with Python (the stage count against `is_over_limit`); one exists only in the page (main's text and tags cannot be edited).

**Before**

```
Ticket (Python)        commands only on FidelityProgress / StageWork; new_chat_link (prompt inside)
page                   TicketChatPrompts: fillSplit, fillHandoff, fillSetUpRoots, closeSession   (prompt text + tool names)
                       ReportClient: fixPrompt, falseViolationPrompt, fixRulePrompt, fixReportPrompt
                       ChatOpening.newChatPrompt(ticket)
                       isMain tests in views; ColumnClient.count; BacklogItemClient.canTakeAsChild
```

**After**

```
Ticket
  + prompts: TicketPrompts            data field: split, handoff, set_up_roots, close_session, new_chat  (each the text to send)
  + can_edit: bool                    false for main; edit_text / tag refuse main with MainStaysOpenError
  ~ new_chat_link                     built from prompts.new_chat
Stage
  + ticket_count: int                 the number the head shows, by the same rule as is_over_limit
ReportRule / Violation (as the report sends them)
  + fix_prompt, false_prompt          the text the Fix and False buttons send
Report
  + fix_prompt
page                                  - TicketChatPrompts' texts, ReportClient's prompt builders, ChatOpening.newChatPrompt,
                                        ColumnClient.count's own rule, the isMain tests for editing
```

**Callers affected.** `ticket.py`, `board.py`, `report.py`, the generated adapters, about eight TypeScript files in the board, and the chat bar's copies in `harness/chat-ui` (outside this area, but the reason to do it).

**Size.** 3 Python files (about 120 lines added), 8 TypeScript files (about 150 lines removed), story tests that assert prompt text move from the page's specs to Python's.

**What could go wrong.** Prompts in every ticket and every violation make `board.show` and a report larger; the report's prompts could be answered by a tool (`fidelity-progress.fix_prompt(violation)`) at the cost of one more call per click. Whether main's text may be edited is a product decision the page made alone; it needs an answer before Python enforces it. Wording changes then need a reinstall instead of a page rebuild.

### 9. The board opens the Files app for files, and its own file panel goes

**Problem.** The board carries a second file viewer of about 620 lines (files-panel-client.ts, file-viewer-view.tsx, files-panel-view.tsx, open-file-comments.ts, file-views-view.tsx, plus `FilesPanel` in board-store.ts) beside `harness/files_app`, and `main.tsx:8` already says files never open here.

**Before**

```
BoardPage.files: FilesPanelClient      openFiles, openFolder, openTab, openFileAtLine, togglePractice, toggleRead, filterChanged, save, reload, refreshShown
  .comments: OpenFileComments          add, remove, send, sendOpen, clearProcessed
PageLinks.openFiles / openSessionFolder   ?files= and ?session-folder= links open the panel
details-view, card-upkeep-view, report-rule-view   call page.files.*
```

**After**

```
EditorAppClient
  + files: AppClientGenerated          as graph and kanban are (editor-app-client.ts:25)
  + openFilesOn(ticket, { fidelities | folder, file, line })   opens the Files app's page on the ticket's session
FilesPanelClient, OpenFileComments, file-viewer-view, files-panel-view, file-views-view   - removed
BoardStore: FilesPanel, FilesSource, FileReads                                             - removed
PageLinks.openFiles / openSessionFolder                                                    - removed (the chat bar links to the Files app)
```

**Callers affected.** `board-page.ts`, `page-links.ts`, `side-panels-view.tsx`, `details-view.tsx`, `card-upkeep-view.tsx`, `report-rule-view.tsx`, `board-store.ts`; the specs `linked-files.spec.ts`, most of `side-panel-client.spec.ts` (530 lines), `tests/kanban/files-and-reports/*`, and the files-and-reports story tests.

**Size.** About 620 production lines and 600 spec lines removed, 40 added.

**What could go wrong.** This changes what a person sees: a file opens in another window, not beside the board, and "open the file at this violation's line" must work in the Files app first (its link takes a file; confirm it takes a line). If the panel beside the board is wanted, the other honest option is the reverse: the board embeds the Files app's views. Either way the product owner decides which viewer stays; keeping both is the cost today.

### 10. `board.py` no longer needs a registry to make its cards

**Problem.** `CARD_KINDS` (board.py:310-324) hides that `board.py` makes `Ticket` and `BacklogItem` while both import `board.py`.

**Before**

```
board.py           Board, CardKinds/CARD_KINDS, CardPlacement (makes tickets/items through CARD_KINDS), BoardFile, BoardReads,
                   Column, Backlog, Complete, Stage, Card, RequiredFidelity, Help, BoardFidelity, BoardOverview, ...
ticket.py          imports board.py
backlog_item.py    imports board.py and ticket.py
__init__.py        CARD_KINDS.place(Ticket, BacklogItem)
```

**After**

```
column.py          + Column, Backlog, Complete, Stage, Card, RequiredFidelity, BoardFile     (knows no ticket; takes the board as a typed reference)
ticket.py          ~ imports column.py
backlog_item.py    ~ imports column.py, ticket.py
board.py           ~ Board, CardPlacement, BoardReads, Help, the overview classes; imports ticket.py and backlog_item.py directly
CardKinds          - removed
```

**Callers affected.** Every `from space.kanban.board import Stage | Column | Card | BACKLOG_COLUMN …` (ticket.py, backlog_item.py, ticket_tree.py, specs, tier files, story tests).

**Size.** 4 production files, mostly moved lines; about 30 import lines in specs and story tests.

**What could go wrong.** `Ticket.load`, `Stage.load`, and `BacklogItem.load` call `Board.load(project)` (ticket.py:357, board.py:622, backlog_item.py:88), which is the one reference upward that remains. It can only go if the loaders ask something lower (the checkout's `Sessions`, which already holds the board's practices) or the framework lets the board load its cards. Without that, this proposal removes the registry but leaves one import inside a function, which the rule also counts. It is honest to say this one is the lowest value of the ten until the loader question is settled.

## Graph hits judged noise

The graph hits in this area that are real are reported above: `StageWork` copying `FidelityProgress` (kanban-model.md:694), `Ticket` with 23 public operations (kanban-model.md:330), `BacklogItem` with 11 (kanban-model.md:739), `FidelityProgress` with 12 (ticket.py:898; fix 1 takes it to 7), and `FilesPanelClient` with 10 (files-panel-client.ts:45; proposal 9 removes it).

| File:line | Rule | Why it is noise |
|---|---|---|
| space/kanban/ticket.py:217 | limit-comments (`TicketEnding` has a descriptive comment) | The docstring states what the class is and its invariant (main never leaves; each ending is committed on main). It narrates no line of code. |
| space/kanban/ticket.py:236 | limit-comments (`close` has a descriptive comment) | The docstring is the published description of the `ticket.close` tool, and the comment at :242-245 says why the merge comes before the record moves, which the signature cannot say. |
| space/kanban/ticket.py:1130 | limit-operation-parameters (`_shown_as` takes 4) | A private mapping from the published tool's own arguments (`rule`, `message`, `location`, `node_id`) to a `Violation`; mapping factories and published arguments are both exempt. It could be folded into its two callers, but it hides no setup. |
| space/kanban/.context/kanban-model.md:624 | limit-operation-parameters (`FidelityProgress` takes 5) | The hit is on a stale line of the model document. The code takes three (`required`, `logged`, `ticket`, ticket.py:905). The stale document is reported as its own finding. |
| space/kanban/.context/kanban-model.md:806 | limit-operation-parameters (`Help` takes 4) | Same: the code takes three (board.py:763). |
| space/kanban/.context/kanban-model.md:852 | limit-operation-parameters (`Report` takes 4) | Same: the code takes three (report.py:107). |
| space/kanban/.context/kanban-model.md:223 | use-typed-signatures (parameter `values` has no type) | The model's notation for `keep(values)`; the code types it (`**values: object`, board.py:425). The real weakness, that the board file is an untyped dict, is reported under `board.py`. |
