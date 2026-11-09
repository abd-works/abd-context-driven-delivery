---
fidelity: [model, behavior]
artifact: [ce-domain-model, bdd-behavior]
format: md
---

# Session

**Sources / context:** `space/session/.context/session-context.md` (the request this module was built from), `space/session/.context/module-context.md` (its seam and dependencies)

**Module:** `space/session`

A session is one named piece of work in a project, kept in `.sessions/{name}/`. `Sessions` knows every session of one checkout and which one is open; `Session` holds where one session works, the practices it uses, and its title. Its log, its files, its handoffs, and its decision records are objects of their own, each reached through the session, so each has one reason to change.

Every tool on a session acts on the session whose `session.json` its `session` argument names. The process keeps one Session per session folder between calls, so every call from any chat works on the same object: a `ToolCall` (`harness/agent_tools/tool_call.py`) opens the session each call works in, through `CallSessions`, which holds the sessions of each checkout by its top, and the open session's name is read from `.sessions/session.json` each time it is asked for, so a switch or a close made by another chat or by the hook server is seen at once.

`patterns` in the source stops at the word pattern. That concept stays unresolved.

---

## clean engineering:

Sessions, a session, and its log

### **Sessions**

+ Sessions(project: Path)
------
+ project: Path
	// the project the call names
+ root: Path
	// the checkout folder holding project
	-> Repo.checkout_folder
+ folder: Path
	// `.sessions` under root
+ backlog_folder: Path
	// `.sessions/_backlog`, where sessions wait before work starts
+ open_name: str
	// the session saved as open in `.sessions/session.json`; main when none is
----
+ of_project(project: Path): Sessions
	// the `@tool_subject` of the `sessions.*` tools, handed the call's project: the sessions this process holds for it
	-> CallSessions.of_project
+ all(): list[Session]
	// the work sessions, open ones first then closed; not main and not the folders the sessions share
+ named(name: str): Session | None
	// only that session's folder is read
+ folder_of(name: str): Path
	// a ticket's session lives in the main checkout's `.sessions`, so a chat in the ticket's linked worktree logs there too
	-> Repo.primary_root
+ load(folder: Path): Session
	// read without opening it
+ with_file(session_file: str): Session
	// the session whose session.json is session_file; refuses a missing one with `SessionNotFoundError`
+ kept(session: Session): Session
	// one Session per session folder, opened for no call, which holds the session's graph and practices; moves with a session whose root moved
+ create(name: str, workpath: Path, title: str, scope: str, parent: str): Session
	// saves the session's fields and writes `--- 1` as the first log line; does not open it
	-> Session.save
	-> SessionLog.seed_first_loop
+ open(session: Session, workpath: Path | None): Session
	// saves the session and saves its name as the open session; main is saved as no name
+ current(): Session
	// MCP `sessions.current`, slash `/current-session`
+ switch(name: str, workpath: Path | None): str
	// MCP `sessions.switch`, slash `/switch-session`: opens the session called name, creating it when missing; the name defaults to the saved session, then to the saved branch
	// returns how to keep the log
	-> SessionLog.instructions
+ close(session: Session): None
	// when session is the open one, main becomes the open one

**Invariants**

- The open session is never held in memory; every read goes to `.sessions/session.json`.
- A session's graph and practices are made once, by its kept session, and every call's session answers them from it.
- main works on the whole repository and is never a work session: `all` and `named` leave it out.
- A name is always a slug (`name_of`), since a git branch refuses a space.
- switch with no name and nothing saved refuses with `SessionNameRequiredError`.

### **CallSessions**

----
+ of_project(project: Path): Sessions
	// the sessions of the checkout holding project, made the first time the process works in it and held by the checkout's top while it runs
+ saved_in(project: Path): Session
	// the session open in project, for work that serves no call, such as a hook event
	-> Sessions.current
+ open_in(call: ToolCall): Session
	// the session open in the call's project, with the call's chat
	-> saved_in(call.project)
+ named_in(session_file: str, call: ToolCall): Session
	// the session a board command names by its session.json, with the call's chat
	-> Sessions.with_file

**Interactions**

- Registered with `ToolCall.open_sessions_with` when the module is imported, so the framework opens a call's session without importing space.

### **Session**

+ Session(sessions: Sessions)
------
+ name: str
	// data field; the slug of the session
+ workpath: Path | None
	// the folder chosen for the session's work; none means the whole repository
+ repo_path: Path
+ session_path: Path | None
	// `.sessions/{name}/`; none before the session has a folder
+ chat: ChatPointer | None
	// the chat of the tool call the session was opened for
+ << composition >> log: SessionLog
+ << composition >> session_files: SessionFiles
+ repo: Repo
	// << association >> the repository that holds `.sessions`
+ work_root: Path
	// workpath, or the whole repository
+ session_file: Path
	// `session.json` in the session's folder: title, workpath, practice roots, practices
+ session_file_from_project: str
	// data field `session_file`: the name every board command gives this session
+ workpath_from_project: str
	// data field `workpath`
+ title: str
	// data field
+ scope: str
	// data field: feature, story, or slice
+ parent: str
	// data field: the session this one was split from
+ is_closed: bool
+ reports_folder: Path
	// `validation-reports/` in the session's folder
+ << composition >> practices: dict[str, PracticeSessionOutput]
	// data field; every practice CDD has, made once with its graph; one Session per folder, which its Sessions hold
+ handoffs: Handoffs
+ latest_handoff: str
	// data field `handoff`
+ decision_records: DecisionRecords
	// under the workpath's `.context/cdr/`
----
+ from_file(session: str, call: ToolCall): Session
	// the `@tool_subject` of the `session.*` tools: the session a call names, through `call.session_named`
+ practice(name: str): PracticeSessionOutput
	// the session's one instance of it; refuses a practice CDD does not have with `UnknownPracticeError`
	-> PracticeCatalogue.has
+ reset(): None
	// forget the opened practices
+ save(): None
	// name, workpath, and repo path into session.json, keeping the fields others store there
+ save_fields(values: dict): None
+ hook_log(filename: str): Path
	// a hook's own log in the session's `logs/` folder
+ keep_file(file: Path): Path
	// moves a person's file, such as a started backlog item's idea, into the session's folder
+ move_to_closed(): Session
+ move_to_archive(): Session
+ move_to_backlog(): Session
+ reopen(): Session
+ close(): None
	// MCP `session.close`, slash `/close-session`
	-> Sessions.close
+ choose_workpath(path: str): Session
	// MCP `session.choose_workpath`; a practice root a person chose is saved again against the new workpath
	-> PracticeSessionOutput.keep_root
+ folder_files(): list[FileEntry]
	// MCP `session.folder_files`
	-> SessionFiles.in_folder
+ read_file(path: str): FileText
	// MCP `session.read_file`
	-> SessionFiles.read
+ mark_loop(): str
	// MCP `session.mark_loop`, slash `/mark-loop`; the marker points at the chat the call came from
	-> SessionLog.mark_loop
+ read_loop(number: int | None): str
	// MCP `session.read_loop`, slash `/read-loop`
	-> SessionLog.read_loop
+ append_log(note: str, loop: int | None, paths: list[str]): str
	// MCP `session.append_log`, slash `/append-log`
	-> SessionLog.append_note
+ write_handoff(content: str, paths: list[str]): str
	// MCP `session.write_handoff`
	-> Handoffs.write
+ read_handoff_format(): str
	// MCP `session.read_handoff_format`: HANDOFF-FORMAT.md
+ handoff_session(next_focus: str): str
	// instructions: read the handoff format, draft the handoff, then call write_handoff with its file
+ read_cdr_format(): str
+ list_cdrs(): str
	-> DecisionRecords.paths
+ write_cdr(slug: str, content: str, paths: list[str]): str
	-> DecisionRecords.write
+ record_decisions_session(): str
	// instructions: offer a CDR when a decision is hard to reverse, surprising, and a real trade-off

**Invariants**

- Every tool acts on the session its `session` argument names, never on whichever session happens to be open.
- A session without a folder writes nothing: its log has no path and its fields are empty.
- save keeps every field others stored in session.json, such as a board ticket's title, scope, and parent.
- A practice root a person chose still names the same folder after the workpath moves.

### **SessionLog**

+ SessionLog(session: Session)
------
+ path: Path | None
	// `session.log`; none before the session has a folder
+ error_path: Path | None
	// `session.err`, which keeps the full trace of each failure
+ entries: list[LogEntry]
+ last_loop_number: int
+ latest_loop_with_entries: int
----
+ record(line: str): None
	// appends line stamped with the time
+ by(chat: ChatPointer | None): ChatLog
	// the lines one chat writes, each pointing at it; a session serves many chats at once, so it holds none
+ injected_rules: InjectedRules
	// the rules a hook gave the agent since the last line, which the next line names
+ seed_first_loop(): None
+ loop_at(number: int): Loop
+ read_loop(number: int | None): str
	// the loop with each line's transcript lines put under it
+ loop_to_note(loop: int | None): int
+ instructions(): str
	// how an agent keeps this log; sessions.switch returns it

### **ChatLog**

+ ChatLog(log: SessionLog, chat: ChatPointer | None)
------
+ chat: ChatPointer
	// `no-chat` when none is known
----
+ line(line: str): None
+ validation(worked: FidelitySessionOutput, violations: list[str]): None
+ action(action: str, paths: list[Path], worked: list[FidelitySessionOutput]): None
	// names the paths and what the practices it worked on were working at, with the injected rules
+ guidance_action(action: str, worked: list[FidelitySessionOutput]): None
	// GuidanceAction logs each action this way, with the workpath and each practice's folder as its paths
+ tool(tool_name: str, tool_input: dict): None
	// the MCP host logs each tool call this way
+ note(message: str, paths: list[Path]): None
+ append_note(note: str, loop: int | None, paths: list[str]): str
+ failure(failure: BaseException, tool: str): None
	// full trace to session.err, a line pointing at it to session.log; the failure still propagates from the caller
+ next_loop(): Loop
+ mark_loop(): int

**Invariants**

- Every line carries a timestamp and points at a chat: one noted for it, else the chat of the call the session was opened for, else the chat the environment names, else `no-chat`.
- A noted chat is used for one line only.
- A line that names rules lists only the injected rule names, sorted, by practice and fidelity, with the file that matched.
- Loop numbers are read from session.log, so numbering resumes after a switch.

### **Loop**

+ Loop(number: int, entries: list[str])
------
+ number: int
	// the marker `--- {number}`
+ entries: list[str]
	// the log lines from this marker to the next
----
+ expanded_text(): str
	// each line followed by the transcript lines its chat covers; a range shown earlier is named, not repeated

### **LogEntry**

+ LogEntry(line: str)
------
+ time: str
+ verb: str
+ words: list[str]
+ stage: str
	// the stage a `move <stage>` line names
+ loop_number: int | None
----
+ names(fidelity: FidelityGuidance): bool

### **SessionFiles**

+ SessionFiles(session: Session)
------
+ file_manager: FileManager
	// reads under the session's roots; a new one when those roots change
----
+ declared(): dict
	// the files every practice the session works on declares, by practice, fidelity, and format
+ in_folder(): list[FileEntry]
	// its log, handoffs, kept notes, and reports
+ read(path: str): FileText
+ worked_on(): set[Path] | None
	// every file when the session has a folder of its own; on the whole repository, only the files its branch changed

### **Handoffs**

+ Handoffs(folder: Path)
------
+ latest: Path | None
----
+ write(document: str): Path
	// `handoff-{timestamp}.md`

### **DecisionRecords**

+ DecisionRecords(folder: Path)
------
+ paths: list[Path]
----
+ write(slug: str, document: str): Path
	// `{NNNN}-{slug}.md`, numbered after the last record

### **PracticeSessionOutput**

+ PracticeSessionOutput(guidance: PracticeGuidance, session: Session)
------
+ name: str
	// data field
+ session: Session
+ session_file: str
	// data field
+ guidance: PracticeGuidance
	// the session's one instance of the practice, which its graph holds
+ fidelities: GuidanceCollection
+ enabled: bool
	// data field
+ working: FidelitySessionOutput | None
	// what the fidelity the practice was made at has in the session, the one that fidelity holds; none at no fidelity
+ folder: Path
	// the root chosen in session.json, else the folder config.json names, else the guidance's default folder
+ output_root: Path
	// the root chosen or configured, else the session's root
+ root: str
	// data field
+ is_root_chosen: bool
	// data field
----
+ load(session: str, practice: str, project: Path): PracticeSessionOutput
	// the `@tool_subject` of the `practice-session-output.*` tools
	-> ToolCall.session_named
	-> Session.practice
+ enable(is_enabled: bool): PracticeSessionOutput
	// MCP `practice-session-output.enable`
+ choose_root(path: str): PracticeSessionOutput
	// MCP `practice-session-output.choose_root`; refuses a `.context` folder with `PracticeRootInContextError`
+ use_default_root(): PracticeSessionOutput
	// MCP `practice-session-output.use_default_root`
+ keep_root(root: Path): None
+ of_fidelity(fidelity: FidelityGuidance): FidelitySessionOutput
	// what PracticeGuidance.work_in gives each fidelity

	// Validate logs each run this way
	-> SessionLog.line

### **FidelitySessionOutput**

+ FidelitySessionOutput(practice: PracticeSessionOutput, fidelity: FidelityGuidance)
------
+ practice: PracticeSessionOutput
	// a log line names its name and folder
+ fidelity: FidelityGuidance
	// a log line names its name and the format it works in
+ reports_folder: Path
+ root: Path
	// the fidelity's own root when session.json names one, else the practice's output root
+ kept_format: str
----
+ keep_format(format: str): None
+ output_paths(): dict[str, list[str]]
	// declared paths under the fidelity's root
+ files(): dict[str, list[FileEntry]]
	-> SessionFiles.worked_on
+ has_output(): bool

### **InjectedRules**

+ InjectedRules(log_path: Path | None)
------
+ pending: list[str]
+ text: str
----
+ note(rules: RulesCollection, matched_path: str): None
	// RulesCollection.inject_rules notes the rules a hook gave the agent, in the session folder's injected-rules.txt
+ clear(): None

**Interactions**

- A `ToolCall` asks `CallSessions` for the session of each call; the session's log lines point at that call's chat.
- `GuidanceAction.run` logs through `SessionLog.guidance_action`, and a failure through `SessionLog.failure`; the MCP host logs each tool through `SessionLog.tool` and each failure through `SessionLog.failure`.
- `Validate.validate` calls `session.log.validation` for each practice it checked. Generate and Satisfy call Validate, so their runs log the same line.
- `RulesCollection.inject_rules` notes the rules it injected on the call's session through `SessionLog.injected_rules`.
- The board reads a ticket's work through its session: `Session.practices`, `PracticeSessionOutput.fidelities`, and `FidelitySessionOutput.files`.

---

## Event map

| Event | Emitted by | Operation | Consumed by |
|-------|------------|-----------|-------------|
| — | — | — | The source names no past-tense event. The session log line is the record. |

---

## Unresolved

- **patterns** — the source names patterns and then stops. No type, property, or operation yet.

---

## Plan

The session writes its own handoffs and decision records; Sketch and GrillContext take their paths from the session. None of them opens a folder of its own.

- `Session.write_handoff` writes `handoff-{timestamp}.md` in the session's folder (`.sessions/{session}/`, or `.sessions/main/` for the main session).
- `Session.write_cdr` writes `{NNNN}-{slug}.md` under `session.work_root / .context / cdr`.
- Sketch writes `{slug}-sketch.md` under the session's root, in that folder's `.context` folder.
- GrillContext writes `grill-answers.md` in that same `.context` folder.

---

## behavior driven development:

Fidelity: behavior

The specs are `space/session/session_spec.py`, `session_log_spec.py`, `current_session_spec.py`, `handoff_spec.py`, and `decision_records_spec.py`. The outline below follows them.

### a session

#### that is new

```
-> instructions = Sessions(project).switch(name, workpath)
-> session = Sessions(project).current()
it should return how to keep its log to the agent
  -> expect(instructions).to contain "append_log"
it should keep the name, the workpath, and the repo path
  -> expect(session.name).to equal name
  -> expect(session.work_root).to equal workpath
it should write --- 1 as the first line of a new session.log
  -> expect(session.log.path).to start with "--- 1"
it should record the name in repo sessions session.json
  -> expect(Sessions(project).open_name).to equal name
```

#### that is closed

```
-> session.close()
it should go back to the main session
  -> expect(Sessions(project).open_name).to equal "main"
```

#### that is selected

##### with only a name

```
-> Sessions(project).switch(name)
it should use the workpath stored on that session
  -> expect(Sessions(project).current().root).to equal the stored workpath
```

##### with a name that has spaces and capitals

```
-> Sessions(project).switch("Pet visits")
it should name the session by its slug
  -> expect(Sessions(project).current().name).to equal "pet-visits"
```

##### from a linked worktree of the checkout whose board holds it

```
it should log into the ticket's folder on the board
  -> expect(session.session_path).to equal the main checkout's .sessions / name
```

#### that a tool call reads

```
-> session = ToolCall(project).session
it should be the main session until another is open on the repo
  -> expect(session.name).to equal "main"
it should be one object for every call, from any chat
  -> expect(ToolCall.sent({"conversation_id": "chat-2"}, project).session).to be session
it should be the same object for a call that names a folder inside the checkout
  -> expect(ToolCall(project / "docs").session).to be session
```

#### that logs an action

```
-> session.log.by(chat).action(action, paths, practices)
it should append a timestamped line that names the action and the path
  -> expect(session.log.path).to contain action and paths
```

##### with no chat known

```
it should log the action as from no chat
  -> expect(session.log.path).to contain "no-chat"
```

##### with rules injected from a inject rules hook

```
it should log that practice, fidelity, rule, and matched file
  -> expect(session.log.path).to contain the matching rule name
it should omit a rule that was not injected
  -> expect(session.log.path).not_to contain the other rule name
```

#### that logs an error

```
-> session.log.by(chat).failure(failure)
it should write the trace to session.err
  -> expect(session.log.error_path).to contain the trace
it should point the session.log line at that session.err file
  -> expect(session.log.path).to contain "session.err"
```

#### that records a loop correction note

```
-> session.append_log(call, note, loop, paths)
it should append a note line with message paths and chat pointer
  -> expect(session.log.path).to contain note, paths, and the chat
```

### a loop

#### that is opened

```
-> loop = session.log.by(chat).next_loop()
it should take the next loop number
  -> expect(loop.number).to equal the previous number plus one
it should append the loop marker to session.log
  -> expect(session.log.path).to contain "--- " + loop.number
```

#### that has log entries

```
-> entries = session.log.loop_at(number).entries
it should return the log lines for that loop number
  -> expect(entries).to equal the lines under that marker
```


### an action

#### that calls validate

```
-> session.log.by(chat).validation(session.practice(name).working, violations)
it should log that practice and that fidelity
  -> expect(session.log.path).to contain the practice and the fidelity
it should log the rule, the synopsis, and the correction
  -> expect(session.log.path).to contain each violation
```

#### that names no action

```
it should leave session.log unchanged
  -> expect(session.log.path).to equal the log from before the run
```

### a practice

#### that a practice has been invoked

```
-> session.practice(name)
it should hold that practice's guidance in memory
  -> expect(session.practice(name).guidance).to be a PracticeGuidance
it should be the one practice the session's graph holds
  -> expect(session.graph.practices.held[name]).to be session.practice(name).guidance
it should be the same practice the next call in the session works with
  -> expect(next call's session.practice(name).guidance).to be session.practice(name).guidance
it should return that same practice on the next ask
  -> expect(session.practice(name)).to be the entry from the first ask
it should list every practice CDD has, opened or not
  -> expect(session.practices.keys()).to equal PracticeCatalogue.keys()
```

##### that a person chooses a folder as the practice's root

```
-> session.practice(name).choose_root(folder)
it should write the practice's files under that folder
  -> expect(the fidelity's output paths).to start with folder
it should refuse a .context folder
  -> expect(choose_root(".context")).to raise PracticeRootInContextError
```

##### with a root a person chose for the practice

```
-> session.practice(name).keep_root(folder)
it should point that practice's folder at that folder
  -> expect(session.practice(name).folder).to equal folder
it should keep that folder in the session's session.json and nowhere else
  -> expect(repo_path / ".context" / "practices.json").not to exist
```

### a session's handoff

```
-> session.write_handoff(paths=[draft])
it should write a file named handoff-{timestamp}.md in that session's folder
  -> expect(session.handoffs.latest).to exist
it should show the handoff as its latest handoff
  -> expect(session.latest_handoff).to equal that file from the project
```
