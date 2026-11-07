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

- The visual representation of one session on the board, with its title, scope, and *parent* (the ticket it was split from). It holds no work of its own: every question about work goes to its session.
- Starts in the earliest stage its session shows work in, or Discovery when nothing is done yet. After that it moves only when a person moves it.
- Its work goes on in its own *worktree*, a checkout of its branch beside the repository, and its *chat* is the chat working in that worktree. Clicking a ticket on the board sends the board's commands to that chat, shown under the ticket's name; when no chat works there yet, the board opens a new chat in the Claude app on the worktree from a `claude://code/new` link, whose prompt asks it to take the ticket's name as its title, opening the worktree first if the ticket has none. The app asks the person to confirm the folder and send, because it starts no session on its own.
- **Invariant:** a ticket never moves to another column by itself. A person moves it, by dragging it or moving it on and back, whatever its session's work, and the move is written to its session log with the stage it enters.

### session

- Has the work that is done. It knows its past work by reading its own log, and it finds the files that work produced by asking the knowledge graph.
- Works in one folder of the repository, its *workpath*; the whole repository until a person chooses one. Each practice writes under its own folder, its *practice root*: the folder a person chose for that practice, or else the workpath plus the practice's default folder.
- Its *work required* is every fidelity of its active practices. A practice is active until a person turns it off for this session, so tickets can work on different practices on one board.
- Each fidelity goes through the same actions in order: Generate, Validate, then Review, where a person approves it. Each action on a fidelity is to do, in progress, or done.
- A fidelity is done when every action is done. Validate is done when its latest activity on that fidelity names no graph-rule violations and the judgment the validating agent added to its latest report fails no rule. The person checks the AI-judged rules in Review, which counts only after Validate is done.
- *Next action* is what Run next does on a ticket: on the first fidelity not done in its stage or any stage before it, earliest stage first, the first of generate, validate, and review not done. Violations hold a session on that fidelity, because Review needs a clean Validate, so the next action is satisfy until they are fixed.

### activity

- One thing that happened in a session, read from one line of its log: when, which action on which fidelity and format, or which stage a person moved the ticket into. A move writes `move <stage>`.

### backlog item

- An idea not yet started: one markdown file per idea in `.sessions/_backlog/`, added by a person. The Backlog column shows them. Starting one asks for the workpath of its session, then opens a ticket for it.
- A ticket moved into the Backlog, from any column, keeps its whole folder there as `_backlog/<name>/<name>.md` beside its log and history, and that folder is a backlog item. Starting its item brings the ticket back with that work.

### the work behind a ticket

- *Practices* say what has to be produced. Each practice has *fidelities*, and each fidelity names the stage that requires it, the *artifacts* it produces, and the *rules* those artifacts must keep. An artifact is a file a fidelity's `outputs` declares, saved relative to the session's workpath, so it is a path rather than a class.
- *Actions* do the work on one fidelity inside a session. Generate writes the artifacts. Validate reads them into the *knowledge graph*, runs the rules on its nodes, and saves a report with the graph it checked beside it, so a report's violations stay on their nodes. Review is a person's approval, which the ticket records itself; it is not an action an agent runs.
- Each node of the knowledge graph knows the fidelity that creates it, the file it came from, and the rules it breaks, so the graph can say which files belong to a fidelity.
- The board runs none of this. Each action writes a line to the session log, and the session answers from those lines and from the graph.

Build order: `Column` → `Stage` → `Backlog` → `Complete` → `Card` → `Ticket` → `FidelityProgress` → `BacklogItem` → `Board` → `Help` → `Report`

---

# space/kanban

Purpose, seam, dependencies, and constraint: `.context/module-context.md`.

Sources: `board.py`, `ticket.py`, `backlog_item.py`, and `report.py`. Every class and member here is in the code. `kanban-model.drawio` still draws an older model (Ticket's string copies, `Workspace`, `TicketFiles`, `PracticeRoot`) and is to be redrawn from this file.

A member noted *data field* is marked `@data_field`: MCP sends an object as exactly those members, each object they hold as its own data, and the language adapter types `{Class}Data` from them. A data field sent under another name says so (*data field `slug`*). A *reference* data field (`@data_field(reference=True)`) sends the object it holds by its `@identity` fields alone, such as `{"name": "Discovery"}` for a column: the object is sent in full by the one that holds it, so a ticket names its column without sending the column, and the column's tickets, again.

A class marked `@identity(...)` names the data fields that name one of its objects. A language adapter reads them as the arguments of the class's `@tool_subject` loader, in the same order.

A `@tool_subject` loader or class tool that takes `project` is handed the project the call works on by its tool, so no tool takes it as an argument.

## Board

+ Board(repo: Repo, practices: list[PracticeGuidance])
------
+ << association >> repo: Repo
	// the repository the sessions folder sits in
+ project: str
	// data field: the repository folder's name
+ << aggregation >> practices: list[PracticeGuidance]
	// data field: the practices every ticket works through, each with its key, slug, short name, colour, and fidelities' slugs
+ << composition >> columns: list[Column]
	// data field; always Backlog, then one Stage for each stage name in `stages.py`, then Complete
+ << composition >> tickets: list[Ticket]
	// one per session of the repository
	-> Sessions.all
+ << aggregation >> backlog_items: list[BacklogItem]
	// every idea file in `.sessions/_backlog/`, and every ticket folder kept there
+ cards: list[Card]
	// its tickets, then its backlog items
+ active: Ticket
	// data field: the ticket of the session saved as open, sent whole; none while the main session is, since main is not on the board
	-> Sessions.saved
+ worktrees: dict[Branch, Worktree]
	// each branch's worktree, listed once per board read rather than once per ticket, because the board is read after every call; a project that is no git clone has none
	-> Repo.worktrees
----
+ load(project: Path): Board
	// the `@tool_subject` of the `board.*` tools, handed the call's project: the board of that project's main checkout with every practice chosen, so a chat in a ticket's worktree reads the same board
	-> Repo.checkout_folder
	-> Repo.primary_root
+ show(): Board
	// `board.show`
+ folders(path: str): list[str]
	// `board.folders`: the folders inside one folder of the repository, as paths from the project; installed packages, caches, and hidden folders are left out
	-> FileManager.list
+ help(slug: str): Help
	// `board.help`: the practice or fidelity slug names, such as `stories` or `stories-story-map`. Refuses a slug no practice or fidelity goes by with `PracticeNotFoundError`
+ practice(key: str): PracticeGuidance
	// the practice whose folder name is key, such as `clean_engineering`; raises `PracticeNotFoundError` for one the board does not have
+ ticket(name: str): Ticket
	// read from that ticket's session folder alone, open before closed
	-> Repo.work_session
+ backlog_item(title: str): BacklogItem
+ column(name: str): Column
	// raises `ColumnNotFoundError` for a column the board does not have

## Column

Marked `@identity("name")`, so a reference to a column is its name.

+ Column(name: str, board: Board)
------
+ name: str
	// data field
+ << aggregation >> cards: list[Card]
	// every card of the board whose column is this one
	-> Board.cards
	-> Card.column
----

## Backlog : Column

+ Backlog(board: Board)
------
+ items: list[BacklogItem]
	// data field: its cards
----

## Complete : Column

+ Complete(board: Board)
------
+ tickets: list[Ticket]
	// data field: its cards, the tickets whose sessions are closed
----

## Stage : Column

+ Stage(name: str, board: Board, actions: list[str])
------
+ actions: list[str]
	// generate, validate, and review, in that order, named as the session log names them
+ << aggregation >> work_required: list[FidelityGuidance]
	// data field: every fidelity of every chosen practice whose stage is this stage, each with its slug, name, outputs by format, and default format
	-> Board.practices
+ next_stage: Stage
	// none after Implementation
+ previous_stage: Stage
	// none before Discovery
+ wip_limit: int
	// data field: the limit saved for this stage in `.sessions/_board.json`, else 3
+ is_over_limit: bool
	// data field: it holds more tickets than its WIP limit
+ in_progress: list[Ticket]
	// data field
+ done: list[Ticket]
	// data field: tickets done in this stage, waiting here until a person moves them
	-> Ticket.is_done
----
+ load(stage: str, project: Path): Stage
	// the `@tool_subject` of the `stage.*` tools; refuses a column that is not a stage with `NotAStageError`
	-> Board.load
+ set_wip_limit(limit: int): Stage
	// `stage.set_wip_limit`: saved in `.sessions/_board.json` beside the other stages' limits

## Card

The base type of Ticket and BacklogItem.

+ Card(board: Board)
------
+ title: str
	// data field
+ << association >> column: Column
+ last_activity: str
	// data field; a timestamp, blank when nothing has happened yet
----
+ move_next(): Card
	// a person's move to the next column
+ move_previous(): Card
	// a person's move to the previous column

## Ticket : Card

Marked `@identity("name")`. Never moves to another column by itself: a person moves it, and the move is written to its session log.

+ Ticket(session: Session, board: Board)
------
+ name: str
	// data field: its session's name; a ticket is an agent toolset, whose own name is the toolset's, so without this it would answer "ticket"
	-> Session.name
+ << association >> session: Session
	// data field: its folders, its practices and their files, and its log
+ << composition >> progress: list[FidelityProgress]
	// data field: one per fidelity the board requires, in stage order, read from the session log each time; a judgment in the fidelity's latest report that fails a rule fails a validate the log shows passing
	-> FidelityProgress.from_log
+ << association >> column: Column
	// reference data field: Complete once its session is closed; otherwise the stage named by its latest `move` line; before any move, the earliest stage its log shows work in, or Discovery
+ is_closed: bool
	// data field: its session is closed, so it shows in Complete
+ is_active: bool
	// data field: its session is the one saved as open
+ drop_targets: list[str]
	// data field: the columns besides the stages it can be dropped on: the Backlog always, Complete from Implementation's Done or while it is active
+ is_done: bool
	// data field: true only in a stage, when a person marked it done there or, with no mark since entering, when all its enabled work there is done
+ next_fidelity: FidelityProgress
	// data field `next`: the first fidelity not done in its stage or any stage before it, earliest stage first, because later work builds on it; none once it is done in its stage
+ worktree: str
	// data field: the folder of its own worktree, where its chat works; empty while it has none
	-> Board.worktrees
+ last_activity: str
	// the timestamp of its log's latest line
----
+ load(ticket: str, project: Path): Ticket
	// the `@tool_subject` of the `ticket.*` tools; raises `TicketNotFoundError` for a ticket the board does not show
	-> Board.load
	-> Board.ticket
+ create(title: str, scope: str, parent: str, path: str, project: Path): Ticket
	// `ticket.create`: a new ticket in Discovery, in progress; it does not become the current session. scope is feature, story, or slice; parent names the ticket it was split from; path is its workpath
	-> Sessions.create
+ branch(): Branch
	// `ticket.branch`: its own branch, named as the ticket, with whether the repository has it and whether it is checked out, so activating a ticket offers only what is missing and leaving one commits, pushes, and merges only its own branch
	-> Repo.branch_named
+ progress_of(slug: str): FidelityProgress
	// raises `FidelityNotFoundError` for a fidelity the ticket does not have
+ activate(leaving: list[str], opening: list[str]): Ticket
	// `ticket.activate`: the active ticket leaves its work as leaving says (commit, push, merge), this ticket opens what opening names (branch, worktree), and its session becomes current
	-> Ticket.leave
	-> Repo.switch_branch
	-> Repo.switch_worktree
	-> Sessions.switch
+ open_worktree(): Ticket
	// `ticket.open_worktree`: opens its own worktree beside the repository, creating its branch when missing; the ticket comes back from a new board read, which lists the new worktree
	-> Branch.open_in_worktree
+ leave(leaving: list[str])
	// commits, pushes, and merges as leaving names, only when the ticket's own branch is checked out
	-> Repo.push_commit
	-> Repo.close_branch
+ move_next(): Ticket
	// `ticket.move_next`: from In progress it writes `done <stage>`, from Done it writes `move <next stage>`, and out of Implementation it closes
+ move_previous(): Ticket | BacklogItem
	// `ticket.move_previous`: from Done it writes `in-progress <stage>`, from In progress it writes `move <previous stage>` and `done <previous stage>`; out of Complete it reopens, and out of Discovery it returns to the Backlog
+ move_to(stage: str, done: bool): Ticket | BacklogItem
	// `ticket.move_to`: a person's drag into a stage's In progress or Done; into the Backlog from any column it returns to the Backlog with its whole folder
	-> BacklogItem.from_ticket
+ close(leaving: list[str]): Ticket
	// `ticket.close`: its session closes and its folder moves to `_complete/`
	-> Ticket.leave
	-> Session.close
	-> Session.move_to_closed
+ archive(): Ticket
	// `ticket.archive`: its session closes and its folder moves to `_archive/`, off the board
	-> Session.move_to_archive
+ violations(): Report
	// `ticket.violations`: the rules broken on every fidelity of its stage left with violations, each naming its fidelity, a rule two fidelities share listed once
	-> FidelityProgress.report
	-> Report.from_reports

## FidelityProgress

How far one fidelity has got through its stage's actions on one ticket, read from session log lines. Marked `@identity("ticket", "slug")`.

+ FidelityProgress(fidelity: FidelityGuidance, stage: Stage, done_actions: list[str], has_violations: bool, ticket: Ticket)
------
+ ticket: str
	// data field: the name of the ticket it is on
+ fidelity_slug: str
	// data field `slug`
+ << association >> fidelity: FidelityGuidance
	// data field: the fidelity as the ticket's session holds it, one object per fidelity in a session, with its name, outputs, and default format
+ << association >> stage: Stage
	// reference data field: the stage that requires the fidelity
+ practice: str
	// data field: its practice's key
+ is_enabled: bool
	// data field: the ticket's session works on its practice
+ next_action: str
	// data field: satisfy while it has violations, else the first of its stage's actions not done
+ allowed_actions: list[str]
	// data field: generate always; validate and review once an action is recorded or a declared file is there
+ state: str
	// data field: done, violations, in_progress, or not_started
+ action_states: ActionStates
	// data field `actions`
+ report_file: str
	// data field: its latest validation report, as a path from the project
+ violation_count: int
	// data field
+ done_actions: list[str]
+ remaining_actions: list[str]
+ has_violations: bool
+ is_done: bool
+ latest_report: ReportFile
+ rule_descriptions: dict[str, str]
	// each rule's text by slug, this fidelity's own winning over the practice's
----
+ from_log(fidelity: FidelityGuidance, stage: Stage, entries: list[LogEntry], ticket: Ticket): FidelityProgress
	// finds the fidelity by name, never by position
	-> LogEntry.names
+ load(ticket: str, fidelity: str, project: Path): FidelityProgress
	// the `@tool_subject` of the `fidelity-progress.*` tools
	-> Ticket.load
	-> Ticket.progress_of
+ finish_review(): FidelityProgress
	// `fidelity-progress.finish_review`: a person's approval, one `review <Practice> <fidelity>` line in its ticket's session log
+ report(): Report
	// `fidelity-progress.report`: its latest report, with the rules broken on the nodes of the graph saved beside it, then each rule the judgment fails
	-> ReportFile.report
+ files(): dict[str, list[FileEntry]]
	// `fidelity-progress.files`: the files the fidelity declares by format in its ticket's session
	-> FidelityGuidance.files
+ with_violations(): FidelityProgress
	// the same progress with its latest validate failed, for a judgment that fails a rule
+ rules_answered_by(report: ReportFile): set[str]

## ActionStates

Where each of a stage's actions stands on one fidelity.

------
+ generate: str
	// data field; to_do, in_progress, or done
+ validate: str
	// data field
+ review: str
	// data field
----

## BacklogItem : Card

Marked `@identity("title")`.

+ BacklogItem(path: Path, board: Board)
------
+ title: str
	// the item's first `# ` heading, or its file name in words
+ column: Column
	// always the Backlog
+ text: str
	// data field: the file's content after its heading
+ path_from_project: str
	// data field `path`
+ last_activity: str
	// when its file last changed
----
+ load(backlog_item: str, project: Path): BacklogItem
	// the `@tool_subject` of the `backlog-item.*` tools
+ create(title: str, text: str, project: Path): BacklogItem
	// `backlog-item.create`: writes one markdown file to `_backlog/`, the title as its heading and the text under it
+ from_ticket(ticket: Ticket, board: Board): BacklogItem
	// the item a ticket moved into the Backlog waits in: `_backlog/<name>/<name>.md`, inside the ticket's kept folder
+ write_if_missing(title: str)
+ start(scope: str, path: str): Ticket
	// `backlog-item.start`: an item a ticket was moved into returns that ticket with its folder; a new item's file moves into the new session folder
	-> Ticket.create
	-> Session.keep_file

## Help

What `board.help` answers: a practice or one of its fidelities, the guidance objects themselves, with the text help shows.

+ Help(practice: PracticeGuidance, fidelity: FidelityGuidance, stage: Stage)
------
+ << association >> practice: PracticeGuidance
	// data field
+ << association >> fidelity: FidelityGuidance
	// data field; none on a practice's help
+ << association >> stage: Stage
	// reference data field: the stage that requires the fidelity; none on a practice's help
+ overview: str
	// data field
+ guidance: str
	// data field
+ rules: list[Rule]
	// data field: the rules themselves, each with its slug and body
+ href: str
	// data field: the fidelity's page on the forge, or its practice's page for a fidelity the forge has none for
----

## Report

The rules a validation found broken, built from the saved report and the graph saved beside it. It lives in `report.py`.

+ Report(path: str, text: str, rules: list[ReportRule], has_saved_graph: bool)
------
+ path: str
	// data field
+ text: str
	// data field
+ << composition >> rules: list[ReportRule]
	// data field
+ has_saved_graph: bool
	// data field; false when the report has no saved graph, so its graph's rules are missing
+ violation_count: int
----
+ from_reports(folder: str, reports: list[Report]): Report
	// every rule broken in reports, each listed once though two fidelities share it

## ReportRule

+ ReportRule(fidelity: str, name: str, description: str, violations: list[Violation])
------
+ fidelity: str
	// data field
+ name: str
	// data field
+ description: str
	// data field
+ count: int
	// data field
+ << composition >> violations: list[Violation]
	// data field
----

## ReportFile

A validation report saved in a session folder, with the graph the validation checked saved beside it.

+ ReportFile(file: Path, progress: FidelityProgress)
------
+ file: Path
+ stamp: str
+ text: str
+ has_result: bool
	// it has a saved graph or a judgment; validate saves a report before the agent judges it
+ is_judged_failing: bool
	-> Judgment.from_report
----
+ report(): Report
	// the rules broken on the nodes of the saved graph, then each rule the judgment fails that the graph did not hit; each violation is named from the project, with the lines around it
	-> violations_from_graph_json_files
	-> GraphPractices.named
	-> Violation.in_file

## Judgment

One rule the judgment in a validation report fails, in one judged file.

------
+ file: str
+ rule: str
+ findings: list[Violation]
----
+ from_report(text: str): list[Judgment]
	// the rules a report's judgment fails, read from its `## Judgment` sections

## ColumnNotFoundError : LookupError

## NotAStageError : ValueError

## PracticeNotFoundError : LookupError

## FidelityNotFoundError : LookupError

## TicketNotFoundError : LookupError

## BacklogItemNotFoundError : LookupError

---

# Collaborators

The classes below belong to other modules and are modelled there; each lists only what the board reads.

## Repo

`space/repo`: `branch_named(name)`, `worktrees`, `checkout_folder`, `primary_root()`, `switch_branch`, `switch_worktree`, `push_commit`, `close_branch`, `file_manager`.

## Sessions

`space/session`: `all()`, `named(name)`, `open_name`, `create(name, workpath, title, scope, parent)`, `load(folder)`, `switch(name)`, `folder`, `backlog_folder`; the board's own `_board.json` sits in its `folder`.

## Branch

`space/repo`: `name`, `exists`, and `is_checked_out` are data fields, which `ticket.branch` sends; `open_in_worktree()`.

## Session

`space/session`: `name`, `title`, `log.entries`, `is_closed`, `practices`, `log.record(entry)`, `close`, `reopen`, `move_to_closed`, `move_to_archive`, `move_to_backlog`, `keep_file`, `from_project(path)`, `reports_folder`; sent as a ticket's `session` data field.

## PracticeGuidance

`harness/guidance`: `key`, `slug`, `short_name`, `colour`, and its fidelities' slugs are data fields; `fidelities`, `rules`, `overview`, `guidance`.

## FidelityGuidance

`harness/guidance`: `slug`, `name`, `outputs`, and `default_format` are data fields, which a stage's `work_required`, a progress's `fidelity`, and help send; `stage`, `rules`, `files()`, `reports()`, `has_declared_output()`.

## Rule

`harness/guidance`: `slug` and `body` are data fields, which help sends.

## Violation

`harness/graph` (`violation.py`): one place a rule is broken, the one shape for graph hits and judged findings. `location`, `line`, and `message` are data fields, and `source`, the numbered *SourceLine*s around the line, once `in_file(location, file, lines_before, lines_after)` has read them. A judged finding is `Violation(rule, message, location=..., line=...)`.
