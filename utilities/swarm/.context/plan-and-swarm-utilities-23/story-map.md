---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Plan And Swarm Utilities

**Sources / context:**
`utilities/swarm/.context/plan-and-swarm-utilities-23/issue-body.md`;
`utilities/swarm/.context/plan-and-swarm-utilities-23/session.md`;
`utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md`;
`utilities/swarm/.context/plan-and-swarm-utilities-23/plan-and-swarm-sketch.md`;
`utilities/plan/.context/module-context.md`;
`utilities/git/.context/module-context.md`;
`utilities/git/.context/git-modules.md`;
`utilities/workflow/.context/module-context.md`;
`utilities/sub_agent/.context/module-context.md`;
`utilities/workspace/.context/module-context.md`;
`context_tools/agent_bdd/.context/module-context.md`;
`context_tools/stories/stories.md`;
`context_tools/stories/templates/md/story-map.md`

---

(E) Run Planned Work
    (E) Compose Plan Sequence
        (S) Practitioner --> Record Planned Turn
        (S) Practitioner --> View Planned Turns
        (S) Practitioner --> Add Judge Checkpoint
        (S) Practitioner --> Add Hip Checkpoint
        (S) Practitioner --> Start Plan
    (E) Manage Ticket Flow
        (S) Practitioner --> Record Research Tags
        (S) Practitioner --> Record Flow Notes
        (S) Practitioner --> Update Ticket Status
        (S) Agent --> Resolve Ticket Number
    (E) Start Agent Swarm
        (S) Supervisor --> Create Agent Swarm
        (S) Supervisor --> Assign Agent Hypothesis
        (S) Swarm agent --> Load Plan Context
        (S) Swarm agent --> Run Planned Turns
    (E) Compare Swarm Results
        (S) Supervisor --> Collect Swarm Results
        (S) Supervisor --> Compare Agent Outcomes
        (S) Supervisor --> Review Supervisor Rubric
        (S) Supervisor --> Review Plan Judges

---

## Scope boundary

**In scope:** A Plan associated with a Workspace, holding ordered PlannedTurns. Each PlannedTurn invokes context tools, actions, fidelities, and context. Optional AI judge and HIP checkpoints hang on a PlannedTurn — they are not distinct turns. Starting the Plan opens a WorkSession; actual Turns run and close, then the next PlannedTurn. Swarm runs a Plan or a slice of PlannedTurns with multiple sub-agents. Supervisor owns Outcome; each Agent owns the “if we do this…” Hypothesis. Supervisor compares using its rubric on Outcome and/or Plan JudgeCheckpoint rubrics on PlannedTurns. Git `Repo` / `Ticket` / `Project` / `TicketState` manage research tags, notes, and flow on the existing API (GitHub issue `#`; Backlog / In Progress / Done; git notes and trailers). Related seams: `@sub_agent` launch, `ai_judge`, workflow ticket + project status.

**Out of scope:** New slash-command product UX beyond existing kits (`/backlog`, `/start-ticket`, `/finish-ticket`, `/sub-agent`). Invented kanban columns or status badges. A second ticket identity besides GitHub issue `#`. A parallel yaml/store beside `utilities/git`. Production Python in this pass.

---

## Thin slices

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
