# harness/health

- **Purpose:** Tell a person whether the parts of CDD that run outside the MCP host are up, so the server health band can show them without anyone opening a terminal.
- **Seam (terms):** ServerHealth, with the `cdd` MCP tool `server-health.report`
- **Dependencies (one-way):** harness/hooks (HookDaemon, HookServer), harness/mcp (`mcp`), scripts/instances (the graph app's ports)

## Constraint

This tool can only answer while the MCP host is up, so it reports the graph app and the hook server and nothing about the host itself. The server health band in `harness/chat-ui/pane/hooks/health/` works out that the MCP host is lost or that tools are missing from how its own calls fail, and counts the loaded tools from the session's tool list.

The band is drawn by the `cdd-board` plugin in `harness/chat-ui/pane`, which already runs in every chat.
