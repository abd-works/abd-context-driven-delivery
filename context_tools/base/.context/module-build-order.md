# Module build order — ContextTool split

Concrete kits only (no separate interface tier — one test tier).

**Shared → `utilities/`** · **ContextTool-only → `context_tools/base/`**

1. `utilities/workspace_session` — WorkspaceSession
2. `utilities/scanners` — Scan (+ engine)
3. `utilities/partition_pipeline` — PartitionPipeline
4. `utilities/repair` — Repair
5. `context_tools/base/artifact_lifecycle` — ArtifactLifecycle
6. `context_tools/base` — ContextTool composer + `@context_tool`

Composer MRO merges: ArtifactLifecycle, PartitionPipeline, Repair, Scan, WorkspaceSession, Toolset.
