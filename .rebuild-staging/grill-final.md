# Grill answers — eval-consolidate-workspace Bdd behavior prep

Design source: `context_tools/actions/eval/.context/sessions/eval-consolidate-workspace/workspace-eval-oo-sketch.md`

Append-only. Runner adds question blocks; judge adds answers beneath.

---

### Turn 9266b3db — grill tick 1

**Question:** For the **first** Bdd behavior sketch slice (§9 workspace module checklist), where should the boundary fall?

**Options:**

- **A — Path overrides only:** `Workspace.load` / `save`, `pathOverrides`, `lookupPath`, `upsertPath`; persistence at `{workspace.path}/.context/context-index.md`; **exclude** `openWorkSession`, `currentWorkSession`, and the host three-step resolution chain on `open`.
- **B — Path overrides + host lookup on open:** everything in A, **plus** observable outcomes when a context tool resolves its edit path via `lookupPath(context_index_key, fidelity)` vs `{workspace.path}/{default_workspace_folder}` (OO sketch resolution steps 2–3 at lines 125–131).
- **C — openWorkSession first:** skip override persistence; start Bdd at `openWorkSession` setting `currentWorkSession` and delegating to `WorkSession.open` (checklist item 5).
- **D — Discard unvalidated draft:** treat existing `workspace-bdd-sketch.md` (path-overrides slice, never judge-validated) as void; re-sketch only after grill ticks name a slice.

**Runner paths read:**

- `workspace-eval-oo-sketch.md` §2 (Workspace model, PathOverride, path overrides table, resolution on open)
- `workspace-eval-oo-sketch.md` §9 workspace checklist items 1–2 and 5
- `workspace-bdd-sketch.md` (existing draft — slice 1 path overrides, deferred list)
- `context_tools/bdd/.context/bdd-grill-sketch-workflow.md`

**Judge answer:** **Recommend A — path overrides only.** Checklist item 1 lists `load` / `save` / `lookupPath` / `upsertPath` on **`Workspace`** together with `pathOverrides`; item 2 isolates **`PathOverride`** row shape. Item 5 (`openWorkSession`) and item 4 (`BaseContextTool.workspace` resolution) are separate slices. OO sketch lines 125–131 label the three-step chain as **resolution on `open`** — that uses host `context_index_key` and `default_workspace_folder`, not bare `Workspace.lookupPath` in isolation. Option B would mix aggregates in one Bdd subject. Option C skips the usage-story prerequisite (overrides exist before a work session opens). Option D is wrong: existing `workspace-bdd-sketch.md` aligns with A but was never judge-validated — keep the hierarchy direction, run validate after a proper sketch turn; do not void without a FAIL on the file.

**Citations:**

- `workspace-eval-oo-sketch.md` §2 lines 47–50, 55–58, 111–123 — `pathOverrides`, `lookupPath`, `upsertPath`, sparse rows, `context-index.md` persistence
- `workspace-eval-oo-sketch.md` §2 lines 84–91, 125–131 — host resolution on **open** (defer to later slice)
- `workspace-eval-oo-sketch.md` §9 lines 826–830 — checklist ordering: items 1–2 before 5
- `context_index.py` lines 15–20 — today’s index path `{workspace}/.context/context-index.md` (persistence seam to fold into `Workspace`)
- `bdd-sketch.md` — usage-story order: establish subject state before downstream open/session behaviors

**Slice unlocked:** **no** — tick 1 selects slice **family** (A). Tick 2 should lock observables inside A (e.g. `lookupPath` when no row: absent override vs today’s `lookup_root` returning `None`; row key shape `tool` + `fidelity` vs today’s single-key entries).

---

### Turn 27ae89d2 — grill tick 2

**Question:** Inside slice **A** (path overrides only), when `Workspace.lookupPath(tool, fidelity)` is called and **no** matching override row exists, what is the stakeholder-visible outcome?

**Options:**

- **A — No override path:** `lookupPath` yields nothing (e.g. `None` / absent) — the host’s default-folder fallback is **out of scope** for this slice (OO sketch puts that at resolution step 3 on **open**, lines 127–129).
- **B — Implicit default path:** `lookupPath` returns `{workspace.path}/{default_workspace_folder}` even though `Workspace` does not carry host defaults in the target model (would duplicate checklist item 4).
- **C — Workspace root path:** return `{workspace.path}` when no row (today’s `root_glob_to_path` for `./*`).
- **D — Error:** raise when no row exists.

**Secondary (index row shape):** persisted rows use **`tool` + `fidelity` + `path`** (OO sketch lines 115–118, PathOverride lines 55–58) — **not** today’s single `tool_key = root_glob` entries in `ContextIndex.parse_current_entries` (one key per tool, no fidelity dimension).

**Runner paths read:**

- `workspace-eval-oo-sketch.md` §2 lines 55–58, 115–118, 125–129
- `context_index.py` `lookup_root`, `parse_current_entries`, `upsert_entry` (today: tool_key only; `## Log` section — target drops Log per OO line 123)
- `grill-answers.md` tick 1 judge recommendation (slice A)

**Judge answer:** **Recommend A — no override path.** Target `Workspace.lookupPath(tool, fidelity)` should behave like today’s absent-key case: `ContextIndex.lookup_root` returns **`None`** when the key is missing (lines 91–94) — not workspace root, not implicit host default. Step 3 of the open resolution chain (`{workspace.path}/{default_workspace_folder}`) belongs on **BaseContextTool** / **open**, not on `Workspace.lookupPath` (OO lines 127–129). Reject B (host default on wrong aggregate), C (workspace root), D (error on miss).

**Row shape:** Confirm **`tool` + `fidelity` + `path`** per PathOverride (OO lines 55–58, 115–118). Today’s `parse_current_entries` / `upsert_entry` use a **single `tool_key`** with no fidelity dimension — Bdd describes the **target** model, not a line-for-line port. Persisted file drops **`## Log`** (OO line 123); today’s `render_index` still emits Log (lines 113–117) — out of scope for slice A observables except “save writes Current rows only.”

**Slice unlocked:** **partial — yes for sketch draft** with one open branch: `upsertPath` “remove row when path matches host default again” (OO line 131) needs tick 3 — `Workspace` does not own `default_workspace_folder`.

**Citations:**

- `workspace-eval-oo-sketch.md` lines 47–50, 55–58, 115–123, 127–129
- `context_index.py` lines 91–94 (`lookup_root` → `None`), 136–165 (`upsert_entry` / Log)
- `grill-answers.md` tick 1 — slice A family

**Slice unlocked:** **partial** — sketch may proceed for load / lookup / save / sparse rows; hold **`it should drop the row when path matches host default`** until tick 3.

---

### Turn 4d111cd1 — grill tick 3

**Question:** OO sketch line 131: `upsertPath` when resolved path **matches host default again** → remove the row. `Workspace` does not own `default_workspace_folder`. How should slice **A** Bdd express default-match **removal**?

**Options:**

- **A — Caller-supplied default:** `upsertPath(tool, fidelity, path, default_path)` — when `path == default_path`, remove the row; when path differs from default, upsert sparse row. Host passes its `default_workspace_folder`-resolved path at call time.
- **B — Explicit remove only:** `removePath(tool, fidelity)` on `Workspace`; slice A Bdd covers add/update + explicit remove; “matches default” removal is host orchestration in a **later** slice (open / BaseContextTool).
- **C — Omit removal from slice A:** only add/update rows in this sketch; no `it should` for default-match removal anywhere yet.

**Runner paths read:**

- `workspace-eval-oo-sketch.md` line 131, lines 47–50
- `grill-answers.md` ticks 1–2 (slice A, lookupPath absent → None)

**Judge answer:** **Recommend A — caller-supplied `default_path`.** OO line 131 describes behavior at **open** time when the host already knows the resolved path and its default — passing `default_path` into `upsertPath` keeps `Workspace` free of host fields while making removal observable on the aggregate: equal → drop row; unequal → sparse upsert. Reject B (splits one policy across two slices unnecessarily). Reject C (drops locked requirement from line 131).

**Citations:**

- `workspace-eval-oo-sketch.md` lines 47–50, 131
- `grill-answers.md` ticks 1–2 — slice A, lookup absent → None, tool+fidelity+path

**Slice unlocked:** **yes** — slice A boundary: `load` / `save` / `lookupPath` (absent → no override) / `upsertPath(tool, fidelity, path, default_path)` (sparse add/update/remove on default match); persistence `{workspace.path}/.context/context-index.md` without `## Log`; exclude `openWorkSession`, host resolution chain, `WorkSession`.

---

### Turn (grill tick 4 — slice B boundary)

**Question:** Slice **B** — `Workspace.openWorkSession(name, goal, fidelities, contexts, path, default_path)` (OO lines 51–53). Which observables belong in B vs defer to slice **C** (`WorkSession.open` / git branch)?

**Options:**

- **A — Workspace open only:** `load()`; add/load session in `workSessions`; set `currentWorkSession`; `upsertPath` when explicit `path` ≠ `default_path`; **exclude** git checkout, branch naming, `WorkSession.open` innards.
- **B — Include git branch checkout** in the same slice (WorkSession.open policy).
- **C — Include host three-step path resolution** instead of openWorkSession.

**Runner paths read:** `workspace-eval-oo-sketch.md` lines 51–53, 60–71, §9 items 3 and 5.

**Judge answer:** **Recommend A.** OO line 53 sequences `load(); currentWorkSession.open(...); upsertPath` — Bdd slice B stops at **Workspace** outcomes before git/branch (slice C). Checklist item 5 is `openWorkSession`; item 3 is `WorkSession` with `openTurn`/git. Reject B (mixes aggregates). Reject C (checklist item 4).

**Citations:** OO lines 45–53, 60–71; §9 lines 826–828.

**Slice unlocked:** **yes** — slice B: openWorkSession loads overrides, mutates workSessions/currentWorkSession, upsertPath on non-default explicit path; exclude WorkSession.open git.

---

### Turn (grill tick 5 — slice C)

**Question:** Slice **C** — `WorkSession.open` git branch policy only?

**Options:** **A** — branch checkout/create/refuse-when-dirty per `workspace_session.md` lines 50–61; exclude Turn/git commit. **B** — include Turn.finish commit.

**Judge answer:** **A.** Git branch rules are documented in workspace_session.md; Turn commit is checklist item 8 / eval slice.

**Slice unlocked:** **yes**

---

### Turn (grill tick 6 — slice D)

**Question:** Slice **D** — host edit-path resolution (OO lines 125–131) as subject **a context tool host**?

**Judge answer:** **yes** — three-step chain as observable outcomes; Workspace lookup already slice A.

**Slice unlocked:** **yes** — Bdd workspace module checklist items 1–5 covered at behavior signature level.


