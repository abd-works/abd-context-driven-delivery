# eval-turn-single-process

- **tool:** Bdd
- **error:** Ran begin_eval_turn, log_mistake, log_correction, and finish_eval_turn as separate tools.ps1 run calls. Each process reloads session.yaml only; mistakes on disk under mistakes/ are not in session._mistakes; log_correction _find_mistake fails silently; repairs/ not created; session.yaml turns 99079d1e and 2245e8ec have mistake_ids: [].
- **rule:** eval-turn-single-process
- **how:** Added bdd-grill-sketch-workflow.md section Eval turn — single process; updated repairs/*/improvement.md and grill-answers tick 8 with orphan turn ids and replay pattern (turn 26ddc97e).
