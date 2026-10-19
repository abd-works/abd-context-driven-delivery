---
fidelity: [model, behavior]
artifact: [ce-domain-model, bdd-behavior]
format: md
---

# Session

**Sources / context:** `space/session/session-context.md`

**Module:** `space/session`

Session owns session logging for the host. The host keeps one Session and sets it whenever a session is opened or created. `new` and `select` are instructions: the code section binds the session, and the instructions section returns `keep_log` to the agent. `new` requires the name, the work path, and the repo path, and places logging at `repo_path/sessions/{name}`. `select` opens a session that already exists. There `name` is enough, and any one of the paths fills in the other two from that session or from the environment.

`patterns` in the source stops at the word pattern. That concept stays unresolved.

---

## clean engineering:

Session and its loops

A Session binds the paths, the repo, and the active guidelines. Each entry pairs one practice guideline with that practice's graph. The graph root points at the parent folders where that practice's tree lives. A Loop is one discrete span of context, generation, and evaluation inside that session, so a later pass can take that span of the log and evaluate it on its own.

### **Session**

+ new(name: str, workpath: Path, repo_path: Path): str
	Instructions
	-> keep_log()
	// returned to the agent when this session opens
	Code
	// binds this session; the host keeps it
	// name, workpath, and repo_path are required
	// session_path is repo_path / "sessions" / name
	// reads repo_path / ".context" / "practices.json" when that file exists
	// does not open a practice; practice(name) opens that practice the first time it is asked for
------
+ workpath: Path
	// folder where work is generated and read
+ repo_path: Path
	// repo being worked in
+ name: str
	// session-name
+ session_path: Path
	// logging and other session artifacts that are not permanent; repo_path / "sessions" / name
+ repo: Repo
	// << association >> Repo opened on repo_path
+ practices: list[Practice]
	// empty until a practice is asked for
	// one entry per practice that has been asked for, and only in memory
+ practice(name: str): Practice
	// creates that practice's guideline and that practice's graph together on the first ask
	// a later ask for the same name returns that same entry
	// the graph root points at the parent folders where that practice's tree lives
	// one practice can name more than one set of peer folders
	// the default set is the folders the practice already declares
	// a set that is not that default is stored in repo_path / ".context" / "practices.json"
	// PracticeGuidance does not load the graph; this operation builds both
+ loops: list[Loop]
	// << composition >> a loop has no session outside this one
----
+ select(name: str, workpath: Path | None, repo_path: Path | None, session_path: Path | None): str
	Instructions
	-> keep_log()
	// returned to the agent when this session is selected
	Code
	-> resolve(name, workpath, repo_path, session_path)
	// opens the session that already has this name
	// name is required; the paths are optional because that session already holds them
	// reads repo_path / ".context" / "practices.json" when that file exists
	// does not open a practice; practice(name) opens that practice the first time it is asked for
- resolve(name: str, workpath: Path | None, repo_path: Path | None, session_path: Path | None): Session
	-> Repo.find_root
	// a given session_path: open that session; workpath is the path stored on it; repo_path is the git root of that folder
	// a given repo_path: session_path is repo_path / "sessions" / name; open that session and read workpath from it
	// a given workpath: repo_path is Repo.find_root(workpath); session_path is repo_path / "sessions" / name
	// none given: repo_path is CDD_REPO, or Repo.find_root of the current directory; workpath is CDD_PROJECT, or the current directory; session_path is repo_path / "sessions" / name; a workpath already stored on that session replaces the environment workpath
	// a path that was passed is kept; the other two are filled from it
+ loop(): Loop
	// increments the loop number and appends a `--- {number}` line to session.log
+ log_action(action: str, paths: list[Path]): None
	-> Loop.entries
	// one timestamped line on session_path / "session.log" for this action
	// the line names the files and folders in paths, the active guidelines, fidelity, format, and action
	// the line names the highest graph node per practice when the graph has one
	// the line points at the chat id, transcript file, and line numbers; it does not copy the transcript
	// when a practice guideline's rules were injected, the line lists those rule names only, sorted, separated by that practice and fidelity, and the file that matched the glob
+ log_validation(guidance: PracticeGuidance, violations: list[str]): None
	// one timestamped line on session_path / "session.log"
	// the line names the practice, the fidelity, and the rules that were run
	// each violation names the exact rule, a synopsis of the code, and the reported correction
+ log_error(failure: BaseException): None
	// writes the full trace to session_path / "session.err"
	// appends a session.log line that points at that session.err line
	// the failure still propagates
+ append_chat(action: str, chat_file: Path): None
	// adds that chat's id, file name, and line numbers onto the log line for that action
	// a validation correction is one use; any logged action can receive a later chat the same way
+ keep_log(): str
	Instructions
	// the shared instructions new and select both return
	// log_action, log_validation, and log_error already run: an action logs itself, validate logs the run, an error logs the trace
	// reuse those operations, and append_chat, when a log line misses the chat or a detail that belongs to it
	// keep the log current with the relevant chat and with changes in the details
	Code
	// returns this instructions text

**Invariants**

- new keeps the name, workpath, and repo_path it was given, and sets session_path to repo_path / "sessions" / name.
- A path passed to select is kept. The other two paths are filled from the session that already exists, or from the environment when none were passed.
- A log line is written only after workpath, repo_path, and session_path are set.
- session.log and session.err stay under session_path.
- log_error records the trace and still raises the same failure.
- practices hold only practices asked for on this session, and only in memory. Each entry is that practice's guideline and that practice's graph, created together.
- A practice graph root uses the practice's default folders unless practices.json names other parent folders for that practice.
- practices.json stores only the practices whose parent folders are not the default.
- A log line that mentions rules names those rules only, sorted, and separated by the practice guideline and fidelity whose glob matched the edit.

**Interactions**

- select asks resolve for the paths. resolve asks Repo.find_root for the git root, and reads a stored workpath from the session at session_path. new does not resolve.
- repo is the Repo for repo_path.
- practice(name) builds that practice's guideline and that practice's graph together. The graph root points at that practice's parent folders. The default folders come from the practice. new and select read repo_path / ".context" / "practices.json" and practice(name) uses a saved set when that practice is listed there.
- A practice guideline's rules carry a glob. inject_rules runs for content that has been edited. The edit matches the glob and those rules are injected. An edit that misses the glob injects nothing from that guideline.
- log_action records the injected rule names for that practice guideline and fidelity.
- Validate.validate calls log_validation. Generate and Satisfy call Validate.validate, so those runs are the same line. Iterate tells the agent to validate and does not call Validate. Sketch does not call Validate.
- GuidanceAction.run calls log_action for the action it is running.
- new and select each run a code section and return keep_log. keep_log is the one instruction set both of them return.
- keep_log tells the agent that log_action, log_validation, and log_error already run, and that append_chat may attach a later chat when those miss the chat or a detail.
- append_chat points at the transcript file. The transcript stays the chat record; the session log is the trail.

### **Loop**

+ Loop(number: int)
------
+ number: int
	// the loop marker written as `--- {number}`
+ entries: list[str]
	// the session.log content from lines that belong to this loop
----
+ inject(chat_file: Path): None
	// places the chat and the response under the entries they belong to
	// each of those lines records the chat id, the file name, and the line numbers

**Invariants**

- number increases by one from the previous loop on this session.
- entries are only the log lines between this loop's marker and the next marker.

**Interactions**

- inject reads the transcript at chat_file and asks append_chat to point at that file. The transcript is not copied into session.log.

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

Handoff, Sketch, and GrillContext take their paths from the host Session. They do not open a workspace of their own.

- Handoff writes `handoff-{timestamp}.md` in `session.session_path`.
- Sketch writes `{slug}-sketch.md` under the session work path, in that path's `.context` folder.
- GrillContext writes `grill-answers.md` in that same `.context` folder.

`tools/workflow/workflow.py` and `tools/plan/plan.py` are retired at `retired/` and stay out of package discovery, toolset collection, and the graph walk.

---

## behavior driven development:

Fidelity: behavior

### a session

```
-> instructions = new Session(name, workpath, repo_path)
// session is the session that code bound; the host keeps it
// instructions are keep_log
```

#### that is new

```
it should return keep_log to the agent
  -> expect(instructions).to contain "log_action"
  -> expect(instructions).to contain "log_validation"
  -> expect(instructions).to contain "log_error"
  -> expect(instructions).to contain "append_chat"
it should keep the name, the workpath, and the repo path the code section set
  -> expect(session.name).to equal name
  -> expect(session.workpath).to equal workpath
  -> expect(session.repo_path).to equal repo_path
it should keep logging under that repo at sessions and the name
  -> expect(session.session_path).to equal repo_path / "sessions" / name
it should leave practices empty until a practice is asked for
  -> expect(session.practices).to equal []
```

#### that is selected

```
-> instructions = session.select(name)
it should return the logger instructions to the agent
  -> expect(instructions).to contain "log_action"
  -> expect(instructions).to contain "log_validation"
  -> expect(instructions).to contain "log_error"
  -> expect(instructions).to contain "append_chat"
it should leave practices empty until a practice is asked for
  -> expect(session.practices).to equal []
```

##### with only a name

```
-> session.select(name)
it should bind the existing session from the environment
  -> expect(session.name).to equal name
  -> expect(session.repo_path).to equal the repo root
  -> expect(session.session_path).to equal session.repo_path / "sessions" / name
it should use the workpath stored on that session
  -> expect(session.workpath).to equal the workpath stored on the session
```

##### with a repo path

```
-> session.select(name, repo_path=repo_path)
it should keep logging under that repo at sessions and the name
  -> expect(session.session_path).to equal repo_path / "sessions" / name
it should read the workpath from that session
  -> expect(session.workpath).to equal the workpath stored on the session
```

##### with a session path

```
-> session.select(name, session_path=session_path)
it should read the repo path and the workpath from that session
  -> expect(session.repo_path).to equal the git root of session_path
  -> expect(session.workpath).to equal the workpath stored on the session
```

##### with a workpath

```
-> session.select(name, workpath=workpath)
it should keep the given workpath
  -> expect(session.workpath).to equal workpath
it should take the repo root from that workpath
  -> expect(session.repo_path).to equal the git root of workpath
  -> expect(session.session_path).to equal session.repo_path / "sessions" / name
```

#### that logs an action

##### with paths passed in

```
-> session.log_action(action, paths)
it should append a timestamped line to session.log
  -> expect(session.session_path / "session.log").to contain the timestamp
  -> expect(session.session_path / "session.log").to contain paths
it should name the guideline, fidelity, format, and action on that line
  -> expect(session.session_path / "session.log").to contain action
```

##### with a graph node known for the practice

```
-> session.log_action(action, paths)
it should name the highest graph node for that practice
  -> expect(session.session_path / "session.log").to contain the node name
```

##### with rules injected from a inject rules hook

```
it should log the matching rule names only, sorted, under that practice and fidelity
  -> expect(session.session_path / "session.log").to contain the matching practice
  -> expect(session.session_path / "session.log").to contain the matching fidelity
  -> expect(session.session_path / "session.log").to contain the matching rule name
it should omit the other practice guideline
  -> expect(session.session_path / "session.log").not_to contain the other rule name
```

##### with a chat transcript

```
-> session.log_action(action, paths)
it should point at the chat id, the transcript file, and the line numbers
  -> expect(session.session_path / "session.log").to contain the chat file
```

#### that logs an error

```
-> session.log_error(failure)
it should write the full trace to session.err
  -> expect(session.session_path / "session.err").to contain the trace
it should point the session.log line at that session.err line
  -> expect(session.session_path / "session.log").to contain the session.err line
it should still raise the failure
  -> expect(session.log_error(failure)).to raise failure
```

### a loop

#### that is opened

```
-> loop = session.loop()
it should take the next loop number
  -> expect(loop.number).to equal the previous number plus one
it should append the loop marker to session.log
  -> expect(session.session_path / "session.log").to contain "--- " + loop.number
```

#### that has log entries

```
-> entries = session.loops[number].entries
it should return the log lines for that loop number
  -> expect(entries).to equal the lines under that marker
```

##### with a chat to place under the lines

```
-> session.loops[number].inject(chat_file)
it should show the chat and the response under the lines they belong to
  -> expect(session.loops[number].entries).to contain the chat
  -> expect(session.loops[number].entries).to contain the response
```

### an action

#### that calls validate

##### with a practice and a fidelity

```
-> session.log_validation(guidance, violations)
it should log that practice, that fidelity, and the rules that were run
  -> expect(session.session_path / "session.log").to contain the practice
  -> expect(session.session_path / "session.log").to contain the fidelity
  -> expect(session.session_path / "session.log").to contain the rule names
```

##### with a violation

```
-> session.log_validation(guidance, violations)
it should log the exact rule, a synopsis of the code, and the reported correction
  -> expect(session.session_path / "session.log").to contain the rule
  -> expect(session.session_path / "session.log").to contain the synopsis
  -> expect(session.session_path / "session.log").to contain the correction
```

#### that appends a chat to a logged action

```
-> session.append_chat(action, chat_file)
it should add that chat's id, file, and line numbers onto that action's log line
  -> expect(session.session_path / "session.log").to contain the chat
```

##### with a validation line

```
-> session.append_chat(action, chat_file)
it should add that chat onto the validation line
  -> expect(session.session_path / "session.log").to contain the chat
  -> expect(session.session_path / "session.log").to contain the correction
```

#### that is annotated with log

```
-> action.run(guidance)
it should log that action and the paths it was given
  -> expect(session.session_path / "session.log").to contain the action
```

#### that is not annotated with log

```
-> action.run(guidance)
it should leave session.log unchanged
  -> expect(session.session_path / "session.log").to equal the log from before the run
```

### a practice

#### that a practice has been invoked

```
-> session.practice(name)
it should hold that practice's guideline and graph in memory
  -> expect(session.practice(name).guideline).to be that practice guideline
  -> expect(session.practice(name).graph).to be that practice graph
it should return that same practice on the next ask
  -> expect(session.practice(name)).to be the entry from the first ask
it should leave the other practices unopened
  -> expect(session.practices).to contain only that practice
```

##### with the practice default folders

```
it should point that practice's graph root at the folders the practice declares
  -> expect(the practice graph root folders).to equal the practice default folders
it should leave that practice out of practices.json
  -> expect(repo_path / ".context" / "practices.json").not_to contain the practice
```

##### with parent folders that are not the default

```
it should point that practice's graph root at those parent folders
  -> expect(the practice graph root folders).to equal the saved parent folders
it should save those folders in practices.json
  -> expect(repo_path / ".context" / "practices.json").to contain the practice
  -> expect(repo_path / ".context" / "practices.json").to contain the saved parent folders
```

##### with more than one set of peer folders

```
it should keep each set of peer folders on that practice's graph root
  -> expect(the practice graph root folders).to equal those sets of peer folders
it should save each set that is not the default
  -> expect(repo_path / ".context" / "practices.json").to contain each non-default set
```

#### with harness/guidance as the tree for clean engineering, stories, and bdd

```
-> session.practice("clean_engineering")
-> session.practice("stories")
-> session.practice("bdd")
it should load the clean engineering, stories, and bdd graphs from harness/guidance
  -> expect(each asked practice graph root).to equal harness/guidance
it should finish that load within 5 seconds
  -> expect(the load).to take at most 5 seconds
```

#### that a practice has not been invoked

```
-> session.practices
it should omit that practice's entry
  -> expect(session.practices).to equal []
```
