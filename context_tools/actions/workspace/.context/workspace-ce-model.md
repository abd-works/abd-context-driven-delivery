# workspace

**Sources / context:** `context_tools/actions/workspace/*.py`, `.context/module-context.md`

## Workspace

+ Workspace(path)
------
+ path: str
+ workSessions: list[WorkSession]
+ currentWorkSession: WorkSession | None
+ pathOverrides: list[PathOverride]
----
+ load(): None
+ save(): Path
+ lookupPath(tool, fidelity): str | None
+ upsertPath(tool, fidelity, path, default_path): None
+ open(host, name, …): WorkSession
+ openWorkSession(name, …): WorkSession

## WorkSession

+ WorkSession(workspace, name, …)
------
+ workspace: Workspace
+ path: str
+ name: str
+ folder: Path
+ goal: str
+ fidelities: str
+ contexts: str
+ session_branch: str
+ scope_paths: list[str]
+ dirty: bool
+ git: GitRepo
+ openTurn: Turn | None
+ turns: list[Turn]
+ repairs: Repairs
----
+ open(name, goal, fidelities, contexts, path): str
+ close(outcome, handoff): Path
+ save(): None
+ load(path, name): WorkSession
+ attach_host(host): None

## PathOverride

+ PathOverride
------
+ tool: str
+ fidelity: str
+ path: str

## GitRepo

+ GitRepo(root)
------
+ root: Path
+ branch: str
----
+ checkout_or_create(branch): str
+ is_dirty(path): bool
+ commit(paths, message): str
+ push(): None
+ note(sha, fields): None
+ read_notes(sha): dict
+ find_mistakes(): list

## NullGitRepo

+ << generalization >> GitRepo

## Turn

+ Turn
------
+ workSession: WorkSession
+ prompt: str
+ result: str
+ context: str
+ commitMessage: str
+ toolCalls: list[ToolCall]
----
+ open(host): Turn
+ finish_turn(tools, prompt, result, context) @agent_tool
+ finish(prompt, result, context): TurnCommit | None
+ record_mistake(…) @agent_tool
+ record_correction(…) @agent_tool

## SessionLog

+ SessionLog
------
+ session: WorkSession
----
+ instance(): SessionLog
+ bind(session): None
+ append(toolset, name, summary, ok, error, role, payload): None

## SessionPaths

+ SessionPaths
------
----
+ docs_dir(destination): Path
