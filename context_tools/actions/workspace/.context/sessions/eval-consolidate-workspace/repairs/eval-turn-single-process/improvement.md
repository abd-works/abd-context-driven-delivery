# eval-turn-single-process

- **tool:** Bdd
- **error:** Ran begin_eval_turn, log_mistake, log_correction, and finish_eval_turn as separate tools.ps1 run calls; also documented mistake and correction on the same turn.
- **rule:** eval-turn-single-process
- **how:** bdd-grill-sketch-workflow.md — mistake turn and correction turn are separate commits; within each turn, begin+tool+finish share one process. Never log_mistake and log_correction on the same turn.
