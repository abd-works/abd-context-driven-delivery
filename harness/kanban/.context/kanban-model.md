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
- *Next action* is what Run next does on a ticket: generate, validate, then review for each practice in order, then the same for the next practice. Violations hold a session on that fidelity, because Review needs a clean Validate, so the next action is satisfy until they are fixed.

### activity

- One thing that happened in a session, read from one line of its log: when, which action on which fidelity and format, or which stage a person moved the ticket into. A move writes `move <stage>`; logs from before that word say `pull <stage>`, and both are read.

### backlog item

- An idea not yet started: one markdown file per idea in `.sessions/_backlog/`, added by a person. The Backlog column shows them. Starting one opens a ticket for it.
- A ticket moved back into the Backlog keeps its work, and starting its item brings the ticket back with that work.

### the work behind a ticket

- *Practices* say what has to be produced. Each practice has *fidelities*, and each fidelity names the stage that requires it, the *artifacts* it produces, and the *rules* those artifacts must keep. An artifact is a file a fidelity's `outputs` declares, saved relative to the session's workpath, so it is a path rather than a class.
- *Actions* do the work on one fidelity inside a session. Generate writes the artifacts. Validate reads them into the *knowledge graph*, runs the rules on its nodes, and saves a report with the graph it checked beside it, so a report's violations stay on their nodes. Review records a person's approval.
- Each node of the knowledge graph knows the fidelity that creates it, the file it came from, and the rules it breaks, so the graph can say which files belong to a fidelity.
- The board runs none of this. Each action writes a line to the session log, and the session answers from those lines and from the graph.

Build order: `Column` → `Stage` → `Backlog` → `Card` → `Ticket` → `FidelityProgress` → `BacklogItem` → `Board`

---

# harness/kanban

Purpose, seam, dependencies, and constraint: `.context/module-context.md`.

Sources: `board.py`, `ticket.py`, `backlog_item.py`, and for what is not built yet, the Board canvas at https://claude.ai/artifact/LGLk189R4aZ14bgwcWRiPN (Version 72). A class or member whose note starts "Intended" is not in the code yet, and `kanban-model.drawio` leaves it out. Everything else mirrors the code, and the diagram draws exactly that. The modules after `harness/kanban` show only the members the board's work depends on.

## Board

+ Board(sessions_folder: Path, practices: list[PracticeGuidance])
------
+ sessions_folder: Path
+ repo_root: Path
+ << association >> repo: Repo
	// the repository the sessions folder sits in
+ practices: list[PracticeGuidance]
+ << composition >> columns: list[Column]
	// always Backlog, then one Stage for each stage name, then Complete
+ << composition >> tickets: list[Ticket]
	// one per folder in `.sessions/` and `.sessions/closed/`; `main` and folders whose names start with `_` are left out
+ << aggregation >> backlog_items: list[BacklogItem]
	// every markdown file in the repository's `.sessions/_backlog/`
+ cards: list[Card]
	// its tickets, then its backlog items
+ active: Ticket
	// the ticket that represents the session saved in `.sessions/session.json`; none in the main session
----
+ to_json(): dict
	// the project, the active ticket's name, and every column with its tickets or items; the shape the board pane and other IDEs read
	-> Column.to_json
+ load(sessions_folder: Path): Board
	// a board with every practice chosen
+ current(): Board
	// the board of the project being worked on: `CDD_PROJECT`, else the current folder. The `@tool_subject` of the `board.*` tools
+ show(): Board
	// `board.show`
+ set_wip_limit(stage: str, limit: int): Board
	// `board.set_wip_limit`: saved in `.sessions/_board.json`
+ wip_limit(stage: str): int
	// 3 until a person sets it
+ help(practice: str, fidelity: str): dict
	// `board.help`: the overview, guidance, rules, and forge page of a practice or fidelity
+ ticket(name: str): Ticket
+ backlog_item(title: str): BacklogItem
+ column(name: str): Column

## Column

+ Column(name: str, board: Board)
------
+ name: str
+ << aggregation >> cards: list[Card]
	// every card of the board whose column is this one
	-> Board.cards
	-> Card.column
----
+ to_json(): dict
	-> Card.to_json

## Backlog : Column

+ Backlog(board: Board)
------
----
+ to_json(): dict
	-> Card.to_json

## Stage : Column

+ Stage(name: str, board: Board, actions: list[type])
------
+ actions: list[type]
	// Generate, Validate, and Review, in that order
+ practices: list[PracticeGuidance]
+ work_required: list[FidelityGuidance]
	// every fidelity of every chosen practice whose stage is this stage
+ next_stage: Stage
	// none after Implementation
+ previous_stage: Stage
	// none before Discovery
+ in_progress: list[Ticket]
+ done: list[Ticket]
	// tickets in this stage that are done; they wait here until a person moves them
	-> Ticket.is_done
+ wip_limit: int
----
+ to_json(): dict
	-> Card.to_json

## Card

The base type of Ticket and BacklogItem.

+ Card(board: Board)
------
+ title: str
+ << association >> column: Column
+ last_activity: str
	// a timestamp; blank when nothing has happened yet
----
+ move_next(): Card
	// a person's move to the next column
+ move_previous(): Card
	// a person's move to the previous column
+ to_json(): dict
	// the title and last activity; each card adds its own fields

## Ticket : Card

+ Ticket(session: Session, board: Board)
	// never moves to another column by itself
------
+ << association >> session: Session
+ name: str
	-> Session.name
+ title: str
+ scope: str
+ << association >> lineage: Ticket
+ practices: dict[str, bool]
	// whether this ticket works on each of the board's practices
	-> Session.active_practices
+ << composition >> progress: list[FidelityProgress]
	// one per fidelity the board requires, in stage order, read from the session log each time
+ column: Column
	// Complete once its session is closed; otherwise the stage named by its latest `move` or `pull` line; before any move, the earliest stage its log shows work in, or Discovery
+ is_done: bool
	// true only in a stage: when a person marked it done there, or, with no mark since entering, when all its enabled work there is done
+ next: FidelityProgress
	// the first fidelity in its stage that is not done
+ next_action: str
	// generate, validate, or review on the next fidelity; satisfy while it has violations
+ last_activity: str
	// the timestamp of its log's latest line
+ latest_handoff: str
+ reports: dict[str, str]
----
+ move_next(): Ticket
	// a person's move on, whatever its session's work: from In progress it writes `done <stage>`, from Done it writes `move <next stage>`, and out of Implementation it closes
+ move_previous(): Ticket | BacklogItem
	// a person's move back: from Done it writes `in-progress <stage>`, from In progress it writes `move <previous stage>` and `done <previous stage>`; out of Complete its session reopens in Implementation's Done; out of Discovery it moves into the Backlog and returns its BacklogItem, its folder kept under `_backlog/`, and it stops being the active ticket
+ close(leaving: list[str]): Ticket
	// after closing, its session is closed and its column is Complete; calls Session.close, then moves the session's folder to `closed/`. leaving names commit, push, merge
	-> Session.close
	-> Session.move_to
+ archive(): Ticket
	// after archiving, its session is closed and its folder is in `_archive/`, off the board
	-> Session.close
	-> Session.move_to
+ load(ticket: str): Ticket
	// the `@tool_subject` of the `ticket.*` tools: finds the ticket a tool call names
+ new(title: str, scope: str, parent: str, path: str): Ticket
	// `ticket.new`: a new ticket is in Discovery, in progress, until its log shows work in a later stage. Does not become the current session
	-> Session.new
+ activate(leaving: list[str], opening: list[str]): Ticket
	// `ticket.activate`: leaving names what to do with the active ticket's work; opening names branch and worktree
	-> Repo.switch_branch
	-> Repo.switch_worktree
	-> Session.switch
+ workspace(): dict
	// `ticket.workspace`: whether it has its branch and worktree
+ enable_practice(practice: str, is_enabled: bool): Ticket
	// `ticket.enable_practice`
	-> PracticeSessionOutput.enabled
+ files(): dict
	// `ticket.files`: each fidelity's declared files by format, with whether each exists
	-> Session.fidelity_outputs
+ read_file(path: str): dict
	// `ticket.read_file`: refuses a path outside the repository
+ report(fidelity: str): dict
	// `ticket.report`: the latest report, with the rules broken on the nodes of the graph saved beside it. A report with no saved graph lists no rules and says so
	-> Graph.write_json
+ generate_commands(fidelities: list[str], formats: list[str]): list[str]
	// `ticket.generate_commands`: renders the earlier fidelity first when a format is new to it
+ record(entry: str)
	// appends a timestamped line to the session log
+ to_json(): dict
	// its fields and column, with its session's work, next action, handoff, and reports

## FidelityProgress

How far one fidelity has got through its stage's actions on one ticket, read from session log lines.

+ FidelityProgress(fidelity: FidelityGuidance, stage: Stage, done_actions: list[type], has_violations: bool)
------
+ << association >> fidelity: FidelityGuidance
+ stage: Stage
+ practice: str
+ done_actions: list[type]
+ remaining_actions: list[type]
+ has_violations: bool
+ is_done: bool
+ slug: str
+ report_files: str
+ state: str
	// done, violations, in_progress, or not_started: what the board pane colours
+ action_states: dict[str, str]
	// each action as to_do, in_progress, or done
+ allowed_actions: list[str]
	// Validate once generated, and Review only after a clean Validate
----
+ from_log(fidelity: FidelityGuidance, stage: Stage, lines: list[str]): FidelityProgress
	// finds the fidelity by name, never by position

## BacklogItem : Card

+ BacklogItem(path: Path, board: Board)
------
+ title: str
	// the item's first `# ` heading, or its file name in words
+ column: Column
	// always the Backlog
+ text: str
	// the file's content after its heading; the details show it
+ path: Path
+ last_activity: str
	// when its file last changed
----
+ load(backlog_item: str): BacklogItem
	// the `@tool_subject` of the `backlog-item.*` tools
+ add(title: str, text: str): BacklogItem
	// `backlog-item.add`: writes one markdown file to `_backlog/`, the title as its heading and the text under it
+ holding(ticket: Ticket, board: Board): BacklogItem
	// the item a ticket moved back into the Backlog waits in
+ start(scope: str, path: str): Ticket
	// `backlog-item.start`: the new ticket's session log names this item's path; an item a ticket was moved back into returns that ticket with its folder, log, and progress; the item goes either way
	-> Ticket.new
+ move_next(): Ticket
	// a person's move forward: starts the item
+ move_previous(): BacklogItem
	// the Backlog is the first column, so the item stays
+ to_json(): dict

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
+ has_branch(name: str): bool
+ worktree_for(branch: str): Worktree
+ switch_branch(name: str): str
	// commits and pushes the branch being left, and leaves the default branch committed but not pushed
+ switch_worktree(name: str): str
	// opens the sibling worktree, and saves it as `worktree` in `.sessions/session.json`
+ push_commit(message: str, sync_remote: bool): Commit
+ close_branch(name: str): str
	// merges into the default branch, pushes it, and deletes the branch locally and on origin

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
+ << composition >> practices: dict[str, PracticeSessionOutput]
	// every practice CDD has, by practice key, opened or not
+ active_practices: list[PracticeSessionOutput]
	// the practices whose enabled is true; a new session has all of them
	-> PracticeSessionOutput.enabled
+ opened_practices: list[PracticeSessionOutput]
	// the practices this session has asked for, which its log lines name
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
+ practice(name: str): PracticeSessionOutput
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
	-> PracticeSessionOutput.artifacts
+ fidelity_outputs(guidance: PracticeGuidance): dict
	// where the active fidelity's artifacts are saved under the workpath, with the overrides in `session.json`
	-> FidelityGuidance.outputs
+ new(name: str, workpath: Path, repo_path: Path, fields: dict, is_current: bool): str
	// opens a session folder with `fields` in its `session.json`; is_current False leaves the current session as it is
+ at(session_path: Path, repo_path: Path): Session
	// the session kept in a folder, read without becoming current
+ fields: dict
	// what `session.json` holds, read each time
+ save_fields(fields)
+ move_to(parent: Path): Session
+ close()
	// ends the session; when it is the current one, the repository goes back to the main session
+ log_guidance_action(action: str, guidance_items: list)
+ log_validation(guidance: PracticeGuidance, violations: list[str])

## PracticeSessionOutput

+ PracticeSessionOutput(name: str, session: Session)
------
+ name: str
+ << association >> guideline: PracticeGuidance
	// loaded on first use, like output_paths and graph, because the board reads enabled after every cdd call and needs none of them
+ << composition >> graph: Graph
	// the knowledge graph of this practice's artifacts in the session
+ output_paths: list
+ enabled: bool
	// whether the session works on this practice; setting it saves it in the `practices` field of `session.json`. True until set
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
+ stage: str
	// which stage requires this fidelity, read from the fidelity's section in the practice markdown. A StageName in place of a string is still to come
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
	// builds the knowledge graph from the artifacts in paths, runs the fidelity's rules on it, saves the report in the session's `validation-reports/` with the graph it checked under the same name in `.json`, and logs one `graph-rule` entry per violation
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
	-> PracticeGraph.apply_rules
+ files_of(fidelity: str): list[str]
	// Intended: the source files of every node that fidelity creates
	-> Node.fidelity
	-> Node.source
+ write_json(path: str): str
	// the graph with every node's rule hits; `violations_from_graph_json_files` reads it back

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

+ GraphRulesCollection(node: Node, entries: dict[str, GraphRule], parent)
------
+ node: Node
+ << composition >> entries: dict[str, GraphRule]
----
+ slugs(): list[str]
+ violations(): list[tuple[str, str]]
	-> GraphRule.violations
+ failed_slugs(): list[str]
+ passing_slugs(): list[str]
+ graph_rules(): Iterator[GraphRule]
+ record_violation(slug: str, message: str, file: str, start: int, end: int)
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
----
+ record(message: str, file: str, start: int, end: int)
+ clear_violations()
+ failing(): bool

---

**Open**

- Starting a ticket's session (its folder and branch) stays with `space/session` and `space/repo`; the board reads what they write and does not call them.
- The path of a violation: `Validate.validate` -> `Graph.load_files` -> `PracticeGraph.apply_rules` -> `Node.rules`, on a `GraphRule`, saved by `Graph.write_json` beside the report, and read back by `Ticket.report`.
- `Validate` with an explicit graph file and paths filters its report to those paths; the saved graph holds the whole file, so `Ticket.report` lists every violation of the practice in it.
- Review is a `GuidanceAction` deployed as a command (`/review <guidance>`). It records a person's approval of a fidelity as a `review` line in the session log, which the ticket reads like any other action line.
- A person's move to Done is written as `done <stage>` and back as `in-progress <stage>`. The latest mark since entering the stage wins; with no mark, `is_done` is derived from progress.
- Locking is pane state, not a board rule: with Active session only on, the canvas disables every action on a ticket other than `Board.active`. The pane reads `active` from `Board.to_json` and holds the switch itself.
- Ticket-wide Run sends one action across a ticket's enabled practices at its current stage. It is a prompt the pane fills, so it needs no operation here beyond `Ticket.practices`.
- `FidelityProgress` and `Stage.work_required` stay until `Session` takes over what they do, and the ticket stops reading the log itself.
- `Session.fidelity_outputs` reads the session it is called on, so `Repo.sessions` must give sessions that can be read without one becoming the current session. `Session` today has one in-memory current, and opening one saves it as current.
- `space/repo` already has a class named `Ticket`, a GitHub issue. It is a different concept from the board's Ticket and needs a different name in one of the two modules.
- A `format` argument on Generate is still to be decided.
