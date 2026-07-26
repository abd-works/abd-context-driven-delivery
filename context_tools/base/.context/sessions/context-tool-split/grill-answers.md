# Grill Answers

### Composer shape
BaseContextTool stays a composer that merges peer toolsets (not a facade).

### Module cut
Peers: WorkspaceSession, Scan, BaseContextTool, PartitionPipeline, Repair; BaseContextTool composer. No DomainContent module — instructions that belong to a concept live on that concept’s kit (merge brings them in). Composer keeps only shared domain face (`module_dir`, `contexts`) + `@base_context_tool`.

### Workspace + session
One mergeable kit (WorkspaceSession). Not a lib dep arrow between workspace and session.

### Scan naming
Module name is `scan` (not scan_tool).

### Repair vs log_fix
Same kit. log_fix records failures into to-fix.log; when repairing, obligation is root-cause fix (same as repair).

### Peer dependencies
Kits have no kit→kit module deps. Only BaseContextTool → each kit. Expansion may reference session/scan on the composed instance — not a module arrow.

### Engagement engines
GrillContext / Sketcher / Iterator stay in utilities/ (already extracted). BaseContextTool keeps only thin grill/sketch/iterate wrappers.

### Folder layout
If not BaseContextTool-only → `utilities/` (workspace_session, scanners, partition_pipeline, repair).  
BaseContextTool-only → `context_tools/base/` (composer + `artifact_lifecycle`). Kit action prose (`{action}.md`) lives beside the kit `.py`, not under a shared `base-context/`.

### Scan kit home
`utilities/scanners` — one kit (`Scan` + `ScannerCollection`).

### Engagement wrappers home
On BaseContextTool (with generate), not on the composer alone.

### Model / extract
Concrete kit classes only (no separate I* / impl tier — one test tier). BaseContextTool is an MI composer of the kits. Kit action docstrings use bare framework names (`generate`, …); prose resolves from `{action}.md` beside the defining kit (MRO walk).

### Lifecycle remerge (2026-07-25)
ArtifactLifecycle is not a peer kit. Lifecycle methods live on BaseContextTool; prose is `# Generate` / `# Validate` / `# Satisfy` / `# Document` sections in `base_context_tool.md` (same kit hygiene as sessions / partition_pipeline).

### Base vs create seam (2026-07-25)
- `base_context_tool` — base for all concrete domains; no aliases to old `ContextTool` / `@base_context_tool`.
- `create_context_tool` — domain that scaffolds new domains (`templates/`, `examples/`, meta contexts). Layout: `context_tools/base/create_context_tool/`.
