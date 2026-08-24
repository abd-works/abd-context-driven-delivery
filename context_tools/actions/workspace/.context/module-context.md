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

- `Workspace` — `path`, `work_sessions`, `current_work_session`, `path_overrides`;
  `load` / `save` / `lookup_path` / `upsert_path` / `open_work_session`
- `WorkSession` — back-ref `workspace`; owns `git`, `open_turn`, `turns`, `repairs`, trail;
  session.md kit (`ensure_started`, `close`, `close_session`, context index helpers)
- `GitRepo` / `NullGitRepo` — `checkout_or_create`, `commit`, `push`, notes (`note` /
  `read_notes` / `find_mistakes`). Session branch naming is WorkSession policy.
- `Turn` / `Mistake` / `Correction` / `PathOverride` / `ToolCall` / `TurnCommit`
- `SessionLog` — `append` → events.log + openTurn.toolCalls; **delete `@log` as host primary**
- `ContextToolHost` — OO host used by `workspace_spec` (production host is `BaseContextTool`)

## Dependencies

stdlib (+ optional yaml); `tools.tool`;
consumed by `context_tools.base.base_context_tool`
