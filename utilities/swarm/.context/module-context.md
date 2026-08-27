# utilities/swarm
- **Purpose:** Runs a Plan (or a slice of PlannedTurns) with several agents at once. Supervisor owns the overarching Outcome; each Agent owns a unique Hypothesis (the “if we do this we will achieve the Outcome” approach). Supervisor compares results with its own rubric against Outcome and/or Plan JudgeCheckpoint rubrics on PlannedTurns. Launch reuses the existing `sub_agent` non-blocking seam — this module is not a second decorator kit.
- **Seam (terms):** Swarm, Supervisor, Agent, Hypothesis, Outcome
- **Dependencies (one-way):** `plan`, `sub_agent`
