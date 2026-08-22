# usage-order-behaviors

- **tool:** Bdd
- **error:** Ran /bdd /sketch without grilling the consolidated usage story. Sketcher generate wrote workspace_spec.py and edited the hierarchy without grill tick classifying legitimate subjects, standing with conditions, enabling that events, and invalid patterns per describe line — repeated bad Bdd (logged state, API narration).
- **rule:** usage-order-behaviors
- **how:** |
    Bdd content: grill tick 8 in grill-answers.md before sketch edits; run audit under `that has finished its turn`.

    **Eval attachment (same failure class):** Turns `99079d1e` and `2245e8ec` called `begin_eval_turn`, `log_mistake`, `log_correction`, and `finish_eval_turn` as separate `tools.ps1 run` invocations — mistake files landed under `mistakes/` but `session.yaml` had `mistake_ids: []` and no `repairs/`. `log_correction` cannot find mistakes across processes (`EvalSession.load` does not read `mistakes/` folders).

    **Fix:** One Python process — `bdd.open(); begin_eval_turn(); log_mistake(...); log_correction(entry_id=..., ...); finish_eval_turn(...)` without exiting between calls. Orphan replay for `745db890`: hydrate `Mistake` from `mistakes/usage-order-behaviors-7/` into `open_turn`, then `log_correction` in that same process (turn `26ddc97e`). Documented in `context_tools/bdd/.context/bdd-grill-sketch-workflow.md` § Eval turn — single process.
