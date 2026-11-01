## Language

*Board* shows a repository's delivery. A repository has sessions, each session is represented on the board as a ticket, and each ticket is in a column: Backlog, a stage (Discovery, Specification, or Implementation), or Complete. A caller reads it to see what is in flight and what to do next. It stores no ticket state: tickets read their sessions each time they are asked, so the board can never disagree with the work.

### board

- Its columns are always the same: Backlog, one stage for each stage name, then Complete. Practices play no part in them, because the session of each ticket says which practices that ticket works on.
- Has a reference to one repository, and shows one ticket for each of the repository's sessions.
- The main session is in use when no named session is open, so it is not a ticket. Closed sessions are finished tickets; archived sessions are off the board.

### card

- Anything on the board that a person moves: a ticket or a backlog item. Every card has a title, a column, and its last activity, and moves forward and backward the same way.
- Moving a backlog item forward starts it as a ticket in Discovery. Moving a ticket back out of Discovery returns it to a backlog item.

### column

- One of the places on the board: Backlog, a stage, or Complete.
- **Invariant:** every card is in exactly one column. Backlog holds backlog items, not tickets.

### stage

- A column where work is done, split into in progress and done. There are exactly three stages, one for each `StageName`: Discovery, Specification, and Implementation.
- Each fidelity section in a practice's markdown declares its `StageName`, so a stage needs no table of fidelities.

### ticket

- The visual representation of one session on the board, with its title, scope, and *lineage* (the ticket it was split from). It holds no work of its own: every question about work goes to its session.
- Starts in the earliest stage its session shows work in, or Discovery when nothing is done yet. After that it moves only when a person moves it.
- **Invariant:** a ticket never moves to another column by itself. A person moves it with the arrows, whatever its session's work, and the move is written to its session log with the stage it enters.

### session

- Has the work that is done. It knows its past work by reading its own log, and it finds the files that work produced by asking the knowledge graph.
- Its *work required* is every fidelity of its active practices. A practice is active until a person turns it off for this session, so tickets can work on different practices on one board.
- Each fidelity goes through the same actions in order: Generate, Validate, then Review, where a person approves it. Each action on a fidelity is to do, in progress, or done.
- A fidelity is done when every action is done. Validate is done when its latest activity on that fidelity names no graph-rule violations. The AI-judged rules are not written to the log; the person checks them in Review, which counts only after Validate is done.
- *Next action* is what Run next does on a ticket: generate, validate, then review for each practice in order, then the same for the next practice. Violations hold a session on that fidelity, because Review needs a clean Validate, so the next action is satisfy until they are fixed. This is intended and not built.

### activity

- One thing that happened in a session, read from one line of its log: when, which action on which fidelity and format, or which stage a person moved the ticket into. It keeps every reader from parsing log text.

### backlog item

- An idea not yet started: one markdown file per idea in `.sessions/_backlog/`, added by a person. The Backlog column shows them. Starting one opens a ticket for it.
- A ticket moved back into the Backlog keeps its work, and starting its item brings the ticket back with that work. This is intended and not built.

### the work behind a ticket

- *Practices* say what has to be produced. Each practice has *fidelities*, and each fidelity names the stage that requires it, the *artifacts* it produces, and the *rules* those artifacts must keep. An artifact is a file a fidelity's `outputs` declares, saved relative to the session's workpath, so it is a path rather than a class.
- *Actions* do the work on one fidelity inside a session. Generate writes the artifacts. Validate reads them into the *knowledge graph*, runs the rules on its nodes, and saves a report. Review records a person's approval.
- Each node of the knowledge graph knows the fidelity that creates it, the file it came from, and the rules it breaks, so the graph can say which files belong to a fidelity.
- The board runs none of this. Each action writes a line to the session log, and the session answers from those lines and from the graph.

Build order: `Column` → `Stage` → `Backlog` → `Card` → `Ticket` → `BacklogItem` → `Board`

---

# harness/kanban

Purpose, seam, dependencies, and constraint: `.context/module-context.md`.

Sources: `board.py`, `ticket.py`, `backlog_item.py`, `kanban.py`, and for what is not built yet, the Board canvas at https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN (Version 72). A member whose note starts "Intended:" is not in the code yet. Everything else mirrors the code. The modules after `harness/kanban` show only the members the board's work depends on.

## Board

+ Board(repo: Repo)
	// Intended: takes only the repository, in place of a sessions folder and a list of practices
------
+ << association >> repo: Repo
	// Intended
+ << composition >> columns: list[Column]
	// always Backlog, then one Stage for each StageName, then Complete
+ << composition >> tickets: list[Ticket]
	// Intended: one per session of the repository
	-> Repo.sessions
+ << aggregation >> backlog_items: list[BacklogItem]
	// every markdown file in the repository's `.sessions/_backlog/`
+ active: Ticket
	// the ticket that represents the repository's current session; none in the main session
	-> Repo.current_session
----
+ to_json(): dict
	// the project, the active ticket's name, and every column with its tickets or items; the shape the board pane and other IDEs read
	-> Column.to_json
+ new_ticket(title: str, scope: str, parent: Ticket, path: str): Ticket
	// a new ticket is in Discovery, in progress, until its log shows work in a later stage
+ add_backlog_item(title: str, text: str): BacklogItem
	// Intended: writes one markdown file to `_backlog/`, the title as its heading and the text under it
+ ticket(name: str): Ticket
+ column(name: str): Column

## Column

+ Column(name: str, board: Board)
------
+ name: str
+ << aggregation >> cards: list[Card]
	// Intended, in place of tickets: every card of the board whose column is this one
	-> Board.tickets
	-> Board.backlog_items
	-> Card.column
----
+ to_json(): dict
	-> Card.to_json

## Backlog : Column

+ Backlog(board: Board)
------
----

## Stage : Column

+ Stage(name: StageName, board: Board)
------
+ << association >> name: StageName
+ next_stage: Stage
	// none after Implementation
+ previous_stage: Stage
	// none before Discovery
+ in_progress: list[Ticket]
+ done: list[Ticket]
	// tickets in this stage that are done; they wait here until a person moves them
	-> Ticket.is_done
----
+ to_json(): dict
	-> Card.to_json

## Card

Intended: the base type of Ticket and BacklogItem, which today share nothing in code.

------
+ title: str
+ << association >> column: Column
+ last_activity: Activity
	// none when nothing has happened yet
----
+ move_next(): Card
	// a person's move to the next column
+ move_previous(): Card
	// a person's move to the previous column
+ to_json(): dict

## Ticket : Card

+ Ticket(session: Session, board: Board)
	// Intended: takes the session it represents, in place of a session folder. Never moves to another column by itself
------
+ << association >> session: Session
	// Intended
+ name: str
	-> Session.name
+ scope: str
+ << association >> lineage: Ticket
+ column: Column
	// Complete once its session is closed; otherwise the stage named by its latest move activity; before any move, the earliest stage its session shows work in, or Discovery
	-> Session.activities
+ is_done: bool
	// true only in a stage, and only when its session has done every fidelity required in that stage
	-> Session.is_stage_done
+ last_activity: Activity
	// Intended, in place of a timestamp: its session's latest activity; none when it has none
	-> Session.activities
----
+ move_next(): Ticket
	// a person's move to the next column, whatever its session's work: writes `pull <next stage>` to its session log, and out of Implementation it closes
+ move_previous(): Card
	// a person's move to the previous column: writes `pull <previous stage>`; out of Complete its session reopens in Implementation; Discovery is as far back as it goes. Intended: out of Discovery it moves into the Backlog and returns its BacklogItem, its folder kept under `_backlog/`, and it stops being the active ticket because the board no longer finds it
+ close(): Ticket
	// after closing, its session is closed and its column is Complete
+ archive(): Ticket
	// after archiving, its session is archived and it is off the board
+ to_json(): dict
	// its fields and column, with its session's work, next action, handoff, reports, and artifacts for each fidelity
	-> Session.action_states
	-> Session.artifacts

## BacklogItem : Card

+ BacklogItem(path: Path, board: Board)
------
+ title: str
	// the item's first `# ` heading, or its file name in words
+ column: Column
	// always the Backlog
+ text: str
	// Intended: the file's content after its heading; the details show it
+ path: Path
+ last_activity: Activity
	// Intended, in place of a timestamp: an activity holding only when its file last changed
----
+ move_next(): Ticket
	// Intended: starts it with scope feature, working on the whole repository
+ move_previous(): BacklogItem
	// Intended: it stays in the Backlog
+ start(scope: str, path: str): Ticket
	// the new ticket's session log names this item's path. Intended: an item a ticket was moved back into returns that ticket with its folder, log, and progress, and the item goes
	-> Board.new_ticket
+ to_json(): dict

## Kanban

+ Kanban(project: str)
	// the board as cdd MCP tools; the project is CDD_PROJECT, else the current folder, and the board shows that repository
------
----
+ board(): dict
	-> Board.to_json
+ move_next(ticket: str): dict
	-> Ticket.move_next
+ move_previous(ticket: str): dict
	-> Ticket.move_previous
+ start(backlog_item: str, scope: str, path: str): dict
	-> BacklogItem.start
+ new(title: str, scope: str, parent: str, path: str): dict
	-> Board.new_ticket
+ add_backlog_item(title: str, text: str): dict
	// Intended: the + on the Backlog heading
	-> Board.add_backlog_item
+ enable_practice(ticket: str, practice: str, is_enabled: bool): dict
	// Intended: sets practices[practice].enabled on the ticket's session, because an MCP tool takes names
	-> Session.practices
	-> Practice.enabled
+ close(ticket: str): dict
	-> Ticket.close
+ archive(ticket: str): str
	-> Ticket.archive

# space/repo

The repository the board shows. Only the members the board's work depends on are shown.

## Repo

+ Repo(root: Path)
------
+ root: Path
+ << composition >> sessions: list[Session]
	// Intended: every session in `.sessions/` and `.sessions/closed/`. The main session is not listed, and folders whose names start with `_` are not sessions
+ current_session: Session
	// Intended: the session saved in `.sessions/session.json`, else the main session
----

# space/session

The work session a ticket represents.

## Session

Has the work that is done. Its log says what happened, and the knowledge graph says which files that work produced.

------
+ name: str
+ workpath: Path
	// the folder of the repository the session works on; every artifact path is relative to it. The main session's is the repository
+ session_path: Path
	// `.sessions/{name}/`, holding `session.log`, `session.json`, `handoff-*.md`, and `validation-reports/`
+ << composition >> practices: dict[str, Practice]
	// Intended, in place of a list of the opened practices: every practice CDD has, by practice key, each active unless this session turned it off
+ active_practices: list[Practice]
	// Intended: the practices whose enabled is true; a new session has all of them
+ work_required: list[FidelityGuidance]
	// Intended, moved from the board: every fidelity of its active practices, in stage order
	-> Session.active_practices
	-> PracticeGuidance.fidelities
+ << composition >> activities: list[Activity]
	// Intended: one for each line of `session.log`, oldest first, read each time
+ latest_handoff: Path
	// Intended, moved from the ticket: the newest `handoff-*.md`; none when it has none
+ next_action: GuidanceAction
	// Intended, moved from the ticket: the first action not done on the first fidelity not done; satisfy while that fidelity has violations, so Run next never validates again over open violations
----
+ practice(name: str): Practice
+ action_states(fidelity: FidelityGuidance): dict[GuidanceAction, ActionState]
	// Intended: one state for each of Generate, Validate, and Review, in order, read from its activities on this fidelity
	-> Activity.action
+ is_stage_done(stage: StageName): bool
	// Intended: every required fidelity of that stage has every action done
	-> Session.action_states
+ violations(fidelity: FidelityGuidance): list[str]
	// Intended: the violations of its latest Validate on this fidelity
	-> Activity.violations
+ reports(fidelity: FidelityGuidance): list[Path]
	// Intended, moved from the ticket: this fidelity's dated files in `validation-reports/`, newest last
+ artifacts(fidelity: FidelityGuidance): list[Path]
	// Intended: the files this fidelity produced, for the list, folder, and files on the card
	-> Practice.artifacts
+ fidelity_outputs(guidance: PracticeGuidance): dict
	// where the active fidelity's artifacts are saved under the workpath, with the overrides in `session.json`
	-> FidelityGuidance.outputs
+ log_guidance_action(action: str, guidance_items: list)
+ log_validation(guidance: PracticeGuidance, violations: list[str])

## Practice

------
+ name: str
+ << association >> guideline: PracticeGuidance
+ << composition >> graph: Graph
	// the knowledge graph of this practice's artifacts in the session
+ folder_sets: list
+ enabled: bool
	// Intended: whether the session works on this practice; setting it saves it in the `practices` field of `session.json`. True until set
----
+ artifacts(fidelity: FidelityGuidance): list[Path]
	// Intended: asks this practice's knowledge graph which files that fidelity's nodes came from
	-> Graph.files_of

## ActionState : Enum

Intended: the only three states an action on a fidelity can be in.

------
+ TO_DO
+ IN_PROGRESS
+ DONE
----

## Activity

Intended: a value object, so readers of the session log get typed values instead of parsing text.

------
+ at: datetime
+ << association >> action: GuidanceAction
	// none on a move line
+ << association >> fidelity: FidelityGuidance
	// none on a move line
+ format: str
	// the format the action ran in, such as markdown or drawio
+ paths: list[Path]
+ violations: list[str]
	// the `graph-rule` entries on a validate line
+ entered_stage: str
	// the stage a person moved the ticket into; none on an action line
----
+ from_log_line(line: str, session: Session): Activity
	// a log line starts with the action; the paths that follow are joined by ", " and can hold spaces; then come the practice and fidelity. Find the practice and fidelity by their names, never by position. The practice appears as its folder name (`clean_engineering`) in action lines and as its class name (`CleanEngineering`) in validate lines.
	-> Session.practice

# harness/guidance

The practices, their fidelities, and their rules: what a ticket has to get done.

## PracticeGuidance

------
+ << composition >> fidelities: list[FidelityGuidance]
+ << composition >> rules: RulesCollection
	// the rules shared by every fidelity of this practice
----

## FidelityGuidance

------
+ name: str
+ << association >> stage: StageName
	// which stage requires this fidelity, read from the fidelity's section in the practice markdown. Intended: a StageName, in place of a string
+ outputs: dict
	// the artifacts this fidelity produces: a file, pattern, or folder per format, relative to the session's workpath
+ << composition >> rules: RulesCollection
	// the rules this fidelity's artifacts are validated against
----

## RulesCollection

------
+ << composition >> rules: list[Rule]
----

## Rule

------
+ slug: str
----

# cdd_guidance/practices

## StageName : Enum

Intended: an enum in place of the three string constants in `stages.py`, so a stage can only be one of these. `STAGE_NAMES` in `harness/kanban/board.py` goes, because it repeats them.

------
+ DISCOVERY
+ SPECIFICATION
+ IMPLEMENTATION
----

# harness/guidance_actions

## GuidanceAction

------
+ << association >> listed: list[FidelityGuidance]
	// the guidance this call runs on
----
+ run(guidance: GuidanceArg, operation, action: str)
	// runs the action on each listed fidelity and writes the action's line to the session log; that line is what the session reads back
	-> Session.log_guidance_action

## Generate : GuidanceAction

------
----
+ generate(guidance: GuidanceArg): str
	// the agent writes the fidelity's artifacts where its outputs say
	-> Session.fidelity_outputs

## Validate : GuidanceAction

------
----
+ validate(guidance: GuidanceArg, rule: Rule, graph: bool, paths: list[str]): str
	// builds the knowledge graph from the artifacts in paths, runs the fidelity's rules on it, saves the report in the session's `validation-reports/`, and logs one `graph-rule` entry per violation
	-> Graph.load_files
	-> Session.log_validation

## Review : GuidanceAction

------
----
+ review(guidance: GuidanceArg): str
	// records a person's approval of the fidelity's artifacts as a `review` line in the session log

# harness/graph

The knowledge graph: the artifacts read into nodes, with each practice's rules run on them.

## Graph

------
+ << composition >> practices: dict[str, PracticeGraph]
----
+ load_files(folder: str, practices: list[str], files: list[str], overlays: list[str]): str
	// builds each practice from only the given artifacts and runs its rules on them
+ files_of(fidelity: str): list[str]
	// Intended: the source files of every node that fidelity creates
	-> Node.fidelity
	-> Node.source
+ write_json(path: str): str

## PracticeGraph

------
+ name: str
+ << composition >> nodes: dict[str, list[Node]]
----

## Node

------
+ type: str
+ source: Source
	// where it came from; source.file is the artifact's path
+ fidelity: str
	// the fidelity that creates this node, so the graph can answer for one fidelity
	-> FidelityGuidance.name
+ failed_rules: list[str]
	// the slugs of the rules this node breaks; Validate logs these as `graph-rule` entries
	-> Rule.slug
----

---

**Open**

- Starting a ticket's session (its folder and branch) stays with `space/session` and `space/repo`; the board reads what they write and does not call them.
- Review is a `GuidanceAction` deployed as a command (`/review <guidance>`). It records a person's approval of a fidelity as a `review` line in the session log, which the ticket reads like any other action line.
- The move line still reads `pull <stage>`. Dropping pull from the language means choosing a new word for that line and what to do with lines already in session logs.
- On the canvas a stage has two steps, so an arrow moves a ticket from In progress to Done and only then across the column. `is_done` is derived from progress here, so the real board has nowhere to record a person's move to Done, and its arrows cross a column in one step. Either the ticket records that move in its log or the arrows keep crossing in one step.
- Locking is pane state, not a board rule: with Active session only on, the canvas disables every action on a ticket other than `Board.active`. The pane reads `active` from `Board.to_json` and holds the switch itself.
- Ticket-wide Run sends one action across a ticket's enabled practices at its current stage. It is a prompt the pane fills, so it needs no operation here beyond `Ticket.practices`.
- `FidelityProgress` and `Stage.work_required` are still in the code. `Session` takes over what they do, and the ticket stops reading the log itself.
- `Session.fidelity_outputs` reads the session it is called on, so `Repo.sessions` must give sessions that can be read without one becoming the current session. `Session` today has one in-memory current, and opening one saves it as current.
- `Board.new_ticket` takes four arguments, over the limit of three. `Repo` creating the session and the board representing it as a ticket would remove `title`, `scope`, `parent`, and `path` from this seam together.
- `space/repo` already has a class named `Ticket`, a GitHub issue. It is a different concept from the board's Ticket and needs a different name in one of the two modules.
- A `format` argument on Generate is still to be decided.
