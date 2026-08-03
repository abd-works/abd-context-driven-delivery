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

### Never executed — `@action` bodies are read, not run

**`@action` method bodies never execute as Python.** They are parsed once via `ast` and walked statically to produce instruction text + a tool list. Every statement in an `@action` body — `self.foo()`, `self.bar(x, y)`, a bare string, a `return "..."` — is *source text being read*, not code being run. Arguments written in an `@action` body (`self.index(context, out_root)`) are never passed anywhere; they exist only so the source reads naturally. This is why `self.verify_segment_completeness()` with zero arguments inside an `@action` body is completely fine even though the real method requires `segment_path` — the call is never made.

**Exception: when the callee's `mode` resource is `"tool"`, the call into that instance's action is *not* walked/inlined right now** (see `mode` under `AgenticToolset` in Public API). It is simply added to the caller's `tools` list by name — same bucket as a real `@tool` step — and expansion stops there. The agent must invoke that action on its own, separately, later (still never executing it as Python — it gets statically walked *then*, at its own top-level `invoke_action` call). So a `mode="tool"` action behaves, from the calling `@action`'s point of view, exactly like a `@tool`: deferred, name-only, no inlined instructions, no argument-passing. `mode` lives on the callee and applies uniformly whether the call is same-instance (`self.some_action()`) or cross-instance (`self.other.some_action()`).

**By contrast, `@tool` method bodies always execute as real Python, on demand, when the agent invokes that tool by name.** A `@tool`'s body runs exactly like any other method the moment `python -m tools run -` dispatches to it — real arguments, real return value, real side effects.

So: if you're staring at code inside an `@action` and asking "what happens when this runs?" — stop, that question doesn't apply. Ask instead "what instructions/tool-list does this produce when *statically walked*?" If you're staring at a `@tool` body, the opposite is true: read it exactly like normal Python, because that's what it is.

### Substitution — where `{{...}}` placeholders resolve

Every prose part (string literals in `@action` bodies, text loaded from `@instruction` file/section slots, and text returned by `@instruction(override=True)` methods) is passed through `_ActionExpander._substitute()` as the **last step** of `_build_instructions()`. This is the single substitution point.

| Placeholder | Source | Raises when |
|---|---|---|
| `{{self.attr}}` | `getattr(instance, attr)` at expand time | attribute does not exist on the live instance |
| `{{param}}` | action `arguments` dict | argument missing AND `param` is a declared action parameter |
| Unknown `{{token}}` | — | left as-is (embedded template content, not an action parameter) |

**Critical:** `Instruction.expand()` returns **raw text** — it does NOT touch `{{...}}` placeholders. A `{{self.domain_slug}}` in `partition_guidance.md` is not resolved when the file is read; it survives into `prose_parts` and resolves when `_substitute()` runs against the live toolset instance. Agents or authors reading a `.md` instruction file that contains `{{self.attr}}` should expect that value to be injected at action expansion time, not at file-read time.

## Public API

**`@action`** — decorator that marks a toolset method as an orchestration recipe. The body is read as instructions, not executed.

**`@agentic_toolset`** — class decorator parallel to `@toolset`. Use instead of `@toolset` on any class that declares `@action` methods. Merges `AgenticToolset` into the class so the `mode` resource is available.

**`AgenticToolset`** — base class added by `@agentic_toolset`. Contributes the `mode` resource (`"action"` by default). `mode` lives on the **callee**, not the caller, so it governs every call into that instance's actions — same-instance (`self.some_action()`) and cross-instance (`self.other_agentic_toolset().some_action()`) alike:

- `"action"` (default) — the callee's full action instructions and tool calls it needs to make is inlined into the caller's instructions. The agent sees the complete recipe.
- `"tool"` — the call is treated like any other tool: the called action's name appears in the caller's expansion `tools` list, but its instructions and inner tools are not inlined. The caller decides when to invoke that action and then receives its internal instructions. Because mode is checked on every call into that instance, a `"tool"`-mode instance whose own actions call further same-instance actions produces a chain of separate deferred steps instead of one inlined block.

Setting `mode` to any value other than `"action"` or `"tool"` raises `ValueError`.

**`Action`** — named handle for one discovered action (name + callable); contributes its own signature entry to the manifest. Exposes `instructions` (the action's docstring text), `signature_entry` (the manifest dict with `kind`, `tools`, etc.), and `add_to_signature` (writes the entry into a signature dict). `@action` only exposes that surface — it is not the seam itself. Run path is `action:` via Tools/`ToolsetExtensions` (private `_ActionRunner`), not a second public runner type.

**`ActionValidationError`** — raised when an `@action` body reaches across instances or names unknown members. Carries `class_name`, `action_name`, and `lineno` attributes; formats the message as `Class.action[:lineno] - reason`.

**`AgentWithActions`** — scaffold host that generates toolsets with `@action` recipes (generator seam in `agent_with_actions.py`, not the authoring annotation).

## Dependencies

**tools** — `Toolset`, `RunError`, `ToolsetExtensions` (and private manifest/signature helpers when building responses).

**primitives** — instruction-slot expansion.

Self-registers with `ToolsetExtensions` on import (`_register` / `_discover_actions` / `_ActionRunner`). Does not own toolset loading or the CLI entrypoint.
