# Handoff - kit prose, sessions merge, specs-with-kits

## 1. Next session focus

**Kit hygiene landed; next is land/commit or pick next CE work.** BaseContextTool peer kits now own their prose (sections in `{slug}.md`), sessions is one package, and kit specs live beside the kits. Do not re-open the module cut unless to-fix forces it.

## 2. Resume in three lines

(a) Stage: **post-split kit packaging** on bout `context-tool-split` (`context_tools/base/.context/sessions/context-tool-split/`) — after bout-closed handoff of 2026-07-24.
(b) Last accepted: merged `workspace_session` → `utilities/sessions`; session-path guidance out of `context_tool.md` into `sessions.md`; kit prose as **sections** in one md (`sessions.md`, `partition_pipeline.md`); specs extracted to kits; resolver section fallback (`create_session` → `# Create Session`).
(c) Next: commit scoped changes if asked; otherwise next CE fidelity/scope. Do not re-split modules.

## 3. Generator state

- Bout: `context_tools/base/.context/sessions/context-tool-split/`
- Composer: `context_tools/base/context_tool.py` — inherits BaseContextTool, PartitionPipeline, Repair, Scan, **WorkspaceSession** (from `sessions`), Toolset
- Sessions package (merged): `utilities/sessions/` — `Session`, `SessionLog`, `WorkspaceSession`, `context_index.py`, prose in `sessions.md`
- Partition kit prose: `utilities/partition_pipeline/partition_pipeline.md` (§ Partition / Index / Segment)
- Lifecycle prose: still per-file under `context_tools/base/{generate,validate,satisfy,document}.md` (not collapsed yet)
- Repair / scan: still `utilities/repair/repair.md`, `utilities/scanners/scan.md`
- **context_index_path:** `.context/context-index.md`
- **Current tool=root:** `clean_engineering = ./utilities/partition_pipeline/*` (was `./context_tools/base/*`)

## 4. Grilling / skills state

- Grill answers: `context_tools/base/.context/sessions/context-tool-split/grill-answers.md`
- Headings (unchanged locks): Composer shape; Module cut; Workspace + session; Scan naming; Repair vs log_fix; Peer dependencies; Engagement engines; Folder layout; Scan kit home; Engagement wrappers home; Model / extract
- Process locks still in force:
  - Instructions that belong to a concept live on that concept's kit
  - Workspace+session = one kit (now one **package** too)
  - Peers have no kit→kit deps; only composer depends on kits
  - Kit prose: prefer one `{slug}.md` with `#` sections over per-action files; `{name}.md` still wins if present
- Suggested skills: handoff done; commit only if user asks; next CE bout via create_session / generate

## 5. CDD progress

None (no cdd-sketch in this bout).

## 6. Artifacts to read

- `.context/context-index.md`
- `context_tools/base/.context/sessions/context-tool-split/grill-answers.md`
- `context_tools/base/.context/sessions/context-tool-split/context-tool-modules-sketch.md`
- `utilities/sessions/sessions.md` + `workspace_session.py`
- `utilities/partition_pipeline/partition_pipeline.md`
- `primitives/instructions/instructions.py` — `_path_for_name`, `_framework_action_prose`, `_section_in_kit`
- Kit specs:
  - `utilities/sessions/workspace_session_spec.py`
  - `utilities/partition_pipeline/partition_pipeline_spec.py`
  - `utilities/repair/repair_spec.py`
  - `context_tools/base/artifact_lifecycle_spec.py`
- Slim composer: `context_tools/base/context_tool_spec.py` (domain/meta face only)

## 7. Open questions / risks

- Working tree still mixes split + kit-hygiene + other edits — scope commits carefully.
- `artifact_lifecycle` / `repair` / `scan` not yet collapsed to single sectioned `{slug}.md` (optional follow-through).
- Agent BDD `context_tool_agent_spec` updated for session tools on generate; full agent run not re-executed this handoff.
- Encoding: mamba + `§` in specs — prefer `"\u00a7 Contexts"` in collector-loaded specs.
