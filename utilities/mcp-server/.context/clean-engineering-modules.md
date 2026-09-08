---
fidelity: [modules]
artifact: [clean_engineering]
format: md
---

**Sources / context:** `utilities/mcp-server/.context/mcp-server-spec.md`

## Language

*McpServer* is the persistent local MCP boundary. *ToolsetLoader* finds annotated CDD toolset classes, constructs them, and hands bound members to catalogs. *McpToolCatalog* and *McpInstructionCatalog* are the in-memory registries the server exposes to MCP. *McpNameFormatter* owns dotted `{toolset_slug}.{method_name}` naming.

## Modules

Build order: `primitives.tools` | `primitives.instructions` → `mcp_server`

---

# utilities/mcp-server

- **Purpose:** MCP-native runtime that discovers CDD `@tool` and `@instruction` members, registers them with MCP, and invokes `@tool` callables directly.
- **Seam (terms):** McpServer, McpToolCatalog, McpInstructionCatalog, ToolsetLoader, ToolBinding, InstructionBinding, McpNameFormatter
- **Dependencies (one-way):** `primitives.tools`, `primitives.instructions`; MCP SDK adapter (internal)
