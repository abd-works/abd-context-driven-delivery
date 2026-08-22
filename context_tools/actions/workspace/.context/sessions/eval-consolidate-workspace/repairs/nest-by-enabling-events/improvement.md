# nest-by-enabling-events

- **tool:** Bdd
- **error:** Used operation outcomes as nested states: `that has logged its action run` and `that has expanded its action instructions`. Logging is not a standing state — the `that` must name what triggers the record (agent asks for instructions → expansion trail; turn finish → run trail). Same class of error as treating API steps as subjects.
- **rule:** nest-by-enabling-events
- **how:** |
    Bdd: expand under `that is asked for its instructions`; action-run audit under `that has finished its turn`.

    Eval: `log_mistake` and `log_correction` on separate turns (see `bdd-grill-sketch-workflow.md` § Eval turn — one process per turn).
