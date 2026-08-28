# utilities/swarm
- **Purpose:** Runs a Plan (or a slice of Turns) with several SubAgents at once. An Agent is a SubAgent executing that Plan under one Hypothesis. A Hypothesis is the first-order approach — which existing context tool, action, and fidelity that Agent believes will achieve the Supervisor’s Outcome (the Plan goal, e.g. Plan started). Supervisor compares using its rubric against Outcome and/or Plan JudgeCheckpoint rubrics on Turns. Launch uses the existing `sub_agent` non-blocking seam.
- **Seam (terms):** Swarm, Supervisor, Agent, Hypothesis, Outcome
- **Dependencies (one-way):** `plan`, `sub_agent`
