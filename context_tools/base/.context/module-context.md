# BaseContextTool (composer + lifecycle)

**Purpose:** Shared base for every concrete context domain — partition/repair peers + generate/validate/satisfy/document/createRule (+ grill/sketch/iterate). Domains subclass it directly.

**Primary use case:** Subclass once per domain toolset; call kit providers and lifecycle actions from the host face without composing Session/Scan yourself.

**Rationale:** One composer owns session open, kit wiring, and lifecycle prose expansion so domains stay thin subclasses.

## Seam

`BaseContextTool` is the seam: domains subclass it and call `workspace()` / `scanner()` / lifecycle actions. The constraint is that providers return real kit instances (`Session(...)`, `Scan()`, …) — never `self` — and lifecycle bodies call through those providers. Host `@tool` / `@resource` methods are thin forwards for agent CLI. `@action` / `@instruction` / `@tool` remain (primitives only). Scaffolding new domains is CreateContextTool.

## Public API

- `module_dir` — package folder for the concrete subclass
- Stage constants: `SHAPING`, `DISCOVERY`, `SPEC`, `ENGINEER`
- `fidelities: ClassVar[dict[str, str] | None]` — subclasses declare stage → fidelity_name mapping; triggers auto-generated lifecycle methods
- `_set_fidelity(fidelity_name)` — updates `self.fidelity` and `self.format` at runtime
- Kit providers: `workspace()`, `scanner()`, `sketcher()`, `grill_context()`, `iterator()`, `decisions()`
- Forwarded session/scan tools: `ensure_session`, `create_session`, `close_session`, `read_context_index`, `record_context_root`, `scan`
- `supported_formats: ClassVar[frozenset[str]]` — formats this tool can render into; empty on the base
- `render(format, content="")` — `@tool` that renders already-generated output into `format`. Default rejects unknown formats. Channel tools override and call their parse/render (or `transform`) in-process.
- Resource `active`; instruction `session_guidance`
- Class knobs: `default_workspace_folder`, `context_index_key`
- Lifecycle actions: `generate`, `validate`, `satisfy`, `document`, `grill`, `sketch`, `iterate`, `createRule`, `generate_output`, `add_generate_header_to_generated`. Kit-owned slash commands: `/iterate` → `Iterator.iterate(tools=…)`; `/sketch` → `Sketcher.sketch(tools=…)`; `/grill` → `GrillContext.grill(tools=…)`; `/partition` → `Partition.partition(tools=…)`; `/generate` / `/validate` / `/document` / `/satisfy` → `HostLifecycle.*(tools=…)`; `/repair` → `Repair.repair(tools=…)`. Host stubs (no kit compose): `grill`, `sketch`, `iterate`, `partition`. Host `generate` / `validate` / `document` / `satisfy` / `repair` keep full bodies — kits delegate to them per tool.
- Eval capture: `self.eval` (`eval.EvalSession`); host tools `begin_eval_turn` / `finish_eval_turn` / `log_mistake` / `log_correction` (YAML index plus `{session.folder}/mistakes/{name}/`). Direct lifecycle actions (`generate`, `validate`, `document`, `partition`, `repair`, `eval`, `createRule`) register begin then finish on the action so the agent runs them. `grill` / `sketch` / `iterate` / `satisfy` do not add their own — they delegate. No `improve`.

## Dependencies

Session / workspace kits under `context_tools/actions/workspace`; Scan under
`utilities/scanners`; Repair under `utilities/eval`; Sketcher, GrillContext,
Iterator, Partition under `context_tools/actions/`; RecordDecisions under
`utilities/record_decisions` (composed via providers — not MI; prose lookup
stays in their source dirs)
