# eval-turn-single-process

- **entry_id:** 9d033ff4
- **artifact:** context_tools/bdd/.context/bdd-grill-sketch-workflow.md
- **rule:** eval-turn-single-process
- **wrong:** Ran begin_eval_turn, log_mistake, log_correction, and finish_eval_turn as separate tools.ps1 run calls. Each process reloads session.yaml only; mistakes on disk under mistakes/ are not in session._mistakes; log_correction _find_mistake fails silently; repairs/ not created; session.yaml turns 99079d1e and 2245e8ec have mistake_ids: [].
- **status:** fixed
