# BaseContextTool (composer + lifecycle)

**Purpose:** Shared base for every concrete context domain — generate/validate/satisfy/document/createRule. Domains subclass it directly.

**Primary use case:** Subclass once per domain toolset; call kit providers and lifecycle actions from the host face without composing Workspace/Scan yourself.

**Rationale:** One composer owns session open, kit wiring, and lifecycle prose expansion so domains stay thin subclasses.

## Seam

`BaseContextTool` is the seam: domains subclass it and call through `workspace` / `scanner` / lifecycle actions. Providers return real kit instances — never `self`. Host `@agent_tool` / `@resource` methods are thin forwards for agent CLI. `@agent_instructions` / `@instruction` / `@agent_tool` remain (primitives only).

## Public API

- `module_dir` — package folder for the concrete subclass
- Stage constants: `SHAPING`, `DISCOVERY`, `SPEC`, `ENGINEER`
- `fidelities: ClassVar[dict[str, str] | None]` — subclasses declare stage → fidelity_name mapping; triggers auto-generated lifecycle methods
- `_set_fidelity(fidelity_name)` — updates `self.fidelity` and `self.format` at runtime
- Composed on host: `workspace` (`Workspace`), `turn` (`Turn`), `scanner` (`Scan`), `decisions` (`RecordDecisions`). **No** `repairer` / `eval` / session-turn re-exports. Stage kits (`Sketch`, `GrillContext`, `Iterate`, `Partition`, `Improvement`) are **not** composed on the host — slash commands invoke them with `arguments.tools`.
- Host tools: `scan`, `render`, `begin_turn`, `finish_turn`, `record_mistake`, `record_correction` (not legacy `close_session`, eval turn names)
- `supported_formats: ClassVar[frozenset[str]]` — formats this tool can render into; empty on the base
- `render(format, content="")` — `@agent_tool` that renders already-generated output into `format`
- Resource `active`; instruction `session_guidance`
- Class knobs: `default_workspace_folder`, `context_index_key`
- Host lifecycle `@agent_instructions`: `generate`, `validate`, `satisfy`, `document`, `createRule`, `generate_output`, `add_generate_header_to_generated` — each auditable body ends with explicit `SessionLog.instance().append(..., role=run)` then `self.turn.finish_turn()`.
- Kit-owned slash: `/iterate`, `/sketch`, `/grill`, `/partition`, `/repair` → `improvement.improvement:Improvement`. **Host-owned** `/generate` `/validate` `/document` `/satisfy` (each context tool `action: …` in order) — no HostLifecycle.
- Mistakes/corrections: `Turn.record_mistake` / `Turn.record_correction` (git-primary).

## Dependencies

Workspace under `context_tools/actions/workspace`; Scan under
`utilities/scanners`; Improvement under `context_tools/actions/improvement`;
Sketch, GrillContext, Iterate, Partition under `context_tools/actions/`;
RecordDecisions under `utilities/record_decisions`
