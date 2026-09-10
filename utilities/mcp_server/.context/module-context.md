# mcp_server — module context

**Layer:** MCP Invocation Layer  
**Location:** `utilities/mcp_server`  
**Ticket theme:** `theme:mcp-invocation-layer` (see `.context/workflow-packages.yaml`)

## Purpose

Persistent local MCP runtime for CDD. Discovers annotated toolset classes, constructs instances, registers MCP tools and prompts, and invokes bound Python callables directly — without YAML request documents, CLI dispatch, or a generic RPC runner underneath MCP.

## Seam (terms)

`McpServer`, `McpToolset`, `McpTool`, `McpPrompt`

## Vocabulary

| CDD | MCP primitive | Type |
|---|---|---|
| `@agent_tool` | **tool** | `McpTool` |
| `@instruction` | **prompt** | `McpPrompt` |

MCP defines **primitives** (tools, prompts, resources) as separate concepts — there is no protocol type that is both a tool and a prompt, and no MCP toolset. `_McpPrimitive` is internal shared identity only. `McpToolset` is our adapter: one loaded CDD `@toolset` instance → discovered `McpTool` / `McpPrompt` operations registered on the server.

## Public API

- `McpToolset(instance)` / `register_on(server)` — discover operations on one loaded CDD instance and enroll them
- `McpServer.start` — load CDD instances, construct `McpToolset` per instance, register on server
- `McpServer.invoke_tool` / `invoke_prompt` — host wire: resolve by `mcp_name` and delegate
- `McpServer.list_tools` / `list_prompts` — enrolled MCP names for the host
- `McpServer.toolsets` — enrolled `McpToolset` per loaded CDD instance
- `McpTool(instance.increment)` / `invoke` / `invocable_parameters` — one `@agent_tool` operation
- `McpPrompt(instance.plan_work)` / `invoke` / `prompt_text` / `referenced_tool_names` — one `@instruction` operation
- `McpToolset.tools` / `prompts` — discovery metadata; do not re-expose through name lookup on the server

## Constraint

Callers must use dotted MCP names (`bdd.find_examples`). Do not route AI execution through `tools.ps1`, `python -m tools run`, or YAML stdin blocks.

## Extend

Pass additional toolset module references to `McpServer.start` when registering more CDD surfaces. Do not add per-user session architecture to the server process.

## Host process

- **Transport:** stdio — Cursor spawns `python -m mcp_server` as a child process
- **Library:** official `mcp==1.30.0` Python SDK (`mcp.server.Server` + `stdio_server`)
- **Entry:** `mcp_server.__main__` — `--toolsets` or `MCP_TOOLSET_REFS` (comma-separated)
- **Adapter:** `McpHost` maps `tools/list`, `tools/call`, `prompts/list`, `prompts/get` → `McpServer`; `@instruction` orchestration is dual-listed on `tools/list` so hosts can invoke it
- **Built-in:** `cdd.ping` health check always available

## Dependencies (one-way)

- `primitives.tools` — `@toolset`, `@agent_tool`, `@resource`; `_ToolsetLoader.load`
- `primitives.instructions` — `@instruction`, `tool(...)` semantics
- `mcp` — stdio transport and protocol only; domain stays in `McpServer`
