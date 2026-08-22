# eval-turn-single-process

- **tool:** Bdd
- **error:** Documented log_mistake and log_correction in the same turn / same finish_eval_turn. Mistake and correction are separate turns; only begin+tool+finish share one process per turn.
- **rule:** eval-turn-single-process
- **how:** bdd-grill-sketch-workflow.md: two turns; one process per turn; not same turn for mistake+correction.
