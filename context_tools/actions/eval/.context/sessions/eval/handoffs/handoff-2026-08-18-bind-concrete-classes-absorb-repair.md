 Handoff — eval (2026-08-18)

## Resume

- **Stage:** development (+ CE model) on `context_tools/actions/eval` — ring 1 coded; I* interfaces removed; Repair absorb sketched and locked
- **Last work:** Dropped all eval I* ABC/Protocol types; `session.py` binds to `ToolCall`, `Correction`, `Mistake`, `Turn`, `Session`, `WorkspaceRepo`, `CDDRepo`, and workspace `WorkspaceSession`. `NullWorkspaceRepo` / `NullCDDRepo` subclass the real repo classes.
- **Next action:** Absorb Repair into eval — wait for **go**. Do not re-open the interface question.
- **Next focus:** absorb-repair

## Resume in three lines

1. **Stage:** EvalSession domain + Repair design locked in sketches; ring-1 `Session` is concrete classes only (no I* seams).
2. **Last accepted:** CE/BDD/drawio match: `createRule` only when `scanReport.matches(mistake)` is false; scan first; `_begin` / `_kind` private; eval is a separate tool; no `improve`. Interfaces removed 2026-08-18.
3. **Next:** After **go**, absorb Repair. Reload `eval-ce.drawio` from disk if the editor tab is stale.

## Generator state

- **Active:** informal CE modules + BDD sketches (not a CDD generate this bout). `cdd-sketch.md` absent.
- **Sketches:**
  - `context_tools/actions/eval/.context/sessions/eval/eval-bdd-sketch.md`
  - `context_tools/actions/eval/.context/sessions/eval/eval-ce-sketch.md`
  - `context_tools/actions/eval/.context/sessions/eval/eval-ce.drawio`
- **Code:** `context_tools/actions/eval/session.py` (no I*), `session_spec.py`, `agent_bdd_spec.py`, `context_tool_recording_spec.py`, `__init__.py` (no I* exports)
- **Module context:** `context_tools/actions/eval/.context/module-context.md`
- **Base:** `context_tools/base/base_context_tool.py` already has `self.eval`; `log_mistake` / `log_correction` still call `Session.record_mistake` / `record_correction` (move onto `Repair` on absorb)
- **context-index:** `.context/context-index.md` — Current: `clean_engineering` / `stories` → `./../story-ui/*` (not eval-specific)

## Locked design (do not re-grill)

- Domain type **EvalSession** (code still named `Session`). Workspace stays `WorkspaceSession`.
- Repair lives under `context_tools/actions/eval`. Delete `context_tools/actions/repair` with **no shim**.
- `Repair.repair` is atomic (does not call eval). **eval** is a separate tool. **No `improve`**.
- If no Mistake/Correction, repair takes them from host context and wires them.
- `createRule` is a Base action: only when scan does not already match the Mistake; then run the new rule and detect a match.
- `ScanReport.matches(mistake)`; Scan overloads `scan(paths)` and `scan(paths, root, rule)`.
- Private: `Repair._begin`, `Repair._kind`.
- CDDRepo **extends** WorkspaceRepo (sketch — not yet in code). Asset session links `cddAt` once. Repair opens a WorkspaceSession on the CDD clone. No `stampTurn`.
- `Null*` repos remain for isolated unit tests only (subclasses of the real repo classes).

## Next coding (ordered)

1. **Done:** remove interfaces; bind to concrete classes.
2. **After go:** absorb Repair — behavior on Mistake / Correction / Turn / Repair; Base `self.repairer`; delete `mistakes.log` and `context_tools/actions/repair`; register `createRule` / `eval` on the host; rename `Session` → `EvalSession` when that slice lands.

## Grilling / skills state

- Grill answers: `context_tools/actions/eval/.context/sessions/eval/grill-answers.md`
- Suggested next: `/ce` or `/bdd` only if sketches drift; do **not** satisfy-after-generate as the default.

## CDD progress

None for this sprint (`cdd-sketch` absent).

## Artifacts to read

- `.context/context-index.md`
- `context_tools/actions/eval/.context/module-context.md`
- `context_tools/actions/eval/.context/sessions/eval/session.md`
- `context_tools/actions/eval/.context/sessions/eval/eval-bdd-sketch.md`
- `context_tools/actions/eval/.context/sessions/eval/eval-ce-sketch.md`
- `context_tools/actions/eval/.context/sessions/eval/eval-ce.drawio` (reload from disk)
- `context_tools/actions/eval/.context/sessions/eval/grill-answers.md`
- `context_tools/actions/eval/session.py` / `session_spec.py` / `__init__.py`
- `context_tools/base/base_context_tool.py` (`self.eval` already attached)
- `context_tools/base/.context/module-context.md`
- `context_tools/base/base_context_tool.md` (# Create Rule)

## Open questions / risks

- Isolated `session_spec.py` examples (15) green; the three real-git sandbox examples failed in `after.each` (`repo_root` unset — `before.each` likely aborted). Re-run that describe after go; do not treat as a reason to bring I* back.
- `finishTurn` stays chat-reply boundary — do not invent a tool-call boundary.
- Drawio in diagrams.net overwrites disk edits unless reloaded from disk.
- Repair absorb is locked in sketches but **not coded**; do not start it without **go**.
