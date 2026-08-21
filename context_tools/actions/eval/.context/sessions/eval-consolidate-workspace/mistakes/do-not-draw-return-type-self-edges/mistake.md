# do-not-draw-return-type-self-edges

- **entry_id:** b3694bec
- **artifact:** context_tools/actions/eval/.context/sessions/eval-consolidate-workspace/workspace-eval-target-ce.drawio
- **rule:** (process) do-not-draw-return-type-self-edges
- **wrong:** Generator draws association edges Turn→Turn (open returns Turn) and WorkSession→WorkSession (load returns WorkSession) as external loops across the diagram instead of keeping return-type self references on the operation row with no edge.
- **status:** open
