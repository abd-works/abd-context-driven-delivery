# mcp — module context

**Layer:** MCP Invocation Layer  
**Location:** `primitives/mcp`  
**Ticket theme:** `theme:mcp-invocation-layer` (see `.context/workflow-packages.yaml`)

## Purpose

One MCP package: the `@mcp` annotation, `McpInstallation` (writes `mcp.json` and records ops), and the stdio host (`McpServer` + `McpHost`). Cursor starts `python -m primitives.mcp --toolsets module:Class,…`.

## Seam

`mcp`, `McpOperationDefinition`, `McpInstallation`, `McpTool`, `McpPrompt`, `McpServer`, `McpHost`

## Public API

- `McpOperationDefinition.from_tool` / `invoke_line` — MCP name and the skill/command `Use MCP tool:` tail
- `McpInstallation.write` — record the op and write `.cursor/mcp.json` with `-m primitives.mcp`
- `McpServer.start` / `bind_from` — enroll recorded `@mcp` ops only
- `McpHost.build` / `run` — stdio process; `cdd.ping` is always listed
- `McpHost.input_schema_for_callable` — JSON Schema from Python parameter types

## Host process

- **Transport:** stdio
- **Entry:** `python -m primitives.mcp` — `--toolsets` or `MCP_TOOLSET_REFS`
- **Built-in:** `cdd.ping`
