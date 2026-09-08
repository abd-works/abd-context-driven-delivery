# Logging

Session-scoped consolidated logging under `.context/sessions/{name}/`.

## Files

| File | Contents |
|------|----------|
| `session.yaml` | Session header + `turns[]` with `operations[]` |
| `prompt.yaml` | Prompt injection audit (skills, rules, agents, dynamic prompts) |

## Operation sources

| `source` | When |
|----------|------|
| `hook` | Registered `@hook` handler ran — **always logged** |
| `agentic tool call` | `@agent_instructions` expand or agent recipe tool |
| `direct invoke` | Explicit run / `SessionLog.append` in recipe |

## Every hook logging

Optional audit of all Cursor hook events. Off by default. Registered hooks still land in `session.yaml` when every hook logging is off.

**Sources / context:** `.context/research/cdd-logging-inventory.md` §16
