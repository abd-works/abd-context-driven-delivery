**Sources / context:** `utilities/swarm/.context/issue-body.md`; `utilities/swarm/.context/grill-answers.md`; `utilities/git/.context/module-context.md`; `utilities/git/.context/git-modules.md`; `utilities/sub_agent/.context/module-context.md`; `utilities/workspace/.context/module-context.md`; `utilities/workflow/.context/module-context.md`; `.context/research/git-knowledge-and-workflow-backbone.md` §8; `context_tools/agent_bdd/.context/module-context.md` (judge vocabulary only)

## Language companion

*Plan* is associated with a *Workspace*. It holds ordered *Turn*s. Each *Turn* has action, fidelity, context, and toolCalls. *Turn.state* is *TicketState* (Backlog / In Progress / Done). A *JudgeCheckpoint* and/or *HILCheck* may hang on a *Turn*. *Start Plan* opens a *WorkSession*; the first Backlog Turn becomes In Progress. *Execute Turn* runs that Turn. *Advance Turn* finishes it (Done) and the next Backlog Turn becomes In Progress.

*Swarm* comes after Execute Plan. *Create Supervisor* owns *Outcome*. A shared *Swarm.turns* slice is selected once before any Agent runs. *Add Agent* owns *Hypothesis* and registers the Agent. *SubAgent.run* launches at *Plan.start* on that Agent’s own *WorkSession*; each Agent runs the shared slice. *Compare Swarm Results* streams after each Judge or HIL evaluation. *Comparative Association* updates automatically under the Supervisor rubric toward *Outcome*.

*ResearchTag* is ticket metadata on the existing *Ticket* / *Project* graph in **git**, keyed by GitHub issue `#`. Notes stay git notes (and trailers for flow). *TicketState* remains Backlog / In Progress / Done.

### plan

- Associated with a *Workspace*; holds ordered *Turn*s
- *start* opens a *WorkSession*

### turn

- Existing *workspace.Turn*: action, fidelity, context, toolCalls
- *state* is *TicketState*: Backlog / In Progress / Done
- Optional *JudgeCheckpoint* and/or *HILCheck*

### judgecheckpoint

- AI judge against a rubric on a *Turn* — same *rubric* argument as *ai_judge*

### hilcheck

- Human-in-the-loop check on a *Turn*

### swarm

- *Supervisor* plus *Agent*s on a *Plan*
- Holds shared *turns* (selected Plan Turns) chosen once before Agents run
- Each Agent runs Execute Plan on that shared slice in its *WorkSession*

### supervisor

- Owns the overarching *Outcome* and *rubric*
- *compare* streams after each Judge or HIL evaluation
- *associate* updates automatically after each streamed compare toward Outcome

### agent

- A *SubAgent* running the *Plan* under one *Hypothesis*
- Owns *Hypothesis* (the approach toward the Supervisor *Outcome*)
- Registered at Add Agent; *SubAgent.run* launches at *Plan.start* on its *WorkSession*

### hypothesis

- The unique first-order approach: “if we do this, we will achieve the Outcome”

### outcome

- Overarching result owned by *Supervisor*

### researchtag

- Label on an existing *Ticket* for research/flow metadata
- Stored on the git Ticket/Project API (notes/trailers/data)

## Modules

Build order: `git` | `workspace` | `sub_agent` → `plan` → `swarm`

Physical module context lives beside source (`utilities/{module}/.context/module-context.md`). Session build order: `module-build-order.md`.

---

# utilities/git
- **Purpose:** OO git + GitHub domain for CDD workspace sessions and workflow commands. Callers manage research tags, notes, and ticket/session flow on the existing Repo / Project / Ticket / TicketState graph — git-primary notes and trailers, not a second ticket store.
- **Seam (terms):** Repo, Branch, Commit, Project, Ticket, TicketState, Git, ResearchTag
- **Dependencies (one-way):** `tools.tool`; consumed by `workspace`, `workflow`

# utilities/plan
- **Purpose:** Owns a Plan associated with a Workspace: an ordered sequence of Turns. Each Turn already has action, fidelity, context, and toolCalls. Turn.state is TicketState (Backlog / In Progress / Done). Optional JudgeCheckpoint and/or HILCheck hang on a Turn. Start Plan opens a WorkSession; Execute Turn runs the In Progress Turn.
- **Seam (terms):** Plan, Turn, JudgeCheckpoint, HILCheck, TicketState
- **Dependencies (one-way):** `workspace`

# utilities/swarm
- **Purpose:** Create Supervisor (Outcome) then select shared Swarm.turns once; Add Agent registers Hypothesis; SubAgent.run launches at Plan.start on each Agent WorkSession running that slice. Compare streams after Judge/HIL; associate updates automatically under Supervisor rubric toward Outcome. Launch uses the existing `sub_agent` non-blocking seam.
- **Seam (terms):** Swarm, Supervisor, Agent, Hypothesis, Outcome
- **Dependencies (one-way):** `plan`, `sub_agent`
