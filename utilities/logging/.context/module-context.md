# logging — module context

## Purpose

Consolidated session logging: **`session.yaml`** (session header + `turns[]` / `operations[]`) and **`prompt.yaml`** (prompt injection audit). Replaces `session.md` + `events.log` + scattered hook debug files.

**Sources / context:** `.context/research/cdd-logging-inventory.md` §16 (design only — not implemented).

## Seam

- Registered `@hook` handlers → **always** append `operations[]` with `source: hook` in `session.yaml`
- **Every hook logging** (all Cursor hook events via `prompt_log`) → optional, off by default → `prompt.yaml`
- Brief rows only: paths, names, param values — no payload sidecars

## Layout

```
.context/sessions/{name}/
  session.yaml
  prompt.yaml
```

## Dependencies

`utilities/workspace` (WorkSession, Turn), `primitives/hooks` (dispatch, prompt_log), `utilities/workspace/session_log.py` (legacy until migrated)
