## Language

*Board* shows every work session as a ticket and where each ticket stands in delivery: Backlog, then the stages Discovery, Specification, and Implementation, then Complete. A caller reads it to see what is in flight and what to do next. It stores no ticket state: tickets read their own session logs each time they are asked, so the board can never disagree with the work.

### board

- Created with the practices chosen for the work (for example Stories, DDD, and UX). The columns and stages follow from those practices.
- Reads `.sessions/`: every folder there is a ticket; `closed/` holds finished tickets; `_backlog/` holds backlog items; `_options/` holds options; `_archive/` holds archived sessions. Options and archived sessions are not on the board.

### column

- One of the places a ticket can be: Backlog, a stage, or Complete. A caller asks a column for its tickets.
- **Invariant:** every ticket is in exactly one column.

### stage

- Discovery, Specification, or Implementation: a column where work is done, split into in progress and done.
- Its *work required* is every chosen practice's fidelity for that stage. Each practice already says which fidelity belongs to which stage (`stage:` on every fidelity section in the practice's markdown), so the stage reads it from the practices rather than keeping a table.
- Its *actions* are the steps every fidelity in the stage goes through. For now every stage uses the same three: Generate, Validate, then a human review.

### ticket

- One work session seen as a unit of delivery: its title, scope, and *lineage* (the ticket it was split from).
- Knows its own location and progress by reading its own `session.log` against the board's stages.
- **Invariant:** a ticket never moves to the next stage by itself. Someone pulls it, and the pull is written to its session log.

### progress

- For each fidelity the board requires: which of its stage's actions are done and which are not.
- A fidelity is done in its stage when every action is done. Validate counts as done only when its latest run for that fidelity found no violations; review counts only after that.

### backlog item

- An idea not yet started: one markdown file per idea in `.sessions/_backlog/`. Backlog items are the Backlog column. Starting one opens a ticket for it.

### option

- A potential idea, before it is on the backlog: one markdown file per idea in `.sessions/_options/`, the same as a backlog item. Options are kept off the board; promoting one moves its file into `_backlog/`.

Build order: `Column` → `Stage` → `FidelityProgress` → `Ticket` → `BacklogItem` → `Board`

---

# harness/kanban

- **Purpose:** Show every work session as a ticket on a kanban, placed by how far each of the board's fidelities has got through its stage's actions, and move tickets through the stages.
- **Seam (terms):** Board, Column, Stage, Ticket, FidelityProgress, BacklogItem
- **Dependencies (one-way):** harness/guidance (PracticeGuidance, FidelityGuidance), harness/guidance_actions (GuidanceAction), cdd_guidance/actions (Generate, Validate)

## Constraint

Create a board with its practices, then read columns and tickets from it; everything is re-read from `.sessions/` when asked. Move a ticket only through `Ticket.pull`, `Ticket.close`, and `Ticket.archive`, so every move is a log line or a folder move the ticket reads back. Store only what cannot be read from the work: a ticket's title, scope, and lineage in its `session.json`. Never store progress or location.

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
	// every folder in sessions_folder whose name does not start with `_`, plus every folder in `closed/`
+ << aggregation >> backlog_items: list[BacklogItem]
	// every markdown file in `_backlog/`
+ << aggregation >> options: list[BacklogItem]
	// every markdown file in `_options/`; never shown on the board
+ active: Ticket
	// the ticket whose session is the current session
----
+ to_json(): dict
	// every column with its tickets; the shape the board pane and other IDEs read
	-> Column.tickets
+ new_ticket(title: str, scope: str, parent: Ticket): Ticket
	// a new ticket is in Backlog until its first action is done
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

## Stage : Column

+ Stage(name: str, board: Board, actions: list[GuidanceAction])
	// for now every stage is given Generate, Validate, and review, in that order
------
+ actions: list[GuidanceAction]
+ practices: list[PracticeGuidance]
	-> Board.practices
+ work_required: list[FidelityGuidance]
	// every chosen practice's fidelity whose stage is this stage, in practice order
	-> GuidanceCollection.child_for_stage
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
	// Backlog until any action is done; then the stage it was last pulled into, starting at Discovery; Complete once its folder is in `closed/`
+ is_done: bool
	// true only when every required fidelity in its current stage is done
+ next: FidelityProgress
	// the first fidelity in its current stage that is not done; none while it waits to be pulled
----
+ pull(): Column
	// only when is_done; writes `pull <stage>` to its session log; fails with StageNotDone otherwise
+ close(): Ticket
	// after closing, its folder is in `closed/` and its column is Complete
+ archive(): Ticket
	// after archiving, its folder is in `_archive/` and it is off the board
- _log_lines(): list[str]
	// finds an action, practice, and fidelity in a line by their names, never by position: paths come first and can hold spaces and commas

## FidelityProgress

+ FidelityProgress(fidelity: FidelityGuidance, stage: Stage, done_actions: list[GuidanceAction])
	// validate is done only when its latest run for this fidelity found no violations; review is done only after that
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
+ is_option: bool
	// true while its file is in `_options/`
----
+ promote(): BacklogItem
	// only an option; afterwards its file is in `_backlog/`
+ start(scope: str): Ticket
	// the new ticket's session log names this item's path
	-> Board.new_ticket

## Open

- Human review has no action class yet. Until it does, a review is a `review <practice> <fidelity>` line in the session log, and `Stage.actions` holds Generate, Validate, and that review step.
- Starting a ticket's session (its folder and branch) stays with `space/session` and `space/repo`; the board reads what they write and does not call them.
