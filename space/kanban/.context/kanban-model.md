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

- A column where work is done, split into in progress and done. There are exactly three stages, one for each `ApproachStage` in `STAGES` (`harness/guidance/stages.py`): Discovery, Specification, and Implementation.
- Each fidelity section in a practice's markdown declares its stage in a `**Stage:**` line, so a stage needs no table of fidelities.

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
- *Next action* is what Run next does on a ticket: on the first fidelity not done in its stage or any stage before it, earliest stage first, the first of generate, validate, and review not done. Violations hold a session on that fidelity, so the next action is review: a person reads the violations and tells the agent to fix them, and the review itself is recorded only after a clean Validate.

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

Sources: `board.py`, `ticket.py`, `backlog_item.py`, and `report.py`. Every class and member here is in the code. `kanban-model.drawio` draws the same classes and relationships.

A member noted *data field* is marked `@data_field`: MCP sends an object as exactly those members, each object they hold as its own data, and the language adapter types `{Class}Data` from them. A data field sent under another name says so (*data field `slug`*). A *reference* data field (`@data_field(reference=True)`) sends the object it holds by its `@identity` fields alone, such as `{"name": "Discovery"}` for a column: the object is sent in full by the one that holds it, so a ticket names its column without sending the column, and the column's tickets, again.

A class marked `@identity(...)` names the data fields that name one of its objects. A language adapter reads them as the arguments of the class's `@tool_subject` loader, in the same order.

A `@tool_subject` loader or class tool that takes `project` is handed the project the call works on by its tool, so no tool takes it as an argument.

## Board

+ Board(repo: Repo, practices: list[PracticeGuidance])
------
+ << association >> repo: Repo
	// the repository the sessions folder sits in
+ sessions: Sessions
	// the sessions of its repository: each one a ticket, and which is open
+ file: Path
	// `.sessions/_board.json`, what the repository's sessions share on the board, such as each stage's WIP limit
	-> Sessions.folder
+ project: str
	// data field: the repository folder's name
+ << aggregation >> practices: list[PracticeGuidance]
	// data field: the practices every ticket works through, each with its key, slug, short name, colour, and fidelities' slugs
+ << composition >> columns: list[Column]
	// data field; always Backlog, then one Stage for each `ApproachStage` in `STAGES` (`harness/guidance/stages.py`), then Complete
+ << composition >> tickets: list[Ticket]
	// one per session of the repository
	-> Sessions.all
+ << aggregation >> backlog_items: list[BacklogItem]
	// every idea file in `.sessions/_backlog/`, and every ticket folder kept there
	-> Sessions.backlog_folder
+ cards: list[Card]
	// its tickets, then its backlog items
+ active: Ticket
	// reference data field: the ticket of the session saved as open, sent by its name, since its column sends it whole; none while the main session is, since main is not on the board
	-> Sessions.open_name
	-> Board.ticket
+ worktrees: dict[Branch, Worktree]
	// each branch's worktree, listed once per board read rather than once per ticket, because the board is read after every call; a project that is no git clone has none
	-> Repo.is_clone
	-> Repo.worktrees
----
+ load(project: Path): Board
	// the `@tool_subject` of the `board.*` tools, handed the call's project: the board of that project's main checkout with every practice chosen, so a chat in a ticket's worktree reads the same board
	-> Repo.checkout_folder
	-> Repo.primary_root
	-> PracticeCatalogue.practices
+ show(): Board
	// `board.show`
+ folders(path: str): list[str]
	// `board.folders`: the folders inside one folder of the repository, as paths from the project; installed packages, caches, and hidden folders are left out
	-> Repo.file_manager
	-> FileManager.list
+ help(practice: str): Help
	// `board.help`: the help of the board's practice named practice, such as `stories`; a fidelity's help comes from its progress, `fidelity-progress.help`
	-> Board.practice
+ practice(key: str): PracticeGuidance
	// the practice whose folder name is key, such as `clean_engineering`; raises `PracticeNotFoundError` for one the board does not have
+ open_ticket(title: str, scope: str, parent: str, path: str): Ticket
	// a new ticket in Discovery, its session working on path, a folder in the repository
	-> Sessions.create
	-> Board.ticket
+ ticket(name: str): Ticket
	// read from that ticket's session folder alone, open before closed; none when no session has that name
	-> Sessions.named
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

Made for one `ApproachStage` of `STAGES`, which gives its title as the column's name, its scope, and its actions; the stage keeps it private.

+ Stage(approach: ApproachStage, board: Board)
------
+ steps: list[str]
	// generate, validate, and review, in that order, named as the session log names them
	-> ApproachStage.steps
+ scope: StageScope
	// data field: how much of the solution the stage's work covers, which the board draws as its shape
	-> ApproachStage.scope
+ actions: list[str]
	// data field: every action a person can run on a fidelity in this stage, its steps first, then iterate, sketch, render, and document
	-> ApproachStage.actions
+ producing_actions: list[str]
	// data field: the actions that write a fidelity's files, every action but validate and review
	-> ApproachStage.producing_actions
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
	// `stage.set_wip_limit`: saved in `.sessions/_board.json` beside the other stages' limits, keeping whatever else the file holds

## Card

The base type of Ticket and BacklogItem. It marks `title` and `last_activity` as data; each subtype overrides them, and its data is read through its own override.

+ Card(board: Board)
------
+ << association >> board: Board
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
+ title: str
	// its session's title, or its name when it has none
	-> Session.title
+ << association >> session: Session
	// data field: its folders, its practices and their files, and its log
+ << composition >> progress: list[FidelityProgress]
	// data field: one per fidelity the board requires, in stage order, read from the session log each time; a judgment in the fidelity's latest report that fails a rule fails a validate the log shows passing
	-> SessionLog.entries
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
	// reference data field `next`: the first fidelity not done in its stage or any stage before it, earliest stage first, because later work builds on it; sent by its ticket and slug, since `progress` sends it; none once it is done in its stage
+ worktree: str
	// data field: the folder of its own worktree, where its chat works; empty while it has none
	-> Ticket.branch
	-> Board.worktrees
+ last_activity: str
	// the timestamp of its log's latest line
	-> SessionLog.entries
----
+ load(ticket: str, project: Path): Ticket
	// the `@tool_subject` of the `ticket.*` tools; raises `TicketNotFoundError` for a ticket the board does not show
	-> Board.load
	-> Board.ticket
+ create(title: str, scope: str, parent: str, path: str, project: Path): Ticket
	// `ticket.create`: a new ticket in Discovery, in progress; it does not become the current session. scope is feature, story, or slice; parent names the ticket it was split from; path is its workpath
	-> Board.load
	-> Board.open_ticket
+ branch(): Branch
	// `ticket.branch`: its own branch, named as the ticket, with whether the repository has it and whether it is checked out, so activating a ticket offers only what is missing and leaving one commits, pushes, and merges only its own branch
	-> Repo.branch_named
+ work_branch(): Branch
	// `ticket.work_branch`: the branch its work is on, which leaving commits and pushes: its own branch while it is checked out, else the default branch while the checkout is on it, as for a session with no branch of its own; any other checkout gives its own branch, not checked out
	-> Ticket.branch
	-> Repo.branch_named
+ progress_of(slug: str): FidelityProgress
	// raises `FidelityNotFoundError` for a fidelity the ticket does not have
+ activate(leaving: list[str], opening: list[str]): Ticket
	// `ticket.activate`: the active ticket leaves its work as leaving says (handoff, commit, push, merge), this ticket opens what opening names (branch, worktree), and its session becomes current
	-> Board.active
	-> Ticket.leave
	-> Repo.switch_branch
	-> Repo.switch_worktree
	-> Sessions.switch
+ open_worktree(): Ticket
	// `ticket.open_worktree`: opens its own worktree beside the repository, creating its branch when missing; the ticket comes back from a new board read, which lists the new worktree
	-> Ticket.branch
	-> Branch.open_in_worktree
	-> Board.load
+ leave(leaving: list[str])
	// writes a handoff for its session when leaving names handoff, then commits, pushes, and merges as leaving names, only while the branch its work is on is checked out; work on the default branch is committed and pushed there, never merged, and no worktree is removed
	-> Handoffs.write
	-> LeavingHandoff.document
	-> Ticket.work_branch
	-> Repo.push_commit
	-> Repo.close_branch
+ move_next(): Ticket
	// `ticket.move_next`: from In progress it writes `done <stage>`, from Done it writes `move <next stage>`, and out of Implementation it closes
	-> Stage.next_stage
	-> SessionLog.record
+ move_previous(): Ticket | BacklogItem
	// `ticket.move_previous`: from Done it writes `in-progress <stage>`, from In progress it writes `move <previous stage>` and `done <previous stage>`; out of Complete it reopens, and out of Discovery it returns to the Backlog
	-> Stage.previous_stage
	-> SessionLog.record
	-> Session.reopen
+ move_to(stage: str, done: bool): Ticket | BacklogItem
	// `ticket.move_to`: a person's drag into a stage's In progress or Done; into the Backlog from any column it returns to the Backlog with its whole folder; raises `NotAStageError` for any other column
	-> SessionLog.record
	-> Session.close
	-> Session.move_to_backlog
	-> BacklogItem.from_ticket
	-> BacklogItem.write_if_missing
+ close(leaving: list[str]): Ticket
	// `ticket.close`: its session closes and its folder moves to `_complete/`
	-> Ticket.leave
	-> Session.close
	-> Session.move_to_closed
+ archive(): Ticket
	// `ticket.archive`: its session closes and its folder moves to `_archive/`, off the board
	-> Session.close
	-> Session.move_to_archive
+ violations(): Report
	// `ticket.violations`: the rules broken on every fidelity of its stage left with violations, each naming its fidelity, a rule two fidelities share listed once; its path is the session's reports folder from the project
	-> FidelityProgress.report
	-> Session.reports_folder
	-> Session.from_project
	-> Report.from_reports

## FidelityProgress

How far one fidelity has got through its stage's actions on one ticket, read from session log lines. Marked `@identity("ticket", "slug")`: the ticket's name and the fidelity's slug are what its loader takes, so they are sent as strings until a language adapter can send an identity made of references.

+ FidelityProgress(fidelity: FidelityGuidance, stage: Stage, done_actions: list[str], has_violations: bool, ticket: Ticket)
------
+ ticket: str
	// data field, part of its identity: the name of the ticket it is on
+ fidelity_slug: str
	// data field `slug`, part of its identity
+ << association >> fidelity: FidelityGuidance
	// data field: the fidelity as the ticket's session holds it, one object per fidelity in a session, with its name, outputs, and default format
+ << association >> stage: Stage
	// reference data field: the stage that requires the fidelity
+ practice_key: str
	// data field `practice`: its practice's key, by which the board's practices and its ticket's session name the practice
+ is_enabled: bool
	// data field: the ticket's session works on its practice
+ next_action: str
	// data field: review while it has violations, else the first of its stage's actions not done
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
+ << composition >> latest_report: ReportFile
	// its latest report in its ticket's session that has its result, else its latest; none when it has none
	-> ReportFile.from_fidelity
----
+ from_log(fidelity: FidelityGuidance, stage: Stage, entries: list[LogEntry], ticket: Ticket): FidelityProgress
	// finds the fidelity by name, never by position
	-> LogEntry.names
	-> Stage.steps
+ load(ticket: str, fidelity: str, project: Path): FidelityProgress
	// the `@tool_subject` of the `fidelity-progress.*` tools
	-> Ticket.load
	-> Ticket.progress_of
+ finish_review(): FidelityProgress
	// `fidelity-progress.finish_review`: a person's approval, one `review <practice key> <fidelity>` line in its ticket's session log, as action lines name the practice; answers its progress read again from the log
	-> SessionLog.record
	-> FidelityProgress.from_log
+ report(): Report
	// `fidelity-progress.report`: its latest report, with the rules broken on the nodes of the graph saved beside it, then each rule the judgment fails
	-> ReportFile.report
+ files(): dict[str, list[FileEntry]]
	// `fidelity-progress.files`: the files the fidelity declares by format in its ticket's session
	-> FidelityGuidance.files
+ help(): Help
	// `fidelity-progress.help`: the help of its fidelity, with its stage, made from what the progress holds
+ with_violations(): FidelityProgress
	// the same progress with its latest validate failed, for a judgment that fails a rule

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
+ path: Path
	// its markdown file
+ path_from_project: str
	// data field `path`
	-> Repo.path_from_top
+ last_activity: str
	// when its file last changed
----
+ load(backlog_item: str, project: Path): BacklogItem
	// the `@tool_subject` of the `backlog-item.*` tools; raises `BacklogItemNotFoundError` for an item the board does not show
	-> Board.load
	-> Board.backlog_item
+ create(title: str, text: str, project: Path): BacklogItem
	// `backlog-item.create`: writes one markdown file to `_backlog/`, the title as its heading and the text under it
	-> Sessions.backlog_folder
+ from_ticket(ticket: Ticket): BacklogItem
	// the item a ticket moved into the Backlog waits in: `_backlog/<name>/<name>.md`, inside the ticket's kept folder on the ticket's board
+ write_if_missing(title: str)
	// gives an item whose ticket never had an idea file one holding title, so it shows in the Backlog
+ start(scope: str, path: str): Ticket
	// `backlog-item.start`: an item a ticket was moved into returns that ticket with its folder; a new item's file moves into the new session folder
	-> Sessions.load
	-> Session.reopen
	-> Board.open_ticket
	-> Session.keep_file
+ move_next(): Ticket
	// a person's move forward out of the Backlog: starting the item
	-> BacklogItem.start
+ move_previous(): BacklogItem
	// the Backlog is the first column, so the item stays where it is

## Help

What `board.help` answers for a practice and `fidelity-progress.help` for a fidelity: the guidance objects themselves, with the text help shows.

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
	// data field: its page on the forge as the catalog generator names it: the fidelity's own page, or its practice's page for a fidelity the catalog has no page for
	-> CatalogPractice.fidelities
	-> CatalogPractice.fidelity_href
	-> CatalogPractice.href
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

+ ReportRule(fidelity: FidelityGuidance, rule: Rule, violations: list[Violation])
------
+ << association >> fidelity: FidelityGuidance
	// data field: the fidelity whose report found the rule broken
+ << association >> rule: Rule
	// data field: the broken rule with its slug and body; a rule no fidelity describes has its slug alone
+ count: int
	// data field
+ << composition >> violations: list[Violation]
	// data field
+ identity: tuple
	// its rule's slug and its violations' practice, location, line, and message: a saved graph holds its whole practice's hits, so two fidelities of one practice report the same broken rule
----

## ReportFile

A validation report of one fidelity saved in a session folder, with the graph the validation checked saved beside it. It knows which of its practice's rules it answers for.

+ ReportFile(file: Path, fidelity: FidelityGuidance, session: Session, repo: Repo)
------
+ file: Path
+ stamp: str
	// the date the report's name ends with, in a form that sorts by time
+ text: str
+ has_result: bool
	// it has a saved graph or a judgment; validate saves a report before the agent judges it
+ is_judged_failing: bool
	-> Judgment.from_report
----
+ from_fidelity(fidelity: FidelityGuidance, session: Session, repo: Repo): ReportFile
	// the fidelity's latest report in the session that has its result, else its latest; none when it has none
	-> FidelityGuidance.reports
+ report(): Report
	// the rules broken on the nodes of the saved graph, then each rule the judgment fails that the graph did not hit; each violation is named from the project, with the lines around it
	// the rules it answers for: its practice's shared rules, its fidelity's own, and every earlier fidelity's but those an earlier fidelity's newer report answers for; each rule is the one its fidelity describes
	-> PracticeGuidance.rules
	-> FidelityGuidance.rules
	-> ReportFile.from_fidelity
	-> violations_from_graph_json_files
	-> violations_by_rule
	-> GraphPractices.named
	-> Judgment.from_report
	-> Violation.in_file
	-> Repo.path_from_top

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

The classes below belong to other modules and are modelled in those modules' own documents. Each heading names the class so links and diagrams can point at it; the line under it says where it lives and what the board calls on it.

## Repo

`space/repo/repo.py`. The board reads `root`, `is_clone`, `checkout_folder`, `primary_root()`, `worktrees` (the `Worktrees` of `space/repo/worktree.py`, each `Worktree` with its `path` and `branch`), `file_manager`, `path_from_top(path)`, and `branch_named(name)`; a ticket calls `switch_branch`, `switch_worktree`, `push_commit`, and `close_branch`.

## Branch

`space/repo/repo.py`. `name`, `exists`, and `is_checked_out` are data fields, which `ticket.branch` sends; `open_in_worktree()` opens a ticket's worktree.

## Sessions

`space/session/sessions.py`. The board calls `all()`, `named(name)`, `load(folder)`, `open_name`, `create(name, workpath, title, scope, parent)`, `switch(name)`, `folder`, and `backlog_folder`; the board's own `_board.json` sits in its `folder`.

## Session

`space/session/session.py`, sent whole as a ticket's `session` data field. The board reads `name`, `title`, `is_closed`, `workpath`, `practices`, `reports_folder`, and `log`, and calls `close()`, `reopen()`, `move_to_closed()`, `move_to_archive()`, `move_to_backlog()`, `keep_file(file)`, and `from_project(path)`. Its `log` is a `SessionLog` (`space/session/session_log.py`), whose `entries` are `LogEntry`s with `time`, `verb`, `stage`, `words`, and `names(fidelity)`, and whose `record(line)` writes a move or a review.

## PracticeGuidance

`harness/guidance/guidance.py`, chosen through `PracticeCatalogue.practices()` (`harness/guidance/practice_catalogue.py`). `key`, `slug`, `short_name`, `colour`, and its fidelities' slugs are data fields; the board reads `fidelities`, `rules`, `overview`, and `guidance`.

## FidelityGuidance

`harness/guidance/guidance.py`. `slug`, `name`, `outputs`, and `default_format` are data fields, which a stage's `work_required`, a progress's `fidelity`, and help send; the board reads `stage`, `practice_guidance`, `rules`, `files()`, `reports()`, and `has_declared_output()`. Each fidelity's stage is one `ApproachStage` of `STAGES` (`harness/guidance/stages.py`), with its `name`, `title`, `scope` (a `StageScope`), `steps`, `actions`, and `producing_actions`.

## Rule

`harness/guidance/rule.py`. `slug` and `body` are data fields, which help sends.

## Violation

`harness/graph/violation.py`: one place a rule is broken, the one shape for graph hits and judged findings. `rule`, `practice`, `location`, `line`, `message`, and `source` (the numbered `SourceLine`s around the line, once `in_file(location, file, lines_before, lines_after)` has read them) are data fields. A judged finding is `Violation(rule, message, location=..., line=...)`. A report reads a saved graph's hits through `violations_from_graph_json_files` and `violations_by_rule` (`cdd_guidance/actions/validate/graph_json_reader.py`), and the rules a scanner checks now through `GraphPractices.named(practice).checks(patterns)` (`harness/graph/graph_practice.py`).

`FileManager` and `FileEntry` (`tools/file_manager/file_manager.py`) list folders for `board.folders` and are the entries `fidelity-progress.files` sends.
