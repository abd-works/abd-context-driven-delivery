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

---

### Turn 7643854d â€” grill tick 7 (deferred slice E)

**Question:** `workspace-bdd-sketch.md` deferred line â€” Turn/git/repairs via `currentWorkSession`; SessionLog; GitRepo commit/push on `Turn.finish`. Where should slice **E** boundary fall for workspace Bdd?

**Options:**

- **A â€” Turn.finish git only:** when a turn finishes, commit scoped changes when the working tree is dirty on the session branch, always push the session branch; **exclude** SessionLog and domain Repair.
- **B â€” Turn.finish + SessionLog:** add observables for action-run and instruction-expand audit on the session trail and on the open turn; commit/push on turn finish as in A; **exclude** domain Repair/mistake/correction (eval package).
- **C â€” Include domain Repair chain:** mistake â†’ correction â†’ themed Repair on `WorkSession.repairs` in the same workspace sketch.
- **D â€” Defer all to eval module:** workspace sketch stays closed at slice D; deferred items move to a separate eval Bdd sketch only.

**Runner paths read:**

- `workspace-eval-oo-sketch.md` Â§4 (SessionLog, Turn envelope, Turn.finish push)
- `workspace-eval-oo-sketch.md` Â§9 workspace checklist items 8â€“9; eval checklist items 2â€“6
- `workspace-bdd-sketch.md` deferred line
- `mistakes/observable-behavior-2/mistake.md` â€” behavior under turn artifact I/O, not API operations

**Slice unlocked:** **no** â€” await judge answer.

**Judge answer:** **Recommend B â€” Turn.finish + SessionLog.** OO Â§4 locks SessionLog.append for expand (framework) and run (recipe body) â€” same record on session trail (`events.log`) and on `openTurn.toolCalls` when a turn is open. Turn.finish (checklist item 8) commits when dirty then **always** pushes session branch. Domain Repair/mistake/correction stays on eval package (`WorkSession.repairs`) â€” eval checklist items 2â€“6; reject C (mixes eval domain into workspace module sketch). Reject D (SessionLog and Turn.finish git are workspace checklist items 8â€“9, not eval-only). Reject A (drops locked SessionLog observables).

**Citations:** OO Â§4 lines 217â€“240, 256â€“266; Â§9 lines 832â€“834; observable-behavior-2 correction â€” nest under turn events, not API calls.

**Slice unlocked:** **yes** â€” slice E: SessionLog audit during open turn; turn finish commit-when-dirty + always push; exclude domain Repair (defer to eval Bdd sketch).

---

### Turn — grill tick 8 — usage-story describe taxonomy (consolidated sketch)

**Question:** Consolidated `workspace-bdd-sketch.md` — for **each** `describe` / `that` / `with` line, what category is it (**subject**, **standing condition**, **enabling event**, **outcome-only leaf**), and what legitimate behaviors, events, or state changes may nest there? What must **never** appear as a nested `that` (operation outcomes, API steps, logging as state)?

**Options (per line class):**

- **A — Subject / entry:** top `describe` names the stakeholder-facing actor (`a context tool`); nest only usage entry (`with a workspace`) then one domain entry event.
- **B — Standing `with`:** narrows git/session/path/input state **already true** before the next observation (`with a new work session name`, `with HEAD already on its session branch`, `with no path override…`); nest `it should` outcomes only — not further API calls.
- **C — Enabling `that` (event):** names something that **happens** and unlocks the next observations (`that has an action run against it`, `that has a turn open`, `that is reading or writing module artifacts`, `that is asked for its instructions`, `that has finished its turn`); nest narrower `with` or `it should` — never past-tense operation results (`that has logged…`).
- **D — Invalid:** operation/API narration (`openWorkSession`, `lookupPath`, `SessionLog.append`), outcomes dressed as state (`that has logged`, `that has expanded`), or manager classes as subjects.

**Runner paths read:**

- `workspace-bdd-sketch.md` (consolidated usage story)
- `workspace-eval-oo-sketch.md` §2 lines 42–93, 125–131; §4 lines 217–266 (turn envelope, SessionLog moments, finish_turn)
- `context_tools/bdd/bdd.md` — hierarchy shape, `nest-by-enabling-events`, `state-not-when`, `observable-behavior`
- `context_tools/bdd/.context/bdd-grill-sketch-workflow.md` — grill before sketch; never skip grill on `/bdd /sketch`
- `mistakes/nest-by-enabling-events-2/mistake.md` (db6b3528) — logged state anti-pattern

**Answer (taxonomy — apply before any sketch edit):**

| Line | Category | What may nest | Reject |
|---|---|---|---|
| `a context tool` | **subject** | `with a workspace` only at this depth | `BaseContextTool`, `SessionLog`, `@agent_tool` |
| `with a workspace` | **standing `with`** | domain entry event | path override load/save as subjects |
| `that has an action run against it` | **enabling event** (single entry) | session-name `with` branches; git `with` branches; prelude outcome; turn-open state; turn-finished event | `openWorkSession`, separate host-resolution slice lines |
| `with a new/existing work session name` | **standing `with`** | `currentWorkSession` / `workSessions` outcomes | WorkSession.open API steps |
| `with HEAD…` / `with a clean…` / `with a dirty…` | **standing `with`** (git) | branch policy `it should` | checkout/create as operation lines |
| `it should open a turn for the action run` | **outcome** (prelude) | leaf | nested under wrong parent |
| `that has a turn open` | **state after event** (`Turn.open`) | artifact-I/O event; path-for-turn `with`; expand event | SessionLog as subject |
| `that is reading or writing module artifacts` | **enabling event** | explicit-path / override `with` branches → edit-path outcomes | `lookupPath`, resolve-on-open |
| `with a path for the turn that differs/equals…` | **standing `with`** (after path known) | keep/drop override outcomes | upsertPath call lines |
| `that is asked for its instructions` | **enabling event** (expand) | expansion trail + openTurn attachment outcomes | `that has expanded…` |
| `that has finished its turn` | **enabling event** (`finish_turn`) | action-run trail + turn attachment; then dirty `with` → commit; always push | `that has logged…`, recipe-run event |

**Locked behaviors from OO §4 (stakeholder-visible, not implementation):**

- **Expand audit** — when instructions are **asked for** (framework expand), record on session trail and on **open** turn.
- **Run audit** — when the turn is **finished** for the action (agent invokes `finish_turn` after work), record action run on session trail and on that turn — **not** under a “logged” state.
- **Git on finish** — commit when dirty on session branch; **always** push session branch (OO lines 256–258).

**Process correction:** `/bdd /sketch` must run **grill → sketch → generate** cadence (`Sketcher.sketch_session` / `bdd-grill-sketch-workflow.md`). Consolidated sketch was generated without tick 8 taxonomy — caused repeated nest-by-enabling-events failures.

**Eval turn attachment:** Mistake and correction are **separate turns** (each: one process for `begin` → tool → `finish`, then commit). See `bdd-grill-sketch-workflow.md` § Eval turn — one process per turn. Orphans `99079d1e` / `2245e8ec`: separate `tools.ps1 run` per tool broke the open turn. Do not combine `log_mistake` and `log_correction` in one turn.

**Citations:** OO §2 lines 51–53, 84–92, 125–131; §4 lines 223–224, 255–266, 611–618; `bdd.md` pass/fail examples; mistake db6b3528.

**Slice unlocked:** **yes** — consolidated usage-story sketch may proceed only where each line matches taxonomy above; re-grill if a new `that`/`with` line is added.

