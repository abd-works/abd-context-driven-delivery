# Tools

## Purpose

Tools turns Python classes into toolsets that can be dropped into an AI chat; annotated operations can be called directly by the AI.

## Primary use case

Mark a class with `@toolset` and its operations with `@agent_tool` / `@resource`. Tools publishes a manifest so the chat (or CLI: `python -m tools manifest|run|agent-spec`) can see what to call and with what arguments.

## Author annotations (locked)

| Annotation | Marker | Role |
|---|---|---|
| `@toolset` | `_is_toolset` | Class is a toolset surface |
| `@agent_tool` | `_is_agent_tool` | Agent-invokable tool — body runs on invoke |
| `@resource` | `_is_resource` | Read-only resource |

Legacy `@tool` author annotation is removed (no alias). Manifest `kind: tool` and CLI key `tool:` stay as the published protocol.

## Seam

Annotating methods with `@agent_tool` / `@resource` and the class with `@toolset` reveals the surface. AI consumers follow the manifest and `run` response; they do not treat the toolset’s `.py` file as the instruction document.

## Public API

**`Toolset`**, **`toolset` / `agent_tool` / `resource`**, **`ToolsetExtensions`**, **`RunError`**, **`read_toolset_header` / `ToolsetHeader`**.

`run` with `tool:` dispatches `@agent_tool` members and registered extension members that are not `@agent_instructions` (currently `@sub_agent` via `ToolsetExtensions.members("sub_agent")`).

## Dependencies

Optional **primitives** for shared helpers. No dependency on actions — peers self-register through `ToolsetExtensions`.
