# nest-by-enabling-events

- **tool:** Bdd
- **error:** Used operation outcomes as nested states: `that has logged its action run` and `that has expanded its action instructions`. Logging is not a standing state — the `that` must name what triggers the record (agent asks for instructions → expansion trail; recipe body runs → run trail). Same class of error as treating API steps as subjects.
- **rule:** nest-by-enabling-events
- **how:** |
    Bdd content: expand audit under `that is asked for its instructions`; action-run audit under `that has finished its turn` — not `that has logged…`.

    **Eval attachment (same failure class):** Turn `2245e8ec` ran `log_correction` in a separate process from `log_mistake` — `db6b3528` stayed under `mistakes/` with `status: open` and no `repairs/` until turn `26ddc97e` replayed correction in one process (hydrate mistake → `log_correction` → `finish_eval_turn`). See `bdd-grill-sketch-workflow.md` § Eval turn — single process.
