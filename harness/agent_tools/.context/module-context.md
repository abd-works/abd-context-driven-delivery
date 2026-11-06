## Language

*AgentToolSet* is the root a practice decorates with `@agent_toolset`. It holds *AgentTool* members: *AgentOperation* (`@agent_tool`) and *AgentInstructions* (`@agent_instructions`).

### AgentToolSet

- One decorated class — `@agent_toolset` merges *AgentToolSet* onto it; do not subclass *AgentToolSet*.
- Class docstring is toolset **description**; **name** is the slugified class name.
- **Invariant:** Each callable member has exactly one mark — `@agent_tool` or `@agent_instructions`.

### AgentTool

- Named callable on a parent *AgentToolSet*.
- Introspection: **kind**, **description**, **parameters**, **response**.
- **mcp_name** is the one name MCP publishes it under and the session log records it by: `{toolset slug}.{name}`, or a practice's slug alone for its own instructions. **invoke_line** is the `Use MCP tool:` line a skill or command ends with.
- **input_schema** is the JSON Schema of its parameters, read from their type hints by *ParameterSchema*; the MCP tool list and the TypeScript language adapter both read it.
- **invoke** runs one call: log it in the session, turn text sent for a `Path` parameter into a `Path`, call the callable. The MCP server calls this and nothing else.
- Install marks live on the callable; **install_to** and **destinations** read *InstallDestination*.

### AgentOperation

- `@agent_tool` — body runs as Python on **invoke**. A guidance action's operation starts a fresh session line before it runs.
- **kind** is `tool`.

### AgentInstructions

- `@agent_instructions` — **expand** walks the body; unwrapped code runs during expand; `tools(...)` defers; `instructions(...)` expands nested *AgentInstructions*.
- **tools** (read-only) names deferred `@agent_tool` callables, including those merged from nested `instructions(...)`.
- First parameter is **self** (the toolset).
- **invoke** answers with the expanded instructions, which is how MCP answers a call to a prompt.
- **Invariant:** Nested `instructions(...)` cycles are rejected.

### ExpansionMode

- On the callee *AgentToolSet* (**mode**): `instructions` expands nested actions inline; `tool` defers them onto the tools list.

### ExpansionResult

- Output of **expand**: **instructions** prose, **tools** names, **result**.

### AgentToolValidationError

- Raised when decorate-time **validate** rejects an `@agent_instructions` body.

### InstallDestination

- Where a member may enroll: `mcp`, `hook`, `skill`, `command`, `rules`.

### ToolSetCollection

- Named child *AgentToolSet* instances on **nested_toolsets**, iterated in entry order.

## Modules

Build order: `agent_tools`

---

# harness/agent_tools
- **Purpose:** Register, introspect, validate, and expand one decorated *AgentToolSet* and its *AgentTool* members. *agent_tools_probe* pings and invokes workspace MCP tools on the live host for `/agent-tools-diagnostics`.
- **Seam (terms):** AgentToolSet, AgentTool, AgentOperation, AgentInstructions, ExpansionMode, ExpansionResult, AgentToolValidationError, InstallDestination, ToolSetCollection, ParameterSchema
- **Dependencies (one-way):** *(none)*

## Public API

- `@agent_toolset`, `@agent_tool`, `@agent_instructions`
- `tools(...)`, `instructions(...)` — wrappers inside `@agent_instructions` bodies
- `AgentToolSet` — `name`, `description`, `operations`, `instructions`, `tools`, `tools_for`, `mode`, `nested_toolsets`, `instantiate`, `validate`
- `AgentTool` — `kind`, `description`, `parameters`, `response`, `mcp_name`, `invoke_line`, `input_schema`, `invoke`
- `ParameterSchema(callable)` — `json_schema` and `coerced(arguments)`, the one reader of a tool's parameter type hints
- `@agent_instructions` — the member’s **instructions**; `tools(...)` / `instructions(...)` in the body

## Constraint

Callers must decorate with `@agent_toolset` rather than subclass *AgentToolSet*. A member must carry exactly one of `@agent_tool` or `@agent_instructions`. `@agent_instructions` is the **instructions** the agent follows, not a Python call; wrap deferred work in `tools(...)` and nested recipes in `instructions(...)`. Wire-out (MCP, hooks, skills) lives in `installation` — this module does not enroll destinations.
