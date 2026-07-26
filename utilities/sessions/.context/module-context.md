# sessions — module context

## Purpose

Named sprint (`Session`), append-only `@log` events (`SessionLog`), workspace binding for BaseContextTool (`WorkspaceSession`), and workspace `context-index.md` helpers.

## Primary use case

- Primitives / utilities: bind a sprint; `@log` tools append under `{session.folder}/logs/`.
- BaseContextTool: inherit `WorkspaceSession` for `workspace` / `path` / `session`, `create_session` / `close_session`, and context-index tools.

## Rationale

One package: sprint model + logging + the BaseContextTool base that exposes them. Primitives import `Session` / `SessionLog` / `@log` without taking a second top-level package for the same concept.

## Layout

```
{path}/.context/sessions/{name}/
  session.md          # Start / End
  logs/               # Session.log → events.log (+ optional payload yaml)
  …

{workspace}/.context/context-index.md   # tool = ./root/* entries
```

## Seam

- **In:** `Session` (path/name/metadata), `@log` markers, run-request `session` / `log` controls; constructor `workspace` / `path` / `session`
- **Out:** `session.md`, `logs/events.log`, optional payload yaml; `context-index.md`

## Public API

- `ISession` / `Session` — `path`, `name`, `folder`, `log`, `session_md`, `load`, `ensure_started`, `close`, `to_dict`
- `docs_dir(destination)` — sprint folder vs `{destination}/.context/`
- `ISessionLog` / `SessionLog` — singleton; `bind` / `set_session`; `apply_log_control`; `append`; `log_dir`
- `@log`, `is_logged`, `member_is_logged`, `summarize_mapping`, `inherit_*`
- `WorkspaceSession` — BaseContextTool base: `session` resource, `session_guidance` instruction, tools `create_session` / `close_session` / `read_context_index` / `record_context_root` (prose sections in `sessions.md`)
- `context_index` helpers — `lookup_root`, `upsert_entry`, …

Run requests may set `session` and `log` (`full` | `verbose` | `off`).

Tests may pass `SessionLog(sessions_root=tmpdir)` so `log_dir = tmpdir / name`.

## Dependencies

- Core model/log: stdlib (+ optional `yaml`)
- `WorkspaceSession`: `tools.tool` (`@tool` / `@resource`)
- Consumed by `primitives.tools`, `primitives.actions`, `context_tools.base.base_context_tool`
