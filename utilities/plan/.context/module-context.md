# utilities/plan
- **Purpose:** Owns a Plan associated with a Workspace: an ordered sequence of PlannedTurns. Each PlannedTurn invokes context tools, actions, fidelities, and context. Optional JudgeCheckpoint and/or HipCheckpoint hang on a PlannedTurn — they are not distinct turns. Starting the Plan opens a WorkSession; after each actual Turn finishes, the next PlannedTurn runs.
- **Seam (terms):** Plan, PlannedTurn, JudgeCheckpoint, HipCheckpoint
- **Dependencies (one-way):** `workspace`
