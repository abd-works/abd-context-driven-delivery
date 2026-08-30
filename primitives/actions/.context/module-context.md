# Actions

## Purpose

Actions turns toolset classes into truly agentic classes. Annotated operations are interpreted by the AI; calls to other recipes and tools are made at the AI’s discretion — not by executing the recipe code directly.

## Primary use case

Mark a toolset method with `@agent_instructions`. On import, Actions registers with `ToolsetExtensions` so the recipe appears in the toolset manifest. When the class is dropped into a chat (or via `python -m tools run` with `action:`), the AI receives expanded instructions plus the allowed tool list and chooses which `@agent_tool`s or nested `@agent_instructions` to invoke. Authors write recipes; the AI decides the call sequence.

## Author annotations (locked)

| Annotation | Marker | Role |
|---|---|---|
| `@agent_instructions` | `_is_agent_instructions` | Recipe — expanded, never executed as Python |
| `@agent_tool` | `_is_agent_tool` | Agent-invokable tool — body runs on invoke |

Legacy `@action` / `@tool` author annotations are removed (no aliases). Manifest `kind` values and CLI keys `action:` / `tool:` stay as the published protocol.

## Seam

The seam is the path from a decorated `@agent_instructions` method to an expanded run payload: discover recipes on a toolset, validate the body, expand docstring/instruction slots and tool steps, then return instructions plus the tool list for the AI to interpret.

When expansion makes tools available, agenda instructions must tell the AI to **display** those tools (each name and what it is for) in the user-visible reply before following the suggested flow — not only follow them silently or rediscover them by remanifesting.

### Never executed — `@agent_instructions` bodies are read, not run

**`@agent_instructions` method bodies never execute as Python.** They are parsed via `ast` and walked statically. **By contrast, `@agent_tool` method bodies always execute as real Python** when the agent invokes that tool by name.

## Dependencies

Optional **primitives** for shared helpers. Peer packages register through `ToolsetExtensions`.
