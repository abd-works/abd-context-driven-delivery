# mcp — module context

**Layer:** MCP Invocation Layer  
**Location:** `harness/mcp`  
**Ticket theme:** `theme:mcp-invocation-layer` (see `.context/workflow-packages.yaml`)

## Purpose

One MCP package: the `@mcp` annotation, `McpInstallation` (writes `mcp.json` and records ops), and the stdio host (`McpServer` + `McpHost`). Cursor starts `python -m harness.mcp --toolsets module:Class,…`.

## Seam

`mcp`, `McpOperationDefinition`, `McpInstallation`, `McpTool`, `McpPrompt`, `McpServer`, `McpHost`

## Public API

- `McpOperationDefinition.from_tool` / `invoke_line` — MCP name and the skill/command `Use MCP tool:` tail
- `McpInstallation.write` — record the op and write `.cursor/mcp.json` with `-m harness.mcp`
- `McpServer.start` / `bind_from` — enroll recorded `@mcp` ops only
- `McpHost.build` / `run` — stdio process; `cdd.ping` is always listed
- `McpHost.input_schema_for_callable` — JSON Schema from Python parameter types

## Host process

- **Transport:** stdio
- **Entry:** `python -m harness.mcp` — `--toolsets` or `MCP_TOOLSET_REFS`
- **Built-in:** `cdd.ping`
- **CodeQL:** `McpHost.run` starts one `codeql execute query-server2` and keeps it on `McpHost.codeql_server` until the host exits. Rule batches use that process; the CLI `database run-queries` path remains when the server is down.
