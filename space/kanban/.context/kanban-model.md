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

Sources: `board.py`, `ticket.py`, `ticket_tree.py`, `ticket_choices.py`, `ticket_checkout.py`, `backlog_item.py`, and `report.py`. Every class and member here is in the code. `kanban-model.drawio` draws the same classes and relationships.

A member noted *data field* is marked `@data_field`: MCP sends an object as exactly those members, each object they hold as its own data, and the language adapter types `{Class}Data` from them. A data field sent under another name says so (*data field `slug`*). A *reference* data field (`@data_field(reference=True)`) sends the object it holds by its `@identity` fields alone, such as `{"name": "Discovery"}` for a column: the object is sent in full by the one that holds it, so a ticket names its column without sending the column, and the column's tickets, again.

A class marked `@identity(...)` names the data fields that name one of its objects. A language adapter reads them as the arguments of the class's `@tool_subject` loader, in the same order.

A `@tool_subject` loader or class tool that takes `project` is handed the project the call works on by its tool, so no tool takes it as an argument.

## Board

+ Board(sessions: Sessions, practices: BoardPractices, call: ToolCall | None)
	// practices is left out by `Board.load(project, call)`, so the board works through its sessions' held `BoardPractices` (`BOARD_PRACTICES.of(sessions)`); a board that works through fewer practices is handed its own. call is the call the board is read for, handed to `Board.load` and to the loaders of `Ticket`, `Stage`, and `BacklogItem` from the call they serve
------
+ call: ToolCall | None
	// the call the board is read for; `chat` is its chat's id, empty for a call that names none: `active` and a ticket's `is_active` name the session that chat has open, a ticket's `close`, `archive`, `delete`, and move to the Backlog close its session for that chat, and `new_chat_link` opens the new chat beside it
+ << association >> repo: Repo
	// the repository the sessions folder sits in: its sessions' repository
+ sessions: Sessions
	// the sessions of its repository, handed to it: each one a ticket, and which is open
+ project: str
	// data field: the repository folder's name
+ sends_fixes_directly: bool
	// data field: whether a report's Fix sends its prompt straight to the chat, or, by default, fills the chat's box for the person to edit; read from `_board.json`, set once per repository
+ << aggregation >> practices: list[PracticeGuidance]
	// data field: the practices every ticket works through, each with its key, slug, short name, and colour: the practice each held catalog view is of
+ << aggregation >> catalogued_practices: BoardPractices
	// the catalog's view of each practice, held for the checkout by `BOARD_PRACTICES.of(sessions)` (`space/kanban/board_practices.py`), so the process makes it and its one skill install once however many boards the calls make; it answers a practice by its class (`of`, `works_through`), which the board's own instance and a ticket's session's share, or by the key a tool names (`keyed`), and every `Help` is handed the one it answers; raises `PracticeNotFoundError` for a practice the board does not have
+ << composition >> stages: list[Stage]
	// its columns from Discovery to Implementation, made once with the board; `stage(name)` answers one and refuses any other column with `NotAStageError`, for `stage.*` tools and `ticket.move_to`
+ << composition >> fidelities: list[BoardFidelity]
	// data field: every fidelity of its practices with its practice, its label, and its skill's slash command, as the catalog names them, so a tile shows them and works out none; the board sends each fidelity once, here
	-> CatalogPractice.shown_fidelities
+ << composition >> columns: list[Column]
	// data field; always Backlog, then one Stage for each `ApproachStage` in `STAGES` (`harness/guidance/stages.py`), then Complete
+ << composition >> tickets: list[Ticket]
	// one per session of the repository, made once per board read and kept until `CardPlacement.reread`
	-> Sessions.all
+ << aggregation >> backlog_items: list[BacklogItem]
	// every idea file in `.sessions/_backlog/`, and every ticket folder kept there, read once per board read and kept until `CardPlacement.reread`
	-> BacklogFolder.idea_files
+ cards: list[Card]
	// its tickets, then its backlog items
+ active: Ticket
	// reference data field: the ticket of the session saved as open, sent by its name, since its column sends it whole; main's ticket while the main session is
	-> OpenSessions.name_for
	-> CardPlacement.ticket
+ << composition >> placement: CardPlacement
	// the cards it places, and what its current read has found, made once with it
+ << composition >> shared: BoardFile
	// what its repository's sessions share on it, in `_board.json`
+ reads: BoardReads
	// what its current read has found
	-> CardPlacement.reads
+ worktrees: dict[Branch, Repo]
	// each branch's worktree, listed once per board read rather than once per ticket, because the board is read after every call; a project that is no git clone has none
	-> Repo.is_clone
	-> Repo.worktrees
----
+ load(project: Path): Board
	// the `@tool_subject` of the `board.*` tools, handed the call's project: the board of that project's main checkout with every practice chosen, so a chat in a ticket's worktree reads the same board
	-> Repo.of_project
	-> Repo.main_clone
	-> BOARD_PRACTICES.of(sessions)
+ show(): Board
	// `board.show`
+ folders(path: str): list[str]
	// `board.folders`: the folders inside one folder of the repository, as paths from the project; installed packages, caches, and hidden folders other than `.context` are left out, so a person can choose a `.context` folder as a practice root
	-> Sessions.file_manager
	-> FileManager.list
	-> Folder.folder_paths
+ help(practice: str): Help
	// `board.help`: the help of the board's practice named practice, such as `stories`; a fidelity's help comes from its progress, `fidelity-progress.help`
	-> BoardPractices.keyed
	-> Help.on_practice
+ set_sends_fixes_directly(sends: bool): Board
	// `board.set_sends_fixes_directly`: keeps sends in `_board.json`, committed on main and pushed
	-> BoardFile.set_sends_fixes_directly
+ unsaved: SaveFailure
	// the latest save of the tickets' records on main that git refused, naming each change not yet saved; none while every save went through
	-> Sessions.saves
	-> SessionSaves.failure
+ save_again(): Board
	// `board.save_again`: queues again the changes whose save git refused, as the board's Save again does
	-> SessionSaves.retry
+ column(name: str): Column
	// raises `ColumnNotFoundError` for a column the board does not have
+ stage(name: str): Stage
	// raises `NotAStageError` for any column that is not a stage, for `stage.*` tools and `ticket.move_to`

## CardPlacement

The cards one board places, made once with the board: a ticket for each session and an item for each idea in its Backlog, of the kinds the kanban package hands over (`CARD_KINDS`), and what the board's current read has found. A change made through the board starts a new read.

+ CardPlacement(board: Board)
------
+ << composition >> reads: BoardReads
	// what the current read has found; replaced whole by `reread`
----
+ reread()
	// forgets the tickets, backlog items, worktrees, and chats read so far, so the next read sees a change made since
+ ticket(name: str): Ticket
	// read from that ticket's session folder alone, open before closed; none when no session has that name
	-> Sessions.named
+ ticket_called(name: str): Ticket
	// `ticket`, raising `TicketNotFoundError` when the board has none: where a ticket's name enters from a tool call
+ open_ticket(title: str, scope: str, path: str): Ticket
	// a new ticket in Discovery, its session working on path, a folder in the repository; raises `FolderOutsideRepositoryError` for a folder outside it
	-> Sessions.create
+ ticket_of(session: Session): Ticket
	// the ticket of a session just opened, moved between folders, closed, or reopened; the board forgets the cards it has read
+ backlog_item_of(ticket: Ticket): BacklogItem
	// the item a ticket becomes once its folder has moved into the Backlog
	-> BacklogItem.from_ticket
+ make_ticket(session: Session): Ticket
	// the ticket the board places for session, as it reads it now
+ make_backlog_item(path: Path): BacklogItem
	// the backlog item the board places for the idea kept in path

## BoardReads

What one read of a board finds, each read once when first asked for: its tickets, its backlog items, its worktrees, its branches, and the chats connected.

+ BoardReads(board: Board)
------
+ tickets: list[Ticket]
	-> Sessions.all
+ backlog_items: list[BacklogItem]
	-> Sessions.backlog_folder
+ backlog_folder: BacklogFolder
	// the Backlog's folder, which answers which of its files are ideas and where each lies
----
+ backlog_item_called(title: str): BacklogItem
	// the backlog item titled title, of those this read found, raising `BacklogItemNotFoundError` when the board has none
+ children_of(ticket: Ticket): list[Ticket]
	// the tickets whose session names ticket's as its parent, found once per board read
	-> Session.parent
+ chat_named(name: str): Chat
	// the first chat connected now that goes by name

## BoardFile

`.sessions/_board.json`, what a repository's sessions share on its board, read once per board read; the board is its one reader and writer.

+ BoardFile(board: Board)
------
+ sends_fixes_directly: bool
- _file: Path
	// `.sessions/_board.json`, in the folder of the board's sessions
	-> Sessions.folder
----
+ set_sends_fixes_directly(sends: bool)
	// keeps whether a report's Fix sends straight to the ticket's chat, beside whatever else the file holds
+ wip_limit(stage: Stage): int
	// the limit saved for stage, else 3
+ set_wip_limit(stage: Stage, limit: int)
	// saved beside the other stages' limits, keeping whatever else the file holds
+ order_in(column: Column): list[str]
	// the keys of column's cards in the order a person last placed them
+ keep_order(column: Column, keys: list[str])
- _keep(values: object)
	// writes values into the file, keeping whatever else it holds

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
	-> BoardFile.order_in
----
+ place_before(card: Card, other: Card): Column
	// keeps card just above other; raises `CardNotInColumnError` when either is not a card of its own here
	-> BoardFile.keep_order

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
	-> BoardFile.wip_limit
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
	-> BoardFile.set_wip_limit

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
+ move_before(other: Card): Card
	// a person's move of it just above other in their column; committed on main and pushed
	-> Column.place_before
+ move_after(other: Card): Card
	// a person's move of it just below other in their column; committed on main and pushed
	-> Column.place_after

## Ticket : Card

Marked `@identity("name")`. Never moves to another column by itself: a person moves it, and the move is written to its session log. It holds five parts, each made once with it: its *TicketWork* (its progress), its *TicketCheckout* (its branch and worktree), its *StageMarks* (the moves and marks a person made), its *TicketTree* (where it sits among its parent and children), and its *TicketMoves* (Move next, Move previous, a drag). Its data fields stay on it, and its tools are declared by job on six bases mixed in ahead of *Card*, each `@hosted_only`, so the toolset still publishes every one as `ticket.*` (`cdr/0004`): *TicketCheckoutTools* (`branch`, `work_branch`, `assign_chat`, `close_choices`, `activate`, each asking its *TicketCheckout*), *TicketChoices* (`fidelity_files`, `root_files`, `format_choices`, `choose_formats`, `overlay_choices`, `choose_overlays`), *TicketMoveTools* (`move_next`, `move_previous`, `move_to`, asking its *TicketMoves*, and `move_before`), *TicketTreeTools* (`add_child`, `pull_out`, `reassign_parent`), *TicketEnding* (`close`, `archive`, `delete`, and `to_backlog`, which is no tool), and *TicketTextTools* (`edit_text`, `tag`). *TicketChoices*, *TicketTreeTools*, and *TicketEnding* do their own work on the ticket they are mixed into, with no part behind them. Below they are listed with the ticket, as its toolset publishes them.

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
	-> CardPlacement.ticket
+ << aggregation >> children: list[Ticket]
	// data field, sent whole, since a stacked child shows in no column: the tickets whose session names it as their parent
	-> BoardReads.children_of
+ is_pulled_out: bool
	// data field: a child moving on the board as a card of its own, still keeping its parent
	-> Session.is_pulled_out
+ is_stacked: bool
	// data field: an open child, not pulled out, of an open parent, shown inside the parent's card
	-> TicketTree.is_stacked
+ << association >> session: Session
	// data field: its folders, its practices and their files, and its log
+ << composition >> progress: list[FidelityProgress]
	// data field: one per fidelity the board requires, in stage order, read from the session log once per ticket read and again after the ticket records a line; a judgment in the fidelity's latest report that fails a rule fails a validate the log shows passing
	-> TicketWork.progress
+ << composition >> work: TicketWork
+ << composition >> checkout: TicketCheckout
+ << composition >> marks: StageMarks
+ << composition >> tree: TicketTree
+ << composition >> moves: TicketMoves
+ << association >> column: Column
	// reference data field: Complete once its session is closed; a parent's is the stage of its child furthest back; otherwise the stage of the fidelity its latest generate or validate names, unless a `move` line came after it, whose stage it then sits in; with neither, Discovery
+ is_closed: bool
	// data field: its session is closed, so it shows in Complete
+ is_active: bool
	// data field: its session is the one saved as open
+ << composition >> prompts: TicketPrompts
	// data field: what the ticket asks its chat to do for it (split, handoff, set_up_roots, close_session, new_chat), each naming its session; the page sends them as Python worded them
+ can_edit: bool
	// data field: whether its text and tags may be edited: false for main, which `edit_text` and `tag` refuse with MainStaysOpenError
+ is_open: bool
	// data field: open for work, in its own worktree or the active ticket, and not main; its card offers Close, which closes it through its Close dialog unless the chosen chat works on it
	-> TicketCheckout.worktree
+ drop_targets: list[str]
	// data field: the columns besides the stages it can be dropped on: the Backlog always, Complete from Implementation's Done or while it is open
+ parent_choices: list[str]
	// data field: the tickets it can be dropped on to become their child: any on the board but its parent, itself, and the tickets under it, which would make a loop; none for main. `reassign_parent` refuses the same loop with `ParentLoopError`
	-> TicketTree.parent_choices
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
	-> CardPlacement.ticket_called
+ create(title: str, scope: str, parent: str, path: str, project: Path): Ticket
	// `ticket.create`: a new ticket in Discovery, in progress; it does not become the current session. scope is feature, story, or slice; parent names the ticket it was split from; path is its workpath
	-> Board.load
	-> CardPlacement.open_ticket
+ branch(): Branch
	// `ticket.branch`: its own branch, named as the ticket, with whether the repository has it and whether it is checked out, so activating a ticket offers only what is missing and leaving one commits, pushes, and merges only its own branch
	-> TicketCheckout.branch
+ work_branch(): Branch
	// `ticket.work_branch`: the branch its work is on, which leaving commits and pushes: its own branch while it is checked out, else the default branch while the checkout is on it, as for a session with no branch of its own; any other checkout gives its own branch, not checked out
	-> TicketCheckout.work_branch
+ format_choices(fidelities: list[str]): list[FormatChoice]
	// `ticket.format_choices`, from *TicketChoices*: the chips of an action bar over those fidelities, each fidelity's files read once
	-> TicketWork.progress_of
	-> FormatChoice.offered_by
+ choose_formats(fidelities: list[str], label: str, is_chosen: bool): list[FormatChoice]
	// `ticket.choose_formats`, from *TicketChoices*: one press on a chip, in the chat bar or on the board, chooses or leaves out its formats in the session
	-> FormatChoice.choose
+ activate(): Ticket
	// `ticket.activate`: opens it in its own worktree, where its own chat works on it; the chat that asks keeps its session, and the repository's own folder stays on main
	-> TicketCheckout.open
+ next_place: StagePlace
	// where Move next puts it while it stays on a stage: its stage's Done, else the next stage's In progress; none when the move closes it, leaves it where it is, or is refused. The page shows the card there at once, and `move_next` goes where it says
	-> TicketMoves.next_place
+ previous_place: StagePlace
	// where Move previous puts it while it stays on a stage: its stage's In progress, else the previous stage's Done; none when the move reopens it, sends it to the Backlog, leaves it where it is, or is refused
	-> TicketMoves.previous_place
+ move_next(): Ticket
	// `ticket.move_next`: from In progress it writes `done <stage>`, from Done it writes `move <next stage>`, and out of Implementation it closes; a parent raises `ParentMovesWithChildrenError`, as `move_previous` and `move_to` do
	-> TicketMoves.move_next
+ move_previous(): Ticket | BacklogItem
	// `ticket.move_previous`: from Done it writes `in-progress <stage>`, from In progress it writes `move <previous stage>` and `done <previous stage>`; out of Complete it reopens, and out of Discovery it returns to the Backlog
	-> TicketMoves.move_previous
+ move_to(stage: str, done: bool): Ticket | BacklogItem
	// `ticket.move_to`: a person's drag into a stage's In progress or Done; into the Backlog from any column it returns to the Backlog with its whole folder; raises `NotAStageError` for any other column
	-> TicketMoves.move_to
+ close(leaving: list[str]): Ticket
	// leaving is read into a Leaving, which refuses a step it does not take
	// `ticket.close`, from *TicketEnding*: does with its work what leaving names (handoff, commit, push, merge, delete_branch, delete_worktree); its session closes, its folder moves to `_complete/`, and that move is committed on main and pushed; main raises `MainStaysOpenError`
	-> TicketCheckout.write_handoff
	-> TicketCheckout.free_worktree
	-> TicketCheckout.keep_landing_release
	-> SessionFolder.move_to_closed
	-> TicketCheckout.save_work
+ assign_chat(chat: str): Ticket
	// `ticket.assign_chat`: keeps the chat's id in its session.json, committed on main and pushed
	-> SessionCheckout.assign_chat
+ archive(): Ticket
	// `ticket.archive`, from *TicketEnding*: its session closes and its folder moves to `_archive/`, off the board; the move is committed on main and pushed
	-> SessionFolder.move_to_archive
+ edit_text(text: str): Ticket
	// `ticket.edit_text`: writes text under its idea file's heading, making the file when it has none; committed on main and pushed; main raises `MainStaysOpenError`
	-> Session.keep_text
+ tag(word: str): Ticket
	// `ticket.tag`: adds word to its session's tags; committed on main and pushed; main raises `MainStaysOpenError`
	-> Session.add_tag
+ delete()
	// `ticket.delete`, from *TicketEnding*: its session closes and its folder is removed, that removal committed on main and pushed; main raises `MainStaysOpenError`
	-> SessionFolder.remove
+ to_backlog(): BacklogItem
	// from *TicketEnding*, no tool: into the Backlog from any column, its session closed and its whole folder a backlog item; main raises `MainStaysOpenError`
	-> SessionFolder.move_to_backlog
	-> CardPlacement.backlog_item_of
+ add_child(title: str): Ticket
	// `ticket.add_child`, from *TicketTreeTools*: a new child ticket, a story In progress in Discovery, working where it works; committed on main and pushed
	-> SessionHierarchy.open_child
	-> CardPlacement.ticket_of
+ pull_out(): Ticket
	// `ticket.pull_out`, from *TicketTreeTools*: a child becomes a card of its own, keeping its parent; a ticket with no parent raises `NotAChildError`
	-> SessionHierarchy.mark_pulled_out
+ reassign_parent(parent: Ticket | None): Ticket
	// `ticket.reassign_parent`, from *TicketTreeTools*: parent, or none, becomes its parent, and it is no longer pulled out; raises `ParentLoopError` when parent is it or one of its children; the tool names parent as it names any ticket
	-> SessionHierarchy.can_take_parent
	-> SessionHierarchy.set_parent
+ move_before(other: Ticket): Ticket
	// `ticket.move_before`: keeps it just above other in their column; the tool names other as it names any ticket
	-> Card.move_before
+ violations(): Report
	// `ticket.violations`: the rules broken on every fidelity of its stage left with violations, each naming its fidelity, a rule two fidelities share listed once; its path is the session's reports folder from the project
	-> TicketWork.violations

## TicketTree

`space/kanban/ticket_tree.py`. Where one ticket sits among the tickets its session names as parent and child, made once with the ticket. The changes a person makes to the tree are the ticket's own tools (`add_child`, `pull_out`, `reassign_parent`), declared on *TicketTreeTools*, which raise this file's `NotAChildError` and `ParentLoopError`.

+ TicketTree(ticket: Ticket)
------
+ is_stacked: bool
	// an open child, not pulled out, of an open parent
+ parent_choices: list[str]
	// any ticket on the board but its parent, itself, and the tickets under it; none for main
	-> Board.tickets
	-> SessionHierarchy.can_take_parent
+ furthest_back_child_stage: Stage
	// the stage of its child furthest back on the board, which a parent's column is
----
+ refuse_moving_a_parent()
	// raises `ParentMovesWithChildrenError` for a ticket with children

## TicketMoves

The moves a person makes with one ticket, made once with the ticket in `ticket.py`. A parent moves only with its children, so each move asks `TicketTree.refuse_moving_a_parent` first; each move is a mark in its *StageMarks*.

+ TicketMoves(ticket: Ticket)
------
+ next_place: StagePlace
	-> Stage.next_stage
+ previous_place: StagePlace
	-> Stage.previous_stage
----
+ move_next(): Ticket
	-> StageMarks.mark
	-> StageMarks.enter
	-> Ticket.close
+ move_previous(): Ticket | BacklogItem
	-> StageMarks.place
	-> SessionFolder.reopen
	-> Ticket.to_backlog
+ move_to(stage: str, done: bool): Ticket | BacklogItem
	-> StageMarks.place
	-> Ticket.to_backlog

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
+ violations: Report
	// the rules broken on every fidelity of the ticket's stage left with violations, taken together
	-> FidelityProgress.report
	-> Session.reports_folder
	-> SessionPaths.from_project
	-> Report.from_reports
----
+ progress_of(slug: str): FidelityProgress
	// only that fidelity's progress is read; raises `FidelityNotFoundError` for a fidelity the ticket does not have
+ in_stage(stage: Stage): StageWork
	// the progress of every fidelity stage requires whose practice its session works on
+ record(line: str)
	// writes line to its session's log, a move, a mark, or a backlog line; its progress is read from the log again next time
	-> SessionLog.record

## TicketCheckout

`space/kanban/ticket_checkout.py`. Where one ticket's work sits in git, made once with the ticket and holding its own *Branch*, named as the ticket.

+ TicketCheckout(ticket: Ticket)
------
+ << association >> branch: Branch
	// its session's checkout's branch: the recorded branch, else the one named as the ticket, else the one branch holding its name as a whole word
	-> SessionCheckout.branch
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
	-> SessionSaves.now
	-> Branch.open_in_worktree
	-> CardPlacement.reread
	-> SessionCheckout.record_opened
+ keep_landing_release(leaving: Leaving)
	// a ticket closed with its branch merged keeps its end-to-end results only
	-> LatestRelease.keep

## Leaving

What a person chose to do with a ticket's work as it closes, made by `Ticket.close` from its published `leaving` list (in `ticket_checkout.py`). A step leaving does not take, such as a misspelt one, is refused with UnknownLeavingStepError before anything changes; it was ignored before. Each step of *TicketCheckout* (`write_handoff`, `save_work`, `keep_landing_release`, `leave_branch`) asks it what was chosen, in the documented order of the close.

+ Leaving(steps: list[str])
------
+ writes_handoff: bool
+ commits: bool
+ pushes: bool
+ merges: bool
+ deletes_branch: bool
+ deletes_worktree: bool
+ changes_branch: bool
	// merges, deletes the branch, or deletes its worktree
+ saves_work: bool
	// commits, pushes, or changes the branch, which saves what a worktree about to go holds
+ removes_worktree: bool
	// deletes the worktree, or the branch, which takes its worktree with it
----
+ freeing_worktree(): Leaving
	// deletes the worktree alone, as archiving or deleting a ticket does

## StagePlace

Where a move puts a ticket that stays on a stage: the stage, and whether in its Done or its In progress. The board sends it on each ticket for Move next and Move previous, so the page shows the card there the moment either is pressed.

+ stage: Stage
+ is_done: bool

## StageMarks

The moves and marks a person made on one ticket's stages, made once with the ticket. They are the board's own fields in its session's session.json (`stage`, `stage_mark`, through `record.extra("ticket")`); a ticket moved before that record existed is read from its log (`SessionLog.latest`). A move or mark is also written to the log through the ticket's work.

+ StageMarks(ticket: Ticket)
------
+ moved_into: Stage
	// the stage session.json records, else the one named by its latest `move` line; none before a person has moved it
	-> OwnedFields.get
	-> SessionLog.latest
----
+ latest_in(stage: Stage): StageMark
	// the mark in stage since it was last moved there; none when there is none
+ enter(stage: Stage): Ticket
	// keeps the stage with no mark and writes `move <stage>`
	-> OwnedFields.save
	-> TicketWork.record
+ mark(mark: StageMark, stage: Stage): Ticket
	// keeps `done` or `in-progress` in stage, writes it to the log, then commits on main and pushes
+ place(stage: Stage, mark: StageMark): Ticket
	// enters stage unless the ticket is there, then marks it there

## StageMark

<< enumeration >> The mark a person gives a ticket in a stage; its value is the word the log and session.json keep.

+ DONE = "done"
+ IN_PROGRESS = "in-progress"

## Work

A ticket's work on some fidelities of one stage: one fidelity's progress (*FidelityProgress*) or a stage's work taken together (*StageWork*), each a *Work*. Each answers the command a chat runs for every action of its stage on its fidelities, which the ticket's session's guidance selection writes: the one place a command and its `format=` are written.

+ stage: Stage
	// abstract
+ fidelities: list[FidelityGuidance]
	// abstract: its one fidelity, or each of its fidelities
+ commands: dict[str, str]
	// data field: the command for each action of its stage
+ command(action: str): str
	-> GuidanceSelection.command

## FidelityProgress

How far one fidelity has got through its stage's actions on one ticket, read from session log lines. Marked `@identity("ticket", "slug")`: the ticket's name and the fidelity's slug are what its loader takes, so they are sent as strings until a language adapter can send an identity made of references.

+ FidelityProgress(required: RequiredFidelity, logged: LoggedWork, ticket: Ticket)
	// required is the fidelity with the stage that requires it; logged is what the ticket's session log says was done on it
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
	// data field, from Work: the command for each action of its stage on this fidelity, naming its ticket's session.json and, for an action that takes them, the formats chosen there
	-> GuidanceSelection.command
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
+ is_done: bool
+ << composition >> latest_report: ReportFile
	// its latest report in its ticket's session that has its result, else its latest; none when it has none; found once per reading of the progress
	-> ReportFile.from_fidelity
----
+ from_log(required: RequiredFidelity, ticket: Ticket): FidelityProgress
	// reads its ticket's session log entries and finds the fidelity by name, never by position
	-> TicketWork.entries
	-> LogLine.names
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
- _with_violations(): FidelityProgress
	// the same progress with its latest validate failed, for a judgment that fails a rule
- _with_accepted_left_out(): FidelityProgress
	// the same progress with its latest validate passed once a person accepted every violation its latest report names

## RequiredFidelity

A fidelity one of the board's stages requires, as a ticket's session holds it, with that stage.

+ RequiredFidelity(stage: Stage, fidelity: FidelityGuidance)
------
+ << association >> stage: Stage
+ << association >> fidelity: FidelityGuidance

## LoggedWork

What a ticket's session log says was done on one fidelity.

+ LoggedWork(done_actions: list[str], has_violations: bool, lines_logged: int)
------
+ done_actions: list[str]
+ has_violations: bool
+ lines_logged: int
	// how many log lines name the fidelity; a change means its files may have changed since they were last looked for
----
+ failed_again(): LoggedWork
	// this work with its latest validate failed
+ validated(steps: list[str]): LoggedWork
	// this work with its latest validate passed

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
	// reference data field: the fidelities of the stage whose practice the session works on, in the stage's order; the page's `TicketWork.progressIn` reads it
+ action_states: ActionStates
	// data field `actions`
	-> ActionStates.taken_together
+ has_violations: bool
	// data field: any of its fidelities has violations
+ violation_count: int
	// data field: its fidelities' violations together
+ commands: dict[str, str]
	// data field, from Work: the command for each action of its stage, one command naming every one of its fidelities
	-> GuidanceSelection.command
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
+ is_chosen: bool
	// data field: every fidelity the chip covers has the format it uses from the group chosen in the session (FidelitySessionOutput.chosen_formats)
----
+ choose(is_chosen: bool): None
	-> FidelitySessionOutput.choose_format (each fidelity the chip covers)
+ offered_by(read: list[tuple[FidelityGuidance, dict[str, list[FileEntry]]]]): list[FormatChoice]
	// a chip per group the fidelities offer, in the order of `Format.GROUPS`
	-> Format.group

## BacklogFolder

The Backlog's folder, `.sessions/_backlog` (in `backlog_folder.py`): it answers which of its files are ideas. An idea is a markdown file in it, or a folder holding a file of its own name: a ticket moved back keeps its whole folder, and a parent keeps its children's files beside its own.

+ BacklogFolder(folder: Path)
------
+ folder: Path
----
+ idea_files(): list[Path]
+ place_of(file: Path): IdeaPlace

## IdeaPlace

Where one idea's file lies in the Backlog, and the only mover of it. An idea's file is its only copy, so a move never deletes it or writes over another file; a folder a move leaves empty goes. *BacklogItem* holds one and asks it, and refuses a nesting (`_nesting_refusal`) before a move could write over a file.

+ IdeaPlace(file: Path, backlog_folder: BacklogFolder)
------
+ file: Path
+ is_in_own_folder: bool
+ ticket_folder: Path
+ holds_ticket: bool
+ parent_file: Path | None
----
+ move_under(parent: IdeaPlace)
+ move_out()
+ remove_emptied_folder()

## BacklogItem : Card

Marked `@identity("title")`. Its two order tools, `move_before` and `move_after`, are declared on *BacklogOrderTools*, a `@hosted_only` base mixed in ahead of *Card*, so the toolset still publishes them as `backlog-item.*`; they are listed below with the item.

+ BacklogItem(path: Path, board: Board)
------
+ title: str
	// the item's first `# ` heading, or its file name in words
+ column: Column
	// always the Backlog
+ parent_choices: list[str]
	// data field: the titles of the items it can be dropped on to become their child, any it is not already the child of and that nest_under would not refuse (one reason, `_nesting_refusal`, for both)
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
	-> BoardReads.backlog_item_called
+ create(title: str, text: str, project: Path): BacklogItem
	// `backlog-item.create`: writes one markdown file to `_backlog/`, the title as its heading and the text under it, committed on main and pushed
	-> Sessions.backlog_folder
	-> SessionSaves.later
+ from_ticket(ticket: Ticket): BacklogItem
	// the item a ticket moved into the Backlog waits in: `_backlog/<name>/<name>.md`, inside the ticket's kept folder on the ticket's board, its idea file made holding the ticket's title when the ticket never had one
+ parent: str
	// the title of the item whose folder keeps this one's file, `_backlog/<parent>/<child>.md`; empty for an item of its own
+ is_stacked: bool
	// a child shows inside its parent's card, not as a card of its own
+ children: list[BacklogItem]
	// the other markdown files in a folder that keeps no ticket's work, beside the parent's own `<parent>.md`; sent whole
+ start(scope: str, path: str): Ticket
	// `backlog-item.start`: an item a ticket was moved into returns that ticket with its folder; a new item's file moves into the new session folder; its children start too, each a story ticket that is its child
	-> HeldSessions.load
	-> SessionFolder.reopen
	-> CardPlacement.open_ticket
	-> SessionFolder.keep_file
	-> BacklogItem.start
	-> Ticket.reassign_parent
+ nest_under(parent: BacklogItem): BacklogItem
	// `backlog-item.nest_under`: moves its file into parent's folder, made from parent's one file the first time; one level only, never into or out of a folder kept with a ticket's work
+ leave_parent(): BacklogItem
	// `backlog-item.leave_parent`: moves its file back to the Backlog folder, an item of its own again
+ start_under(parent: Ticket): Ticket
	// `backlog-item.start_under`: starts the item, as dropping it on parent's card does, and gives its ticket parent as its parent
	-> BacklogItem.start
	-> Ticket.reassign_parent
+ edit_text(text: str): BacklogItem
	// `backlog-item.edit_text`: rewrites the text under its file's heading, which keeps its title; committed on main and pushed
	-> IdeaFile.rewrite_text
+ move_before(other: BacklogItem): BacklogItem
	// `backlog-item.move_before`: keeps it just above other in the Backlog; the tool names other by its title
	-> Card.move_before
+ move_after(other: BacklogItem): BacklogItem
	// `backlog-item.move_after`: keeps it just below other in the Backlog, as dropping it on other's bottom edge does
	-> Card.move_after

## Help

What `board.help` answers for a practice and `fidelity-progress.help` for a fidelity: the guidance objects themselves, with the text help shows.

+ Help(practice: PracticeGuidance, catalogued: CatalogPractice, required: RequiredFidelity)
	// required is left out for a practice's help
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
	-> GuidanceCollection.called
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
	-> CatalogSkills.skill_of
----

## Report

The rules a validation found broken, built from the saved report and the graph saved beside it, which keeps only the graph's violations and the nodes they were found on. It lives in `report.py`.

+ Report(source: ReportSource, rules: list[ReportRule], standing: SavedGraphStanding)
	// source is where the report was read from, its path and its text; standing says whether its graph is saved beside it and still in a shape the graph reads
------
+ path: str
	// data field
+ text: str
	// data field
+ << composition >> rules: list[ReportRule]
	// data field
+ fix_prompt: str
	// data field: fix every violation found in this report, read from the report itself, naming its ticket's session; empty for a report of no rule
+ has_saved_graph: bool
	// data field; false when the report has no saved graph, so its graph's rules are missing
+ violation_count: int
	// data field: graph hits and judged findings together, which the board app shows as they are sent
----
+ from_reports(folder: str, reports: list[Report]): Report
	// every rule broken in reports, each listed once though two fidelities share it

## ReportSource

Where a report was read from: its path from the project, or the reports folder of several, and its text.

+ ReportSource(path: str, text: str)
------
+ path: str
+ text: str

## SavedGraphStanding

Whether the graph a validation checked is saved beside its report, and whether it was saved in a shape the graph no longer writes; either way the graph's rules are missing from the report.

+ SavedGraphStanding(has_saved_graph: bool, is_out_of_date: bool)
------
+ has_saved_graph: bool
+ is_out_of_date: bool

## ReportRule

+ ReportRule(fidelity: FidelityGuidance, rule: Rule, violations: list[Violation], report_path: str)
	// report_path: the report, from the project, that found the rule broken
------
+ << association >> fidelity: FidelityGuidance
	// data field: the fidelity whose report found the rule broken
+ << association >> rule: Rule
	// data field: the broken rule with its slug and body; a rule no fidelity describes has its slug alone
+ count: int
	// data field
+ << composition >> violations: list[Violation]
	// data field
+ << composition >> violation_prompts: list[ViolationPrompts]
	// data field: what each violation's Fix (`fix`) and False (`false`) send its ticket's chat, one for each of violations in the same order, each naming the ticket's session
+ fix_prompt: str
	// data field: fix every violation of the rule, read from the report at report_path
+ identity: tuple
	// its rule's slug and its violations' practice, location, line, and message: a saved graph holds its whole practice's hits, so two fidelities of one practice report the same broken rule
----

## ReportFile

A validation report of one fidelity as the board reads it: the rules it finds broken, with the violations of the graph the validation checked, and the nodes they were found on, saved beside it. It knows which of its practice's rules it answers for, and describes each from its practice: the saved report points at each rule's text instead of copying it.

+ ReportFile(report: ValidationReport)
	// the report's fidelity is the one its session holds: its practice's session names the folder the saved graph names files from, and that session's repository names the report's files from its top
------
+ file: Path
+ << association >> report: ValidationReport
	// its name, when it was made, its saved graph, and its result are the session's ValidationReport's; an earlier fidelity's report is newer when ValidationReport.is_newer_than says so
+ text: str
+ has_result: bool
	// it has a saved graph or a judgment; validate saves a report before the agent judges it
+ is_judged_failing: bool
	-> Judgment.from_report
----
+ from_fidelity(fidelity: FidelityGuidance): ReportFile
	// the fidelity's latest report in the session that has its result, else its latest; none when it has none
	-> ValidationReports.listed
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

One rule the judgment in a validation report fails, in one judged file. It lives in `space/session/validation/validation_judgment.py`, beside *ReportJudgment*, so the session's violation history reads the judgment the same way the board does.

------
+ file: str
+ rule: str
+ findings: list[Violation]
----
+ from_report(text: str): list[Judgment]
	// the rules a report's judgment fails, read from its `## Judgment` sections

## ColumnNotFoundError : LookupError

## NotAStageError : ValueError

Keeps the column named, as `stage`.

## PracticeNotFoundError : LookupError

`space/session/sessions.py`, raised by `BoardPractices`.

## FidelityNotFoundError : LookupError

## TicketNotFoundError : LookupError

Keeps the name asked for, as `ticket`.

## BacklogItemNotFoundError : LookupError

Keeps the title asked for, as `backlog_item`.

## CardNotInColumnError : ValueError

Keeps the card's key and the column's name, as `card` and `column`.

## ParentMovesWithChildrenError : ValueError

`ticket_tree.py`, with `NotAChildError` and `ParentLoopError`.

## NotAChildError : ValueError

## ParentLoopError : ValueError

## MainStaysOpenError : ValueError

`ticket.py`, raised when a tool would close, archive, shelve, or delete main, or edit its text or its tags. Keeps what was asked of main, as `action`.

---

# Collaborators

The classes below belong to other modules and are modelled in those modules' own documents. Each heading names the class so links and diagrams can point at it; the line under it says where it lives and what the board calls on it.

## Repo

`space/repo/repo.py`. The board reads the main clone of the project's sessions' repository (`Sessions.of_project(project).repo.main_clone`), and from it `root`, `is_clone`, `worktrees` (the `Worktrees` of `space/repo/worktree.py`, each checkout a `Repo`; `by_branch` names the checkout each branch is out in), `path_from_top(path)`, and `branch_named(name)`; a ticket calls `switch_branch`, `switch_worktree`, `push_commit`, and `close_branch`.

## Chat

`harness/chat/chat.py`. `Board.chats` lists the connected chats once per board read with `Chats.load().list()`; a ticket reads each chat's `folder` and `name`.

## Branch

`space/repo/repo.py`. `name`, `exists`, and `is_checked_out` are data fields, which `ticket.branch` sends; `open_in_worktree()` opens a ticket's worktree.

## Sessions

`space/session/sessions.py`. The board calls `all()`, `named(name)`, `load(folder)`, `opened.name_for(chat)` (*OpenSessions*, for the chat the board is read for, `board.chat`), `create(name, workpath, title, scope, parent)`, `switch(name)`, `folder`, and `backlog_folder`; the board's own `_board.json` sits in its `folder`.

## Session

`space/session/session.py`, sent whole as a ticket's `session` data field. The board reads `name`, `title`, `parent`, `is_pulled_out`, `tags`, `text`, `is_closed`, `workpath`, `practices`, `reports_folder`, and `log`, and calls `close()`, `remove()`, `reopen()`, `move_to_closed()`, `move_to_archive()`, `move_to_backlog()`, `keep_file(file)`, `keep_text(text)`, `add_tag(word)`, `set_parent(parent)`, `mark_pulled_out()`, `open_child(name, title, scope)`, and `from_project(path)`. A backlog item reads and writes its file through an `IdeaFile` (`space/session/idea_file.py`), the same as a session's idea file. Its `log` is a `SessionLog` (`space/session/session_log.py`), whose `entries` are `LogLine`s with `time`, `verb`, `stage`, `words`, and `names(fidelity)`, and whose `record(line)` writes a `LogLine` the board makes for a move or a mark; `latest(*verbs, stage)` answers a ticket's latest move and its latest mark in a stage.

## IdeaFile

`space/session/idea_file.py`: one markdown file holding an idea, its `# ` heading and the text under it. A backlog item holds one for its file and reads its `text` and calls `rewrite_text(text)`; a session's `idea_file` is the `<name>.md` its folder keeps, from which it answers `text` and `keep_text(text)`.

## PracticeGuidance

`harness/guidance/guidance.py`, the board's own set, which the board makes once for each checkout with `PRACTICE_CATALOGUE.create_all()` and holds as the catalog shows them (`BOARD_PRACTICES.of(sessions)`, `CatalogPractice.of_practices`). `key`, `slug`, `short_name`, and `colour` are data fields; the board reads `fidelities`, `rules`, `overview`, and `guidance`.

## FidelityGuidance

`harness/guidance/guidance.py`. `slug`, `name`, `outputs`, and `default_format` are data fields, which a stage's `work_required`, a progress's `fidelity`, and help send; the board reads `stage`, `practice_guidance`, `rules`, and `session_output.written` (its `files()`, `has_named_output()` and `has_found_output()`). Each fidelity's stage is one `ApproachStage` of `STAGES` (`harness/guidance/stages.py`), with its `name`, `title`, `scope` (a `StageScope`), `steps`, `actions`, and `producing_actions`.

## Rule

`harness/guidance/rule.py`. `slug` and `body` are data fields, which help sends.

## Violation

`harness/graph/violation.py`: one place a rule is broken, the one shape for graph hits and judged findings. `rule`, `practice`, `location`, `line`, `message`, and `source` (the numbered `SourceLine`s around the line, once `in_file(location, file)` has read them) are data fields. A judged finding is `Violation(FoundBy(rule), message, Location(file, line))`. A report reads the graph saved beside it through `SavedGraph.from_file` (`harness/graph/saved_graph.py`), the one reader of a saved graph document and of the node list `graph.return_nodes` answers with, groups its hits with `Violation.by_rule`, and reads the rules a scanner checks now from its session's graph, `graph.applied_patterns.checks_of(practice, saved.overlays)` (`harness/graph/pattern_overlays.py`), which asks the report's own practice with the overlays the graph was saved with, through the patterns the session's graph already holds.

`FileManager` and `FileEntry` (`space/session/files/file_manager.py`) list folders for `board.folders`, through the board's `Sessions.file_manager`, and are the entries `fidelity-progress.files` sends.
