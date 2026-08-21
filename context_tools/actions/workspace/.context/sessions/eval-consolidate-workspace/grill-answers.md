# Grill answers ΓÇö eval-consolidate-workspace Bdd behavior prep

Design source: `context_tools/actions/eval/.context/sessions/eval-consolidate-workspace/workspace-eval-oo-sketch.md`

Append-only. Runner adds question blocks; judge adds answers beneath.

---

### Turn 9266b3db ΓÇö grill tick 1

**Question:** For the **first** Bdd behavior sketch slice (┬º9 workspace module checklist), where should the boundary fall?

**Options:**

- **A ΓÇö Path overrides only:** `Workspace.load` / `save`, `pathOverrides`, `lookupPath`, `upsertPath`; persistence at `{workspace.path}/.context/context-index.md`; **exclude** `openWorkSession`, `currentWorkSession`, and the host three-step resolution chain on `open`.
- **B ΓÇö Path overrides + host lookup on open:** everything in A, **plus** observable outcomes when a context tool resolves its edit path via `lookupPath(context_index_key, fidelity)` vs `{workspace.path}/{default_workspace_folder}` (OO sketch resolution steps 2ΓÇô3 at lines 125ΓÇô131).
- **C ΓÇö openWorkSession first:** skip override persistence; start Bdd at `openWorkSession` setting `currentWorkSession` and delegating to `WorkSession.open` (checklist item 5).
- **D ΓÇö Discard unvalidated draft:** treat existing `workspace-bdd-sketch.md` (path-overrides slice, never judge-validated) as void; re-sketch only after grill ticks name a slice.

**Runner paths read:**

- `workspace-eval-oo-sketch.md` ┬º2 (Workspace model, PathOverride, path overrides table, resolution on open)
- `workspace-eval-oo-sketch.md` ┬º9 workspace checklist items 1ΓÇô2 and 5
- `workspace-bdd-sketch.md` (existing draft ΓÇö slice 1 path overrides, deferred list)
- `context_tools/bdd/.context/bdd-grill-sketch-workflow.md`

**Judge answer:** *(pending)*

**Citations:** *(pending)*

**Slice unlocked:** *(pending)*
