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

**Judge answer:** **Recommend A ΓÇö path overrides only.** Checklist item 1 lists `load` / `save` / `lookupPath` / `upsertPath` on **`Workspace`** together with `pathOverrides`; item 2 isolates **`PathOverride`** row shape. Item 5 (`openWorkSession`) and item 4 (`BaseContextTool.workspace` resolution) are separate slices. OO sketch lines 125ΓÇô131 label the three-step chain as **resolution on `open`** ΓÇö that uses host `context_index_key` and `default_workspace_folder`, not bare `Workspace.lookupPath` in isolation. Option B would mix aggregates in one Bdd subject. Option C skips the usage-story prerequisite (overrides exist before a work session opens). Option D is wrong: existing `workspace-bdd-sketch.md` aligns with A but was never judge-validated ΓÇö keep the hierarchy direction, run validate after a proper sketch turn; do not void without a FAIL on the file.

**Citations:**

- `workspace-eval-oo-sketch.md` ┬º2 lines 47ΓÇô50, 55ΓÇô58, 111ΓÇô123 ΓÇö `pathOverrides`, `lookupPath`, `upsertPath`, sparse rows, `context-index.md` persistence
- `workspace-eval-oo-sketch.md` ┬º2 lines 84ΓÇô91, 125ΓÇô131 ΓÇö host resolution on **open** (defer to later slice)
- `workspace-eval-oo-sketch.md` ┬º9 lines 826ΓÇô830 ΓÇö checklist ordering: items 1ΓÇô2 before 5
- `context_index.py` lines 15ΓÇô20 ΓÇö todayΓÇÖs index path `{workspace}/.context/context-index.md` (persistence seam to fold into `Workspace`)
- `bdd-sketch.md` ΓÇö usage-story order: establish subject state before downstream open/session behaviors

**Slice unlocked:** **no** ΓÇö tick 1 selects slice **family** (A). Tick 2 should lock observables inside A (e.g. `lookupPath` when no row: absent override vs todayΓÇÖs `lookup_root` returning `None`; row key shape `tool` + `fidelity` vs todayΓÇÖs single-key entries).

---

### Turn 27ae89d2 ΓÇö grill tick 2

**Question:** Inside slice **A** (path overrides only), when `Workspace.lookupPath(tool, fidelity)` is called and **no** matching override row exists, what is the stakeholder-visible outcome?

**Options:**

- **A ΓÇö No override path:** `lookupPath` yields nothing (e.g. `None` / absent) ΓÇö the hostΓÇÖs default-folder fallback is **out of scope** for this slice (OO sketch puts that at resolution step 3 on **open**, lines 127ΓÇô129).
- **B ΓÇö Implicit default path:** `lookupPath` returns `{workspace.path}/{default_workspace_folder}` even though `Workspace` does not carry host defaults in the target model (would duplicate checklist item 4).
- **C ΓÇö Workspace root path:** return `{workspace.path}` when no row (todayΓÇÖs `root_glob_to_path` for `./*`).
- **D ΓÇö Error:** raise when no row exists.

**Secondary (index row shape):** persisted rows use **`tool` + `fidelity` + `path`** (OO sketch lines 115ΓÇô118, PathOverride lines 55ΓÇô58) ΓÇö **not** todayΓÇÖs single `tool_key = root_glob` entries in `ContextIndex.parse_current_entries` (one key per tool, no fidelity dimension).

**Runner paths read:**

- `workspace-eval-oo-sketch.md` ┬º2 lines 55ΓÇô58, 115ΓÇô118, 125ΓÇô129
- `context_index.py` `lookup_root`, `parse_current_entries`, `upsert_entry` (today: tool_key only; `## Log` section ΓÇö target drops Log per OO line 123)
- `grill-answers.md` tick 1 judge recommendation (slice A)

**Judge answer:** *(pending)*

**Citations:** *(pending)*

**Slice unlocked:** *(pending)*

