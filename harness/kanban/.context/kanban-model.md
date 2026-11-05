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

Build order: `Column` → `Stage` → `Backlog` → `Complete` → `Card` → `Ticket` → `FidelityProgress` → `BacklogItem` → `Board` → `Report` → `TicketFiles`

---

# harness/kanban

Purpose, seam, dependencies, and constraint: `.context/module-context.md`.

Sources: `board.py`, `ticket.py`, `backlog_item.py`, and for what is not built yet, the Board canvas at https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN (Version 72). A class or member whose note starts "Intended" is not in the code yet, and `kanban-model.drawio` leaves it out. An Intended member that takes over from a member the code has says so ("Intended, replaces `Ticket.report`"), and the code's member stays in this model and the diagram until the Intended one is built. Everything else mirrors the code, and the diagram draws exactly that. The modules after `harness/kanban` show only the members the board's work depends on.

A member noted *data field* is marked `@data_field`: MCP sends an object as exactly those members, each object they hold as its own data, and the language adapter types `{Class}Data` from them. A data field sent under another name says so (*data field `column`*), because the member of that name returns the object itself.

## Board

+ Board(repo: Repo, practices: list[PracticeGuidance])
------
+ << association >> repo: Repo
	// the repository the sessions folder sits in; its root is the one root the board knows
+ practices: list[PracticeGuidance]
+ << composition >> columns: list[Column]
	// data field; always Backlog, then one Stage for each stage name in `stages.py`, then Complete
+ << composition >> tickets: list[Ticket]
	// one per folder in `.sessions/` and `.sessions/_complete/`; `main` and the other folders whose names start with `_` are left out
	-> Session.all_in
+ << aggregation >> backlog_items: list[BacklogItem]
	// every markdown file in the repository's `.sessions/_backlog/`
+ cards: list[Card]
	// its tickets, then its backlog items
+ active: Ticket
	// the ticket of the session saved as open; none while the main session is, since main is not on the board
	-> Session.active_name
+ project: str
	// data field: the repository folder's name
+ active_name: str
	// data field `active`: the active ticket's name, or none
----
+ load(repo_root: Path): Board
	// the board of the repository at repo_root with every practice chosen; the practices are built once per process, because they do not change between tool calls
+ current(): Board
	// the `@tool_subject` of the `board.*` tools: the board of the project the request names. One cdd server answers every chat, so it reads the project from each request's `X-CDD-Project` header and runs the call inside `space.work_state.working_on(project)`, which is what `project_checkout()` returns for that call. Intended: the server passes that project to the tool subject as an argument, so the board takes it as an input instead of reading it from the call
	-> Board.load
+ show(): Board
	// `board.show`
+ set_wip_limit(stage: str, limit: int): Board
	// `board.set_wip_limit`: saved in `.sessions/_board.json`
+ wip_limit(stage: str): int
+ worktree_of(ticket: str): Path
	// the worktree that has ticket's branch checked out; none when it has none. The worktrees are listed once per board read, because the board is read after every call, and a project that is no git clone has none
	-> Repo.is_clone
	-> Repo.list_worktrees
	// 3 until a person sets it
+ folders(path: str): list[str]
	// `board.folders`: the folders inside one folder of the repository, as paths from the project, for a person choosing a workpath or a practice root; installed packages, caches, and hidden folders are left out
+ help(practice: str, fidelity: str): Help
	// `board.help`: the practice, fidelity, and stage, with the overview, guidance, rules, and forge page. Refuses a practice or fidelity it does not have with `PracticeNotFoundError` or `FidelityNotFoundError`
	-> Board.practice
+ practice(key: str): PracticeGuidance
	// the practice whose folder name is key, such as `clean_engineering`; raises `PracticeNotFoundError` for one the board does not have
	-> PracticeGuidance.key
+ ticket(name: str): Ticket
+ backlog_item(title: str): BacklogItem
+ column(name: str): Column
	// raises `ColumnNotFoundError` for a column the board does not have

## Column

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
+ work_required: list[FidelityGuidance]
	// every fidelity of every chosen practice whose stage is this stage. It stays while each tile reads its formats from the stage; once Intended `Session.work_required` is built, each ticket gives its own fidelities' formats and this list goes, so one list says what is required
	-> Board.practices
+ next_stage: Stage
	// none after Implementation
+ previous_stage: Stage
	// none before Discovery
+ in_progress: list[Ticket]
	// data field
+ done: list[Ticket]
	// data field
	// tickets in this stage that are done; they wait here until a person moves them
	-> Ticket.is_done
+ wip_limit: int
	// data field
+ work_required_slugs: list[str]
	// data field `work_required`: each required fidelity as `<practice>-<fidelity>`
+ formats: dict[str, list[str]]
	// data field: the formats each required fidelity offers
+ default_formats: dict[str, str]
	// data field: the format a tile opens with for each required fidelity
+ is_over_limit: bool
	// data field: it holds more tickets than its WIP limit
----

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

+ Ticket(session: Session, board: Board)
	// never moves to another column by itself
------
+ << association >> session: Session
	// held by the ticket alone: callers ask the ticket, and the ticket asks its session
+ name: str
	// data field
	// its session's name; a ticket is an agent toolset, whose own name is the toolset's, so without this it would answer "ticket"
	-> Session.name
+ title: str
	-> Session.title
+ scope: str
	// data field
	-> Session.scope
+ << association >> parent: Ticket
	// the ticket this one was split from
	-> Session.parent
+ practices: dict[str, bool]
	// data field
	// whether this ticket works on each of the board's practices
	-> Session.active_practices
+ << composition >> progress: list[FidelityProgress]
	// one per fidelity the board requires, in stage order, read from the session log each time; a judgment in the fidelity's latest report that fails a rule fails a validate the log shows passing
	-> FidelityProgress.from_log
	-> ReportFile.is_judged_failing
+ parent_name: str
	// data field `parent`
+ column_name: str
	// data field `column`
+ next_slug: str
	// data field `next`: the next fidelity's slug, or none
+ fidelity_states: dict[str, str]
	// data field `progress`: each fidelity's state
+ fidelity_actions: dict[str, ActionStates]
	// data field `actions`
+ allowed_actions: dict[str, list[str]]
	// data field: generate always, validate and review once any action on the fidelity is recorded
+ column: Column
	// Complete once its session is closed; otherwise the stage named by its latest `move` line; before any move, the earliest stage its log shows work in, or Discovery
+ is_done: bool
	// data field
	// true only in a stage: when a person marked it done there, or, with no mark since entering, when all its enabled work there is done
+ next_fidelity: FidelityProgress
	// the first fidelity not done in its stage or any stage before it, earliest stage first, because later work builds on it; none once it is done in its stage
+ next_action: str
	// data field
	// generate, validate, or review on the next fidelity; satisfy while it has violations
+ last_activity: str
	// the timestamp of its log's latest line
+ latest_handoff: str
	// data field `handoff`
+ reports: dict[str, str]
	// data field
	-> FidelityProgress.reports_among
+ violation_counts: dict[str, int]
	// data field
+ workpath: str
	// data field
	// its session's workpath, as a path from the project; empty for the whole repository
	-> Session.workpath
+ worktree: str
	// data field
	// the folder of its own worktree, where its chat works; empty while it has none. The board picks the chat working in this folder, or a folder inside it, when a person clicks the ticket
	-> Board.worktree_of
+ practice_roots: dict[str, PracticeRoot]
	// data field
	// where each practice writes, as a path from the project, and whether a person chose it or it is the default
	-> Session.practice_root
	-> Session.has_chosen_practice_root
+ session_file: str
	// data field
	// its session's `session.json` as a path from the project; every command the board sends names it, because a command runs in whichever chat it is sent to
	-> Session.session_file
----
+ move_next(): Ticket
	// a person's move on, whatever its session's work: from In progress it writes `done <stage>`, from Done it writes `move <next stage>`, and out of Implementation it closes
	-> Ticket.close
+ move_previous(): Ticket | BacklogItem
	// a person's move back: from Done it writes `in-progress <stage>`, from In progress it writes `move <previous stage>` and `done <previous stage>`; out of Complete it reopens, and out of Discovery it returns to the Backlog
	-> Stage.previous_stage
	-> Ticket.reopen
	-> Ticket.return_to_backlog
+ move_to(stage: str, done: bool): Ticket | BacklogItem
	// a person's drag into a stage's In progress or Done, written as `move <stage>` and the mark; into the Backlog from any column it returns to the Backlog
	-> Ticket.return_to_backlog
+ reopen(): Ticket
	// out of Complete into Implementation's Done: its session reopens
	-> Session.reopen
+ return_to_backlog(): BacklogItem
	// its session closes and its whole folder becomes a backlog item under `_backlog/`, so starting the item brings the ticket back with its work; it stops being the active ticket
	-> Session.close
	-> Session.move_to_backlog
	-> BacklogItem.from_ticket
	-> BacklogItem.write_if_missing
+ finish_review(fidelities: list[str]): Ticket
	// `ticket.finish_review`: a person's approval, one `review <Practice> <fidelity>` line each; it counts once that fidelity's latest Validate has passed. Raises `FidelityNotFoundError` for a fidelity the ticket does not have, writing none
	-> Ticket.record
+ choose_workpath(path: str): Ticket
	// `ticket.choose_workpath`: the folder its session works in
	-> Session.choose_workpath
+ choose_practice_root(practice: str, path: str): Ticket
	// `ticket.choose_practice_root`: where that practice writes for this ticket
	-> Session.choose_practice_root
+ use_default_practice_root(practice: str): Ticket
	// `ticket.use_default_practice_root`
	-> Session.use_default_practice_root
+ close(leaving: list[str]): Ticket
	// after closing, its session is closed, its folder is in `_complete/`, and its column is Complete. leaving names commit, push, merge
	-> Ticket.leave
	-> Session.close
	-> Session.move_to_closed
+ archive(): Ticket
	// after archiving, its session is closed and its folder is in `_archive/`, off the board
	-> Session.close
	-> Session.move_to_archive
+ load(ticket: str): Ticket
	// the `@tool_subject` of the `ticket.*` tools: finds the ticket a tool call names; ticket holds that ticket's name
+ create(title: str, scope: str, parent: str, path: str): Ticket
	// `ticket.create`: a new ticket is in Discovery, in progress, until its log shows work in a later stage. Does not become the current session
	-> Session.new
+ activate(leaving: list[str], opening: list[str]): Ticket
	// `ticket.activate`: the active ticket leaves its work as leaving says, this ticket opens what opening names, and its session becomes current
	-> Ticket.leave
	-> Ticket.open_workspace
	-> Session.switch
+ leave(leaving: list[str])
	// commits, pushes, and merges as leaving names, only when the ticket's own branch is checked out
	-> Repo.push_commit
	-> Repo.close_branch
+ open_workspace(opening: list[str])
	// opens the ticket's branch and its worktree, as opening names
	-> Repo.switch_branch
	-> Repo.switch_worktree
+ open_worktree(): Ticket
	// `ticket.open_worktree`: opens its own worktree beside the repository, creating its branch when missing, and leaves the open session as it is; the ticket comes back from a new board read, which lists the new worktree
	-> Branch.open_in_worktree
+ workspace(): Workspace
	// `ticket.workspace`: whether it has its branch and worktree, and whether the ticket being left is on its branch
	-> Repo.has_branch
	-> Repo.worktree_for
+ violations(): Report
	// `ticket.violations`: the rules of every fidelity with violations, each naming its fidelity, a rule the practice's fidelities share listed once
	-> Ticket.report
	-> Report.from_reports
+ enable_practice(practice: str, is_enabled: bool): Ticket
	// `ticket.enable_practice`: raises `PracticeNotFoundError` for a practice the board does not have
	-> Session.enable_practice
+ files(fidelities: list[str]): dict[str, dict[str, list[FileEntry]]]
	// `ticket.files`: the declared files by format of the fidelities asked for, with whether each exists. A named part of a path, such as `{module}`, matches folders at any depth, `.context` folders included. A pattern in the whole repository lists only what the ticket's branch changed. Intended: `Session.files` takes this over and the tool asks the ticket's session
	-> TicketFiles.declared_by
+ session_files(): list[FileEntry]
	// `ticket.session_files`: every file in its session folder: the log, handoffs, kept notes, and validation reports
	-> TicketFiles.in_session_folder
+ read_file(path: str): FileText
	// `ticket.read_file`: no text for a file that is gone, such as one deleted since the board listed it; raises `PathOutsideRootsError` for a path outside the repository. Intended: `Session.read_file` takes this over
	-> TicketFiles.read
+ report(fidelity: str): Report
	// `ticket.report`: the latest report, with the rules broken on the nodes of the graph saved beside it, then each rule its judgment fails. A report with no saved graph lists no graph rules and says so; a fidelity with no report has an empty one. Intended: `Session.report` takes this over, so the ticket only asks its session
	-> ReportFile.report
+ generate_commands(fidelities: list[str], formats: list[str]): list[str]
	// `ticket.generate_commands`: renders the earlier fidelity first when a format is new to it; raises `FidelityNotFoundError` for a fidelity the ticket does not have. Intended: `Generate.commands_for` takes this over
+ keep_file(file: Path): Path
	// keeps a file, such as a started backlog item's idea, with the ticket's work
	-> Session.keep_file
+ record(entry: str)
	// appends a timestamped line to the session log

## FidelityProgress

How far one fidelity has got through its stage's actions on one ticket, read from session log lines. Intended: `Session.action_states` and `Session.violations` take this over, reading the log once through `Activity`, and the ticket asks its session; until then the ticket builds one of these for each fidelity with `from_log`.

+ FidelityProgress(fidelity: FidelityGuidance, stage: Stage, done_actions: list[str], has_violations: bool)
------
+ << association >> fidelity: FidelityGuidance
+ stage: Stage
+ practice: str
	-> PracticeGuidance.key
+ done_actions: list[str]
+ remaining_actions: list[str]
+ has_violations: bool
+ is_done: bool
+ slug: str
+ rule_descriptions: dict[str, str]
	// each rule's text by slug, this fidelity's own winning over the practice's
+ state: str
	// done, violations, in_progress, or not_started: what the board app dims and colours
+ action_states: ActionStates
	// each action as to_do, in_progress, or done
----
+ from_log(fidelity: FidelityGuidance, stage: Stage, lines: list[str]): FidelityProgress
	// finds the fidelity by name, never by position
+ reports_among(reports: list[Path]): list[Path]
	// this fidelity's dated validation reports among the session's, in the order given
+ with_violations(): FidelityProgress
	// the same progress with its latest validate failed, for a judgment that fails a rule

## Judgment

One rule the judgment in a validation report fails, in one judged file, with its findings in the shape the board shows any violation. It lives in `report.py`.

------
+ file: str
+ rule: str
+ findings: list[Violation]
	// each finding at the file and line it names, when it names them
----
+ from_report(text: str): list[Judgment]
	// the rules a report's judgment fails, read from the `## Judgment` sections validate.md asks for; none when the report has none

## BacklogItem : Card

+ BacklogItem(path: Path, board: Board)
------
+ title: str
	// the item's first `# ` heading, or its file name in words
+ column: Column
	// always the Backlog
+ text: str
	// data field; the file's content after its heading, which the details show
+ path: Path
+ path_from_project: str
	// data field `path`
+ last_activity: str
	// when its file last changed
----
+ load(backlog_item: str): BacklogItem
	// the `@tool_subject` of the `backlog-item.*` tools
+ create(title: str, text: str): BacklogItem
	// `backlog-item.create`: writes one markdown file to `_backlog/`, the title as its heading and the text under it
+ from_ticket(ticket: Ticket, board: Board): BacklogItem
	// the item a ticket moved into the Backlog waits in: `_backlog/<name>/<name>.md`, inside the ticket's kept folder
+ write_if_missing(title: str)
	// gives an item whose ticket never had an idea file one holding its title, so it shows in the Backlog
+ start(scope: str, path: str): Ticket
	// `backlog-item.start`: path is the workpath of the new ticket's session. An item a ticket was moved into returns that ticket with its folder, log, and progress; a new item's file moves into the new session folder
	-> Ticket.create
	-> Ticket.keep_file
+ move_next(): Ticket
	// a person's move forward: starts the item
+ move_previous(): BacklogItem
	// the Backlog is the first column, so the item stays

## PracticeRoot

Where one practice writes for a ticket: a value the ticket reports, not stored on its own.

------
+ root: str
	// data field; a path from the project
+ is_chosen: bool
	// data field; a person chose it, otherwise it is the session's workpath plus the practice's default folder
----

## ActionStates

Where each of a stage's actions stands on one fidelity: a value the ticket reports, not stored on its own.

------
+ generate: str
	// data field; to_do, in_progress, or done
+ validate: str
	// data field
+ review: str
	// data field
----

## Workspace

Whether a ticket has its branch and its worktree, and whether the active ticket being left is on a branch of its own: what activating a ticket offers.

------
+ has_branch: bool
	// data field
+ has_worktree: bool
	// data field
+ leaving_has_branch: bool
	// data field
----

## Help

The overview, guidance, and rules of a practice or one of its fidelities, with its stage and its page on the forge.

+ Help(practice: str, fidelity: str, stage: str, subject: PracticeGuidance | FidelityGuidance, href: str)
------
+ practice: str
	// data field
+ fidelity: str
	// data field; empty for a practice's help
+ stage: str
	// data field
+ overview: str
	// data field
+ guidance: str
	// data field
+ << composition >> rules: list[HelpRule]
	// data field
+ href: str
	// data field
----

## HelpRule

One rule as help shows it.

+ HelpRule(rule: Rule)
------
+ slug: str
	// data field
+ text: str
	// data field
----

## Report

The rules a fidelity's latest validation found broken, built from the saved report and the graph saved beside it. A fidelity with no report has an empty one. It lives in `report.py`.

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
	// graph hits and judged findings together
----
+ from_reports(folder: str, reports: list[Report]): Report
	// every rule broken in reports, each listed once though two fidelities share it, the latest first
	-> ReportRule.identity

## ReportRule

One rule a report finds broken, in the one shape the board reads for graph hits and judged findings alike.

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
+ identity: tuple
	// a saved graph holds its whole practice's hits, so two fidelities of one practice report the same broken rule
----

## Violation

One place a report says a rule is broken.

+ Violation(location: str, line: int, message: str, source: list[SourceLine])
------
+ location: str
	// data field: the file, as a path from the project
+ line: int
	// data field; none when the finding names no line
+ message: str
	// data field
+ << composition >> source: list[SourceLine]
	// data field: the numbered lines around the line
----
+ at(location: str, source: list[SourceLine]): Violation
	// this violation in location, with the lines around it read from there

## SourceLine

One numbered line of the file a violation names.

------
+ number: int
	// data field
+ text: str
	// data field
----

## ReportFile

A validation report saved in a session folder, with the graph the validation checked saved beside it.

+ ReportFile(file: Path, repo: Repo, workpath: Path)
------
+ text: str
+ has_result: bool
	// it has a saved graph or a judgment; validate saves a report before the agent judges it
+ is_judged_failing: bool
	-> Judgment.from_report
----
+ report(progress: FidelityProgress, superseded: list[FidelityGuidance]): Report
	// the rules broken on the nodes of the saved graph, then each rule the judgment fails that the graph did not hit
	-> FidelityProgress.rule_slugs_without
	-> Judgment.from_report
	-> Repo.path_from_top

## TicketFiles

The files of one ticket's session. It lives in `ticket_files.py`.

+ TicketFiles(session: Session, repo: Repo, branch: str)
------
----
+ declared_by(fidelity: FidelityGuidance): dict[str, list[FileEntry]]
	// the files fidelity declares, by format. A named part of a path, such as `{module}`, matches folders at any depth, `.context` folders included; a pattern in the whole repository lists only what the ticket's branch changed
	-> Session.fidelity_outputs
	-> Repo.files_changed_on
+ in_session_folder(): list[FileEntry]
+ read(path: str): FileText
	// through a `FileManager` whose one root is the repository
	-> FileManager.read

## FileEntry

One file a ticket lists, and whether it is there yet.

------
+ path: str
	// data field: a path from the project
+ exists: bool
	// data field
----

## ColumnNotFoundError : LookupError

A caller named a column the board does not have.

------
+ column: str
----

## PracticeNotFoundError : LookupError

A caller named a practice, such as `clean_engineering`, that the board does not have.

------
+ practice: str
+ within: str
	// what was searched: the board or a ticket
----

## FidelityNotFoundError : LookupError

A caller named a fidelity, such as `stories-story_map`, that a ticket or a practice does not have.

------
+ fidelity: str
+ within: str
	// the ticket or practice searched, so a caller can say which request was refused
----

## FileOutsideRepositoryError : ValueError

A tool asked a ticket for a file outside its repository.

------
+ path: str
+ ticket: str
----

# space/repo

The repository the board shows. Only the members the board's work depends on are shown.

## Repo

+ Repo(root: Path)
------
+ root: Path
+ is_clone: bool
	// whether git works here: a `.git` folder holding a HEAD, or a linked worktree's `.git` file. An empty `.git` folder only marks a project's root
+ << composition >> sessions: list[Session]
	// Intended, replaces `Session.all_in`: every session in `.sessions/` and `.sessions/_complete/`. The main session is not listed, and folders whose names start with `_`, other than `_complete`, are not sessions
+ current_session: Session
	// Intended: the session saved in `.sessions/session.json`, else the main session
----
+ has_branch(name: str): bool
+ path_from_top(path: Path): str
	// path as written from the repository's top, empty for the top itself, or as it is when it lies outside the repository, where a session may work
+ files_changed_on(branch: str): list[str]
	// what the branch changed since it left the default branch, with uncommitted changes when it is checked out
+ worktree_for(branch: str): Worktree
+ list_worktrees(): list[Worktree]
+ switch_branch(name: str): str
	// commits and pushes the branch being left, and leaves the default branch committed but not pushed
+ switch_worktree(name: str): str
	// opens the sibling worktree, and saves it as `worktree` in `.sessions/session.json`
+ push_commit(message: str, sync_remote: bool): Commit
+ close_branch(name: str): str
	// merges into the default branch, pushes it, and deletes the branch locally and on origin

# tools/file_manager

Lists and reads files under a set of roots. A ticket reads the repository's files through one whose only root is the repository. Only the members the board's work depends on are shown.

## FileManager

+ FileManager(workpath: Path, roots: tuple[Path])
------
+ workpath: Path
	// data field
+ roots: tuple[Path]
	// data field
----
+ read(path: str): FileText
	// no text for a file that is not there; raises `PathOutsideRootsError` for a path outside every root

## FileText

The text of one file, with its path from the workpath.

------
+ path: str
	// data field; a source file a view opens
+ text: str
	// data field
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
+ session_file: Path
	// its `session.json`, which holds its title, scope, parent, workpath, practice roots, and practices; callers ask for a named value, so the file's layout stays the session's own
+ title: str
+ scope: str
	// feature, story, or slice
+ parent: str
	// the name of the session this one was split from
+ << composition >> practices: dict[str, PracticeSessionOutput]
	// every practice CDD has, by practice key, opened or not
+ active_practices: list[PracticeSessionOutput]
	// the practices whose enabled is true; a new session has all of them
	-> PracticeSessionOutput.enabled
+ opened_practices: list[PracticeSessionOutput]
	// the practices this session has asked for, which its log lines name
+ work_required: list[FidelityGuidance]
	// Intended, replaces `Stage.work_required`: every fidelity of its active practices, in stage order
	-> Session.active_practices
	-> PracticeGuidance.fidelities
+ << composition >> activities: list[Activity]
	// Intended: one for each line of `session.log`, oldest first, read each time
+ latest_handoff: Path
	// Intended, replaces `Ticket.latest_handoff`: the newest `handoff-*.md`; none when it has none
+ next_action: GuidanceAction
	// Intended, replaces `Ticket.next_action`: the first action not done on the first fidelity not done; satisfy while that fidelity has violations, so Run next never validates again over open violations
+ is_closed: bool
+ main_session: str
+ default_wip: int
----
+ practice(name: str): PracticeSessionOutput
+ action_states(fidelity: FidelityGuidance): dict[GuidanceAction, ActionState]
	// Intended, replaces `FidelityProgress.action_states`: one state for each of Generate, Validate, and Review, in order, read from its activities on this fidelity
	-> Activity.action
+ is_stage_done(stage: StageName): bool
	// Intended: every required fidelity of that stage has every action done
	-> Session.action_states
+ violations(fidelity: FidelityGuidance): list[str]
	// Intended, replaces `FidelityProgress.has_violations`: the violations of its latest Validate on this fidelity
	-> Activity.violations
+ reports(fidelity: FidelityGuidance): list[Path]
	// Intended, replaces `Ticket.reports`: this fidelity's dated files in `validation-reports/`, newest last
+ report(fidelity: FidelityGuidance): dict
	// Intended, replaces `Ticket.report`: the latest report with the rules broken on the nodes of the graph saved beside it, then each rule its judgment fails; the `ticket.report` tool asks the ticket's session
	-> Session.reports
	-> Graph.saved_violations
	-> Judgment.from_report
+ files(fidelities: list[FidelityGuidance]): dict
	// Intended, replaces `Ticket.files`: the declared files by format of each fidelity, with whether each exists
	-> Session.fidelity_outputs
+ read_file(path: str): str
	// Intended, replaces `Ticket.read_file`: the text of a file in the repository, none for one that is gone; raises `FileOutsideRepositoryError` for a path outside it
+ artifacts(fidelity: FidelityGuidance): list[Path]
	// Intended: the files this fidelity produced, for the list, folder, and files on the card
	-> PracticeSessionOutput.artifacts
+ fidelity_outputs(guidance: PracticeGuidance, fidelity: FidelityGuidance): dict
	// where fidelity's artifacts are saved under the workpath, with the overrides in `session.json`; the practice's active fidelity when none is named. Naming it leaves the practice as it is, because the board's practices are shared by every call
	-> FidelityGuidance.outputs
+ active_name(repo_path: Path): str
	// the session saved as open on the repository; main when none is named. The one place that reads `session` from `.sessions/session.json`
+ choose_workpath(workpath: Path)
	// work in another folder of the repository from now on, saved in `session.json`; a chosen practice root keeps naming the same folder
+ choose_practice_root(practice: str, root: Path): Path
	// write that practice's files under root, saved in `session.json` relative to the workpath, and return the practice root now in use. Raises `PracticeRootInContextError` for a root inside a `.context` folder, because the practice's documents already go in its root's own `.context`
+ use_default_practice_root(practice: str)
	// write that practice's files under its default practice root again
+ has_chosen_practice_root(practice: str): bool
+ practice_root(guidance: PracticeGuidance, practice: str): Path
	// the practice root a person chose, else the workpath plus the practice's default folder from `.context/config.json` or the practice itself
+ enable_practice(practice: str, is_enabled: bool)
	// turn a practice on or off for this session, saved in `session.json`
	-> PracticeSessionOutput.enabled
+ keep_file(file: Path): Path
	// moves a file, such as a started backlog item's idea, into the session folder, where it stays with the session's work until it becomes lasting context
+ new(name: str, workpath: Path, repo_path: Path, is_current: bool, title: str, scope: str, parent: str): str
	// opens a session folder with its title, scope, and parent in `session.json`; is_current False leaves the current session as it is
+ load(session_path: Path, repo_path: Path): Session
	// the session kept in a folder, read without becoming current
+ move_folder_to(parent: Path): Session
	// moves the session's folder under parent, such as `.sessions/_complete/`
+ all_in(repo_path: Path): list[Session]
	// the repo's work sessions, open then closed: not main, and not the folders the sessions share. Goes when Intended `Repo.sessions` is built
+ backlog_folder(repo_path: Path): Path
+ board_file(repo_path: Path): Path
+ timestamp(moment: datetime): str
+ move_to_closed(): Session
	-> Session.move_folder_to
+ move_to_archive(): Session
	-> Session.move_folder_to
+ move_to_backlog(): Session
	-> Session.move_folder_to
+ reopen(): Session
	-> Session.move_folder_to
+ close()
	// ends the session; when it is the current one, the repository goes back to the main session
+ log_guidance_action(action: str, guidance_items: list)
+ log_validation(guidance: PracticeGuidance, violations: list[str])

## PracticeSessionOutput

+ PracticeSessionOutput(name: str, session: Session)
------
+ name: str
+ << association >> guideline: PracticeGuidance
	// loaded on first use, like graph, because the board reads enabled after every cdd call and needs neither
+ << composition >> graph: Graph
	// the knowledge graph of this practice's artifacts in the session
+ enabled: bool
	// whether the session works on this practice; setting it saves it in the `practices` field of `session.json`. True until set
----
+ artifacts(fidelity: FidelityGuidance): list[Path]
	// Intended: asks this practice's knowledge graph which files that fidelity's nodes came from
	-> Graph.files_of

## PracticeRootInContextError : ValueError

A practice root was chosen inside a `.context` folder, which would put the practice's code among its documents.

------
+ practice: str
+ root: Path
----

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
+ entered_stage: StageName
	// the stage a person moved the ticket into; none on an action line
----
+ from_log_line(line: str, session: Session): Activity
	// a log line starts with the action; the paths that follow are joined by ", " and can hold spaces; then come the practice and fidelity. Find the practice and fidelity by their names, never by position. The practice appears as its folder name (`clean_engineering`) in action lines and as its class name (`CleanEngineering`) in validate lines.
	-> Session.practice

# harness/guidance

The practices, their fidelities, and their rules: what a ticket has to get done.

## PracticeGuidance

------
+ key: str
	// the practice's folder name, such as `clean_engineering`: how session log action lines and `session.json` name the practice
+ << composition >> fidelities: list[FidelityGuidance]
+ << composition >> rules: RulesCollection
	// the rules shared by every fidelity of this practice
----

## FidelityGuidance

------
+ name: str
+ stage: str
	// which stage requires this fidelity, one of the names in `stages.py`, read from the fidelity's section in the practice markdown. Intended: a `StageName` in place of the string
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

Intended: an enum in place of the three string constants in `stages.py`, so a stage can only be one of these. The board already builds its stage columns from those constants rather than a list of its own.

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
	// the agent writes the fidelity's artifacts where its outputs say. A guidance string can carry its format (`stories-scenarios format=python`). Reads the rules without running Validate, so it logs only its own `generate` line
	-> Validate.rules_of
	-> Session.fidelity_outputs
+ commands_for(session: Session, fidelities: list[FidelityGuidance], formats: list[str]): list[str]
	// Intended, replaces `Ticket.generate_commands`: the commands that generate fidelities in formats, rendering the earlier fidelity first when a format is new to it
	-> Session.files

## Validate : GuidanceAction

------
----
+ validate(guidance: GuidanceArg, rule: Rule, graph: bool, paths: list[str]): str
	// builds the knowledge graph from the artifacts in paths, runs the fidelity's rules on it, saves the report in the session's `validation-reports/` with the graph it checked under the same name in `.json`, and logs one `graph-rule` entry per violation
	-> Graph.load_files
	-> Session.log_validation
+ rules_of(guidance: GuidanceArg): str
	// the shared and active fidelity's rules as text for another action to follow; checks nothing, saves no report, and writes nothing to the session log

# harness/graph

The knowledge graph: the artifacts read into nodes, with each practice's rules run on them.

## Graph

------
+ << composition >> practices: dict[str, PracticeGraph]
----
+ load_files(folder: str, practices: list[str], files: list[str], overlays: list[str]): str
	// builds each practice from only the given artifacts and runs its rules on them
	-> PracticeGraph.apply_rules
+ files_of(fidelity: str): list[str]
	// Intended: the source files of every node that fidelity creates
	-> Node.fidelity
	-> Node.source
+ write_json(path: str): str
	// the graph with every node's rule hits, saved beside the report Validate writes
+ saved_violations(path: Path, practice: str): dict[str, list[dict]]
	// Intended, replaces the Validate action's module functions `violations_from_graph_json_files` and `violations_by_rule`: each broken rule's hits in a graph `write_json` saved, by rule slug, so the graph that writes the file also reads it back

## PracticeGraph

------
+ name: str
+ << composition >> nodes: dict[str, list[Node]]
+ rules_run: list[str]
----
+ apply_rules(rule: str, tuples: list[Tuple])
	// records each rule's hits on the nodes they name
	-> Node.rules

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
	-> GraphRulesCollection.failed_slugs
+ << composition >> rules: GraphRulesCollection
	// the schema rules for this node, with the violations on each
----

## GraphRulesCollection : RulesCollection

The schema rules for one node. Violations live on each GraphRule.

+ GraphRulesCollection(node: Node, entries: dict[str, GraphRule])
------
+ node: Node
+ << composition >> entries: dict[str, GraphRule]
+ slugs: list[str]
+ violations: list[tuple[str, str]]
	// each violation on the node as its rule's slug and its message
	-> GraphRule.violations
+ failed_slugs: list[str]
+ passing_slugs: list[str]
+ graph_rules: list[GraphRule]
----
+ record_violation(slug: str, message: str)
	// keeps the violation at the node's source; a slug the node has no rule for records nothing, since the rule does not apply to it
	-> GraphRule.record
+ clear_violations()

## GraphRule : Rule

One schema rule on a node, the guidance Rule of the same slug with its executable check and its violations.

+ GraphRule(slug: str, body: str, node_types: tuple[str, ...], executable: bool)
------
+ slug: str
+ node_types: tuple[str, ...]
+ executable: bool
+ violations: list[str]
+ hits: list[dict]
	// each violation's message, file, start, and end
+ is_failing: bool
----
+ record(message: str, source: Source)
	// keeps message as a violation at source, the node's place in its file
+ clear_violations()

---

**Open**

- Starting a ticket's session (its folder and branch) stays with `space/session` and `space/repo`; the board reads what they write and does not call them.
- The path of a violation: `Validate.validate` -> `Graph.load_files` -> `PracticeGraph.apply_rules` -> `Node.rules`, on a `GraphRule`, saved by `Graph.write_json` beside the report, and read back for `Ticket.report` by the Validate action's reader until Intended `Graph.saved_violations` and `Session.report` take that over.
- `Validate` with an explicit graph file and paths filters its report to those paths; the saved graph holds the whole file, so `Ticket.report` lists every violation of the practice in it.
- Review is the ticket's own operation, `Ticket.finish_review`, not an action an agent runs: a person approves on the board, and the ticket writes the `review` line it later reads back like any other action line.
- A person's move to Done is written as `done <stage>` and back as `in-progress <stage>`. The latest mark since entering the stage wins; with no mark, `is_done` is derived from progress.
- Leaving a ticket commits, pushes, and merges only when the ticket has its branch and that branch is checked out, because those steps act on whatever is checked out. A ticket in its own worktree therefore has nothing committed by leaving it.
- `Stage.formats` and `Stage.default_formats` give each fidelity's formats and the one a tile opens with, which is how a tile knows which chip to open with.
- Locking is page state, not a board rule: with Active session only on, the board app turns off what sends commands to a chat for every ticket other than `Board.active`; moving a card stays on. The page reads `active` from the board's data and holds the switch itself.
- Ticket-wide Run sends one action across a ticket's enabled practices at its current stage. It is a command the board app sends to a chat, so it needs no operation here beyond `Ticket.practices`.
- `FidelityProgress` and `Stage.work_required` stay until Intended `Session.action_states`, `Session.violations`, and `Session.work_required` are built; then the ticket stops reading the log itself and one list says what is required.
- `Session.fidelity_outputs` reads the session it is called on, so `Repo.sessions` must give sessions that can be read without one becoming the current session. `Session` today has one in-memory current, and opening one saves it as current.
- The GitHub issue class in `space/repo` is `ProjectTicket`, with `ProjectTicketState` and `ProjectTicketNotFoundError`, so `Ticket` names only the board's card.
- Generate takes its format inside the guidance string (`format=python`) rather than as an argument of its own; a separate `format` argument is still to be decided.
- One word each: the folder a session works in is its workpath, on the ticket and the session alike, and the folder a practice writes under is its practice root. A card moves with `move_next`, `move_previous`, and `move_to`; a session's folder moves with `move_folder_to`. Every object a tool call names is found with `load`, except the board, found with `current` until the project reaches it as an argument.
- `Ticket` holds a card's moves, its review, and its lifecycle; its files, file reading, report, and generate commands are Intended to move to `Session.files`, `Session.read_file`, `Session.report`, and `Generate.commands_for`. The `ticket.*` tools keep their names because the board app and the chat pane send them, and each will ask the ticket's session.
- Left as they are, each for a reason another rule gives: `Ticket.create` and `Session.new` take every field a new ticket or session is made from, which `limit-operation-parameters` allows a creation factory. `Ticket.name` stays beside `Ticket.session`, because a ticket is an agent toolset whose own name would otherwise answer "ticket". `Ticket.load(ticket)` keeps its parameter name, because the tool layer makes it the argument every `ticket.*` call sends and renaming it changes every call the board app and chat pane make. `Board.current` reads the project from the call rather than taking it as an input, because a `@tool_subject` takes only the tool's own arguments; passing the project needs that change in `harness/agent_tools`.
