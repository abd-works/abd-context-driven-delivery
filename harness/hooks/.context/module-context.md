## Language

*Hook* is an operation Cursor may call when a named IDE event fires. The author marks the member; install writes Cursor’s hook files; Cursor starts `hook_server.py` with stdin JSON and gets one merged result.

Object model: [hooks-runtime-model.md](hooks-runtime-model.md). Toast work lives in [tools/prompt_echo](../../tools/prompt_echo/.context/module-context.md).

### Hook

- Put `@Hook("sessionStart")` (or `hook`) on a toolset member so that Cursor event runs the method.
- The body receives the event payload and returns the fields Cursor reads (`permission`, `continue`, `user_message`, `agent_message`, `followup_message`, `additional_context`).
- **Invariant:** the event string is one of `Hook.EVENTS`. Unknown names fail at decoration.

### Hooks

- Put `@Hooks(disabled=True)` above `@agent_toolset` to skip every hook on that class. PromptLog uses this today; PromptEcho does not.

### HookInstallation

- `Installer.install` walks marked members here. The writer records handlers and points each distinct event at `hook_server.py`.
- `@Hook` and `@mcp` on the same operation stay two independent installs.

### HookServer

- Cursor’s stdin process for every hooked event. Authors do not start it by hand; install wires the command.

Build order: `installation` → `harness/hooks`

---

# harness/hooks
- **Purpose:** Mark a member `@Hook("event")` so Cursor stdin events run that Python and return one merged result.
- **Seam (terms):** Hook, Hooks, HookInstallation, HookServer, SessionLogs, HookDaemon
- **Dependencies (one-way):** `installation` (*Destination*, *Installation*), `harness/agent_tools`

## Constraint

The event name is the Cursor event (`sessionStart`, `preToolUse`, …) from `Hook.EVENTS` in `harness.hooks.hooks`. `@Hooks(disabled=True)` on a toolset skips every hook on it. *Echo* / *PromptEcho* live in `tools/prompt_echo`.
