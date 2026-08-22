# domain-practice-alignment-2

- **entry_id:** acddcec1
- **artifact:** context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md
- **rule:** domain-practice-alignment
- **wrong:** openWorkSession call listed tool, fidelity, and default_path parameters that are not on Workspace.openWorkSession in the target model (OO sketch lines 51-53). default_path belongs on upsertPath at call time; tool and fidelity belong on lookupPath/PathOverride, not on openWorkSession.
- **status:** fixed
