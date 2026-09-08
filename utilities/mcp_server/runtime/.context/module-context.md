# mcp_server.runtime — module context

## Purpose

Internal collaborators for `mcp_server`. Implementation detail for the parent module — not a separate public seam.

## Public API

- Re-exported on the parent seam as `ToolBinding`, `InstructionBinding`, `McpToolCatalog`, `McpInstructionCatalog`, `ToolsetLoader`, `McpNameFormatter`, `tool`, and `mcp_instruction`.

## Constraint

Callers must import from the `mcp_server` package — do not import this nested module directly.

## Dependencies (one-way)

- `primitives.tools` — toolset loading and `@agent_tool` discovery
- `mcp_server.McpServer` — instruction orchestration host
