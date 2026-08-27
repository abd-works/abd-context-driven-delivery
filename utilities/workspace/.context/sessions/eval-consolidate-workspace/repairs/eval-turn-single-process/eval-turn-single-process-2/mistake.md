# eval-turn-single-process-2

- **entry_id:** cb4724b1
- **artifact:** context_tools/bdd/.context/bdd-grill-sketch-workflow.md
- **rule:** eval-turn-single-process
- **wrong:** Documented log_mistake and log_correction in the same turn / same finish_eval_turn. Mistake and correction are separate turns; only begin+tool+finish share one process per turn.
- **status:** fixed
