# hooks

Object model: [hooks-runtime-model.md](hooks-runtime-model.md)

## Purpose

Connect Cursor IDE hook events to Python toolset methods. Authors mark an operation with `@hook("sessionStart")` from `installation.marks`. `Installer.install` runs `HookInstallation`, which wires `hook_server.py` into `.cursor/hooks.json`.

## Author annotation

| Annotation | Role |
| --- | --- |
| `@hook("event")` | Required Cursor event on an operation. Sets `_hook` and `_hook_name`. |
| `@hooks(disabled=True)` | Class annotation. Skips every hook on that toolset. |

Valid events include `CURSOR_EVENTS` in `installer/marks.py` (`sessionStart`, `beforeSubmitPrompt`, `beforeReadFile`, `subagentStart`, `preToolUse`, …).

## Toolsets

| Toolset | Events | Role |
| --- | --- | --- |
| `Turn` | `afterAgentResponse` | Auto-commit; `@hooks(disabled=True)` |
| `PromptLog` | `beforeSubmitPrompt`, `beforeReadFile`, `preToolUse`, `subagentStart`, `afterAgentResponse` | Audit log |
| `PromptEcho` | `preToolUse` | Action-name echo; `@hooks(disabled=True)` |

Dispatch puts each handler’s `tool.docstring` on the merged event as `agent_message`.

## Seam

1. **Declare** — `@hook` on a toolset method; body receives Cursor stdin JSON.
2. **Install** — `HookInstallation` writes dispatch entries in `hooks.json` and refs in `hook-handlers.json`.
3. **HookServer** — Cursor’s stdin process; loads the catalog, runs enabled handlers, and merges one `HookResult`.

Disable example: `@hooks(disabled=True)` on `Turn` and `PromptEcho`.

## Public API

- Install mark: `installation.marks.hook`, `CURSOR_EVENTS`
- Installer: `HookInstallation`
- Runtime: `HookServer`, `HookPayload`, `HookResult`, `HandlerCatalog`, `HookHandler`
