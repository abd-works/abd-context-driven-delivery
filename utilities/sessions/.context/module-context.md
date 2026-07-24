# sessions — module context

## Purpose

Model a named work bout (`Session`) and record append-only events for `@log`-marked tools and actions (`SessionLog`).

## Primary use case

A Context (or tool runner) binds a bout, then `@log` tools/actions append summary lines under `{session.folder}/logs/` — optionally with full request/response payloads when log control is `verbose`/`full`.

## Rationale

Keep bout identity and process-doc paths separate from the logging seam. Callers depend on small interfaces (`ISession`, `ISessionLog`). Event location is always `Session.log` when bound; tests may override with `sessions_root`.

## Layout

```
{path}/.context/sessions/{name}/
  session.md          # Start / End
  logs/               # Session.log → events.log (+ optional payload yaml)
  …
```

## Seam

- **In:** `Session` (path/name/metadata), `@log` markers, run-request `session` / `log` controls
- **Out:** `session.md`, `logs/events.log`, optional `event-*-{request,response}.yaml`

## Public API

- `ISession` / `Session` — `path`, `name`, `folder`, `log` (`folder/logs`), `session_md`, `load`, `ensure_started`, `close`, `to_dict`
- `docs_dir(destination)` — bout folder vs `{destination}/.context/`
- `ISessionLog` / `SessionLog` — singleton; `bind(Session)` or `set_session(Session | str | None)`; `apply_log_control`; `append`; `log_dir`; `session`
- `@log`, `is_logged`, `member_is_logged`, `summarize_mapping`, `inherit_*`

Run requests may set `session` and `log` (`full` | `verbose` | `off`).

Tests may pass `SessionLog(sessions_root=tmpdir)` so `log_dir = tmpdir / name`.

## Dependencies

- stdlib only for core model/log (`pathlib`, `dataclasses`, `abc`, `json`; optional `yaml` for payload dump with JSON fallback)
- Consumed by `primitives.tools`, `primitives.actions`, `context_tools.base.context`
