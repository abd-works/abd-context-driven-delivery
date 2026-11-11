## Language

*Board* shows a repository's delivery. A repository has sessions, each session is represented on the board as a ticket, and each ticket is in a column: Backlog, a stage (Discovery, Specification, or Implementation), or Complete. A caller reads it to see what is in flight and what to do next. It stores no ticket state: tickets read their sessions each time they are asked, so the board can never disagree with the work.

### board

- Its columns are always the same: Backlog, one stage for each stage name, then Complete. Practices play no part in them, because the session of each ticket says which practices that ticket works on.
- Has a reference to one repository, and shows one ticket for each of the repository's sessions.
- The main session is in use when no named session is open. It is a ticket like any other, placed in its stage's column and listed first, and every chat in the repository's own folder, which stays on the default branch, works on it; it never closes, archives, or goes to the Backlog. Sessions open only from main: activating a ticket opens it in its own worktree, where its own chat works on it. Closed sessions are finished tickets; archived sessions are off the board.

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
- Sits in the stage of its latest work, or Discovery when nothing is done yet. A generate or validate on a fidelity of any stage takes it into that stage, forward or back; a person's move puts it in a stage, which holds until the next generate or validate.
- Its work goes on in its own *worktree*, a checkout of its branch beside the repository, and its *chat* is the chat working in that worktree. Clicking a ticket on the board sends the board's commands to that chat, shown under the ticket's name; when no chat works there yet, the board opens a new chat in the Claude app on the worktree from a `claude://code/new` link, whose prompt asks it to take the ticket's name as its title, opening the worktree first if the ticket has none. The app asks the person to confirm the folder and send, because it starts no session on its own.
- **Invariant:** a ticket never moves to another column by itself. A person moves it, by dragging it or moving it on and back, whatever its session's work, and the move is written to its session log with the stage it enters.
- Its *text* says what its work is about: the idea file `<name>.md` its session folder keeps, the backlog item's file when it was started from one. Its *tags* are words a person tagged its session with, kept in its `session.json`.
- A *parent* ticket holds the *child* tickets whose session names it as their parent. A child is stacked inside its parent's card and shows in no column of its own until a person pulls it out; a *pulled-out* child is a card of its own, titled under its parent's title, and keeps its parent, which keeps a row for it. Giving a child another parent, or none, makes it no longer pulled out.
- **Invariant:** a parent is in the column of its child furthest back on the board, and moves only with its children: a person moving it is refused.
- A person keeps a card where they put it in its column: the order is kept in `.sessions/_board.json`, and a card not placed yet follows those that were.

### session

- Has the work that is done. It knows its past work by reading its own log, and it finds the files that work produced by asking the knowledge graph.
- Works in one folder of the repository, its *workpath*; the whole repository until a person chooses one. Each practice writes under its own folder, its *practice root*: the folder a person chose for that practice, or else the workpath plus the practice's default folder.
- Its *work required* is every fidelity of its active practices. A practice is active until a person turns it off for this session, so tickets can work on different practices on one board.
- Each fidelity goes through Generate, then Validate. Each action on a fidelity is to do, in progress, or done.
- A fidelity is done once Generate and Validate are done. Validate is done when its latest activity on that fidelity names no graph-rule violations and the judgment the validating agent added to its latest report fails no rule.
- *Next action* is what Run next does on a ticket: on the first fidelity not done in its stage or any stage before it, earliest stage first, the first of generate and validate not done. Violations hold a session on that fidelity, so the next action is validate again: Run next opens the report, a person reads the violations and tells the agent to fix them.

### activity

- One thing that happened in a session, read from one line of its log: when, which action on which fidelity and format, or which stage a person moved the ticket into. A move writes `move <stage>`.

### backlog item

- An idea not yet started: one markdown file per idea in `.sessions/_backlog/`, added by a person. The Backlog column shows them. Starting one asks for the workpath of its session, then opens a ticket for it.
- A ticket moved into the Backlog, from any column, keeps its whole folder there as `_backlog/<name>/<name>.md` beside its log and history, and that folder is a backlog item. Starting its item brings the ticket back with that work.

### the work behind a ticket

- *Practices* say what has to be produced. Each practice has *fidelities*, and each fidelity names the stage that requires it, the *artifacts* it produces, and the *rules* those artifacts must keep. An artifact is a file a fidelity's `outputs` declares, saved relative to the session's workpath, so it is a path rather than a class.
- *Actions* do the work on one fidelity inside a session. Generate writes the artifacts. Validate reads them into the *knowledge graph*, runs the rules on its nodes, and saves a report with the graph it checked beside it, so a report's violations stay on their nodes.
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

+ Board(repo: Repo, practices: BoardPractices)
------
+ << association >> repo: Repo
	// the repository the sessions folder sits in
+ sessions: Sessions
	// the sessions of its repository: each one a ticket, and which is open
+ file: Path
	// `.sessions/_board.json`, what the repository's sessions share on the board, such as each stage's WIP limit; the board is its one reader and writer, and reads it once per board read
	-> Sessions.folder
+ project: str
	// data field: the repository folder's name
+ << aggregation >> practices: list[PracticeGuidance]
	// data field: the practices every ticket works through, each with its key, slug, short name, and colour: the practice each held catalog view is of
+ << aggregation >> catalogued_practices: BoardPractices
	// the catalog's view of each practice, held for the checkout by `Sessions.board_practices` (`space/session/sessions.py`), so the process makes it and its one skill install once however many boards the calls make; it answers a practice by its class (`of`, `works_through`), which the board's own instance and a ticket's session's share, or by the key a tool names (`keyed`), and every `Help` is handed the one it answers; raises `PracticeNotFoundError` for a practice the board does not have
+ << composition >> stages: list[Stage]
	// its columns from Discovery to Implementation, made once with the board; `stage(name)` answers one and refuses any other column with `NotAStageError`, for `stage.*` tools and `ticket.move_to`
+ << composition >> fidelities: list[BoardFidelity]
	// data field: every fidelity of its practices with its practice, its label, and its skill's slash command, as the catalog names them, so a tile shows them and works out none; the board sends each fidelity once, here
	-> CatalogPractice.shown_fidelities
+ << composition >> columns: list[Column]
	// data field; always Backlog, then one Stage for each `ApproachStage` in `STAGES` (`harness/guidance/stages.py`), then Complete
+ << composition >> tickets: list[Ticket]
	// one per session of the repository, made once per board read and kept until `reread`
	-> Sessions.all
+ << aggregation >> backlog_items: list[BacklogItem]
	// every idea file in `.sessions/_backlog/`, and every ticket folder kept there, read once per board read and kept until `reread`
	-> Sessions.backlog_folder
+ cards: list[Card]
	// its tickets, then its backlog items
+ active: Ticket
	// reference data field: the ticket of the session saved as open, sent by its name, since its column sends it whole; main's ticket while the main session is
	-> Sessions.open_name
	-> Board.ticket
+ worktrees: dict[Branch, Worktree]
	// each branch's worktree, listed once per board read rather than once per ticket, because the board is read after every call; a project that is no git clone has none
	-> Repo.is_clone
	-> Repo.worktrees
----
+ load(project: Path): Board
	// the `@tool_subject` of the `board.*` tools, handed the call's project: the board of that project's main checkout with every practice chosen, so a chat in a ticket's worktree reads the same board
	-> Repo.of_project
	-> Repo.main_clone
	-> Sessions.board_practices
+ show(): Board
	// `board.show`
+ folders(path: str): list[str]
	// `board.folders`: the folders inside one folder of the repository, as paths from the project; installed packages, caches, and hidden folders other than `.context` are left out, so a person can choose a `.context` folder as a practice root
	-> Sessions.file_manager
	-> FileManager.list
+ help(practice: str): Help
	// `board.help`: the help of the board's practice named practice, such as `stories`; a fidelity's help comes from its progress, `fidelity-progress.help`
	-> BoardPractices.keyed
+ save_sessions_on_main(message: str)
	// commits the session folders not yet committed on main and pushes main, while the repository's own folder has main checked out: every ticket's record is kept on main, so each change to one is committed and pushed as it is made
	-> Repo.commit
	-> Repo.push_upstream
+ open_ticket(title: str, scope: str, parent: str, path: str): Ticket
	// a new ticket in Discovery, its session working on path, a folder in the repository; the session takes its name from the title
	-> Sessions.create
	-> Board.ticket_of
+ ticket_of(session: Session): Ticket
	// the ticket of a session just opened, moved between folders, closed, or reopened; the board forgets the cards it has read
	-> Board.reread
	-> Board.make_ticket
+ make_ticket(session: Session): Ticket
	// the ticket the board places for session, as it reads it now; the board is the one reader of the card classes the kanban package hands it, and its reads make their cards through it
+ make_backlog_item(path: Path): BacklogItem
	// the backlog item the board places for the idea kept in path
+ reread()
	// forgets the tickets, backlog items, and worktrees read so far, so the next read sees a change made since
+ wip_limit(stage: Stage): int
	// the limit saved for stage in `.sessions/_board.json`, else 3
+ set_wip_limit(stage: Stage, limit: int)
	// saved in `.sessions/_board.json` beside the other stages' limits, keeping whatever else the file holds
+ ticket(name: str): Ticket
	// read from that ticket's session folder alone, open before closed; none when no session has that name
	-> Sessions.named
+ ticket_called(name: str): Ticket
	// `ticket`, raising `TicketNotFoundError` when the board has none: where a ticket's name enters from a tool call
+ children_of(ticket: Ticket): list[Ticket]
	// the tickets whose session names ticket's as its parent, found once per board read
	-> Session.parent
+ backlog_item(title: str): BacklogItem
+ backlog_item_called(title: str): BacklogItem
	// `backlog_item`, raising `BacklogItemNotFoundError` when the board has none
+ order_in(column: Column): list[str]
	// the keys of column's cards in the order a person last placed them, kept in `.sessions/_board.json`
+ keep_order(column: Column, keys: list[str])
	// saved in `.sessions/_board.json` beside the WIP limits, keeping whatever else the file holds
+ column(name: str): Column
	// raises `ColumnNotFoundError` for a column the board does not have

## Column

Marked `@identity("name")`, so a reference to a column is its name.

+ Column(name: str, kind: str, board: Board)
------
+ name: str
	// data field
+ kind: str
	// data field: backlog, stage, or complete, so a reader of the board knows which fields the column sends
+ << aggregation >> cards: list[Card]
	// every card of its own on the board whose column is this one, in the order a person placed them, then any not placed yet; a child stacked in its parent's card is not one
	-> Board.cards
	-> Card.column
	-> Card.is_stacked
	-> Board.order_in
----
+ place_before(card: Card, other: Card): Column
	// keeps card just above other; raises `CardNotInColumnError` when either is not a card of its own here
	-> Board.keep_order

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
	// generate, then validate, named as the session log names them
	-> ApproachStage.steps
+ scope: StageScope
	// data field: how much of the solution the stage's work covers, which the board draws as its shape
	-> ApproachStage.scope
+ actions: list[str]
	// data field: every action a person can run on a fidelity in this stage, its steps first, then iterate, sketch, render, and document
	-> ApproachStage.actions
+ producing_actions: list[str]
	// data field: the actions that write a fidelity's files, every action but validate
	-> ApproachStage.producing_actions
+ << aggregation >> work_required: list[FidelityGuidance]
	// data field: every fidelity of every chosen practice whose stage is this stage, each with its slug, name, outputs by format, and default format
	-> Board.practices
+ next_stage: Stage
	// none after Implementation
+ previous_stage: Stage
	// none before Discovery
+ wip_limit: int
	// data field: the limit the board keeps for this stage
	-> Board.wip_limit
+ is_over_limit: bool
	// data field: it holds more tickets than its WIP limit
+ in_progress: list[Ticket]
	// data field
+ done: list[Ticket]
	// data field: tickets done in this stage, waiting here until a person moves them
	-> Ticket.is_done
----
+ requires(fidelity: FidelityGuidance): bool
	// its approach stage is this stage's, and its practice's class is one the board works through
	-> BoardPractices.works_through
+ load(stage: str, project: Path): Stage
	// the `@tool_subject` of the `stage.*` tools; refuses a column that is not a stage with `NotAStageError`
	-> Board.load
+ set_wip_limit(limit: int): Stage
	// `stage.set_wip_limit`: the board keeps it
	-> Board.set_wip_limit

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
+ key: str
	// what names it among its column's cards, by which the board keeps its place: a ticket's name, a backlog item's title
+ is_stacked: bool
	// whether it shows inside another card rather than as a card of its own; only a ticket's child does
----
+ move_next(): Card
	// a person's move to the next column
+ move_previous(): Card
	// a person's move to the previous column
+ move_before(other: Card): Card
	// a person's move of it just above other in their column; committed on main and pushed
	-> Column.place_before

## Ticket : Card

Marked `@identity("name")`. Never moves to another column by itself: a person moves it, and the move is written to its session log. It holds three parts, each made once with it: its *TicketWork* (its progress), its *TicketCheckout* (its branch and worktree), and its *StageMarks* (the moves and marks a person made). Its tools and data fields stay on it and hand the work to those parts, so their published names do not change (`cdr/0004`).

+ Ticket(session: Session, board: Board)
------
+ name: str
	// data field: its session's name; a ticket is an agent toolset, whose own name is the toolset's, so without this it would answer "ticket"
	-> Session.name
+ title: str
	// its session's title, or its name when it has none; a pulled-out child's is under its parent's, as Checkout flow.Enter card details
	-> Session.title
+ text: str
	// data field: the text of the idea file its session folder keeps
	-> Session.text
+ tags: list[str]
	// data field: the words a person tagged its session with
	-> Session.tags
+ << association >> parent: Ticket
	// the ticket its session names as its parent; none when it names none or one the board does not have
	-> Board.ticket
+ << association >> ancestors: list[Ticket]
	// its parent, its parent's parent, and so on
+ << aggregation >> children: list[Ticket]
	// data field, sent whole, since a stacked child shows in no column: the tickets whose session names it as their parent
	-> Board.children_of
+ is_pulled_out: bool
	// data field: a child moving on the board as a card of its own, still keeping its parent
	-> Session.is_pulled_out
+ is_stacked: bool
	// data field: an open child, not pulled out, of an open parent, shown inside the parent's card
+ << association >> session: Session
	// data field: its folders, its practices and their files, and its log
+ << composition >> progress: list[FidelityProgress]
	// data field: one per fidelity the board requires, in stage order, read from the session log once per ticket read and again after the ticket records a line; a judgment in the fidelity's latest report that fails a rule fails a validate the log shows passing
	-> TicketWork.progress
+ << composition >> work: TicketWork
+ << composition >> checkout: TicketCheckout
+ << composition >> marks: StageMarks
+ << association >> column: Column
	// reference data field: Complete once its session is closed; a parent's is the stage of its child furthest back; otherwise the stage of the fidelity its latest generate or validate names, unless a `move` line came after it, whose stage it then sits in; with neither, Discovery
+ is_closed: bool
	// data field: its session is closed, so it shows in Complete
+ is_active: bool
	// data field: its session is the one saved as open
+ is_open: bool
	// data field: open for work, in its own worktree or the active ticket, and not main; its card offers Close, which closes it through its Close dialog unless the chosen chat works on it
	-> TicketCheckout.worktree
+ drop_targets: list[str]
	// data field: the columns besides the stages it can be dropped on: the Backlog always, Complete from Implementation's Done or while it is open
+ is_done: bool
	// data field: true only in a stage: a parent's when every child of it in that stage is done; else when a person marked it done there or, with no mark since entering, when all its enabled work there is done
+ next_fidelity: FidelityProgress
	// reference data field `next`: the first fidelity not done in its stage or any stage before it, earliest stage first, because later work builds on it; sent by its ticket and slug, since `progress` sends it; none once it is done in its stage
+ worktree: str
	// data field: the folder of its own worktree, where its chat works; empty while it has none
	-> TicketCheckout.worktree
+ << association >> chat: Chat
	// reference data field `working_chat`, sent by its id: the connected chat working in its worktree or a folder inside it, else one whose mod names no folder and that is titled by the ticket's name; none while no chat works on it
	-> TicketCheckout.chat
+ << composition >> stage_work: list[StageWork]
	// data field: its work in each stage taken together, which a stage head's action bar shows and acts on
	-> TicketWork.in_stage
+ last_activity: str
	// the timestamp of its log's latest line
	-> SessionLog.entries
----
+ load(ticket: str, project: Path): Ticket
	// the `@tool_subject` of the `ticket.*` tools; raises `TicketNotFoundError` for a ticket the board does not show
	-> Board.load
	-> Board.ticket_called
+ create(title: str, scope: str, parent: str, path: str, project: Path): Ticket
	// `ticket.create`: a new ticket in Discovery, in progress; it does not become the current session. scope is feature, story, or slice; parent names the ticket it was split from; path is its workpath
	-> Board.load
	-> Board.open_ticket
	-> Board.save_sessions_on_main
+ branch(): Branch
	// `ticket.branch`: its own branch, named as the ticket, with whether the repository has it and whether it is checked out, so activating a ticket offers only what is missing and leaving one commits, pushes, and merges only its own branch
	-> TicketCheckout.branch
+ work_branch(): Branch
	// `ticket.work_branch`: the branch its work is on, which leaving commits and pushes: its own branch while it is checked out, else the default branch while the checkout is on it, as for a session with no branch of its own; any other checkout gives its own branch, not checked out
	-> TicketCheckout.work_branch
+ format_choices(fidelities: list[str]): list[FormatChoice]
	// `ticket.format_choices`: the chips of an action bar over those fidelities, each fidelity's files read once
	-> TicketWork.progress_of
	-> FidelityProgress.files
	-> FormatChoice.offered_by
+ activate(): Ticket
	// `ticket.activate`: opens it in its own worktree, where its own chat works on it; the chat that asks keeps its session, and the repository's own folder stays on main
	-> TicketCheckout.open
+ move_next(): Ticket
	// `ticket.move_next`: from In progress it writes `done <stage>`, from Done it writes `move <next stage>`, and out of Implementation it closes; a parent raises `ParentMovesWithChildrenError`, as `move_previous` and `move_to` do
	-> Stage.next_stage
	-> StageMarks.mark
	-> StageMarks.enter
+ move_previous(): Ticket | BacklogItem
	// `ticket.move_previous`: from Done it writes `in-progress <stage>`, from In progress it writes `move <previous stage>` and `done <previous stage>`; out of Complete it reopens, and out of Discovery it returns to the Backlog
	-> Stage.previous_stage
	-> StageMarks.place
	-> Session.reopen
+ move_to(stage: str, done: bool): Ticket | BacklogItem
	// `ticket.move_to`: a person's drag into a stage's In progress or Done; into the Backlog from any column it returns to the Backlog with its whole folder; raises `NotAStageError` for any other column
	-> StageMarks.place
	-> Session.close
	-> Session.move_to_backlog
	-> BacklogItem.from_ticket
	-> BacklogItem.write_if_missing
	-> Board.save_sessions_on_main
+ close(leaving: list[str]): Ticket
	// `ticket.close`: does with its work what leaving names (handoff, commit, push, merge, delete_branch, delete_worktree); its session closes, its folder moves to `_complete/`, and that move is committed on main and pushed
	-> TicketCheckout.free_worktree
	-> TicketCheckout.keep_landing_release
	-> Session.close
	-> Session.move_to_closed
	-> Board.save_sessions_on_main
+ assign_chat(chat: str): Ticket
	// `ticket.assign_chat`: keeps the chat's id in its session.json, committed on main and pushed
	-> TicketCheckout.assign_chat
+ archive(): Ticket
	// `ticket.archive`: its session closes and its folder moves to `_archive/`, off the board; the move is committed on main and pushed
	-> Session.close
	-> Session.move_to_archive
	-> Board.save_sessions_on_main
+ edit_text(text: str): Ticket
	// `ticket.edit_text`: writes text under its idea file's heading, making the file when it has none; committed on main and pushed
	-> Session.keep_text
+ tag(word: str): Ticket
	// `ticket.tag`: adds word to its session's tags; committed on main and pushed
	-> Session.add_tag
+ delete()
	// `ticket.delete`: its session closes and its folder is removed, that removal committed on main and pushed; main raises `MainStaysOpenError`
	-> Session.close
	-> Session.remove
	-> Board.save_sessions_on_main
+ add_child(title: str): Ticket
	// `ticket.add_child`: a new child ticket, a story In progress in Discovery, working where it works; committed on main and pushed
	-> Session.open_child
	-> Board.ticket_of
+ pull_out(): Ticket
	// `ticket.pull_out`: a child becomes a card of its own, keeping its parent; a ticket with no parent raises `NotAChildError`
	-> Session.mark_pulled_out
+ reassign_parent(parent: Ticket | None): Ticket
	// `ticket.reassign_parent`: parent, or none, becomes its parent, and it is no longer pulled out; raises `ParentLoopError` when parent is it or one of its children; the tool names parent as it names any ticket
	-> Session.set_parent
+ move_before(other: Ticket): Ticket
	// `ticket.move_before`: keeps it just above other in their column; the tool names other as it names any ticket
	-> Card.move_before
+ violations(): Report
	// `ticket.violations`: the rules broken on every fidelity of its stage left with violations, each naming its fidelity, a rule two fidelities share listed once; its path is the session's reports folder from the project
	-> FidelityProgress.report
	-> Session.reports_folder
	-> Session.from_project
	-> Report.from_reports

## TicketWork

A ticket's progress on each fidelity the board requires whose practice its session holds, in stage order, made once with the ticket.

+ TicketWork(ticket: Ticket)
------
+ << composition >> progress: list[FidelityProgress]
	// read from the session log once per ticket read and again after `record` writes a line
	-> SessionLog.entries
	-> Stage.requires
	-> FidelityProgress.from_log
+ enabled: list[FidelityProgress]
	// the progress of the fidelities whose practice its session works on
----
+ progress_of(slug: str): FidelityProgress
	// only that fidelity's progress is read; raises `FidelityNotFoundError` for a fidelity the ticket does not have
+ in_stage(stage: Stage): StageWork
	// the progress of every fidelity stage requires whose practice its session works on
+ command(action: str, fidelities: list[FidelityGuidance]): str
	// one command running action on fidelities, naming its session.json and no format; FidelityProgress.commands and StageWork.commands both ask it
+ record(line: str)
	// writes line to its session's log, a move, a mark, or a backlog line; its progress is read from the log again next time
	-> SessionLog.record

## TicketCheckout

`space/kanban/ticket_checkout.py`. Where one ticket's work sits in git, made once with the ticket and holding its own *Branch*, named as the ticket.

+ TicketCheckout(ticket: Ticket)
------
+ << composition >> branch: Branch
	// made once, found among the branches the board lists once per read: the recorded branch, else the one named as the ticket, else the one branch holding its name as a whole word; a Branch reads whether it is checked out from git each time
	-> Board.branches
	-> Repo.branch_named
+ work_branch: Branch
	// its own branch while it is checked out, else the default branch while the checkout is on it; any other checkout gives its own branch, not checked out
+ worktree: str
	// the folder of its own worktree; empty while it has none
	-> Board.worktrees
+ << association >> chat: Chat
	// the connected chat working in its worktree or a folder inside it, else one with no folder titled by the ticket's name
	-> Board.chats
+ close_choices: LeaveChoices
	// `ticket.close_choices`: a handoff, a commit and push of its work branch while a checkout has it, and a merge, branch delete, and worktree delete for its own branch; none chosen at first
+ open()
	// opens the ticket in its own worktree: the one it has, else a new one on its own branch, after the session folders not yet committed are committed on main and pushed; records the branch and worktree in its session, and commits that record on main and pushes it, every time; refuses with TicketBranchUnclearError when several branches could each be the ticket's
	-> Board.save_sessions_on_main
	-> Branch.open_in_worktree
	-> Board.reread
	-> Session.save_fields
+ assign_chat(chat: str)
	// keeps chat's id in the ticket's session.json, committed on main and pushed
	-> Session.save_fields
	-> Board.save_sessions_on_main
+ keep_landing_release(leaving: list[str])
	// a ticket closed with its branch merged keeps its end-to-end results only
	-> LatestRelease.keep

## StageMarks

The moves and marks a person made on one ticket's stages, made once with the ticket. Its session's log answers them (`SessionLog.latest`); a move or mark is written through the ticket's work.

+ StageMarks(ticket: Ticket)
------
+ moved_into: Stage
	// the stage named by its latest `move` line; none before a person has moved it
	-> SessionLog.latest
----
+ latest_in(stage: Stage): str
	// the latest `done` or `in-progress` mark in stage since its latest `move` into it; none when there is none
	-> SessionLog.latest
+ enter(stage: Stage): Ticket
	// writes `move <stage>`
	-> TicketWork.record
+ mark(mark: str, stage: Stage): Ticket
	// writes `done <stage>` or `in-progress <stage>` to session.json and the log, then commits on main and pushes
	-> TicketWork.record
	-> Board.save_sessions_on_main
+ place(stage: Stage, mark: str): Ticket
	// enters stage unless the ticket is there, then marks it there: one commit on main, pushed, for both

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
	// data field: the first of its stage's actions not done, which is validate again while it has violations
+ commands: dict[str, str]
	// data field: the command for each action of its stage on this fidelity, naming its ticket's session.json and no format
	-> TicketWork.command
+ allowed_actions: list[str]
	// data field: every action of its stage; validate and render only once an action is recorded or a declared file is there
+ state: str
	// data field: done, violations, in_progress, or not_started
+ action_states: ActionStates
	// data field `actions`
+ report_file: str
	// data field: its latest validation report, as a path from the project
+ violation_count: int
	// data field
+ has_violations: bool
	// data field: its latest validate left violations
+ done_actions: list[str]
+ remaining_actions: list[str]
+ is_done: bool
+ << composition >> latest_report: ReportFile
	// its latest report in its ticket's session that has its result, else its latest; none when it has none; found once per reading of the progress
	-> ReportFile.from_fidelity
----
+ from_log(fidelity: FidelityGuidance, stage: Stage, entries: list[LogEntry], ticket: Ticket): FidelityProgress
	// finds the fidelity by name, never by position
	-> LogEntry.names
	-> Stage.steps
+ load(ticket: str, fidelity: str, project: Path): FidelityProgress
	// the `@tool_subject` of the `fidelity-progress.*` tools
	-> Ticket.load
	-> TicketWork.progress_of
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
----
+ taken_together(every: list[ActionStates]): ActionStates
	// each action done only once it is done on all, in progress once it is under way on any, else to do

## StageWork

A ticket's work in one stage taken together: the progress of each fidelity the stage requires whose practice the ticket's session works on.

+ StageWork(ticket: Ticket, stage: Stage, progress: list[FidelityProgress])
------
+ << association >> stage: Stage
	// reference data field
+ << association >> progress: list[FidelityProgress]
+ action_states: ActionStates
	// data field `actions`
	-> ActionStates.taken_together
+ has_violations: bool
	// data field: any of its fidelities has violations
+ violation_count: int
	// data field: its fidelities' violations together
+ commands: dict[str, str]
	// data field: the command for each action of its stage, one command naming every one of its fidelities
	-> TicketWork.command
+ allowed_actions: list[str]
	// data field: the actions every one of its fidelities allows
----

## FormatChoice

`space/kanban/format_choice.py`. One chip of an action bar: a group of formats over the fidelities the bar acts on.

------
+ label: str
	// data field: the group, such as markdown, or a format in no group under its own name
+ formats: list[str]
	// data field: the format each fidelity uses from the group, its default when the group holds it, else the first it offers
+ offered: int
	// data field
+ made: int
	// data field: how many of the fidelities have a file in the group already
+ starts_picked: bool
	// data field: it holds a fidelity's default format and nothing is made in it
----
+ offered_by(read: list[tuple[FidelityGuidance, dict[str, list[FileEntry]]]]): list[FormatChoice]
	// a chip per group the fidelities offer, in the order of `Format.GROUPS`
	-> Format.group

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
	-> IdeaFile.text
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
	-> Board.backlog_item_called
+ create(title: str, text: str, project: Path): BacklogItem
	// `backlog-item.create`: writes one markdown file to `_backlog/`, the title as its heading and the text under it, committed on main and pushed
	-> Sessions.backlog_folder
	-> Board.save_sessions_on_main
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
	-> Board.save_sessions_on_main
+ move_next(): Ticket
	// a person's move forward out of the Backlog: starting the item
	-> BacklogItem.start
+ move_previous(): BacklogItem
	// the Backlog is the first column, so the item stays where it is
+ edit_text(text: str): BacklogItem
	// `backlog-item.edit_text`: rewrites the text under its file's heading, which keeps its title; committed on main and pushed
	-> IdeaFile.rewrite_text
+ move_before(other: BacklogItem): BacklogItem
	// `backlog-item.move_before`: keeps it just above other in the Backlog; the tool names other by its title
	-> Card.move_before

## Help

What `board.help` answers for a practice and `fidelity-progress.help` for a fidelity: the guidance objects themselves, with the text help shows.

+ Help(practice: PracticeGuidance, fidelity: FidelityGuidance, stage: Stage, catalogued: CatalogPractice)
------
+ << association >> catalogued: CatalogPractice
	// the catalog's view of the practice the board holds (`BoardPractices.of`), which names every page on the forge
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
	-> PracticeGuidance.fidelity_called
	-> CatalogPractice.fidelities
	-> CatalogPractice.fidelity_href
	-> CatalogPractice.href
----

## BoardFidelity

A fidelity as a board tile names it. The page shows its label and its skill's slash command and works out neither.

+ BoardFidelity(catalogued: CatalogPractice, shown: CatalogFidelity)
------
+ << association >> fidelity: FidelityGuidance
	// reference data field: the fidelity, sent by its slug
+ << association >> practice: PracticeGuidance
	// reference data field: the practice it belongs to, sent by its key, so a tile finds a fidelity's practice without a second list of each practice's fidelities
+ label: str
	// data field: its name on a tile, such as `story-map`, or `information-architecture` for UX's `ia`
	-> CatalogFidelity.label
+ skill: str
	// data field: the slash command of the skill the installer publishes for it, such as `/practices-stories-stories-story-map`
	-> CatalogPractice.skill_of
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
	// data field: graph hits and judged findings together, which the board app shows as they are sent
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

+ ReportFile(file: Path, fidelity: FidelityGuidance)
	// fidelity is the one its session holds: its practice's session names the folder the saved graph names files from, and that session's repository names the report's files from its top
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
+ from_fidelity(fidelity: FidelityGuidance): ReportFile
	// the fidelity's latest report in the session that has its result, else its latest; none when it has none
	-> FidelityGuidance.reports
+ report(): Report
	// the rules broken on the nodes of the saved graph, then each rule the judgment fails that the graph did not hit; each violation is named from the project, with the lines around it
	// the rules it answers for: its practice's shared rules, its fidelity's own, and every earlier fidelity's but those an earlier fidelity's newer report answers for; each rule is the one its fidelity describes
	-> PracticeGuidance.rules
	-> FidelityGuidance.rules
	-> ReportFile.from_fidelity
	-> SavedGraph.from_file
	-> SavedGraph.violations
	-> Violation.by_rule
	-> session.graph.applied_patterns.checks_of(practice, saved.overlays)
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

`space/session/sessions.py`, raised by `BoardPractices`.

## FidelityNotFoundError : LookupError

## TicketNotFoundError : LookupError

## BacklogItemNotFoundError : LookupError

## CardNotInColumnError : ValueError

## ParentMovesWithChildrenError : ValueError

## NotAChildError : ValueError

## ParentLoopError : ValueError

## MainStaysOpenError : ValueError

`ticket.py`, raised when a tool would close, archive, shelve, or delete main.

---

# Collaborators

The classes below belong to other modules and are modelled in those modules' own documents. Each heading names the class so links and diagrams can point at it; the line under it says where it lives and what the board calls on it.

## Repo

`space/repo/repo.py`. The board reads the main clone of the project's sessions' repository (`Sessions.of_project(project).repo.main_clone`), and from it `root`, `is_clone`, `worktrees` (the `Worktrees` of `space/repo/worktree.py`, each `Worktree` with its `path` and `branch`), `path_from_top(path)`, and `branch_named(name)`; a ticket calls `switch_branch`, `switch_worktree`, `push_commit`, and `close_branch`.

## Chat

`harness/chat/chat.py`. `Board.chats` lists the connected chats once per board read with `Chat.list`; a ticket reads each chat's `folder` and `name`.

## Branch

`space/repo/repo.py`. `name`, `exists`, and `is_checked_out` are data fields, which `ticket.branch` sends; `open_in_worktree()` opens a ticket's worktree.

## Sessions

`space/session/sessions.py`. The board calls `all()`, `named(name)`, `load(folder)`, `open_name`, `create(name, workpath, title, scope, parent)`, `switch(name)`, `folder`, and `backlog_folder`; the board's own `_board.json` sits in its `folder`.

## Session

`space/session/session.py`, sent whole as a ticket's `session` data field. The board reads `name`, `title`, `parent`, `is_pulled_out`, `tags`, `text`, `is_closed`, `workpath`, `practices`, `reports_folder`, and `log`, and calls `close()`, `remove()`, `reopen()`, `move_to_closed()`, `move_to_archive()`, `move_to_backlog()`, `keep_file(file)`, `keep_text(text)`, `add_tag(word)`, `set_parent(parent)`, `mark_pulled_out()`, `open_child(title, scope)`, and `from_project(path)`. A backlog item reads and writes its file through an `IdeaFile` (`space/session/idea_file.py`), the same as a session's idea file. Its `log` is a `SessionLog` (`space/session/session_log.py`), whose `entries` are `LogEntry`s with `time`, `verb`, `stage`, `words`, and `names(fidelity)`, and whose `record(line)` writes a move or a mark; `latest(*verbs, stage)` answers a ticket's latest move and its latest mark in a stage.

## IdeaFile

`space/session/idea_file.py`: one markdown file holding an idea, its `# ` heading and the text under it. A backlog item holds one for its file and reads its `text` and calls `rewrite_text(text)`; a session's `idea_file` is the `<name>.md` its folder keeps, from which it answers `text` and `keep_text(text)`.

## PracticeGuidance

`harness/guidance/guidance.py`, the board's own set, which the checkout's `Sessions` makes once with `PracticeCatalogue.create_all()` and holds as the catalog shows them (`board_practices`, `CatalogPractice.of_practices`). `key`, `slug`, `short_name`, and `colour` are data fields; the board reads `fidelities`, `rules`, `overview`, and `guidance`.

## FidelityGuidance

`harness/guidance/guidance.py`. `slug`, `name`, `outputs`, and `default_format` are data fields, which a stage's `work_required`, a progress's `fidelity`, and help send; the board reads `stage`, `practice_guidance`, `rules`, `files()`, `reports()`, and `has_declared_output()`. Each fidelity's stage is one `ApproachStage` of `STAGES` (`harness/guidance/stages.py`), with its `name`, `title`, `scope` (a `StageScope`), `steps`, `actions`, and `producing_actions`.

## Rule

`harness/guidance/rule.py`. `slug` and `body` are data fields, which help sends.

## Violation

`harness/graph/violation.py`: one place a rule is broken, the one shape for graph hits and judged findings. `rule`, `practice`, `location`, `line`, `message`, and `source` (the numbered `SourceLine`s around the line, once `in_file(location, file, lines_before, lines_after)` has read them) are data fields. A judged finding is `Violation(rule, message, location=..., line=...)`. A report reads the graph saved beside it through `SavedGraph.from_file` (`harness/graph/saved_graph.py`), the one reader of a saved graph document and of the node list `graph.return_nodes` answers with, groups its hits with `Violation.by_rule`, and reads the rules a scanner checks now from its session's graph, `graph.applied_patterns.checks_of(practice, saved.overlays)` (`harness/graph/pattern_overlays.py`), which asks the report's own practice with the overlays the graph was saved with, through the patterns the session's graph already holds.

`FileManager` and `FileEntry` (`space/session/file_manager.py`) list folders for `board.folders`, through the board's `Sessions.file_manager`, and are the entries `fidelity-progress.files` sends.
