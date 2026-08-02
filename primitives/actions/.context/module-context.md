# Actions

## Purpose

Actions turns toolset classes into truly agentic classes. Annotated operations are interpreted by the AI; calls to other actions and tools are made at the AI’s discretion — not by executing the code directly.

## Primary use case

Mark a toolset method with `@action`. On import, Actions registers with `ToolsetExtensions` so the action appears in the toolset manifest. When the class is dropped into a chat (or via `python -m tools run` with `action:`), the AI receives expanded instructions plus the allowed tool list and chooses which tools or nested actions to invoke. Authors write recipes; the AI decides the call sequence.

## Rationale

1. Agentic operations defined with object-oriented means — classes, methods, inheritance, and composition express recipes; the AI interprets them rather than Python executing the tool calls.
2. Avoid markdown sprawl — keep agentic behavior in code next to the tools it orchestrates, not in a growing pile of free-floating prompt files.
3. Markdown-first systems make cross-cutting concerns hard — encapsulation, shared wrappers, and reuse fight prose documents; OO structure keeps those concerns named and composable.

## Seam

The seam is the path from a decorated `@action` method to an expanded run payload: discover actions on a toolset, validate the body, expand docstring/instruction slots and tool steps, then return instructions plus the tool list for the AI to interpret. The constraint on callers is that action bodies only reference tools and instruction slots that exist on the same toolset instance — expansion fails with `ActionValidationError` when the body reaches across instances or names unknown members. The AI—not the expander—decides which listed tools or further actions to call.

## Public API

**`@action`** — decorator that marks a toolset method as an orchestration recipe. The body is read as instructions, not executed.

**`@agentic_toolset`** — class decorator parallel to `@toolset`. Use instead of `@toolset` on any class that declares `@action` methods. Merges `AgenticToolset` into the class so the `mode` resource is available.

**`AgenticToolset`** — base class added by `@agentic_toolset`. Contributes the `mode` resource (`"action"` by default). Controls how a cross-instance action call — `self.other_agentic_toolset().some_action()` — behaves:

- `"action"` (default) — the callee's full action instructions and tool calls it needs to make is inlined into the caller's instructions. The agent sees the complete recipe.
- `"tool"` — the cross-instance call is treated like any other tool: the companion action name appears in the caller's expansion `tools` list, but its instructions and inner tools are not inlined. The caller decides when to invoke that action and then receives its internal instructions.

Setting `mode` to any value other than `"action"` or `"tool"` raises `ValueError`.

**`Action`** — named handle for one discovered action (name + callable); contributes its own signature entry to the manifest. Exposes `instructions` (the action's docstring text), `signature_entry` (the manifest dict with `kind`, `tools`, etc.), and `add_to_signature` (writes the entry into a signature dict). `@action` only exposes that surface — it is not the seam itself. Run path is `action:` via Tools/`ToolsetExtensions` (private `_ActionRunner`), not a second public runner type.

**`ActionValidationError`** — raised when an `@action` body reaches across instances or names unknown members. Carries `class_name`, `action_name`, and `lineno` attributes; formats the message as `Class.action[:lineno] - reason`.

**`AgentWithActions`** — scaffold host that generates toolsets with `@action` recipes (generator seam in `agent_with_actions.py`, not the authoring annotation).

## Dependencies

**tools** — `Toolset`, `RunError`, `ToolsetExtensions` (and private manifest/signature helpers when building responses).

**primitives** — instruction-slot expansion.

Self-registers with `ToolsetExtensions` on import (`_register` / `_discover_actions` / `_ActionRunner`). Does not own toolset loading or the CLI entrypoint.
