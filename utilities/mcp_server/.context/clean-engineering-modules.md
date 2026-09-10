---

fidelity: [modules]

artifact: [clean_engineering]

format: md

---



**Sources / context:** `utilities/mcp_server/.context/mcp_server_spec.md`



## Language



*McpToolset* wraps one loaded CDD toolset — discovers *McpTool* and *McpPrompt* per operation and registers them on a server.

*McpServer* is the persistent local MCP boundary. It loads CDD instances via *McpToolset*, finds enrolled operations by `mcp_name`, and delegates invocation.



*McpTool* is one MCP **tool** primitive — a discovered `@agent_tool`. *McpPrompt* is one MCP **prompt** primitive — a discovered `@instruction` body plus its prompt text. MCP has no named superclass for tool and prompt together; only our private `_McpPrimitive` shares their local identity fields.



## Modules



Build order: `primitives.tools` | `primitives.instructions` → `mcp_server`



---



# utilities/mcp_server

- **Purpose:** MCP-native runtime that discovers CDD `@agent_tool` and `@instruction` members, registers them as MCP tools and prompts, and invokes bound Python callables directly.

- **Seam (terms):** McpServer, McpToolset, McpTool, McpPrompt

- **Dependencies (one-way):** `primitives.tools`, `primitives.instructions`; MCP SDK adapter (internal)

