# Thin slicing — Plan And Swarm Utilities

### Increment 1: Compose a judged plan

**Outcome:** A Practitioner records ordered PlannedTurns, attaches optional judge and HIP checkpoints on a PlannedTurn, and starts the Plan so a WorkSession opens.

**Slicing notes:** Plan definition and start only — no swarm launch and no git flow writes. Checkpoints are not turns.

**Decision prompt:** Ready to manage ticket flow state on the existing git API after this slice?

**Stories:**
- Record Planned Turn
- View Planned Turns
- Add Judge Checkpoint
- Add Hip Checkpoint
- Start Plan

### Increment 2: Manage ticket flow on git

**Outcome:** Research tags, flow notes, and project TicketState (Backlog / In Progress / Done) live on the current git Ticket / Project / notes API keyed by GitHub issue `#`.

**Slicing notes:** Enhance `Repo`, `Ticket`, `TicketState`, `note` / `read_notes` — not a second store. Status examples are the existing columns only.

**Decision prompt:** Ready to launch a swarm against a plan after this slice?

**Stories:**
- Record Research Tags
- Record Flow Notes
- Update Ticket Status
- Resolve Ticket Number

### Increment 3: Launch a plan swarm

**Outcome:** A Supervisor starts a Swarm; each Agent has a unique Hypothesis (approach) toward the Supervisor Outcome, loads the Plan, and runs the Plan or a slice of PlannedTurns.

**Slicing notes:** Launch uses existing `@sub_agent` non-blocking launch. Full Plan vs selected PlannedTurns are examples of Run Planned Turns.

**Decision prompt:** Ready to compare swarm results after this slice?

**Stories:**
- Create Agent Swarm
- Assign Agent Hypothesis
- Load Plan Context
- Run Planned Turns

### Increment 4: Compare swarm results

**Outcome:** The Supervisor collects agent results and scores them with a Supervisor rubric against Outcome and/or Plan JudgeCheckpoint rubrics on PlannedTurns.

**Slicing notes:** Either target, not a Supervisor rubric on each Hypothesis.

**Decision prompt:** Ready to specify remaining scenarios after this slice?

**Stories:**
- Collect Swarm Results
- Compare Agent Outcomes
- Review Supervisor Rubric
- Review Plan Judges
