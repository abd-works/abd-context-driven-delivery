# hooks



## Purpose



Connect Cursor IDE hook events to Python toolset methods. Authors declare handlers with `@hook`; harness deploy wires `dispatch.py` into `.cursor/hooks.json` and generates on/off slash skills for each handler.



## Primary use case



Mark a `@toolset` method with `@hook(event=...)`. On deploy, harness registers the handler, adds `dispatch.py` for that event, and writes toggle skills so the agent can enable or disable the handler without editing code.



Handlers run only when their flag file exists under `.context/hooks/`.



## Author annotation



| Annotation | Role |

|---|---|

| `@hook` / `Hook(...)` | Registers a method as a Cursor hook handler; sets `_harness_writes` so deploy discovers it |



Valid events: `CURSOR_EVENTS` in `hook.py` (`beforeSubmitPrompt`, `preToolUse`, `sessionStart`, …).



## Cursor hook output fields (definitive)



Only these fields are documented per event. `dispatch._merge_results` passes them through; other keys are ignored by Cursor.



| Event | Output fields | Notes |

|---|---|---|

| `beforeSubmitPrompt` | `continue`, `user_message` | No `agent_message` — Cursor ignores it |

| `preToolUse` | `permission`, `agent_message`, `user_message` | Used by `skill_inject.py` for edit-time context |

| `postToolUse` | `permission`, `agent_message`, `user_message` | Same shape as `preToolUse` |

| `postToolUseFailure` | `permission`, `agent_message`, `user_message` | Same shape as `preToolUse` |

| `stop` | `followup_message` | Auto-submits the next user message (e.g. ask agent to `/turn`) |

| `afterAgentResponse` | *(none documented)* | Dispatch may merge handler output; Cursor effect unverified |

| `afterAgentThought` | *(none documented)* | Same as `afterAgentResponse` |

| `sessionStart`, `sessionEnd`, `preCompact` | *(none documented)* | Mechanical scripts use `permission: allow` where applicable |



## Seam



1. **Declare** — `@hook(event="stop")` on a toolset method; body receives the Cursor stdin JSON payload and returns a hook result dict using only documented fields for that event.

2. **Bootstrap** — `dispatch.py` calls `bootstrap.load()` to import toolsets that declare handlers (currently `workspace.workspace:Turn`).

3. **Dispatch** — for each registered binding on the event, check the flag file; if enabled, instantiate the owner and call the handler; merge results. Debug trace: `primitives/hooks/dispatch.debug`.

4. **Deploy** — harness `write_deploy` calls `deploy_dispatch()` last so partial deploys do not strip dispatch wiring.



Flag path: `.context/hooks/{owner}/{method}_{event_suffix}.enabled`  

Example: `.context/hooks/turn/auto_turn_stop.enabled`



## Slash scene



Harness generates **toggle skills** per `@hook` handler (not the handler logic itself):



| Slash | What it does |

|---|---|

| `/auto_turn_stop_on` | Create flag → `Turn.auto_turn` runs on `stop` and commits dirty checkouts |

| `/auto_turn_stop_off` | Remove flag → dispatcher skips `auto_turn` |



Naming: `{operation}_{event_suffix}_{on\|off}` where `operation` is the `@hook` method name.



Related on `Turn` but **not** part of hooks — commit, not a hook toggle:



| Slash | What it does |

|---|---|

| `/turn` | Commit checkout with skill lineage (`Turn.turn`) |



## Mechanical scripts (`.cursor/hooks.json`)



These run as direct hook commands; they are **not** routed through `@hook` dispatch:



| Script | Event(s) | Role |

|---|---|---|

| `dispatch.py` | per registered `@hook` event | Route stdin to enabled handlers |

| `prompt_log/prompt_log.py` | `preToolUse`, `beforeSubmitPrompt`, `beforeReadFile`, `subagentStart` | Silent audit log (`.context/prompt-log.txt`) |

| `skill_inject.py` | `preToolUse` (Write\|StrReplace), `preCompact` | Inject skill context on edits |

| `prompt_echo/prompt_echo.py` | `preToolUse` | Dev notification when action keywords detected |



Install helpers: `install_dispatch.py`, `prompt_log/install_prompt_log.py`.



## Public API



**Decorators / registry**



- `hook`, `Hook` — register a handler

- `Hook.attach_owners`, `Hook.registered`, `Hook.bindings_for`, `Hook.is_enabled`, `Hook.set_enabled`, `Hook.toggle_flag`

- `CURSOR_EVENTS`



**Deploy**



- `HookHarness` — write or sync `hooks.json` entries (`deploy`, `sync_dispatch`)

- `HookBinding`, `hook_skill_sources`, `deploy_dispatch`



**Runtime**



- `bootstrap.load()` — populate registry before dispatch

- `dispatch.dispatch(payload)` — invoke enabled handlers for an event



## Dependencies



- **Harness** — discovers `@hook` via `_harness_writes`, emits toggle skills, calls `deploy_dispatch` on full deploy

- **Tools** — `@toolset` triggers `Hook.attach_owners` after class merge

- **Consumers** — e.g. `utilities/workspace` (`Turn.auto_turn` on `stop`)


