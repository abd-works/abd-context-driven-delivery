# draw-association-for-caller-not-only-owner

- **tool:** CleanEngineering
- **error:** Correction declares + fixedIn: Turn | None and Correction.apply sets fixedIn to the closing Turn, but the diagram has no Correction→Turn association edge — only Mistake→Correction and Repair→Correction.
- **rule:** (process) draw-association-for-caller-not-only-owner
- **how:** Manual draw.io edit — added Correction→Turn association edge (id=21) for fixedIn; routes via x=1040 to Turn entry.
