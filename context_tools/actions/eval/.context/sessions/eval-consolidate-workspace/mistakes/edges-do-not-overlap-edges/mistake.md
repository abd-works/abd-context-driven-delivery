# edges-do-not-overlap-edges

- **entry_id:** 4be8ff6c
- **artifact:** context_tools/actions/eval/.context/sessions/eval-consolidate-workspace/workspace-eval-target-ce.drawio
- **rule:** edges-do-not-overlap-edges
- **wrong:** Long orthogonal edge runs share the same rows/columns (e.g. WorkSession→Turn at y=978/2384, BaseContextTool→Turn at y=208/2252, Repair→GitRepo at y=986/878) so edge segments stack on top of each other and read as overlapping lines.
- **status:** open
