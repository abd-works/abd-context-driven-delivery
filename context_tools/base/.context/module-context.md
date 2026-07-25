# ContextTool (composer)

**Purpose:** Merge peer kits; host shared domain face and `@context_tool`. Action prose lives beside each kit.

**Seam:** ContextTool, context_tool

**Public API:** `module_dir`; `contexts`; `context_tool(cls)` decorator

**Dependencies:** WorkspaceSession, Scan, PartitionPipeline, Repair (utilities/); ArtifactLifecycle (base/)

**Mechanism:** Multiple-inheritance composer of concrete kits (one test tier — no I*/Class split). Concept-owned `@instruction` slots live on kits and merge in. Domains `@context_tool` merge with ContextTool as before.
