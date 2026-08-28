**Sources / context:** `utilities/swarm/.context/plan-and-swarm-utilities-23/issue-body.md`; `utilities/swarm/.context/plan-and-swarm-utilities-23/grill-answers.md`; `utilities/git/.context/module-context.md`; `utilities/git/.context/git-modules.md`; `utilities/sub_agent/.context/module-context.md`; `utilities/workspace/.context/module-context.md`; `utilities/workflow/.context/module-context.md`; `.context/research/git-knowledge-and-workflow-backbone.md` §8; `context_tools/agent_bdd/.context/module-context.md` (judge vocabulary only)

## Language companion

*Plan* is associated with a *Workspace*. It holds ordered *PlannedTurn*s. A *PlannedTurn* invokes context tools, actions, fidelities, and context. A *JudgeCheckpoint* and/or *HipCheckpoint* may hang on a *PlannedTurn* — they are not distinct turns. Starting the Plan opens a *WorkSession*; after each actual *Turn* finishes, the next *PlannedTurn* runs. Plan does not run agents and does not own ticket flow.

*Swarm* is a collection of *Agent*s executing the same *Plan* (or a slice of *PlannedTurn*s). *Supervisor* owns the overarching *Outcome*. Each *Agent* owns a unique *Hypothesis* — the “if we do this we will achieve the Outcome” approach. *Supervisor* compares results with its rubric against Outcome and/or *JudgeCheckpoint* rubrics on *PlannedTurn*s. Launch is the existing *sub_agent* seam.

*ResearchTag* is ticket metadata on the existing *Ticket* / *Project* graph in **git** — not a second identity besides GitHub issue `#`. Notes stay git notes (and trailers for flow). *TicketState* remains Backlog / In Progress / Done; this work does not add kanban columns.

### plan

- Associated with a *Workspace*; holds ordered *PlannedTurn*s
- *start* opens a *WorkSession* (no second session type)
- **Invariant:** a plan is a sequence, not a swarm; it does not launch agents

### plannedturn

- One slot in a *Plan*: context tools, actions, fidelities, and context
- Optional *JudgeCheckpoint* and/or *HipCheckpoint*
- **Invariant:** checkpoints are not distinct turns; after actual *Turn*.finish, the next *PlannedTurn* is due

### judgecheckpoint

- AI judge against a rubric on a *PlannedTurn*
- Rubrics here can later be consumed by a *Supervisor*; plan still does not depend on swarm

### hipcheckpoint

- Human-in-process gate on a *PlannedTurn*
- **Invariant:** HIP is not an AI judge and not a new ticket status

### swarm

- Aggregates *Agent*s that share a *Plan* or a slice of *PlannedTurn*s
- Does not own plan structure or git ticket identity

### supervisor

- Owns the overarching *Outcome*
- Compares *Agent* results: own rubric against Outcome, and/or *JudgeCheckpoint* rubrics on *PlannedTurn*s

### agent

- One member of a *Swarm*
- Owns *Hypothesis* (the approach toward the Supervisor *Outcome*)
- Launched through existing `sub_agent` (non-blocking), not a second decorator

### hypothesis

- The unique first-order approach: “if we do this, we will achieve the Outcome”

### outcome

- Overarching result owned by *Supervisor* — not the Agent approach

### researchtag

- Label on an existing *Ticket* for research/flow metadata
- **Invariant:** stored on the git Ticket/Project API (notes/trailers/data) — not a parallel yaml ticket index

## Modules

Build order: `git` | `workspace` | `sub_agent` → `plan` → `swarm`

Physical module context lives beside source (`utilities/{module}/.context/module-context.md`). Session build order: `module-build-order.md`.

---

# utilities/git
- **Purpose:** OO git + GitHub domain for CDD workspace sessions and workflow commands. Callers manage research tags, notes, and ticket/session flow on the existing Repo / Project / Ticket / TicketState graph — git-primary notes and trailers, not a second ticket store.
- **Seam (terms):** Repo, Branch, Commit, Project, Ticket, TicketState, Git, ResearchTag
- **Dependencies (one-way):** `tools.tool`; consumed by `workspace`, `workflow`

# utilities/plan
- **Purpose:** Owns a Plan associated with a Workspace: an ordered sequence of PlannedTurns. Each PlannedTurn invokes context tools, actions, fidelities, and context. Optional JudgeCheckpoint and/or HipCheckpoint hang on a PlannedTurn — they are not distinct turns. Starting the Plan opens a WorkSession; after each actual Turn finishes, the next PlannedTurn runs.
- **Seam (terms):** Plan, PlannedTurn, JudgeCheckpoint, HipCheckpoint
- **Dependencies (one-way):** `workspace`

# utilities/swarm
- **Purpose:** Runs a Plan (or a slice of PlannedTurns) with several agents at once. Supervisor owns the overarching Outcome; each Agent owns a unique Hypothesis (the “if we do this we will achieve the Outcome” approach). Supervisor compares results with its own rubric against Outcome and/or Plan JudgeCheckpoint rubrics on PlannedTurns. Launch reuses the existing `sub_agent` non-blocking seam — this module is not a second decorator kit.
- **Seam (terms):** Swarm, Supervisor, Agent, Hypothesis, Outcome
- **Dependencies (one-way):** `plan`, `sub_agent`
