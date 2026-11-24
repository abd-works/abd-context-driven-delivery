# space/session

A *Session* is one named piece of work in `.sessions/{name}/`; *Sessions* are all of a checkout's sessions; its *SessionLog* records each action, a *PracticeSessionOutput* is what one practice has in it, and its *FileManager* lists and reads the files under its roots.

- **Purpose:** Keep the state of one piece of work — where it works, which practices it uses and where they write, the files it works with, the log of what was done, the handoff the next agent resumes from, and the reasons behind hard-to-reverse choices — so any chat or tool can pick the work up from its folder.
- **Seam (terms):** Sessions, Session, BoardPractices, CallSessions, SessionLog, ChatLog, LogEntry, LogTimestamp, HookLog, PracticeSessionOutput, FidelitySessionOutput, FileManager, FileEntry, FileText, PathOutsideRootsError, ThrowawayProject, SessionDiagnostics
- **Dependencies (one-way):** harness/annotations, harness/agent_tools, harness/installation, harness/hooks, harness/mcp, harness/guidance, harness/graph, harness/diagnostics, harness/catalog_generator, harness/git, space/work_state, space/repo, cdd_guidance/actions (the session diagnostics probe runs Generate and Validate)

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
+ << composition >> board_practices: BoardPractices
+ << composition >> file_manager: FileManager
----
+ of_project(project: Path): Sessions
	-> CallSessions.of_project
+ folder_of(name: str): Path
+ all(): list[Session]
+ named(name: str): Session | None
+ with_file(session_file: str): Session
	-> HeldSessions.load
+ create(name: str, workpath: Path | None = None, title: str = '', scope: str = '', parent: str = ''): Session
+ current(call: ToolCall | None = None): Session
	-> OpenSessions.current
+ switch(name: str = '', workpath: Path | None = None, call: ToolCall | None = None): str
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
	-> SessionRoots.root_of
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
+ state(chat: str = ''): WorkState
+ name_for(chat: str = ''): str
+ open(session: Session, chat: str = ''): Session
+ current(chat: str = ''): Session
+ close(session: Session): None
+ ticket_of_worktree(): Session | None
+ switch(name: str, workpath: Path | None, call: ToolCall | None): str
	-> SessionLog.instructions
---<<creates>>--> WorkState
---<<raises>>--> SessionNameRequiredError

## ServedAnswers

The answers the process gives from one checkout's sessions (`answer_reads.py`): none until *CallSessions* begins one.

+ ServedAnswers()
------
+ current: int | None
----
+ begin(): None

## BoardPractices

The practices a checkout's session board works through, each as the catalog shows it, made once for the checkout and kept by its *Sessions*.

+ BoardPractices(catalogued: list[CatalogPractice])
------
+ << aggregation >> catalogued: list[CatalogPractice]
----
+ of(kind: type): CatalogPractice
+ works_through(kind: type): bool
+ keyed(key: str): CatalogPractice
---<<raises>>--> PracticeNotFoundError

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

+ Session(sessions: Sessions)
------
+ name: str
+ << association >> sessions: Sessions
+ << association >> repo: Repo
+ repo_path: Path
+ << composition >> context_config: ContextConfig
+ workpath: Path | None
+ record_folder: Path | None
+ work_folder: Path | None
+ is_closed: bool
+ is_repository: bool
+ session_file: Path
+ session_file_from_project: str
+ work_root: Path
+ << composition >> graph: Graph
	-> PracticeOutputs.graph
+ << composition >> practice_outputs: PracticeOutputs
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
+ context_folder(module: str = ''): Path
+ path_named(named: str | Path): Path
+ document_named(content: str = '', paths: list[str] | str | None = None): str
+ from_project(path: Path | str): str
	-> Repo.path_from_top
+ save_fields(**values): None
+ save(): None
+ hook_log(filename: str): HookLog
+ keep_file(file: Path): Path
+ move_to_closed(): Session
+ move_to_archive(): Session
+ move_to_backlog(): Session
+ reopen(): Session
	-> Sessions.moved
+ practice(name: str): PracticeSessionOutput
+ close(): None
	-> OpenSessions.close
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

## SessionExplorer

Mixed into *Session*: the published graph tools a page browsing the session's files calls, each reading the session's graph itself.

----
+ graph_trees(paths: list[str], call: ToolCall | None = None): list[ExplorerEntry]
	-> SessionPaths.in_project
	-> Graph.load_files
	-> GraphExplorer.explorer_trees
+ graph_branch(node_id: str, paths: list[str]): ExplorerEntry | None
	-> GraphExplorer.explorer_branch
+ graph_node_ranges(node_id: str, paths: list[str]): list[Range]
	-> NodeSpans.collect
+ graph_members(): list[NodeSource]
	-> GraphExplorer.source_members

## SessionGuidanceTools

Mixed into *Session*: the published tools that read and change its guidance selection, whose versions its *GuidanceVersion* keeps.

----
+ guidance_selection(): GuidanceSelection
+ update_guidance_selection(stages: list[str] | None = None, practices: list[str] | None = None, formats: list[str] | None = None): GuidanceSelection
	-> GuidanceVersion.select
+ guidance_selection_after(version: int): GuidanceSelection
	-> GuidanceVersion.wait_past

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
+ << composition >> entries: list[LogEntry]
+ << composition >> injected_rules: InjectedRules
+ last_loop_number: int
+ latest_loop_with_entries: int
----
+ latest(*verbs: str, stage: str = ''): LogEntry | None
+ record(line: str): None
	// a session without a folder has a log that writes nothing
+ by(chat: ChatPointer | None): ChatLog
+ append_trace(failure: BaseException, tool: str): int
+ seed_first_loop(): None
+ loop_at(number: int): Loop
+ read_loop(number: int | None = None): str
+ loop_to_note(loop: int | None): int
+ instructions(): str
---<<creates>>--> LogEntry
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

## LogEntry

One line of a session log: `<time> <verb> <words...>`, the words being the subject the verb acted on.

+ LogEntry(line: str)
------
+ text: str
+ time: str
+ verb: str
+ words: list[str]
+ stage: str
+ loop_number: int | None
----
+ names(fidelity: FidelityGuidance): bool
---<<reads practice guidance of>>--> FidelityGuidance
---<<reads name of>>--> FidelityGuidance

## LogTimestamp

The time a session log line, a hook log entry, or a toast is stamped with: a moment in UTC, to the second, such as `2026-11-07T17:30:05Z`, so every log's lines sort and compare alike.

+ LogTimestamp(moment: datetime)
------
+ moment: datetime
----
+ now(): LogTimestamp
+ read(text: str): LogTimestamp

## HookLog

A log a hook appends to while a session is open, such as `dispatch.debug` or the prompt log, in the `logs` folder of the session's work folder.

+ HookLog(path: Path)
------
+ path: Path
----
+ append(text: str): None
+ stamped(line: str): None
---<<stamps lines with>>--> LogTimestamp

## PracticeSessionOutput

What one practice has in one session: the session's one instance of the practice, whether it is on, and the folder it writes under.

+ PracticeSessionOutput(guidance: PracticeGuidance, session: Session)
------
+ name: str
+ << association >> session: Session
+ session_file: str
+ << composition >> guidance: PracticeGuidance
+ fidelities: GuidanceCollection
+ saved: dict
+ enabled: bool
+ chosen_outputs: dict
+ folder: Path
+ output_root: Path
+ root: str
+ is_root_chosen: bool
----
+ load(session: str, practice: str, call: ToolCall): PracticeSessionOutput
	-> ToolCall.session_named
	-> Session.practice
+ of_fidelity(fidelity: FidelityGuidance): FidelitySessionOutput
+ save(**values): None
+ enable(is_enabled: bool): PracticeSessionOutput
+ choose_root(path: str): PracticeSessionOutput
+ keep_root(root: Path): None
+ use_default_root(): PracticeSessionOutput
---<<creates>>--> FidelitySessionOutput
---<<reads the configured folder from>>--> ContextConfig
---<<saves fields>>--> Session
---<<annotated with>>--> Identity
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> NoSessionLog

## FidelitySessionOutput

Where one fidelity writes in one session: its output paths by format, the files it declares there, the format it last used, and its reports folder.

+ FidelitySessionOutput(practice: PracticeSessionOutput, fidelity: FidelityGuidance)
------
+ << association >> practice: PracticeSessionOutput
+ << association >> fidelity: FidelityGuidance
+ is_enabled: bool
+ reports_folder: Path
+ root: Path
+ chosen_formats: list[str]
+ chosen_outputs: dict
+ << composition >> formats: FidelityFormats
+ << composition >> validation_reports: ValidationReports
+ << composition >> written: WrittenFiles
----
+ load(session: str, practice: str, fidelity: str, call: ToolCall): FidelitySessionOutput
+ choose_root(path: str): FidelitySessionOutput
+ choose_format(format: str, is_chosen: bool): FidelitySessionOutput
---<<holds>>--> WrittenFiles

## WrittenFiles

The files one fidelity writes in a session (`session_output.written`): where it writes each format under its root, the files it declares there, whether any is there yet, and which the session's branch changed.

+ WrittenFiles(output: FidelitySessionOutput)
------
----
+ output_paths(): dict[str, list[str]]
+ files(): dict[str, list[FileEntry]]
	-> SessionFiles.find
+ holds(file: Path): bool
+ every_file(): list[Path]
+ has_output(): bool
+ has_named_output(): bool
+ has_found_output(): bool
---<<matches declared paths with>>--> DeclaredFile
---<<lists the declared files as>>--> FileEntry

## FileManager

List and read the files under a session's roots, the folders its practices work in, named from its workpath. Moved here from tools/file_manager.

+ FileManager(workpath: Path | str, roots: tuple[Path, ...])
------
+ workpath: Path
+ roots: tuple[Path, ...]
----
+ load(call: ToolCall): FileManager
	-> ToolCall.session
+ list(folder: str = ''): Folder
+ read(path: str): FileText
	// never reads a path outside the session's roots; such a path raises PathOutsideRootsError
+ find(pattern: str): list[Path]
---<<creates>>--> Folder
---<<creates>>--> FileText
---<<raises>>--> PathOutsideRootsError
---<<annotated with>>--> LanguageAdapter
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> NoSessionLog

## FileEntry

One file something declares, such as a fidelity's output, as a path from the project, and whether it is there yet.

+ FileEntry(path: str, exists: bool)
------
+ path: str
+ exists: bool
----

## FileText

The text of one file, with its path from the workpath; no text for a file that is not there.

+ FileText(path: str, text: str)
------
+ path: Annotated[str, SourceFile]
+ text: str
----

## PathOutsideRootsError : ValueError

A path outside every root of the session, which a page may name but never reach.

+ PathOutsideRootsError(path: str)
------
----

## ThrowawayProject

An empty project named by `CDD_PROJECT` while a spec runs, so the actions a spec runs write to their own session log instead of the log of whoever is working in the repository.

+ ThrowawayProject(name: str = '')
------
+ root: Path
+ folder: Path
----
+ close_all(): None
+ close(): None

## SessionDiagnostics : CallDiagnostics

Probe session logging (generate, validate, loops, chat pointers). Made for one call, as every diagnostics toolset is, so it writes the report into the install of the project that call names.

------
----
+ session_diagnostics(): str
+ write_to(diagnostics: InstallDiagnostics): str
	-> SessionProbe.run
---<<writes a section of>>--> InstallDiagnostics
---<<runs>>--> Generate
---<<runs>>--> Validate
---<<annotated with>>--> AgentToolSetAnnotation
---<<annotated with>>--> Mcp
---<<annotated with>>--> Skill
---<<annotated with>>--> Command
