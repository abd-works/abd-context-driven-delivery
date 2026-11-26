# space/session

A *Session* is one named piece of work in `.sessions/{name}/`; *Sessions* are all of a checkout's sessions; its *SessionLog* records each action, a *PracticeSessionOutput* is what one practice has in it, and its *FileManager* lists and reads the files under its roots.

- **Purpose:** Keep the state of one piece of work — where it works, which practices it uses and where they write, the files it works with, the log of what was done, the handoff the next agent resumes from, and the reasons behind hard-to-reverse choices — so any chat or tool can pick the work up from its folder.
- **Seam (terms):** Sessions, Session, CallSessions, SessionLog, ChatLog, LogLine, HookLog, SessionsRead, SessionFolderHeldError
- **Dependencies (one-way):** space/session/practices, space/session/files, space/session/validation, harness/process, harness/annotations, harness/agent_tools, harness/installation, harness/hooks, harness/mcp, harness/guidance, harness/graph, harness/chat, harness/git, space/work_state, space/repo

## Sessions

The work sessions of one checkout: open ones in `.sessions/{name}/`, closed ones in `.sessions/_complete/`. Which one each chat has open is its part *OpenSessions*; `main` works on the whole repository and is open when no other is.

+ Sessions(project: Path | str)
------
+ << association >> repo: Repo
+ root: Path
+ folder: Path
+ backlog_folder: Path
+ << composition >> opened: OpenSessions
+ << composition >> listing: SessionListing
+ << composition >> held: HeldSessions
+ << composition >> answers: ServedAnswers
+ << composition >> file_manager: FileManager
----
+ of_project(project: Path): Sessions
	-> CallSessions.of_project
+ folder_of(name: str): Path
+ all(): list[Session]
+ read_apart(): SessionsRead
	// goes on past a session.json it cannot read, where all stops at the first
+ named(name: str): Session | None
+ with_file(session_file: str): Session
	-> HeldSessions.load
+ create(name: str, workpath: Path | None = None, title: str = '', scope: str = '', parent: str = ''): Session
+ current(call: ToolCall | None = None): Session
	-> OpenSessions.current
+ switch(name: str = '', workpath: Path | None = None, create: bool = False, call: ToolCall | None = None): str
	// a name no session has is refused with UnknownSessionError unless create is true
	-> OpenSessions.switch
---<<creates>>--> Name
---<<calls of_project on>>--> Repo
---<<creates>>--> Session
---<<holds>>--> SessionListing
---<<holds>>--> HeldSessions
---<<holds>>--> OpenSessions
---<<holds>>--> ServedAnswers
---<<raises>>--> SessionNotFoundError
---<<reads the answering call from>>--> ToolCall
---<<creates all practices from>>--> PracticeCatalogue
---<<lists practices as>>--> CatalogPractice
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> AgentToolAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> Command

## SessionsRead

One read of a checkout's sessions that went on past a session.json it could not read: the sessions that read, in the board's order, and the failure of each that did not, which names its file.

+ SessionsRead()
------
+ sessions: list[Session]
+ failures: list[JsonFileUnreadable]
----

## SessionListing

Which folders in a checkout's `.sessions` hold a session (`sessions.listing`): main, the open work sessions, and the closed ones, never the folders the sessions share or what a closed session left behind among the open ones.

+ SessionListing(sessions: Sessions)
------
----
+ work_folders(): list[Path]
+ is_work_session(name: str): bool
+ is_open(folder: Path): bool
+ is_left_behind(folder: Path): bool
+ open_names(): list[str]

## HeldSessions

The one *Session* a checkout's sessions hold for each session folder (`sessions.held`), made the first time it is read, so every call in a session, from any chat, works on the same object, and held under the folder it moves to.

+ HeldSessions(sessions: Sessions)
------
----
+ load(folder: Path): Session
	// one Session is held for each session folder, so every call in a session, from any chat, works on the same object
	-> Session.placed
+ at(folder: Path): Session
+ moved(session: Session, moved_from: Path): None
+ removed(session: Session): None
---<<creates>>--> Session
---<<keeps>>--> Session

## OpenSessions

Which session each chat has open in one checkout, kept by the cdd server under `~/.cdd` (*WorkState*), never in the checkout, and switching a chat to another (`open_sessions.py`).

+ OpenSessions(sessions: Sessions)
------
----
+ state(chat: str): WorkState
+ name_for(chat: str): str
+ open(session: Session, chat: str): Session
+ current(chat: str): Session
+ close(session: Session, chat: str): None
+ ticket_of_worktree(): Session | None
+ switch(name: str, workpath: Path | None, create: bool, call: ToolCall | None): SwitchedSession
---<<creates>>--> WorkState
---<<creates>>--> SwitchedSession
---<<raises>>--> SessionNameRequiredError
---<<raises>>--> UnknownSessionError

## SwitchedSession

One switch of a chat to a session: the session opened, what the modules listening for an opening told the chat, and the notes the chat must read first, worded in `space/session/SESSION-SWITCH.md`.

+ SwitchedSession(session: Session, told_on_opening: str, asked_in_ticket_worktree: str | None = None, chat_works_in: Path | None = None)
------
+ session: Session
+ told_on_opening: str
+ opened_in_worktree_of: str
+ outside_worktree: Path | None
+ default_roots: list[str]
+ instructions: str
	-> SessionLog.instructions

## CallSessions

The sessions of every project this process serves, each made once and held while it runs. Registered with *ToolCall* when `sessions.py` is imported, so the framework opens a call's session without importing space.

+ CallSessions()
------
----
+ of_project(project: Path | str): Sessions
+ saved_in(project: Path): Session
+ open_in(call: ToolCall): Session
+ of_chat(call: ToolCall): Sessions
+ named_in(session_file: str, call: ToolCall): Session
---<<creates>>--> Sessions
---<<calls of_project on>>--> Repo
---<<registers itself as the session opener with>>--> ToolCall

## Session

One named piece of work in a project, its record (session.json, idea file) kept in the main clone's `.sessions/{name}/` and everything else it writes in its work folder, the same folder in its ticket's worktree when it has one. It holds where it works, the practices it uses, and its title; its log, files, handoffs, decision records, and chat injections are objects of their own, made with it. It holds no chat: a line a call logs points at that call's chat.

+ Session(sessions: Sessions, record_folder: Path)
------
+ name: str
	// its record folder's name
+ is_main: bool
	// whether it is main, the default session, which never closes
+ << association >> sessions: Sessions
+ << association >> repo: Repo
+ << composition >> checkout: SessionCheckout
+ << composition >> record: SessionRecord
+ << composition >> context_config: ContextConfig
	// the config.json of its checkout, made again when it is placed in another
+ workpath: Path | None
+ record_folder: Path
+ work_folder: Path | None
+ is_closed: bool
+ is_repository: bool
+ session_file: Path
+ session_file_from_project: str
+ work_root: Path
+ << composition >> graph: Graph
	-> SessionGraph.graph
+ << composition >> session_practices: SessionPractices
+ << composition >> session_graph: SessionGraph
+ workpath_from_checkout: str
+ title: str
+ scope: str
+ parent: str
+ fields: dict
+ reports_folder: Path
+ << composition >> practices: dict[str, PracticeSessionOutput]
+ latest_handoff: str
+ << composition >> log: SessionLog
+ << composition >> session_files: SessionFiles
+ << composition >> handoffs: Handoffs | None
+ << composition >> decision_records: DecisionRecords
+ << composition >> chat_injections: ChatInjections
----
+ from_file(session: str, call: ToolCall): Session
	-> ToolCall.session_named
+ placed(): Session
	// derives its checkout, then its work folder, then its workpath, in that one order
	-> SessionCheckout.own_worktree
+ context_folder(module: str = ''): Path
+ path_named(named: str | Path): Path
+ document_named(content: str = '', paths: list[str] | str | None = None): str
+ from_project(path: Path | str): str
	-> Repo.path_from_top
+ update(change: Callable[[SessionFields], object], said: str): None
	// changes the fields as session.json holds them now and queues the save on main
+ extra(owner: str): OwnedFields
+ save(): None
+ hook_log(filename: str): HookLog
+ keep_file(file: Path): Path
+ move_to_closed(): Session
+ move_to_archive(): Session
+ move_to_backlog(): Session
+ reopen(): Session
	-> Sessions.moved
+ practice(name: str): PracticeSessionOutput
+ refuse_if_main(action: str): None
	// raises MainStaysOpenError for main
+ close(call: ToolCall): None
	// closes the session for the calling chat; main, the default session, raises MainStaysOpenError
	-> OpenSessions.close
---<<raises>>--> MainStaysOpenError
+ choose_workpath(path: str = ''): Session
+ show(): Session
+ add_tag(word: str): None
+ keep_text(text: str): None
+ choose_overlays(overlays: list[str]): None
---<<mixes in>>--> SessionFileTools
---<<mixes in>>--> SessionExplorer
---<<mixes in>>--> SessionGuidanceTools
---<<mixes in>>--> SessionLogTools
---<<mixes in>>--> SessionDecisionTools
---<<creates all practices from>>--> PracticeCatalogue
---<<creates>>--> PracticeSessionOutput
---<<calls work_in on>>--> PracticeGuidance
---<<creates and opens saved>>--> Graph
---<<creates>>--> SessionLog
---<<creates>>--> HookLog
---<<raises>>--> UnknownPracticeError
---<<annotated with>>--> Identity
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> ToolSubject
---<<annotated with>>--> Skill
---<<annotated with>>--> Command
---<<annotated with>>--> AgentInstructionsAnnotation
---<<annotated with>>--> NoSessionLog

## SessionFileTools

Mixed into *Session*: the published tools that list, read, and write a session's files and put a file into a chat's context, each asking its *SessionFiles*. A toolset publishes the tools its class's bases declare under its own name, so they stay `session.*`.

----
+ folder_files(): list[FileEntry]
	-> SessionFiles.in_folder
+ workpath_files(): list[FileEntry]
	-> SessionFiles.in_workpath
+ read_file(path: str = ''): FileText
	-> SessionFiles.read
+ write_file(path: str, text: str): FileText
	-> SessionFiles.write
+ file(path: str, rules: bool = False, cross_file: bool = False): SessionFile
+ add_to_chat_context(chat: str, path: str, start_line: int = 0, end_line: int = 0): Chat

## SessionGuidanceTools

Mixed into *Session*: the published tools that read and change its guidance selection, which the session holds (`session.guidance`, a *GuidanceSelection* that changes itself and raises its own version).

----
+ guidance_selection(): GuidanceSelection
+ toggle_guidance(part: "stage" | "practice" | "format", name: str): GuidanceSelection
	-> GuidanceSelection.toggle
+ guidance_selection_after(version: int): GuidanceSelection
	-> GuidanceSelection.wait_past

## SessionLogTools

Mixed into *Session*: the published tools that mark and read its log's loops, add notes to it, and hand its work on, each asking its *SessionLog* or its *Handoffs*.

----
+ mark_loop(call: ToolCall): str
	-> ChatLog.next_loop
+ read_loop(number: int | None = None): str
	-> SessionLog.read_loop
+ append_log(call: ToolCall, note: str = '', loop: int | None = None, paths: list[str] | None = None): str
	-> ChatLog.append_note
+ write_handoff(content: str = '', paths: list[str] | str | None = None): str
	-> Handoffs.write
+ read_handoff_format(): str
+ handoff_session(next_focus: str = ''): str
+ debug_session(choice: str = '', details: str = ''): str

## SessionDecisionTools

Mixed into *Session*: the published tools that list and write its Context Decision Records, which its *DecisionRecords* keep.

----
+ read_cdr_format(): str
+ list_cdrs(): str
+ write_cdr(slug: str, content: str = '', paths: list[str] | str | None = None): str
	-> DecisionRecords.write
+ record_decisions_session(): str

## SessionLog

The log of one session: `session.log`, one timestamped line per action, tool call, note, and loop marker, each ending with a pointer to the chat that caused it, and `session.err`, the full trace of each failure a log line points at. A chat writes its lines through `by(chat)`.

+ SessionLog(session: Session)
------
+ session: Session
+ path: Path | None
+ error_path: Path | None
+ << composition >> entries: list[LogLine]
+ << composition >> injected_rules: InjectedRules
+ last_loop_number: int
+ latest_loop_with_entries: int
----
+ latest(*verbs: str, stage: str = ''): LogLine | None
+ record(line: str): None
	// a session without a folder has a log that writes nothing
+ by(chat: ChatPointer | None): ChatLog
+ append_trace(failure: BaseException, tool: str): int
+ seed_first_loop(): None
+ loop_at(number: int): Loop
+ read_loop(number: int | None = None): str
+ loop_to_note(loop: int | None): int
+ instructions(): str
---<<creates>>--> LogLine
---<<creates>>--> ChatLog
---<<stamps lines with>>--> LogTimestamp
---<<raises>>--> LoopNotFoundError
---<<reads session path of>>--> Session

## ChatLog

The lines one chat writes in a session's log, each pointing at that chat; `no-chat` when none is known.

+ ChatLog(log: SessionLog, chat: ChatPointer | None)
------
+ << association >> chat: ChatPointer
----
+ line(line: str): None
+ validation(worked: FidelitySessionOutput, violations: list[str]): None
+ action(action: str, paths: list[Path], worked: list[FidelitySessionOutput] | None = None): None
+ guidance_action(action: str, worked: list[FidelitySessionOutput]): None
+ tool(tool_name: str, paths: list[str] | None = None): None
+ note(message: str, paths: list[Path] | None = None): None
+ append_note(note: str, loop: int | None = None, paths: list[str] | None = None): str
+ failure(failure: BaseException, tool: str = ''): None
	-> SessionLog.append_trace
+ next_loop(): Loop
+ mark_loop(): int
---<<records lines in>>--> SessionLog
---<<names practice and fidelity of>>--> FidelitySessionOutput

## LogLine

One line of a session log, which writes and reads itself: `<time> <verb> <words...>`. A chat's log (*ChatLog*) makes one for each of its operations.

+ LogLine(verb: str, subject: str = '', paths: Iterable[str | Path] = (), practices: Iterable[str] = (), fidelities: Iterable[str] = (), formats: Iterable[str] = (), detail: str = '', rules: str = '', chat: ChatPointer | None = None, time: str = '')
------
+ verb: str
+ time: str
+ subject: str
	// what the verb acted on: a tool's name, a note, a loop's number, a stage
+ detail: str
	// written after the names, such as a validate's findings
+ paths: list[str]
+ practices: list[str]
+ fidelities: list[str]
+ formats: list[str]
+ rules: str
+ chat: ChatPointer | None
+ written: str
	// verb, subject, paths, practices, fidelities, formats, detail, rules, chat, each left out when empty; the log stamps the time
+ text: str
+ words: list[str]
+ stage: str
+ loop_number: int | None
----
+ read(text: str): LogLine
	// a line as the log holds it: its time, its verb, and the rest of its words as its subject
+ names(fidelity: FidelityGuidance): bool
	// by the practice's key, or, in an older validate line, its class
---<<reads practice guidance of>>--> FidelityGuidance
---<<reads name of>>--> FidelityGuidance

## HookLog

A log a hook appends to while a session is open, such as `dispatch.debug` or the prompt log, in the `logs` folder of the session's work folder.

+ HookLog(path: Path)
------
+ path: Path
----
+ append(text: str): None
+ stamped(line: str): None
---<<stamps lines with>>--> LogTimestamp

## MainStaysOpenError : ValueError

Raised when a tool would close main, the default session, or a board tool would archive, delete, or shelve it or edit its text or tags (`Session.refuse_if_main`); `session.close` and `ticket.close` give this one refusal. Keeps what was asked of main.

+ MainStaysOpenError(action: str)
------
+ action: str
----

## UnknownSessionError : LookupError

`sessions.switch` to a name no session has, without create: nothing is made or opened. Names the name asked for and the sessions there are.

+ UnknownSessionError(name: str, there: list[str])
------
+ name: str
+ there: list[str]
----

## SessionFolderHeldError : RuntimeError

A session's record folder cannot be removed because a running program holds it open. Nothing in the folder was deleted; it names the folder.

+ SessionFolderHeldError(folder: Path)
------
+ folder: Path
----
