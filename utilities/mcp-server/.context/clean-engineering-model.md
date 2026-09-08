---
fidelity: [model]
artifact: [clean_engineering]
format: py
---

**Sources / context:** `utilities/mcp-server/.context/mcp-server-spec.md`; `utilities/mcp-server/.context/clean-engineering-modules.md`; `utilities/mcp-server/.context/module-context.md`

Model fidelity lives in `utilities/mcp-server/mcp_server.py` (Python channel).

## Language

*McpServer* boots a persistent local MCP process, loads annotated toolsets, registers `@tool` callables and `@instruction` prompts, and invokes tools directly. *ToolsetLoader* constructs instances and collects bindings. *McpToolCatalog* and *McpInstructionCatalog* hold registrations. *McpNameFormatter* always emits `{toolset_slug}.{method_name}`.

## Module

# utilities/mcp-server

See class stubs in `mcp_server.py`: `McpServer`, `McpToolCatalog`, `McpInstructionCatalog`, `ToolsetLoader`, `ToolBinding`, `InstructionBinding`, `McpNameFormatter`.
