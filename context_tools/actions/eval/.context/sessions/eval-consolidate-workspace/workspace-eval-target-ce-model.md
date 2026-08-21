# workspace-eval-target

**Sources / context:** `workspace-eval-oo-sketch.md` §4 target object graph (eval-consolidate-workspace session). Not current code.

## BaseContextTool

+ BaseContextTool
------
+ << composition >> workspace: WorkSession
+ << association >> turn: Turn
----
+ generate(): str
+ validate(): str
+ document(paths): str
+ satisfy(): str
+ scan(paths): str

## WorkSession

+ WorkSession(path, name, goal, fidelities, contexts, ...)
------
+ path: str
+ name: str
+ folder: Path
+ goal: str
+ fidelities: str
+ contexts: str
+ session_branch: str
+ scope_paths: list[str]
+ dirty: bool
+ << composition >> git: GitRepo
+ << association >> openTurn: Turn | None
+ << composition >> turns: list[Turn]
+ << composition >> repairs: list[Repair]
+ << dependency >> ContextIndex
+ << dependency >> SessionPaths
----
+ open(name, goal, fidelities, contexts, path): str
+ close(outcome, handoff): Path
+ save(): None
+ load(path, name): WorkSession

## Turn

+ << generalization >> AgenticToolset
+ Turn(workSession)
------
+ workSession: WorkSession
+ prompt: str
+ result: str
+ context: str
+ commitMessage: str
+ << composition >> toolCalls: list[ToolCall]
+ << composition >> mistakes: list[Mistake]
+ changeCommit: TurnCommit | None
----
+ open(host): Turn
+ finish_turn(tools, prompt, result, context): None
+ finish(prompt, result, context): TurnCommit | None
+ record_mistake(tools, artifact, rule, wrong, original, tool, fidelity): None
+ record_correction(tools, entry_id, improved, how, status): None

## GitRepo

+ GitRepo(root)
------
+ root: Path
+ branch: str
+ current_branch: str
+ current_commit: str
----
+ create_branch(branch): None
+ checkout_or_create(branch): None
+ is_dirty(scope_paths): bool
+ commit(paths, message): str
+ push(): None

## SessionLog

+ SessionLog
------
+ << association >> session: WorkSession
----
+ bind(session): None
+ append(toolset, name, summary, ok, error, role, payload): None

## ToolCall

+ ToolCall
------
+ toolset: str
+ name: str
+ summary: str
+ ok: bool
+ error: str | None
+ role: str | None

## TurnCommit

+ TurnCommit
------
+ turnId: str
+ sessionName: str
+ toolNames: list[str]
+ mistakeIds: list[str]
+ sha: str

## ContextIndex

+ ContextIndex
------
----
+ lookup_root(workspace, tool_key): str | None
+ upsert_entry(workspace, tool_key, root_glob, note): Path

## SessionPaths

+ SessionPaths
------
----
+ docs_dir(destination): Path

## Mistake

+ Mistake
------
+ entry_id: str
+ artifact: str
+ rule: str
+ theme: str
+ << association >> repair: Repair | None
+ << association >> correction: Correction | None
----
+ persist(workSession): None

## Correction

+ Correction
------
+ improved: str
+ how: str
+ status: str
+ fixedIn: Turn | None
+ << composition >> mistakes: list[Mistake]
----
+ add(mistake): None
+ persist(workSession): None

## Repair

+ Repair
------
+ theme: str
+ status: str
+ << composition >> mistakes: list[Mistake]
+ << association >> correction: Correction | None
+ << association >> tools_git: GitRepo | None
----
+ open(host, asset, violation): None
+ verify_fix(): None
+ nest(mistakes): None
+ finish(turn): None

## Improvement

+ << generalization >> AgenticToolset
+ Improvement
------
----
+ repair(tools, asset, violation): None
+ verify_fix(tools, theme): None
