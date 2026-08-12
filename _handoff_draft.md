# Handoff — eval session capture

## Next session focus

Wire `BaseContextTool.self.eval` and route `@log` / `log_mistake` / `log_correction` onto the eval `Session` (first-order ToolCalls + mistakes on the open Turn).

## Resume in three lines

1. **Stage:** BDD development (+ CE model) on `utilities/eval` — ring-1 Session capture theme.
2. **Last accepted:** Ring-1 green (16/16): Session auto-branch from `workspace.name`; mistake→later-turn nesting; CDD no longer inlines generate/satisfy (separate tools runs); BDD satisfy expansion aligned with tool-mode validate.
3. **Next:** `/bdd` (path `utilities/eval`, session `eval`) — add behaviors for “context tool records through eval”, then RED→GREEN Base wiring (`self.eval`, `@log` → `recordToolCall`, `log_mistake`/`log_correction` → eval).

## Generator state  

- **Active:** `context_tools.bdd.bdd:Bdd` (fidelity `development`); CE companion at matching model/code when needed.
- **Sketches:**
  - `utilities/eval/.context/sessions/eval/eval-bdd-sketch.md`
  - `utilities/eval/.context/sessions/eval/eval-ce-sketch.md`
- **Code:** `utilities/eval/session.py`, `session_spec.py`, `__init__.py`
- **Module context:** `utilities/eval/.context/module-context.md` (Constraint: branch from session name via WorkspaceRepo)
- **context-index:** `.context/context-index.md` (workspace root) — Current: `clean_engineering` / `stories` → `./../story-ui/*` (not eval-specific)

## Grilling / skills state

- Grill answers: `utilities/eval/.context/sessions/eval/grill-answers.md`
- Suggested skills next: `/bdd` for Base wiring tests; `/ce` only if closing CE model gaps on eval after wiring; do **not** default to satisfy after a clean generate.

## CDD progress

None for this sprint (`cdd-sketch` absent). Side fix this bout: CDD `generate`/`satisfy`/`iterate`/`validate`/`document` defer children with `mode=tool` + Separate tools-run hints; grill/sketch stay inlined. Expander for-each now respects loop-var `mode`.

## Artifacts to read

- `.context/context-index.md`
- `utilities/eval/.context/module-context.md`
- `utilities/eval/.context/sessions/eval/session.md`
- `utilities/eval/.context/sessions/eval/eval-bdd-sketch.md`
- `utilities/eval/.context/sessions/eval/eval-ce-sketch.md` (First coding slice items 3–5)
- `utilities/eval/.context/sessions/eval/grill-answers.md`
- `utilities/eval/session.py` / `session_spec.py`
- `context_tools/base/base_context_tool.py` (still `repairer.log_mistake`; no `self.eval` yet)
- `context_tools/cdd/cdd.py` (deferred child tool-mode — already landed)

## Open questions / risks

- When to call `finishTurn` (chat-reply boundary) vs tool-call boundary — locked as chat turn, but Base wiring must not invent a second boundary.
- Real `WorkspaceRepo`/`CDDRepo` git still Null stubs — thin real git is slice item 5 after Base wiring.
- Eval `session.yaml` vs legacy `events.log` / `mistakes.log` coexistence until `@log` fully pointed at eval.
- Logging rule: first-order `tools run` / skill invokes only; CDD inlined grill/sketch ≠ separate ToolCalls; deferred CDD children = separate ToolCalls when the agent actually runs them.
