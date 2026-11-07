# harness/health
*ServerHealth* tells a person whether the parts of CDD that run beside the MCP server are up — the Session Board app, the graph app, and the hook server — and which port each app answers on, so the server health band in the chat can show them without anyone opening a terminal. A caller asks with the `server-health.report` MCP operation, or through its TypeScript language adapter.

- **Purpose:** Report whether the board app, the graph app, and the hook server are running, for the chat's server health band.
- **Seam (terms):** ServerHealth; the MCP operation `server-health.report`
- **Dependencies (one-way):** harness/agent_tools, harness/installation (`@language_adapter`, `@data_field`), harness/mcp, harness/hooks (*HookDaemon*, *HookServer*), space/work_state (the project being worked on), `scripts/instances.py` (the graph app's ports). It reads the board app's port as a number and imports nothing from harness/kanban.

## Constraint

The report answers only while the MCP server is up, so it says nothing about the server itself; the band in harness/chat-ui/pane works out that the server is lost, or that tools are missing, from how its own calls fail. The band calls the report after every cdd call and every prompt, so the operation stays out of the session log (`@noSessionLog`).
