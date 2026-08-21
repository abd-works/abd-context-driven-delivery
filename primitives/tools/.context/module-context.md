# Tools

## Purpose

Tools turns Python classes into toolsets that can be dropped into an AI chat; annotated operations can be called directly by the AI.

## Primary use case

Mark a class with `@toolset` and its operations with `@tool` / `@resource`. Tools publishes a manifest so the chat (or CLI: `python -m tools manifest|run|agent-spec`) can see what to call and with what arguments. The class remains ordinary Python for human callers; the toolset is the drop-in surface for AI. Authors and AI read the manifest as a string (`front_matter` or the CLI), not by treating the toolset’s `.py` file as the instruction document.

## Rationale

1. Plain old Python objects become agentic tools — write a normal class, annotate the operations the AI may call; no separate tool framework object model to learn.
2. Minimal visible scaffolding — a few decorators and a manifest/`run` path; the rest stays ordinary Python.
3. Focus on logic — authors spend attention on behavior, not on wiring schemas or host-specific adapters for each chat.

## Seam

The same surface is revealed by annotating methods with `@tool` / `@resource` and the class with `@toolset` (plus the `@toolset-manifest` header that names the CLI command to load it). When that class is dropped into a chat, the AI reads the published manifest — instructions, tools, resources, actions — and calls one named tool or action with typed arguments through `run`. The constraint is that AI consumers follow the manifest and the `run` response (`response.instructions`); they do not treat the toolset’s `.py` file as the instruction document.

## Public API

**`Toolset`** — the surface: instructions, tools/resources, `front_matter` (manifest YAML string), and CLI command strings. Callers do not subclass it.

**`toolset` / `tool` / `resource`** — annotations that expose a plain class as that surface (`@toolset` mixes in `Toolset`; `@tool` / `@resource` mark callable members). They are not the surface themselves.

**`ToolsetExtensions`** — registry for optional signature contributors, member bags, capability detectors, validators, and run handlers. Peer packages register here; Tools only iterates the registry.

**`RunError`** — failure carrying a structured run-response document for CLI output.

`run` with `tool:` dispatches `@tool` members and registered extension members that are not `@action` (currently `@sub_agent` via `ToolsetExtensions.members("sub_agent")`). Manifest kind stays `sub_agent`; the CLI still executes the Python body.

**`read_toolset_header` / `ToolsetHeader`** — parse the `@toolset-manifest` header from a source file.

## Dependencies

Optional **primitives** for shared helpers. No dependency on actions or sub-agents — peers self-register through `ToolsetExtensions`; manifest assembly and `run` iterate that registry plus Tools’ own `@tool` / `@resource` discovery.

Existing peer docs in this folder (not replaced by this file): `.context/tools-behavior.md`.
