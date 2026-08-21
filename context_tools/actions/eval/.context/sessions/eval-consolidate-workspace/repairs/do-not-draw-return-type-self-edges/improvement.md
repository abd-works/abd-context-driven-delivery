# do-not-draw-return-type-self-edges

- **tool:** CleanEngineering
- **error:** Generator draws association edges Turn→Turn (open returns Turn) and WorkSession→WorkSession (load returns WorkSession) as external loops across the diagram instead of keeping return-type self references on the operation row with no edge.
- **rule:** (process) do-not-draw-return-type-self-edges
- **how:** Manual draw.io edit — removed Turn→Turn and WorkSession→WorkSession return-type self-edges from the diagram.
