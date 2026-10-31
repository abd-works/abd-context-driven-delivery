## Language

*KanbanBoard* shows every work session as a ticket and where each ticket stands in delivery: Backlog first, then the three stages Discovery, Specification, and Implementation, then Complete. A caller reads it to see what is in flight and what to do next. It holds no state of its own: it reads the session folders under `.sessions/` each time it is asked, so it can never disagree with the work.

### kanban board

- Lets a person see all delivery work at once, and lets Claude know which ticket it is working on and what that ticket needs next.
- Reads `.sessions/`: every folder there is a *ticket*; `closed/` holds finished tickets; `_backlog/` holds *backlog items*; folders whose names start with `_` (`_archive/`, `_options/`) are not tickets.
- Columns are fixed: Backlog, Discovery, Specification, Implementation, Complete. Each *stage* column has an in-progress part and a done part.
- **Invariant:** every ticket occupies exactly one column.

### ticket

- One work session, seen as a unit of delivery: its title, scope, *lineage*, the *guidance* it needs, and how far each guidance has got.
- A ticket is the session folder `.sessions/{name}/`; its fields live in that folder's `session.json`, and its progress is read from that folder's `session.log`.
- **Invariant:** a ticket never moves to the next stage by itself. Someone pulls it, and the pull is written to its session log.

### lineage

- The ticket a ticket was split from (*scatter*), so a story-level ticket still traces back to its feature.

### selected guidance

- The practice fidelities this ticket needs, chosen from the board options: one ticket may need only Stories and UX, another all five practices.
- Progress, board position, and the next guidance count only the selected guidance, so a ticket is never held back by work it does not need.

### skill progress

- How far one selected guidance has got on one ticket: not started, in progress, violations, or reviewed.
- Read from the ticket's session log, never stored. The latest `validate` line for that guidance decides between violations and reviewed: review is the practice's own rules passing.

### column

- One of the five places a ticket can be: Backlog, Discovery, Specification, Implementation, Complete.
- Backlog and Complete are plain columns. The other three are *stages*.

### stage

- Discovery, Specification, or Implementation: a column where work is done, with an in-progress part and a done part.
- Each practice already says which of its fidelities belongs to which stage: every fidelity section in a practice's markdown declares `stage:`, read as `FidelityGuidance.stage`. The board keeps no table of its own.
- *Stage work required* for a ticket is its selected guidance whose stage is this stage.

### board position

- Where a ticket sits: a column, and, in a stage, whether the stage is done (waiting to be pulled).
- Derived from the ticket's skill progress, its pull lines, and whether its folder is in `closed/`.

### backlog item

- An idea not yet started: a markdown file in `.sessions/_backlog/`. Starting it opens a ticket for it.

### board options

- `.sessions/_options/`: the guidance a ticket can select from, and the guidance a new ticket starts with.

Build order: `Column` → `Stage` → `SkillProgress` → `SessionLog` → `BoardPosition` → `BoardOptions` → `Ticket` → `BacklogItem` → `KanbanBoard`

---

# harness/kanban

- **Purpose:** Show every work session as a ticket on a kanban, placed by how far its selected guidance has got, and move tickets through the stages.
- **Seam (terms):** KanbanBoard, Ticket, BacklogItem, BoardPosition, SkillProgress, Column, Stage
- **Dependencies (one-way):** space/session (Session), space/repo (Repo), harness/guidance (FidelityGuidance)

## Constraint

Read the board through `KanbanBoard.board()`; it re-reads `.sessions/` every time. Move a ticket only through `Ticket.pull`, `Ticket.close`, and `Ticket.archive`, so every move is a log line or a folder move the board reads back. Store only what cannot be read from the work: title, scope, lineage, and selected guidance in `session.json`. Never store skill progress or board position.

## KanbanBoard

+ KanbanBoard(sessions_folder: Path, options: BoardOptions, session: Session)
	// always re-reads sessions_folder when asked; holds no ticket state between calls
------
+ << composition >> columns: list[Column]
	// always Backlog, Discovery, Specification, Implementation, Complete, in that order; the middle three are Stages
+ << aggregation >> tickets: list[Ticket]
	// every folder in sessions_folder whose name does not start with `_`, plus every folder in `closed/`
+ << aggregation >> backlog: list[BacklogItem]
	// every markdown file in `_backlog/`
+ << association >> options: BoardOptions
+ active: Ticket
	// the ticket whose session is the current session
----
+ board(): dict
	// the columns, with every ticket and backlog item in exactly one
	-> Ticket.position
	-> Ticket.next_guidance
+ new_ticket(title: str, scope: str, parent: Ticket): Ticket
	// a new ticket starts in Backlog with the options' default guidance
	-> Session.new
	-> BoardOptions.default_guidance
+ ticket(name: str): Ticket
- _ticket_folders(): list[Path]

## Ticket

+ Ticket(session: Session, log: SessionLog, stages: list[Stage], repo: Repo)
	// never moves to the next stage by itself
------
+ name: str
+ title: str
+ scope: str
+ << association >> lineage: Ticket
+ selected_guidance: list[FidelityGuidance]
	// always a subset of the board options' available guidance
+ << composition >> skill_progress: list[SkillProgress]
	// one per selected guidance; read from the session log, never stored
	-> SessionLog.progress_for
+ position: BoardPosition
	-> SessionLog.pulled_into
	-> Stage.work_required
+ next_guidance: FidelityGuidance
	// the first selected guidance in the current stage that is not reviewed; none while waiting to be pulled
+ is_closed: bool
----
+ select_guidance(guidance: list[FidelityGuidance]): Ticket
	// must only hold guidance the board options make available
+ pull(): BoardPosition
	// only when the current stage's work required is all reviewed; fails with StageNotDone otherwise
	-> SessionLog.record_pull
+ switch_to(): Ticket
	-> Session.switch
	-> Repo.switch_branch
+ close(): Ticket
	// after closing, the folder is in `closed/` and the ticket shows as Complete
	-> Session.close
+ archive(): Ticket
	// after archiving, the folder is in `_archive/` and the ticket is off the board
- _stage_done(stage: Stage): bool

## SkillProgress

+ SkillProgress(guidance: FidelityGuidance, state: str)
------
+ guidance: FidelityGuidance
+ state: str
	// one of not_started, in_progress, violations, reviewed
+ is_reviewed: bool
----

## SessionLog

+ SessionLog(log_path: Path, guidance: list[FidelityGuidance])
	// finds a guidance in a line by its practice and fidelity names, never by position: paths come first and can hold spaces and commas
------
----
+ progress_for(guidance: FidelityGuidance): SkillProgress
	// reviewed only when the latest validate line for that guidance has no violations
+ pulled_into(): Stage
	// the stage named by the latest pull line; none before the first pull
+ record_pull(stage: Stage): None
	-> Session.append_log
- _lines_naming(guidance: FidelityGuidance): list[str]

## BoardPosition

+ BoardPosition(column: Column, is_done: bool)
	// is_done only in a Stage, and only when every selected guidance in that stage is reviewed
------
+ << association >> column: Column
+ is_done: bool
+ is_ready_to_pull: bool
	// true only in a done Stage before Implementation
----

## Column

+ Column(name: str)
------
+ name: str
----

## Stage : Column

+ Stage(name: str)
------
----
+ work_required(selected: list[FidelityGuidance]): list[FidelityGuidance]
	// the selected guidance whose stage is this stage, in practice order

## BacklogItem

+ BacklogItem(path: Path, board: KanbanBoard)
------
+ title: str
+ path: Path
----
+ start(scope: str): Ticket
	// the new ticket's session log names this item's path
	-> KanbanBoard.new_ticket

## BoardOptions

+ BoardOptions(options_folder: Path)
	// with no `_options/` folder, every practice fidelity is available and selected by default
------
+ available_guidance: list[FidelityGuidance]
+ default_guidance: list[FidelityGuidance]
	// always a subset of available_guidance
----
