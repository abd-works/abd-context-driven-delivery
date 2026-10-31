## Language

*Board* shows every work session as a ticket and where each ticket stands in delivery: Backlog, then the stages Discovery, Specification, and Implementation, then Complete. A caller reads it to see what is in flight and what to do next. It stores no ticket state: tickets read their own session logs each time they are asked, so the board can never disagree with the work.

### board

- Created with the practices chosen for the work (for example Stories, DDD, and UX). The columns and stages follow from those practices.
- Reads `.sessions/`: every folder there is a ticket, except `default/`, `closed/`, and folders whose names start with `_`. `closed/` holds finished tickets; `_backlog/` holds backlog items; `_archive/` holds archived sessions. `default/` is where work goes when no session is open, so it is not a ticket. The board reads no other `_` folder.

### column

- One of the places on the board: Backlog, a stage, or Complete.
- **Invariant:** every ticket is in exactly one column. Backlog holds backlog items, not tickets.

### stage

- Discovery, Specification, or Implementation: a column where work is done, split into in progress and done.
- Its *work required* is every fidelity of the chosen practices whose `stage:` is this stage. Each fidelity section in a practice's markdown declares its stage, so the stage reads it from the practices rather than keeping a table. A practice can have none in a stage or several, so the stage keeps every fidelity whose stage matches.
- Its *actions* are the steps every fidelity in the stage goes through. For now every stage uses the same three: Generate, Validate, then Review, where a person approves the fidelity.

### ticket

- One work session seen as a unit of delivery: its title, scope, and *lineage* (the ticket it was split from).
- Knows its own column and progress by reading its own `session.log` against the board's stages.
- Starts in the earliest stage its log shows work in, or Discovery when nothing is done yet. After that it moves only when a person moves it.
- **Invariant:** a ticket never moves to another column by itself. A person moves it with the arrows, whatever its progress, and the move is written to its session log with the stage it enters.

### progress

- For each fidelity the board requires: which of its stage's actions are done and which are not.
- A fidelity is done in its stage when every action is done. Validate is done when the latest validate line for that fidelity names no graph-rule violations. The AI-judged rules are not written to the log; the person checks them in Review, which counts only after Validate is done.
- *Next action* is what Run next does on a ticket: generate, validate, then review for each practice in order, then the same for the next practice. Violations hold a ticket on that fidelity, because Review needs a clean Validate, so the next action is satisfy until they are fixed. This is intended and not built.

### backlog item

- An idea not yet started: one markdown file per idea in `.sessions/_backlog/`, added by a person. The Backlog column shows them. Starting one opens a ticket for it.
- A ticket moved back into the Backlog keeps its work, and starting its item brings the ticket back with that work. This is intended and not built.

Build order: `Column` → `Stage` → `Backlog` → `FidelityProgress` → `Ticket` → `BacklogItem` → `Board`

---

# harness/kanban

Purpose, seam, dependencies, and constraint: `.context/module-context.md`.

Sources: `board.py`, `ticket.py`, `backlog_item.py`, `kanban.py`, and for what is not built yet, the Board canvas at https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN (Version 72). A member whose note starts "Intended:" is not in the code yet; "Going:" is in the code and the canvas removes it. Everything else mirrors the code.

## Board

+ Board(sessions_folder: Path, practices: list[PracticeGuidance])
	// practices are chosen when the board is created; the columns follow from them
+ load(sessions_folder: Path): Board
	// a board with every practice chosen
------
+ sessions_folder: Path
+ practices: list[PracticeGuidance]
+ << composition >> columns: list[Column]
	// always Backlog, then one Stage for each of Discovery, Specification, Implementation, then Complete
+ << aggregation >> tickets: list[Ticket]
	// every folder in sessions_folder except `default/`, `closed/`, and `_` folders, plus every folder in `closed/`
+ << aggregation >> backlog_items: list[BacklogItem]
	// every markdown file in `_backlog/`
+ active: Ticket
	// the ticket whose session is the current session in `session.json`; none when no ticket has that name
----
+ to_json(): dict
	// the project, the active ticket's name, and every column with its tickets or items; the shape the board pane and other IDEs read
	-> Column.to_json
+ new_ticket(title: str, scope: str, parent: Ticket): Ticket
	// a new ticket is in Discovery, in progress, until its log shows work in a later stage
+ add_backlog_item(title: str, text: str): BacklogItem
	// Intended: writes one markdown file to `_backlog/`, the title as its heading and the text under it
+ ticket(name: str): Ticket
+ column(name: str): Column

## Column

+ Column(name: str, board: Board)
------
+ name: str
+ tickets: list[Ticket]
	// every ticket of the board whose column is this one
	-> Board.tickets
	-> Ticket.column
----
+ to_json(): dict
	-> Ticket.to_json

## Backlog : Column

+ Backlog(board: Board)
------
+ items: list[BacklogItem]
	-> Board.backlog_items
----
+ to_json(): dict
	-> BacklogItem.to_json

## Stage : Column

+ Stage(name: str, board: Board, actions: list[GuidanceAction])
	// for now every stage is given Generate, Validate, and Review, in that order
------
+ actions: list[GuidanceAction]
+ practices: list[PracticeGuidance]
	-> Board.practices
+ work_required: list[FidelityGuidance]
	// every fidelity of every chosen practice whose stage is this stage, in practice order; none for a practice with no fidelity here
	-> FidelityGuidance.stage
+ next_stage: Stage
	// none after Implementation
+ previous_stage: Stage
	// none before Discovery
+ in_progress: list[Ticket]
+ done: list[Ticket]
	// tickets in this stage whose every required fidelity has every action done; they wait here until a person moves them
----
+ to_json(): dict
	-> Ticket.to_json

## Ticket

+ Ticket(session_folder: Path, board: Board)
	// never moves to another column by itself
------
+ name: str
+ title: str
+ scope: str
+ << association >> lineage: Ticket
+ << composition >> progress: list[FidelityProgress]
	// one per fidelity the board requires, in stage order; read from session.log each time, never stored
+ column: Column
	// Complete once its folder is in `closed/`; otherwise the stage named by its latest move line; before any move, the earliest stage its log shows an action in, or Discovery
+ is_done: bool
	// true only in a stage, and only when every required fidelity in that stage is done
+ next: FidelityProgress
	// the first fidelity in its current stage that is not done, in practice order; none when it is done or Complete
+ last_activity: str
	// the timestamp of its latest log line; empty when it has none
+ latest_handoff: str
	// the newest `handoff-*.md` in its session folder as a path from the project; empty when it has none
+ reports: dict
	// each fidelity's newest report in `validation-reports/`, named `{practice}-{fidelity}-{date}.md`, as a path from the project; a fidelity with no report is left out
+ practices: list[PracticeGuidance]
	// Intended: the practices enabled for this ticket, from the `practices` field in its `session.json`, else the board's; progress, next, and is_done count only these
----
+ pull(): Stage
	// Going: the canvas drops pull, and moves are the arrows. Only when is_done and its stage has a next stage; writes `pull <next stage>` to its session log and returns that stage; fails with StageNotDone otherwise. A done ticket in Implementation is closed, not pulled.
+ move_next(): Ticket
	// a person's move to the next column, whatever its progress: writes `pull <next stage>` to its session log, and out of Implementation it closes
+ move_previous(): Ticket
	// a person's move to the previous column: writes `pull <previous stage>`; out of Complete its folder leaves `closed/` and it is in Implementation; Discovery is as far back as it goes. Intended: out of Discovery it moves into the Backlog and returns its BacklogItem, its folder kept under `_backlog/`, and it stops being the active ticket because the board no longer finds it
+ enable_practice(practice: PracticeGuidance, is_enabled: bool): Ticket
	// Intended: writes the ticket's `practices` field in its `session.json`
+ close(): Ticket
	// after closing, its folder is in `closed/` and its column is Complete
+ archive(): Ticket
	// after archiving, its folder is in `_archive/` and it is off the board
+ to_json(): dict
	// the ticket's fields, column, next, handoff, reports, and each fidelity's state. Intended: also next_action and practices
	-> FidelityProgress.state
- _log_lines(): list[str]
	// a log line starts with the action; the paths that follow are joined by ", " and can hold spaces; then come the practice and fidelity. Find the practice and fidelity by their names, never by position. The practice appears as its folder name (`clean_engineering`) in action lines and as its class name (`CleanEngineering`) in validate lines.

## StageNotDone : Exception

+ StageNotDone(ticket: Ticket, stage: Column)
	// Going, with Ticket.pull
------
+ << association >> ticket: Ticket
+ << association >> stage: Column
----

## FidelityProgress

+ FidelityProgress(fidelity: FidelityGuidance, stage: Stage, done_actions: list[GuidanceAction], has_violations: bool)
	// validate is done only when its latest line for this fidelity names no graph-rule violations; review is done only after that
+ from_log(fidelity: FidelityGuidance, stage: Stage, lines: list[str]): FidelityProgress
------
+ fidelity: FidelityGuidance
+ << association >> stage: Stage
+ done_actions: list[GuidanceAction]
+ remaining_actions: list[GuidanceAction]
	// the stage's actions not yet done, in order
	-> Stage.actions
+ is_done: bool
+ slug: str
	// practice folder name and fidelity, such as `stories-story_map`
+ report_files: str
	// the name pattern of this fidelity's dated validation reports
+ state: str
	// done, violations, in_progress, or not_started: what the board pane colours
+ next_action: str
	// Intended: what Run next does here: `generate`, `validate`, or `review`, the first remaining action; `satisfy` while it has violations, so Run next never validates again over open violations
----

## BacklogItem

+ BacklogItem(path: Path, board: Board)
------
+ title: str
	// the item's first `# ` heading, or its file name in words
+ text: str
	// Intended: the file's content after its heading; the details show it
+ path: Path
+ last_activity: str
	// when its file last changed
----
+ start(scope: str): Ticket
	// the new ticket's session log names this item's path. Intended: an item a ticket was moved back into returns that ticket with its folder, log, and progress, and the item goes
	-> Board.new_ticket
+ to_json(): dict

## Kanban

+ Kanban(project: str)
	// the board as cdd MCP tools; the project is CDD_PROJECT, else the current folder, and its `.sessions/` is the board
------
----
+ board(): dict
	-> Board.to_json
+ pull(ticket: str): dict
	// Going, with Ticket.pull
	-> Ticket.pull
+ move_next(ticket: str): dict
	-> Ticket.move_next
+ move_previous(ticket: str): dict
	-> Ticket.move_previous
+ start(backlog_item: str, scope: str): dict
	-> BacklogItem.start
+ new(title: str, scope: str, parent: str): dict
	-> Board.new_ticket
+ add_backlog_item(title: str, text: str): dict
	// Intended: the + on the Backlog heading
	-> Board.add_backlog_item
+ enable_practice(ticket: str, practice: str, is_enabled: bool): dict
	// Intended
	-> Ticket.enable_practice
+ close(ticket: str): dict
	-> Ticket.close
+ archive(ticket: str): str
	-> Ticket.archive

---

**Open**

- Starting a ticket's session (its folder and branch) stays with `space/session` and `space/repo`; the board reads what they write and does not call them.
- Review is a `GuidanceAction` deployed as a command (`/review <guidance>`). It records a person's approval of a fidelity as a `review` line in the session log, which the ticket reads like any other action line.
- The move line still reads `pull <stage>`. Dropping pull from the language means choosing a new word for that line and what to do with lines already in session logs.
- On the canvas a stage has two steps, so an arrow moves a ticket from In progress to Done and only then across the column. `is_done` is derived from progress here, so the real board has nowhere to record a person's move to Done, and its arrows cross a column in one step. Either the ticket records that move in its log or the arrows keep crossing in one step.
- Locking is pane state, not a board rule: with Active session only on, the canvas disables every action on a ticket other than `Board.active`. The pane reads `active` from `Board.to_json` and holds the switch itself.
- Ticket-wide Run sends one action across a ticket's enabled practices at its current stage. It is a prompt the pane fills, so it needs no operation here beyond `Ticket.practices`.
- The canvas's list, folder, and files come from each fidelity's outputs, which `Session.fidelity_outputs` works out in `space/session`. This module does not depend on `space/session`, and the pane has no other route to them, so that seam is still to be decided, along with a `format` argument on Generate.
