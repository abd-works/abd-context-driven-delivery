# Grill answers â€” eval-consolidate-workspace Bdd behavior prep

Design source: `context_tools/actions/eval/.context/sessions/eval-consolidate-workspace/workspace-eval-oo-sketch.md`

Append-only. Runner adds question blocks; judge adds answers beneath.

---

### Turn 9266b3db â€” grill tick 1

**Question:** For the **first** Bdd behavior sketch slice (Â§9 workspace module checklist), where should the boundary fall?

**Options:**

- **A â€” Path overrides only:** `Workspace.load` / `save`, `pathOverrides`, `lookupPath`, `upsertPath`; persistence at `{workspace.path}/.context/context-index.md`; **exclude** `openWorkSession`, `currentWorkSession`, and the host three-step resolution chain on `open`.
- **B â€” Path overrides + host lookup on open:** everything in A, **plus** observable outcomes when a context tool resolves its edit path via `lookupPath(context_index_key, fidelity)` vs `{workspace.path}/{default_workspace_folder}` (OO sketch resolution steps 2â€“3 at lines 125â€“131).
- **C â€” openWorkSession first:** skip override persistence; start Bdd at `openWorkSession` setting `currentWorkSession` and delegating to `WorkSession.open` (checklist item 5).
- **D â€” Discard unvalidated draft:** treat existing `workspace-bdd-sketch.md` (path-overrides slice, never judge-validated) as void; re-sketch only after grill ticks name a slice.

**Runner paths read:**

- `workspace-eval-oo-sketch.md` Â§2 (Workspace model, PathOverride, path overrides table, resolution on open)
- `workspace-eval-oo-sketch.md` Â§9 workspace checklist items 1â€“2 and 5
- `workspace-bdd-sketch.md` (existing draft â€” slice 1 path overrides, deferred list)
- `context_tools/bdd/.context/bdd-grill-sketch-workflow.md`

**Judge answer:** **Recommend A â€” path overrides only.** Checklist item 1 lists `load` / `save` / `lookupPath` / `upsertPath` on **`Workspace`** together with `pathOverrides`; item 2 isolates **`PathOverride`** row shape. Item 5 (`openWorkSession`) and item 4 (`BaseContextTool.workspace` resolution) are separate slices. OO sketch lines 125â€“131 label the three-step chain as **resolution on `open`** â€” that uses host `context_index_key` and `default_workspace_folder`, not bare `Workspace.lookupPath` in isolation. Option B would mix aggregates in one Bdd subject. Option C skips the usage-story prerequisite (overrides exist before a work session opens). Option D is wrong: existing `workspace-bdd-sketch.md` aligns with A but was never judge-validated â€” keep the hierarchy direction, run validate after a proper sketch turn; do not void without a FAIL on the file.

**Citations:**

- `workspace-eval-oo-sketch.md` Â§2 lines 47â€“50, 55â€“58, 111â€“123 â€” `pathOverrides`, `lookupPath`, `upsertPath`, sparse rows, `context-index.md` persistence
- `workspace-eval-oo-sketch.md` Â§2 lines 84â€“91, 125â€“131 â€” host resolution on **open** (defer to later slice)
- `workspace-eval-oo-sketch.md` Â§9 lines 826â€“830 â€” checklist ordering: items 1â€“2 before 5
- `context_index.py` lines 15â€“20 â€” todayâ€™s index path `{workspace}/.context/context-index.md` (persistence seam to fold into `Workspace`)
- `bdd-sketch.md` â€” usage-story order: establish subject state before downstream open/session behaviors

**Slice unlocked:** **no** â€” tick 1 selects slice **family** (A). Tick 2 should lock observables inside A (e.g. `lookupPath` when no row: absent override vs todayâ€™s `lookup_root` returning `None`; row key shape `tool` + `fidelity` vs todayâ€™s single-key entries).

---

### Turn 27ae89d2 â€” grill tick 2

**Question:** Inside slice **A** (path overrides only), when `Workspace.lookupPath(tool, fidelity)` is called and **no** matching override row exists, what is the stakeholder-visible outcome?

**Options:**

- **A â€” No override path:** `lookupPath` yields nothing (e.g. `None` / absent) â€” the hostâ€™s default-folder fallback is **out of scope** for this slice (OO sketch puts that at resolution step 3 on **open**, lines 127â€“129).
- **B â€” Implicit default path:** `lookupPath` returns `{workspace.path}/{default_workspace_folder}` even though `Workspace` does not carry host defaults in the target model (would duplicate checklist item 4).
- **C â€” Workspace root path:** return `{workspace.path}` when no row (todayâ€™s `root_glob_to_path` for `./*`).
- **D â€” Error:** raise when no row exists.

**Secondary (index row shape):** persisted rows use **`tool` + `fidelity` + `path`** (OO sketch lines 115â€“118, PathOverride lines 55â€“58) â€” **not** todayâ€™s single `tool_key = root_glob` entries in `ContextIndex.parse_current_entries` (one key per tool, no fidelity dimension).

**Runner paths read:**

- `workspace-eval-oo-sketch.md` Â§2 lines 55â€“58, 115â€“118, 125â€“129
- `context_index.py` `lookup_root`, `parse_current_entries`, `upsert_entry` (today: tool_key only; `## Log` section â€” target drops Log per OO line 123)
- `grill-answers.md` tick 1 judge recommendation (slice A)

**Judge answer:** **Recommend A â€” no override path.** Target `Workspace.lookupPath(tool, fidelity)` should behave like todayâ€™s absent-key case: `ContextIndex.lookup_root` returns **`None`** when the key is missing (lines 91â€“94) â€” not workspace root, not implicit host default. Step 3 of the open resolution chain (`{workspace.path}/{default_workspace_folder}`) belongs on **BaseContextTool** / **open**, not on `Workspace.lookupPath` (OO lines 127â€“129). Reject B (host default on wrong aggregate), C (workspace root), D (error on miss).

**Row shape:** Confirm **`tool` + `fidelity` + `path`** per PathOverride (OO lines 55â€“58, 115â€“118). Todayâ€™s `parse_current_entries` / `upsert_entry` use a **single `tool_key`** with no fidelity dimension â€” Bdd describes the **target** model, not a line-for-line port. Persisted file drops **`## Log`** (OO line 123); todayâ€™s `render_index` still emits Log (lines 113â€“117) â€” out of scope for slice A observables except â€œsave writes Current rows only.â€

**Slice unlocked:** **partial â€” yes for sketch draft** with one open branch: `upsertPath` â€œremove row when path matches host default againâ€ (OO line 131) needs tick 3 â€” `Workspace` does not own `default_workspace_folder`.

**Citations:**

- `workspace-eval-oo-sketch.md` lines 47â€“50, 55â€“58, 115â€“123, 127â€“129
- `context_index.py` lines 91â€“94 (`lookup_root` â†’ `None`), 136â€“165 (`upsert_entry` / Log)
- `grill-answers.md` tick 1 â€” slice A family

**Slice unlocked:** **partial** â€” sketch may proceed for load / lookup / save / sparse rows; hold **`it should drop the row when path matches host default`** until tick 3.

---

### Turn 4d111cd1 â€” grill tick 3

**Question:** OO sketch line 131: `upsertPath` when resolved path **matches host default again** â†’ remove the row. `Workspace` does not own `default_workspace_folder`. How should slice **A** Bdd express default-match **removal**?

**Options:**

- **A â€” Caller-supplied default:** `upsertPath(tool, fidelity, path, default_path)` â€” when `path == default_path`, remove the row; when path differs from default, upsert sparse row. Host passes its `default_workspace_folder`-resolved path at call time.
- **B â€” Explicit remove only:** `removePath(tool, fidelity)` on `Workspace`; slice A Bdd covers add/update + explicit remove; â€œmatches defaultâ€ removal is host orchestration in a **later** slice (open / BaseContextTool).
- **C â€” Omit removal from slice A:** only add/update rows in this sketch; no `it should` for default-match removal anywhere yet.

**Runner paths read:**

- `workspace-eval-oo-sketch.md` line 131, lines 47â€“50
- `grill-answers.md` ticks 1â€“2 (slice A, lookupPath absent â†’ None)

**Judge answer:** **Recommend A â€” caller-supplied `default_path`.** OO line 131 describes behavior at **open** time when the host already knows the resolved path and its default â€” passing `default_path` into `upsertPath` keeps `Workspace` free of host fields while making removal observable on the aggregate: equal â†’ drop row; unequal â†’ sparse upsert. Reject B (splits one policy across two slices unnecessarily). Reject C (drops locked requirement from line 131).

**Citations:**

- `workspace-eval-oo-sketch.md` lines 47â€“50, 131
- `grill-answers.md` ticks 1â€“2 â€” slice A, lookup absent â†’ None, tool+fidelity+path

**Slice unlocked:** **yes** â€” slice A boundary: `load` / `save` / `lookupPath` (absent â†’ no override) / `upsertPath(tool, fidelity, path, default_path)` (sparse add/update/remove on default match); persistence `{workspace.path}/.context/context-index.md` without `## Log`; exclude `openWorkSession`, host resolution chain, `WorkSession`.

---

### Turn (grill tick 4 â€” slice B boundary)

**Question:** Slice **B** â€” `Workspace.openWorkSession(name, goal, fidelities, contexts, path, default_path)` (OO lines 51â€“53). Which observables belong in B vs defer to slice **C** (`WorkSession.open` / git branch)?

**Options:**

- **A â€” Workspace open only:** `load()`; add/load session in `workSessions`; set `currentWorkSession`; `upsertPath` when explicit `path` â‰  `default_path`; **exclude** git checkout, branch naming, `WorkSession.open` innards.
- **B â€” Include git branch checkout** in the same slice (WorkSession.open policy).
- **C â€” Include host three-step path resolution** instead of openWorkSession.

**Runner paths read:** `workspace-eval-oo-sketch.md` lines 51â€“53, 60â€“71, Â§9 items 3 and 5.

**Judge answer:** **Recommend A.** OO line 53 sequences `load(); currentWorkSession.open(...); upsertPath` â€” Bdd slice B stops at **Workspace** outcomes before git/branch (slice C). Checklist item 5 is `openWorkSession`; item 3 is `WorkSession` with `openTurn`/git. Reject B (mixes aggregates). Reject C (checklist item 4).

**Citations:** OO lines 45â€“53, 60â€“71; Â§9 lines 826â€“828.

**Slice unlocked:** **yes** â€” slice B: openWorkSession loads overrides, mutates workSessions/currentWorkSession, upsertPath on non-default explicit path; exclude WorkSession.open git.

---

### Turn (grill tick 5 â€” slice C)

**Question:** Slice **C** â€” `WorkSession.open` git branch policy only?

**Options:** **A** â€” branch checkout/create/refuse-when-dirty per `workspace_session.md` lines 50â€“61; exclude Turn/git commit. **B** â€” include Turn.finish commit.

**Judge answer:** **A.** Git branch rules are documented in workspace_session.md; Turn commit is checklist item 8 / eval slice.

**Slice unlocked:** **yes**

---

### Turn (grill tick 6 â€” slice D)

**Question:** Slice **D** â€” host edit-path resolution (OO lines 125â€“131) as subject **a context tool host**?

**Judge answer:** **yes** â€” three-step chain as observable outcomes; Workspace lookup already slice A.

**Slice unlocked:** **yes** â€” Bdd workspace module checklist items 1â€“5 covered at behavior signature level.



