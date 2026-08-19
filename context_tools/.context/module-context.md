# Contexts

## Purpose

Contexts provides functionality to manage knowledge for a field of expertise, and include tools to generate, validate, test, and otherwise work content according to that field’s guidelines and context_tools.

## Primary use case

Capture a field’s guidelines and examples as a context, then use its tools to generate and check content against those guidelines. Examples include`clean_engineering`, `bdd`, `stories`, `ux`, `ddd`, `agent_bdd`;

## Rationale

1. Knowledge and code regarding using ai for a context stay together — the same context holds the guidelines and the tools that apply them.
2. One shape per field of expertise — each context reuses the same generate / validate / document / satisfy / repair surface instead of inventing a custom harness.
3. Built on Tools/Actions — ordinary Python classes become expertise toolsets; authors focus on the field, not chat wiring.



## Seam

Annotate a class with `@context`, then create markdown for the named instruction properties: `contexts`, `examples`, `templates` (action prose comes from the action docstring / `# Generate` / `# Document` sections). Optionally extend any of the actions or tools to customize — `generate`, `validate`, `document`, `satisfy`, `repair`, `generate_output`, `add_generate_header_to_generated`, `scan`, `render`. Constraint: do not subclass `Context` directly; use `@context`. Constraint: AI consumers follow the manifest and `response.instructions`, not the context `.py` as the instruction document.

## Public API

`Context` — base generator toolset: `format`, `module_dir`, instruction slots, actions (`generate`, `validate`, `document`, `satisfy`, `repair`, `generate_output`, `add_generate_header_to_generated`), and tools `scan`, `render`. Authors do not subclass it in source.

`context` — class annotation that merges a context class with `Context` and registers it as a context toolset.

`instruction` — re-exported slot decorator for contexts that need an extra instruction slot (unusual; defaults cover the common slots).

## Dependencies

**tools** — `Toolset`, `tool` (and manifest/`run` via the toolset surface).

**actions** — `@action`, `_ActionRunner` validation on merge.

**primitives** — `Instruction`, `@instruction` expansion and asset location under `module_dir`.

**scanners** (package under this folder) — `ScannerCollection` used by `scan` / `_scanner_collection`.

Does not own practice context prose; each practice folder owns its `{context-slug}.md`, examples, and templates.

## Mechanism stereotype

**Key mechanism** — structural pattern instantiated once per practice context generator (`CleanEngineering`, `Bdd`, `Stories`, `Ux`, `Ddd`, `AgentBdd`, `CarChronicle`, …).

Observed from current instances:


|                      |                                                                                                                                                                                                                                                                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Variation points** | Context folder contents (`{context-slug}.md`, examples, templates/formats); optional `format` (and context-specific constructor args such as `fidelity`); optional `@action` body overrides / composition with other toolsets; optional context scanners behind `_scanner_collection`.                                |
| **Fixed parts**      | `@context` merge (not direct subclass); instruction slots for contexts / generate & document instructions / examples / templates; standard actions `generate` → `validate`, plus `document`, `satisfy`, `repair`; `scan` tool; `module_dir` = folder of the class module; toolset manifest + `run` as the AI surface. |
