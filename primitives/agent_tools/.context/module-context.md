# Actions

## Purpose

Actions turns toolset classes into truly agentic classes. Annotated operations are interpreted by the AI; calls to nested `@agent_instructions` members and `@agent_tool` methods are made at the AI’s discretion — not by executing the action body as normal Python at invoke time.

## Primary use case

Mark a toolset method with `@agent_instructions`. Deploy walks the member via `operation_writes`; MCP enrolls it when marked `@mcp`. When the agent follows the deployed skill or MCP prompt, it receives expanded instructions plus the allowed tool list and chooses which `@agent_tool`s or nested `@agent_instructions` to invoke. Authors write `@agent_instructions` bodies; the AI decides the call sequence.

## Author annotations (locked)

| Annotation | Marker | Role |
|---|---|---|
| `@agent_instructions` | `_is_agent_instructions` | Action — body scanned and expanded, not executed as Python at invoke time |
| `@agent_tool` | `_is_agent_tool` | Agent-invokable tool — body runs on invoke |

Legacy `@action` / `@tool` author annotations are removed (no aliases). Manifest `kind` values and run-request keys `action:` / `tool:` stay as the published protocol.

## Seam

The seam is the path from a decorated `@agent_instructions` method to an expanded run payload: discover actions on a toolset, validate the body, expand string literals and `tools(...)` / `instructions(...)` wrappers, then return instructions plus the tool list for the AI to interpret.

When expansion makes tools available, agenda instructions must tell the AI to **display** those tools (each name and what it is for) in the user-visible reply before following the suggested flow — not only follow them silently or rediscover them by remanifesting.

### Never executed — `@agent_instructions` bodies are read, not run

**`@agent_instructions` method bodies never execute as Python at invoke time.** They are parsed via `ast` and walked statically (`AgentInstructions._scan`). **By contrast, `@agent_tool` method bodies always execute as real Python** when the agent invokes that tool by name.

## Dependencies

Optional **primitives** for shared helpers.
