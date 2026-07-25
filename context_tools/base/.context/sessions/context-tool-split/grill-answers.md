# Grill Answers

### Composer shape
ContextTool stays a composer that merges peer toolsets (not a facade).

### Module cut
Peers: WorkspaceSession, Scan, ArtifactLifecycle, PartitionPipeline, Repair; ContextTool composer. No DomainContent module — instructions that belong to a concept live on that concept’s kit (merge brings them in). Composer keeps only shared domain face (`module_dir`, `contexts`) + `@context_tool`.

### Workspace + session
One mergeable kit (WorkspaceSession). Not a lib dep arrow between workspace and session.

### Scan naming
Module name is `scan` (not scan_tool).

### Repair vs log_fix
Same kit. log_fix records failures into to-fix.log; when repairing, obligation is root-cause fix (same as repair).

### Peer dependencies
Kits have no kit→kit module deps. Only ContextTool → each kit. Expansion may reference session/scan on the composed instance — not a module arrow.

### Engagement engines
GrillContext / Sketcher / Iterator stay in utilities/ (already extracted). ArtifactLifecycle keeps only thin grill/sketch/iterate wrappers.

### Folder layout
If not ContextTool-only → `utilities/` (workspace_session, scanners, partition_pipeline, repair).  
ContextTool-only → `context_tools/base/` (composer + `artifact_lifecycle`). Kit action prose (`{action}.md`) lives beside the kit `.py`, not under a shared `base-context/`.

### Scan kit home
`utilities/scanners` — one kit (`Scan` + `ScannerCollection`).

### Engagement wrappers home
On ArtifactLifecycle (with generate), not on the composer alone.

### Model / extract
Concrete kit classes only (no separate I* / impl tier — one test tier). ContextTool is an MI composer of the kits. Kit action docstrings use bare framework names (`generate`, …); prose resolves from `{action}.md` beside the defining kit (MRO walk).
