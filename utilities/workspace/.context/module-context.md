# workspace — module context

## Purpose

**Workspace** aggregate (`workspace.py`): parent of `.context/`, owns many **WorkSession**s,
**currentWorkSession**, and **pathOverrides**. **GitRepo** is the git collaborator on
`WorkSession.git`. **SessionLog** records expand|run trails explicitly (not via `@log`).

## Primary use case

`BaseContextTool.workspace` is a **Workspace**. Opening a sprint calls
`Workspace.open_work_session(...)` → sets `currentWorkSession`. Turn/git go through
`currentWorkSession` (`openTurn`, `git`).

## Layout

```
{workspace.path}/                       # Workspace.path — parent of .context/
  .context/
    context-index.md                    # PathOverride persistence
    sessions/{name}/                    # WorkSession.folder
      session.md
      session.yaml                      # bootstrap only (not mistake index)
      logs/events.log
```

## Public API

- `Workspace` — `@toolset` (`workspace.workspace:Workspace`); `open` is `@agent_tool`;
  `path`, `work_sessions`, `current_work_session`, `path_overrides`;
  `load` / `save` / `lookup_path` / `upsert_path` / `open_work_session`
- `WorkSession` — `@toolset` (`workspace.workspace:WorkSession`); CLI context is
  `workspace` path + `session` name (same as `Turn`; session may come from the current
  `session/` git branch). OO callers still pass a `Workspace` object + name.
  Owns `git`, `open_turn`, `turns`, `repairs`, trail; session.md kit
  (`ensure_started`, `close`, `close_session`, context index helpers).
  `close` writes End, commits `session.md` if dirty, then
  `git.branch_named(default_branch).checkout()` (`main`);
  `start_work_session` / `finish_work_session` `@agent_tool` with `@prompt` names
  `start-work-session` / `finish-work-session` (`tool:` invoke, not `action:`)
- `SessionPaths` / `docs_dir` — sprint folder vs `{destination}/.context/`
- `GitRepo` / `NullGitRepo` — `checkout_or_create`, `commit`, `push`, notes (`note` /
  `read_notes` / `find_mistakes`). Session branch naming is WorkSession policy.
- `Turn` — `@agentic_toolset` (`workspace.workspace:Turn`); CLI context is `workspace` path + `session` name (session may come from the current `session/` git branch). Host is optional (`if host:` for bind/index/trail). Owns `mistakes` and optional `correction`; `record_mistake` / `record_correction` attach to the open turn before `finish`. `open` / `finish_turn` stay `@agent_tool` (`/start-turn`, `/finish-turn`). `performTurn` is `@agent_instructions` with `@prompt(name="turn")` so `/turn` invokes `action: performTurn` (open, do the work in context, `finish_turn`).
- `Turn` / `Mistake` / `Correction` / `PathOverride` / `ToolCall` / `TurnCommit`
  (`TurnCommit.name` = git commit subject from `Turn.name`, not a uuid slug)
- `SessionLog` — `append` → events.log + openTurn.toolCalls; **delete `@log` as host primary**
- `ContextToolHost` — OO host used by `workspace_spec` (production host is `BaseContextTool`)

## Dependencies

stdlib (+ optional yaml); `tools.tool`;
consumed by `context_tools.base.base_context_tool`
