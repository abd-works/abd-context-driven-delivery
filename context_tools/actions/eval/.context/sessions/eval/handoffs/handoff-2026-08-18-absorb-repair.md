 Handoff — eval (2026-08-18)

## Resume

- **Stage:** development (+ CE model) on `context_tools/actions/eval` — ring 1 + Repair absorb coded
- **Last work:** Absorbed Repair into eval. `Repair` lives in `context_tools/actions/eval/session.py`. Base holds `self.repairer`. Old `context_tools/actions/repair` package deleted (no shim). No `improve`. Eval tool is `Repair.eval` (not a host method named `eval` — that would shadow `self.eval`).
- **Next action:** Ring 2+ only if sketches move; do not re-open I* or `improve`.
- **Next focus:** none for absorb — coded

## Resume in three lines

1. **Stage:** EvalSession + Repair coded from CE/BDD sketches (no I* seams).
2. **Last accepted:** `createRule` only when `ScanReport.matches(mistake)` is false; scan first; `_begin` / `_kind` private; eval is a separate tool; no `improve`. Absorb landed 2026-08-18.
3. **Next:** Optional catalog/skill copy still lists `improve` (stale). Real-git sandbox examples skip when `git` is not on PATH.

## Generator state

- **Active:** informal CE modules + BDD sketches (not a CDD generate this bout). `cdd-sketch.md` absent.
- **Sketches:**
  - `context_tools/actions/eval/.context/sessions/eval/eval-bdd-sketch.md`
  - `context_tools/actions/eval/.context/sessions/eval/eval-ce-sketch.md`
  - `context_tools/actions/eval/.context/sessions/eval/eval-ce.drawio`
- **Code:** `context_tools/actions/eval/session.py` (`EvalSession` alias `Session`, `Repair`, `CDDRepo` extends `WorkspaceRepo`), `session_spec.py`, `agent_bdd_spec.py`, `context_tool_recording_spec.py`, `__init__.py`
- **Guides:** `context_tools/actions/eval/repair.md`, `log_mistake.md`, `log_correction.md`, `eval.md`; `context_tools/base/createRule.md`
- **Module context:** `context_tools/actions/eval/.context/module-context.md`
- **Base:** `self.eval` + `self.repairer`; `log_mistake` / `log_correction` forward to Repair; host `createRule`; no `improve` / `verify_regression` / `archive_mistakes`
- **context-index:** `.context/context-index.md` — Current: `clean_engineering` / `stories` → `./../story-ui/*` (not eval-specific)

## Locked design (do not re-grill)

- Domain type **EvalSession** (`Session = EvalSession` alias). Workspace stays `WorkspaceSession`.
- Repair lives under `context_tools/actions/eval`. `context_tools/actions/repair` deleted with **no shim**.
- `Repair.repair` is atomic (does not call eval). **eval** is a separate tool on Repair. **No `improve`**. Host must not define a method named `eval`.
- If no Mistake/Correction, repair takes them from host context and wires them.
- `createRule` is a Base action: only when scan does not already match the Mistake; then run the new rule and detect a match.
- `ScanReport.matches(mistake)`; Scan overloads `scan(paths)` and `scan(paths, root, rule)`.
- Private: `Repair._begin`, `Repair._kind`. Executable wiring is `_run` (not the `@action` body).
- CDDRepo **extends** WorkspaceRepo. Asset session links `cddAt` once. Repair opens a WorkspaceSession on the CDD clone. No `stampTurn`.
- `Null*` repos remain for isolated unit tests only (subclasses of the real repo classes).

## Next coding (ordered)

1. **Done:** remove interfaces; bind to concrete classes.
2. **Done:** absorb Repair — Mistake / Correction / Turn / Repair behavior; Base `self.repairer`; delete `mistakes.log` store and `context_tools/actions/repair`; `createRule` on the host; `EvalSession` name with `Session` alias.
3. Optional later: regenerate catalog/skills so they stop listing `improve`.

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
- `context_tools/base/base_context_tool.py`
- `context_tools/base/.context/module-context.md`
- `context_tools/base/base_context_tool.md` (# Create Rule)

## Open questions / risks

- Real-git sandbox examples in `session_spec.py` / `agent_bdd_spec.py` skip when `git` is not on PATH (this Windows shell has no git). Isolated Null* examples cover the domain. Do not treat missing git as a reason to bring I* back.
- `finishTurn` stays chat-reply boundary — do not invent a tool-call boundary.
- Drawio in diagrams.net overwrites disk edits unless reloaded from disk.
- `@action repair` / `@action eval` on Repair are instruction-only (validator forbids `self.session` in `@action`). In-process wiring is `_run` / `_begin`. Host `Base.repair` expands `self.repairer.repair()` for the agent; it does not execute `_run`.
