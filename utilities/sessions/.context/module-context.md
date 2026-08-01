# sessions — module context

## Purpose

Named sprint + workspace kit (`Session` in `workspace_session.py`), append-only `@log` events (`SessionLog`), and `context-index.md` helpers. (`WorkspaceSession` is a back-compat alias for `Session`.)

## Primary use case

BaseContextTool holds a composed `Session` via `workspace()` and calls **`self.workspace().open()`** once at the start of lifecycle actions. That opens path + folder + context index together.

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

- `Session` — sprint record + kit: `path`, `folder`, `context_index`; `load` / `ensure_started` / `close`; action **`open`**; tools `ensure_session` / `create_session` / `close_session` / `read_context_index` / `record_context_root`
- Prose: **`workspace_session.md`** (`# Session Guidance` and tool sections) — resolved via normal `@instruction` / tool docstring lookup (`domain_slug = workspace_session`)
- `docs_dir` (in `session.py`), `SessionLog`, `@log`, context_index helpers

## Dependencies

stdlib (+ optional yaml); `tools.tool`; consumed by `context_tools.base.base_context_tool`
