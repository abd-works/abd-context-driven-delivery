# workspace

**Sources / context:** `context_tools/actions/workspace/*.py`, `.context/module-context.md`

## Session

+ Session(path, name, goal, fidelities, contexts, ...)
------
+ path: str
+ name: str
+ workspace_root: str
+ goal: str
+ fidelities: str
+ contexts: str
+ started: str
+ ended: str
+ outcome: str
+ handoff: str
+ body: str
+ << association >> context_index: str
+ << association >> eval: EvalSession
+ << dependency >> WorkspaceRepo
+ << dependency >> ContextIndex
----
+ load(path, name): Session
+ ensure_started(goal, fidelities, contexts): Path
+ close(outcome, handoff): Path
+ open(name, goal, fidelities, contexts, path): str
+ close_session(outcome, handoff): str
+ attach_host(host): None
+ to_dict(): dict
- _ensure_sprint(name, goal, fidelities, contexts, path): str
- _ensure_session_branch(): None
- _bind_session_log(): None
- _bind_eval(): None
- _sync_host_repairer(): None
- _write_eval_state(): None
- read_context_index(): str
- record_context_root(root, note): str

## WorkspaceSession

+ << generalization >> Session

## SessionPaths

SessionPaths
------
----
+ docs_dir(destination): Path

## ContextIndex

ContextIndex
------
----
+ context_index_path(workspace): Path
+ normalize_root_glob(root): str
+ root_glob_to_path(workspace, root_glob): str
+ path_to_root_glob(workspace, working): str
+ read_entries(workspace): dict
+ lookup_root(workspace, tool_key): str | None
+ upsert_entry(workspace, tool_key, root_glob, note): Path
+ render_index(entries, log_lines): str

## WorkspaceRepo

+ WorkspaceRepo(root)
------
+ root: Path
----
+ ensure_session_branch(session_name): str
+ commit_on_session_branch(paths, message): str
+ current_commit(): str
+ current_branch(): str
+ is_dirty(path): bool

## NullWorkspaceRepo

+ << generalization >> WorkspaceRepo

## SessionLog

+ SessionLog
------
----
+ bind(session): None
+ append(event): None
