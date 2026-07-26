# Module build order — BaseContextTool / CreateContextTool

Concrete kits only (no separate interface tier — one test tier).

**Shared → `utilities/`** · **Base / create → `context_tools/base/`**

1. `utilities/sessions` — WorkspaceSession
2. `utilities/scanners` — Scan (+ engine)
3. `utilities/partition_pipeline` — PartitionPipeline
4. `utilities/repair` — Repair
5. `context_tools/base/base_context_tool.py` — BaseContextTool (composer + lifecycle) + `@base_context_tool`
6. `context_tools/create_context_tool/` — CreateContextTool (meta generator domain)

Composer MRO merges: PartitionPipeline, Repair, Scan, WorkspaceSession, Toolset (lifecycle methods on BaseContextTool).
