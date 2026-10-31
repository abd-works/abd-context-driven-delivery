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
- Starts in the earliest stage its log shows work in, or Discovery when nothing is done yet. After that it moves only when pulled.
- **Invariant:** a ticket never moves to the next stage by itself. Someone pulls it, and the pull is written to its session log with the stage it enters.

### progress

- For each fidelity the board requires: which of its stage's actions are done and which are not.
- A fidelity is done in its stage when every action is done. Validate is done when the latest validate line for that fidelity names no graph-rule violations. The AI-judged rules are not written to the log; the person checks them in Review, which counts only after Validate is done.

### backlog item

- An idea not yet started: one markdown file per idea in `.sessions/_backlog/`, added by a person. The Backlog column shows them. Starting one opens a ticket for it.

Build order: `Column` → `Stage` → `Backlog` → `FidelityProgress` → `Ticket` → `BacklogItem` → `Board`

---

# harness/kanban

Purpose, seam, dependencies, and constraint: `.context/module-context.md`.

## Board

+ Board(sessions_folder: Path, practices: list[PracticeGuidance])
	// practices are chosen when the board is created; the columns follow from them
+ load(sessions_folder: Path): Board
	// a board with every practice chosen
------
+ practices: list[PracticeGuidance]
+ << composition >> columns: list[Column]
	// always Backlog, then one Stage for each of Discovery, Specification, Implementation, then Complete
+ << aggregation >> tickets: list[Ticket]
	// every folder in sessions_folder except `default/`, `closed/`, and `_` folders, plus every folder in `closed/`
+ << aggregation >> backlog_items: list[BacklogItem]
	// every markdown file in `_backlog/`
+ active: Ticket
	// the ticket whose session is the current session
----
+ to_json(): dict
	// every column with its tickets or items; the shape the board pane and other IDEs read
	-> Column.tickets
	-> Backlog.items
+ new_ticket(title: str, scope: str, parent: Ticket): Ticket
	// a new ticket is in Discovery, in progress, until its log shows work in a later stage
+ ticket(name: str): Ticket

## Column

+ Column(name: str, board: Board)
------
+ name: str
+ tickets: list[Ticket]
	// every ticket of the board whose column is this one
	-> Board.tickets
	-> Ticket.column
----

## Backlog : Column

+ Backlog(board: Board)
------
+ items: list[BacklogItem]
	-> Board.backlog_items
----

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
+ in_progress: list[Ticket]
+ done: list[Ticket]
	// tickets in this stage whose every required fidelity has every action done; they wait here until pulled
----

## Ticket

+ Ticket(session_folder: Path, board: Board)
	// never moves to the next stage by itself
------
+ name: str
+ title: str
+ scope: str
+ << association >> lineage: Ticket
+ << composition >> progress: list[FidelityProgress]
	// one per fidelity the board requires, in stage order; read from session.log each time, never stored
+ column: Column
	// Complete once its folder is in `closed/`; otherwise the stage named by its latest pull line; before any pull, the earliest stage its log shows an action in, or Discovery
+ is_done: bool
	// true only in a stage, and only when every required fidelity in that stage is done
+ next: FidelityProgress
	// the first fidelity in its current stage that is not done; none when it is done or Complete
----
+ pull(): Stage
	// only when is_done and its stage has a next stage; writes `pull <next stage>` to its session log and returns that stage; fails with StageNotDone otherwise. A done ticket in Implementation is closed, not pulled.
+ close(): Ticket
	// after closing, its folder is in `closed/` and its column is Complete
+ archive(): Ticket
	// after archiving, its folder is in `_archive/` and it is off the board
- _log_lines(): list[str]
	// a log line starts with the action; the paths that follow are joined by ", " and can hold spaces; then come the practice and fidelity. Find the practice and fidelity by their names, never by position. The practice appears as its folder name (`clean_engineering`) in action lines and as its class name (`CleanEngineering`) in validate lines.

## FidelityProgress

+ FidelityProgress(fidelity: FidelityGuidance, stage: Stage, done_actions: list[GuidanceAction])
	// validate is done only when its latest line for this fidelity names no graph-rule violations; review is done only after that
------
+ fidelity: FidelityGuidance
+ << association >> stage: Stage
+ done_actions: list[GuidanceAction]
+ remaining_actions: list[GuidanceAction]
	// the stage's actions not yet done, in order
	-> Stage.actions
+ is_done: bool
----

## BacklogItem

+ BacklogItem(path: Path, board: Board)
------
+ title: str
+ path: Path
----
+ start(scope: str): Ticket
	// the new ticket's session log names this item's path
	-> Board.new_ticket

## Open

- Review is a new action beside Generate and Validate, a `GuidanceAction` deployed as a command for now (`/review <guidance>`). It records a person's approval of a fidelity as a `review` line in the session log, which the ticket reads like any other action line.
- Starting a ticket's session (its folder and branch) stays with `space/session` and `space/repo`; the board reads what they write and does not call them.
