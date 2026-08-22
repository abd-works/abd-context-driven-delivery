# usage-order-behaviors-5

- **entry_id:** 1bcaf881
- **artifact:** context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md
- **rule:** usage-order-behaviors
- **wrong:** lookupPath miss/hit branches were abstract ("that is asked for a tool path" / "with no path override for that tool and fidelity") with no caller scenario. lookupPath is invoked when a context tool resolves its edit path for context_index_key and fidelity on open — miss when no row, hit when row matches, miss when row is for a different pair.
- **status:** open
