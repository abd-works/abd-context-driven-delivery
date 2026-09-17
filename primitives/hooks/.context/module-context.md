# hooks

## Purpose

Connect Cursor IDE hook events to Python toolset methods. Authors mark an operation with `@hook("sessionStart")` from `primitives.installer.marks`. `Installer.install` runs `HookInstallation`, which wires `dispatch.py` into `.cursor/hooks.json`.

## Author annotation

| Annotation | Role |
| --- | --- |
| `@hook("event")` | Required Cursor event name (`CURSOR_EVENTS` in `installer/marks.py`). Sets `_hook` and `_hook_name`. |

Stack on the operation (`@agent_instructions` / `@agent_tool` as needed). `@mcp` on the same member is a separate MCP install, not the hook runtime.

Valid events: `sessionStart`, `beforeSubmitPrompt`, `afterAgentResponse`, `afterAgentThought`, `stop`, `sessionEnd`, `preCompact`, `preToolUse`, `postToolUse`, `postToolUseFailure`.

## Seam

1. **Declare** — `@hook("afterAgentResponse")` on a toolset method; the body receives the Cursor stdin JSON payload.
2. **Install** — `HookInstallation` writes dispatch entries in `hooks.json` and host refs in `hook-handlers.json`.
3. **Dispatch** — for each marked method on that event, run it when `.context/hooks/{owner}/{method}_{event}.enabled` exists; merge Cursor output fields.

Flag example: `.context/hooks/turn/auto_turn_after_agent_response.enabled`

## Mechanical scripts

These run as direct hook commands; they are not `@hook` dispatch:

| Script | Role |
| --- | --- |
| `dispatch.py` | Route stdin to enabled `@hook` methods |
| `prompt_log/prompt_log.py` | Silent audit log |
| `skill_inject.py` | Inject skill context on edits |

## Public API

- Install mark: `primitives.installer.marks.hook`, `CURSOR_EVENTS`
- Installer: `HookInstallation`
- Runtime: `dispatch.dispatch`, `parse_payload`, `load_hosts`, `is_enabled`, `set_enabled`

## Dependencies

- **Installer** — discovers `_hook` via `declared_installations`
- **Consumers** — `utilities/workspace` (`Turn.auto_turn` on `afterAgentResponse`)
