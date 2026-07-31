# BaseContextTool (composer + lifecycle)

**Purpose:** Shared base for every concrete context domain — MI peer kits + generate/validate/satisfy/document (+ grill/sketch/iterate) + `@base_context_tool`.

**Seam:** BaseContextTool, base_context_tool

**Public API:** `module_dir`; `contexts`; lifecycle actions; lazy providers (`sketcher`, `grill_context`, `iterator`, `decisions`); `base_context_tool(cls)` decorator

**Dependencies:** WorkspaceSession, Scan, PartitionPipeline, Repair (utilities/); Sketcher, GrillContext, Iterator, RecordDecisions via in-method providers

**Mechanism:** Multiple-inheritance composer for peer kits (workspace/scan/partition/repair). Lifecycle is inlined; engagement kits are **called linearly** in action bodies (`self.workspace_session_bind()`, `self.sketcher().sketch_session()`, …) — not `@` chain decorators. `@action` / `@instruction` / `@tool` remain (primitives only). Domains `@base_context_tool` merge with BaseContextTool. Scaffolding new domains is **CreateContextTool** (`create_context_tool/`), not this class.
