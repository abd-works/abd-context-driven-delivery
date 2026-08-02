# BaseContextTool (composer + lifecycle)

**Purpose:** Shared base for every concrete context domain — partition/repair peers + generate/validate/satisfy/document (+ grill/sketch/iterate). Domains subclass it directly.

**Primary use case:** Subclass once per domain toolset; call kit providers and lifecycle actions from the host face without composing Session/Scan yourself.

**Rationale:** One composer owns session open, kit wiring, and lifecycle prose expansion so domains stay thin subclasses.

## Seam

`BaseContextTool` is the seam: domains subclass it and call `workspace()` / `scanner()` / lifecycle actions. The constraint is that providers return real kit instances (`Session(...)`, `Scan()`, …) — never `self` — and lifecycle bodies call through those providers. Host `@tool` / `@resource` methods are thin forwards for agent CLI. `@action` / `@instruction` / `@tool` remain (primitives only). Scaffolding new domains is CreateContextTool.

## Public API

- `module_dir` — package folder for the concrete subclass
- Kit providers: `workspace()`, `scanner()`, `sketcher()`, `grill_context()`, `iterator()`, `decisions()`
- Forwarded session/scan tools: `ensure_session`, `create_session`, `close_session`, `read_context_index`, `record_context_root`, `scan`
- Resource `active`; instruction `session_guidance`
- Class knobs: `default_workspace_folder`, `context_index_key`
- Lifecycle actions: `generate`, `validate`, `satisfy`, `document`, `grill`, `sketch`, `iterate`, `generate_output`, `add_generate_header_to_generated`

## Dependencies

Session (composed via `workspace()`), Scan (composed instances); PartitionPipeline, Repair (MI peers); Sketcher, GrillContext, Iterator, RecordDecisions (composed)
