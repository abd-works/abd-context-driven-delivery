# harness/hooks
*Hook* lets a toolset member run when the IDE fires a named event, such as `sessionStart`, `preToolUse`, or `afterAgentResponse`: the author types `@Hook("preToolUse")` on the member, the member receives the event's payload, and it returns the fields the IDE reads (`permission`, `continue`, `user_message`, `agent_message`, `additional_context`). Every hook on the same event runs, and the IDE gets one merged answer. `@Hook("event", disabled=True)` turns one member off; `@Hooks(disabled=True)` above `@agent_toolset` turns off every hook on that class.
*HookInstallation* is how `/install` publishes hooks: it records each hooked member and points every event it uses at the hook server. `@Hook` and `@mcp` on the same member are two separate publications.
*HookServer* is the long-running process that answers every hook call for one repository. For each event it reads the session saved as open in the repository's `.sessions/session.json` (main when none is), so a switch or a close made through MCP reaches the hooks at once, and it writes its logs under that session's `logs/` folder; *HookDaemon* finds, starts, and checks it, so health reports and the MCP server can ask whether it is running.
The hook server names, starts, and stops its process through harness/process.

- **Purpose:** Let a toolset member answer IDE events, and keep one hook server per repository that runs every hooked member and merges their answers.
- **Seam (terms):** Hook, Hooks, HookPayload, HookInstallation, HookServer, HookDaemon; the marks `@Hook("event")` and `@Hooks(disabled=True)`
- **Dependencies (one-way):** harness/agent_tools (the hook server reads the open session through *ToolCall*, as every tool call does), harness/marks (*Destination*), harness/installation (*Installation*, *RepositoryToolsets*), harness/process, harness/name, space/context_config (which guideline applies to an edited file). Nothing in the framework below harness/installer imports this module; space/context_config is the one import of space left (`.sessions/_backlog/break-module-dependency-cycles.md`).

## Constraint

Name the event exactly as the IDE does; it must be one of `Hook.EVENTS`, and an unknown name fails when the class is decorated, so a misspelled hook never installs silently. A disabled hook returns nothing, even when another operation calls it directly. Do not start the hook server by hand: the installed hook command and `HookDaemon` start it, and a second start finds the first through its lock file.
