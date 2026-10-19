# CreateAgentToolset

**Purpose:** Scaffold a decorated `AgentToolSet` — `@agent_tool` operations and `@agent_instructions` recipes — from `templates/` matching by `examples/car/`.

**Primary use case:** Generate a new `@agent_toolset` class that follows the domain model in `harness/agent_tools`, not a BaseContextTool domain (that is CreateContextTool).

## Seam

`CreateAgentToolset` is the public surface. Constraint: recipes use `recipe` plus `tools(...)` / `instructions(...)`; do not emit `@resource` or execute recipe bodies.

## Public API

- `CreateAgentToolset(format=None, path=None, session=None, workspace=None)`
- Inherited operations: `guidance`, `contexts`, `examples`, `templates`. Lifecycle generate / validate live on kits.
