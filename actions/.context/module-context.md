# Actions

## Purpose

Actions turns toolset classes into truly agentic classes. Annotated operations are interpreted by the AI; calls to other actions and tools are made at the AI’s discretion — not by executing the recipe body as Python.

## Primary use case

Mark a toolset method with `@action`. On import, Actions registers with `ToolsetExtensions` so the action appears in the toolset manifest. When the class is dropped into a chat (or via `python -m tools run` with `action:`), the AI receives expanded instructions plus the allowed tool list and chooses which tools or nested actions to invoke. Authors write recipes; the AI decides the call sequence.

## Rationale

1. Agentic, not scripted execution — an `@action` body is a recipe of steps and slots for an AI, not Python that runs the tools itself.
2. Same-instance safety — validation keeps action bodies on tools and instruction slots that exist on that toolset, so recipes cannot silently reach across instances.
3. Plug into Tools without coupling Tools to Actions — self-register on import; Tools only sees the extension registry.

## Seam

The seam is the path from a decorated `@action` method to an expanded run payload: discover actions on a toolset, validate the body, expand docstring/instruction slots and tool steps, then return instructions plus the tool list for the AI to interpret. The constraint on callers is that action bodies only reference tools and instruction slots that exist on the same toolset instance — expansion fails with `ActionValidationError` when the body reaches across instances or names unknown members. The AI—not the expander—decides which listed tools or further actions to call.

## Public API

**`ActionRunner`** — the run surface for `action:` requests: expand a named action on a toolset instance and build the CLI response (`ok`, `instructions`, `tools`, optional `resources`).

**`Action`** — named handle for one discovered action (name + callable); contributes its own signature entry to the manifest.

**`action`** — annotation that exposes a method as that recipe surface. It is not the surface itself.

**`ActionExpander` / `ActionValidator`** — expand one action callable into prose and tool steps; validate that a toolset class’s `@action` methods only call allowed tools/slots.

**`add_action_wrapper` / `require_action`** — compose wrapper chains around actions (e.g. sketch/grill).

**`discover_actions` / `has_actions`** — inspect a toolset instance for `@action` methods (also registered into Tools’ extension bags).

## Dependencies

Actions depends on **tools** for `Toolset`, `RunError`, and `ToolsetExtensions` (and private manifest/signature helpers used when building responses), and on **primitives** for instruction-slot expansion. On import, Actions registers itself with `ToolsetExtensions` so actions appear in manifests and `action:` run requests without Tools importing this package. The package does not own toolset loading or the CLI entrypoint.
