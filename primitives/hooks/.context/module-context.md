# hooks

Object model: [hooks-runtime-model.md](hooks-runtime-model.md)

## Purpose

Connect Cursor IDE hook events to Python toolset methods. Authors mark an operation with `@hook("sessionStart")` from `primitives.installer.marks`. `Installer.install` runs `HookInstallation`, which wires `dispatch.py` into `.cursor/hooks.json`.

## Author annotation

| Annotation | Role |
| --- | --- |
| `@hook("event")` | Required Cursor event. Sets `_hook` and `_hook_name`. Opt-in via `.enabled` flag. |
| `@hook("event", always=True)` | Same mark; runs unless a `.disabled` flag exists. |

Valid events include `CURSOR_EVENTS` in `installer/marks.py` (`sessionStart`, `beforeSubmitPrompt`, `beforeReadFile`, `subagentStart`, `preToolUse`, …).

## Hosts

| Toolset | Events | Role |
| --- | --- | --- |
| `Turn` | `afterAgentResponse` | Auto-commit when the enable flag exists |
| `PromptLog` | `beforeSubmitPrompt`, `beforeReadFile`, `preToolUse`, `subagentStart`, `afterAgentResponse` | Audit log (`always=True`) |
| `SkillInject` | `preToolUse`, `preCompact` | Skill digest on edits (`always=True`) |
| `PromptEcho` | `preToolUse` | Action-name echo; no-op if `.context/hooks/prompt_echo.disabled` exists |

## Seam

1. **Declare** — `@hook` on a toolset method; body receives Cursor stdin JSON.
2. **Install** — `HookInstallation` writes dispatch entries in `hooks.json` and refs in `hook-handlers.json`.
3. **Dispatch** — `dispatch.py` is only the Cursor process: parse stdin, call marked methods, merge output fields.

Flag example (opt-in): `.context/hooks/turn/auto_turn_after_agent_response.enabled`

## Public API

- Install mark: `primitives.installer.marks.hook`, `CURSOR_EVENTS`
- Installer: `HookInstallation`
- Runtime: `dispatch.dispatch`, `parse_payload`, `load_hosts`, `is_enabled`, `set_enabled`
