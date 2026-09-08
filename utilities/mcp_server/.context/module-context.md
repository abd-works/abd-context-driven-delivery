# mcp_server — module context

## Purpose

Persistent local MCP runtime for CDD. Discovers annotated toolset classes, constructs instances, registers AI-callable operations and agent guidance, and invokes bound Python callables directly — without YAML request documents, CLI dispatch, or a generic RPC runner underneath MCP.

## Seam (terms)

`McpServer`, `McpToolCatalog`, `McpInstructionCatalog`, `ToolsetLoader`, `ToolBinding`, `InstructionBinding`, `McpNameFormatter`

## Public API

- `McpServer.start` — boot the persistent process and load annotated toolsets from the repository working tree
- `McpServer.invoke_tool` — call a registered `@tool` by dotted MCP name with structured arguments
- `McpServer.invoke_instruction` — run an `@instruction` body; `tool(...)` calls invoke registered tools and results may flow to output
- `McpServer.list_tools` — return registered MCP tool names
- `McpServer.list_instructions` — return registered instruction prompt names
- `McpServer.instruction_for` — return discovery metadata (prompt text and declared tools) for an `@instruction`
- `ToolsetLoader.load_instances` — construct toolset objects required for discovery
- `McpNameFormatter.format` — derive `{toolset_slug}.{method_name}` dotted names

## Constraint

Callers must use dotted MCP names (`bdd.find_examples`). Do not route AI execution through `tools.ps1`, `python -m tools run`, or YAML stdin blocks.

## Extend

Pass additional toolset module references or search roots to `McpServer.start` when registering more CDD surfaces. Do not add per-user session architecture to the server process.

## Dependencies (one-way)

- `primitives.tools` — `@toolset`, `@tool`, `@resource` discovery conventions
- `primitives.instructions` — `@instruction`, docstring extraction, `tool(...)` reference semantics
- MCP host SDK (adapter behind `McpServer`; not re-exported on the public seam)
