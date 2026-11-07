# harness/hooks
*Hook* lets a toolset member run when the IDE fires a named event, such as `sessionStart`, `preToolUse`, or `afterAgentResponse`: the author types `@Hook("preToolUse")` on the member, the member receives the event's payload, and it returns the fields the IDE reads (`permission`, `continue`, `user_message`, `agent_message`, `additional_context`). Every hook on the same event runs, and the IDE gets one merged answer. `@Hook("event", disabled=True)` turns one member off; `@Hooks(disabled=True)` above `@agent_toolset` turns off every hook on that class.
*HookInstallation* is how `/install` publishes hooks: it records each hooked member and points every event it uses at the hook server. `@Hook` and `@mcp` on the same member are two separate publications.
*HookServer* is the long-running process that answers every hook call for one repository and keeps that repository's current session between calls; *HookDaemon* finds, starts, and checks it, so health reports and the MCP server can ask whether it is running.
*SessionLogs* names the active session's folder and the hook logs under `.sessions/{name}/logs/`, so every hook writes its log in the same place. *RunningProcess* is a process on this computer by its id, asked whether it is still running; the hook server's lock file, the daemons' address files, and `scripts/instances.py` name processes this way.

- **Purpose:** Let a toolset member answer IDE events, and keep one hook server per repository that runs every hooked member and merges their answers.
- **Seam (terms):** Hook, Hooks, HookInstallation, HookServer, HookDaemon, SessionLogs, RunningProcess; the marks `@Hook("event")` and `@Hooks(disabled=True)`
- **Dependencies (one-way):** harness/agent_tools, harness/installation (*Destination*, *Installation*), space/session (the hook server holds the repository's current session), space/context_config (which guideline applies to an edited file). harness/agent_tools, harness/installation, and space/session import this module back, so it sits in their dependency cycle (`.sessions/_backlog/break-module-dependency-cycles.md`).

## Constraint

Name the event exactly as the IDE does; it must be one of `Hook.EVENTS`, and an unknown name fails when the class is decorated, so a misspelled hook never installs silently. A disabled hook returns nothing, even when another operation calls it directly. Do not start the hook server by hand: the installed hook command and `HookDaemon` start it, and a second start finds the first through its lock file.
