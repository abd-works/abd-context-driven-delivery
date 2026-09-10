# MCP Invocation Layer — `utilities/mcp_server`

**Package location:** `utilities/mcp_server`  
**Layer:** MCP Invocation Layer  
**Project theme:** `theme:mcp-invocation-layer`  
**Module seam:** `McpServer`, `McpToolset`, `McpTool`, `McpPrompt`

Persistent local MCP runtime for CDD. Replaces YAML/CLI agent invocation with dotted MCP tool names (`bdd.find_examples`) and stdio host registration via `.cursor/mcp.json`.

## Spec and context

- `utilities/mcp_server/.context/mcp_server_spec.md` — migration and acceptance criteria
- `utilities/mcp_server/.context/module-context.md` — module purpose and host process
- `.context/sessions/replace-yaml-with-mcp-server/` — host discovery notes

## Ticket bodies

When filing or updating a ticket for this package, include **Package:** `utilities/mcp_server` and **Layer:** MCP Invocation Layer so `/tickets` can apply `theme:mcp-invocation-layer` without guessing.
