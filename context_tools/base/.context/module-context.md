# BaseContextTool (composer + lifecycle)

**Purpose:** Shared base for every concrete context domain — MI peer kits + generate/validate/satisfy/document (+ grill/sketch/iterate) + `@base_context_tool`.

**Seam:** BaseContextTool, base_context_tool

**Public API:** `module_dir`; `contexts`; lifecycle actions; `base_context_tool(cls)` decorator

**Dependencies:** WorkspaceSession, Scan, PartitionPipeline, Repair (utilities/)

**Mechanism:** Multiple-inheritance composer. Lifecycle is inlined (not a peer kit); action prose is `#` sections in `base_context_tool.md`. Domains `@base_context_tool` merge with BaseContextTool. Scaffolding new domains is **CreateContextTool** (`create_context_tool/`), not this class.
