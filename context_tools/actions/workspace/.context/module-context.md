# workspace — module context

## Purpose

Named sprint + workspace kit (`Session` in `workspace_session.py`), append-only `@log` events (`SessionLog`), and `context-index.md` helpers. (`WorkspaceSession` is a back-compat alias for `Session`.)

## Primary use case

BaseContextTool holds a composed `Session` as the plain attribute `workspace` and calls **`self.open()`** once at the start of lifecycle actions. That opens path + folder + context index + eval bind together.

## Layout

```
{path}/                                 # durable tool root (session.path)
  .context/
    sessions/{name}/                    # folder (session.folder)
      session.md
      logs/
      …

{workspace_root}/.context/context-index.md
```

## Public API

- `WorkSession` — sprint record + kit: `path`, `folder`, `context_index`; `load` / `ensure_started` / `close`; tool **`open`** (sprint + index + root + eval bind); tool **`close_session`**; internal `_ensure_sprint`, `read_context_index`, `record_context_root` (called from `open`, not agent tools). Target model also has aggregate **`Workspace`** in `workspace.py` (`workSessions`, `currentWorkSession`, `pathOverrides`) — host still composes `WorkSession` today; cutover to `Workspace` is remaining.
- `GitRepo` — git working-tree collaborator at `find_git_root(...)` (`checkout_or_create`, `commit`, `push`, notes). Composed on `WorkSession.git`. Session branch naming (`session/{name}`) is **WorkSession** policy via `checkout_or_create`, not GitRepo. Starting a session refuses dirty checkout onto another branch (`DirtyBranchSwitchError`). Eval/turn finish commits via `git.commit`; it does not switch branches.
- Prose: **`workspace_session.md`** (`# Session Guidance` and tool sections) — resolved via normal `@instruction` / tool docstring lookup (`domain_slug = workspace_session`)
- `docs_dir` / `SessionPaths.docs_dir` (in `session.py`), `SessionLog`, `@log`, `ContextIndex` helpers

## Dependencies

stdlib (+ optional yaml); `tools.tool`; `eval` (EvalSession bind on open); consumed by `context_tools.base.base_context_tool`
