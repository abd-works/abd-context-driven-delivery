---
fidelity: [model]
artifact: [clean_engineering]
format: md
---

**Sources / context:** `utilities/mcp_server/mcp_server.py`; `utilities/mcp_server/.context/mcp_server_spec.md`

## Language

*McpToolset* wraps one loaded CDD toolset — discovers `McpTool` and `McpPrompt` per operation and registers them on a server.

*McpServer* loads CDD instances via `McpToolset`, finds tools and prompts by `mcp_name`, and delegates.

*McpTool* is one MCP **tool** — discovered from `@agent_tool`, invoked via `tools/call`.

*McpPrompt* is one MCP **prompt** — discovered from `@instruction`, listed via `prompts/list`, body runs when invoked.

MCP groups tools, prompts, and resources under **primitives**. There is no protocol-level type shared only by tools and prompts — `_McpPrimitive` is an internal implementation base.

## Modules

Build order: `primitives.tools` | `primitives.instructions` → `mcp_server`

---

# utilities/mcp_server

- **Purpose:** MCP-native runtime for CDD tool and prompt discovery and invocation.
- **Seam (terms):** McpServer, McpToolset, McpTool, McpPrompt
- **Dependencies (one-way):** `primitives.tools`, `primitives.instructions`

## McpTool

+ McpTool(toolset_name: str, method_name: str, callable: Callable, description: str)
------
+ toolset_name: str
+ method_name: str
+ callable: Callable
+ description: str
+ mcp_name: str
----
+ McpTool(instance.increment)
+ register_on(registry): None
+ invocable_parameters(): tuple[str, ...]
+ invoke(arguments): object

## McpPrompt

+ McpPrompt(toolset_name: str, method_name: str, callable: Callable, prompt_text: str, referenced_tool_names: tuple[str, ...])
------
+ toolset_name: str
+ method_name: str
+ callable: Callable
+ prompt_text: str
+ referenced_tool_names: tuple[str, ...]
+ mcp_name: str
----
+ McpPrompt(instance.plan_work)
+ register_on(registry): None
+ invoke(server, arguments): object
	-> McpServer.invoke_tool

## McpToolset

+ McpToolset(instance: AnnotatedToolset)
------
+ instance: AnnotatedToolset
+ toolset_name: str
+ << aggregation >> tools: dict[str, McpTool]
+ << aggregation >> prompts: dict[str, McpPrompt]
----
+ register_on(server): None

## McpServer

+ McpServer(toolset_loader: _CddToolsetLoader | None = None)
------
+ << aggregation >> toolsets: dict[str, McpToolset]
+ << aggregation >> _tools: dict[str, McpTool]
+ << aggregation >> _prompts: dict[str, McpPrompt]
+ started: bool
----
+ start(toolset_refs): None
+ list_tools(): tuple[str, ...]
+ list_prompts(): tuple[str, ...]
+ invoke_tool(mcp_name, arguments): object
	-> McpTool.invoke
+ invoke_prompt(mcp_name, arguments): object
	-> McpPrompt.invoke
