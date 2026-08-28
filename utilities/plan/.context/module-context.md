# utilities/plan
- **Purpose:** Owns a Plan associated with a Workspace: an ordered sequence of Turns. Each Turn already has action, fidelity, context, and toolCalls. Turn.state is TicketState (Backlog / In Progress / Done). Optional JudgeCheckpoint and/or HILCheck hang on a Turn. Start Plan opens a WorkSession; the first Backlog Turn becomes In Progress. Execute Turn runs that In Progress Turn. Advance Turn finishes it (Done) and the next Backlog Turn becomes In Progress. Fix and Rerun uses Turn.recordMistake, recordCorrection, and WorkSession.repairs.
- **Seam (terms):** Plan, Turn, JudgeCheckpoint, HILCheck, TicketState
- **Dependencies (one-way):** `workspace`
